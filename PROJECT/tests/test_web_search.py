"""Tests for web search service."""

from backend.services.web_search import format_search_results_for_llm


class TestFormatSearchResults:
    """Test the LLM-friendly result formatter."""

    def test_formats_results_with_numbers(self):
        results = [
            {"title": "Test", "snippet": "A snippet", "url": "https://example.com"}
        ]
        output = format_search_results_for_llm(results)
        assert "[1]" in output
        assert "Test" in output
        assert "https://example.com" in output

    def test_empty_results_returns_message(self):
        output = format_search_results_for_llm([])
        assert "No web results found" in output

    def test_multiple_results_numbered(self):
        results = [
            {"title": f"Result {i}", "snippet": "text", "url": "url"}
            for i in range(3)
        ]
        output = format_search_results_for_llm(results)
        assert "[1]" in output
        assert "[2]" in output
        assert "[3]" in output

    def test_missing_fields_handled(self):
        results = [{"title": "", "snippet": "", "url": ""}]
        output = format_search_results_for_llm(results)
        assert "[1]" in output
