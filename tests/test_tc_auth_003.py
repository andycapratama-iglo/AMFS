"""
TC-AUTH-003 | Authentication / Login
Title: Login Gagal dengan Username Salah (Login Fails with Wrong Username)
Pre-conditions: User is on the Login page.
Priority: P1 - Critical
Edge case noted: Error message must NOT reveal whether username or password was wrong
(protects against username enumeration).

Steps:
    1. Enter an unregistered username (e.g. wronguser)
    2. Enter 'admin123' in Password
    3. Click Login button

Expected Result:
    'Invalid credentials' error is shown; user remains on the Login page.
"""
import pytest
from utils.config import Config


@pytest.mark.p1
class TestTC_AUTH_003:
    def test_login_fails_with_wrong_username(self, login_page):
        login_page.login("wronguser", Config.VALID_PASSWORD)

        error_text = login_page.get_invalid_credentials_text()
        assert "Invalid credentials" in error_text, (
            f"Expected 'Invalid credentials' message, got: '{error_text}'"
        )
        assert login_page.is_on_login_page(), "User should remain on the Login page"

    def test_error_message_does_not_leak_which_field_was_wrong(self, login_page):
        """Edge case: generic message only, no 'username not found' style disclosure."""
        login_page.login("wronguser", Config.VALID_PASSWORD)
        error_text = login_page.get_invalid_credentials_text().lower()

        leaking_phrases = ["user not found", "username does not exist", "no such user"]
        for phrase in leaking_phrases:
            assert phrase not in error_text, (
                f"Error message leaks account-enumeration info: '{phrase}' found in '{error_text}'"
            )
