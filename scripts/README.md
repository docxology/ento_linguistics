# scripts/ — Thin Orchestrators

## Overview

Scripts are **thin orchestrators**: they set up paths, parse arguments, configure
logging, and make a single delegated call into a `src/` entrypoint. All business,
data, plotting, and analysis logic lives exclusively in `src/` (importable and
tested). Scripts never implement algorithms themselves, and they never fail
silently.

## Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `01_build_corpus.py` | Build/refresh the literature corpus (cached; `--force` re-fetches) | `src/pipeline/corpus_build.py` | `uv run python scripts/01_build_corpus.py` |
| `02_generate_figures.py` | **Main entry point** — clean slate, regenerate all 11 figures + data, fill manuscript variables | `src/visualization/manuscript_figures.py` | `uv run python scripts/02_generate_figures.py` |
| `_analysis_pipeline.py` | End-to-end run: corpus → figures → preflight (stage selection + dry run) | the three scripts above | `uv run python scripts/_analysis_pipeline.py [--stages corpus figures preflight] [--dry-run]` |
| `_conceptual_mapping_script.py` | Concept mapping and network generation | `src/pipeline/conceptual_mapping_pipeline.py` | `uv run python scripts/_conceptual_mapping_script.py` |
| `_convert_corpus.py` | Convert literature corpus JSON to plain abstracts list | `src/data/loader.py` (`convert_corpus`) | `uv run python scripts/_convert_corpus.py` |
| `_discourse_analysis_script.py` | Discourse pattern analysis | `src/pipeline/discourse_pipeline.py` | `uv run python scripts/_discourse_analysis_script.py` |
| `_domain_analysis_script.py` | Domain-specific terminology analysis | `src/pipeline/domain_analysis_pipeline.py` | `uv run python scripts/_domain_analysis_script.py [domain]` |
| `_example_figure.py` | Example figure generation (self-contained demo; fails loudly) | `src/core/logging`, `src/visualization/figure_manager` | `uv run python scripts/_example_figure.py` |
| `_fill_manuscript_variables.py` | Fill `{{VAR}}` placeholders in manuscript markdown | `src/core/manuscript_variables.py` | `uv run python scripts/_fill_manuscript_variables.py` |
| `_generate_domain_figures.py` | Per-domain frequency and ambiguity figures | `src/pipeline/domain_figures.py` | `uv run python scripts/_generate_domain_figures.py [domain]` |
| `_literature_analysis_pipeline.py` | Full literature mining + analysis | `src/pipeline/literature_pipeline.py` | `uv run python scripts/_literature_analysis_pipeline.py` |
| `_manuscript_preflight.py` | Validate figure refs, glossary, bibliography | `src/core/validation_utils.py` | `uv run python scripts/_manuscript_preflight.py --strict` |
| `_quality_report.py` | Readability, integrity, reproducibility snapshot | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | `uv run python scripts/_quality_report.py` |
| `_register_manuscript_figures.py` | Sync `figure_registry.json` from actual PNGs in `output/figures/` | `src/visualization/figure_manager.py` | `uv run python scripts/_register_manuscript_figures.py` |
| `_render_pdf_override.py` | Combined PDF via Pandoc/XeLaTeX; `{{KEY}}` substitution | `src/pipeline/rendering.py` | `uv run python scripts/_render_pdf_override.py --strict-templates` |
| `_scientific_simulation.py` | Simulation workflows | `src/pipeline/simulation.py`, `src/data/data_generator.py` | `uv run python scripts/_scientific_simulation.py` |

## Deleted Scripts (remediation wave 2, 2026-09-14)

| Script | Verdict | Reason |
|--------|---------|--------|
| `_generate_missing_figures.py` | Deleted | Imported a non-existent module and duplicated `02_generate_figures.py`. |
| `_generate_scientific_figures.py` | Deleted | Overlapped `02_generate_figures.py`; unseeded RNG; paths that could never resolve. |

Analysis/report/plot logic from `_conceptual_mapping_script.py`,
`_discourse_analysis_script.py`, `_domain_analysis_script.py`,
`_generate_domain_figures.py`, `_literature_analysis_pipeline.py`, and
`01_build_corpus.py` moved into `src/pipeline/` (see
[`../src/pipeline/AGENTS.md`](../src/pipeline/AGENTS.md)); each script is now a
thin wrapper.

## Notes

> `02_generate_figures.py` wipes `output/figures/` and `output/data/` on every
> run, then regenerates all outputs from scratch.
>
> `_manuscript_preflight.py` and `_quality_report.py` default to
> `docs/manuscript` and derive all other paths from the project root, not the
> CWD. The rendered PDF artifact is `output/pdf/ento_linguistics_combined.pdf`.

## Thin Orchestrator Pattern

```python
# Scripts do this (with src/ on PYTHONPATH):
from visualization.manuscript_figures import main

main(project_root=project_root)   # business logic in src/
```

Scripts **never** implement algorithms or mathematical computations directly.

## See Also

- [`AGENTS.md`](AGENTS.md) — thin-orchestrator contract and keep/delete verdicts
- [`../src/AGENTS.md`](../src/AGENTS.md) — available `src/` modules
- [`../docs/development_workflow.md`](../docs/development_workflow.md) — commands and workflow
