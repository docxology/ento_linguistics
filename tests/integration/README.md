# Integration tests

Run from the repository root with the locked development environment:

```bash
uv run pytest tests/integration/ -v
uv run pytest tests/ --cov=src --cov-report=term-missing
```

These tests exercise real module interactions, temporary project trees, corpus slices, and figure files. Some cases require an external parent-template checkout and skip when it is absent; a skip does not verify standalone behavior. The complete suite also contains corpus, provenance, numerical, renderer, and fixed-margin artifact controls outside this directory.

Keep generation and tests sequential because integration checks can consume generated exports. Numerical examples should use fixed seeds and independent expected values. Figure decoding and registry checks establish file integrity; inspect rendered figures and PDF pages separately for readability and accurate interpretation.

See [test guidance](../AGENTS.md), [development](../../docs/guides/development.md), and [captured verification](../../docs/reference/verification.md). The configured coverage floor applies to the complete measured source suite, not to this subset in isolation.
