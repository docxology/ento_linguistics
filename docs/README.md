# Ento-Linguistics documentation

Current entry points are [repository README](../README.md), [validation guide](validation_guide.md), [reproducibility boundaries](reproducibility.md), and the [dated review evidence](review_20261005.md).

## Run the standalone project

~~~bash
uv sync --extra dev
uv run python -m nltk.downloader -d .venv/nltk_data stopwords punkt_tab wordnet omw-1.4
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

Run testing and regeneration sequentially. The manuscript renderer requires a completed content receipt; a resolved placeholder alone does not establish source freshness.

## Evidence sources

| Artifact | Role |
|----------|------|
| *output/reports/corpus_audit.json* | Source custody and explicit metadata gaps |
| *output/data/statistical_analysis.json* | Abstract-layer valid entropy, heuristic scores and exploratory comparisons |
| *output/data/fulltext_analysis.json* | All stored PMC records by default, with explicit discourse sampling |
| *data/corpus/arxiv_analysis.json* | Separate preprint analysis |
| *data/bhl/era_term_usage.json* | Complete literal frequencies, streamed extraction/framing, bounded term entropy, and recorded coverage |
| *output/figures/figure_registry.json* | Generated figure registration |
| *output/data/analysis_manifest.json* | Implementation, corpus and output content binding |
| *output/pdf/ento_linguistics_combined.pdf* | Rendered manuscript after strict checks |

The six-domain taxonomy, lexical markers, context clustering and CACE scores are inspectable methods rather than independent validation of language effects. See the methods and limitations in [the manuscript](manuscript/03_methods.md).

Historical documents in this directory describe earlier corpus snapshots and template-based workflows. Their fixed counts, old parent-template commands, and earlier review verdicts must not be treated as current validation. Use the artifact definitions above and the dated report for the current standalone repository.
