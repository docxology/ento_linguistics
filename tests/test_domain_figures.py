"""Behavioral tests for pipeline.domain_figures and visualization._style.

Exercises every figure-generating function of ``DomainFigureGenerator`` on
real data: a subset of ``data/corpus/abstracts.json`` plus a small
extracted-terms structure derived from ``output/data/extracted_terms.json``.
All outputs are written under ``tmp_path``; matplotlib uses the Agg backend.

Note on the ``keep_figures_open`` fixture: ``plt.close`` is deferred (not
replaced with a fake) so that figure contents (titles, labels, artist
colors) can be asserted after the real functions render and save real
figures. Every plot call still executes the full, unmodified rendering path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.colors
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from analysis.domain_analysis import DomainAnalysis
from analysis.term_extraction import Term
from pipeline.domain_figures import DomainFigureGenerator
from visualization._style import (
    FALLBACK_COLOR,
    MIN_FONT,
    primary_domain,
    publication_rc,
    publication_style,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ABSTRACTS_FILE = PROJECT_ROOT / "data" / "corpus" / "abstracts.json"
EXTRACTED_TERMS_FILE = PROJECT_ROOT / "output" / "data" / "extracted_terms.json"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# A short real-corpus-flavoured passage repeating domain seed vocabulary so
# that TerminologyExtractor(min_frequency=2) yields terms in every domain.
SEED_PASSAGE = (
    "Workers forage for resources within the colony. Foraging behavior "
    "involves task specialization and role differentiation. The queen "
    "controls reproduction and mating. Kin recognition and relatedness "
    "shape altruism. Caste hierarchy lets dominant individuals control "
    "labor. Resource allocation trades off cost and benefit. Each "
    "individual organism joins the collective unit."
)


def assert_valid_png(path: Path, min_bytes: int = 1000) -> None:
    """Assert a file exists, is non-empty, and carries a valid PNG header."""
    assert path.exists(), f"missing figure: {path}"
    data = path.read_bytes()
    assert len(data) >= min_bytes, f"figure suspiciously small: {path}"
    assert data[:8] == PNG_MAGIC, f"not a PNG: {path}"


@pytest.fixture
def generator(tmp_path: Path) -> DomainFigureGenerator:
    """A generator writing every artifact (incl. the figure registry) to tmp."""
    gen = DomainFigureGenerator(tmp_path / "output")
    gen.figure_manager.registry_file = tmp_path / "figure_registry.json"
    return gen


@pytest.fixture
def real_terms() -> dict:
    """Real extracted-term records keyed by term text (read-only source)."""
    with open(EXTRACTED_TERMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def terms_for_domain(real_terms: dict, domain: str, limit: int) -> dict:
    """Build real Term objects (from the extracted-terms export) for a domain."""
    picked = {}
    for text, rec in real_terms.items():
        if domain in rec.get("domains", []):
            picked[text] = Term(
                text=text,
                lemma=rec.get("lemma", text),
                domains=list(rec.get("domains", [])),
                frequency=rec.get("frequency", 1),
                confidence=rec.get("confidence", 0.5),
            )
            if len(picked) >= limit:
                break
    return picked


def keep_figures_open():
    """Defer matplotlib figure cleanup so rendered axes can be inspected.

    Only cleanup is deferred; the plotting functions run their full real
    rendering and savefig path. Figures are closed again on exit.

    Used as ``with keep_figures_open():`` around calls whose generated
    figure contents (titles, labels, artist colours) are asserted.
    """
    from contextlib import contextmanager

    opened = []
    real_close = plt.close

    def _defer_close(fig=None, *args, **kwargs):
        opened.append(fig)

    @contextmanager
    def _ctx():
        plt.close = _defer_close
        try:
            yield
        finally:
            plt.close = real_close
            for fig in opened:
                if fig is not None:
                    real_close(fig)
            real_close("all")

    return _ctx()


@pytest.fixture
def small_corpus_file(tmp_path: Path) -> Path:
    """A small LiteratureCorpus-format JSON built from real abstracts."""
    with open(ABSTRACTS_FILE, "r", encoding="utf-8") as f:
        abstracts = [a for a in json.load(f) if isinstance(a, str)]
    publications = [
        {
            "title": "Foraging behavior and division of labor in ant colonies",
            "authors": ["Smith J"],
            "abstract": abstracts[i][:1200],
            "doi": None,
            "pmid": str(100000000 + i),
            "year": 2020,
            "journal": "Insectes Sociaux",
            "keywords": ["ants"],
            "full_text": None,
        }
        for i in range(3)
    ]
    publications.append(
        {
            "title": "Domain vocabulary in the myrmecological literature",
            "authors": ["Doe A"],
            "abstract": " ".join([SEED_PASSAGE] * 3),
            "doi": None,
            "pmid": "999999999",
            "year": 2021,
            "journal": "Insectes Sociaux",
            "keywords": [],
            "full_text": None,
        }
    )
    corpus_file = tmp_path / "small_corpus.json"
    with open(corpus_file, "w", encoding="utf-8") as f:
        json.dump({"publications": publications, "metadata": {}}, f)
    return corpus_file


# ───────────────────────── DomainFigureGenerator basics ────────────────────


class TestGeneratorBasics:
    def test_init_creates_output_directories(self, tmp_path: Path) -> None:
        out = tmp_path / "output"
        DomainFigureGenerator(out)
        assert (out / "figures").is_dir()
        assert (out / "data").is_dir()

    def test_invalid_domain_returns_error(self, generator: DomainFigureGenerator) -> None:
        result = generator.generate_domain_figures("not_a_domain")
        assert result == {"error": "Invalid domain name: not_a_domain"}
        assert list(generator.figures_dir.glob("*.png")) == []

    def test_missing_corpus_yields_no_terms_error(
        self, generator: DomainFigureGenerator
    ) -> None:
        # No corpus_file and no default corpus in tmp data_dir -> empty corpus.
        result = generator.generate_domain_figures("behavior_and_identity")
        assert result == {"error": "No terms found for domain behavior_and_identity"}

    def test_load_corpus_uses_default_file(
        self, generator: DomainFigureGenerator, tmp_path: Path
    ) -> None:
        from data.literature_mining import LiteratureCorpus

        default = generator.data_dir / "literature_corpus.json"
        corpus = LiteratureCorpus()
        corpus.add_publication(
            {
                "title": "T",
                "authors": ["A"],
                "abstract": "body",
                "doi": None,
                "pmid": "1",
                "year": 2020,
                "journal": "J",
                "keywords": [],
                "full_text": None,
            }
            and __import__("data.literature_mining", fromlist=["Publication"]).Publication(
                title="T", authors=["A"], abstract="body"
            )
        )
        corpus.save_to_file(default)
        loaded = generator._load_corpus(None)
        assert len(loaded.publications) == 1
        assert loaded.publications[0].title == "T"

    def test_load_corpus_empty_when_no_file_anywhere(
        self, generator: DomainFigureGenerator
    ) -> None:
        corpus = generator._load_corpus(None)
        assert corpus.publications == []


# ─────────────────────── Full pipeline through the class ───────────────────


class TestGenerateDomainFigures:
    def test_success_generates_registered_pngs(
        self,
        generator: DomainFigureGenerator,
        small_corpus_file: Path,
        tmp_path: Path,
    ) -> None:
        result = generator.generate_domain_figures(
            "behavior_and_identity", small_corpus_file
        )
        assert "error" not in result
        assert result["domain"] == "behavior_and_identity"
        assert result["terms_visualized"] >= 1
        assert result["figures_generated"] >= 2
        assert set(result["figure_files"]) >= {"term_frequency", "ambiguity_analysis"}
        for fig_path in result["figure_files"].values():
            assert fig_path.startswith(str(generator.figures_dir))
            assert_valid_png(Path(fig_path))
        # Figure registry was written into tmp and records the manuscript label.
        registry = json.loads((tmp_path / "figure_registry.json").read_text())
        assert "fig:behavior_identity_frequencies" in registry
        assert (
            registry["fig:behavior_identity_frequencies"]["filename"]
            == "behavior_and_identity_term_frequencies.png"
        )

    def test_generate_all_domains_summary(
        self, generator: DomainFigureGenerator, small_corpus_file: Path
    ) -> None:
        summary = generator.generate_all_domain_figures(small_corpus_file)
        assert summary["domains_processed"] >= 1
        assert summary["total_figures_generated"] >= 1
        successful = [
            r for r in summary["individual_domains"].values() if "error" not in r
        ]
        assert successful, "seed passage should yield terms in at least one domain"
        for results in successful:
            assert results["figures_generated"] >= 1
        # Comparative step runs; without per-domain analysis JSON files it
        # correctly produces no comparison figure.
        assert summary["comparative_figures"] == {}

    def test_generate_all_domains_survives_unreadable_corpus(
        self, generator: DomainFigureGenerator, tmp_path: Path
    ) -> None:
        bad = tmp_path / "bad_corpus.json"
        bad.write_text("{not json")
        summary = generator.generate_all_domain_figures(bad)
        assert summary["domains_processed"] == 0
        assert summary["total_figures_generated"] == 0
        for domain, results in summary["individual_domains"].items():
            assert "error" in results, f"{domain} should report the failure"


# ────────────────────────────── Figure functions ───────────────────────────


class TestTermFrequencyPlot:
    def test_creates_png_with_labels(
        self, generator: DomainFigureGenerator, real_terms: dict, tmp_path: Path
    ) -> None:
        domain_terms = terms_for_domain(real_terms, "unit_of_individuality", 8)
        assert len(domain_terms) >= 2
        with keep_figures_open():
            path = generator._generate_term_frequency_plot(
                "unit_of_individuality", domain_terms
            )
            assert path is not None
            assert_valid_png(Path(path))
            fig = plt.gcf()
            ax = fig.axes[0]
            assert ax.get_title() == "Term Frequency Distribution - Unit Of Individuality"
            assert ax.get_ylabel() == "Frequency in Corpus"
            labels = [t.get_text() for t in ax.get_xticklabels()]
            assert sorted(labels) == sorted(domain_terms)

    def test_empty_terms_returns_none(self, generator: DomainFigureGenerator) -> None:
        assert generator._generate_term_frequency_plot("economics", {}) is None
        assert list(generator.figures_dir.glob("*.png")) == []


class TestAmbiguityPlot:
    def test_creates_png(self, generator: DomainFigureGenerator, real_terms: dict) -> None:
        ambiguities = [
            {
                "term": term,
                "contexts": [f"Context {i} for {term}", f"Another use of {term}"],
            }
            for i, term in enumerate(
                terms_for_domain(real_terms, "sex_and_reproduction", 3)
            )
        ]
        path = generator._generate_ambiguity_plot("sex_and_reproduction", ambiguities)
        assert path is not None
        assert_valid_png(Path(path))
        assert Path(path).name == "sex_and_reproduction_ambiguities.png"

    def test_empty_ambiguities_returns_none(
        self, generator: DomainFigureGenerator
    ) -> None:
        assert generator._generate_ambiguity_plot("economics", []) is None


class TestPatternPlot:
    def test_single_pattern_uses_bar_chart(
        self, generator: DomainFigureGenerator
    ) -> None:
        with keep_figures_open():
            path = generator._generate_pattern_plot("economics", {"compound": 7})
            assert path is not None
            assert_valid_png(Path(path))
            ax = plt.gcf().axes[0]
            assert ax.get_title() == "Term Pattern Counts - Economics"
            assert ax.get_ylabel() == "Count"
            assert [t.get_text() for t in ax.get_xticklabels()] == ["Compound"]

    def test_multiple_patterns_uses_pie_chart(
        self, generator: DomainFigureGenerator
    ) -> None:
        patterns = {"compound": 5, "simple": 3, "hybrid": 2}
        path = generator._generate_pattern_plot("economics", patterns)
        assert path is not None
        assert_valid_png(Path(path))
        assert Path(path).name == "economics_patterns.png"

    def test_empty_patterns_returns_none(self, generator: DomainFigureGenerator) -> None:
        assert generator._generate_pattern_plot("economics", {}) is None


class TestDomainNetwork:
    def test_creates_png_for_three_or_more_terms(
        self, generator: DomainFigureGenerator, real_terms: dict
    ) -> None:
        domain_terms = terms_for_domain(real_terms, "kin_and_relatedness", 6)
        assert len(domain_terms) >= 3
        path = generator._generate_domain_network("kin_and_relatedness", domain_terms)
        assert path is not None
        assert_valid_png(Path(path))
        assert Path(path).name == "kin_and_relatedness_network.png"

    def test_unknown_domain_renders_fallback_color(
        self, generator: DomainFigureGenerator, real_terms: dict
    ) -> None:
        """Unknown domain name -> every node drawn in the neutral FALLBACK_COLOR."""
        domain_terms = terms_for_domain(real_terms, "kin_and_relatedness", 4)
        with keep_figures_open():
            path = generator._generate_domain_network("mystery_domain", domain_terms)
            assert path is not None
            assert_valid_png(Path(path))
            ax = plt.gcf().axes[0]
            node_collections = [
                c for c in ax.collections if hasattr(c, "get_facecolor")
            ]
            assert node_collections, "network nodes should be drawn as artists"
            facecolors = node_collections[0].get_facecolor()
            expected_rgb = matplotlib.colors.to_rgba(FALLBACK_COLOR)[:3]
            for row in facecolors:
                # Nodes render with alpha=0.7; compare RGB channels only.
                assert tuple(float(v) for v in row[:3]) == pytest.approx(
                    expected_rgb
                )
            assert ax.get_title() == "Term Relationship Network - Mystery Domain"

    def test_fewer_than_three_terms_returns_none(
        self, generator: DomainFigureGenerator, real_terms: dict
    ) -> None:
        domain_terms = terms_for_domain(real_terms, "economics", 2)
        assert generator._generate_domain_network("economics", domain_terms) is None


class TestDomainSpecificFigures:
    def test_full_analysis_generates_all_four_figures(
        self, generator: DomainFigureGenerator, real_terms: dict
    ) -> None:
        domain_terms = terms_for_domain(real_terms, "unit_of_individuality", 7)
        assert len(domain_terms) > 5
        ambiguity_term = next(iter(domain_terms))
        analysis = DomainAnalysis(
            domain_name="unit_of_individuality",
            ambiguities=[
                {"term": ambiguity_term, "contexts": ["ctx one", "ctx two"]}
            ],
            term_patterns={"compound": 4, "simple": 2},
        )
        figures = generator._generate_domain_specific_figures(
            "unit_of_individuality", domain_terms, analysis
        )
        assert set(figures) == {
            "term_frequency",
            "ambiguity_analysis",
            "term_patterns",
            "term_network",
        }
        for fig_path in figures.values():
            assert_valid_png(Path(fig_path))

    def test_sparse_analysis_skips_empty_sections(
        self, generator: DomainFigureGenerator, real_terms: dict
    ) -> None:
        domain_terms = terms_for_domain(real_terms, "economics", 2)
        analysis = DomainAnalysis(domain_name="economics")
        figures = generator._generate_domain_specific_figures(
            "economics", domain_terms, analysis
        )
        # Only the frequency plot qualifies: no ambiguities, no patterns, <=5 terms.
        assert set(figures) == {"term_frequency"}
        assert_valid_png(Path(figures["term_frequency"]))


class TestComparativeFigures:
    def test_single_successful_domain_produces_nothing(
        self, generator: DomainFigureGenerator
    ) -> None:
        results = {
            "economics": {"terms_visualized": 3, "figures_generated": 1},
            "kin_and_relatedness": {"error": "No terms found"},
        }
        assert generator._generate_comparative_figures(results) == {}

    def test_comparison_figure_written_when_analysis_files_present(
        self, generator: DomainFigureGenerator, real_terms: dict
    ) -> None:
        # Small per-domain analysis files derived from the real extracted terms.
        for domain in ("economics", "kin_and_relatedness"):
            extracted = {
                term: {"frequency": term_obj.frequency}
                for term, term_obj in terms_for_domain(
                    real_terms, domain, 5
                ).items()
            }
            with open(
                generator.data_dir / f"{domain}_analysis.json", "w", encoding="utf-8"
            ) as f:
                json.dump({"extracted_terms": extracted}, f)
        results = {
            "economics": {"terms_visualized": 5},
            "kin_and_relatedness": {"terms_visualized": 5},
        }
        figures = generator._generate_comparative_figures(results)
        assert "domain_comparison" in figures
        assert figures["domain_comparison"].endswith("domain_comparison.png")
        assert_valid_png(Path(figures["domain_comparison"]))
        registered = generator.figure_manager.get_figure("fig:domain_comparison")
        assert registered is not None
        assert registered.filename == "domain_comparison.png"

    def test_missing_analysis_files_produces_nothing(
        self, generator: DomainFigureGenerator
    ) -> None:
        results = {
            "economics": {"terms_visualized": 5},
            "kin_and_relatedness": {"terms_visualized": 5},
        }
        assert generator._generate_comparative_figures(results) == {}


# ────────────────────────────── CLI entry point ────────────────────────────
# main() is exercised in-process; its only external write (the figure
# registry) is redirected into tmp_path by patching the module-level
# FigureManager constructor default, keeping every write under tmp_path.


class TestMainEntryPoint:
    def test_main_single_domain(
        self, monkeypatch, tmp_path: Path, small_corpus_file: Path
    ) -> None:
        from pipeline import domain_figures as mod
        from visualization.figure_manager import FigureManager

        outdir = tmp_path / "cli_output"
        orig_init = FigureManager.__init__

        def init_with_tmp_registry(self, registry_file=None):
            orig_init(self, str(tmp_path / "cli_registry.json"))

        monkeypatch.setattr(mod.FigureManager, "__init__", init_with_tmp_registry)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "domain_figures",
                "behavior_and_identity",
                "--corpus-file",
                str(small_corpus_file),
                "--output-dir",
                str(outdir),
            ],
        )
        mod.main()
        assert (outdir / "figures" / "behavior_and_identity_term_frequencies.png").exists()

    def test_main_reports_failure_when_no_terms(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        from pipeline import domain_figures as mod
        from visualization.figure_manager import FigureManager

        outdir = tmp_path / "cli_empty"
        orig_init = FigureManager.__init__

        def init_with_tmp_registry(self, registry_file=None):
            orig_init(self, str(tmp_path / "cli_registry2.json"))

        monkeypatch.setattr(mod.FigureManager, "__init__", init_with_tmp_registry)
        monkeypatch.setattr(
            sys,
            "argv",
            ["domain_figures", "behavior_and_identity", "--output-dir", str(outdir)],
        )
        # No corpus anywhere: every domain fails with "No terms found" and no
        # figures are produced, but main() must not raise.
        mod.main()
        assert list((outdir / "figures").glob("*.png")) == []


# ───────────────────────────── visualization._style ────────────────────────


class TestPrimaryDomain:
    def test_none_and_empty_return_none(self) -> None:
        assert primary_domain(None) is None
        assert primary_domain([]) is None
        assert primary_domain(set()) is None

    def test_deterministic_minimum(self) -> None:
        assert primary_domain({"economics", "kin_and_relatedness"}) == "economics"
        assert primary_domain(["behavior_and_identity", "economics"]) == (
            "behavior_and_identity"
        )
        # Insertion order must not matter.
        assert primary_domain(["economics", "behavior_and_identity"]) == (
            "behavior_and_identity"
        )


class TestPublicationRc:
    def test_applies_style_and_restores(self) -> None:
        before = dict(plt.rcParams)
        with publication_rc():
            assert plt.rcParams["font.size"] == MIN_FONT
            assert plt.rcParams["axes.titlesize"] == MIN_FONT + 2
            assert plt.rcParams["savefig.dpi"] == 300
        for key, value in before.items():
            assert plt.rcParams[key] == value, f"rcParam {key} not restored"

    def test_extra_overrides_merge_on_top(self) -> None:
        with publication_rc({"axes.labelsize": 20, "savefig.dpi": 150}):
            assert plt.rcParams["axes.labelsize"] == 20
            assert plt.rcParams["savefig.dpi"] == 150
            # Non-overridden style values still enforced.
            assert plt.rcParams["font.size"] == MIN_FONT
        assert plt.rcParams["axes.labelsize"] != 20
        assert plt.rcParams["savefig.dpi"] != 150

    def test_restored_after_exception(self) -> None:
        before_font = plt.rcParams["font.size"]
        with pytest.raises(RuntimeError, match="plot blew up"):
            with publication_rc():
                assert plt.rcParams["font.size"] == MIN_FONT
                raise RuntimeError("plot blew up")
        assert plt.rcParams["font.size"] == before_font


class TestPublicationStyle:
    def test_wraps_function_in_style(self) -> None:
        @publication_style
        def render(value: int) -> float:
            return plt.rcParams["font.size"] + value

        assert render(2) == MIN_FONT + 2
        assert plt.rcParams["font.size"] != MIN_FONT  # restored afterwards
        assert render.__name__ == "render"

    def test_restores_rcparams_when_decorated_function_raises(self) -> None:
        before = dict(plt.rcParams)

        @publication_style
        def boom() -> None:
            assert plt.rcParams["font.size"] == MIN_FONT
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            boom()
        for key, value in before.items():
            assert plt.rcParams[key] == value, f"rcParam {key} not restored"


class TestStyleConstants:
    def test_min_font_and_palette_are_coherent(self) -> None:
        from visualization._style import DOMAIN_PALETTE

        assert MIN_FONT >= 16.0
        # Fallback colour is a valid hex colour distinct from every domain colour.
        matplotlib.colors.to_rgba(FALLBACK_COLOR)
        assert FALLBACK_COLOR not in set(DOMAIN_PALETTE.values())
