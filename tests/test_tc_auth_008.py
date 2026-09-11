"""
TC-AUTH-008 | Authentication / Login
Title: Login dengan Input Hanya Spasi (Login with Whitespace-Only Input)
Pre-conditions: User is on the Login page.
Priority: P3 - Medium
Edge case noted: Check trim-behavior consistency between frontend and backend.

Steps:
    1. Enter only spaces in Username
    2. Enter only spaces in Password
    3. Click Login button

Expected Result:
    System rejects the login (either 'Required' validation or 'Invalid credentials');
    login must NOT succeed.
"""
import pytest


@pytest.mark.p3
class TestTC_AUTH_008:
    def test_login_with_whitespace_only_input(self, login_page):
        login_page.login("   ", "   ")

        # Whichever guard fires, the user must not be authenticated.
        required_count = login_page.get_required_messages_count()
        has_invalid_credentials = False
        if required_count == 0:
            try:
                error_text = login_page.get_invalid_credentials_text(timeout=5000)
                has_invalid_credentials = "Invalid credentials" in error_text
            except Exception:
                has_invalid_credentials = False

        assert required_count >= 1 or has_invalid_credentials, (
            "Whitespace-only credentials were not rejected by either "
            "client-side validation or server-side authentication"
        )
        assert not login_page.is_on_dashboard(), (
            "Login must not succeed with whitespace-only credentials"
        )
