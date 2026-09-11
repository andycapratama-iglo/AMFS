"""
TC-PIM-006 | PIM / Employee List / Search
Title: Pencarian dengan Field Employee Name Kosong (Search Semua Data)
       (Search with Empty Employee Name Field - Search All Data)
Pre-conditions: User is on Employee List; filters are default/empty.
Priority: P3 - Medium

Steps:
    1. Ensure Employee Name is empty
    2. Click the Search button without filling any filter

Expected Result:
    Table shows all active employee data (same as the initial state);
    no validation error occurs.
"""
import pytest


@pytest.mark.p3
class TestTC_PIM_006:
    def test_search_with_all_filters_empty_returns_all_data(self, pim_page):
        initial_records_found = pim_page.get_records_found_count()

        assert pim_page.employee_name_input.input_value() == "", (
            "Precondition failed: Employee Name is not empty"
        )
        pim_page.click_search()

        records_found_after_search = pim_page.get_records_found_count()
        assert records_found_after_search == initial_records_found, (
            "Records Found changed after searching with empty filters: "
            f"{initial_records_found} -> {records_found_after_search}"
        )

    def test_no_validation_error_shown(self, pim_page):
        pim_page.click_search()
        required_text_visible = pim_page.page.locator(
            "span.oxd-input-field-error-message"
        ).count()
        assert required_text_visible == 0, (
            "Unexpected validation error shown for an empty-filter search"
        )
