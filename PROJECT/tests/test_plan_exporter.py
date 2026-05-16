"""Tests for plan exporter."""

from backend.services.plan_exporter import export_plan, _format_date


class TestExportPlan:
    """Test the plan.md generator."""

    def test_includes_all_sections(self):
        results = {
            "occupation": "Developer",
            "idea": "AI tool",
            "timestamp": "2025-01-01T12:00:00",
            "stages": {
                "brainstorm": {"content": "Ideas here"},
                "sentiment": {"content": "Sentiment here"},
                "niche": {"content": "Niche here"},
                "mvp": {"content": "MVP here"},
            },
        }
        plan = export_plan(results)
        assert "Developer" in plan
        assert "AI tool" in plan
        assert "Ideas here" in plan
        assert "Sentiment here" in plan
        assert "Niche here" in plan
        assert "MVP here" in plan

    def test_handles_missing_stages(self):
        results = {"occupation": "Test", "idea": "Test", "stages": {}}
        plan = export_plan(results)
        assert "N/A" in plan

    def test_contains_header(self):
        results = {"occupation": "X", "idea": "Y", "stages": {}}
        plan = export_plan(results)
        assert "PRODUCT THINKER" in plan


class TestFormatDate:
    """Test date formatting."""

    def test_valid_iso_formatted(self):
        result = _format_date("2025-06-15T14:30:00")
        assert "June" in result
        assert "2025" in result

    def test_invalid_returns_original(self):
        result = _format_date("not-a-date")
        assert result == "not-a-date"
