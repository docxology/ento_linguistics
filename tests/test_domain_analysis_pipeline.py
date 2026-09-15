"""Behavioral tests for the domain analysis pipeline.

Runs the real analysis -> report -> figures path end-to-end against a
small corpus derived from ``data/corpus/abstracts.json``, with all
writes isolated under ``tmp_path`` (figure registry redirected) and the
matplotlib Agg backend (set in conftest).
"""

from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

import pytest

import pipeline.domain_analysis_pipeline as dap
from pipeline.domain_analysis_pipeline import DomainAnalysisScript
from visualization.figure_manager import FigureManager

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

DOMAINS = {
    "unit_of_individuality",
    "behavior_and_identity",
    "power_and_labor",
    "sex_and_reproduction",
    "kin_and_relatedness",
    "economics",
}

REPORT_HEADINGS = [
    "# Power And Labor Domain Analysis",
    "## Overview",
    "## Key Terminology",
    "## Framing Assumptions",
    "## Conceptual Structure",
    "## Ambiguities and Communication Challenges",
    "## Recommendations for Clearer Communication",
    "## Detailed Term Analysis",
    "## Data Sources",
]


@pytest.fixture(scope="module")
def real_abstracts() -> list[str]:
    """Load a real subset of the committed corpus (read-only)."""
    corpus_path = (
        Path(__file__).resolve().parents[1] / "data" / "corpus" / "abstracts.json"
    )
    with open(corpus_path, encoding="utf-8") as f:
        data = json.load(f)
    texts = [a for a in data if isinstance(a, str) and a.strip()]
    return texts[:8]


@pytest.fixture(scope="module")
def corpus_file(tmp_path_factory, real_abstracts) -> Path:
    """Write a LiteratureCorpus JSON built from the real abstract subset."""
    path = tmp_path_factory.mktemp("corpus") / "literature_corpus.json"
    publications = [
        {
            "title": f"Social insect study {i}",
            "authors": [f"Author {i}"],
            "abstract": text,
        }
        for i, text in enumerate(real_abstracts)
    ]
    path.write_text(
        json.dumps({"publications": publications}), encoding="utf-8"
    )
    return path


@pytest.fixture
def script(tmp_path, monkeypatch) -> DomainAnalysisScript:
    """DomainAnalysisScript with the figure registry pinned to tmp_path.

    The pipeline constructs ``FigureManager()`` with its default registry
    location inside the repository; a thin subclass redirects only the
    registry file into tmp_path while keeping every real behavior.
    """
    out_dir = tmp_path / "output"

    class TmpRegistryFigureManager(FigureManager):
        def __init__(self, registry_file=None):
            super().__init__(
                registry_file=str(out_dir / "figures" / "figure_registry.json")
            )

    monkeypatch.setattr(dap, "FigureManager", TmpRegistryFigureManager)
    return DomainAnalysisScript(output_dir=out_dir)


def assert_valid_png(path: Path) -> None:
    assert path.exists(), f"missing figure: {path}"
    assert path.read_bytes()[:8] == PNG_MAGIC, f"not a valid PNG: {path}"


class TestInit:
    def test_creates_output_directory_layout(self, script) -> None:
        assert script.figures_dir.is_dir()
        assert script.reports_dir.is_dir()
        assert script.data_dir.is_dir()


class TestAnalyzeDomain:
    def test_invalid_domain_returns_error(self, script) -> None:
        result = script.analyze_domain("not_a_domain")
        assert result == {"error": "Invalid domain name: not_a_domain"}

    def test_power_and_labor_end_to_end(self, script, corpus_file) -> None:
        results = script.analyze_domain(
            "power_and_labor", corpus_file=corpus_file, generate_figures=True
        )

        assert results["domain"] == "power_and_labor"
        assert results["terms_analyzed"] > 0
        assert results["key_terms"]
        assert results["ambiguities_found"] > 0
        assert results["recommendations"] > 0

        report_path = Path(results["report_file"])
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        for heading in REPORT_HEADINGS:
            assert heading in content
        assert f"**Terms Analyzed:** {results['terms_analyzed']}" in content
        assert "- **queen**" in content
        assert "#### queen" in content
        assert "**Frequency**" in content

        # Both conditional figures: terms exist and ambiguities exist.
        assert results["figures_generated"] == 2
        # figure_files lists figure names, not paths; the files live in
        # the figures directory with power_and_labor renamed to power_labor.
        assert set(results["figure_files"]) == {"term_frequencies", "ambiguities"}
        assert_valid_png(script.figures_dir / "power_labor_term_frequencies.png")
        assert_valid_png(script.figures_dir / "power_labor_ambiguities.png")

        # Figures registered with the manuscript-expected labels.
        freq_meta = script.figure_manager.get_figure("fig:power_labor_frequencies")
        assert freq_meta is not None
        assert freq_meta.filename == "power_labor_term_frequencies.png"
        assert freq_meta.section == "supplemental_results"
        amb_meta = script.figure_manager.get_figure("fig:power_labor_ambiguities")
        assert amb_meta is not None
        assert amb_meta.filename == "power_labor_ambiguities.png"

    def test_without_figures_omits_figure_keys(self, script, corpus_file) -> None:
        results = script.analyze_domain(
            "kin_and_relatedness", corpus_file=corpus_file, generate_figures=False
        )
        assert "figures_generated" not in results
        assert "figure_files" not in results
        assert results["terms_analyzed"] > 0
        assert Path(results["report_file"]).exists()
        assert list(script.figures_dir.glob("*.png")) == []


class TestLoadCorpus:
    def test_explicit_corpus_file(self, script, corpus_file) -> None:
        corpus = script._load_corpus(corpus_file)
        assert len(corpus.publications) == 8
        texts = corpus.get_text_corpus()
        assert len(texts) == 8
        assert all(isinstance(t, str) and t.strip() for t in texts)

    def test_default_corpus_location(self, tmp_path, monkeypatch) -> None:
        out_dir = tmp_path / "out_default"

        class TmpRegistryFigureManager(FigureManager):
            def __init__(self, registry_file=None):
                super().__init__(
                    registry_file=str(out_dir / "figures" / "figure_registry.json")
                )

        monkeypatch.setattr(dap, "FigureManager", TmpRegistryFigureManager)
        fresh = DomainAnalysisScript(output_dir=out_dir)

        default_corpus = fresh.data_dir / "literature_corpus.json"
        default_corpus.write_text(
            json.dumps(
                {
                    "publications": [
                        {"title": "Default corpus study", "authors": ["A"], "abstract": "x"}
                    ]
                }
            ),
            encoding="utf-8",
        )
        corpus = fresh._load_corpus(None)
        assert len(corpus.publications) == 1

    def test_missing_corpus_falls_back_to_empty(self, tmp_path, monkeypatch) -> None:
        out_dir = tmp_path / "out_empty"

        class TmpRegistryFigureManager(FigureManager):
            def __init__(self, registry_file=None):
                super().__init__(
                    registry_file=str(out_dir / "figures" / "figure_registry.json")
                )

        monkeypatch.setattr(dap, "FigureManager", TmpRegistryFigureManager)
        fresh = DomainAnalysisScript(output_dir=out_dir)

        corpus = fresh._load_corpus(tmp_path / "does_not_exist.json")
        assert corpus.publications == []
        assert corpus.get_text_corpus() == []


class TestGenerateDomainFigures:
    def test_no_terms_and_no_ambiguities_yields_no_figures(
        self, script, corpus_file
    ) -> None:
        from analysis.domain_analysis import DomainAnalyzer
        from analysis.term_extraction import TerminologyExtractor

        corpus = script._load_corpus(corpus_file)
        texts = corpus.get_text_corpus()
        terms = TerminologyExtractor().extract_terms(texts, min_frequency=2)
        analysis = DomainAnalyzer().analyze_all_domains(terms, texts)["economics"]
        ambiguity_free = dataclasses.replace(analysis, ambiguities=[])

        figures = script._generate_domain_figures(
            "economics", ambiguity_free, {}
        )
        assert figures == {}
        assert list(script.figures_dir.glob("*.png")) == []


class TestAnalyzeAllDomains:
    def test_end_to_end_all_six_domains(self, script, corpus_file) -> None:
        summary = script.analyze_all_domains(corpus_file=corpus_file)

        results = summary["individual_analyses"]
        assert set(results) == DOMAINS
        assert summary["summary"]["domains_analyzed"] == 6
        assert summary["summary"]["total_terms"] > 0
        assert summary["summary"]["total_ambiguities"] == sum(
            r.get("ambiguities_found", 0) for r in results.values()
        )
        assert summary["summary"]["total_recommendations"] == sum(
            r.get("recommendations", 0) for r in results.values()
        )
        for domain, result in results.items():
            assert "error" not in result, f"{domain} failed: {result}"
            assert Path(result["report_file"]).exists()

        comparative = Path(summary["comparative_report"])
        assert comparative.exists()
        assert comparative.name == "comparative_domain_analysis.md"
        content = comparative.read_text(encoding="utf-8")
        assert "# Comparative Ento-Linguistic Domain Analysis" in content
        assert (
            "| Domain | Terms Analyzed | Key Ambiguities | Recommendations |"
            in content
        )
        assert "| Unit Of Individuality | " in content
        assert "| Economics | " in content

    def test_empty_corpus_yields_termless_analyses(self, tmp_path, monkeypatch) -> None:
        out_dir = tmp_path / "out_errors"

        class TmpRegistryFigureManager(FigureManager):
            def __init__(self, registry_file=None):
                super().__init__(
                    registry_file=str(out_dir / "figures" / "figure_registry.json")
                )

        monkeypatch.setattr(dap, "FigureManager", TmpRegistryFigureManager)
        failing = DomainAnalysisScript(output_dir=out_dir)

        summary = failing.analyze_all_domains(corpus_file=tmp_path / "missing.json")

        results = summary["individual_analyses"]
        assert set(results) == DOMAINS
        # An empty corpus yields no terms: every domain comes back with an
        # empty result ("no analysis available"), not an error entry.
        for result in results.values():
            assert result == {}
        assert summary["summary"]["domains_analyzed"] == 6
        assert summary["summary"]["total_terms"] == 0
        assert summary["summary"]["total_ambiguities"] == 0
        content = Path(summary["comparative_report"]).read_text(encoding="utf-8")
        assert "# Comparative Ento-Linguistic Domain Analysis" in content
        assert "| Unit Of Individuality | 0 | 0 | 0 |" in content


class TestComparativeReport:
    def test_error_domains_omitted_from_table(self, script) -> None:
        path_str = script._generate_comparative_report(
            {
                "economics": {"error": "boom"},
                "kin_and_relatedness": {
                    "terms_analyzed": 3,
                    "ambiguities_found": 1,
                    "recommendations": 2,
                },
            }
        )
        content = Path(path_str).read_text(encoding="utf-8")
        assert "| Kin And Relatedness | 3 | 1 | 2 |" in content
        assert "| Economics |" not in content
        assert Path(path_str).name == "comparative_domain_analysis.md"


class TestMainCli:
    def test_single_domain_no_figures(
        self, monkeypatch, tmp_path, corpus_file
    ) -> None:
        out_dir = tmp_path / "cli_single"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "domain-analysis",
                "kin_and_relatedness",
                "--corpus-file",
                str(corpus_file),
                "--output-dir",
                str(out_dir),
                "--no-figures",
            ],
        )
        dap.main()
        report = out_dir / "reports" / "kin_and_relatedness_analysis_report.md"
        assert report.exists()
        assert "Kin And Relatedness Domain Analysis" in report.read_text(
            encoding="utf-8"
        )
        assert list((out_dir / "figures").glob("*.png")) == []

    def test_all_domains_cli(self, monkeypatch, tmp_path, corpus_file) -> None:
        out_dir = tmp_path / "cli_all"

        class TmpRegistryFigureManager(FigureManager):
            def __init__(self, registry_file=None):
                super().__init__(
                    registry_file=str(out_dir / "figures" / "figure_registry.json")
                )

        monkeypatch.setattr(dap, "FigureManager", TmpRegistryFigureManager)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "domain-analysis",
                "all",
                "--corpus-file",
                str(corpus_file),
                "--output-dir",
                str(out_dir),
            ],
        )
        dap.main()
        assert (out_dir / "reports" / "comparative_domain_analysis.md").exists()
        assert (out_dir / "reports" / "power_and_labor_analysis_report.md").exists()
        assert list((out_dir / "figures").glob("*.png"))

    def test_invalid_domain_cli_is_rejected(self, monkeypatch, tmp_path) -> None:
        out_dir = tmp_path / "cli_invalid"
        monkeypatch.setattr(
            sys,
            "argv",
            ["domain-analysis", "not_a_domain", "--output-dir", str(out_dir)],
        )
        # The CLI restricts domains via argparse choices and exits(2).
        with pytest.raises(SystemExit) as excinfo:
            dap.main()
        assert excinfo.value.code == 2
