# Manuscript Status

- **Project:** ento_linguistics
- **Manuscript title:** Ento-Linguistics: Language, Ambiguity, and Scientific Communication in Entomology
- **Location:** `docs/manuscript/` (single canonical location; no legacy fallback)
- **Type:** Active publication-target manuscript (17 section files: 9 main sections 01–08 incl. 04a/04b, 6 supplemental sections S01a–S04, plus 98_symbols_glossary and 99_references)
- **Status file purpose:** Tracks publication-readiness of the manuscript content in this directory.
- **Data linkage:** All corpus statistics in prose are double-brace variable placeholders substituted at PDF build time by `scripts/_render_pdf_override.py` from `output/data/*.json` and `data/corpus/abstracts.json` (see `docs/manuscript_data_lineage.md`). Inferential statistics in `S02_supplemental_results.md` (ANOVA, pairwise Welch t-tests, correction metadata) are token-driven from `output/data/statistical_analysis.json`; the "Full-Text Parallel Layer" subsection is token-driven from `output/data/fulltext_analysis.json` via the `FULLTEXT_*` family.
- **Version:** 1.1.0 (2026-09-15); see `CHANGELOG.md` at the project root.
- **Figures:** 13 registered figures in `output/figures/figure_registry.json`, including the inferential-statistics summary `statistical_analysis.png` and the full-text parallel-layer summary `fulltext_analysis.png` (`fig:fulltext_analysis`).
