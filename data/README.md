# Stored research sources

The corpus has four separately analyzed layers:

| Layer | Source files | Provenance and analysis |
| --- | --- | --- |
| Headline abstracts | `corpus/abstracts.json` | Digest-indexed `corpus/provenance.json`; only identified PubMed strings enter headline results |
| PMC | `fulltexts/fulltexts_*.json` | Full-text records and associated provenance; includes notices and repeated boilerplate |
| BHL | `bhl/bhl_shard_*.json` | Historical mirror OCR, provenance, era counts, and analysis exports |
| arXiv | `corpus/arxiv_records.json` | Preprint records with nested source metadata; analyzed separately |

See [data lineage](../docs/reference/data-lineage.md) for output paths and selection boundaries. Derive counts and custody gaps from the current audit:

```bash
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
```

The audit checks source identity and artifact agreement. Relevance screening, article-type review, and reuse permissions require additional assessment. Preserve source strings and unresolved provenance rather than rewriting them to make counts agree.

For acquisition, use [the corpus guide](corpus/README.md); for reproduction, use [workflow](../docs/guides/workflow.md). Acquisition changes research inputs and requires affected analysis regeneration. Stored data and historical snapshots retain their source identities.
