"""Tests for the _quality_report.py script.

Validates the quality report generation logic — argument parsing, error
aggregation, and JSON report output — using subprocess (no mocks).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


# Ensure the scripts and src directories are importable
PROJECT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_DIR / "scripts"


SUBPROCESS_TIMEOUT_SECONDS = 1800


def run_subprocess(*args, **kwargs):
    """subprocess.run with a hard timeout; raises pytest.fail.TestFailed on expiry."""
    kwargs.setdefault("timeout", SUBPROCESS_TIMEOUT_SECONDS)
    try:
        return subprocess.run(*args, **kwargs)
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"Subprocess timed out after {SUBPROCESS_TIMEOUT_SECONDS}s: {exc.cmd}")


# ═══════════════════════════════════════════════════════════════════════
#  Argument Parsing (via subprocess)
# ═══════════════════════════════════════════════════════════════════════


class TestParseArgs:
    """Tests for _parse_args via subprocess execution."""

    def test_default_args_resolve_from_project_root(self, tmp_path: Path):
        """Defaults derive from the project root, independent of the CWD."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "_quality_report_defaults", SCRIPTS_DIR / "_quality_report.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        args = mod._parse_args([])
        assert args.manuscript_dir == PROJECT_DIR / "docs" / "manuscript"
        assert args.output_dir == PROJECT_DIR / "output" / "reports"

    def test_default_manuscript_dir_runs_from_foreign_cwd(self, tmp_path: Path):
        """Running with only --output-dir from an unrelated CWD still succeeds
        against the real docs/manuscript directory."""
        out_dir = tmp_path / "reports"
        result = run_subprocess([
            sys.executable,
            str(SCRIPTS_DIR / "_quality_report.py"),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),)
        assert result.returncode == 0, f"stderr: {result.stderr}"

        report = json.loads((out_dir / "quality_report.json").read_text())
        assert "markdown_issues" in report

    def test_explicit_real_manuscript_dir_runs(self, tmp_path: Path):
        """Running against the real docs/manuscript directory completes."""
        out_dir = tmp_path / "reports"
        ms_dir = PROJECT_DIR / "docs" / "manuscript"
        result = run_subprocess([
            sys.executable,
            str(SCRIPTS_DIR / "_quality_report.py"),
            "--manuscript-dir",
            str(ms_dir),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),)
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_custom_args(self, tmp_path: Path):
        """Custom manuscript and output dirs should be accepted."""
        ms_dir = tmp_path / "manuscript"
        ms_dir.mkdir()
        (ms_dir / "01_abstract.md").write_text("# Abstract\nTest.")
        out_dir = tmp_path / "output"

        result = run_subprocess([
            sys.executable,
            str(SCRIPTS_DIR / "_quality_report.py"),
            "--manuscript-dir",
            str(ms_dir),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert out_dir.exists()


# ═══════════════════════════════════════════════════════════════════════
#  Error Aggregator Integration
# ═══════════════════════════════════════════════════════════════════════


# Need src/ on path for direct import
sys.path.insert(0, str(PROJECT_DIR / "src"))


class TestErrorAggregator:
    """Tests for error aggregator interaction."""

    def test_get_error_aggregator_returns_object(self):
        """get_error_aggregator should return an object with add_error and get_summary."""
        from pipeline.reporting import get_error_aggregator

        agg = get_error_aggregator()
        assert hasattr(agg, "add_error") or hasattr(agg, "__setitem__")
        assert hasattr(agg, "get_summary") or hasattr(agg, "__getitem__")


# ═══════════════════════════════════════════════════════════════════════
#  Main Function Integration Tests (via subprocess)
# ═══════════════════════════════════════════════════════════════════════


class TestMainFunction:
    """Integration tests for the main() function via subprocess."""

    def test_main_creates_output(self, tmp_path: Path):
        """main() should create a quality_report.json in the output directory."""
        ms_dir = tmp_path / "manuscript"
        ms_dir.mkdir()
        (ms_dir / "01_abstract.md").write_text("# Abstract\nTest abstract.")
        (ms_dir / "98_symbols_glossary.md").write_text("# Glossary")
        (ms_dir / "99_references.md").write_text(r"\bibliography{references}")

        out_dir = tmp_path / "reports"

        result = run_subprocess([
            sys.executable,
            str(SCRIPTS_DIR / "_quality_report.py"),
            "--manuscript-dir",
            str(ms_dir),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),)
        assert result.returncode == 0, f"stderr: {result.stderr}"

        report_path = out_dir / "quality_report.json"
        assert report_path.exists(), "quality_report.json should be created"

        report = json.loads(report_path.read_text())
        assert "markdown_issues" in report
        assert "quality_metrics" in report
        assert "errors" in report

    def test_main_handles_missing_manuscript_gracefully(self, tmp_path: Path):
        """main() should not crash when manuscript dir is empty."""
        ms_dir = tmp_path / "empty_manuscript"
        ms_dir.mkdir()
        out_dir = tmp_path / "reports"

        result = run_subprocess([
            sys.executable,
            str(SCRIPTS_DIR / "_quality_report.py"),
            "--manuscript-dir",
            str(ms_dir),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),)
        assert result.returncode == 0, f"stderr: {result.stderr}"

        report_path = out_dir / "quality_report.json"
        assert report_path.exists()

    def test_report_has_expected_keys(self, tmp_path: Path):
        """The generated report should contain all expected top-level keys."""
        ms_dir = tmp_path / "manuscript"
        ms_dir.mkdir()
        (ms_dir / "01_abstract.md").write_text("# Abstract")

        out_dir = tmp_path / "reports"

        result = run_subprocess([
            sys.executable,
            str(SCRIPTS_DIR / "_quality_report.py"),
            "--manuscript-dir",
            str(ms_dir),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),)
        assert result.returncode == 0, f"stderr: {result.stderr}"

        report = json.loads((out_dir / "quality_report.json").read_text())
        expected_keys = {
            "markdown_issues",
            "quality_metrics",
            "integrity_summary",
            "reproducibility",
            "errors",
        }
        assert expected_keys.issubset(
            set(report.keys())
        ), f"Missing keys: {expected_keys - set(report.keys())}"
