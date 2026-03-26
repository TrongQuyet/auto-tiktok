import logging
import random
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def search_videos(query: str, api_key: str, orientation: str = "portrait", per_page: int = 15, page: int = 1) -> list[dict]:
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": per_page,
        "size": "large",
        "page": page,
    }
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("videos", [])


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
    """Pick video file 720p-1080p to save RAM. Avoid 2K/4K."""
    files = video.get("video_files", [])
    if not files:
        return None
    preferred = [f for f in files if 720 <= f.get("height", 0) <= 1080]
    if preferred:
        preferred.sort(key=lambda f: f.get("height", 0), reverse=True)
        return preferred[0]["link"]
    hd = sorted([f for f in files if f.get("height", 0) >= 720], key=lambda f: f.get("height", 0))
    if hd:
        return hd[0]["link"]
    return sorted(files, key=lambda f: f.get("height", 0), reverse=True)[0]["link"]


def _choose_video(videos: list[dict], used_ids: set) -> dict | None:
    """Choose a video that hasn't been used yet, with duration >= 3s."""
    for v in videos:
        vid = v.get("id")
        if vid in used_ids:
            continue
        if v.get("duration", 0) >= 3:
            return v
    # If all good ones used, pick any unused
    for v in videos:
        if v.get("id") not in used_ids:
            return v
    return None


def get_footage_for_segments(search_queries: list[str], api_key: str, temp_dir: Path) -> list[Path]:
    paths = []
    used_ids: set[int] = set()

    for i, query in enumerate(search_queries):
        logger.info(f"Searching Pexels for: '{query}'")

        # Try page 1 first
        videos = search_videos(query, api_key, page=1)
        chosen = _choose_video(videos, used_ids) if videos else None

        # If all page 1 results used, try page 2
        if not chosen and videos:
            logger.info(f"Page 1 exhausted for '{query}', trying page 2")
            videos2 = search_videos(query, api_key, page=2)
            chosen = _choose_video(videos2, used_ids) if videos2 else None

        # If still nothing, try simpler query
        if not chosen:
            simple_query = query.split()[0] if " " in query else "nature"
            logger.warning(f"No unique results for '{query}', trying '{simple_query}'")
            videos = search_videos(simple_query, api_key, page=random.randint(1, 3))
            chosen = _choose_video(videos, used_ids) if videos else None

        if not chosen:
            raise RuntimeError(f"No stock footage found for query: {query}")

        # Track used video
        used_ids.add(chosen.get("id"))
        logger.info(f"Selected video id={chosen.get('id')} for '{query}' (used: {len(used_ids)})")

        video_url = _pick_best_file(chosen)
        if not video_url:
            raise RuntimeError(f"No downloadable file for query: {query}")

        save_path = temp_dir / f"clip_{i}.mp4"
        download_video(video_url, save_path)
        paths.append(save_path)

    return paths
