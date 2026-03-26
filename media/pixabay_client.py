import logging
import random
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def search_videos(query: str, api_key: str, per_page: int = 15, page: int = 1, lang: str = "vi") -> list[dict]:
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": api_key,
        "q": query,
        "lang": lang,
        "video_type": "film",
        "per_page": min(per_page, 200),
        "page": page,
        "safesearch": "true",
        "min_width": 720,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("hits", [])


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
    """Pick video URL from Pixabay result. Prefer medium (960p) or large (1920p)."""
    videos = video.get("videos", {})

    # Prefer medium (960p) - good quality, not too large
    medium = videos.get("medium", {})
    if medium.get("url"):
        return medium["url"]

    # Fallback to large
    large = videos.get("large", {})
    if large.get("url"):
        return large["url"]

    # Fallback to small
    small = videos.get("small", {})
    if small.get("url"):
        return small["url"]

    return None


def _choose_video(videos: list[dict], used_ids: set) -> dict | None:
    """Choose a video not yet used, with duration >= 3s."""
    for v in videos:
        vid = v.get("id")
        if vid in used_ids:
            continue
        if v.get("duration", 0) >= 3:
            return v
    for v in videos:
        if v.get("id") not in used_ids:
            return v
    return None


def get_footage_for_segments(search_queries: list[str], api_key: str, temp_dir: Path) -> list[Path]:
    paths = []
    used_ids: set[int] = set()

    for i, query in enumerate(search_queries):
        logger.info(f"Searching Pixabay for: '{query}'")

        videos = search_videos(query, api_key, page=1)
        chosen = _choose_video(videos, used_ids) if videos else None

        if not chosen and videos:
            logger.info(f"Page 1 exhausted for '{query}', trying page 2")
            videos2 = search_videos(query, api_key, page=2)
            chosen = _choose_video(videos2, used_ids) if videos2 else None

        if not chosen:
            simple_query = query.split()[0] if " " in query else "nature"
            logger.warning(f"No unique results for '{query}', trying '{simple_query}'")
            videos = search_videos(simple_query, api_key, page=random.randint(1, 3))
            chosen = _choose_video(videos, used_ids) if videos else None

        if not chosen:
            raise RuntimeError(f"No stock footage found on Pixabay for: {query}")

        used_ids.add(chosen.get("id"))
        logger.info(f"Selected Pixabay video id={chosen.get('id')} for '{query}'")

        video_url = _pick_best_file(chosen)
        if not video_url:
            raise RuntimeError(f"No downloadable file for query: {query}")

        save_path = temp_dir / f"clip_{i}.mp4"
        download_video(video_url, save_path)
        paths.append(save_path)

    return paths
