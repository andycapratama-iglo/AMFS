"""
TC-AUTH-004 | Authentication / Login
Title: Login Gagal dengan Username dan Password Salah
       (Login Fails with Both Wrong Username and Wrong Password)
Pre-conditions: User is on the Login page.
Priority: P2 - High

Steps:
    1. Enter a wrong username
    2. Enter a wrong password
    3. Click Login button

Expected Result:
    'Invalid credentials' error message is shown.
"""
import pytest


@pytest.mark.p2
class TestTC_AUTH_004:
    def test_login_fails_with_wrong_username_and_password(self, login_page):
        login_page.login("wronguser", "WrongPass123")

        error_text = login_page.get_invalid_credentials_text()
        assert "Invalid credentials" in error_text, (
            f"Expected 'Invalid credentials' message, got: '{error_text}'"
        )
        assert login_page.is_on_login_page(), "User should remain on the Login page"
