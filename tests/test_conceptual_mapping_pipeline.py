"""Behavioral tests for src/pipeline/conceptual_mapping_pipeline.py.

Exercises :class:`ConceptualMappingScript` end-to-end on a small real slice
of ``data/corpus/abstracts.json`` — no mocks. Verifies the analysis result
contract, the written data artifacts, the generated figures (real PNG files),
the markdown report, and the documented error paths.
"""

import json
from pathlib import Path

import pytest

from data.literature_mining import LiteratureCorpus, Publication
from pipeline.conceptual_mapping_pipeline import ConceptualMappingScript

# Small real slice: enough abstracts to extract terms with min_frequency=3
# and to surface an anthropomorphic indicator term (e.g. "selection").
CORPUS_SLICE = 20
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def assert_valid_png(path) -> None:
    """Assert ``path`` is a non-empty file with real PNG magic bytes."""
    path = Path(path)
    assert path.is_file(), f"figure was not written: {path}"
    assert path.stat().st_size > 0, f"figure is empty: {path}"
    assert path.read_bytes()[:8] == PNG_MAGIC, f"not a PNG file: {path}"


@pytest.fixture(scope="module")
def corpus_file(tmp_path_factory) -> Path:
    """A corpus JSON built from a real slice of the project abstracts."""
    texts = json.loads((PROJECT_ROOT / "data" / "corpus" / "abstracts.json").read_text())
    assert len(texts) >= CORPUS_SLICE, "real corpus data must be present"
    publications = [
        Publication(title=f"Study {i}", authors=["Researcher"], abstract=text)
        for i, text in enumerate(texts[:CORPUS_SLICE])
    ]
    path = tmp_path_factory.mktemp("corpus") / "literature_corpus.json"
    LiteratureCorpus(publications).save_to_file(path)
    return path


@pytest.fixture(scope="module")
def full_results(corpus_file, tmp_path_factory):
    """Run the full analysis once for the module."""
    script = ConceptualMappingScript(output_dir=tmp_path_factory.mktemp("out_full"))
    return script.generate_concept_map(corpus_file=corpus_file, analysis_type="full")


@pytest.fixture(scope="module")
def terminology_results(corpus_file, tmp_path_factory):
    script = ConceptualMappingScript(output_dir=tmp_path_factory.mktemp("out_term"))
    return script.generate_concept_map(corpus_file=corpus_file, analysis_type="terminology_only")


@pytest.fixture(scope="module")
def concepts_results(corpus_file, tmp_path_factory):
    script = ConceptualMappingScript(output_dir=tmp_path_factory.mktemp("out_concepts"))
    return script.generate_concept_map(corpus_file=corpus_file, analysis_type="concepts_only")


# ── Full analysis ─────────────────────────────────────────────────────


class TestFullAnalysis:
    def test_results_contract(self, full_results):
        """Full analysis reports real term/concept/relationship counts."""
        assert "error" not in full_results
        assert full_results["terms_extracted"] > 0
        assert full_results["concepts_mapped"] > 0
        assert full_results["relationships_found"] > 0
        for key in (
            "visualizations",
            "report_file",
            "concept_map_file",
            "terminology_file",
        ):
            assert key in full_results

    def test_figures_are_real_pngs(self, full_results):
        """Every reported visualization exists on disk as a valid PNG."""
        assert set(full_results["visualizations"]) >= {
            "concept_map",
            "terminology_network",
            "concept_hierarchy",
            "anthropomorphic_analysis",
        }
        for path in full_results["visualizations"].values():
            assert_valid_png(path)
        # Visualization metadata is exported alongside the figures.
        metadata = Path(full_results["report_file"]).parents[1] / "data" / (
            "concept_mapping_visualizations.json"
        )
        assert metadata.is_file()
        assert json.loads(metadata.read_text())["visualization_settings"]

    def test_data_artifacts_written(self, full_results):
        """concept_map.json and terminology.json hold the analysis output."""
        concept_map_path = Path(full_results["concept_map_file"])
        terminology_path = Path(full_results["terminology_file"])
        assert concept_map_path.is_file()
        assert terminology_path.is_file()

        concept_map = json.loads(concept_map_path.read_text())
        assert concept_map["concepts"], "concept_map.json must not be empty"
        assert len(concept_map["concepts"]) == full_results["concepts_mapped"]
        assert len(concept_map["relationships"]) == full_results["relationships_found"]

        terminology = json.loads(terminology_path.read_text())
        assert len(terminology) == full_results["terms_extracted"]
        first = next(iter(terminology.values()))
        assert first["text"] in terminology

    def test_report_content(self, full_results):
        """The markdown report contains the analysis summary and relationships."""
        report = Path(full_results["report_file"]).read_text()
        assert report.startswith("# Ento-Linguistic Conceptual Mapping Report")
        assert f"- **Terms Extracted**: {full_results['terms_extracted']}" in report
        assert f"- **Concepts Mapped**: {full_results['concepts_mapped']}" in report
        # Relationship lines are properly formatted (regression: the report
        # once appended the literal string ".3f.3f" per relationship).
        assert "-> " in report
        assert ".3f.3f" not in report


# ── Terminology-only analysis ─────────────────────────────────────────


class TestTerminologyOnly:
    def test_results(self, terminology_results):
        """Terminology-only mode reports domain and frequency statistics."""
        assert terminology_results["analysis_type"] == "terminology_only"
        assert terminology_results["terms_analyzed"] > 0
        assert terminology_results["domain_distribution"]
        distribution = terminology_results["domain_distribution"]
        assert all(count >= 1 for count in distribution.values())
        assert terminology_results["avg_frequency"] > 0
        assert terminology_results["max_frequency"] >= terminology_results["avg_frequency"]

    def test_overview_figure(self, terminology_results):
        assert_valid_png(terminology_results["visualization_file"])


# ── Concepts-only analysis ────────────────────────────────────────────


class TestConceptsOnly:
    def test_results(self, concepts_results):
        """Concepts-only mode reports per-concept and relationship statistics."""
        assert concepts_results["analysis_type"] == "concepts_only"
        stats = concepts_results["concept_statistics"]
        assert stats
        assert concepts_results["concepts_analyzed"] == len(stats)
        sample = next(iter(stats.values()))
        assert set(sample) == {
            "terms_count",
            "domains_count",
            "parent_concepts",
            "child_concepts",
        }
        rel = concepts_results["relationship_statistics"]
        assert rel["total_relationships"] >= 0
        assert rel["avg_relationship_strength"] >= 0

    def test_concept_map_figure(self, concepts_results):
        assert_valid_png(concepts_results["visualization_file"])


# ── Error paths and edge cases ────────────────────────────────────────


class TestErrorPaths:
    def test_invalid_analysis_type(self, tmp_path):
        script = ConceptualMappingScript(output_dir=tmp_path / "err1")
        results = script.generate_concept_map(analysis_type="bogus")
        assert results == {
            "error": "Invalid analysis_type 'bogus'. Must be one of: full, "
            "terminology_only, concepts_only"
        }

    def test_missing_corpus_file(self, tmp_path):
        script = ConceptualMappingScript(output_dir=tmp_path / "err2")
        missing = tmp_path / "does_not_exist.json"
        results = script.generate_concept_map(corpus_file=missing)
        assert "error" in results
        assert "does not exist" in results["error"]

    def test_empty_corpus_terminology_only(self, tmp_path):
        """With no corpus anywhere, terminology analysis degrades to zeros."""
        script = ConceptualMappingScript(output_dir=tmp_path / "err3")
        results = script.generate_concept_map(analysis_type="terminology_only")
        assert results["terms_analyzed"] == 0
        assert results["domain_distribution"] == {}
        assert results["avg_frequency"] == 0
        assert results["max_frequency"] == 0
        # No figure is generated for an empty terminology set.
        assert results["visualization_file"].endswith("terminology_overview.png")
        assert not Path(results["visualization_file"]).exists()

    def test_empty_corpus_full_analysis(self, tmp_path):
        """A full run without any corpus text still completes and reports zeros."""
        script = ConceptualMappingScript(output_dir=tmp_path / "err5")
        results = script.generate_concept_map(analysis_type="full")
        assert results["terms_extracted"] == 0
        assert results["relationships_found"] == 0
        # The mapper still emits its predefined concept skeleton.
        assert results["concepts_mapped"] > 0
        assert Path(results["report_file"]).is_file()
        metadata = Path(results["report_file"]).parents[1] / "data" / (
            "concept_mapping_visualizations.json"
        )
        assert metadata.is_file()

    def test_default_corpus_autodetect(self, tmp_path, corpus_file):
        """With corpus_file=None, the default corpus in data_dir is loaded."""
        script = ConceptualMappingScript(output_dir=tmp_path / "err4")
        (script.data_dir / "literature_corpus.json").write_bytes(corpus_file.read_bytes())
        results = script.generate_concept_map(analysis_type="terminology_only")
        assert results["terms_analyzed"] > 0


# ── CLI entry point ───────────────────────────────────────────────────


class TestMain:
    def test_main_runs_analysis(self, monkeypatch, corpus_file, tmp_path):
        import pipeline.conceptual_mapping_pipeline as module

        out_dir = tmp_path / "cli_out"
        monkeypatch.setattr(
            "sys.argv",
            [
                "conceptual-mapping",
                "--corpus-file",
                str(corpus_file),
                "--output-dir",
                str(out_dir),
                "--analysis-type",
                "terminology_only",
            ],
        )
        module.main()
        assert_valid_png(out_dir / "figures" / "terminology_overview.png")
