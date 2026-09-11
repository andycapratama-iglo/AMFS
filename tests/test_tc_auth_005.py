"""
TC-AUTH-005 | Authentication / Login
Title: Login dengan Field Username Kosong (Login with Empty Username Field)
Pre-conditions: User is on the Login page.
Priority: P2 - High
Edge case noted: Client-side validation should appear instantly, without a server request.

Steps:
    1. Leave Username empty
    2. Enter 'admin123' in Password
    3. Click Login button

Expected Result:
    'Required' validation appears under the Username field; the form is not submitted.
"""
import pytest
from utils.config import Config


@pytest.mark.p2
class TestTC_AUTH_005:
    def test_login_with_empty_username(self, login_page):
        login_page.clear_username()
        login_page.enter_password(Config.VALID_PASSWORD)
        login_page.click_login()

        assert login_page.get_required_messages_count() >= 1, (
            "'Required' validation message did not appear for empty Username"
        )
        assert login_page.is_on_login_page(), (
            "Form should not be submitted when Username is empty"
        )

    def test_validation_is_instant_client_side(self, login_page, page):
        """Edge case: validation should not depend on a network round-trip."""
        requests_before = []
        page.on("request", lambda req: requests_before.append(req.url))

        login_page.clear_username()
        login_page.enter_password(Config.VALID_PASSWORD)

        request_count_before_click = len(requests_before)
        login_page.click_login()
        page.wait_for_timeout(300)  # allow any client-side render to settle

        assert login_page.get_required_messages_count() >= 1
        # No new POST/login request should have fired for a client-side-only validation error
        login_requests = [
            url for url in requests_before[request_count_before_click:]
            if "login" in url.lower() and "validate" not in url.lower()
        ]
        assert len(login_requests) == 0, (
            "A login request was sent to the server despite client-side validation failing"
        )
