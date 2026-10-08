# scripts/ - Thin Orchestrators

## Purpose

The `scripts/` directory contains **thin orchestrators** that integrate with `src/` modules. Scripts handle argparse, path bootstrap, logging, and a single delegated call into a `src/` entrypoint — they never implement business logic themselves.

## Script Inventory

| Script | Pattern | Delegates to | Output |
|--------|---------|--------------|--------|
| `01_build_corpus.py` | Stage 01 Thin Orchestrator | `src/pipeline/corpus_build.py` | `data/corpus/abstracts.json`, `output/data/corpus_statistics.json` |
| `02_generate_figures.py` | Stage 02 Thin Orchestrator | `src/visualization/manuscript_figures.py` | Registered PNGs in `output/figures/`, JSONs in `output/data/`, validated manuscript variables |
| `_analysis_pipeline.py` | End-to-end orchestrator (corpus → figures → preflight) | corpus, figures, and preflight entry points | Stage sequencing, dry-run and stage selection |
| `_conceptual_mapping_script.py` | Thin Orchestrator | `src/pipeline/conceptual_mapping_pipeline.py` | Concept map figures/data |
| `_convert_corpus.py` | Thin Orchestrator | `src/data/loader.py` (`convert_corpus`) | `data/corpus/abstracts.json` |
| `_discourse_analysis_script.py` | Thin Orchestrator | `src/pipeline/discourse_pipeline.py` | Discourse analysis outputs |
| `_domain_analysis_script.py` | Thin Orchestrator | `src/pipeline/domain_analysis_pipeline.py` | Domain analysis figures/data |
| `_example_figure.py` | Self-contained demo (no silent fallbacks) | `src/core/logging`, `src/visualization/figure_manager` | Example PNG/CSV/NPZ |
| `_fill_manuscript_variables.py` | Thin Orchestrator | `src/core/manuscript_variables.py` | `{{VAR}}` coverage validation (dry run; never rewrites markdown) |
| `_generate_domain_figures.py` | Thin Orchestrator | `src/pipeline/domain_figures.py` | Per-domain figures |
| `_literature_analysis_pipeline.py` | Thin Orchestrator | `src/pipeline/literature_pipeline.py` | Mined corpus + analysis outputs |
| `_manuscript_preflight.py` | Thin Orchestrator | `src/core/validation_utils.py` | Preflight validation (defaults: `docs/manuscript`, `output/pdf/ento_linguistics_combined.pdf`) |
| `_quality_report.py` | Thin Orchestrator | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | Quality report JSON (defaults: `docs/manuscript`, `output/reports`) |
| `_register_manuscript_figures.py` | Registry sync from actual PNGs | `src/visualization/figure_manager.py` | `output/figures/figure_registry.json` |
| `_render_pdf_override.py` | Thin Orchestrator | `src/pipeline/rendering.py` | `output/pdf/ento_linguistics_combined.pdf` |
| `_scientific_simulation.py` | Demo driver | `src/pipeline/simulation.py`, `src/data/data_generator.py` | Simulation outputs |

## Design Contract

- Scripts are orchestration only: path bootstrap, argparse/logging, and module entrypoint invocation.
- Data/model/plot logic lives in `src/`.
- All reusable script behavior must be covered by tests in `tests/`.
- Manually-run helpers are prefixed `_` and are **not** auto-discovered by the pipeline (which runs `01_build_corpus.py` and `02_generate_figures.py`).
- Failures are explicit: scripts must not silently fall back when imports, paths, or registration steps fail.

## What Scripts Do / Don't Do

**Do**: import from `src/`, orchestrate data flow, handle file I/O and directory management, configure logging.

**Don't**: implement mathematical algorithms, duplicate business logic, contain complex computations.

## See Also

- [`README.md`](README.md) — script inventory with commands
- [`../src/AGENTS.md`](../src/AGENTS.md) - Available src/ modules
- [`../src/pipeline/AGENTS.md`](../src/pipeline/AGENTS.md) — pipeline stage modules
- [`../AGENTS.md`](../AGENTS.md) - Project documentation
