"""Behavioral tests for manuscript figure generation.

Exercises the real analysis pipeline on a small subset of the real corpus
(``data/corpus/abstracts.json``) — no mocks — and verifies that every figure
generator produces a real file, propagates save failures, and never registers
a figure that was not saved.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from visualization import manuscript_figures as mf

REPO_ROOT = Path(__file__).resolve().parents[1]

# Small real slice: enough abstracts to populate the six domains without
# paying the full-corpus pipeline cost on every test.
CORPUS_SLICE = 6


@pytest.fixture(scope="module")
def real_corpus() -> list:
    """Load the real corpus from data/corpus/abstracts.json."""
    corpus_file = REPO_ROOT / "data" / "corpus" / "abstracts.json"
    assert corpus_file.exists(), "real corpus data must be present"
    texts = mf.load_real_corpus()
    assert isinstance(texts, list) and len(texts) > 0
    assert all(isinstance(t, str) and t.strip() for t in texts)
    return texts


@pytest.fixture(scope="module")
def results(real_corpus):
    """Run the real analysis pipeline once for the module."""
    return mf.run_analysis_pipeline(real_corpus[:CORPUS_SLICE])


@pytest.fixture
def figure_dir(tmp_path):
    d = tmp_path / "figures"
    d.mkdir()
    return d


# ── Module import and corpus loading ─────────────────────────────────


def test_module_loaded_real_corpus_at_import(real_corpus):
    """REAL_ABSTRACTS is populated from the real corpus at import time."""
    assert len(mf.REAL_ABSTRACTS) == len(real_corpus)


# ── Directory setup ──────────────────────────────────────────────────


def test_setup_directories_creates_and_wipes(tmp_path):
    """_setup_directories creates output dirs and wipes stale artefacts."""
    project_root = tmp_path / "proj"
    output_dir, data_dir, figure_dir = mf._setup_directories(str(project_root))

    figure_dir = Path(figure_dir)
    assert Path(output_dir).is_dir()
    assert Path(data_dir).is_dir()
    assert figure_dir.is_dir()
    assert not (figure_dir / "stale.png").exists()


# ── Analysis pipeline ────────────────────────────────────────────────


def test_run_analysis_pipeline_real_data(results):
    """The pipeline produces real terms, concepts, and domain statistics."""
    assert results["terms"], "real corpus must extract terms"
    assert results["corpus_stats"]["total_tokens"] > 0
    assert results["concept_map"].concepts
    assert isinstance(results["relationships"], dict)
    assert results["domain_data"], "domain data must be populated"

    for domain, data in results["domain_data"].items():
        assert data["term_count"] >= 0
        assert "semantic_entropy" in data
        assert "bridging_terms" in data


# ── Figure generators (happy path) ───────────────────────────────────


class TestFigureGenerators:
    """Each generator writes a real file and returns its path."""

    def test_generate_concept_map(self, results, figure_dir):
        path = mf.generate_concept_map(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_terminology_network(self, results, figure_dir):
        path = mf.generate_terminology_network(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_domain_comparison(self, results, figure_dir):
        path = mf.generate_domain_comparison(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_domain_overlap_heatmap(self, results, figure_dir):
        path = mf.generate_domain_overlap_heatmap(results, str(figure_dir))
        assert path, "expected a heatmap for a populated term set"
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_anthropomorphic_analysis(self, results, figure_dir):
        path = mf.generate_anthropomorphic_analysis(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_concept_hierarchy(self, results, figure_dir):
        path = mf.generate_concept_hierarchy(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_unit_of_individuality_patterns(self, results, figure_dir):
        path = mf.generate_unit_of_individuality_patterns(results, str(figure_dir))
        assert path, "real corpus yields unit_of_individuality terms"
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_power_labor_term_frequencies(self, results, figure_dir):
        path = mf.generate_power_labor_term_frequencies(results, str(figure_dir))
        assert path, "real corpus yields power_and_labor terms"
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_power_labor_ambiguities(self, results, figure_dir):
        path = mf.generate_power_labor_ambiguities(results, str(figure_dir))
        assert path, "pipeline computes semantic entropy for real terms"
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_domain_overview_grid(self, results, figure_dir):
        path = mf.generate_domain_overview_grid(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")

    def test_generate_domain_patterns_grid(self, results, figure_dir):
        path = mf.generate_domain_patterns_grid(results, str(figure_dir))
        assert Path(path).is_file() and Path(path).stat().st_size > 0
        plt.close("all")


# ── Failure propagation ──────────────────────────────────────────────


class TestFailurePropagation:
    """Failed saves must never be reported as success."""

    def test_concept_map_empty_data_returns_empty_string(self, figure_dir):
        """An empty concept map cannot be saved; generator must say so."""
        from analysis.conceptual_mapping import ConceptMap

        empty = ConceptMap()
        path = mf.generate_concept_map({"concept_map": empty}, str(figure_dir))
        assert path == ""
        assert not (Path(figure_dir) / "concept_map.png").exists()

    def test_unit_patterns_no_terms_returns_empty_string(self, figure_dir):
        """No terms in the domain -> no file, empty path."""
        path = mf.generate_unit_of_individuality_patterns(
            {"terms": {}, "domain_analyses": {}}, str(figure_dir)
        )
        assert path == ""
        assert not (Path(figure_dir) / "unit_of_individuality_patterns.png").exists()

    def test_power_labor_frequencies_no_terms_returns_empty_string(self, figure_dir):
        path = mf.generate_power_labor_term_frequencies(
            {"terms": {}}, str(figure_dir)
        )
        assert path == ""

    def test_power_labor_ambiguities_no_entropy_returns_empty_string(self, figure_dir):
        """Terms exist but all entropy is zero -> no figure."""
        from analysis.term_extraction import Term

        term = Term(text="worker", lemma="worker", frequency=5,
                    domains=["power_and_labor"])
        term.semantic_entropy = 0.0
        path = mf.generate_power_labor_ambiguities(
            {"terms": {"worker": term}}, str(figure_dir)
        )
        assert path == ""

    def test_unwritable_target_propagates_error(self, results, tmp_path):
        """A save error must propagate, never be swallowed into a success path."""
        blocker = tmp_path / "not_a_dir"
        blocker.write_text("i am a file")
        with pytest.raises(OSError):
            mf.generate_anthropomorphic_analysis(results, str(blocker))
        plt.close("all")


# ── Data export ──────────────────────────────────────────────────────


def test_save_analysis_data_writes_real_files(results, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    saved = mf.save_analysis_data(results, str(data_dir))

    assert len(saved) == 4
    for path in saved:
        assert Path(path).is_file() and Path(path).stat().st_size > 0

    domain_stats = json.loads((data_dir / "domain_statistics.json").read_text())
    assert domain_stats, "domain statistics must be populated"
    first = next(iter(domain_stats.values()))
    assert {"term_count", "semantic_entropy",
            "anthropomorphic_proportion"} <= set(first)

    terms_summary = json.loads((data_dir / "extracted_terms.json").read_text())
    assert terms_summary
    first_term = next(iter(terms_summary.values()))
    assert {"domains", "frequency", "confidence"} <= set(first_term)


# ── Figure registry ──────────────────────────────────────────────────


def test_register_figures_only_registers_saved_files(
    results, figure_dir
):
    """Registry must contain only figures that actually exist on disk."""
    path_a = mf.generate_concept_map(results, str(figure_dir))
    assert path_a

    mf._register_figures_with_manager(
        [path_a, str(figure_dir / "never_generated.png")], str(figure_dir)
    )

    registry_file = figure_dir / "figure_registry.json"
    assert registry_file.exists()
    registry = json.loads(registry_file.read_text())
    assert "fig:concept_map" in registry
    for entry in registry.values():
        assert (figure_dir / entry["filename"]).is_file()


# ── End-to-end main() ────────────────────────────────────────────────


def test_main_end_to_end(real_corpus, tmp_path, monkeypatch):
    """main() produces figures, data files, and a populated registry."""
    monkeypatch.setattr(mf, "REAL_ABSTRACTS", real_corpus[:CORPUS_SLICE])

    mf.main(project_root=str(tmp_path))

    figure_dir = tmp_path / "output" / "figures"
    data_dir = tmp_path / "output" / "data"
    assert figure_dir.is_dir() and data_dir.is_dir()

    generated = [p for p in figure_dir.iterdir() if p.suffix == ".png"]
    assert len(generated) >= 11, "all eleven figure generators ran"

    registry_file = figure_dir / "figure_registry.json"
    assert registry_file.exists()
    registry = json.loads(registry_file.read_text())
    assert registry, "saved figures must be registered"
    for entry in registry.values():
        assert (figure_dir / entry["filename"]).is_file()

    assert (data_dir / "corpus_statistics.json").is_file()
    assert (data_dir / "domain_statistics.json").is_file()
    assert (data_dir / "extracted_terms.json").is_file()
    assert (data_dir / "concept_map_summary.json").is_file()
