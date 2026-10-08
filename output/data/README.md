# Core analysis exports

The generator writes corpus/domain statistics, extracted terms, concept-map summaries, full-text analysis and statistical analysis here. `analysis_manifest.json` binds actual corpus/export/figure inventory, source implementation, dependency lock and selected NLTK contents. It is written only after required stages pass.

Regenerate with `uv run python scripts/02_generate_figures.py`; validate the content manifest before rendering. Do not hand-edit derived numerical results or forge matching receipt hashes.

See [output map](../README.md), [workflow](../../docs/guides/workflow.md), [validation](../../docs/guides/validation.md), and [captured verification](../../docs/reference/verification.md).
