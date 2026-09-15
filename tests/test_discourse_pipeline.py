"""Behavioral tests for src/pipeline/discourse_pipeline.py.

Exercises :class:`DiscourseAnalysisScript` end-to-end on a small real slice
of ``data/corpus/abstracts.json`` — no mocks. Verifies the analysis result
contract, the written data artifact, the generated figures (real PNG files),
the markdown report, and the empty-input error path.
"""

import json
from pathlib import Path

import pytest

from data.literature_mining import LiteratureCorpus, Publication
from pipeline.discourse_pipeline import DiscourseAnalysisScript

CORPUS_SLICE = 10
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def assert_valid_png(path) -> None:
    """Assert ``path`` is a non-empty file with real PNG magic bytes."""
    path = Path(path)
    assert path.is_file(), f"figure was not written: {path}"
    assert path.stat().st_size > 0, f"figure is empty: {path}"
    assert path.read_bytes()[:8] == PNG_MAGIC, f"not a PNG file: {path}"


def build_corpus_file(directory: Path, texts, name: str = "literature_corpus.json") -> Path:
    """Write a corpus JSON for ``texts`` into ``directory`` and return its path."""
    publications = [
        Publication(title=f"Study {i}", authors=["Researcher"], abstract=text)
        for i, text in enumerate(texts)
    ]
    path = directory / name
    LiteratureCorpus(publications).save_to_file(path)
    return path


@pytest.fixture(scope="module")
def corpus_file(tmp_path_factory) -> Path:
    """A corpus JSON built from a real slice of the project abstracts."""
    texts = json.loads((PROJECT_ROOT / "data" / "corpus" / "abstracts.json").read_text())
    assert len(texts) >= CORPUS_SLICE, "real corpus data must be present"
    return build_corpus_file(tmp_path_factory.mktemp("corpus"), texts[:CORPUS_SLICE])


@pytest.fixture(scope="module")
def analysis_results(corpus_file, tmp_path_factory):
    """Run the discourse analysis once for the module."""
    script = DiscourseAnalysisScript(output_dir=tmp_path_factory.mktemp("out_full"))
    return script.analyze_discourse(
        corpus_file=corpus_file, focus_areas=["patterns", "rhetoric"]
    )


# ── End-to-end analysis ───────────────────────────────────────────────


class TestAnalyzeDiscourse:
    def test_results_contract(self, analysis_results):
        """The analysis reports every artifact it produced."""
        assert "error" not in analysis_results
        assert analysis_results["texts_analyzed"] == CORPUS_SLICE
        assert analysis_results["patterns_identified"] >= 0
        assert analysis_results["structures_found"] >= 1
        assert Path(analysis_results["report_file"]).is_file()
        assert analysis_results["visualizations"]
        assert Path(analysis_results["data_file"]).is_file()

    def test_figures_are_real_pngs(self, analysis_results):
        for path in analysis_results["visualizations"].values():
            assert_valid_png(path)

    def test_data_artifact(self, analysis_results):
        """discourse_analysis.json holds the complete discourse profile."""
        profile = json.loads(Path(analysis_results["data_file"]).read_text())
        assert profile["summary"]["total_texts"] == CORPUS_SLICE
        assert profile["summary"]["argumentative_structures_found"] >= 1
        for key in (
            "patterns",
            "argumentative_structures",
            "rhetorical_strategies",
            "narrative_frameworks",
            "persuasive_techniques",
        ):
            assert key in profile

    def test_report_content(self, analysis_results):
        """The markdown report renders patterns and argument structures."""
        report = Path(analysis_results["report_file"]).read_text()
        assert report.startswith("# Ento-Linguistic Discourse Analysis Report")
        assert f"- **Texts Analyzed**: {CORPUS_SLICE}" in report
        assert "## Discourse Patterns" in report
        # Argument-structure section rendered (regression: claim grouping once
        # crashed with TypeError: unhashable type: 'list' on real corpora).
        assert "### Common Argument Patterns" in report
        assert "- **Occurrences**:" in report


# ── Report helper edge cases ──────────────────────────────────────────


class TestReportGeneration:
    def test_report_without_structures(self, tmp_path):
        """A profile without argumentative structures gets the fallback text."""
        script = DiscourseAnalysisScript(output_dir=tmp_path / "empty_profile")
        profile = {
            "summary": {"total_texts": 1},
            "patterns": {},
            "argumentative_structures": [],
            "rhetorical_strategies": {},
            "narrative_frameworks": {},
            "persuasive_techniques": {},
        }
        path = Path(script._generate_discourse_report(profile, None))
        content = path.read_text()
        assert path.name == "discourse_analysis_report.md"
        assert "No clear argumentative structures identified." in content


# ── Error paths and edge cases ────────────────────────────────────────


class TestErrorPaths:
    def test_empty_corpus_returns_error(self, tmp_path):
        """With no texts available the pipeline reports an explicit error."""
        script = DiscourseAnalysisScript(output_dir=tmp_path / "err1")
        results = script.analyze_discourse()
        assert results == {"error": "No texts available"}

    def test_default_corpus_autodetect(self, tmp_path, corpus_file):
        """With corpus_file=None, the default corpus in data_dir is loaded."""
        script = DiscourseAnalysisScript(output_dir=tmp_path / "err2")
        (script.data_dir / "literature_corpus.json").write_bytes(corpus_file.read_bytes())
        results = script.analyze_discourse()
        assert "error" not in results
        assert results["texts_analyzed"] == CORPUS_SLICE


# ── CLI entry point ───────────────────────────────────────────────────


class TestMain:
    def _run_main(self, monkeypatch, argv):
        import pipeline.discourse_pipeline as module

        monkeypatch.setattr("sys.argv", ["discourse-analysis", *argv])
        module.main()

    def test_main_success(self, monkeypatch, corpus_file, tmp_path):
        out_dir = tmp_path / "cli_out"
        self._run_main(
            monkeypatch,
            [
                "--corpus-file",
                str(corpus_file),
                "--output-dir",
                str(out_dir),
                "--focus-areas",
                "patterns",
            ],
        )
        assert (out_dir / "reports" / "discourse_analysis_report.md").is_file()

    def test_main_error_path(self, monkeypatch, tmp_path):
        """An empty corpus still completes main() through the error branch."""
        empty_corpus = build_corpus_file(
            tmp_path, [], name="empty_corpus.json"
        )
        out_dir = tmp_path / "cli_err"
        self._run_main(
            monkeypatch,
            ["--corpus-file", str(empty_corpus), "--output-dir", str(out_dir)],
        )
        assert not (out_dir / "reports" / "discourse_analysis_report.md").exists()
