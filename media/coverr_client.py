import logging
import random
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=3, max=30))
def search_videos(query: str, api_key: str, per_page: int = 10, page: int = 1) -> list[dict]:
    """Search Coverr for videos. Only supports English queries. 50 calls/hour limit."""
    url = "https://api.coverr.co/videos"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "query": query,
        "page_size": per_page,
        "page": page,
    }
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("hits", data.get("videos", []))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def download_video(video_url: str, save_path: Path) -> Path:
    resp = requests.get(video_url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"Downloaded: {save_path}")
    return save_path


def _pick_best_file(video: dict) -> str | None:
    """Pick best video URL from Coverr result."""
    # Coverr uses urls.mp4 or similar structure
    urls = video.get("urls", {})
    # Try different quality levels
    for key in ("mp4", "hd", "sd", "small"):
        if urls.get(key):
            return urls[key]

    # Try assets array
    assets = video.get("assets", [])
    if assets:
        for asset in assets:
            if asset.get("url") and asset.get("type", "").startswith("video"):
                return asset["url"]

    # Try direct url field
    if video.get("url"):
        return video["url"]

    # Try video_files
    files = video.get("video_files", [])
    if files:
        return files[0].get("link") or files[0].get("url")

    return None


def _choose_video(videos: list[dict], used_ids: set) -> dict | None:
    """Choose a video not yet used."""
    for v in videos:
        vid = v.get("id")
        if vid in used_ids:
            continue
        if v.get("duration", 5) >= 3:
            return v
    for v in videos:
        if v.get("id") not in used_ids:
            return v
    return None


def get_footage_for_segments(search_queries: list[str], api_key: str, temp_dir: Path) -> list[Path]:
    paths = []
    used_ids: set = set()

    for i, query in enumerate(search_queries):
        logger.info(f"Searching Coverr for: '{query}'")

        videos = search_videos(query, api_key, page=1)
        chosen = _choose_video(videos, used_ids) if videos else None

        if not chosen and videos:
            videos2 = search_videos(query, api_key, page=2)
            chosen = _choose_video(videos2, used_ids) if videos2 else None

        if not chosen:
            simple_query = query.split()[0] if " " in query else "nature"
            logger.warning(f"No Coverr results for '{query}', trying '{simple_query}'")
            videos = search_videos(simple_query, api_key, page=random.randint(1, 2))
            chosen = _choose_video(videos, used_ids) if videos else None

        if not chosen:
            raise RuntimeError(f"No stock footage found on Coverr for: {query}")

        used_ids.add(chosen.get("id"))
        logger.info(f"Selected Coverr video id={chosen.get('id')} for '{query}'")

        video_url = _pick_best_file(chosen)
        if not video_url:
            raise RuntimeError(f"No downloadable file for query: {query}")

        save_path = temp_dir / f"clip_{i}.mp4"
        download_video(video_url, save_path)
        paths.append(save_path)

    return paths
