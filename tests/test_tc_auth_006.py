"""
TC-AUTH-006 | Authentication / Login
Title: Login dengan Field Password Kosong (Login with Empty Password Field)
Pre-conditions: User is on the Login page.
Priority: P2 - High

Steps:
    1. Enter 'Admin' in Username
    2. Leave Password empty
    3. Click Login button

Expected Result:
    'Required' validation appears under the Password field; the form is not submitted.
"""
import pytest
from utils.config import Config


@pytest.mark.p2
class TestTC_AUTH_006:
    def test_login_with_empty_password(self, login_page):
        login_page.enter_username(Config.VALID_USERNAME)
        login_page.clear_password()
        login_page.click_login()

        assert login_page.get_required_messages_count() >= 1, (
            "'Required' validation message did not appear for empty Password"
        )
        assert login_page.is_on_login_page(), (
            "Form should not be submitted when Password is empty"
        )
