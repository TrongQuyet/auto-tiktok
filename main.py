import asyncio
import logging
import shutil
import sys
from pathlib import Path

from config import load_settings
from content.script_generator import generate_content
from media.pexels_client import get_footage_for_segments
from media.tts import generate_voiceover
from uploader.tiktok import TikTokUploader
from video.assembler import assemble_video

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("auto.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("auto")


async def run(niche: str | None = None, upload: bool = True):
    settings = load_settings()
    niche = niche or settings.default_niche

    # Clean temp directory
    if settings.temp_dir.exists():
        shutil.rmtree(settings.temp_dir)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate content plan via AI
    logger.info(f"=== Generating content for niche: {niche} ===")
    content = await generate_content(niche, settings)
    logger.info(f"Title: {content.title}")
    logger.info(f"Segments: {len(content.script_segments)}")
    logger.info(f"Caption: {content.caption}")

    # Step 2: Download footage and generate TTS in parallel
    logger.info("=== Downloading footage & generating voiceover ===")

    # Run Pexels download in executor (sync) while TTS runs async
    loop = asyncio.get_event_loop()
    footage_task = loop.run_in_executor(
        None,
        get_footage_for_segments,
        content.search_queries,
        settings.pexels_api_key,
        settings.temp_dir,
    )
    tts_task = generate_voiceover(
        content.script_segments, settings.tts_voice, settings.temp_dir
    )

    footage_paths, audio_paths = await asyncio.gather(footage_task, tts_task)
    logger.info(f"Downloaded {len(footage_paths)} clips, {len(audio_paths)} audio files")

    # Step 3: Assemble video
    logger.info("=== Assembling video ===")
    video_path = assemble_video(content, footage_paths, audio_paths, settings)
    logger.info(f"Video saved: {video_path}")

    # Step 4: Upload to TikTok
    if upload:
        logger.info("=== Uploading to TikTok ===")
        uploader = TikTokUploader(settings)
        try:
            uploader.start_browser()
            uploader.login()
            success = uploader.upload_video(video_path, content.caption, content.hashtags)
            if success:
                logger.info("=== Successfully posted to TikTok! ===")
            else:
                logger.error("Upload failed. Video saved locally at: %s", video_path)
        finally:
            uploader.close()
    else:
        logger.info("Upload skipped (--no-upload). Video at: %s", video_path)

    # Cleanup temp
    shutil.rmtree(settings.temp_dir, ignore_errors=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)

    return video_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto TikTok Video Generator")
    parser.add_argument("--niche", type=str, help="Content niche/topic (e.g., 'motivation', 'fun facts')")
    parser.add_argument("--no-upload", action="store_true", help="Generate video only, skip TikTok upload")
    args = parser.parse_args()

    video = asyncio.run(run(niche=args.niche, upload=not args.no_upload))
    print(f"\nDone! Video: {video}")


if __name__ == "__main__":
    main()
