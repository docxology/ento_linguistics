"""Tests for pipeline.literature_pipeline.

Covers collection (cached and mined over HTTP), text processing, the full
analysis run, report writing, and error paths. All HTTP traffic is served by
pytest-httpserver with payloads modeled on the real PubMed/arXiv API shapes;
no live network access occurs.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

import pipeline.literature_pipeline as literature_pipeline_module
from data.literature_mining import (
    ArXivMiner,
    LiteratureCorpus,
    PubMedMiner,
    Publication,
)
from pipeline.literature_pipeline import LiteratureAnalysisPipeline
from visualization.figure_manager import FigureManager

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# Shared abstract rich in repeated entomological tokens so that terminology
# extraction with min_frequency=3 yields terms.
ANT_ABSTRACT = (
    "The queen ant lays eggs in the brood chamber of the colony. "
    "Workers of the colony tend the brood and forage for food resources. "
    "Colony labor is divided among workers, and the queen controls "
    "reproduction. Foraging workers allocate resources for the colony brood."
)

PUBMED_IDS = ["111", "222", "333"]

PUBMED_SEARCH_RESPONSE = {"esearchresult": {"idlist": PUBMED_IDS}}

PUBMED_SUMMARY_RESPONSE = {
    "result": {
        pmid: {
            "title": f"Colony organization in ants, study {pmid}",
            "authors": [{"name": "Author A"}, {"name": "Author B"}],
            "pubdate": "2023 Jan 15",
            "source": "Entomology Journal",
            "uid": pmid,
        }
        for pmid in PUBMED_IDS
    }
}


def _pubmed_fetch_xml() -> str:
    """Build an eFetch XML document with abstracts for the three PMIDs."""
    articles = []
    for pmid in PUBMED_IDS:
        articles.append(
            f"""
  <PubmedArticle>
    <MedlineCitation>
      <PMID>{pmid}</PMID>
      <Article>
        <Abstract>
          <AbstractText>{ANT_ABSTRACT}</AbstractText>
        </Abstract>
      </Article>
    </MedlineCitation>
  </PubmedArticle>"""
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<PubmedArticleSet>" + "".join(articles) + "\n</PubmedArticleSet>"
    )


ARXIV_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Ant colony behavior modeling</title>
    <author><name>Author C</name></author>
    <summary>Study of ant colony behavior in social insect populations.</summary>
    <published>2024-01-15T00:00:00Z</published>
  </entry>
  <entry>
    <title>Foraging strategies of harvester ants</title>
    <author><name>Author D</name></author>
    <summary>Colony-level foraging allocation in desert ants.</summary>
    <published>2024-02-20T00:00:00Z</published>
  </entry>
</feed>"""


@pytest.fixture
def literature_httpserver(httpserver, monkeypatch):
    """Serve realistic PubMed and arXiv payloads and redirect the miners."""
    httpserver.expect_request("/esearch.fcgi").respond_with_json(
        PUBMED_SEARCH_RESPONSE
    )
    httpserver.expect_request("/esummary.fcgi").respond_with_json(
        PUBMED_SUMMARY_RESPONSE
    )
    httpserver.expect_request("/efetch.fcgi").respond_with_data(
        _pubmed_fetch_xml(), content_type="application/xml"
    )
    httpserver.expect_request("/api/query").respond_with_data(
        ARXIV_FEED_XML, content_type="application/xml"
    )
    monkeypatch.setattr(PubMedMiner, "BASE_URL", httpserver.url_for("/"))
    monkeypatch.setattr(ArXivMiner, "BASE_URL", httpserver.url_for("/api/query?"))
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    return httpserver


@pytest.fixture
def make_pipeline(tmp_path, monkeypatch):
    """Build pipeline instances whose figure registry lives in tmp_path.

    The registry redirect keeps FigureManager's real behavior but prevents
    writes into the project's ``output/figures`` directory.
    """
    registry_file = tmp_path / "figure_registry.json"

    def _make(output_dir: Path | None = None) -> LiteratureAnalysisPipeline:
        out_dir = Path(output_dir) if output_dir is not None else tmp_path / "output"
        pipeline = LiteratureAnalysisPipeline(out_dir)
        pipeline.figure_manager = FigureManager(registry_file=str(registry_file))
        return pipeline

    monkeypatch.setattr(
        literature_pipeline_module,
        "FigureManager",
        lambda: FigureManager(registry_file=str(registry_file)),
    )
    return _make


class TestCollectLiterature:
    """Tests for LiteratureAnalysisPipeline._collect_literature."""

    def test_rejects_non_positive_max_publications(self, tmp_path) -> None:
        """max_publications must be positive; both 0 and negatives raise."""
        pipeline = LiteratureAnalysisPipeline(tmp_path / "out")
        with pytest.raises(ValueError, match="max_publications must be positive"):
            pipeline._collect_literature(0, use_cached=True)
        with pytest.raises(ValueError, match="got -5"):
            pipeline._collect_literature(-5, use_cached=True)

    def test_warns_on_very_large_max_publications(self, tmp_path, caplog) -> None:
        """max_publications above 10000 logs a size warning but proceeds."""
        pipeline = LiteratureAnalysisPipeline(tmp_path / "out")
        cached = LiteratureCorpus(
            [Publication(title="Small cache", authors=[], pmid="1")]
        )
        cached.save_to_file(tmp_path / "out" / "data" / "literature_corpus.json")
        with caplog.at_level("WARNING"):
            corpus = pipeline._collect_literature(20000, use_cached=True)
        assert "very large" in caplog.text
        assert [p.title for p in corpus.publications] == ["Small cache"]

    def test_uses_cached_corpus_without_network(self, tmp_path) -> None:
        """A cached literature_corpus.json is loaded instead of mined."""
        output_dir = tmp_path / "out"
        pipeline = LiteratureAnalysisPipeline(output_dir)
        cached = LiteratureCorpus(
            [
                Publication(
                    title="Cached colony study",
                    authors=["Author A"],
                    abstract=ANT_ABSTRACT,
                    pmid="999",
                    year=2022,
                    journal="Cached Journal",
                )
            ]
        )
        corpus_file = output_dir / "data" / "literature_corpus.json"
        cached.save_to_file(corpus_file)
        before = corpus_file.read_text(encoding="utf-8")

        corpus = pipeline._collect_literature(10, use_cached=True)

        assert [p.pmid for p in corpus.publications] == ["999"]
        assert corpus.publications[0].title == "Cached colony study"
        # Cache is used as-is: file untouched, no mining artifacts added.
        assert corpus_file.read_text(encoding="utf-8") == before

    def test_mines_and_saves_corpus(
        self, tmp_path, literature_httpserver, make_pipeline
    ) -> None:
        """Without a cache, publications are mined over HTTP and saved."""
        pipeline = make_pipeline(tmp_path / "out")
        corpus = pipeline._collect_literature(10, use_cached=False)

        assert len(corpus.publications) >= 1
        pmids = [p.pmid for p in corpus.publications if p.pmid]
        assert "111" in pmids

        corpus_file = tmp_path / "out" / "data" / "literature_corpus.json"
        assert corpus_file.exists()
        data = json.loads(corpus_file.read_text(encoding="utf-8"))
        assert data["metadata"]["total_publications"] == len(corpus.publications)
        assert len(data["publications"]) == len(corpus.publications)

    def test_uses_cache_when_present(
        self, tmp_path, literature_httpserver, make_pipeline
    ) -> None:
        """use_cached=True with a valid cache file skips mining entirely."""
        output_dir = tmp_path / "out"
        pipeline = make_pipeline(output_dir)
        cached = LiteratureCorpus(
            [Publication(title="Only cached publication", authors=[], pmid="1")]
        )
        corpus_file = output_dir / "data" / "literature_corpus.json"
        cached.save_to_file(corpus_file)

        corpus = pipeline._collect_literature(10, use_cached=True)

        assert [p.title for p in corpus.publications] == ["Only cached publication"]

    def test_http_errors_yield_empty_corpus(
        self, tmp_path, httpserver, monkeypatch, make_pipeline
    ) -> None:
        """HTTP 5xx from both APIs is handled gracefully: empty corpus."""
        httpserver.expect_request("/esearch.fcgi").respond_with_json(
            {"error": "upstream"}, status=500
        )
        httpserver.expect_request("/api/query").respond_with_data(
            "service unavailable", status=503
        )
        monkeypatch.setattr(PubMedMiner, "BASE_URL", httpserver.url_for("/"))
        monkeypatch.setattr(ArXivMiner, "BASE_URL", httpserver.url_for("/api/query?"))
        monkeypatch.setattr(time, "sleep", lambda _seconds: None)

        pipeline = make_pipeline(tmp_path / "out")
        corpus = pipeline._collect_literature(10, use_cached=False)

        assert corpus.publications == []
        corpus_file = tmp_path / "out" / "data" / "literature_corpus.json"
        data = json.loads(corpus_file.read_text(encoding="utf-8"))
        assert data["publications"] == []

    def test_malformed_payloads_yield_empty_corpus(
        self, tmp_path, httpserver, monkeypatch, make_pipeline
    ) -> None:
        """Malformed JSON from PubMed and malformed XML from arXiv are caught."""
        httpserver.expect_request("/esearch.fcgi").respond_with_data(
            "{not valid json", content_type="application/json"
        )
        httpserver.expect_request("/api/query").respond_with_data(
            "<feed><entry>unclosed", content_type="application/xml"
        )
        monkeypatch.setattr(PubMedMiner, "BASE_URL", httpserver.url_for("/"))
        monkeypatch.setattr(ArXivMiner, "BASE_URL", httpserver.url_for("/api/query?"))
        monkeypatch.setattr(time, "sleep", lambda _seconds: None)

        pipeline = make_pipeline(tmp_path / "out")
        corpus = pipeline._collect_literature(10, use_cached=False)

        assert corpus.publications == []


class TestProcessTexts:
    """Tests for LiteratureAnalysisPipeline._process_texts."""

    def test_skips_empty_and_whitespace_texts(self, tmp_path) -> None:
        """Publications with no usable text are dropped from processing."""
        pipeline = LiteratureAnalysisPipeline(tmp_path / "out")
        corpus = LiteratureCorpus(
            [
                Publication(title=" ", authors=[]),  # whitespace only
                Publication(title="Colony study", authors=[], abstract=ANT_ABSTRACT),
            ]
        )
        processed = pipeline._process_texts(corpus)
        assert len(processed) == 1
        assert "colony" in processed[0]


class TestRunCompleteAnalysis:
    """End-to-end and failure-path tests for run_complete_analysis."""

    def test_end_to_end_success(
        self, tmp_path, literature_httpserver, make_pipeline
    ) -> None:
        """A full offline run completes and writes every expected artifact."""
        pipeline = make_pipeline(tmp_path / "out")
        results = pipeline.run_complete_analysis(max_publications=10)

        metadata = results["pipeline_metadata"]
        assert metadata["status"] == "completed"
        assert metadata["max_publications"] == 10
        assert metadata["duration_seconds"] >= 0
        assert set(results["stages"]) == {
            "literature_collection",
            "text_processing",
            "terminology_extraction",
            "conceptual_mapping",
            "domain_analysis",
            "discourse_analysis",
            "visualization",
            "reporting",
        }
        assert results["stages"]["literature_collection"]["publications_found"] >= 1
        assert results["stages"]["text_processing"]["texts_processed"] >= 1
        assert results["stages"]["terminology_extraction"]["terms_extracted"] >= 1

        out = tmp_path / "out"
        # Data artifacts
        for name in (
            "literature_corpus.json",
            "terminology.json",
            "terminology.csv",
            "concept_map.json",
            "discourse_analysis.json",
            "visualization_metadata.json",
        ):
            assert (out / "data" / name).exists(), name
        terminology = json.loads(
            (out / "data" / "terminology.json").read_text(encoding="utf-8")
        )
        assert terminology, "terminology.json should contain extracted terms"
        csv_lines = (out / "data" / "terminology.csv").read_text(
            encoding="utf-8"
        ).strip().splitlines()
        assert len(csv_lines) >= 2  # header plus at least one term row

        # Figures are real PNG files
        for name in ("concept_map.png", "terminology_network.png", "domain_comparison.png"):
            fig = out / "figures" / name
            assert fig.exists(), name
            assert fig.read_bytes()[:8] == PNG_MAGIC, f"{name} is not a valid PNG"

        # Reports
        report = out / "reports" / "literature_analysis_report.md"
        report_text = report.read_text(encoding="utf-8")
        assert "# Ento-Linguistic Literature Analysis Report" in report_text
        assert (
            out / "reports" / "domain_analysis_report.md"
        ).read_text(encoding="utf-8").startswith("# Ento-Linguistic Domain Analysis")
        summary = json.loads(
            (out / "reports" / "analysis_summary.json").read_text(encoding="utf-8")
        )
        assert summary["pipeline_metadata"]["status"] == "completed"
        assert "literature_collection" in summary["stages"]

        # Figure registry captured both registered figures
        assert pipeline.figure_manager.get_figure("fig:terminology_network") is not None
        assert pipeline.figure_manager.get_figure("fig:domain_comparison") is not None

    def test_second_run_uses_cached_corpus(
        self, tmp_path, literature_httpserver, make_pipeline
    ) -> None:
        """A second run with use_cached_data=True reuses the saved corpus."""
        output_dir = tmp_path / "out"
        first = make_pipeline(output_dir)
        first_results = first.run_complete_analysis(max_publications=10)
        first_pub = first_results["stages"]["literature_collection"]["publications_found"]

        second = make_pipeline(output_dir)
        second_results = second.run_complete_analysis(max_publications=500)
        assert (
            second_results["stages"]["literature_collection"]["publications_found"]
            == first_pub
        )

    def test_invalid_max_publications_raises_and_logs(
        self, tmp_path, make_pipeline, caplog
    ) -> None:
        """Non-positive max_publications propagates ValueError through the run."""
        pipeline = make_pipeline(tmp_path / "out")
        with caplog.at_level("ERROR"):
            with pytest.raises(ValueError, match="max_publications must be positive"):
                pipeline.run_complete_analysis(max_publications=0)
        assert "Pipeline failed" in caplog.text

    def test_corrupt_cached_corpus_raises(
        self, tmp_path, literature_httpserver, make_pipeline
    ) -> None:
        """A cached corpus file that cannot be parsed aborts the pipeline."""
        output_dir = tmp_path / "out"
        pipeline = make_pipeline(output_dir)
        corpus_file = output_dir / "data" / "literature_corpus.json"
        corpus_file.write_text("{definitely not json", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            pipeline.run_complete_analysis(max_publications=10)


class TestFinalReport:
    """Tests for _generate_final_report in isolation."""

    def test_writes_report_and_summary(self, tmp_path) -> None:
        """The report and machine-readable summary are written to reports/."""
        pipeline = LiteratureAnalysisPipeline(tmp_path / "out")
        results = {
            "pipeline_metadata": {
                "duration_seconds": 1.5,
                "output_directory": str(tmp_path / "out"),
            },
            "stages": {
                "literature_collection": {"publications_found": 7},
                "text_processing": {"texts_processed": 7, "total_tokens": 1400},
                "terminology_extraction": {"terms_extracted": 12},
                "conceptual_mapping": {
                    "concepts_mapped": 6,
                    "relationships_found": 2,
                },
                "domain_analysis": {"domains_analyzed": 4},
                "discourse_analysis": {
                    "patterns_identified": 2,
                    "structures_found": 1,
                },
            },
        }
        report_path = pipeline._generate_final_report(results)

        assert report_path == str(tmp_path / "out" / "reports" / "literature_analysis_report.md")
        report_text = Path(report_path).read_text(encoding="utf-8")
        assert "Publications Analyzed:** 7" in report_text
        assert "Terms Identified:** 12" in report_text
        assert "Concepts Mapped:** 6" in report_text
        assert "Patterns Identified:** 2" in report_text

        summary = json.loads(
            (tmp_path / "out" / "reports" / "analysis_summary.json").read_text(
                encoding="utf-8"
            )
        )
        assert summary == results


class TestFigureRegistrationFailure:
    """The pipeline tolerates figure-registry write failures with a warning."""

    def test_run_completes_when_registry_unwritable(
        self, tmp_path, literature_httpserver, make_pipeline, caplog
    ) -> None:
        """An unwritable figure registry is skipped; the run still completes."""
        import stat

        read_only = tmp_path / "read_only_registry"
        read_only.mkdir()
        read_only.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            pipeline = make_pipeline(tmp_path / "out")
            pipeline.figure_manager = FigureManager(
                registry_file=str(read_only / "figure_registry.json")
            )
            with caplog.at_level("WARNING"):
                results = pipeline.run_complete_analysis(max_publications=10)
        finally:
            read_only.chmod(stat.S_IRWXU)

        assert results["pipeline_metadata"]["status"] == "completed"
        assert "Failed to register" in caplog.text
        assert not (read_only / "figure_registry.json").exists()


class TestMainEntryPoint:
    """Tests for the module's command-line entry point."""

    def test_main_runs_full_pipeline(
        self, tmp_path, literature_httpserver, monkeypatch
    ) -> None:
        """main() honors CLI flags and produces the full artifact tree."""
        output_dir = tmp_path / "cli_out"
        registry_file = tmp_path / "cli_registry.json"
        monkeypatch.setattr(
            literature_pipeline_module,
            "FigureManager",
            lambda: FigureManager(registry_file=str(registry_file)),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "_literature_analysis_pipeline.py",
                "--max-publications",
                "10",
                "--output-dir",
                str(output_dir),
                "--no-cache",
                "--verbose",
            ],
        )

        literature_pipeline_module.main()

        assert (output_dir / "reports" / "literature_analysis_report.md").exists()
        assert (output_dir / "reports" / "analysis_summary.json").exists()
        summary = json.loads(
            (output_dir / "reports" / "analysis_summary.json").read_text(
                encoding="utf-8"
            )
        )
        assert summary["pipeline_metadata"]["status"] == "completed"
        assert summary["pipeline_metadata"]["max_publications"] == 10
        assert summary["stages"]["literature_collection"]["publications_found"] >= 1
        # --no-cache forced fresh mining: corpus was written by this run.
        assert (output_dir / "data" / "literature_corpus.json").exists()
