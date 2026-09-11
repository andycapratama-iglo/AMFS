"""
TC-PIM-003 | PIM / Employee List / Search
Title: Pencarian Employee Berdasarkan Nama (Happy Path)
       (Search Employee by Name - Happy Path)
Pre-conditions: User is on Employee List; at least 1 employee with a known name exists.
Priority: P1 - Critical
Edge case noted: Verify the search is case-insensitive.

Steps:
    1. Enter a valid employee name, e.g. 'Michael', into Employee Name
    2. Select a hint or click Search
    3. Observe the results table

Expected Result:
    Table only shows employees whose name matches/contains 'Michael';
    'Records Found' updates accordingly.
"""
import pytest

SEARCH_NAME = "Prabs"


@pytest.mark.p1
@pytest.mark.smoke
class TestTC_PIM_003:
    def test_search_by_valid_employee_name(self, pim_page):
        pim_page.search_by_employee_name(SEARCH_NAME, require_hint=True)

        # Poll until the 'Records Found' counter and the actual table rows
        # agree - they update via two separate reactive properties and can
        # briefly disagree right after a search, especially one triggered by
        # selecting an autocomplete hint on top of the Search click itself.
        records_found, row_count = pim_page.wait_for_results_to_settle()

        if row_count == 0:
            pytest.skip(
                f"No employee named '{SEARCH_NAME}' exists in this environment's "
                "seed data - happy-path assumption not met."
            )

        assert records_found == row_count, (
            f"Records Found count ({records_found}) does not match the number "
            f"of visible rows ({row_count}) after waiting for results to settle"
        )
        for i in range(row_count):
            row_text = pim_page.wait_for_row_text_to_contain(i, SEARCH_NAME)
            assert SEARCH_NAME.lower() in row_text.lower(), (
                f"Row {i} does not contain the searched name '{SEARCH_NAME}': "
                f"'{row_text}'"
            )

    def test_search_is_case_insensitive(self, pim_page):
        """Edge case: 'michael' (lowercase) should return the same result set."""
        pim_page.search_by_employee_name(SEARCH_NAME, require_hint=True)
        upper_count, _ = pim_page.wait_for_results_to_settle()

        pim_page.click_reset()

        # Explicit guard before re-using the form: confirm the search button
        # (and therefore the whole filter section) has finished re-rendering
        # after Reset before filling/searching again.
        pim_page.search_button.wait_for(state="visible", timeout=10000)
        assert pim_page.search_button.is_visible(), (
            "Search button is not visible/ready after Reset - filter form "
            "did not finish re-rendering before the second search"
        )

        # `require_hint=True`: this component is an autocomplete, not a plain
        # text field. If the lowercase text doesn't surface a matching
        # suggestion, selecting it is what actually filters correctly -
        # without it, the app can silently ignore the search text and return
        # every employee instead of raising a clear, actionable failure.
        pim_page.search_by_employee_name(SEARCH_NAME.lower(), require_hint=True)
        lower_count, _ = pim_page.wait_for_results_to_settle()

        assert upper_count == lower_count, (
            f"Case-insensitive search mismatch: '{SEARCH_NAME}' -> {upper_count} "
            f"records, '{SEARCH_NAME.lower()}' -> {lower_count} records"
        )
