import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def segments_to_srt(segments: list[dict]) -> str:
    """Convert segments to SRT format string."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _format_time(seg["start"])
        end = _format_time(seg["end"])
        text = seg["text"]
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def _format_time(seconds: float) -> str:
    """Format seconds to SRT time format: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def burn_subtitles(
    video_path: Path,
    segments: list[dict],
    output_path: Path,
    font_size: int = 18,
    font_name: str = "Liberation Sans",
    margin_v: int = 30,
) -> Path:
    """
    Burn subtitles into video using FFmpeg ASS filter.
    Returns path to output video.
    """
    # Write SRT to temp file
    srt_path = output_path.with_suffix(".srt")
    srt_content = segments_to_srt(segments)
    srt_path.write_text(srt_content, encoding="utf-8")
    logger.info(f"SRT saved: {srt_path}")

    # Build FFmpeg command with subtitles filter
    # Use force_style for Vietnamese font support
    style = (
        f"FontName={font_name},"
        f"FontSize={font_size},"
        f"PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"BorderStyle=3,"
        f"Outline=2,"
        f"Shadow=1,"
        f"MarginV={margin_v},"
        f"Alignment=2"
    )

    srt_path_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles='{srt_path_escaped}':force_style='{style}'",
        "-c:a", "copy",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        str(output_path),
    ]

    logger.info(f"Burning subtitles into video...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        logger.error(f"FFmpeg error: {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg failed: {result.stderr[-200:]}")

    # Clean up temp SRT
    srt_path.unlink(missing_ok=True)

    logger.info(f"Subtitled video saved: {output_path}")
    return output_path
