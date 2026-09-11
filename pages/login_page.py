"""
LoginPage: Page Object Model for the OrangeHRM Login screen.
Covers all locators/actions needed by TC-AUTH-001 .. TC-AUTH-015.
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.config import Config


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # --- Locators -------------------------------------------------
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.login_button = page.locator("button[type='submit']")
        self.login_logo = page.locator(".orangehrm-login-branding img")
        self.login_form = page.locator(".orangehrm-login-form")

        # Server-side error banner ("Invalid credentials")
        self.invalid_credentials_alert = page.locator(
            ".oxd-alert-content-text"
        )

        # Client-side "Required" validation messages.
        # Actual OrangeHRM DOM renders these as:
        # <span class="oxd-text oxd-text--span oxd-input-field-error-message oxd-input-group__message">Required</span>
        self.required_messages = page.locator(
            "span.oxd-input-field-error-message"
        )

        # Forgot password
        self.forgot_password_link = page.locator(
            ".orangehrm-login-forgot-header, a:has-text('Forgot your password?')"
        )
        self.reset_password_title = page.locator(".orangehrm-forgot-password-title")

        # Post-login dashboard marker
        self.dashboard_header = page.locator(
            ".oxd-topbar-header-breadcrumb h6"
        )

    # --- Actions --------------------------------------------------------
    def open(self):
        self.goto(Config.login_url())

    def enter_username(self, username: str):
        self.username_input.fill(username)

    def enter_password(self, password: str):
        self.password_input.fill(password)

    def clear_username(self):
        self.username_input.fill("")

    def clear_password(self):
        self.password_input.fill("")

    def click_login(self):
        self.login_button.click()

    def submit_via_enter(self):
        self.password_input.press("Enter")

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def login_via_keyboard(self, username: str, password: str):
        """Click username, type, Tab to password, type, then press Enter."""
        self.username_input.click()
        self.username_input.type(username)
        self.page.keyboard.press("Tab")
        self.password_input.type(password)
        self.password_input.press("Enter")

    def click_forgot_password(self):
        self.forgot_password_link.first.click()

    # --- State / assertcatcher helpers ----------------------------------
    def get_invalid_credentials_text(self, timeout: int = None) -> str:
        self.invalid_credentials_alert.first.wait_for(
            state="visible", timeout=timeout or Config.DEFAULT_TIMEOUT
        )
        return self.invalid_credentials_alert.first.inner_text().strip()

    def get_required_messages_count(self, timeout: int = None) -> int:
        """
        Waits for at least one 'Required' validation message to render before
        counting. `locator.count()` does NOT auto-wait in Playwright, so calling
        it immediately after a click can race the Vue re-render and read 0.
        """
        timeout = timeout or Config.DEFAULT_TIMEOUT
        try:
            self.required_messages.first.wait_for(state="visible", timeout=timeout)
        except Exception:
            # No message appeared within the timeout - genuinely 0.
            return 0
        return self.required_messages.count()

    def is_on_login_page(self) -> bool:
        return "auth/login" in self.current_url()

    def is_on_dashboard(self) -> bool:
        try:
            self.dashboard_header.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
            return "Dashboard" in self.dashboard_header.inner_text()
        except Exception:
            return False
