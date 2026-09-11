"""
Shared pytest fixtures for the AMFS Playwright suite.
- Spins up a fresh browser context/page per test (isolation).
- Injects the LoginPage POM.
- Captures a screenshot automatically on test failure.
"""
import os
import sys
import pytest
from playwright.sync_api import sync_playwright

# Make `pages` / `utils` importable when running pytest from the repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.login_page import LoginPage
from pages.pim_page import PIMPage
from utils.config import Config

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(
        headless=Config.HEADLESS, slow_mo=Config.SLOW_MO
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    yield context
    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def login_page(page):
    lp = LoginPage(page)
    lp.open()
    return lp


@pytest.fixture
def pim_page(page):
    """
    Fulfils the shared pre-condition for all PIM test cases ('User sudah
    login' / TC-AUTH-001): logs in, then opens PIM > Employee List and
    hands back a ready-to-use PIMPage POM.
    """
    lp = LoginPage(page)
    lp.open()
    lp.login(Config.VALID_USERNAME, Config.VALID_PASSWORD)
    assert lp.is_on_dashboard(), "Setup failed: could not log in before PIM test"

    pim = PIMPage(page)
    pim.open_pim_module()
    return pim


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the report dir whenever a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page_fixture = item.funcargs.get("page")
        if page_fixture is not None:
            safe_name = item.name.replace("/", "_")
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{safe_name}.png")
            try:
                page_fixture.screenshot(path=screenshot_path, full_page=True)
            except Exception:
                pass
