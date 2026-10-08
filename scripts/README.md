# scripts/ — Thin Orchestrators

## Overview

Scripts are **thin orchestrators**: they set up paths, parse arguments, configure
logging, and make a single delegated call into a `src/` entrypoint. Reusable business,
data, plotting, and analysis logic lives in `src/` (importable and
tested). The standalone renderer is the paper acceptance path; several older report/preflight helpers retain optional parent-template validation, which must be reported as unavailable when absent.

## Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `01_build_corpus.py` | Build/refresh the literature corpus (cached; `--force` re-fetches) | `src/pipeline/corpus_build.py` | `uv run python scripts/01_build_corpus.py` |
| `02_generate_figures.py` | **Main entry point** — regenerate registered core figures and data, validate manuscript variables | `src/visualization/manuscript_figures.py` | `uv run python scripts/02_generate_figures.py` |
| `_analysis_pipeline.py` | End-to-end run: corpus → figures → preflight (stage selection + dry run) | the three scripts above | `uv run python scripts/_analysis_pipeline.py [--stages corpus figures preflight] [--dry-run]` |
| `_conceptual_mapping_script.py` | Concept mapping and network generation | `src/pipeline/conceptual_mapping_pipeline.py` | `uv run python scripts/_conceptual_mapping_script.py` |
| `_convert_corpus.py` | Convert literature corpus JSON to plain abstracts list | `src/data/loader.py` (`convert_corpus`) | `uv run python scripts/_convert_corpus.py` |
| `_discourse_analysis_script.py` | Discourse pattern analysis | `src/pipeline/discourse_pipeline.py` | `uv run python scripts/_discourse_analysis_script.py` |
| `_domain_analysis_script.py` | Domain-specific terminology analysis | `src/pipeline/domain_analysis_pipeline.py` | `uv run python scripts/_domain_analysis_script.py [domain]` |
| `_example_figure.py` | Example figure generation (self-contained demo; fails loudly) | `src/core/logging`, `src/visualization/figure_manager` | `uv run python scripts/_example_figure.py` |
| `_fill_manuscript_variables.py` | Validate `{{VAR}}` placeholder coverage in manuscript markdown (dry run only — substitution happens at PDF build; in-place baking is prohibited) | `src/core/manuscript_variables.py` | `uv run python scripts/_fill_manuscript_variables.py` |
| `_generate_domain_figures.py` | Per-domain frequency and ambiguity figures | `src/pipeline/domain_figures.py` | `uv run python scripts/_generate_domain_figures.py [domain]` |
| `_literature_analysis_pipeline.py` | Full literature mining + analysis | `src/pipeline/literature_pipeline.py` | `uv run python scripts/_literature_analysis_pipeline.py` |
| `_manuscript_preflight.py` | Validate figure refs, glossary, bibliography | `src/core/validation_utils.py` | `uv run python scripts/_manuscript_preflight.py --strict` |
| `_quality_report.py` | Readability, integrity, reproducibility snapshot | `src/pipeline/reporting.py`, `src/core/validation_utils.py` | `uv run python scripts/_quality_report.py` |
| `_register_manuscript_figures.py` | Sync `figure_registry.json` from actual PNGs in `output/figures/` | `src/visualization/figure_manager.py` | `uv run python scripts/_register_manuscript_figures.py` |
| `_render_pdf_override.py` | Combined PDF via Pandoc/XeLaTeX; `{{KEY}}` substitution | `src/pipeline/rendering.py` | `uv run python scripts/_render_pdf_override.py --strict-templates` |
| `_scientific_simulation.py` | Simulation workflows | `src/pipeline/simulation.py`, `src/data/data_generator.py` | `uv run python scripts/_scientific_simulation.py` |

## Execution and outputs

`02_generate_figures.py` rebuilds the managed `output/figures/` and `output/data/` directories. Expensive source-layer analyses can reuse matching fingerprints and completed BHL-era checkpoints. Preserve evidence outside those directories before a deliberate cold recomputation. See [workflow](../docs/guides/workflow.md).

`_manuscript_preflight.py` and `_quality_report.py` default to `docs/manuscript` and resolve paths from the project root. Numerical placeholders remain in Markdown and resolve during rendering. `_render_pdf_override.py` validates the fixed-margin companions and the separately recomputed network-reading report and writes `output/pdf/ento_linguistics_combined.pdf`.

The fixed-margin extension is implemented in [research/network_robustness/](../research/network_robustness/README.md), with its own receipts and figure. It is separate from the core figure generator.

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
- [`../docs/guides/development.md`](../docs/guides/development.md) — commands and workflow

## Helper limitations

`_manuscript_preflight.py --strict` gates missing figures, glossary markers and reference boilerplate; it does not turn every optional infrastructure diagnostic into a hard failure. `_quality_report.py` may report skipped parent-template quality/reproducibility checks. Their successful exits do not replace the standalone suite, manifest/extension validation or strict renderer. Use `--output-dir` to keep a new helper report separate from historical reports.

Use real commands rather than copying the illustrative square-bracket optional arguments literally. For direct layer CLIs, run `PYTHONPATH=src uv run python -m pipeline.bhl_analysis --help` or `-m pipeline.fulltext_pipeline --help`; individual layer execution alone does not refresh the complete manifest/figures.

Run `PYTHONPATH=src uv run python -m research.network_reading.study --root .` after core generation and before strict rendering when its source or consumed inputs changed. This module owns its separately receipted report, curves and graphical abstract.
