"""
TC-PIM-008 | PIM / Employee List / Delete
Title: Validasi Employee yang Dihapus Tidak Muncul di Pencarian
       (Validate a Deleted Employee Does Not Appear in Search)
Pre-conditions (per manual case): employee already deleted (state from TC-PIM-010).
Priority: P1 - Critical
Edge case noted: Full page refresh (F5) to confirm the data is permanently
removed on the backend.

Steps:
    1. Search for the target employee (plain text) to identify the row to delete
    2. Delete it, then enter that employee's name into Employee Name again
    3. Click the Search button

Expected Result:
    Table shows 'No Records Found'; the employee does not appear in any
    search, including after a page refresh.
"""
import pytest

# Same fixed target as TC-PIM-010, so both specs are unambiguously operating
# on the same known employee rather than an arbitrary "row 0".
EMPLOYEE_NAME = "Carter"


@pytest.mark.p1
class TestTC_PIM_008:
    def test_deleted_employee_does_not_appear_in_search(self, pim_page):
        pim_page.search_by_employee_name(EMPLOYEE_NAME)
        _, row_count_before = pim_page.wait_for_results_to_settle()

        if row_count_before == 0:
            # Employee already deleted/not found (e.g. by an earlier test in
            # this run) - that already satisfies the expected result ("does
            # not appear in search"), so this is a pass, not a skip.
            assert pim_page.is_no_records_found_visible(), (
                f"'{EMPLOYEE_NAME}' was not found, but 'No Records Found' is "
                "not shown either - unexpected empty-state rendering"
            )
            return

        deleted_name = pim_page.get_employee_name_in_row(0).strip().split("\n")[0]

        pim_page.click_delete_in_row(0)
        pim_page.confirm_delete()

        pim_page.search_by_employee_name(deleted_name)
        assert pim_page.is_no_records_found_visible(), (
            f"Deleted employee '{deleted_name}' still appears in search results"
        )

    def test_deleted_employee_stays_gone_after_full_refresh(self, pim_page, page):
        """Edge case: F5 full page refresh - deletion must be persisted server-side."""
        pim_page.search_by_employee_name(EMPLOYEE_NAME)
        _, row_count_before = pim_page.wait_for_results_to_settle()

        if row_count_before == 0:
            # Already deleted/not found before we even got to delete it -
            # still exercise the actual point of this edge case (does the
            # "gone" state survive a refresh) rather than passing trivially.
            page.reload(wait_until="domcontentloaded")
            pim_page.employee_list_tab.wait_for(state="visible")
            pim_page.search_by_employee_name(EMPLOYEE_NAME)
            assert pim_page.is_no_records_found_visible(), (
                f"'{EMPLOYEE_NAME}' was not found before refresh, but "
                "reappeared after a full page refresh"
            )
            return

        deleted_name = pim_page.get_employee_name_in_row(0).strip().split("\n")[0]

        pim_page.click_delete_in_row(0)
        pim_page.confirm_delete()

        page.reload(wait_until="domcontentloaded")
        pim_page.employee_list_tab.wait_for(state="visible")
        pim_page.search_by_employee_name(deleted_name)

        assert pim_page.is_no_records_found_visible(), (
            f"Deleted employee '{deleted_name}' reappeared after a full page refresh - "
            "deletion may not be persisted on the backend"
        )
