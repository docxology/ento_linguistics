"""Tests for the _manuscript_preflight.py script.

Validates that preflight checks correctly detect missing figures,
absent glossary markers, and missing references blocks.
"""
from __future__ import annotations

import sys
from pathlib import Path


import pytest

# Ensure the scripts directory is importable
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "scripts"))
sys.path.insert(0, str(PROJECT_DIR / "src"))


# ---------------------------------------------------------------------------
# Import helpers — _manuscript_preflight registers its own sys.path entries
# so we just import the module directly.
# ---------------------------------------------------------------------------
import importlib

_preflight = importlib.import_module("_manuscript_preflight")
CheckResult = _preflight.CheckResult
_find_markdown_files = _preflight._find_markdown_files
_collect_figure_paths = _preflight._collect_figure_paths
run_checks = _preflight.run_checks


# ═══════════════════════════════════════════════════════════════════════
#  CheckResult dataclass
# ═══════════════════════════════════════════════════════════════════════


class TestCheckResult:
    """Tests for the CheckResult dataclass."""

    def test_clean_result(self):
        """A result with no issues reports is_clean() == True."""
        result = CheckResult(
            missing_figures=[],
            missing_glossary_markers=False,
            missing_references_block=False,
        )
        assert result.is_clean()

    def test_missing_figures_not_clean(self):
        """Missing figures should make the result not clean."""
        result = CheckResult(
            missing_figures=["04a_corpus_and_networks.md: fig/missing.png"],
            missing_glossary_markers=False,
            missing_references_block=False,
        )
        assert not result.is_clean()

    def test_missing_glossary_not_clean(self):
        """Missing glossary markers should make the result not clean."""
        result = CheckResult(
            missing_figures=[],
            missing_glossary_markers=True,
            missing_references_block=False,
        )
        assert not result.is_clean()

    def test_missing_references_not_clean(self):
        """Missing references block should make the result not clean."""
        result = CheckResult(
            missing_figures=[],
            missing_glossary_markers=False,
            missing_references_block=True,
        )
        assert not result.is_clean()

    def test_all_issues_not_clean(self):
        """All issues present should make the result not clean."""
        result = CheckResult(
            missing_figures=["test.md: fig.png"],
            missing_glossary_markers=True,
            missing_references_block=True,
        )
        assert not result.is_clean()


# ═══════════════════════════════════════════════════════════════════════
#  File discovery helpers
# ═══════════════════════════════════════════════════════════════════════


class TestFileDiscovery:
    """Tests for _find_markdown_files."""

    def test_finds_markdown_files(self, tmp_path: Path):
        """Should discover .md files in a directory."""
        (tmp_path / "01_abstract.md").write_text("# Abstract")
        (tmp_path / "02_intro.md").write_text("# Introduction")
        (tmp_path / "not_markdown.txt").write_text("plain text")

        files = _find_markdown_files(tmp_path)
        assert len(files) == 2
        assert all(f.suffix == ".md" for f in files)

    def test_empty_directory(self, tmp_path: Path):
        """Returns empty list for a directory with no .md files."""
        (tmp_path / "readme.txt").write_text("not markdown")
        assert _find_markdown_files(tmp_path) == []


class TestCollectFigurePaths:
    """Tests for _collect_figure_paths."""

    def test_detects_includegraphics(self, tmp_path: Path):
        """Should extract paths from \\includegraphics directives."""
        md = tmp_path / "04_results.md"
        md.write_text(
            r"\includegraphics[width=\textwidth]{output/figures/concept_map.png}"
        )
        refs = _collect_figure_paths([md])
        assert len(refs) == 1
        assert refs[0][1] == "output/figures/concept_map.png"

    def test_no_figures(self, tmp_path: Path):
        """Returns empty when no figure references exist."""
        md = tmp_path / "01_abstract.md"
        md.write_text("Just plain text, no figures.")
        assert _collect_figure_paths([md]) == []


# ═══════════════════════════════════════════════════════════════════════
#  run_checks integration
# ═══════════════════════════════════════════════════════════════════════


class TestRunChecks:
    """Integration tests for the run_checks function."""

    def test_clean_manuscript(self, tmp_path: Path):
        """A well-formed manuscript directory passes all checks."""
        # Create figure that exists
        fig_dir = tmp_path / "output" / "figures"
        fig_dir.mkdir(parents=True)
        (fig_dir / "concept_map.png").write_text("fake png")

        # Create markdown that references existing figure
        (tmp_path / "04_results.md").write_text(
            r"\includegraphics{output/figures/concept_map.png}"
        )

        # Create glossary with markers
        (tmp_path / "98_symbols_glossary.md").write_text(
            "<!-- BEGIN: AUTO-API-GLOSSARY -->\nglossary\n<!-- END: AUTO-API-GLOSSARY -->"
        )

        # Create references with bibliography
        (tmp_path / "99_references.md").write_text(r"\bibliography{references}")

        result = run_checks(tmp_path)
        assert result.is_clean()

    def test_missing_figure_detected(self, tmp_path: Path):
        """Missing figures are reported."""
        (tmp_path / "04_results.md").write_text(
            r"\includegraphics{output/figures/nonexistent.png}"
        )
        (tmp_path / "98_symbols_glossary.md").write_text(
            "<!-- BEGIN: AUTO-API-GLOSSARY -->\n<!-- END: AUTO-API-GLOSSARY -->"
        )
        (tmp_path / "99_references.md").write_text(r"\bibliography{references}")

        result = run_checks(tmp_path)
        assert not result.is_clean()
        assert len(result.missing_figures) == 1

    def test_missing_glossary_markers_detected(self, tmp_path: Path):
        """Missing glossary markers are detected."""
        (tmp_path / "98_symbols_glossary.md").write_text("No markers here")
        (tmp_path / "99_references.md").write_text(r"\bibliography{references}")

        result = run_checks(tmp_path)
        assert result.missing_glossary_markers

    def test_missing_references_detected(self, tmp_path: Path):
        """Missing references block is detected."""
        (tmp_path / "98_symbols_glossary.md").write_text(
            "<!-- BEGIN: AUTO-API-GLOSSARY -->\n<!-- END: AUTO-API-GLOSSARY -->"
        )
        (tmp_path / "99_references.md").write_text("No bibliography here")

        result = run_checks(tmp_path)
        assert result.missing_references_block

    def test_no_glossary_file(self, tmp_path: Path):
        """Missing glossary file is treated as missing markers."""
        (tmp_path / "99_references.md").write_text(r"\bibliography{references}")
        result = run_checks(tmp_path)
        assert result.missing_glossary_markers

    def test_no_references_file(self, tmp_path: Path):
        """Missing references file is treated as missing block."""
        (tmp_path / "98_symbols_glossary.md").write_text(
            "<!-- BEGIN: AUTO-API-GLOSSARY -->\n<!-- END: AUTO-API-GLOSSARY -->"
        )
        result = run_checks(tmp_path)
        assert result.missing_references_block
