import json
import logging
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)


async def generate_single(text: str, voice: str, output_path: Path, rate: str = "+0%") -> tuple[Path, list[dict]]:
    """
    Generate TTS audio and capture word-level timestamps.
    rate: speed adjustment, e.g. "+0%", "+20%", "+50%", "-10%"
    Returns (audio_path, word_timings)
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    word_timings = []

    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                offset_ms = chunk["offset"] / 10000  # Convert 100ns units to ms
                duration_ms = chunk["duration"] / 10000
                word_timings.append({
                    "word": chunk["text"],
                    "start": offset_ms / 1000,  # Convert to seconds
                    "end": (offset_ms + duration_ms) / 1000,
                })

    logger.info(f"TTS generated: {output_path} ({len(word_timings)} word timings)")
    return output_path, word_timings


async def generate_voiceover(
    segments: list[str], voice: str, temp_dir: Path, rate: str = "+0%"
) -> tuple[list[Path], list[list[dict]]]:
    """
    Generate voiceover for all segments.
    Returns (audio_paths, all_word_timings).
    """
    paths = []
    all_timings = []
    for i, segment in enumerate(segments):
        output_path = temp_dir / f"audio_{i}.mp3"
        audio_path, timings = await generate_single(segment, voice, output_path, rate=rate)
        paths.append(audio_path)
        all_timings.append(timings)

    # Save timings to JSON for debugging
    timings_path = temp_dir / "word_timings.json"
    with open(timings_path, "w", encoding="utf-8") as f:
        json.dump(all_timings, f, ensure_ascii=False, indent=2)

    return paths, all_timings
