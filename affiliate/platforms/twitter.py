import asyncio
import logging
import os
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Settings

logger = logging.getLogger(__name__)


async def post_to_twitter(content: str, affiliate_url: str, settings: Settings) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_post, content, affiliate_url, settings)


def _sync_post(content: str, affiliate_url: str, settings: Settings) -> dict:
    import undetected_chromedriver as uc

    driver = None
    full_text = f"{content}\n{affiliate_url}"

    try:
        options = uc.ChromeOptions()
        profile_dir = settings.chrome_profile_dir / "twitter"
        profile_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={str(profile_dir.resolve())}")
        options.add_argument("--disable-blink-features=AutomationControlled")

        if os.environ.get("DISPLAY"):
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

        driver = uc.Chrome(options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 30)

        driver.get("https://x.com/home")
        time.sleep(3)

        # Check if logged in
        try:
            compose = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']")
            ))
        except Exception:
            return {"success": False, "platform": "twitter", "error": "Chưa đăng nhập Twitter/X. Hãy đăng nhập thủ công tại localhost:6080 trước."}

        compose.click()
        time.sleep(random.uniform(0.8, 1.5))

        for chunk in _chunks(full_text, 40):
            compose.send_keys(chunk)
            time.sleep(random.uniform(0.04, 0.12))

        time.sleep(random.uniform(1.5, 3.0))

        # Post button
        tweet_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-testid='tweetButtonInline']")
        ))
        tweet_btn.click()
        time.sleep(3)

        logger.info("Twitter/X post successful")
        return {"success": True, "platform": "twitter"}

    except Exception as e:
        logger.error(f"Twitter post failed: {e}")
        return {"success": False, "platform": "twitter", "error": str(e)}
    finally:
        if driver:
            driver.quit()


def _chunks(text: str, size: int):
    for i in range(0, len(text), size):
        yield text[i:i + size]
