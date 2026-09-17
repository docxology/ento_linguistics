"""Tests for the StatisticalVisualizer class.

Comprehensive tests for all statistical visualization methods including
significance testing, correlation matrices, distribution comparisons,
effect sizes, confidence intervals, dashboards, and hypothesis testing.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from visualization.statistical_visualization import StatisticalVisualizer


@pytest.fixture
def visualizer():
    """Create a StatisticalVisualizer instance."""
    return StatisticalVisualizer()


@pytest.fixture
def visualizer_custom_size():
    """Create a StatisticalVisualizer with custom figsize."""
    return StatisticalVisualizer(figsize=(10, 6))


@pytest.fixture
def significance_results():
    """Create sample significance test results."""
    return {
        "p_value": 0.03,
        "significance_threshold": 0.05,
        "chi_square_statistic": 12.5,
        "effect_size": 0.45,
        "significant_patterns": ["pattern_a", "pattern_b", "pattern_c"],
    }


@pytest.fixture
def correlation_data():
    """Create sample correlation data."""
    return {
        "term_frequency": {"metaphor_density": 0.75, "complexity": -0.3, "clarity": 0.6},
        "metaphor_density": {"term_frequency": 0.75, "complexity": 0.4, "clarity": -0.2},
        "complexity": {"term_frequency": -0.3, "metaphor_density": 0.4, "clarity": -0.5},
        "clarity": {"term_frequency": 0.6, "metaphor_density": -0.2, "complexity": -0.5},
    }


@pytest.fixture
def distribution_data():
    """Create sample distribution data."""
    np.random.seed(42)
    return {
        "anthropomorphic": list(np.random.normal(5.0, 1.5, 50)),
        "hierarchical": list(np.random.normal(3.0, 2.0, 50)),
        "economic": list(np.random.normal(4.0, 1.0, 50)),
    }


@pytest.fixture
def effect_size_data():
    """Create sample effect size data."""
    return {
        "colony vs organism": {"effect_size": 0.85},
        "queen vs worker": {"effect_size": 0.45},
        "forager vs nurse": {"effect_size": 0.15},
        "caste vs role": {"effect_size": -0.6},
    }


@pytest.fixture
def ci_data():
    """Create sample confidence interval data."""
    return {
        "Group A": {"estimate": 2.5, "ci_lower": 1.8, "ci_upper": 3.2},
        "Group B": {"estimate": -0.3, "ci_lower": -1.1, "ci_upper": 0.5},
        "Group C": {"estimate": 1.0, "ci_lower": 0.2, "ci_upper": 1.8},
        "Group D": {"estimate": -1.5, "ci_lower": -2.3, "ci_upper": -0.7},
    }


@pytest.fixture
def dashboard_data(correlation_data, distribution_data, ci_data):
    """Create sample dashboard data."""
    return {
        "significance_results": {
            "p_value": 0.01,
            "significance_threshold": 0.05,
        },
        "effect_sizes": {
            "comparison_1": 0.8,
            "comparison_2": 0.3,
            "comparison_3": -0.5,
        },
        "distributions": distribution_data,
        "correlation_matrix": correlation_data,
        "confidence_intervals": ci_data,
    }


@pytest.fixture
def hypothesis_results():
    """Create sample hypothesis test results."""
    return [
        {"test_name": "Test Colony Size", "p_value": 0.001, "effect_size": 0.9},
        {"test_name": "Test Worker Ratio", "p_value": 0.15, "effect_size": 0.2},
        {"test_name": "Test Foraging Rate", "p_value": 0.03, "effect_size": 0.6},
        {"test_name": "Test Nest Temp", "p_value": 0.80, "effect_size": 0.05},
    ]


class TestStatisticalVisualizerInit:
    """Tests for StatisticalVisualizer initialization."""

    def test_default_init(self, visualizer):
        assert visualizer.figsize == (12, 8)
        assert "significant" in visualizer.significance_colors
        assert "marginally_significant" in visualizer.significance_colors
        assert "not_significant" in visualizer.significance_colors
        # Colorblind-safe palette: no red/green significance coding
        assert visualizer.significance_colors["significant"] == "#D55E00"
        assert visualizer.significance_colors["marginally_significant"] == "#E69F00"
        assert visualizer.significance_colors["not_significant"] == "#0072B2"

    def test_significance_figure_uses_colorblind_status_colors(
        self, visualizer, significance_results
    ):
        fig = visualizer.visualize_statistical_significance(significance_results)
        status_texts = [
            t for t in fig.axes[0].texts
            if t.get_text() in {"SIGNIFICANT", "NOT SIGNIFICANT"}
        ]
        assert status_texts, "expected a significance status label"
        assert status_texts[0].get_color() in {"#D55E00", "#0072B2"}
        plt.close(fig)

    def test_custom_figsize(self, visualizer_custom_size):
        assert visualizer_custom_size.figsize == (10, 6)

    def test_inherits_concept_visualizer(self, visualizer):
        # Should have figsize from ConceptVisualizer parent
        assert hasattr(visualizer, "figsize")


class TestVisualizeStatisticalSignificance:
    """Tests for visualize_statistical_significance method."""

    def test_basic_significance(self, visualizer, significance_results):
        fig = visualizer.visualize_statistical_significance(significance_results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_not_significant_result(self, visualizer):
        results = {
            "p_value": 0.15,
            "significance_threshold": 0.05,
            "effect_size": 0.08,
        }
        fig = visualizer.visualize_statistical_significance(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_empty_patterns(self, visualizer):
        results = {
            "p_value": 0.03,
            "significance_threshold": 0.05,
            "effect_size": 0.3,
            "significant_patterns": [],
        }
        fig = visualizer.visualize_statistical_significance(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_chi_square(self, visualizer, significance_results):
        fig = visualizer.visualize_statistical_significance(significance_results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_large_effect_size(self, visualizer):
        results = {
            "p_value": 0.001,
            "significance_threshold": 0.05,
            "effect_size": 0.95,
            "chi_square_statistic": 25.0,
            "significant_patterns": ["strong_pattern"],
        }
        fig = visualizer.visualize_statistical_significance(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, significance_results):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "significance.png"
            fig = visualizer.visualize_statistical_significance(
                significance_results, filepath=filepath
            )
            assert filepath.exists()
            plt.close(fig)

    def test_custom_title(self, visualizer, significance_results):
        fig = visualizer.visualize_statistical_significance(
            significance_results, title="Custom Title"
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_negligible_effect_size(self, visualizer):
        results = {
            "p_value": 0.5,
            "significance_threshold": 0.05,
            "effect_size": 0.05,
        }
        fig = visualizer.visualize_statistical_significance(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_small_effect_size(self, visualizer):
        results = {
            "p_value": 0.04,
            "significance_threshold": 0.05,
            "effect_size": 0.25,
        }
        fig = visualizer.visualize_statistical_significance(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_medium_effect_size(self, visualizer):
        results = {
            "p_value": 0.02,
            "significance_threshold": 0.05,
            "effect_size": 0.45,
        }
        fig = visualizer.visualize_statistical_significance(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestCreateCorrelationMatrixPlot:
    """Tests for create_correlation_matrix_plot method."""

    def test_basic_correlation(self, visualizer, correlation_data):
        fig = visualizer.create_correlation_matrix_plot(correlation_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, correlation_data):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "correlation.png"
            fig = visualizer.create_correlation_matrix_plot(
                correlation_data, filepath=filepath
            )
            assert filepath.exists()
            plt.close(fig)

    def test_custom_title(self, visualizer, correlation_data):
        fig = visualizer.create_correlation_matrix_plot(
            correlation_data, title="Custom Correlation"
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_two_variables(self, visualizer):
        data = {
            "var_a": {"var_b": 0.9},
            "var_b": {"var_a": 0.9},
        }
        fig = visualizer.create_correlation_matrix_plot(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestVisualizeDistributionComparison:
    """Tests for visualize_distribution_comparison method."""

    def test_basic_comparison(self, visualizer, distribution_data):
        fig = visualizer.visualize_distribution_comparison(distribution_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, distribution_data):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "distributions.png"
            fig = visualizer.visualize_distribution_comparison(
                distribution_data, filepath=filepath
            )
            assert filepath.exists()
            plt.close(fig)

    def test_two_distributions(self, visualizer):
        np.random.seed(42)
        data = {
            "dist_1": list(np.random.normal(0, 1, 30)),
            "dist_2": list(np.random.normal(2, 1.5, 30)),
        }
        fig = visualizer.visualize_distribution_comparison(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_title(self, visualizer, distribution_data):
        fig = visualizer.visualize_distribution_comparison(
            distribution_data, title="My Distributions"
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestVisualizeEffectSizes:
    """Tests for visualize_effect_sizes method."""

    def test_basic_effect_sizes(self, visualizer, effect_size_data):
        fig = visualizer.visualize_effect_sizes(effect_size_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, effect_size_data):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "effect_sizes.png"
            fig = visualizer.visualize_effect_sizes(
                effect_size_data, filepath=filepath
            )
            assert filepath.exists()
            plt.close(fig)

    def test_all_negligible(self, visualizer):
        data = {
            "comp_1": {"effect_size": 0.05},
            "comp_2": {"effect_size": -0.1},
        }
        fig = visualizer.visualize_effect_sizes(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_all_large(self, visualizer):
        data = {
            "comp_1": {"effect_size": 1.2},
            "comp_2": {"effect_size": -0.9},
        }
        fig = visualizer.visualize_effect_sizes(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_mixed_signs(self, visualizer):
        data = {
            "positive": {"effect_size": 0.7},
            "negative": {"effect_size": -0.3},
            "zero": {"effect_size": 0.0},
        }
        fig = visualizer.visualize_effect_sizes(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestPlotConfidenceIntervals:
    """Tests for plot_confidence_intervals method."""

    def test_basic_ci(self, visualizer, ci_data):
        fig = visualizer.plot_confidence_intervals(ci_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, ci_data):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "ci_plot.png"
            fig = visualizer.plot_confidence_intervals(ci_data, filepath=filepath)
            assert filepath.exists()
            plt.close(fig)

    def test_all_positive_ci(self, visualizer):
        data = {
            "A": {"estimate": 5.0, "ci_lower": 4.0, "ci_upper": 6.0},
            "B": {"estimate": 3.0, "ci_lower": 2.5, "ci_upper": 3.5},
        }
        fig = visualizer.plot_confidence_intervals(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_ci_spanning_zero(self, visualizer):
        data = {
            "X": {"estimate": 0.5, "ci_lower": -0.3, "ci_upper": 1.3},
        }
        fig = visualizer.plot_confidence_intervals(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_title(self, visualizer, ci_data):
        fig = visualizer.plot_confidence_intervals(ci_data, title="My CIs")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestCreateStatisticalDashboard:
    """Tests for create_statistical_dashboard method."""

    def test_full_dashboard(self, visualizer, dashboard_data):
        fig = visualizer.create_statistical_dashboard(dashboard_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, dashboard_data):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "dashboard.png"
            fig = visualizer.create_statistical_dashboard(
                dashboard_data, filepath=filepath
            )
            assert filepath.exists()
            plt.close(fig)

    def test_partial_dashboard_significance_only(self, visualizer):
        data = {
            "significance_results": {
                "p_value": 0.02,
                "significance_threshold": 0.05,
            }
        }
        fig = visualizer.create_statistical_dashboard(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_partial_dashboard_effects_only(self, visualizer):
        data = {
            "effect_sizes": {"comp_1": 0.5, "comp_2": 0.3},
        }
        fig = visualizer.create_statistical_dashboard(data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty_dashboard(self, visualizer):
        fig = visualizer.create_statistical_dashboard({})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_hidden_panels_carry_metric_labels(self, visualizer):
        """Panels whose metric had no data are labelled, never anonymous."""
        data = {"effect_sizes": {"comparison_1": 0.5}}
        fig = visualizer.create_statistical_dashboard(data)
        titles = [ax.get_title() for ax in fig.axes]
        assert "Effect Sizes" in titles
        labelled_no_data = [t for t in titles if "no data" in t]
        assert labelled_no_data, "skipped metrics must be labelled 'no data'"
        assert all(t for t in titles if "no data" in t)
        plt.close(fig)

    def test_font_floor_enforced(self, visualizer, dashboard_data):
        """Every rendered text element is at least 16pt."""
        fig = visualizer.create_statistical_dashboard(dashboard_data)
        sizes = []
        for ax in fig.axes:
            sizes.append(ax.title.get_fontsize())
            sizes.extend(t.get_fontsize() for t in ax.texts)
            sizes.extend(
                lab.get_fontsize()
                for lab in ax.get_xticklabels() + ax.get_yticklabels()
            )
        suptitle = getattr(fig, "_suptitle", None)
        if suptitle is not None:
            sizes.append(suptitle.get_fontsize())
        assert sizes
        assert min(sizes) >= 16.0, f"sub-16pt text found: {min(sizes)}"
        plt.close(fig)

    def test_custom_title(self, visualizer, dashboard_data):
        fig = visualizer.create_statistical_dashboard(
            dashboard_data, title="Custom Dashboard"
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestVisualizeHypothesisTesting:
    """Tests for visualize_hypothesis_testing method."""

    def test_basic_hypothesis(self, visualizer, hypothesis_results):
        fig = visualizer.visualize_hypothesis_testing(hypothesis_results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_save_to_file(self, visualizer, hypothesis_results):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "hypothesis.png"
            fig = visualizer.visualize_hypothesis_testing(
                hypothesis_results, filepath=filepath
            )
            assert filepath.exists()
            plt.close(fig)

    def test_all_significant(self, visualizer):
        results = [
            {"test_name": "T1", "p_value": 0.001, "effect_size": 0.8},
            {"test_name": "T2", "p_value": 0.01, "effect_size": 0.6},
        ]
        fig = visualizer.visualize_hypothesis_testing(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_none_significant(self, visualizer):
        results = [
            {"test_name": "T1", "p_value": 0.5, "effect_size": 0.1},
            {"test_name": "T2", "p_value": 0.8, "effect_size": 0.05},
        ]
        fig = visualizer.visualize_hypothesis_testing(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_single_result(self, visualizer):
        results = [{"test_name": "Only Test", "p_value": 0.04, "effect_size": 0.5}]
        fig = visualizer.visualize_hypothesis_testing(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_title(self, visualizer, hypothesis_results):
        fig = visualizer.visualize_hypothesis_testing(
            hypothesis_results, title="My Hypothesis Tests"
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_missing_fields_use_defaults(self, visualizer):
        results = [
            {"p_value": 0.02},
            {"test_name": "Named Test"},
        ]
        fig = visualizer.visualize_hypothesis_testing(results)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestStandaloneModuleImport:
    """statistical_visualization's absolute-import fallback branches."""

    def test_module_loads_without_package_context(self, monkeypatch):
        """Loading the module standalone (no parent package) exercises the
        fallback import branches for ConceptVisualizer and _style."""
        import importlib.util
        from pathlib import Path

        import visualization.statistical_visualization as pkg_svv

        # The bare `from concept_visualization import ...` fallback expects
        # the visualization directory itself on sys.path.
        vis_dir = Path(pkg_svv.__file__).parent
        monkeypatch.syspath_prepend(str(vis_dir))

        source = Path(pkg_svv.__file__)
        spec = importlib.util.spec_from_file_location(
            "_svv_standalone_probe", source
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, "StatisticalVisualizer")
        assert hasattr(module, "plot_statistical_analysis")
        assert module.MIN_FONT >= 16
        plt.close("all")


class TestPlotLayerComparison:
    """plot_layer_comparison: grouped abstract-vs-fulltext entropy bars."""

    ABSTRACT_ARTIFACT = {
        "layer": "abstract",
        "descriptives": {
            domain: {"n_terms": 10 + i, "entropy_mean": 1.0 + i * 0.1}
            for i, domain in enumerate(
                [
                    "unit_of_individuality",
                    "behavior_and_identity",
                    "power_and_labor",
                    "sex_and_reproduction",
                    "kin_and_relatedness",
                    "economics",
                ]
            )
        },
    }

    FULLTEXT_ARTIFACT = {
        "layer": "fulltext",
        "descriptives": {
            domain: {"n_terms": 20 + i, "entropy_mean": 2.0 + i * 0.1}
            for i, domain in enumerate(
                [
                    "unit_of_individuality",
                    "behavior_and_identity",
                    "power_and_labor",
                    "sex_and_reproduction",
                    "kin_and_relatedness",
                    "economics",
                ]
            )
        },
    }

    def test_renders_valid_png(self, tmp_path) -> None:
        from visualization.statistical_visualization import plot_layer_comparison

        filepath = plot_layer_comparison(
            self.ABSTRACT_ARTIFACT,
            self.FULLTEXT_ARTIFACT,
            str(tmp_path),
        )
        path = Path(filepath)
        assert path.name == "layer_comparison.png"
        assert path.exists() and path.stat().st_size > 0

    def test_custom_filename(self, tmp_path) -> None:
        from visualization.statistical_visualization import plot_layer_comparison

        filepath = plot_layer_comparison(
            self.ABSTRACT_ARTIFACT,
            self.FULLTEXT_ARTIFACT,
            str(tmp_path),
            filename="custom_name.png",
        )
        assert Path(filepath).name == "custom_name.png"
        assert Path(filepath).exists()

    def test_missing_descriptives_falls_back(self, tmp_path) -> None:
        from visualization.statistical_visualization import plot_layer_comparison

        filepath = plot_layer_comparison({}, {}, str(tmp_path))
        assert Path(filepath).exists() and Path(filepath).stat().st_size > 0

    def test_font_floor_enforced(self, tmp_path, monkeypatch) -> None:
        """Every rendered text element is at least 16pt."""
        import matplotlib.pyplot as plt

        import visualization.statistical_visualization as svv

        captured = {}

        def capturing_save_and_verify(fig, filepath, dpi=300):
            captured["fig"] = fig

        monkeypatch.setattr(svv, "save_and_verify", capturing_save_and_verify)
        svv.plot_layer_comparison(
            self.ABSTRACT_ARTIFACT,
            self.FULLTEXT_ARTIFACT,
            str(tmp_path),
        )
        fig = captured["fig"]
        sizes = []
        for ax in fig.axes:
            sizes.append(ax.title.get_fontsize())
            sizes.extend(t.get_fontsize() for t in ax.texts)
            sizes.extend(
                lab.get_fontsize()
                for lab in ax.get_xticklabels() + ax.get_yticklabels()
            )
            legend = ax.get_legend()
            if legend is not None:
                sizes.extend(
                    t.get_fontsize() for t in legend.get_texts()
                )
        assert sizes
        assert min(sizes) >= 16.0, f"sub-16pt text found: {min(sizes)}"
        plt.close(fig)

    def test_real_artifacts_smoke(self, tmp_path) -> None:
        """Renders a valid PNG from the two real pipeline artifacts."""
        from visualization.statistical_visualization import plot_layer_comparison

        output_data = Path(__file__).resolve().parents[1] / "output" / "data"
        abstract_path = output_data / "statistical_analysis.json"
        fulltext_path = output_data / "fulltext_analysis.json"
        if not (abstract_path.is_file() and fulltext_path.is_file()):
            pytest.skip("real pipeline artifacts not present")
        with abstract_path.open() as f:
            abstract_artifact = json.load(f)
        with fulltext_path.open() as f:
            fulltext_artifact = json.load(f)
        filepath = Path(
            plot_layer_comparison(
                abstract_artifact, fulltext_artifact, str(tmp_path)
            )
        )
        assert filepath.exists() and filepath.stat().st_size > 0


class TestFulltextFingerprintGuard:
    """Corpus-fingerprint freshness guard for the full-text stage
    (src/visualization/manuscript_figures._ensure_fulltext_artifact)."""

    @staticmethod
    def _write_corpus(fulltexts_dir: Path, n_docs: int = 3) -> None:
        """Materialize one shard + provenance sidecar."""
        fulltexts_dir.mkdir(parents=True, exist_ok=True)
        corpus = [{"pmcid": f"PMC{i}"} for i in range(n_docs)]
        (fulltexts_dir / "fulltexts_00001.json").write_text(
            json.dumps(corpus), encoding="utf-8"
        )
        (fulltexts_dir / "provenance.json").write_text(
            json.dumps({"PMC0": {}, "PMC1": {}, "PMC2": {}}), encoding="utf-8"
        )

    @staticmethod
    def _fake_builder(calls):
        def builder(fulltexts):
            calls.append(list(fulltexts))
            return {
                "layer": "fulltext",
                "n_documents": len(fulltexts),
                "pairwise": [],
                "skipped": [],
            }

        return builder

    def test_fingerprint_shape(self, tmp_path) -> None:
        from visualization.manuscript_figures import (
            _fulltext_corpus_fingerprint,
        )

        self._write_corpus(tmp_path)
        fingerprint = _fulltext_corpus_fingerprint(
            [{"pmcid": "PMC0"}, {"pmcid": "PMC1"}, {"pmcid": "PMC2"}],
            str(tmp_path),
        )
        assert fingerprint["record_count"] == 3
        assert len(fingerprint["provenance_sha256"]) == 64

    def test_stale_artifact_is_regenerated_once(self, tmp_path, monkeypatch) -> None:
        """A pre-guard artifact (no fingerprint) counts as stale."""
        from visualization.manuscript_figures import _ensure_fulltext_artifact

        fulltexts_dir = tmp_path / "fulltexts"
        data_dir = tmp_path / "output" / "data"
        data_dir.mkdir(parents=True)
        self._write_corpus(fulltexts_dir)
        (data_dir / "fulltext_analysis.json").write_text(
            json.dumps({"layer": "fulltext", "n_documents": 500}),
            encoding="utf-8",
        )
        monkeypatch.delenv("FULLTEXT_ANALYSIS_LIMIT", raising=False)
        calls = []
        artifact = _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert artifact["n_documents"] == 3
        assert artifact["corpus_fingerprint"]["record_count"] == 3
        assert artifact["corpus_fingerprint"]["limit"] is None
        assert len(calls) == 1
        # Stored artifact carries the fingerprint.
        stored = json.loads(
            (data_dir / "fulltext_analysis.json").read_text(encoding="utf-8")
        )
        assert stored["corpus_fingerprint"] == artifact["corpus_fingerprint"]

    def test_fresh_artifact_is_skipped(self, tmp_path, monkeypatch) -> None:
        """Matching fingerprint → the builder is not called again."""
        from visualization.manuscript_figures import _ensure_fulltext_artifact

        fulltexts_dir = tmp_path / "fulltexts"
        data_dir = tmp_path / "output" / "data"
        data_dir.mkdir(parents=True)
        self._write_corpus(fulltexts_dir)
        monkeypatch.delenv("FULLTEXT_ANALYSIS_LIMIT", raising=False)
        calls = []
        first = _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert len(calls) == 1
        second = _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert len(calls) == 1  # builder not called again
        assert second == first

    def test_changed_corpus_is_regenerated(self, tmp_path, monkeypatch) -> None:
        """A changed provenance sidecar invalidates the fingerprint."""
        from visualization.manuscript_figures import _ensure_fulltext_artifact

        fulltexts_dir = tmp_path / "fulltexts"
        data_dir = tmp_path / "output" / "data"
        data_dir.mkdir(parents=True)
        self._write_corpus(fulltexts_dir)
        monkeypatch.delenv("FULLTEXT_ANALYSIS_LIMIT", raising=False)
        calls = []
        _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert len(calls) == 1
        # Touch the provenance sidecar → corpus changed.
        (fulltexts_dir / "provenance.json").write_text(
            json.dumps({"changed": True}), encoding="utf-8"
        )
        _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert len(calls) == 2

    def test_bounded_run_never_satisfies_full_corpus_guard(
        self, tmp_path, monkeypatch
    ) -> None:
        """FULLTEXT_ANALYSIS_LIMIT artifacts are marked with their limit."""
        from visualization.manuscript_figures import _ensure_fulltext_artifact

        fulltexts_dir = tmp_path / "fulltexts"
        data_dir = tmp_path / "output" / "data"
        data_dir.mkdir(parents=True)
        self._write_corpus(fulltexts_dir, n_docs=5)
        monkeypatch.setenv("FULLTEXT_ANALYSIS_LIMIT", "2")
        calls = []
        bounded = _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert bounded["n_documents"] == 2
        assert bounded["corpus_fingerprint"]["limit"] == 2
        # Even with the same env, the bounded artifact is fresh only for
        # the bounded fingerprint (same limit) — not for a full run.
        monkeypatch.delenv("FULLTEXT_ANALYSIS_LIMIT", raising=False)
        _ensure_fulltext_artifact(
            str(data_dir), str(fulltexts_dir), builder=self._fake_builder(calls)
        )
        assert len(calls) == 2  # full corpus rebuilt over the bounded one

    def test_missing_shards_returns_none(self, tmp_path) -> None:
        from visualization.manuscript_figures import _ensure_fulltext_artifact

        calls = []
        result = _ensure_fulltext_artifact(
            str(tmp_path / "out"), str(tmp_path / "absent"),
            builder=self._fake_builder(calls),
        )
        assert result is None
        assert calls == []
