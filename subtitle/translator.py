import json
import logging
import os
import time

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

LANG_NAMES = {
    "zh-CN": "Chinese", "zh": "Chinese",
    "ja": "Japanese", "ko": "Korean",
    "en": "English", "vi": "Vietnamese",
}


def _translate_with_ai(segments: list[dict], source: str, target: str) -> list[str] | None:
    """Try translating all segments at once using AI for better context."""
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    texts = [seg["text"] for seg in segments]
    src_name = LANG_NAMES.get(source, source)
    tgt_name = LANG_NAMES.get(target, target)

    prompt = (
        f"Translate the following {src_name} sentences to {tgt_name}. "
        f"These are subtitles from a video, so keep translations natural and conversational. "
        f"Return ONLY a JSON array of translated strings, same order and count as input.\n\n"
        f"Input:\n{json.dumps(texts, ensure_ascii=False)}"
    )

    result_text = None

    try:
        if gemini_key:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt,
            )
            result_text = response.text
        elif openai_key:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            result_text = response.choices[0].message.content
        elif anthropic_key:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            result_text = response.content[0].text
        else:
            return None
    except Exception as e:
        logger.warning(f"AI translation failed, falling back to Google: {e}")
        return None

    # Parse JSON array from response
    try:
        result_text = result_text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]
        translations = json.loads(result_text)
        if isinstance(translations, list) and len(translations) == len(texts):
            return translations
        logger.warning(f"AI returned {len(translations)} translations for {len(texts)} segments, falling back")
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse AI translation: {e}")

    return None


def _translate_with_google(segments: list[dict], source: str, target: str) -> list[str]:
    """Fallback: translate segment by segment with Google Translate."""
    translator = GoogleTranslator(source=source, target=target)
    results = []
    for i, seg in enumerate(segments):
        try:
            result = translator.translate(seg["text"])
            results.append(result or seg["text"])
        except Exception as e:
            logger.warning(f"Google translation failed for segment {i}: {e}")
            results.append(seg["text"])
        if (i + 1) % 10 == 0:
            time.sleep(0.5)
    return results


def translate_segments(segments: list[dict], source: str = "zh-CN", target: str = "vi") -> list[dict]:
    """
    Translate text in each segment.
    Uses AI (Gemini/OpenAI/Anthropic) if API key available, otherwise Google Translate.
    """
    # Try AI translation first (better quality, context-aware)
    ai_results = _translate_with_ai(segments, source, target)

    if ai_results:
        logger.info(f"AI translated {len(segments)} segments: {source} -> {target}")
        translations = ai_results
    else:
        logger.info(f"Using Google Translate for {len(segments)} segments")
        translations = _translate_with_google(segments, source, target)

    translated = []
    for seg, trans in zip(segments, translations):
        translated.append({
            **seg,
            "original": seg["text"],
            "text": trans,
        })

    logger.info(f"Translated {len(translated)} segments: {source} -> {target}")
    return translated
