"""
TC-AUTH-007 | Authentication / Login
Title: Login dengan Kedua Field Kosong (Login with Both Fields Empty)
Pre-conditions: User is on the Login page.
Priority: P3 - Medium

Steps:
    1. Leave Username and Password empty
    2. Click Login button

Expected Result:
    'Required' validation appears on both fields simultaneously.
"""
import pytest


@pytest.mark.p3
class TestTC_AUTH_007:
    def test_login_with_both_fields_empty(self, login_page):
        login_page.clear_username()
        login_page.clear_password()
        login_page.click_login()

        required_count = login_page.get_required_messages_count()
        assert required_count >= 2, (
            f"Expected 'Required' validation on both fields, found {required_count} message(s)"
        )
        assert login_page.is_on_login_page(), (
            "Form should not be submitted when both fields are empty"
        )
