# scripts/ - Thin Orchestrators

## Purpose

The `scripts/` directory contains **thin orchestrators** that integrate with `src/` modules. Scripts handle argparse, path bootstrap, logging, and a single delegated call into a `src/` entrypoint — they never implement business logic themselves.

## Script Inventory

| Script | Pattern | Delegates to | Output |
|--------|---------|--------------|--------|
| `01_build_corpus.py` | Stage 01 Thin Orchestrator | `src/pipeline/corpus_build.py` | `data/corpus/abstracts.json`, `output/data/corpus_statistics.json` |
| `02_generate_figures.py` | Stage 02 Thin Orchestrator | `src/visualization/manuscript_figures.py` | 11 PNGs in `output/figures/`, JSONs in `output/data/`, filled manuscript variables |
| `_analysis_pipeline.py` | End-to-end orchestrator (corpus → figures → preflight) | the three scripts above | Stage sequencing, dry-run and stage selection |
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

## Keep / Delete / Move Verdicts (remediation wave 2, 2026-09-14)

| Former script | Verdict | Rationale |
|---------------|---------|-----------|
| `_generate_missing_figures.py` | **DELETED** | Imported a non-existent module (`generate_research_figures`) and duplicated `02_generate_figures.py` plotting. |
| `_generate_scientific_figures.py` | **DELETED** | Fully overlapped `02_generate_figures.py`; used unseeded RNG and referenced infrastructure/manuscript paths that could never resolve. |
| `_conceptual_mapping_script.py` (628 lines) | **MOVED** to `src/pipeline/conceptual_mapping_pipeline.py`; script is now a ~20-line wrapper. |
| `_discourse_analysis_script.py` (384 lines) | **MOVED** to `src/pipeline/discourse_pipeline.py`. |
| `_domain_analysis_script.py` (565 lines) | **MOVED** to `src/pipeline/domain_analysis_pipeline.py`. |
| `_generate_domain_figures.py` (628 lines) | **MOVED** to `src/pipeline/domain_figures.py`. |
| `_literature_analysis_pipeline.py` (718 lines) | **MOVED** to `src/pipeline/literature_pipeline.py`. |
| `01_build_corpus.py` (~90 lines of logic) | **MOVED** to `src/pipeline/corpus_build.py`; script is a thin wrapper. |
| `_analysis_pipeline.py` | **REWRITTEN** | All 7 stage commands referenced non-existent script names; now sequences the real stages `corpus` → `figures` → `preflight`. |
| `_register_manuscript_figures.py` | **REWRITTEN** | Dropped the hardcoded stale metadata table (with duplicate labels); figures are derived from actual PNGs in `output/figures/` merged with existing registry metadata; failures skip with a logged reason. |
| `_manuscript_preflight.py` / `_quality_report.py` | **FIXED** | Defaults now resolve from the project root (`docs/manuscript`, `output/reports`, `output/pdf/ento_linguistics_combined.pdf`); the silent `except Exception: reproducibility = {}` was replaced with explicit error aggregation. |

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
