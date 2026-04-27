from enum import Enum
import logging

from playwright.async_api import Page

from oddsharvester.core.odds_portal_selectors import OddsPortalSelectors
from oddsharvester.utils.bookies_filter_enum import BookiesFilter
from oddsharvester.utils.constants import (
    BOOKIES_FILTER_TIMEOUT_MS,
    FALLBACK_VERIFY_WAIT_MS,
    PERIOD_SELECTOR_TIMEOUT_MS,
)


class BrowserHelper:
    """
    A helper class for managing common browser interactions using Playwright.

    This class provides high-level methods for:
    - Cookie banner management
    - Market navigation (including hidden markets)
    - Scrolling operations
    - Element interaction utilities
    """

    def __init__(self):
        """
        Initialize the BrowserHelper class.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    # =============================================================================
    # BOOKMAKER FILTER MANAGEMENT
    # =============================================================================

    async def ensure_bookies_filter_selected(self, page: Page, desired_filter: BookiesFilter) -> bool:
        """
        Ensure the desired bookmaker filter is selected on the page.

        This method:
        1. Checks if the bookies filter nav is present
        2. Reads the currently selected filter
        3. If it matches desired filter, does nothing
        4. Otherwise, clicks the desired filter option
        5. Waits for the selection to update

        Args:
            page (Page): The Playwright page instance.
            desired_filter (BookiesFilter): The desired bookmaker filter to select.

        Returns:
            bool: True if the desired filter is selected, False otherwise.
        """
        try:
            display_label = BookiesFilter.get_display_label(desired_filter)
            self.logger.info(f"Ensuring bookmaker filter is set to: {display_label}")

            # Check if bookies filter nav exists
            filter_container = await page.query_selector(OddsPortalSelectors.BOOKIES_FILTER_CONTAINER)
            if not filter_container:
                self.logger.warning("Bookies filter navigation not found on page. Skipping filter selection.")
                return False

            # Get current selected filter
            current_filter = await self._get_current_bookies_filter(page)
            if current_filter:
                self.logger.info(f"Current bookmaker filter: {current_filter}")

                # If already selected, do nothing
                if current_filter == desired_filter.value:
                    self.logger.info(f"Bookmaker filter already set to '{desired_filter.value}'. No action needed.")

                    return True

            # Click the desired filter
            filter_selector = OddsPortalSelectors.get_bookies_filter_selector(desired_filter.value)

            self.logger.info(f"Clicking bookmaker filter: {BookiesFilter.get_display_label(desired_filter)}")
            filter_element = await page.query_selector(filter_selector)

            if not filter_element:
                self.logger.error(f"Bookmaker filter element not found for: {desired_filter.value}")
                return False

            await filter_element.click()

            # Wait for selection to update using robust wait condition
            try:
                active_class = OddsPortalSelectors.BOOKIES_FILTER_ACTIVE_CLASS
                await page.wait_for_function(
                    f"""
                    () => {{
                        const container = document.querySelector('[data-testid="bookies-filter-nav"]');
                        if (!container) return false;
                        const activeElement = container.querySelector('.{active_class}');
                        if (!activeElement) return false;
                        return activeElement.getAttribute('data-testid') === '{desired_filter.value}';
                    }}
                    """,
                    timeout=BOOKIES_FILTER_TIMEOUT_MS,
                )
                display_label = BookiesFilter.get_display_label(desired_filter)
                self.logger.info(f"Successfully set bookmaker filter to: {display_label}")
                return True

            except Exception as wait_error:
                self.logger.warning(f"Wait condition failed: {wait_error}. Verifying selection...")

                # Fallback: verify the selection after a short delay
                await page.wait_for_timeout(FALLBACK_VERIFY_WAIT_MS)
                new_filter = await self._get_current_bookies_filter(page)
                if new_filter == desired_filter.value:
                    self.logger.info(f"Bookmaker filter successfully set to: {desired_filter.value}")
                    return True
                else:
                    self.logger.error(f"Failed to set bookmaker filter to: {desired_filter.value}")
                    return False

        except Exception as e:
            self.logger.error(f"Error setting bookmaker filter: {e}")
            return False

    async def _get_current_bookies_filter(self, page: Page) -> str | None:
        """
        Get the currently selected bookmaker filter.

        Args:
            page (Page): The Playwright page instance.

        Returns:
            str | None: The data-testid of the currently selected filter, or None if not found.
        """
        try:
            # Find the active element within the bookies filter container
            active_selector = (
                f"{OddsPortalSelectors.BOOKIES_FILTER_CONTAINER} .{OddsPortalSelectors.BOOKIES_FILTER_ACTIVE_CLASS}"
            )
            active_element = await page.query_selector(active_selector)

            if active_element:
                data_testid = await active_element.get_attribute("data-testid")
                return data_testid

            self.logger.warning("No active bookmaker filter found")
            return None

        except Exception as e:
            self.logger.error(f"Error getting current bookmaker filter: {e}")
            return None

    # =============================================================================
    # PERIOD SELECTION MANAGEMENT
    # =============================================================================

    async def ensure_period_selected(self, page: Page, desired_period: Enum) -> bool:
        """
        Ensure the desired match period is selected on the page.

        This method:
        1. Checks if the period selector nav is present
        2. Reads the currently selected period
        3. If it matches desired period, does nothing
        4. Otherwise, clicks the desired period option
        5. Waits for the selection to update

        Args:
            page (Page): The Playwright page instance.
            desired_period: The desired period enum to select.

        Returns:
            bool: True if the desired period is selected, False otherwise.
        """
        try:
            # All period enums have get_display_label method
            display_label = desired_period.get_display_label(desired_period)
            self.logger.info(f"Ensuring match period is set to: {display_label}")

            # Check if period selector nav exists
            period_container = await page.query_selector(OddsPortalSelectors.PERIOD_SELECTOR_CONTAINER)
            if not period_container:
                self.logger.warning("Period selector navigation not found on page. Skipping period selection.")
                return False

            # Get current selected period
            current_period = await self._get_current_period(page)
            if current_period:
                self.logger.info(f"Current match period: {current_period}")

                # If already selected, do nothing
                if current_period == display_label:
                    self.logger.info(f"Match period already set to '{display_label}'. No action needed.")
                    return True

            # Click the desired period
            self.logger.info(f"Clicking match period: {display_label}")

            # Find the period element by text within the container
            period_element = await page.query_selector(
                f"{OddsPortalSelectors.PERIOD_SELECTOR_CONTAINER} div:has-text('{display_label}')"
            )

            if not period_element:
                self.logger.error(f"Period element not found for: {display_label}")
                return False

            await period_element.click()

            # Wait for selection to update using robust wait condition
            try:
                active_class = OddsPortalSelectors.PERIOD_ACTIVE_CLASS
                await page.wait_for_function(
                    f"""
                    () => {{
                        const container = document.querySelector('[data-testid="kickoff-events-nav"]');
                        if (!container) return false;
                        const activeElement = container.querySelector('.{active_class}');
                        if (!activeElement) return false;
                        return activeElement.textContent.trim() === '{display_label}';
                    }}
                    """,
                    timeout=PERIOD_SELECTOR_TIMEOUT_MS,
                )
                self.logger.info(f"Successfully set match period to: {display_label}")
                return True

            except Exception as wait_error:
                self.logger.warning(f"Wait condition failed: {wait_error}. Verifying selection...")

                # Fallback: verify the selection after a short delay
                await page.wait_for_timeout(FALLBACK_VERIFY_WAIT_MS)
                new_period = await self._get_current_period(page)
                if new_period == display_label:
                    self.logger.info(f"Match period successfully set to: {display_label}")
                    return True
                else:
                    self.logger.error(f"Failed to set match period to: {display_label}")
                    return False

        except Exception as e:
            self.logger.error(f"Error setting match period: {e}")
            return False

    async def _get_current_period(self, page: Page) -> str | None:
        """
        Get the currently selected match period.

        Args:
            page (Page): The Playwright page instance.

        Returns:
            str | None: The text of the currently selected period, or None if not found.
        """
        try:
            # Find the active element within the period selector container
            active_selector = (
                f"{OddsPortalSelectors.PERIOD_SELECTOR_CONTAINER} .{OddsPortalSelectors.PERIOD_ACTIVE_CLASS}"
            )
            active_element = await page.query_selector(active_selector)

            if active_element:
                period_text = await active_element.text_content()
                return period_text.strip() if period_text else None

            self.logger.warning("No active period found")
            return None

        except Exception as e:
            self.logger.error(f"Error getting current period: {e}")
            return None
