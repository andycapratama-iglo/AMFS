"""
TC-PIM-010 | PIM / Employee List / Delete
Title: Cancel Konfirmasi Delete Employee (Cancel Delete Confirmation)
Pre-conditions: User is on Employee List with at least 1 employee.
Priority: P2 - High

Steps:
    1. Click the delete icon on any row
    2. Click 'Cancel' or close (X) on the confirmation dialog

Expected Result:
    Dialog closes with no change; the employee still appears in the table;
    Records Found is unchanged.
"""
import pytest


@pytest.mark.p2
class TestTC_PIM_010:
    def test_cancel_button_aborts_delete(self, pim_page):
        records_found_before = pim_page.get_records_found_count()
        row_count_before = pim_page.get_visible_row_count()
        employee_name = pim_page.get_employee_name_in_row(0)

        pim_page.click_delete_in_row(0)
        pim_page.cancel_delete()

        assert not pim_page.confirm_dialog.is_visible(), (
            "Confirmation dialog is still visible after clicking Cancel"
        )
        assert pim_page.get_records_found_count() == records_found_before, (
            "Records Found changed after cancelling a delete"
        )
        assert pim_page.get_visible_row_count() == row_count_before, (
            "Row count changed after cancelling a delete"
        )
        assert employee_name == pim_page.get_employee_name_in_row(0), (
            "Employee row content changed after cancelling a delete"
        )

    def test_close_x_button_aborts_delete(self, pim_page):
        records_found_before = pim_page.get_records_found_count()

        pim_page.click_delete_in_row(0)
        pim_page.close_delete_dialog_via_x()

        assert not pim_page.confirm_dialog.is_visible(), (
            "Confirmation dialog is still visible after clicking the close (X) button"
        )
        assert pim_page.get_records_found_count() == records_found_before, (
            "Records Found changed after closing the delete dialog via X"
        )
