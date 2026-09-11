"""
Environment / configuration management for the AMFS Playwright suite.
Values can be overridden via environment variables or a local .env file.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed - fall back to plain os.environ
    pass


class Config:
    BASE_URL = os.getenv("BASE_URL", "https://opensource-demo.orangehrmlive.com")
    LOGIN_PATH = os.getenv("LOGIN_PATH", "/web/index.php/auth/login")

    VALID_USERNAME = os.getenv("VALID_USERNAME", "Admin")
    VALID_PASSWORD = os.getenv("VALID_PASSWORD", "admin123")

    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10000"))  # ms, for UI actions

    # Navigation (page.goto) gets a longer budget than regular UI actions.
    # This suite logs in fresh for nearly every test against a shared public
    # demo instance, which can respond slower than 10s under repeated load -
    # that's a server-responsiveness issue, not a broken locator, so it gets
    # more time plus a retry rather than a bigger blanket action timeout.
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))  # ms
    NAVIGATION_RETRIES = int(os.getenv("NAVIGATION_RETRIES", "1"))

    @classmethod
    def login_url(cls) -> str:
        return f"{cls.BASE_URL}{cls.LOGIN_PATH}"
