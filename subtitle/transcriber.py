import logging
from pathlib import Path

import whisper

logger = logging.getLogger(__name__)

_model = None


def _get_model(model_size: str = "base"):
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model '{model_size}'... (first time may take a while)")
        _model = whisper.load_model(model_size)
        logger.info("Whisper model loaded")
    return _model


def transcribe(video_path: Path, language: str = "zh", model_size: str = "base") -> list[dict]:
    """
    Transcribe audio from video file.
    Returns list of segments: [{"start": 0.0, "end": 2.5, "text": "..."}]
    """
    model = _get_model(model_size)

    logger.info(f"Transcribing: {video_path.name} (language={language})")
    result = model.transcribe(
        str(video_path),
        language=language,
        task="transcribe",
    )

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })

    logger.info(f"Transcribed {len(segments)} segments")
    return segments
