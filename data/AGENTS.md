# Corpus maintenance

Follow [project standards](../AGENTS.md). Preserve source text, identifiers, retrieval metadata, digest-indexed sidecars, and unresolved associations. Acquisition and analysis are different operations: inspect `scripts/01_build_corpus.py --help` before changing input data, then regenerate affected analyses and validate receipts.

Read [data lineage](../docs/reference/data-lineage.md) for the separate PubMed, PMC, BHL OCR, and arXiv layers. Source identity is distinct from relevance and reuse permission. Inspect [corpus guidance](corpus/AGENTS.md) before changing headline selection or provenance.

Use real-input tests and explicit custody checks. Never invent missing metadata or silently replace archived strings. Bounded development selections require separate fingerprints and coverage descriptions.
