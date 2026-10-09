# Headline abstracts and preprint records

`abstracts.json` is the ordered archive of abstract strings. Digest-indexed `provenance.json` records retrieved PubMed metadata, including identifiers and query information where available. Headline analysis selects source-identified strings; unreconciled strings remain archived and excluded. Exact-text provenance recovery establishes identity, not topical relevance. Two reconciliation passes over the original strings are recorded under `_reconciliation` in `provenance.json`; near matches are not admitted.

`arxiv_records.json` retains a separate preprint layer. Its records and analysis are not merged into the headline abstract list. OpenAlex enrichment adds citation metadata where available; it is not an additional corpus of analyzed article text. Historical snapshots and retrieval sidecars retain acquisition history.

## Inspect the stored corpus

Run from the repository root:

```bash
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
```

Read `output/reports/corpus_audit.json` for current record counts, digest gaps, duplicate text, and identifier disagreement. A digest-keyed mapping may collapse distinct records with identical text; matching row totals alone do not establish custody.

## Acquisition and reproduction

```bash
uv run python scripts/01_build_corpus.py --help
uv run python scripts/02_generate_figures.py
uv run python scripts/_render_pdf_override.py --strict-templates
```

Inspect acquisition options before choosing force or growth modes, which can perform live retrieval and change research inputs. Executable query definitions live in `src/pipeline/corpus_build.py` and `src/data/literature_mining.py`; cumulative archived retrieval is not reconstructed by one illustrative query. After input changes, regenerate affected artifacts, inspect custody, and render the paper against fresh receipts.

Use [setup](../../docs/guides/setup.md) and [workflow](../../docs/guides/workflow.md) for dependencies, resources, caching, and bounded development. The [reproducibility reference](../../docs/reference/reproducibility.md) explains convenience sampling, relevance, extraction thresholds, and license limits. Current publication counts belong to the matching release, not a permanent corpus specification.
