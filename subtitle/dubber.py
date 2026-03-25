import asyncio
import logging
import shutil
import subprocess
from pathlib import Path

import edge_tts

logger = logging.getLogger(__name__)


async def _generate_tts(text: str, voice: str, output_path: Path) -> Path:
    """Generate TTS audio for a single segment."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


def _get_duration(path: Path) -> float:
    """Get audio/video duration using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def _build_dubbed_audio(
    video_path: Path,
    tts_paths: list[Path],
    segments: list[dict],
    output_audio: Path,
    original_volume: float = 0.1,
) -> None:
    """
    Build dubbed audio track using FFmpeg:
    - Original audio at lowered volume
    - TTS segments placed at correct timestamps with speed adjustment
    """
    inputs = ["-i", str(video_path)]
    for p in tts_paths:
        inputs.extend(["-i", str(p)])

    filters = []

    # Lower original audio volume
    filters.append(f"[0:a]volume={original_volume}[orig]")

    # Process each TTS segment: adjust speed to fit + delay to correct position
    for i, (tts_path, seg) in enumerate(zip(tts_paths, segments)):
        input_idx = i + 1
        delay_ms = int(seg["start"] * 1000)
        seg_dur = seg["end"] - seg["start"]

        parts = []

        # Speed adjustment to fit segment duration
        try:
            tts_dur = _get_duration(tts_path)
            if seg_dur > 0.1 and tts_dur > 0.1:
                ratio = tts_dur / seg_dur
                # Only adjust if significantly off, clamp to safe range
                if abs(ratio - 1.0) > 0.15:
                    tempo = max(0.5, min(ratio, 2.0))
                    parts.append(f"atempo={tempo:.2f}")
        except (ValueError, subprocess.SubprocessError):
            pass

        parts.append(f"adelay={delay_ms}|{delay_ms}")
        filters.append(f"[{input_idx}:a]{','.join(parts)}[tts{i}]")

    # Mix all: original (lowered) + all TTS segments
    # normalize=0 prevents amix from reducing volume per input count
    n = 1 + len(tts_paths)
    mix_labels = "[orig]" + "".join(f"[tts{i}]" for i in range(len(tts_paths)))
    filters.append(f"{mix_labels}amix=inputs={n}:duration=first:dropout_transition=0:normalize=0[out]")

    filter_complex = ";".join(filters)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k",
        str(output_audio),
    ]

    logger.info(f"Building dubbed audio ({len(tts_paths)} segments)...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        logger.error(f"FFmpeg error: {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg dubbed audio failed: {result.stderr[-200:]}")


def _replace_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    """Replace video's audio track with dubbed audio."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg merge failed: {result.stderr[-200:]}")


async def dub_video(
    video_path: Path,
    segments: list[dict],
    voice: str,
    output_path: Path,
    original_volume: float = 0.1,
    temp_dir: Path | None = None,
) -> Path:
    """
    Full dubbing pipeline:
    1. Generate Vietnamese TTS for each translated segment
    2. Build dubbed audio (original lowered + TTS at correct timestamps)
    3. Replace video audio with dubbed track

    segments: [{"start": 0.0, "end": 2.5, "text": "translated text", ...}]
    """
    if temp_dir is None:
        temp_dir = output_path.parent / "temp_dub"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Generate TTS for each segment
        logger.info(f"Generating dubbed TTS ({len(segments)} segments, voice={voice})...")
        tts_paths = []
        for i, seg in enumerate(segments):
            if not seg["text"].strip():
                continue
            tts_path = temp_dir / f"dub_{i:03d}.mp3"
            await _generate_tts(seg["text"], voice, tts_path)
            tts_paths.append(tts_path)
            logger.info(f"TTS {i + 1}/{len(segments)}: {seg['text'][:40]}...")

        if not tts_paths:
            raise RuntimeError("No TTS segments generated")

        # Filter segments to match tts_paths (skip empty)
        valid_segments = [s for s in segments if s["text"].strip()]

        # Step 2: Build dubbed audio track
        dubbed_audio = temp_dir / "dubbed_audio.aac"
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, _build_dubbed_audio,
            video_path, tts_paths, valid_segments, dubbed_audio, original_volume,
        )

        # Step 3: Replace video audio
        logger.info("Merging dubbed audio with video...")
        await loop.run_in_executor(
            None, _replace_audio, video_path, dubbed_audio, output_path,
        )

        logger.info(f"Dubbed video saved: {output_path}")
        return output_path

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
