import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    ai_provider: str
    openai_api_key: str
    anthropic_api_key: str
    gemini_api_key: str
    pexels_api_key: str
    pixabay_api_key: str
    coverr_api_key: str
    tiktok_username: str
    tiktok_password: str
    video_width: int
    video_height: int
    video_fps: int
    video_max_duration: int
    tts_voice: str
    output_dir: Path
    temp_dir: Path
    chrome_profile_dir: Path
    default_niche: str
    reddit_client_id: str
    reddit_client_secret: str
    reddit_username: str
    reddit_password: str
    reddit_user_agent: str
    affiliate_post_delay_min: int
    affiliate_post_delay_max: int


def load_settings() -> Settings:
    load_dotenv()

    settings = Settings(
        ai_provider=os.getenv("AI_PROVIDER", "template"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        pexels_api_key=os.getenv("PEXELS_API_KEY", ""),
        pixabay_api_key=os.getenv("PIXABAY_API_KEY", ""),
        coverr_api_key=os.getenv("COVERR_API_KEY", ""),
        tiktok_username=os.getenv("TIKTOK_USERNAME", ""),
        tiktok_password=os.getenv("TIKTOK_PASSWORD", ""),
        video_width=int(os.getenv("VIDEO_WIDTH", "1080")),
        video_height=int(os.getenv("VIDEO_HEIGHT", "1920")),
        video_fps=int(os.getenv("VIDEO_FPS", "30")),
        video_max_duration=int(os.getenv("VIDEO_MAX_DURATION", "60")),
        tts_voice=os.getenv("TTS_VOICE", "en-US-ChristopherNeural"),
        output_dir=Path(os.getenv("OUTPUT_DIR", "./output")),
        temp_dir=Path(os.getenv("TEMP_DIR", "./temp")),
        chrome_profile_dir=Path(os.getenv("CHROME_PROFILE_DIR", "./chrome_profile")),
        default_niche=os.getenv("DEFAULT_NICHE", "motivation"),
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID", ""),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
        reddit_username=os.getenv("REDDIT_USERNAME", ""),
        reddit_password=os.getenv("REDDIT_PASSWORD", ""),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "AffiliateBot/1.0"),
        affiliate_post_delay_min=int(os.getenv("AFFILIATE_POST_DELAY_MIN", "30")),
        affiliate_post_delay_max=int(os.getenv("AFFILIATE_POST_DELAY_MAX", "90")),
    )

    # Validate required keys based on provider
    if settings.ai_provider == "openai" and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
    if settings.ai_provider == "anthropic" and not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic")
    if settings.ai_provider == "gemini" and not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
    if not settings.pexels_api_key and not settings.pixabay_api_key:
        raise ValueError("PEXELS_API_KEY or PIXABAY_API_KEY is required")

    # Ensure directories exist
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)

    return settings
