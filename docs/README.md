# Ento-Linguistics Project Documentation

Reference materials and guides for the **Ento-Linguistic Domains** research project — studying how entomological metaphors permeate and shape scientific discourse across six analytical domains.

## Key Documents

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Technical overview of every doc in this directory |
| [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md) | Review summary and completed coherence edits |
| [development_workflow.md](development_workflow.md) | Environment setup, test commands, script names, module paths |
| [manuscript_data_lineage.md](manuscript_data_lineage.md) | Mappings of how `src/` modules populate `manuscript/` contents |
| [manuscript_style_guide.md](manuscript_style_guide.md) | Figures, citations, equations, and cross-reference examples from the actual manuscript |
| [refactor_playbook.md](refactor_playbook.md) | Module dependency map, hotspots, and safe-change recipes |
| [standards_compliance.md](standards_compliance.md) | Compliance matrix, live corpus table (synced to `output/data/*.json`), PDF template workflow |
| [testing_expansion_plan.md](testing_expansion_plan.md) | Targeted testing additions across 38 test files |
| [validation_guide.md](validation_guide.md) | Preflight, figure, and manuscript validation commands |

### PDF rendering and template variables

The project PDF is built by [`scripts/_render_pdf_override.py`](../scripts/_render_pdf_override.py) (not the generic template `03_render_pdf.py` alone). It concatenates the manuscript files listed in that script, substitutes every `{{KEY}}` using `_load_corpus_vars()` (JSON under `data/corpus/` and `output/data/`), then runs Pandoc and XeLaTeX. Use `--strict-templates` or `STRICT_TEMPLATE_VARS=1` so an unresolved placeholder fails the build. Variable catalog: [`../manuscript/README.md`](../manuscript/README.md) and [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md). Lineage: [manuscript_data_lineage.md](manuscript_data_lineage.md).

## Quick Access

```bash
# Run the full test suite
uv run pytest tests/ -x -q

# Clean-slate figure regeneration (clears output/, rebuilds all 11 figures)
uv run python scripts/02_generate_figures.py

# Build corpus (stage 1)
uv run python scripts/01_build_corpus.py

# Validate manuscript figures and references
uv run python scripts/_manuscript_preflight.py --strict

# Run the full analysis pipeline
uv run python scripts/_analysis_pipeline.py
```

## Project Architecture

```text
src/
├── analysis/          # term_extraction, text_analysis, semantic_entropy, cace_scoring,
│                      # discourse_analysis, discourse_patterns, domain_analysis,
│                      # conceptual_mapping, persuasive_analysis, rhetorical_analysis,
│                      # statistics, performance
├── core/              # exceptions, logging, metrics, parameters, validation,
│                      # validation_utils, markdown_integration, example
├── data/              # literature_mining, loader, data_generator, data_processing
├── pipeline/          # simulation, reporting
└── visualization/     # concept_visualization, statistical_visualization, figure_manager,
                       # plots, visualization
```

## Live Pipeline Stats

Representative counts from `output/data/*.json` and `data/corpus/abstracts.json` after a full analysis run (re-run pipeline to refresh). The PDF manuscript does not embed these as literals—it uses `{{KEY}}` substitution at build time (see [standards_compliance.md](standards_compliance.md)).

| Metric | Value |
|--------|-------|
| Figures generated | 11 |
| Publications (abstracts) | 369 |
| Tokens | 48,787 |
| Unique token types | 7,105 |
| Extracted terms (candidates) | 888 |
| Domain-assigned terms | 261 |
| Concept relationships | 9 |

## See Also

- [`../src/AGENTS.md`](../src/AGENTS.md) — Source code documentation
- [`../scripts/AGENTS.md`](../scripts/AGENTS.md) — Scripts documentation
- [`../tests/AGENTS.md`](../tests/AGENTS.md) — Test suite documentation
- [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md) — Manuscript structure
