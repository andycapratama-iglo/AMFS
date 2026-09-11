"""
TC-PIM-008 | PIM / Employee List / Delete
Title: Delete Employee (Happy Path)
Pre-conditions: User is on Employee List; the target employee 'Carter' exists
                 (name noted before deleting).
Priority: P1 - Critical

Steps:
    1. Search for the employee 'Carter' to identify the row to delete
    2. Click the delete icon on that row
    3. Confirm the 'Yes, Delete' dialog

Expected Result:
    Success notification appears; the employee no longer appears in the
    table; Records Found decreases by 1.
"""
import pytest

# Fixed target employee so this test always deletes the same, known record -
# using row 0 of the unfiltered list would delete whatever employee happens
# to sort first, which varies with seed data and test order.
EMPLOYEE_NAME = "Bahlil"


@pytest.mark.p1
@pytest.mark.smoke
class TestTC_PIM_008:
    def test_delete_employee_happy_path(self, pim_page):
        pim_page.search_by_employee_name(EMPLOYEE_NAME, require_hint=True)
        _, row_count_before = pim_page.wait_for_results_to_settle()

        if row_count_before == 0:
            pytest.skip(
                f"'{EMPLOYEE_NAME}' not found - likely already deleted by an "
                "earlier test in this run, or not present in seed data."
            )

        records_found_before = pim_page.get_records_found_count()
        deleted_employee_name = pim_page.get_employee_name_in_row(0)

        pim_page.click_delete_in_row(0)
        pim_page.confirm_delete()

        toast_text = pim_page.get_toast_text()
        assert "success" in toast_text.lower(), (
            f"Expected a success notification, got: '{toast_text}'"
        )

        records_found_after = pim_page.get_records_found_count()
        assert records_found_after == records_found_before - 1, (
            f"Records Found did not decrease by 1: {records_found_before} -> "
            f"{records_found_after}"
        )

        remaining_names = " ".join(pim_page.get_all_employee_names())
        deleted_name_fragment = deleted_employee_name.strip().split("\n")[0]
        assert deleted_name_fragment not in remaining_names, (
            f"Deleted employee '{deleted_name_fragment}' still appears in the table"
        )
