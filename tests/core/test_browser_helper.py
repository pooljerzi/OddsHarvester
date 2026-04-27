import logging
from unittest.mock import AsyncMock, patch

import pytest

from oddsharvester.core.browser_helper import BrowserHelper


class TestBrowserHelper:
    """Test cases for BrowserHelper."""

    @pytest.fixture
    def browser_helper(self):
        """Create a BrowserHelper instance."""
        return BrowserHelper()

    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright page."""
        page = AsyncMock()
        return page

    # =============================================================================
    # MARKET NAVIGATION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_success_direct(self, browser_helper, mock_page):
        """Test successful market tab navigation (directly visible)."""
        # Mock successful navigation
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=True),
            patch.object(browser_helper, "_verify_tab_is_active", return_value=True),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet")
            assert result is True

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_success_dropdown(self, browser_helper, mock_page):
        """Test successful market tab navigation (via dropdown)."""
        # Mock failed direct navigation but successful dropdown navigation
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=False),
            patch.object(browser_helper, "_click_more_if_market_hidden", return_value=True),
            patch.object(browser_helper, "_verify_tab_is_active", return_value=True),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet")
            assert result is True

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_clicked_but_not_active(self, browser_helper, mock_page):
        """Test market tab navigation when clicked but not active."""
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=True),
            patch.object(browser_helper, "_verify_tab_is_active", return_value=False),
            patch.object(browser_helper, "_click_more_if_market_hidden", return_value=False),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet")
            assert result is False

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_complete_failure(self, browser_helper, mock_page):
        """Test market tab navigation when all attempts fail."""
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=False),
            patch.object(browser_helper, "_click_more_if_market_hidden", return_value=False),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet")
            assert result is False

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_dropdown_clicked_but_not_active(self, browser_helper, mock_page):
        """Test market tab navigation when dropdown clicked but not active."""
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=False),
            patch.object(browser_helper, "_click_more_if_market_hidden", return_value=True),
            patch.object(browser_helper, "_verify_tab_is_active", return_value=False),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet")
            assert result is False

    # =============================================================================
    # PRIVATE HELPER METHODS TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_wait_and_click_success_with_text(self, browser_helper, mock_page):
        """Test successful wait and click with text."""
        with patch.object(browser_helper, "_click_by_text", return_value=True):
            result = await browser_helper._wait_and_click(mock_page, "test-selector", "test-text")
            assert result is True
            mock_page.wait_for_selector.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_and_click_success_without_text(self, browser_helper, mock_page):
        """Test successful wait and click without text."""
        mock_element = AsyncMock()
        mock_page.query_selector.return_value = mock_element

        result = await browser_helper._wait_and_click(mock_page, "test-selector")
        assert result is True
        mock_page.wait_for_selector.assert_called_once()
        mock_element.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_and_click_wait_error(self, browser_helper, mock_page):
        """Test wait and click when wait_for_selector fails."""
        mock_page.wait_for_selector.side_effect = Exception("Wait failed")

        result = await browser_helper._wait_and_click(mock_page, "test-selector", "test-text")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_by_text_success(self, browser_helper, mock_page):
        """Test successful click by text."""
        # Mock element with matching text
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Target Text"

        mock_page.query_selector_all.return_value = [mock_element]

        result = await browser_helper._click_by_text(mock_page, "test-selector", "Target")
        assert result is True
        mock_element.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_by_text_no_match(self, browser_helper, mock_page):
        """Test click by text when no match is found."""
        # Mock element with different text
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Different Text"

        mock_page.query_selector_all.return_value = [mock_element]

        result = await browser_helper._click_by_text(mock_page, "test-selector", "Target")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_by_text_empty_text(self, browser_helper, mock_page):
        """Test click by text when element text is empty."""
        # Mock element with empty text
        mock_element = AsyncMock()
        mock_element.text_content.return_value = ""

        mock_page.query_selector_all.return_value = [mock_element]

        result = await browser_helper._click_by_text(mock_page, "test-selector", "Target")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_by_text_click_error(self, browser_helper, mock_page):
        """Test click by text when click fails."""
        # Mock element with matching text but click fails
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Target Text"
        mock_element.click.side_effect = Exception("Click failed")

        mock_page.query_selector_all.return_value = [mock_element]

        result = await browser_helper._click_by_text(mock_page, "test-selector", "Target")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_by_text_query_error(self, browser_helper, mock_page):
        """Test click by text when query_selector_all fails."""
        mock_page.query_selector_all.side_effect = Exception("Query failed")

        result = await browser_helper._click_by_text(mock_page, "test-selector", "Target")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_success(self, browser_helper, mock_page):
        """Test successful click more if market hidden."""
        # Mock more button found and clicked
        mock_more_element = AsyncMock()
        mock_more_element.text_content.return_value = "More"

        # Mock dropdown element found and clicked
        mock_dropdown_element = AsyncMock()
        mock_dropdown_element.text_content.return_value = "Draw No Bet"

        mock_page.query_selector.side_effect = [mock_more_element, mock_dropdown_element]
        mock_page.wait_for_timeout = AsyncMock()

        result = await browser_helper._click_more_if_market_hidden(mock_page, "Draw No Bet")
        assert result is True

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_no_more_button(self, browser_helper, mock_page):
        """Test click more if market hidden when no more button is found."""
        # Mock no more button found
        mock_page.query_selector.return_value = None

        result = await browser_helper._click_more_if_market_hidden(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_more_button_click_error(self, browser_helper, mock_page):
        """Test click more if market hidden when more button click fails."""
        # Mock more button found but click fails
        mock_more_element = AsyncMock()
        mock_more_element.text_content.return_value = "More"
        mock_more_element.click.side_effect = Exception("Click failed")

        mock_page.query_selector.return_value = mock_more_element

        result = await browser_helper._click_more_if_market_hidden(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_no_dropdown_match(self, browser_helper, mock_page):
        """Test click more if market hidden when no dropdown match is found."""
        # Mock more button found and clicked
        mock_more_element = AsyncMock()
        mock_more_element.text_content.return_value = "More"

        # Mock dropdown element found but no text match
        mock_dropdown_element = AsyncMock()
        mock_dropdown_element.text_content.return_value = "Different Market"

        mock_page.query_selector.side_effect = [mock_more_element, mock_dropdown_element]
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all.return_value = []  # No debug elements

        result = await browser_helper._click_more_if_market_hidden(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_dropdown_click_error(self, browser_helper, mock_page):
        """Test click more if market hidden when dropdown click fails."""
        # Mock more button found and clicked
        mock_more_element = AsyncMock()
        mock_more_element.text_content.return_value = "More"

        # Mock dropdown element found but click fails
        mock_dropdown_element = AsyncMock()
        mock_dropdown_element.text_content.return_value = "Draw No Bet"
        mock_dropdown_element.click.side_effect = Exception("Click failed")

        mock_page.query_selector.side_effect = [mock_more_element, mock_dropdown_element]
        mock_page.wait_for_timeout = AsyncMock()

        result = await browser_helper._click_more_if_market_hidden(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_exception(self, browser_helper, mock_page):
        """Test click more if market hidden when exception occurs."""
        mock_page.query_selector.side_effect = Exception("General error")

        result = await browser_helper._click_more_if_market_hidden(mock_page, "Draw No Bet")
        assert result is False

    # =============================================================================
    # TAB VERIFICATION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_success(self, browser_helper, mock_page):
        """Test successful tab verification."""
        # Mock active element with correct market name
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Draw No Bet"
        mock_page.query_selector.return_value = mock_element

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_wrong_market(self, browser_helper, mock_page):
        """Test tab verification with wrong market name."""
        # Mock active element with different market name
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="1X2")
        mock_page.query_selector = AsyncMock(return_value=mock_element)
        # Mock content to return string that doesn't contain the market name
        mock_page.content = AsyncMock(return_value="some content without the target market")

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_no_active_element(self, browser_helper, mock_page):
        """Test tab verification when no active element is found."""
        # Mock no active element found
        mock_page.query_selector.return_value = None
        mock_page.content = AsyncMock(return_value="<html><body>Some content</body></html>")

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_content_fallback(self, browser_helper, mock_page):
        """Test tab verification using content fallback."""
        # Mock no active element but market name in content
        mock_page.query_selector.return_value = None
        mock_page.content = AsyncMock(return_value="<html><body>Draw No Bet content</body></html>")

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_exception_handling(self, browser_helper, mock_page):
        """Test tab verification with exception handling."""
        # Mock exception during verification
        mock_page.query_selector = AsyncMock(side_effect=Exception("Test exception"))
        # Mock content to return string that doesn't contain the market name
        mock_page.content = AsyncMock(return_value="some content without the target market")

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_empty_text(self, browser_helper, mock_page):
        """Test tab verification with empty text content."""
        # Mock active element with empty text
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="")
        mock_page.query_selector = AsyncMock(return_value=mock_element)
        # Mock content to return string that doesn't contain the market name
        mock_page.content = AsyncMock(return_value="some content without the target market")

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_case_insensitive(self, browser_helper, mock_page):
        """Test tab verification with case insensitive matching."""
        # Mock active element with different case
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="DRAW NO BET")
        mock_page.query_selector.return_value = mock_element

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_partial_match(self, browser_helper, mock_page):
        """Test tab verification with partial text match."""
        # Mock active element with partial match
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="Draw No Bet Market")
        mock_page.query_selector.return_value = mock_element

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_content_exception(self, browser_helper, mock_page):
        """Test tab verification when content() fails."""
        # Mock active element not found and content() fails
        mock_page.query_selector.return_value = None
        mock_page.content = AsyncMock(side_effect=Exception("Content failed"))

        result = await browser_helper._verify_tab_is_active(mock_page, "Draw No Bet")
        assert result is False

    # =============================================================================
    # EDGE CASES AND ERROR HANDLING TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_empty_market_name(self, browser_helper, mock_page):
        """Test market tab navigation with empty market name."""
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=False),
            patch.object(browser_helper, "_click_more_if_market_hidden", return_value=False),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "")
            assert result is False

    @pytest.mark.asyncio
    async def test_navigate_to_market_tab_none_market_name(self, browser_helper, mock_page):
        """Test market tab navigation with None market name."""
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=False),
            patch.object(browser_helper, "_click_more_if_market_hidden", return_value=False),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, None)
            assert result is False

    @pytest.mark.asyncio
    async def test_wait_and_click_empty_selector(self, browser_helper, mock_page):
        """Test wait and click with empty selector."""
        result = await browser_helper._wait_and_click(mock_page, "", "test-text")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_by_text_empty_selector(self, browser_helper, mock_page):
        """Test click by text with empty selector."""
        result = await browser_helper._click_by_text(mock_page, "", "test-text")
        assert result is False

    @pytest.mark.asyncio
    async def test_click_more_if_market_hidden_empty_market_name(self, browser_helper, mock_page):
        """Test click more if market hidden with empty market name."""
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await browser_helper._click_more_if_market_hidden(mock_page, "")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_tab_is_active_empty_market_name(self, browser_helper, mock_page):
        """Test verify tab is active with empty market name."""
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.content = AsyncMock(return_value="some content without empty market name")

        result = await browser_helper._verify_tab_is_active(mock_page, "")
        assert result is False

    # =============================================================================
    # LOGGING TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_logging_during_market_navigation(self, browser_helper, mock_page, caplog):
        """Test logging during market navigation."""
        with caplog.at_level(logging.INFO):
            with (
                patch.object(browser_helper, "_wait_and_click", return_value=True),
                patch.object(browser_helper, "_verify_tab_is_active", return_value=True),
            ):
                await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet")

                assert "Attempting to navigate to market tab: Draw No Bet" in caplog.text
                assert "Successfully navigated to Draw No Bet tab" in caplog.text

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_full_market_navigation_flow(self, browser_helper, mock_page):
        """Test the complete market navigation flow."""
        # Mock successful navigation through all steps
        with (
            patch.object(browser_helper, "_wait_and_click", return_value=True),
            patch.object(browser_helper, "_verify_tab_is_active", return_value=True),
        ):
            result = await browser_helper.navigate_to_market_tab(mock_page, "Draw No Bet", timeout=5000)
            assert result is True
