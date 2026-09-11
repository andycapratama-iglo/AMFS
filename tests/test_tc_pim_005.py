"""
TC-PIM-005 | PIM / Employee List / Search
Title: Pencarian Employee dengan Nama Partial/Sebagian
       (Search Employee with a Partial Name)
Pre-conditions: User is on Employee List.
Priority: P2 - High

Steps:
    1. Enter a partial name, e.g. 'Mich', into Employee Name
    2. Click the Search button

Expected Result:
    Table shows all employees whose name contains the substring 'Mich'
    (partial match).
"""
import pytest

PARTIAL_NAME = "Tys"


@pytest.mark.p2
class TestTC_PIM_005:
    def test_search_with_partial_name_returns_substring_matches(self, pim_page):
        pim_page.search_by_employee_name(PARTIAL_NAME)

        # Poll the results count itself to settle first (same race as
        # TC-PIM-004: the counter and the row cards update on separate ticks).
        _, row_count = pim_page.wait_for_results_to_settle()
        if row_count == 0:
            assert pim_page.is_no_records_found_visible(), (
                "No rows returned but 'No Records Found' is not shown either"
            )
            return

        for i in range(row_count):
            # Row wrapper elements are commonly reused in place across
            # searches, so cell text can still be mid-update even after the
            # row count has settled - wait for this specific row's text to
            # actually reflect the expected match before asserting on it.
            row_text = pim_page.wait_for_row_text_to_contain(i, PARTIAL_NAME)
            assert PARTIAL_NAME.lower() in row_text.lower(), (
                f"Row {i} does not contain the partial match '{PARTIAL_NAME}': "
                f"'{row_text}'"
            )
