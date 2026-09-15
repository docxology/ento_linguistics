# AGENTS.md — `ento_linguistics/src/pipeline`

> Pipeline stage modules: importable business logic for the thin orchestrator
> scripts in `scripts/`. Verified by direct listing (OrchFix, 2026-09-14).

## Scope
- Local-only path under `projects/ongoing/` — matched by the root `.gitignore`
  rule `projects/*`; never commit, add, or push anything here.
- Parent standard: see `projects/ongoing/AGENTS.md`; parent project docs: `ento_linguistics/src/AGENTS.md`.

## Layout
Files: `AGENTS.md`, `README.md`, `__init__.py`, `corpus_build.py`,
`conceptual_mapping_pipeline.py`, `discourse_pipeline.py`,
`domain_analysis_pipeline.py`, `domain_figures.py`, `literature_pipeline.py`,
`rendering.py`, `reporting.py`, `simulation.py`

## Modules

| Module | Responsibility | Invoked by |
|--------|----------------|------------|
| `corpus_build.py` | PubMed retrieval, dedup, corpus validation statistics | `scripts/01_build_corpus.py` |
| `conceptual_mapping_pipeline.py` | Concept maps and terminology networks | `scripts/_conceptual_mapping_script.py` |
| `discourse_pipeline.py` | Discourse-pattern analysis and reports | `scripts/_discourse_analysis_script.py` |
| `domain_analysis_pipeline.py` | Per-domain terminology analysis/reports | `scripts/_domain_analysis_script.py` |
| `domain_figures.py` | Per-domain figure generation | `scripts/_generate_domain_figures.py` |
| `literature_pipeline.py` | Full mining→extraction→mapping workflow | `scripts/_literature_analysis_pipeline.py` |
| `rendering.py` | Pandoc/XeLaTeX PDF build, TeX post-processing, `{{KEY}}` substitution | `scripts/_render_pdf_override.py` |
| `reporting.py` | Report generation, error aggregation | `_quality_report.py`, `_scientific_simulation.py` |
| `simulation.py` | Simulation base classes | `_scientific_simulation.py` |

## Gotchas
- Modules import sibling packages as flat top-level names (`analysis.*`,
  `core.*`, `data.*`, `visualization.*`) — `src/` must be on `sys.path`
  (the thin-orchestrator scripts and `pyproject.toml` `pythonpath` do this).
- `rendering.build_pdf` shells out to `pandoc`/`xelatex`/`bibtex`; the pure
  helpers (`_postprocess_combined_tex`, `_build_frontmatter`,
  `_load_corpus_vars`, `_apply_corpus_vars`) are covered by
  `tests/test_rendering.py`.
