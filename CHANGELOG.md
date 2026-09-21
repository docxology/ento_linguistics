# Changelog

All notable changes to the Ento-Linguistics project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Concept DOI: [10.5281/zenodo.19574118](https://doi.org/10.5281/zenodo.19574118) — all versions of this release are grouped under the same concept DOI.

## [Unreleased]

Pipeline performance: the language-analysis stages now run the same
computations with redundant work removed and the embarrassingly parallel
parts spread over a bounded process pool. Artifacts are unchanged within
a process (byte-identical determinism holds; cross-process float/list-order
nondeterminism in KMeans and hash-ordered term sets predates this change).

### Changed

- **Per-domain entropy recompute removed**: `_format_domain_descriptives`
  no longer re-runs `quantify_ambiguity_metrics` per domain (a full-corpus
  re-tokenization plus per-term regex/KMeans pass, up to 7× per build);
  `ambiguity_mean` reuses the already-computed `entropy_mean`, which is the
  same mean over the same entropy list (`src/pipeline/statistics_pipeline.py`).
- **Entropy context extraction pruned**: per-term whole-corpus regex scans
  are preceded by an alphanumeric part-token inverted index (a sentence can
  only whole-word match a term if every alphanumeric part of the term is
  present), so the regex still decides but only over candidate sentences —
  O(total characters) instead of O(terms × total characters)
  (`src/analysis/domain_analysis.py`).
- **Per-term entropy parallelized**: each term's context extraction +
  TF-IDF → KMeans → Shannon entropy is independent and runs through
  `core.parallel.map_ordered` (spawn pool, ordered merge) when the term
  count warrants it (`src/analysis/domain_analysis.py`).
- **Tokenization parallelized and de-duplicated**: `extract_terms`
  tokenizes texts via the same ordered map and builds candidate-token
  positions in one pass; the full-text framing passes reuse the identical
  `process_text` stream via per-record workers with integer merges
  (`src/analysis/term_extraction.py`, `src/pipeline/fulltext_pipeline.py`,
  `src/pipeline/statistics_pipeline.py`).
- **New shared helper**: `src/core/parallel.py::map_ordered` — bounded
  spawn pool with serial fallback below 64 items and on pool failure;
  ordered merges keep results identical to a serial map.

### Performance

- Full-corpus figure/statistics pipeline (7,609 abstracts + 7,073 full
  texts): previously the statistics + full-text stages alone ran for
  hours (the full-text stage measured ~7-8 h); the complete
  `scripts/02_generate_figures.py` run now completes in ~25 min on the
  same corpus with byte-identical in-process outputs.

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
