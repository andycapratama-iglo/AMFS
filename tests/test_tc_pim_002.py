"""
TC-PIM-002 | PIM / Employee List
Title: Validasi Field Filter Employee List dalam Keadaan Kosong/Default
       (Validate Employee List Filter Fields Are Empty/Default)
Pre-conditions: User is on PIM > Employee List (fresh state).
Priority: P2 - High
Edge case noted: Refresh the page and confirm filters stay reset (no stale
cache/session leftovers from a previous session).

Steps:
    1. Check Employee Name is empty with placeholder 'Type for hints...'
    2. Check Employee Id is empty with no placeholder
    3. Check Employment Status = '-- Select --'
    4. Check Include = 'Current Employees Only'
    5. Check Supervisor Name is empty with placeholder
    6. Check Job Title = '-- Select --'
    7. Check Sub Unit = '-- Select --'

Expected Result:
    All filter fields are empty/default as on first load; no stale values
    remain from a previous session.
"""
import pytest


@pytest.mark.p2
class TestTC_PIM_002:
    def test_all_filter_fields_are_empty_or_default(self, pim_page):
        assert pim_page.employee_name_input.input_value() == "", (
            "Employee Name should be empty by default"
        )
        assert pim_page.employee_name_input.get_attribute("placeholder") == (
            "Type for hints..."
        ), "Employee Name placeholder does not match expected text"

        assert pim_page.employee_id_input.input_value() == "", (
            "Employee Id should be empty by default"
        )

        assert pim_page.employment_status_select.inner_text().strip() == "-- Select --", (
            "Employment Status should default to '-- Select --'"
        )
        assert pim_page.include_select.inner_text().strip() == "Current Employees Only", (
            "Include should default to 'Current Employees Only'"
        )

        assert pim_page.supervisor_name_input.input_value() == "", (
            "Supervisor Name should be empty by default"
        )
        assert pim_page.supervisor_name_input.get_attribute("placeholder") == (
            "Type for hints..."
        ), "Supervisor Name placeholder does not match expected text"

        assert pim_page.job_title_select.inner_text().strip() == "-- Select --", (
            "Job Title should default to '-- Select --'"
        )
        assert pim_page.sub_unit_select.inner_text().strip() == "-- Select --", (
            "Sub Unit should default to '-- Select --'"
        )

    def test_filters_remain_reset_after_page_refresh(self, pim_page, page):
        """Edge case: full page refresh should not leave stale filter values."""
        pim_page.search_by_employee_name("Michael")
        page.reload(wait_until="domcontentloaded")
        pim_page.employee_list_tab.wait_for(state="visible")

        assert pim_page.employee_name_input.input_value() == "", (
            "Employee Name filter retained a stale value after page refresh"
        )
