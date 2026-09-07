# scripts/ - Thin Orchestrators

## Purpose

The `scripts/` directory contains **thin orchestrators** that integrate with `src/` modules. Scripts handle argparse, path bootstrap, logging, and a single delegated call into a `src/` entrypoint — they never implement business logic themselves.

## Script Inventory

| Script | Pattern | Delegates to | Output |
|--------|---------|--------------|--------|
| `01_build_corpus.py` | Stage 01 Thin Orchestrator | `src/data/literature_mining.py` | Corpus files under `data/corpus/` |
| `02_generate_figures.py` | Stage 02 Thin Orchestrator | `src/visualization/manuscript_figures.py` | 11 PNGs in `output/figures/`, JSONs in `output/data/`, filled manuscript variables |
| `_analysis_pipeline.py` | Helper | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | Pipeline reports under `output/reports/` |
| `_conceptual_mapping_script.py` | Helper | `src/analysis/conceptual_mapping.py`, `src/visualization/concept_visualization.py` | Concept map figures/data |
| `_convert_corpus.py` | Helper | `src/data/loader.py` (`convert_corpus`) | `data/corpus/abstracts.json` |
| `_discourse_analysis_script.py` | Helper | `src/analysis/discourse_analysis.py`, `src/visualization/concept_visualization.py` | Discourse analysis outputs |
| `_domain_analysis_script.py` | Helper | `src/analysis/domain_analysis.py`, `src/visualization/figure_manager.py` | Domain analysis figures/data |
| `_example_figure.py` | Helper (self-contained demo) | — | Example PNG |
| `_fill_manuscript_variables.py` | Helper | `src/core/manuscript_variables.py` | `{{VAR}}`-substituted manuscript markdown |
| `_generate_domain_figures.py` | Helper | `src/analysis/domain_analysis.py`, `src/visualization/figure_manager.py` | Per-domain figures |
| `_generate_missing_figures.py` | Helper (stale import; superseded by `02_generate_figures.py`) | former `generate_research_figures` script | — |
| `_generate_scientific_figures.py` | Helper | `src/visualization/plots.py`, `src/analysis/performance.py` | Simulation figures |
| `_literature_analysis_pipeline.py` | Helper | `src/data/literature_mining.py`, `src/analysis/*` | Mined corpus + analysis outputs |
| `_manuscript_preflight.py` | Helper | `src/core/validation_utils.py` | Preflight validation report |
| `_quality_report.py` | Helper | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | Quality report JSON |
| `_register_manuscript_figures.py` | Helper | `src/visualization/figure_manager.py` | `figure_registry.json` updates |
| `_render_pdf_override.py` | Helper | `src/pipeline/rendering.py` | `output/pdf/ento_linguistics_combined.pdf` |
| `_scientific_simulation.py` | Helper | `src/pipeline/simulation.py`, `src/data/data_generator.py` | Simulation outputs |

## Design Contract

- Scripts are orchestration only: path bootstrap, argparse/logging, and module entrypoint invocation.
- Data/model/plot logic lives in `src/`.
- All reusable script behavior must be covered by tests in `tests/`.
- Manually-run helpers are prefixed `_` and are **not** auto-discovered by the pipeline (which runs `01_build_corpus.py` and `02_generate_figures.py`).

## What Scripts Do / Don't Do

**Do**: import from `src/`, orchestrate data flow, handle file I/O and directory management, configure logging.

**Don't**: implement mathematical algorithms, duplicate business logic, contain complex computations.

## See Also

- [`README.md`](README.md) — script inventory with commands
- [`../src/AGENTS.md`](../src/AGENTS.md) - Available src/ modules
- [`../AGENTS.md`](../AGENTS.md) - Project documentation
