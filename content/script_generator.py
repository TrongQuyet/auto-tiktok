import json
import logging
from dataclasses import dataclass

from tenacity import retry, stop_after_attempt, wait_exponential

from config import Settings

logger = logging.getLogger(__name__)


@dataclass
class ContentPlan:
    title: str
    script_segments: list[str]
    caption: str
    hashtags: list[str]
    search_queries: list[str]


def _parse_response(text: str) -> ContentPlan:
    # Extract JSON from response (handle markdown code blocks)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    data = json.loads(text)

    plan = ContentPlan(
        title=data["title"],
        script_segments=data["script_segments"],
        caption=data["caption"],
        hashtags=data["hashtags"],
        search_queries=data["search_queries"],
    )

    # Validate segment/query count match
    if len(plan.script_segments) != len(plan.search_queries):
        raise ValueError(
            f"Segment count ({len(plan.script_segments)}) != "
            f"query count ({len(plan.search_queries)})"
        )

    return plan


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
async def generate_content(niche: str, settings: Settings) -> ContentPlan:
    # Template mode: no AI needed
    if settings.ai_provider == "template":
        from content.templates import get_template

        data = get_template(niche)
        plan = ContentPlan(**data)
        logger.info(f"Template content: {plan.title} ({len(plan.script_segments)} segments)")
        return plan

    from content.prompts import SCRIPT_GENERATION_PROMPT

    prompt = SCRIPT_GENERATION_PROMPT.format(niche=niche)

    if settings.ai_provider == "openai":
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        text = response.choices[0].message.content

    elif settings.ai_provider == "anthropic":
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text

    elif settings.ai_provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = await model.generate_content_async(prompt)
        text = response.text

    else:
        raise ValueError(f"Unknown AI provider: {settings.ai_provider}")

    logger.info(f"AI response received for niche: {niche}")
    plan = _parse_response(text)
    logger.info(f"Content plan: {plan.title} ({len(plan.script_segments)} segments)")
    return plan
