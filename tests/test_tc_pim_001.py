"""
TC-PIM-001 | PIM / Employee List
Title: Navigasi ke Menu PIM dan Tampilan Employee List
       (Navigate to PIM Menu and Employee List View)
Pre-conditions: User sudah login (fulfilled by the `pim_page` fixture, TC-AUTH-001).
Priority: P1 - Critical

Steps:
    1. Click 'PIM' on the sidebar
    2. Observe the default active tab

Expected Result:
    PIM page opens with the 'Employee List' tab active; the PIM sidebar item
    is highlighted; the filter section and data table are displayed.
"""
import pytest


@pytest.mark.p1
@pytest.mark.smoke
class TestTC_PIM_001:
    def test_navigate_to_pim_opens_employee_list_tab(self, pim_page):
        # `pim_page` fixture already logged in and clicked PIM -> this
        # asserts the resulting state matches the expected default view.
        assert "PIM" in pim_page.page_heading.inner_text(), (
            "Page heading does not indicate the PIM module is open"
        )
        assert pim_page.is_employee_list_tab_active(), (
            "'PIM' tab is not marked active by default"
        )

    def test_pim_sidebar_item_is_highlighted(self, pim_page):
        assert pim_page.is_pim_menu_highlighted(), (
            "PIM sidebar menu item is not highlighted/active"
        )

    def test_filter_section_and_table_are_visible(self, pim_page):
        assert pim_page.employee_name_input.is_visible(), (
            "Filter section (Employee Name field) is not visible"
        )
        assert pim_page.search_button.is_visible(), "Search button is not visible"
        assert (
            pim_page.table_rows.first.is_visible()
            or pim_page.is_no_records_found_visible()
        ), "Employee data table is not rendered"
