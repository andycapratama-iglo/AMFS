"""
PIMPage: Page Object Model for the OrangeHRM PIM > Employee List screen.
Covers all locators/actions needed by TC-PIM-001 .. TC-PIM-014.

NOTE: Selectors target the OrangeHRM demo app's typical Vue/oxd markup.
Some elements (dropdowns, dialogs) render inside portal/overlay containers -
adjust selectors here if the target app's exact DOM differs.
"""
import time
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.config import Config


class PIMPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # --- Navigation -------------------------------------------------
        # The sidebar link's visible label renders as:
        # <span class="oxd-text oxd-text--span oxd-main-menu-item--name">PIM</span>
        # nested inside the clickable <a class="oxd-main-menu-item">. Matching
        # on the exact label span (not the ancestor wrapper) is more resilient
        # to markup/version changes, and Playwright's click on the span still
        # triggers the parent link's navigation.
        self.pim_menu_link = page.locator(
            "span.oxd-main-menu-item--name", has_text="PIM"
        ).first
        self.employee_list_tab = page.locator(
            ".oxd-topbar-body-nav-tab", has_text="Employee List"
        ).first
        self.add_employee_tab = page.locator(
            ".oxd-topbar-body-nav-tab", has_text="Add Employee"
        ).first
        self.page_heading = page.locator(".oxd-topbar-header-breadcrumb h6").first

        # --- Filter section ----------------------------------------------
        # There are two "Type for hints..." fields: Employee Name (0) and
        # Supervisor Name (1).
        self._hint_inputs = page.locator("input[placeholder='Type for hints...']")
        self.employee_name_input = self._hint_inputs.nth(0)
        self.supervisor_name_input = self._hint_inputs.nth(1)

        self.employee_id_input = page.locator(
            ".oxd-input-group:has-text('Employee Id') input"
        ).first
        self.employment_status_select = page.locator(
            ".oxd-input-group:has-text('Employment Status') .oxd-select-text"
        ).first
        self.include_select = page.locator(
            ".oxd-input-group:has-text('Include') .oxd-select-text"
        ).first
        self.job_title_select = page.locator(
            ".oxd-input-group:has-text('Job Title') .oxd-select-text"
        ).first
        self.sub_unit_select = page.locator(
            ".oxd-input-group:has-text('Sub Unit') .oxd-select-text"
        ).first

        self.search_button = page.locator("button[type='submit']", has_text="Search").first
        self.reset_button = page.locator("button[type='reset']", has_text=" Reset ").first

        # --- Autocomplete hint dropdown (for name fields) -----------------
        self.autocomplete_options = page.locator(".oxd-autocomplete-dropdown span")

        # --- Table / results ----------------------------------------------
        self.records_found_text = page.locator(".orangehrm-horizontal-padding span").filter(
            has_text="Record"
        ).first
        # Renders as:
        # <div class="orangehrm-horizontal-padding orangehrm-vertical-padding">
        #   <span class="oxd-text oxd-text--span">No Records Found</span>
        # </div>
        # get_by_text() alone hit a strict-mode violation (matches more than
        # one element in the DOM), so scope to this specific wrapper div
        # instead and take .first as a further guard against duplicates.
        self.no_records_found = page.locator(
            "div.orangehrm-horizontal-padding.orangehrm-vertical-padding",
            has_text="No Records Found",
        ).first
        self.table_rows = page.locator(".oxd-table-card")
        self.table_header_cells = page.locator(".oxd-table-header .oxd-table-cell")
        self.select_all_checkbox = page.locator(
            ".oxd-table-header input[type='checkbox']"
        ).first

        # --- Row-level action icons (relative to a given row locator) -----
        # Usage: self.edit_icon_in_row(row), self.delete_icon_in_row(row)

        # --- Delete confirmation dialog ------------------------------------
        # `.oxd-dialog-container` here is an assumed wrapper class that was
        # never confirmed against the real DOM (unlike the delete icon,
        # which was). Rather than keep guessing at the container, match the
        # dialog's buttons directly by their visible text - that's the
        # concrete thing we actually need to interact with, and it doesn't
        # depend on unconfirmed wrapper markup.
        self.confirm_delete_button = page.locator("button", has_text="Yes, Delete").first
        self.cancel_delete_button = page.locator("button", has_text="Cancel").first
        self.close_dialog_x = page.locator("button.oxd-dialog-close-button")
        # Kept for any callers that just need "is a modal open" - built from
        # the button locator's own ancestor rather than a guessed class name.
        self.confirm_dialog = self.confirm_delete_button.locator(
            "xpath=ancestor::*[self::div or self::section][1]"
        )

        # --- Bulk actions ----------------------------------------------------
        self.bulk_delete_button = page.locator(
            ".orangehrm-bulk-action-container button, .oxd-table-toolbar button",
            has_text="Delete Selected",
        )

        # --- Toast / success notification -------------------------------------
        self.toast_message = page.locator(".oxd-toast-content, .oxd-toast")

    # --- Navigation actions -------------------------------------------------
    def open_pim_module(self):
        self.pim_menu_link.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.pim_menu_link.click()
        self.employee_list_tab.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self._wait_for_table_load()

    def _wait_for_table_load(self, timeout: int = None):
        """
        The Employee List table is populated by an async AJAX call after the
        tab renders, so checking table_rows/no_records_found immediately after
        navigation is a race condition. Wait for either state to attach before
        proceeding - this is called after every navigation, search, and reset.
        """
        timeout = timeout or Config.DEFAULT_TIMEOUT
        try:
            self.page.wait_for_selector(
                ".oxd-table-card, span:text-is('No Records Found')",
                timeout=timeout,
            )
        except Exception:
            # Table may genuinely still be empty/loading in edge cases - let
            # the calling assertion decide whether that's a failure.
            pass

    # --- Safe attribute helper -------------------------------------------------
    def _safe_ancestor_class(self, locator, xpath: str) -> str:
        """
        Looks up an ancestor via xpath and returns its `class` attribute.
        Playwright's `get_attribute()` waits/retries for a locator to resolve
        to at least one element - if the xpath legitimately matches nothing
        (e.g. no <li> wrapper exists in this markup), that wait runs until
        timeout instead of returning immediately. Guard with `count()` first,
        which checks the current DOM synchronously with no wait.
        """
        try:
            ancestor = locator.locator(f"xpath={xpath}")
            if ancestor.count() == 0:
                return ""
            return ancestor.get_attribute("class", timeout=2000) or ""
        except Exception:
            return ""

    def is_employee_list_tab_active(self) -> bool:
        """
        Same pattern as `is_pim_menu_highlighted`: the 'active' state class
        typically lives on an ancestor (<a>/<li>) of the tab's text node,
        not on the has_text-matched element itself. Check both, then fall
        back to the URL, which is the most reliable signal either way.
        """
        own_classes = self.employee_list_tab.get_attribute("class", timeout=2000) or ""
        if "active" in own_classes:
            return True

        if "active" in self._safe_ancestor_class(self.employee_list_tab, "ancestor-or-self::a[1]"):
            return True

        if "active" in self._safe_ancestor_class(self.employee_list_tab, "ancestor::li[1]"):
            return True

        return "viewEmployeeList" in self.page.url or "pim" in self.page.url.lower()

    def is_pim_menu_highlighted(self) -> bool:
        """
        The 'active' state class lives on an ancestor of the label span
        (typically the <a class="oxd-main-menu-item"> or its parent <li>),
        not on the span itself. Walk up the DOM to find it; fall back to
        checking the URL, which is the most reliable signal either way.
        """
        if "active" in self._safe_ancestor_class(self.pim_menu_link, "ancestor::a[1]"):
            return True

        if "active" in self._safe_ancestor_class(self.pim_menu_link, "ancestor::li[1]"):
            return True

        return "pim" in self.page.url.lower()

    # --- Filter actions -------------------------------------------------------
    def search_by_employee_name(
        self, name: str, require_hint: bool = False, hint_timeout: int = 3000
    ):
        """
        Employee Name is an autocomplete component, not a plain text field.
        Just calling `.fill()` and clicking Search leaves the component's
        internal "selected employee" state unset - the app can then silently
        ignore the typed text and return unfiltered results (observed: typing
        an exact-case match like 'Tyson' worked, but 'tyson' returned all 138
        records instead of the expected 1). This mirrors real usage: a person
        typing a name normally has a suggestion appear and gets it selected.

        By default, this method tries to select the first matching hint
        within `hint_timeout` - if one appears - and otherwise proceeds with
        the raw typed text. That fallback matters for callers who search for
        text with no matching employee on purpose (unregistered names,
        already-deleted names, injection/XSS payloads): those must NOT hang
        waiting for a hint that will never come.

        Set `require_hint=True` for happy-path searches where a hint should
        exist and its absence should fail loudly rather than silently
        degrading to an unfiltered/free-text search.
        """
        self.employee_name_input.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.employee_name_input.fill(name)

        # Known "empty state" text the dropdown itself renders when nothing
        # matches. If we blindly click whatever span appears first, we'd
        # click this placeholder for garbage/unregistered input - which can
        # overwrite the field's value with the placeholder's own text (or
        # clear it), so the query actually submitted on Search is no longer
        # what we typed. That silently turns an "unregistered name" search
        # into an empty/unfiltered one instead of a genuine no-match search.
        NO_MATCH_PHRASES = ("no matching", "no records", "no options", "no result")

        try:
            self.autocomplete_options.first.wait_for(state="visible", timeout=hint_timeout)
            hint_appeared = True
        except Exception:
            hint_appeared = False

        if not hint_appeared:
            if require_hint:
                raise AssertionError(
                    f"No autocomplete suggestion appeared for '{name}' within "
                    f"{hint_timeout}ms - expected an existing employee to match"
                )
            # No hint available (e.g. unregistered/deleted name, injection
            # payload) - proceed with the raw typed text as-is.
        else:
            option_text = self.autocomplete_options.first.inner_text().strip().lower()
            is_placeholder = any(phrase in option_text for phrase in NO_MATCH_PHRASES)

            if is_placeholder:
                if require_hint:
                    raise AssertionError(
                        f"No real autocomplete suggestion appeared for '{name}' - "
                        f"only a placeholder ('{option_text}') - expected an "
                        "existing employee to match"
                    )
                # Genuine "no match" placeholder - dismiss it without
                # clicking. NOTE: Escape is deliberately NOT used here - on
                # many autocomplete/typeahead components, Escape doesn't just
                # close the dropdown, it reverts the input to its previous
                # value (often empty), which would silently wipe out the very
                # text we're trying to search for and reproduce this exact
                # bug through a different path. Blur via JS instead, which
                # closes the dropdown through the component's outside-click/
                # blur handler without an associated "revert" behavior.
                self.employee_name_input.evaluate("el => el.blur()")
            else:
                self.autocomplete_options.first.click()

        # Final safety net regardless of which path above ran: some
        # component behaviors around dismissing the dropdown (blur, Escape,
        # clicking away) can still alter the field's value in ways that
        # aren't obvious from the outside. Explicitly confirm the field still
        # holds what we intended to search for immediately before submitting,
        # and re-fill if anything changed it.
        if self.employee_name_input.input_value() != name:
            self.employee_name_input.fill(name)
            # Re-filling can re-trigger the dropdown to reopen (fill()
            # dispatches an input event) - blur again so it doesn't overlap
            # and interfere with the Search button click below.
            self.employee_name_input.evaluate("el => el.blur()")

        self.click_search()

    def search_by_employment_status(self, status_label: str):
        self.employment_status_select.click()
        option = self.page.locator(".oxd-select-dropdown span", has_text=status_label)
        option.first.click()
        self.click_search()

    def click_search(self):
        self.search_button.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        self._wait_for_table_load()

    def click_reset(self):
        self.reset_button.click()
        self._wait_for_table_load()
        # Guard the filter form itself, not just the table - callers commonly
        # chain a fresh search_by_employee_name() right after reset, and the
        # form needs to have finished re-rendering before that fill/click.
        self.employee_name_input.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.search_button.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)

    # --- Table / result assertions helpers -------------------------------------
    def get_records_found_count(self) -> int:
        """Parses '(50) Records Found' -> 50. Returns 0 if 'No Records Found'."""
        if self.no_records_found.is_visible():
            return 0
        text = self.records_found_text.inner_text()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    def get_visible_row_count(self) -> int:
        return self.table_rows.count()

    def wait_for_results_to_settle(self, timeout: int = 5000, poll_interval: float = 0.2):
        """
        The 'Records Found' counter text and the actual table row cards are
        two separate reactive updates after a search - they don't necessarily
        land in the same tick, especially right after selecting an
        autocomplete hint (which triggers its own re-render on top of the
        Search click's). Comparing them the instant after a search is a race
        condition. Poll both until they agree (or `timeout` runs out) and
        return the final (records_found, row_count) pair either way, so the
        caller gets accurate numbers for its assertion message regardless of
        outcome.
        """
        start = time.monotonic()
        records_found = self.get_records_found_count()
        row_count = self.get_visible_row_count()
        while records_found != row_count and (time.monotonic() - start) < (timeout / 1000):
            self.page.wait_for_timeout(int(poll_interval * 1000))
            records_found = self.get_records_found_count()
            row_count = self.get_visible_row_count()
        return records_found, row_count

    def get_all_employee_names(self) -> list:
        names = []
        rows = self.table_rows
        for i in range(rows.count()):
            row_text = rows.nth(i).inner_text()
            names.append(row_text)
        return names

    def is_no_records_found_visible(self, timeout: int = 5000, poll_interval: float = 0.2) -> bool:
        """
        `_wait_for_table_load()` only confirms *some* `.oxd-table-card`
        attached at least once - which is trivially already true from the
        page's initial (populated) state before this search even ran. It
        gives no real guarantee when a search transitions FROM a populated
        table TO an empty one, since the stale old rows can still be
        attached at the instant we check. Poll for the actual "No Records
        Found" state directly instead of trusting a single snapshot.
        """
        start = time.monotonic()
        visible = self.no_records_found.is_visible()
        while not visible and (time.monotonic() - start) < (timeout / 1000):
            self.page.wait_for_timeout(int(poll_interval * 1000))
            visible = self.no_records_found.is_visible()
        return visible

    # --- Row action helpers -------------------------------------------------------
    def _reveal_row_actions(self, row_index: int):
        """
        Actual markup:
        <button class="oxd-icon-button oxd-table-cell-action-space" type="button">
          <i class="oxd-icon bi-trash"></i>
        </button>
        These action buttons are commonly hidden/hover-revealed on OrangeHRM's
        table rows, which is why a plain `.wait_for(state="visible")` on the
        icon timed out - the element exists in the DOM but isn't visible
        until the row is hovered. Scroll into view + hover before returning
        the row locator so callers get an interactable target.
        """
        row = self.table_rows.nth(row_index)
        row.scroll_into_view_if_needed()
        row.hover()
        return row

    def edit_icon_in_row(self, row_index: int):
        row = self._reveal_row_actions(row_index)
        return row.locator("i.bi-pencil-fill, i.bi-pencil, i[class*='bi-pencil']")

    def delete_icon_in_row(self, row_index: int):
        row = self._reveal_row_actions(row_index)
        return row.locator("i.bi-trash")

    def checkbox_in_row(self, row_index: int):
        return self.table_rows.nth(row_index).locator("input[type='checkbox']")

    def get_employee_name_in_row(self, row_index: int) -> str:
        # Employee names typically sit in the 3rd/4th data cell; using full row
        # text as a resilient fallback for name-substring assertions.
        return self.table_rows.nth(row_index).inner_text()

    def wait_for_row_text_to_contain(
        self, row_index: int, expected_substring: str, timeout: int = 5000,
        poll_interval: float = 0.2,
    ) -> str:
        """
        Row wrapper elements are commonly reused/patched in place across
        searches (Vue diffs the existing DOM node rather than replacing it),
        so `_wait_for_table_load()` seeing *a* row present doesn't guarantee
        *this* row's text reflects the latest search yet - cells can update
        asynchronously and out of order (e.g. the Id column refreshes before
        the Name column does), so a single `inner_text()` read right after a
        search can catch a partial/stale state (e.g. just "01715" with the
        name not yet in). Poll until the expected text actually shows up (or
        timeout), and return whatever the final read was either way so the
        caller's own assertion message stays accurate.
        """
        start = time.monotonic()
        row_text = self.get_employee_name_in_row(row_index)
        while (
            expected_substring.lower() not in row_text.lower()
            and (time.monotonic() - start) < (timeout / 1000)
        ):
            self.page.wait_for_timeout(int(poll_interval * 1000))
            row_text = self.get_employee_name_in_row(row_index)
        return row_text

    def click_delete_in_row(self, row_index: int):
        delete_icon = self.delete_icon_in_row(row_index)
        # Wait for at least "attached" rather than strictly "visible" - if the
        # hover-reveal transition hasn't fully finished, `visible` can still
        # read false for a moment. `force=True` on click bypasses Playwright's
        # own visibility/actionability check as a last-resort safety net,
        # since we've already hovered the row to reveal the icon ourselves.
        delete_icon.wait_for(state="attached", timeout=Config.DEFAULT_TIMEOUT)
        delete_icon.click(force=True)
        # Wait on the concrete "Yes, Delete" button rather than a guessed
        # dialog-container class - it's the element we need next anyway,
        # and it doesn't depend on unconfirmed wrapper markup.
        self.confirm_delete_button.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)

    def confirm_delete(self):
        self.confirm_delete_button.click()
        self.page.wait_for_load_state("networkidle")

    def cancel_delete(self):
        self.cancel_delete_button.click()

    def close_delete_dialog_via_x(self):
        self.close_dialog_x.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.close_dialog_x.click()

    def select_rows(self, row_indices: list):
        for idx in row_indices:
            self.checkbox_in_row(idx).check()

    def click_select_all_checkbox(self):
        self.select_all_checkbox.check()

    def is_bulk_delete_button_visible(self) -> bool:
        try:
            return self.bulk_delete_button.first.is_visible()
        except Exception:
            return False

    def click_bulk_delete(self):
        self.bulk_delete_button.first.click()
        self.confirm_delete_button.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)

    def get_toast_text(self, timeout: int = None) -> str:
        self.toast_message.first.wait_for(
            state="visible", timeout=timeout or Config.DEFAULT_TIMEOUT
        )
        return self.toast_message.first.inner_text().strip()
