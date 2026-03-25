import logging
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
    # Load clips
    video = VideoFileClip(str(footage_path))
    audio = AudioFileClip(str(audio_path))

    # Crop to vertical
    video = crop_to_vertical(video, target_w, target_h)

    # Match video duration to audio
    audio_duration = audio.duration
    if video.duration < audio_duration:
        # Loop video to match audio
        loops = int(audio_duration / video.duration) + 1
        from moviepy.editor import concatenate_videoclips as concat
        video = concat([video] * loops)
    video = video.subclip(0, audio_duration)

    # Apply Ken Burns zoom
    video = apply_ken_burns(video, zoom_factor=1.08)

    # Add text overlay
    video = add_text_overlay(video, text)

    # Set audio
    video = video.set_audio(audio)

    return video


def assemble_video(
    content: ContentPlan,
    footage_paths: list[Path],
    audio_paths: list[Path],
    settings: Settings,
) -> Path:
    """Build the final TikTok video from all scenes."""
    logger.info(f"Assembling video: {content.title}")

    scenes = []
    for i, (footage, audio, text) in enumerate(
        zip(footage_paths, audio_paths, content.script_segments)
    ):
        logger.info(f"Building scene {i + 1}/{len(footage_paths)}")
        scene = _build_scene(
            footage, audio, text, settings.video_width, settings.video_height
        )
        scenes.append(scene)

    # Concatenate all scenes
    final = concatenate_videoclips(scenes, method="compose")

    # Enforce max duration
    if final.duration > settings.video_max_duration:
        final = final.subclip(0, settings.video_max_duration)

    # Export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = settings.output_dir / f"video_{timestamp}.mp4"

    logger.info(f"Exporting video to: {output_path}")
    final.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=settings.video_fps,
        preset="medium",
        threads=4,
    )

    # Cleanup moviepy clips
    final.close()
    for scene in scenes:
        scene.close()

    logger.info(f"Video exported: {output_path}")
    return output_path
