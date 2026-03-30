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


async def post_to_facebook(content: str, settings: Settings) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_post, content, settings)


def _sync_post(content: str, settings: Settings) -> dict:
    import undetected_chromedriver as uc

    driver = None
    try:
        options = uc.ChromeOptions()
        profile_dir = settings.chrome_profile_dir / "facebook"
        profile_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={str(profile_dir.resolve())}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=vi-VN")

        if os.environ.get("DISPLAY"):
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

        driver = uc.Chrome(options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 30)

        driver.get("https://www.facebook.com")
        time.sleep(3)

        # Check if logged in by looking for the compose area
        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[aria-label=\"What's on your mind?\"], [aria-placeholder=\"What's on your mind?\"]")
            ))
        except Exception:
            return {"success": False, "platform": "facebook", "error": "Chưa đăng nhập Facebook. Hãy đăng nhập thủ công tại localhost:6080 trước."}

        # Click compose box
        compose_box = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[aria-label=\"What's on your mind?\"], [aria-placeholder=\"What's on your mind?\"]")
        ))
        compose_box.click()
        time.sleep(random.uniform(1.5, 2.5))

        # Find the expanded text input
        text_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[contenteditable='true'][role='textbox']")
        ))
        text_input.click()

        # Type with human-like speed
        for chunk in _chunks(content, 40):
            text_input.send_keys(chunk)
            time.sleep(random.uniform(0.04, 0.12))

        time.sleep(random.uniform(2.0, 4.0))

        # Click Post button
        post_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@aria-label='Post' and @role='button']")
        ))
        post_btn.click()
        time.sleep(4)

        logger.info("Facebook post successful")
        return {"success": True, "platform": "facebook"}

    except Exception as e:
        logger.error(f"Facebook post failed: {e}")
        return {"success": False, "platform": "facebook", "error": str(e)}
    finally:
        if driver:
            driver.quit()


def _chunks(text: str, size: int):
    for i in range(0, len(text), size):
        yield text[i:i + size]
