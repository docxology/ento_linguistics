# Ento-Linguistics Review Summary

Review completed per plan to ensure complete functional coherence across methods, documentation, tests, and manuscript.

**Note:** Test counts and corpus figures mentioned in the changelog below are historical snapshots. For current numbers, run `uv run pytest tests/ --collect-only -q` and see [standards_compliance.md](standards_compliance.md). PDF builds use `scripts/_render_pdf_override.py` with `{{KEY}}` substitution from `output/data/*.json` (see [manuscript_data_lineage.md](manuscript_data_lineage.md)).

## Completed Edits

### Documentation Drift

- **tests/AGENTS.md**: Replaced `project/tests/` and `project/src/` with `tests/` and `src/`; removed obsolete `test_simulation_coverage.py` (file does not exist); updated directory structure to match actual 38 test files; updated all pytest commands to use `uv run pytest tests/ --cov=src`; fixed See Also links.
- **tests/README.md**: Updated test count from 923 to 1013; corrected integration file count from 5 to 3.
- **docs/AGENTS.md**: Updated test counts from 983 to 1013, 35 to 38 test files.
- **README.md**: Updated test count from 983 to 1013; trimmed adjectives ("Advanced", "Sophisticated") from Recent Improvements list.
- **src/AGENTS.md**: Trimmed "Advanced" from concept_visualization description.

### Manuscript–Data Linkage

- **docs/manuscript/AGENTS.md**: Updated figure list to match actual `output/figures/` contents (11 PNGs); removed non-existent per-domain figures; corrected `project/` paths to `output/` and `docs/manuscript/`; fixed validation commands to use `scripts/_manuscript_preflight.py` and `scripts/_quality_report.py`.

### Scripts

- **scripts/README.md**: Fixed import example to use `from analysis.` (not `from src.analysis.`) when `src/` is on PYTHONPATH.
- **scripts/AGENTS.md**: Clarified that `_`-prefixed scripts are preserved for targeted analysis, validation, or debugging.

## Verification

- **Test count**: 1225 tests collected (measured by `uv run pytest tests/ --collect-only -q`, 2026-09-14); the last recorded full run in `output/reports/test_results.json` reports 1224 passed, 1 skipped (integration test), ~93% coverage.
- **Coverage**: Run `uv run pytest tests/ --cov=src --cov-report=term-missing` for current coverage. Remove stale `.coverage` and `.coverage.*` files before runs if coverage reporting fails with "Can't combine statement coverage data with branch data" (e.g. after using pytest-xdist).
- **Figures**: 12 PNGs in `output/figures/` match manuscript references, including the inferential-statistics summary `statistical_analysis.png`.
- **Placeholders**: `{{CORPUS_*}}`, `{{DOMAIN_*}}`, `{{NETWORK_*}}`, `{{TERM_FREQ_*}}` are populated by `_render_pdf_override.py` from `output/data/*.json` and `data/corpus/abstracts.json`; `{{ANOVA_*}}`, `{{PAIRWISE_*}}`, `{{CORRECTION_METHOD}}`, and `{{PAIRWISE_N_COMPARISONS}}` are populated from `output/data/statistical_analysis.json`.

## Module–Test Mapping

| src/ | tests/ |
|------|--------|
| analysis/*.py | test_*.py (12 modules) |
| core/*.py | test_*.py (8 modules) |
| data/*.py | test_*.py (4 modules) |
| pipeline/*.py | test_*.py (4 modules) |
| visualization/*.py | test_*.py (5 modules) |

## Remaining Notes

- No root `coverage.json` is maintained; coverage is reported inline via `uv run pytest tests/ --cov=src` (branch coverage is enabled in `pyproject.toml`).
- `98_symbols_glossary.md` has an empty `<!-- BEGIN: AUTO-API-GLOSSARY -->` block; the hand-maintained Pipeline Modules table remains the source of truth.
- Figure registry (`output/figures/figure_registry.json`) tracks 12 figures: the 11 analysis figures plus the inferential-statistics summary `statistical_analysis.png` (see `CHANGELOG.md` 1.1.0).
