import logging
import os
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Settings

logger = logging.getLogger(__name__)

TIKTOK_UPLOAD_URL = "https://www.tiktok.com/creator#/upload?scene=creator_center"


class TikTokUploader:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.driver = None

    def start_browser(self):
        import undetected_chromedriver as uc

        options = uc.ChromeOptions()
        profile_dir = str(self.settings.chrome_profile_dir.resolve())
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=en-US")

        # Docker/Linux: add flags for running in container
        if os.environ.get("DISPLAY"):
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()
        logger.info("Browser started with persistent profile")

    def login(self):
        """Navigate to TikTok. If not logged in, pause for manual login."""
        self.driver.get("https://www.tiktok.com")
        time.sleep(3)

        # Check if already logged in by looking for upload button or profile icon
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='upload-icon']"))
            )
            logger.info("Already logged in to TikTok")
        except Exception:
            logger.info("Not logged in. Please log in manually in the browser window.")
            logger.info("After logging in, press Enter in the terminal to continue...")
            input(">>> Press Enter after you've logged in to TikTok... ")
            time.sleep(2)

    def upload_video(self, video_path: Path, caption: str, hashtags: list[str]) -> bool:
        """Upload a video to TikTok via the web creator tools."""
        try:
            logger.info(f"Navigating to TikTok upload page...")
            self.driver.get(TIKTOK_UPLOAD_URL)
            time.sleep(5)

            # Find the file input and upload the video
            file_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(str(video_path.resolve()))
            logger.info("Video file selected for upload")

            # Wait for upload to process
            time.sleep(10)

            # Build caption text with hashtags
            full_caption = f"{caption} {' '.join(hashtags)}"

            # Find and fill the caption editor
            try:
                # Try the contenteditable div (TikTok's rich text editor)
                caption_editor = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[contenteditable='true']")
                    )
                )
                # Clear existing text
                caption_editor.clear()
                time.sleep(1)

                # Type caption using JavaScript to handle the rich text editor
                self.driver.execute_script(
                    "arguments[0].textContent = arguments[1];",
                    caption_editor,
                    full_caption,
                )
                # Trigger input event so TikTok registers the change
                self.driver.execute_script(
                    """
                    var event = new Event('input', { bubbles: true });
                    arguments[0].dispatchEvent(event);
                    """,
                    caption_editor,
                )
                logger.info(f"Caption set: {full_caption[:50]}...")
            except Exception as e:
                logger.warning(f"Could not set caption automatically: {e}")

            # Wait for video processing
            logger.info("Waiting for video to finish processing...")
            time.sleep(15)

            # Click the Post button
            try:
                post_button = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'btn-post')]|//button[text()='Post']|//div[text()='Post']")
                    )
                )
                post_button.click()
                logger.info("Post button clicked")
            except Exception:
                # Try alternative selectors
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if btn.text.strip().lower() in ("post", "đăng"):
                        btn.click()
                        logger.info("Post button clicked (fallback)")
                        break

            # Wait for confirmation
            time.sleep(10)
            logger.info("Video posted successfully!")
            return True

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
