# Pipeline modules

Importable workflow logic under the flat `pipeline` package. Run from the repository root with `src/` on the import path; [scripts](../../scripts/README.md) bootstrap it for their delegated calls. Not every module has a one-to-one script: several source-layer stages are composed by the core figure generator.

| Module | Responsibility |
| --- | --- |
| `corpus_build.py` | Cached or live PubMed acquisition and headline statistics |
| `corpus_audit.py` | Stored source custody and optional analysis-manifest validation |
| `statistics_pipeline.py` | Shared domain entropy/CACE samples and exploratory statistics |
| `fulltext_pipeline.py` | Separate PMC layer, framing and bounded discourse analysis |
| `bhl_analysis.py` | Historical literal frequencies and era analysis |
| `bhl_artifact.py` | Content-bound BHL cache and completed-era checkpoint recovery |
| `arxiv_analysis.py` | Separate preprint layer |
| `conceptual_mapping_pipeline.py` | Concept-map and terminology-network helper workflow |
| `discourse_pipeline.py` | Discourse helper workflow |
| `domain_analysis_pipeline.py` | Per-domain analysis and reports |
| `domain_figures.py` | Per-domain helper figures |
| `literature_pipeline.py` | Literature retrieval/analysis helper workflow |
| `rendering.py` | Receipt-bound strict Pandoc/XeLaTeX/BibTeX paper build |
| `reporting.py` | Report formatting and error aggregation |
| `simulation.py` | Synthetic simulation framework used by demos/tests |

Maintained paper commands and their scope are in [workflow](../../docs/guides/workflow.md). The primary generator is `visualization.manuscript_figures`, called by `scripts/02_generate_figures.py`. Rendering is `scripts/_render_pdf_override.py --strict-templates`; its script also ensures both fixed-margin companion protocols. Calling `build_pdf` directly requires those companions to exist and validate.

For direct imports, use `PYTHONPATH=src uv run python ...`. `corpus_build.main(project_root=Path(...))` delegates corpus processing; never run acquisition merely to test imports. Read [maintenance](AGENTS.md), [lineage](../../docs/reference/data-lineage.md), and [reproducibility](../../docs/reference/reproducibility.md) before changing measurements or inputs.
