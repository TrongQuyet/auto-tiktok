import logging
import time

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


def translate_segments(segments: list[dict], source: str = "zh-CN", target: str = "vi") -> list[dict]:
    """
    Translate text in each segment from source to target language.
    Returns new list with translated text added.
    """
    translator = GoogleTranslator(source=source, target=target)
    translated = []

    for i, seg in enumerate(segments):
        original = seg["text"]
        try:
            result = translator.translate(original)
            translated.append({
                **seg,
                "original": original,
                "text": result or original,
            })
        except Exception as e:
            logger.warning(f"Translation failed for segment {i}: {e}")
            translated.append({
                **seg,
                "original": original,
                "text": original,
            })
        # Rate limit
        if (i + 1) % 10 == 0:
            time.sleep(0.5)

    logger.info(f"Translated {len(translated)} segments: {source} -> {target}")
    return translated
