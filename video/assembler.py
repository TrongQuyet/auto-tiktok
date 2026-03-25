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


def _build_scene(
    footage_path: Path,
    audio_path: Path,
    text: str,
    target_w: int,
    target_h: int,
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
    video = add_text_overlay(video, text)
    video = video.set_audio(audio)

    return video


def _ffmpeg_concat(scene_paths: list[Path], output_path: Path, settings: Settings) -> None:
    """Concatenate scene files using FFmpeg concat demuxer (near-zero RAM)."""
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
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "medium",
        "-crf", "23",
        "-r", str(settings.video_fps),
        str(output_path),
    ]

    logger.info(f"FFmpeg concat: {len(scene_paths)} scenes")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    concat_list.unlink(missing_ok=True)

    if result.returncode != 0:
        logger.error(f"FFmpeg concat error: {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg concat failed: {result.stderr[-200:]}")


def assemble_video(
    content: ContentPlan,
    footage_paths: list[Path],
    audio_paths: list[Path],
    settings: Settings,
) -> Path:
    """Build the final TikTok video, one scene at a time to save RAM."""
    logger.info(f"Assembling video: {content.title}")

    temp_scene_dir = settings.temp_dir / f"scenes_{datetime.now().strftime('%H%M%S')}"
    temp_scene_dir.mkdir(parents=True, exist_ok=True)
    scene_paths = []

    try:
        # Phase 1: Build and export each scene individually, free RAM after each
        for i, (footage, audio, text) in enumerate(
            zip(footage_paths, audio_paths, content.script_segments)
        ):
            logger.info(f"Building scene {i + 1}/{len(footage_paths)}")
            scene = _build_scene(
                footage, audio, text, settings.video_width, settings.video_height
            )

            scene_file = temp_scene_dir / f"scene_{i:03d}.mp4"
            scene.write_videofile(
                str(scene_file),
                codec="libx264",
                audio_codec="aac",
                fps=settings.video_fps,
                preset="ultrafast",
                threads=2,
                logger=None,
            )
            scene_paths.append(scene_file)

            # Free RAM immediately
            scene.close()
            del scene
            gc.collect()
            logger.info(f"Scene {i + 1} exported, memory freed")

        # Phase 2: FFmpeg concat (near-zero RAM)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = settings.output_dir / f"video_{timestamp}.mp4"
        _ffmpeg_concat(scene_paths, output_path, settings)

        logger.info(f"Video exported: {output_path}")
        return output_path

    finally:
        shutil.rmtree(temp_scene_dir, ignore_errors=True)
