import asyncio
import logging

from config import Settings

logger = logging.getLogger(__name__)


async def post_to_reddit(content: str, subreddits: list[str], settings: Settings) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_post, content, subreddits, settings)


def _sync_post(content: str, subreddits: list[str], settings: Settings) -> dict:
    try:
        import praw

        if not settings.reddit_client_id or not settings.reddit_client_secret:
            return {"success": False, "platform": "reddit", "error": "Chưa cấu hình REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET trong .env"}

        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            username=settings.reddit_username,
            password=settings.reddit_password,
            user_agent=settings.reddit_user_agent or f"AffiliateBot/1.0 by {settings.reddit_username}",
        )

        results = []
        for sub_name in subreddits:
            sub_name = sub_name.strip().lstrip("r/")
            try:
                subreddit = reddit.subreddit(sub_name)
                # Comment on the top non-stickied hot post
                for post in subreddit.hot(limit=5):
                    if not post.stickied:
                        post.reply(content)
                        logger.info(f"Reddit comment posted on r/{sub_name}: {post.title[:60]}")
                        results.append({"subreddit": sub_name, "success": True})
                        break
            except Exception as e:
                logger.error(f"Reddit r/{sub_name} failed: {e}")
                results.append({"subreddit": sub_name, "success": False, "error": str(e)})

        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count > 0,
            "platform": "reddit",
            "results": results,
        }

    except ImportError:
        return {"success": False, "platform": "reddit", "error": "Thư viện praw chưa được cài. Chạy: pip install praw"}
    except Exception as e:
        logger.error(f"Reddit post failed: {e}")
        return {"success": False, "platform": "reddit", "error": str(e)}
