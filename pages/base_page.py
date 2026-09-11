"""
BasePage: parent class for all Page Object Model classes.
Wraps common Playwright interactions so page classes stay thin and readable.
"""
from playwright.sync_api import Page, expect
from utils.config import Config


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.page.set_default_timeout(Config.DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)

    def goto(self, url: str):
        """
        Navigates with a longer timeout than regular UI actions, plus a
        retry, since this suite logs in fresh for nearly every test against
        a shared public demo instance - occasional slow responses there are
        a server-load issue, not a locator/selector bug, so retrying once
        is the right response rather than failing outright.
        """
        last_error = None
        for attempt in range(Config.NAVIGATION_RETRIES + 1):
            try:
                self.page.goto(
                    url, wait_until="domcontentloaded", timeout=Config.NAVIGATION_TIMEOUT
                )
                return
            except Exception as e:
                last_error = e
        raise last_error

    def click(self, locator):
        locator.click()

    def fill(self, locator, text: str):
        locator.fill(text)

    def type_text(self, locator, text: str, delay: int = 0):
        """Types text character by character (useful for keyboard-nav tests)."""
        locator.click()
        locator.type(text, delay=delay)

    def press_key(self, locator, key: str):
        locator.press(key)

    def is_visible(self, locator) -> bool:
        return locator.is_visible()

    def get_text(self, locator) -> str:
        return locator.inner_text().strip()

    def current_url(self) -> str:
        return self.page.url

    def wait_for_url_contains(self, fragment: str, timeout: int = None):
        self.page.wait_for_url(f"**/*{fragment}*", timeout=timeout or Config.DEFAULT_TIMEOUT)

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)
