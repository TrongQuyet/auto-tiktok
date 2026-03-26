import logging
import re

import requests
from deep_translator import GoogleTranslator

from content.script_generator import ContentPlan

logger = logging.getLogger(__name__)

REDDIT_HEADERS = {"User-Agent": "AutoTikTok/1.0"}

SUBREDDIT_MAP = {
    "todayilearned": "Today I Learned",
    "showerthoughts": "Shower Thoughts",
    "funfacts": "Fun Facts",
    "didyouknow": "Did You Know",
    "animalfacts": "Animal Facts",
    "spacefacts": "Space Facts",
    "historyfacts": "History Facts",
    # Funny/Meme
    "Jokes": "Jokes",
    "dadjokes": "Dad Jokes",
    "AnimalsBeingDerps": "Animals Being Derps",
    "AnimalsBeingJerks": "Animals Being Jerks",
    "aww": "Cute Animals",
    "meirl": "Me In Real Life",
}


def crawl_reddit(subreddit: str = "todayilearned", limit: int = 20) -> list[str]:
    """Crawl top posts from a subreddit using public JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    params = {"limit": limit, "t": "week"}

    resp = requests.get(url, headers=REDDIT_HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    posts = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        title = post.get("title", "").strip()
        selftext = post.get("selftext", "").strip()

        if post.get("stickied") or not title:
            continue

        # Clean up TIL prefix
        title = re.sub(r"^TIL\s+(?:that\s+)?", "", title, flags=re.IGNORECASE)

        # For joke subreddits: combine title (setup) + selftext (punchline)
        if selftext and len(selftext) < 300:
            combined = f"{title} {selftext}"
            if len(combined) > 20:
                posts.append(combined)
        elif len(title) > 20:
            posts.append(title)

    logger.info(f"Crawled {len(posts)} posts from r/{subreddit}")
    return posts


def crawl_wikipedia(topic: str, sentences: int = 8) -> list[str]:
    """Get summary sentences from Wikipedia API."""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_")

    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        # Try search
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "opensearch",
            "search": topic,
            "limit": 1,
            "format": "json",
        }
        search_resp = requests.get(search_url, params=search_params, timeout=15)
        results = search_resp.json()
        if len(results) > 1 and results[1]:
            actual_title = results[1][0]
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + actual_title.replace(" ", "_")
            resp = requests.get(url, timeout=15)

    if resp.status_code != 200:
        raise RuntimeError(f"Wikipedia article not found for: {topic}")

    data = resp.json()
    extract = data.get("extract", "")

    # Split into sentences
    raw_sentences = re.split(r'(?<=[.!?])\s+', extract)
    result = [s.strip() for s in raw_sentences if len(s.strip()) > 20][:sentences]

    logger.info(f"Wikipedia '{topic}': {len(result)} sentences")
    return result


def translate_to_vi(texts: list[str]) -> list[str]:
    """Translate English texts to Vietnamese using Google Translate."""
    translator = GoogleTranslator(source="en", target="vi")
    translated = []
    for text in texts:
        try:
            result = translator.translate(text[:500])
            translated.append(result or text)
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            translated.append(text)
    logger.info(f"Translated {len(translated)} texts to Vietnamese")
    return translated


def crawl_and_generate(source: str, topic: str, count: int = 5) -> ContentPlan:
    """
    Crawl content from source, translate to Vietnamese, create ContentPlan.
    source: "reddit" or "wikipedia"
    topic: subreddit name (for reddit) or article topic (for wikipedia)
    """
    if source == "reddit":
        subreddit = topic.replace("r/", "").strip()
        english_texts = crawl_reddit(subreddit, limit=20)
        if not english_texts:
            raise RuntimeError(f"No content found in r/{subreddit}")
        # Pick random subset
        import random
        selected = random.sample(english_texts, min(count, len(english_texts)))
        title = f"Facts from r/{subreddit}"

    elif source == "wikipedia":
        english_texts = crawl_wikipedia(topic, sentences=count + 2)
        if not english_texts:
            raise RuntimeError(f"No Wikipedia content for: {topic}")
        selected = english_texts[:count]
        title = f"Facts about {topic}"

    else:
        raise ValueError(f"Unknown source: {source}")

    # Translate to Vietnamese
    vi_texts = translate_to_vi(selected)

    # Generate search queries (keep English for Pexels, or Vietnamese for Pixabay)
    search_queries = []
    for en_text in selected:
        words = en_text.split()
        # Extract 2-3 key nouns
        skip = {"the", "a", "an", "is", "are", "was", "were", "of", "to", "in",
                "and", "that", "it", "for", "you", "has", "have", "with", "from",
                "this", "not", "but", "can", "been", "than", "more", "its"}
        key_words = [w.strip(".,!?()\"'") for w in words if w.lower().strip(".,!?()\"'") not in skip and len(w) > 2]
        query = " ".join(key_words[:3]) if key_words else "nature"
        search_queries.append(query)

    # Build hashtags
    hashtags = ["#fyp", "#facts", "#viral", "#trending"]
    if source == "reddit":
        hashtags.append(f"#reddit")
        hashtags.append(f"#{topic.lower()}")
    else:
        hashtags.append("#wikipedia")
        hashtags.append(f"#{topic.lower().replace(' ', '')}")

    caption = f"Những sự thật thú vị về {topic}"

    plan = ContentPlan(
        title=title,
        script_segments=vi_texts,
        caption=caption[:150],
        hashtags=hashtags[:7],
        search_queries=search_queries,
    )

    logger.info(f"Crawled content plan: {plan.title} ({len(plan.script_segments)} segments)")
    return plan
