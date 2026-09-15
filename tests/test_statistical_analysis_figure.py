"""Behavioral tests for the frozen statistics-artifact figure contract.

Covers ``plot_statistical_analysis`` in
``src/visualization/statistical_visualization.py``: the multi-panel figure
rendered from the frozen ``statistical_analysis.json`` schema, its save-and-
verify contract, the 16 pt font floor, BH-significance colour coding, and the
edge-case fallback panels.

The fixture uses the real canonical Ento-Linguistic domain names with
plausible, deterministic values — no randomness, no mocks.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgba

from visualization._style import CANONICAL_DOMAINS, DOMAIN_PALETTE, MIN_FONT
from visualization.statistical_visualization import (
    _domain_order,
    _format_p,
    plot_statistical_analysis,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def stats_artifact():
    """Schema-faithful statistics artifact built from real domain names.

    Values are plausible deterministic floats; the artifact includes a
    non-canonical domain and a zero ``p`` to exercise every panel branch.
    """
    return {
        "descriptives": {
            "unit_of_individuality": {
                "n_terms": 42,
                "entropy_mean": 2.31,
                "entropy_sd": 0.42,
                "ambiguity_mean": 1.8,
                "cace_mean": 0.12,
                "bridging_count": 7,
            },
            "power_and_labor": {
                "n_terms": 55,
                "entropy_mean": 2.74,
                "entropy_sd": 0.51,
                "ambiguity_mean": 2.1,
                "cace_mean": 0.19,
                "bridging_count": 11,
            },
            "kin_and_relatedness": {
                "n_terms": 31,
                "entropy_mean": 2.05,
                "entropy_sd": 0.38,
                "ambiguity_mean": 1.5,
                "cace_mean": 0.08,
                "bridging_count": 4,
            },
            "noncanonical_extra_domain": {
                "n_terms": 9,
                "entropy_mean": 1.70,
                "entropy_sd": 0.20,
                "ambiguity_mean": 1.0,
                "cace_mean": 0.0,
                "bridging_count": 0,
            },
        },
        "pairwise": [
            {
                "domain_a": "unit_of_individuality",
                "domain_b": "power_and_labor",
                "metric": "semantic_entropy",
                "t": -3.21,
                "df": 78.4,
                "p": 0.002,
                "p_bh": 0.006,
                "cohens_d": -0.71,
                "n_a": 42,
                "n_b": 55,
                "significant_bh": True,
            },
            {
                "domain_a": "unit_of_individuality",
                "domain_b": "kin_and_relatedness",
                "metric": "semantic_entropy",
                "t": 1.87,
                "df": 64.0,
                "p": 0.066,
                "p_bh": 0.099,
                "cohens_d": 0.45,
                "n_a": 42,
                "n_b": 31,
                "significant_bh": False,
            },
            {
                "domain_a": "power_and_labor",
                "domain_b": "kin_and_relatedness",
                "metric": "semantic_entropy",
                "t": 5.13,
                "df": 82.1,
                "p": 0.0,
                "p_bh": 0.0,
                "cohens_d": 1.12,
                "n_a": 55,
                "n_b": 31,
                "significant_bh": True,
            },
        ],
        "anova": {
            "metric": "semantic_entropy",
            "F": 7.83,
            "df1": 3,
            "df2": 124,
            "p": 0.0,
            "eta_squared": 0.159,
        },
        "corrections": {"method": "benjamini_hochberg", "n_comparisons": 3},
    }


def _capture_figure(monkeypatch):
    """Keep ``plot_statistical_analysis``'s figure open for inspection.

    Patches ``plt.close`` to skip Figure instances so the rendered figure
    can be introspected after the call, while delegating ``close("all")``
    and other non-figure targets to the real implementation.
    """
    original_close = plt.close
    monkeypatch.setattr(
        plt,
        "close",
        lambda target: (
            None
            if isinstance(target, matplotlib.figure.Figure)
            else original_close(target)
        ),
    )


def _last_figure():
    """Return the single currently open figure."""
    nums = plt.get_fignums()
    assert len(nums) == 1, f"expected exactly one open figure, got {len(nums)}"
    return plt.figure(nums[0])


def _axes_by_title(fig):
    """Map panel title -> Axes for the multi-panel figure."""
    return {ax.get_title(): ax for ax in fig.get_axes()}


class TestPlotStatisticalAnalysisContract:
    """Contract tests: signature behaviour, save-and-verify, PNG validity."""

    def test_returns_path_and_writes_valid_png(self, stats_artifact, tmp_path):
        """The figure file exists, is non-empty, and is a real PNG."""
        out = plot_statistical_analysis(stats_artifact, str(tmp_path))

        assert out == str(tmp_path / "statistical_analysis.png")
        path = tmp_path / "statistical_analysis.png"
        assert path.exists()
        data = path.read_bytes()
        assert len(data) > 0
        assert data.startswith(PNG_MAGIC)

    def test_default_filename_is_statistical_analysis_png(
        self, stats_artifact, tmp_path
    ):
        """Default ``filename`` produces statistical_analysis.png."""
        out = plot_statistical_analysis(stats_artifact, str(tmp_path))
        assert os.path.basename(out) == "statistical_analysis.png"

    def test_custom_filename_respected(self, stats_artifact, tmp_path):
        """A custom ``filename`` overrides the default."""
        out = plot_statistical_analysis(
            stats_artifact, str(tmp_path), filename="custom_stats.png"
        )
        assert os.path.basename(out) == "custom_stats.png"
        assert (tmp_path / "custom_stats.png").exists()

    def test_creates_missing_output_dir(self, stats_artifact, tmp_path):
        """A non-existent output directory is created rather than failing."""
        target = tmp_path / "nested" / "figures"
        out = plot_statistical_analysis(stats_artifact, str(target))
        assert os.path.exists(out)

    def test_output_is_deterministic(self, stats_artifact, tmp_path):
        """Two runs on the same input produce byte-identical PNGs."""
        dir_a = tmp_path / "a"
        dir_b = tmp_path / "b"
        out_a = plot_statistical_analysis(stats_artifact, str(dir_a))
        out_b = plot_statistical_analysis(stats_artifact, str(dir_b))
        with open(out_a, "rb") as fa, open(out_b, "rb") as fb:
            assert fa.read() == fb.read()


class TestPlotStatisticalAnalysisFontFloor:
    """Every text element in the rendered figure honours the 16 pt floor."""

    def test_all_text_artists_meet_font_floor(self, stats_artifact, monkeypatch):
        """Titles, labels, ticks, annotations and legend text are >= MIN_FONT."""
        _capture_figure(monkeypatch)
        try:
            plot_statistical_analysis(stats_artifact, "/tmp/unused_psa")
            fig = _last_figure()
            texts = [
                t
                for t in fig.findobj(matplotlib.text.Text)
                if t.get_text().strip()
            ]
            assert texts, "figure rendered no text"
            for text in texts:
                size = text.get_fontsize()
                assert size >= MIN_FONT, (
                    f"text {text.get_text()!r} has fontsize {size} "
                    f"below {MIN_FONT}pt floor"
                )
        finally:
            plt.close("all")


class TestPlotStatisticalAnalysisPanels:
    """Panel content: entropy bars, effect sizes, ANOVA summary."""

    def test_entropy_bars_annotate_n(self, stats_artifact, monkeypatch):
        """Panel (a) shows one bar per domain with an n=<n_terms> annotation."""
        _capture_figure(monkeypatch)
        try:
            plot_statistical_analysis(stats_artifact, "/tmp/unused_psa")
            fig = _last_figure()
            ax = _axes_by_title(fig)["Domain Entropy"]
            descriptives = stats_artifact["descriptives"]
            assert len(ax.patches) == len(descriptives)

            annotations = [
                t.get_text() for t in ax.texts if t.get_text().startswith("n=")
            ]
            expected_ns = {f"n={d['n_terms']}" for d in descriptives.values()}
            assert set(annotations) == expected_ns

            # Bar fills use the shared canonical palette; unknown domains
            # fall back to neutral grey.
            fills = {tuple(p.get_facecolor()[:3]) for p in ax.patches}
            for domain in descriptives:
                color = DOMAIN_PALETTE.get(domain, "#7f7f7f")
                assert to_rgba(color)[:3] in fills, (
                    f"{domain}: expected fill {color} among {fills}"
                )
        finally:
            plt.close("all")

    def test_effect_sizes_significance_coding(self, stats_artifact, monkeypatch):
        """Panel (b) codes BH-significant comparisons vermillion, others blue."""
        _capture_figure(monkeypatch)
        try:
            plot_statistical_analysis(stats_artifact, "/tmp/unused_psa")
            fig = _last_figure()
            ax = _axes_by_title(fig)["Pairwise Effect Sizes"]

            bars = ax.patches
            pairwise = stats_artifact["pairwise"]
            assert len(bars) == len(pairwise)
            for bar, row in zip(bars, pairwise):
                face = tuple(bar.get_facecolor())
                expected = "#D55E00" if row["significant_bh"] else "#0072B2"
                assert face[:3] == to_rgba(expected)[:3], (
                    f"{row['domain_a']} vs {row['domain_b']}: expected "
                    f"{expected}, got {face}"
                )
        finally:
            plt.close("all")

    def test_effect_sizes_show_cohens_d_values(self, stats_artifact, monkeypatch):
        """Panel (b) labels each bar with its Cohen's d value."""
        _capture_figure(monkeypatch)
        try:
            plot_statistical_analysis(stats_artifact, "/tmp/unused_psa")
            fig = _last_figure()
            ax = _axes_by_title(fig)["Pairwise Effect Sizes"]
            labels = {t.get_text() for t in ax.texts}
            for row in stats_artifact["pairwise"]:
                assert f"{row['cohens_d']:+.2f}" in labels
        finally:
            plt.close("all")

    def test_anova_summary_panel_content(self, stats_artifact, monkeypatch):
        """Panel (c) reports F, df, p and eta^2 from the artifact."""
        _capture_figure(monkeypatch)
        try:
            plot_statistical_analysis(stats_artifact, "/tmp/unused_psa")
            fig = _last_figure()
            summary_axes = [
                ax
                for ax in fig.get_axes()
                if ax.get_title() == ""
                and any("ANOVA Summary" in t.get_text() for t in ax.texts)
            ]
            assert summary_axes, "no ANOVA summary panel found"
            text = "\n".join(t.get_text() for t in summary_axes[0].texts)
            anova = stats_artifact["anova"]
            assert f"F({anova['df1']},{anova['df2']}) = {anova['F']:.2f}" in text
            assert f"η² = {anova['eta_squared']:.3f}" in text
            # p = 0.0 must render as p < 0.001
            assert "p < 0.001" in text
        finally:
            plt.close("all")

    def test_legend_codes_significance(self, stats_artifact, monkeypatch):
        """Panel (b) legend explains the colourblind-safe significance coding."""
        _capture_figure(monkeypatch)
        try:
            plot_statistical_analysis(stats_artifact, "/tmp/unused_psa")
            fig = _last_figure()
            ax = _axes_by_title(fig)["Pairwise Effect Sizes"]
            legend_labels = {t.get_text() for t in ax.get_legend().get_texts()}
            assert legend_labels == {"BH-significant", "Not significant"}
        finally:
            plt.close("all")


class TestPlotStatisticalAnalysisEdgeCases:
    """Edge cases must not raise and must render fallback panels."""

    def test_empty_artifact_renders_fallback_panels(self, tmp_path, monkeypatch):
        """An artifact with all sections empty renders three fallback panels."""
        _capture_figure(monkeypatch)
        try:
            out = plot_statistical_analysis(
                {"descriptives": {}, "pairwise": [], "anova": {}}, str(tmp_path)
            )
            figs = [plt.figure(n) for n in plt.get_fignums()]
        finally:
            plt.close("all")
        assert os.path.exists(out)
        with open(out, "rb") as f:
            assert f.read().startswith(PNG_MAGIC)

        fallback = [t.get_text() for fig in figs for t in fig.findobj(matplotlib.text.Text)]
        assert "No domain descriptives available" in fallback
        assert "No pairwise comparisons available" in fallback
        assert "No ANOVA results available" in fallback

    def test_missing_sections_renders_fallbacks(self, tmp_path):
        """An artifact missing keys entirely (None defaults) still renders."""
        out = plot_statistical_analysis({}, str(tmp_path))
        assert (tmp_path / "statistical_analysis.png").exists()
        assert os.path.basename(out) == "statistical_analysis.png"

    def test_subset_of_domains_renders(self, stats_artifact, tmp_path):
        """A descriptives dict with fewer domains than the canon works."""
        reduced = dict(stats_artifact)
        reduced["descriptives"] = {
            "economics": {
                "n_terms": 12,
                "entropy_mean": 1.9,
                "entropy_sd": 0.3,
                "ambiguity_mean": 1.1,
                "cace_mean": 0.05,
                "bridging_count": 1,
            },
        }
        reduced["pairwise"] = []
        out = plot_statistical_analysis(reduced, str(tmp_path))
        assert os.path.exists(out)
        with open(out, "rb") as f:
            assert f.read().startswith(PNG_MAGIC)

    def test_small_but_nonzero_p_not_rendered_as_lt_threshold(self):
        """p values above the 0.001 threshold render as p = 0.066 style."""
        assert _format_p(0.066) == "p = 0.066"


class TestFormatP:
    """Unit tests for the p-value annotation helper."""

    def test_zero_renders_as_below_threshold(self):
        """Exact 0.0 is rendered as p < 0.001."""
        assert _format_p(0.0) == "p < 0.001"

    def test_tiny_renders_as_below_threshold(self):
        """Values under 0.001 render as p < 0.001."""
        assert _format_p(0.0007) == "p < 0.001"

    def test_threshold_boundary_renders_with_decimals(self):
        """Exactly 0.001 is NOT below the threshold (strict ``<``)."""
        assert _format_p(0.001) == "p = 0.001"

    def test_typical_value_renders_with_three_decimals(self):
        """Values above the threshold render with three decimals."""
        assert _format_p(0.0391) == "p = 0.039"

    def test_one_renders_as_one(self):
        """p = 1.0 renders without the threshold shortcut."""
        assert _format_p(1.0) == "p = 1.000"


class TestDomainOrder:
    """The domain ordering is canonical-first, extras sorted, deterministic."""

    def test_canonical_domains_precede_extras(self):
        """Canonical domains come first in canon order, extras after sorted."""
        descriptives = {
            "zzz_extra": {},
            "economics": {},
            "unit_of_individuality": {},
            "aaa_extra": {},
            "kin_and_relatedness": {},
        }
        assert _domain_order(descriptives) == [
            "unit_of_individuality",
            "kin_and_relatedness",
            "economics",
            "aaa_extra",
            "zzz_extra",
        ]

    def test_all_canonical_domains(self):
        """A descriptives dict over the full canon lists every domain."""
        descriptives = {d: {} for d in reversed(CANONICAL_DOMAINS)}
        assert _domain_order(descriptives) == list(CANONICAL_DOMAINS)

    def test_empty_descriptives(self):
        """An empty mapping yields an empty order."""
        assert _domain_order({}) == []
