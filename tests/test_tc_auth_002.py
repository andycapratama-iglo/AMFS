"""
TC-AUTH-002 | Authentication / Login
Title: Login Gagal dengan Password Salah (Login Fails with Wrong Password)
Pre-conditions: User is on the Login page.
Priority: P1 - Critical
Edge case noted: Password field must not retain its value after the error is shown.

Steps:
    1. Enter 'Admin' in Username
    2. Enter a wrong password (e.g. WrongPass123)
    3. Click Login button

Expected Result:
    'Invalid credentials' error is shown; user remains on the Login page.
"""
import pytest
from utils.config import Config


@pytest.mark.p1
class TestTC_AUTH_002:
    def test_login_fails_with_wrong_password(self, login_page):
        login_page.login(Config.VALID_USERNAME, "WrongPass123")

        error_text = login_page.get_invalid_credentials_text()
        assert "Invalid credentials" in error_text, (
            f"Expected 'Invalid credentials' message, got: '{error_text}'"
        )
        assert login_page.is_on_login_page(), "User should remain on the Login page"

    def test_password_field_cleared_after_error(self, login_page):
        """Edge case: password value should not persist in the field after a failed attempt."""
        login_page.login(Config.VALID_USERNAME, "WrongPass123")
        login_page.get_invalid_credentials_text()  # wait for error to render

        password_value = login_page.password_input.input_value()
        assert password_value == "", (
            "Password field should be cleared after a failed login attempt"
        )
