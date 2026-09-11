"""
TC-PIM-005 | PIM / Employee List / Search
Title: Pencarian Employee dengan Nama Tidak Terdaftar
       (Search Employee with an Unregistered Name)
Pre-conditions: User is on Employee List.
Priority: P2 - High

Steps:
    1. Enter an unregistered name, e.g. 'Zzxxqq123'
    2. Click the Search button

Expected Result:
    Table shows 'No Records Found'; '(0) Records Found' is displayed;
    no error/crash occurs.
"""
import pytest

UNREGISTERED_NAME = "Zzxxqq1235452"


@pytest.mark.p2
class TestTC_PIM_005:
    def test_search_unregistered_name_shows_no_records(self, pim_page):
        pim_page.search_by_employee_name(UNREGISTERED_NAME)

        assert pim_page.is_no_records_found_visible(), (
            "'No Records Found' message was not shown for an unregistered name"
        )
        assert pim_page.get_records_found_count() == 0, (
            "'(0) Records Found' was not reflected in the records count"
        )

    def test_no_error_or_crash_on_empty_result(self, pim_page, page):
        console_errors = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        pim_page.search_by_employee_name(UNREGISTERED_NAME)
        page.wait_for_timeout(300)

        assert pim_page.employee_list_tab.is_visible(), (
            "Page appears to have crashed / navigated away unexpectedly"
        )
        assert not console_errors, f"Unexpected console errors: {console_errors}"
