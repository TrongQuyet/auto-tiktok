import logging
import random
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def search_videos(query: str, api_key: str, orientation: str = "portrait", per_page: int = 5) -> list[dict]:
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": per_page,
        "size": "large",
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
    # Prefer 720-1080p range
    preferred = [f for f in files if 720 <= f.get("height", 0) <= 1080]
    if preferred:
        preferred.sort(key=lambda f: f.get("height", 0), reverse=True)
        return preferred[0]["link"]
    # Fallback: smallest file >= 720p
    hd = sorted([f for f in files if f.get("height", 0) >= 720], key=lambda f: f.get("height", 0))
    if hd:
        return hd[0]["link"]
    # Last resort
    return sorted(files, key=lambda f: f.get("height", 0), reverse=True)[0]["link"]


def get_footage_for_segments(search_queries: list[str], api_key: str, temp_dir: Path) -> list[Path]:
    paths = []
    for i, query in enumerate(search_queries):
        logger.info(f"Searching Pexels for: '{query}'")
        videos = search_videos(query, api_key)

        if not videos:
            # Try simpler query
            simple_query = query.split()[0] if " " in query else "nature"
            logger.warning(f"No results for '{query}', trying '{simple_query}'")
            videos = search_videos(simple_query, api_key)

        if not videos:
            raise RuntimeError(f"No stock footage found for query: {query}")

        video_url = _pick_best_file(random.choice(videos))
        if not video_url:
            raise RuntimeError(f"No downloadable file for query: {query}")

        save_path = temp_dir / f"clip_{i}.mp4"
        download_video(video_url, save_path)
        paths.append(save_path)

    return paths
