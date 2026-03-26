import gc
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,
)

from config import Settings
from content.script_generator import ContentPlan
from video.effects import add_text_overlay, apply_ken_burns, crop_to_vertical

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def _build_scene(
    footage_path: Path,
    audio_path: Path,
    text: str,
    target_w: int,
    target_h: int,
    subtitle_style: str = "karaoke",
    word_timings: list[dict] | None = None,
) -> VideoFileClip:
    """Build a single scene: crop footage, match audio duration, add effects."""
    video = VideoFileClip(str(footage_path))
    audio = AudioFileClip(str(audio_path))

    video = crop_to_vertical(video, target_w, target_h)

    audio_duration = audio.duration
    if video.duration < audio_duration:
        loops = int(audio_duration / video.duration) + 1
        from moviepy.editor import concatenate_videoclips as concat
        video = concat([video] * loops)
    video = video.subclip(0, audio_duration)

    video = apply_ken_burns(video, zoom_factor=1.08)
    video = add_text_overlay(video, text, style=subtitle_style, word_timings=word_timings)
    video = video.set_audio(audio)

    return video


def _ffmpeg_concat_simple(scene_paths: list[Path], output_path: Path, settings: Settings) -> None:
    """Concatenate without transitions (hard cut)."""
    concat_list = scene_paths[0].parent / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in scene_paths:
            abs_path = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list.resolve()),
        "-t", str(settings.video_max_duration),
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "medium", "-crf", "18",
        "-r", str(settings.video_fps),
        str(output_path),
    ]

    logger.info(f"FFmpeg concat (simple): {len(scene_paths)} scenes")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    concat_list.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed: {result.stderr[-200:]}")


def _ffmpeg_concat_fade(scene_paths: list[Path], output_path: Path, settings: Settings, fade_duration: float = 0.4) -> None:
    """Concatenate with crossfade transitions between scenes."""
    if len(scene_paths) <= 1:
        return _ffmpeg_concat_simple(scene_paths, output_path, settings)

    # Build xfade filter chain
    # Input: [0:v][1:v][2:v]... → xfade between each pair
    inputs = []
    for p in scene_paths:
        inputs.extend(["-i", str(p.resolve())])

    # Get durations for offset calculation
    durations = []
    for p in scene_paths:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p.resolve())],
            capture_output=True, text=True,
        )
        durations.append(float(probe.stdout.strip() or "5"))

    # Build xfade filter chain
    n = len(scene_paths)
    filter_parts = []
    offset = durations[0] - fade_duration

    # First xfade
    filter_parts.append(f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={max(offset, 0.1)}[v1]")
    # Audio crossfade
    filter_parts.append(f"[0:a][1:a]acrossfade=d={fade_duration}[a1]")

    for i in range(2, n):
        prev_v = f"v{i-1}"
        prev_a = f"a{i-1}"
        offset += durations[i-1] - fade_duration
        filter_parts.append(f"[{prev_v}][{i}:v]xfade=transition=fade:duration={fade_duration}:offset={max(offset, 0.1)}[v{i}]")
        filter_parts.append(f"[{prev_a}][{i}:a]acrossfade=d={fade_duration}[a{i}]")

    last_v = f"[v{n-1}]"
    last_a = f"[a{n-1}]"
    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", last_v, "-map", last_a,
        "-t", str(settings.video_max_duration),
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "medium", "-crf", "18",
        "-r", str(settings.video_fps),
        str(output_path),
    ]

    logger.info(f"FFmpeg concat (fade): {n} scenes, fade={fade_duration}s")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        logger.warning(f"Fade concat failed, falling back to simple: {result.stderr[-200:]}")
        _ffmpeg_concat_simple(scene_paths, output_path, settings)


def _add_bgm(video_path: Path, bgm_style: str, bgm_volume: float = 0.15) -> None:
    """Mix background music into the video in-place."""
    bgm_file = ASSETS_DIR / "bgm" / f"{bgm_style}.mp3"
    if not bgm_file.exists():
        logger.warning(f"BGM file not found: {bgm_file}")
        return

    temp_output = video_path.with_suffix(".bgm.mp4")

    # Get video duration
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)],
        capture_output=True, text=True,
    )
    video_duration = float(probe.stdout.strip() or "30")

    # Mix: loop BGM, lower volume, mix with original audio
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-stream_loop", "-1", "-i", str(bgm_file),
        "-filter_complex",
        f"[1:a]volume={bgm_volume},afade=t=in:st=0:d=1,afade=t=out:st={max(video_duration-2, 0)}:d=2[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        str(temp_output),
    ]

    logger.info(f"Adding BGM: {bgm_style} (volume={bgm_volume})")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        temp_output.replace(video_path)
        logger.info("BGM added successfully")
    else:
        logger.warning(f"BGM mix failed: {result.stderr[-200:]}")
        temp_output.unlink(missing_ok=True)


def _add_sfx(video_path: Path) -> None:
    """Add sound effects: woosh at start, ding between scenes."""
    woosh = ASSETS_DIR / "sfx" / "woosh.mp3"
    ding = ASSETS_DIR / "sfx" / "ding.mp3"

    if not woosh.exists() or not ding.exists():
        logger.warning("SFX files not found")
        return

    temp_output = video_path.with_suffix(".sfx.mp4")

    # Add woosh at 0.0s and ding at 0.5s
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(woosh),
        "-i", str(ding),
        "-filter_complex",
        "[1:a]volume=0.5,adelay=0|0[sfx1];"
        "[2:a]volume=0.4,adelay=500|500[sfx2];"
        "[0:a][sfx1][sfx2]amix=inputs=3:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        str(temp_output),
    ]

    logger.info("Adding SFX...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        temp_output.replace(video_path)
        logger.info("SFX added successfully")
    else:
        logger.warning(f"SFX mix failed: {result.stderr[-200:]}")
        temp_output.unlink(missing_ok=True)


def assemble_video(
    content: ContentPlan,
    footage_paths: list[Path],
    audio_paths: list[Path],
    settings: Settings,
    subtitle_style: str = "karaoke",
    all_word_timings: list[list[dict]] | None = None,
    transition: str = "fade",
    bgm_style: str = "none",
    sfx_enabled: bool = False,
    on_progress: callable = None,
) -> Path:
    """Build the final TikTok video with optional BGM, transitions, and SFX."""
    total = len(footage_paths)
    logger.info(f"Assembling: {content.title} ({total} scenes, sub={subtitle_style}, trans={transition})")

    def report(msg, pct):
        logger.info(msg)
        if on_progress:
            on_progress(msg, pct)

    temp_scene_dir = settings.temp_dir / f"scenes_{datetime.now().strftime('%H%M%S')}"
    temp_scene_dir.mkdir(parents=True, exist_ok=True)
    scene_paths = []

    try:
        # Phase 1: Build each scene
        for i, (footage, audio, text) in enumerate(
            zip(footage_paths, audio_paths, content.script_segments)
        ):
            scene_pct = 60 + int((i / total) * 30)  # 60% → 90%
            report(f"Rendering scene {i + 1}/{total}...", scene_pct)

            timings = all_word_timings[i] if all_word_timings and i < len(all_word_timings) else None
            scene = _build_scene(
                footage, audio, text, settings.video_width, settings.video_height,
                subtitle_style=subtitle_style, word_timings=timings,
            )

            scene_file = temp_scene_dir / f"scene_{i:03d}.mp4"
            scene.write_videofile(
                str(scene_file),
                codec="libx264", audio_codec="aac",
                fps=settings.video_fps, preset="fast",
                threads=2, logger=None,
            )
            scene_paths.append(scene_file)

            scene.close()
            del scene
            gc.collect()

        # Phase 2: Concat
        report(f"Ghép {total} scenes...", 92)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = settings.output_dir / f"video_{timestamp}.mp4"

        if transition == "fade":
            _ffmpeg_concat_fade(scene_paths, output_path, settings)
        else:
            _ffmpeg_concat_simple(scene_paths, output_path, settings)

        # Phase 3: Add BGM
        if bgm_style and bgm_style != "none":
            report(f"Thêm nhạc nền ({bgm_style})...", 95)
            _add_bgm(output_path, bgm_style)

        # Phase 4: Add SFX
        if sfx_enabled:
            report("Thêm sound effects...", 97)
            _add_sfx(output_path)

        report(f"Video exported: {output_path}", 99)
        return output_path

    finally:
        shutil.rmtree(temp_scene_dir, ignore_errors=True)
