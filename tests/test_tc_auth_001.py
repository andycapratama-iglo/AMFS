"""
TC-AUTH-001 | Authentication / Login
Title: Login Sukses dengan Kredensial Valid (Successful Login with Valid Credentials)
Pre-conditions: Browser open on OrangeHRM Login page; admin/Admin123 account active.
Priority: P1 - Critical

Steps:
    1. Open the Login page
    2. Enter 'Admin' in Username
    3. Enter 'admin123' in Password
    4. Click Login button

Expected Result:
    User logs in successfully and is redirected to the Dashboard; no error message shown.
"""
import pytest
from utils.config import Config


@pytest.mark.p1
@pytest.mark.smoke
class TestTC_AUTH_001:
    def test_login_success_with_valid_credentials(self, login_page):
        # Step 1: already on login page via `login_page` fixture
        # Step 2-4: enter valid credentials and submit
        login_page.login(Config.VALID_USERNAME, Config.VALID_PASSWORD)

        # Expected: redirected to Dashboard
        assert login_page.is_on_dashboard(), (
            "User was not redirected to the Dashboard after a valid login"
        )

        # Expected: no error message present
        assert login_page.invalid_credentials_alert.count() == 0, (
            "An error message was unexpectedly shown after a valid login"
        )
