# scripts/ — Thin Orchestrators

## Overview

Scripts are **thin orchestrators**: they set up paths, parse arguments, configure
logging, and make a single delegated call into a `src/` entrypoint. All business,
data, plotting, and analysis logic lives exclusively in `src/` (importable and
tested). Scripts never implement algorithms themselves.

## Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `01_build_corpus.py` | Build literature corpus from entomological sources | `src/data/literature_mining.py` | `uv run python scripts/01_build_corpus.py` |
| `02_generate_figures.py` | **Main entry point** — clean slate, regenerate all 11 figures + data, fill manuscript variables | `src/visualization/manuscript_figures.py` | `uv run python scripts/02_generate_figures.py` |
| `_analysis_pipeline.py` | Full analysis pipeline (all stages) | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | `uv run python scripts/_analysis_pipeline.py` |
| `_conceptual_mapping_script.py` | Concept mapping and network generation | `src/analysis/conceptual_mapping.py`, `src/visualization/concept_visualization.py` | `uv run python scripts/_conceptual_mapping_script.py` |
| `_convert_corpus.py` | Convert literature corpus JSON to plain abstracts list | `src/data/loader.py` (`convert_corpus`) | `uv run python scripts/_convert_corpus.py` |
| `_discourse_analysis_script.py` | Discourse pattern analysis | `src/analysis/discourse_analysis.py`, `src/visualization/concept_visualization.py` | `uv run python scripts/_discourse_analysis_script.py` |
| `_domain_analysis_script.py` | Domain-specific terminology analysis | `src/analysis/domain_analysis.py`, `src/visualization/figure_manager.py` | `uv run python scripts/_domain_analysis_script.py` |
| `_example_figure.py` | Example figure generation (self-contained demo) | — | `uv run python scripts/_example_figure.py` |
| `_fill_manuscript_variables.py` | Fill `{{VAR}}` placeholders in manuscript markdown | `src/core/manuscript_variables.py` | `uv run python scripts/_fill_manuscript_variables.py` |
| `_generate_domain_figures.py` | Per-domain frequency and ambiguity figures | `src/analysis/domain_analysis.py`, `src/visualization/figure_manager.py` | `uv run python scripts/_generate_domain_figures.py` |
| `_generate_missing_figures.py` | Regenerate any missing figures (stale import; see note) | `scripts/02_generate_figures.py` logic | `uv run python scripts/_generate_missing_figures.py` |
| `_generate_scientific_figures.py` | Scientific simulation figures | `src/visualization/plots.py`, `src/analysis/performance.py` | `uv run python scripts/_generate_scientific_figures.py` |
| `_literature_analysis_pipeline.py` | Full literature mining + analysis | `src/data/literature_mining.py`, `src/analysis/*` | `uv run python scripts/_literature_analysis_pipeline.py` |
| `_manuscript_preflight.py` | Validate figure refs, glossary, bibliography | `src/core/validation_utils.py` | `uv run python scripts/_manuscript_preflight.py --strict` |
| `_quality_report.py` | Readability, integrity, reproducibility snapshot | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | `uv run python scripts/_quality_report.py` |
| `_register_manuscript_figures.py` | Figure registry updates | `src/visualization/figure_manager.py` | `uv run python scripts/_register_manuscript_figures.py` |
| `_render_pdf_override.py` | Combined PDF via Pandoc/XeLaTeX; `{{KEY}}` substitution | `src/pipeline/rendering.py` | `uv run python scripts/_render_pdf_override.py --strict-templates` |
| `_scientific_simulation.py` | Simulation workflows | `src/pipeline/simulation.py`, `src/data/data_generator.py` | `uv run python scripts/_scientific_simulation.py` |

Notes:

> `02_generate_figures.py` wipes `output/figures/` and `output/data/` on every
> run, then regenerates all outputs from scratch.
>
> `_generate_missing_figures.py` imports a former script name
> (`generate_research_figures`) that no longer exists; use
> `02_generate_figures.py` instead.

## Thin Orchestrator Pattern

```python
# Scripts do this (with src/ on PYTHONPATH):
from visualization.manuscript_figures import main

main(project_root=project_root)   # business logic in src/
```

Scripts **never** implement algorithms or mathematical computations directly.

## See Also

- [`AGENTS.md`](AGENTS.md) — thin-orchestrator contract
- [`../src/AGENTS.md`](../src/AGENTS.md) — available `src/` modules
- [`../docs/development_workflow.md`](../docs/development_workflow.md) — commands and workflow
