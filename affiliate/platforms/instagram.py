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


async def post_to_instagram(content: str, settings: Settings) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_post, content, settings)


def _sync_post(content: str, settings: Settings) -> dict:
    import undetected_chromedriver as uc

    driver = None
    try:
        options = uc.ChromeOptions()
        profile_dir = settings.chrome_profile_dir / "instagram"
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

        driver.get("https://www.instagram.com")
        time.sleep(3)

        # Check if logged in
        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "svg[aria-label='Home'], [aria-label='New post']")
            ))
        except Exception:
            return {"success": False, "platform": "instagram", "error": "Chưa đăng nhập Instagram. Hãy đăng nhập thủ công tại localhost:6080 trước."}

        # Click the "New post" button (the + icon)
        new_post_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[aria-label='New post'], svg[aria-label='New post']")
        ))
        new_post_btn.click()
        time.sleep(2)

        # Instagram requires an image to post — we'll copy caption to clipboard
        # and inform the user. Full automation requires uploading an image.
        logger.warning("Instagram: Caption prepared but image upload requires manual action or a pre-selected image.")
        return {
            "success": False,
            "platform": "instagram",
            "error": "Instagram yêu cầu upload hình ảnh. Tính năng đang phát triển — hãy post thủ công với caption đã tạo ở trên.",
        }

    except Exception as e:
        logger.error(f"Instagram post failed: {e}")
        return {"success": False, "platform": "instagram", "error": str(e)}
    finally:
        if driver:
            driver.quit()
