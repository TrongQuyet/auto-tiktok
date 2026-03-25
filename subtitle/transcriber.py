import json
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _extract_audio(video_path: Path, output_path: Path) -> Path:
    """Extract audio from video using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn", "-acodec", "libmp3lame",
        "-ar", "16000", "-ac", "1",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def _transcribe_gemini(audio_path: Path, language: str) -> list[dict]:
    """Transcribe audio using Gemini 2.0 Flash."""
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required for transcription")

    client = genai.Client(api_key=api_key)

    lang_names = {
        "zh": "Chinese", "ja": "Japanese",
        "ko": "Korean", "en": "English",
        "vi": "Vietnamese",
    }
    lang_name = lang_names.get(language, language)

    prompt = (
        f"Transcribe this {lang_name} audio precisely. "
        f"Return ONLY a JSON array of segments with start/end timestamps (seconds) and text. "
        f"Format: [{{\"start\": 0.0, \"end\": 2.5, \"text\": \"...\"}}, ...]\n"
        f"Rules:\n"
        f"- Transcribe exactly what is spoken, do NOT translate\n"
        f"- Each segment should be a natural sentence or phrase\n"
        f"- Timestamps must be accurate to 0.1 seconds\n"
        f"- Return ONLY the JSON array, no other text"
    )

    logger.info("Uploading audio to Gemini...")
    audio_file = client.files.upload(file=str(audio_path))

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[prompt, audio_file],
    )

    # Clean up uploaded file
    try:
        client.files.delete(name=audio_file.name)
    except Exception:
        pass

    # Parse response
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]

    segments = json.loads(text)
    return [s for s in segments if s.get("text", "").strip()]


def _transcribe_whisper(video_path: Path, language: str, model_size: str) -> list[dict]:
    """Fallback: transcribe using local Whisper model."""
    import whisper

    logger.info(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    result = model.transcribe(
        str(video_path),
        language=language,
        task="transcribe",
    )

    segments = []
    for seg in result["segments"]:
        text = seg["text"].strip()
        if not text:
            continue
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": text,
        })
    return segments


def transcribe(video_path: Path, language: str = "zh", model_size: str = "small") -> list[dict]:
    """
    Transcribe audio from video file.
    Uses Gemini if API key available, otherwise falls back to Whisper.
    Returns list of segments: [{"start": 0.0, "end": 2.5, "text": "..."}]
    """
    # Try Gemini first (more accurate, no RAM needed)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            logger.info(f"Transcribing with Gemini: {video_path.name} (language={language})")
            audio_path = video_path.parent / f"{video_path.stem}_audio.mp3"
            _extract_audio(video_path, audio_path)
            segments = _transcribe_gemini(audio_path, language)
            audio_path.unlink(missing_ok=True)
            logger.info(f"Gemini transcribed {len(segments)} segments")
            return segments
        except Exception as e:
            logger.warning(f"Gemini transcription failed: {e}, falling back to Whisper")

    # Fallback to Whisper (local, offline)
    logger.info(f"Transcribing with Whisper: {video_path.name} (language={language}, model={model_size})")
    segments = _transcribe_whisper(video_path, language, model_size)
    logger.info(f"Whisper transcribed {len(segments)} segments")
    return segments
