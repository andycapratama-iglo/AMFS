"""
TC-PIM-003 | PIM / Employee List
Title: Validasi Tampilan Tabel Data Employee Default
       (Validate Default Employee Data Table Display)
Pre-conditions: User is on PIM > Employee List.
Priority: P3 - Medium

Steps:
    1. Observe the data table section
    2. Check the 'Records Found' count and table columns

Expected Result:
    Table displays all active employees matching the total record count;
    every row has edit/delete action icons; sortable columns work.
"""
import pytest


@pytest.mark.p3
class TestTC_PIM_003:
    def test_records_found_count_matches_visible_rows(self, pim_page):
        records_found = pim_page.get_records_found_count()
        visible_rows = pim_page.get_visible_row_count()

        # OrangeHRM paginates at 50 rows/page by default, so only assert
        # equality when the total is within a single page.
        if records_found <= 50:
            assert visible_rows == records_found, (
                f"Records Found ({records_found}) does not match visible "
                f"table rows ({visible_rows})"
            )
        else:
            assert visible_rows == 50, (
                f"Expected a full page (50) of rows, got {visible_rows}"
            )
