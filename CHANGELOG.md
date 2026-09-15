# Changelog

All notable changes to the Ento-Linguistics project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Concept DOI: [10.5281/zenodo.19574118](https://doi.org/10.5281/zenodo.19574118) — all versions of this release are grouped under the same concept DOI.

## [1.1.0] - 2026-09-15

Methods and statistics revision of the analysis pipeline and manuscript.

### Added

- **Inferential statistics stage**: Welch's two-sample t-tests on per-term semantic entropy across all 15 Ento-Linguistic domain pairs, Benjamini–Hochberg false-discovery-rate correction, Cohen's d effect sizes, and a one-way ANOVA omnibus test with eta-squared (`src/analysis/statistics.py`, orchestrated by `src/pipeline/statistics_pipeline.py`).
- **Statistics artifact**: `output/data/statistical_analysis.json` with the frozen schema (`descriptives`, `pairwise`, `anova`, `corrections`), produced by the statistics stage inside the figure-generation entry point (`scripts/02_generate_figures.py` → `src/visualization/manuscript_figures.py::main()`).
- **Statistics figure**: `output/figures/statistical_analysis.png` (`src/visualization/statistical_visualization.py::plot_statistical_analysis`), rendered from the artifact and registered in `output/figures/figure_registry.json` (12 figures total).
- **Manuscript token family**: `ANOVA_*`, `PAIRWISE_*`, `CORRECTION_METHOD`, and `PAIRWISE_N_COMPARISONS` variables substituted at PDF build time; the supplemental results tables in `docs/manuscript/S02_supplemental_results.md` are now fully token-driven for all inferential columns.
- `CHANGELOG.md` (this file).

### Changed

- Scripts follow the thin-orchestrator pattern: business logic lives in `src/`, `scripts/` delegate to it.
- Test coverage measured at 93%+ via `uv run pytest tests/ --cov=src`.
- Subprocess invocations during pipeline runs are bounded (timeouts enforced).

### Fixed

- **Ambiguity scores are real**: supplemental tables no longer present hardcoded placeholder scores; descriptives come from per-term valid-entropy means with exclusions counted.
- **Manuscript data corrections**: inferential claims in the manuscript are restated as token-driven values, and the pairwise comparisons are correctly described as tests on per-term semantic entropy (not mean ambiguity scores).

[1.1.0]: https://doi.org/10.5281/zenodo.19574118
