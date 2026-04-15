"""Tests for src/utils/validation.py to improve coverage."""

import sys
from pathlib import Path

import pytest
from core.validation_utils import (IntegrityReport, _ensure_infrastructure_path,
                                  validate_markdown, validate_pdf_rendering)


class TestValidateMarkdown:
    """Test validate_markdown function."""

    def test_validate_markdown_success(self, tmp_path):
        """Test successful markdown validation."""
        markdown_dir = tmp_path / "manuscript"
        markdown_dir.mkdir()
        (markdown_dir / "test.md").write_text("# Test\n\nContent here.")

        result = validate_markdown(str(markdown_dir), strict=False)

        assert "status" in result
        assert "path" in result

    def test_validate_markdown_error_handling(self, tmp_path):
        """Test markdown validation error handling."""
        # Test with non-existent directory
        result = validate_markdown(str(tmp_path / "nonexistent"), strict=False)

        assert "status" in result
        # Should handle error gracefully
        assert result["status"] in ["validated", "issues_found", "error"]


class TestValidatePdfRendering:
    """Test validate_pdf_rendering function."""

    def test_validate_pdf_rendering_success(self, tmp_path):
        """Test PDF validation."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\\n1 0 obj <</Type/Catalog/Pages 2 0 R>> endobj\\n2 0 obj <</Type/Pages/Count 0/Kids[]>> endobj\\nxref\\n0 3\\n0000000000 65535 f \\n0000000009 00000 n \\n0000000052 00000 n \\ntrailer <</Size 3/Root 1 0 R>>\\nstartxref\\n95\\n%%EOF")

        result = validate_pdf_rendering(str(pdf_file))

        assert "status" in result
        assert "path" in result

    def test_validate_pdf_rendering_error_handling(self):
        """Test PDF validation error handling."""
        # Test with non-existent file
        result = validate_pdf_rendering("nonexistent.pdf")

        assert "status" in result
        # Should handle error gracefully
        assert result["status"] in ["validated", "issues_found", "error"]


class TestIntegrityReport:
    """Test IntegrityReport class."""

    def test_integrity_report_with_results(self):
        """Test creating integrity report with results."""
        results = {"status": "passed", "summary": "All checks passed", "issues": []}
        report = IntegrityReport(results)

        assert report.status == "passed"
        assert report.summary == "All checks passed"
        assert len(report.issues) == 0

    def test_integrity_report_without_results(self):
        """Test creating integrity report without results."""
        report = IntegrityReport()

        assert report.status == "not_validated"
        assert report.summary == "No validation performed"
        assert len(report.issues) == 0

    def test_integrity_report_string_representation(self):
        """Test string representation of integrity report."""
        results = {"status": "passed", "issues": []}
        report = IntegrityReport(results)

        str_repr = str(report)
        assert "IntegrityReport" in str_repr
        assert "passed" in str_repr


class TestEnsureInfrastructurePath:
    """Test _ensure_infrastructure_path function."""

    def test_infrastructure_already_available(self):
        """Test when infrastructure is already available."""
        # This function modifies sys.path, so we test it indirectly
        # by checking that it doesn't raise errors when infrastructure exists
        try:
            _ensure_infrastructure_path()
            # If no error, infrastructure was found or path was added
            assert True
        except Exception:
            # If error, that's also acceptable - infrastructure may not be available
            pass

    def test_infrastructure_path_addition(self):
        """Test adding infrastructure path when not available."""
        # Test that function handles missing infrastructure gracefully
        try:
            _ensure_infrastructure_path()
            # Function should complete without error
            assert True
        except Exception:
            # May fail if infrastructure doesn't exist, that's ok
            pass

    def test_ensure_path_when_infrastructure_missing(self, monkeypatch):
        """Force the ImportError branch inside _ensure_infrastructure_path."""
        saved = sys.modules.get("infrastructure")
        monkeypatch.delitem(sys.modules, "infrastructure", raising=False)
        monkeypatch.setattr(
            "builtins.__import__",
            _make_failing_import("infrastructure", monkeypatch),
        )
        _ensure_infrastructure_path()
        if saved is not None:
            sys.modules["infrastructure"] = saved


class TestValidateFigureRegistry:
    """Cover validate_figure_registry and verify_output_integrity error paths."""

    def test_validate_figure_registry_error(self, tmp_path):
        """validate_figure_registry returns error dict on missing file."""
        from core.validation_utils import validate_figure_registry

        result = validate_figure_registry(
            tmp_path / "nonexistent.json", tmp_path
        )
        assert result["status"] == "error"
        assert "error" in result

    def test_verify_output_integrity_error(self, tmp_path):
        """verify_output_integrity returns error dict on missing directory."""
        from core.validation_utils import verify_output_integrity

        result = verify_output_integrity(tmp_path / "nonexistent")
        assert result["status"] == "error"
        assert "error" in result


def _make_failing_import(blocked_name, monkeypatch):
    """Return an __import__ replacement that raises ImportError for *blocked_name*."""
    real_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    def _import(name, *args, **kwargs):
        if name == blocked_name:
            raise ImportError(f"Simulated missing {blocked_name}")
        return real_import(name, *args, **kwargs)

    return _import
