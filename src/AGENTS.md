# Source maintenance

Follow [project standards](../AGENTS.md). [Source architecture](README.md) maps the five packages and maintained entry points. Read the affected package's AGENTS.md before changes; keep scripts thin and reusable computation in source modules.

Reproduce defects with real text, files, HTTP servers, subprocesses, or independent numerical examples. Inspect callers before changing interfaces. Public APIs require type hints and documented success and failure behavior. Use fixed seeds and negative controls; never swallow required-stage errors.

For extraction, statistics, framing, CACE, network, or resource changes, read [data lineage](../docs/reference/data-lineage.md) and [reproducibility](../docs/reference/reproducibility.md). Regenerate affected analyses, verify receipts, inspect figures, and render the paper strictly. Corpus/input identity and software consistency do not establish relevance, licensing, sense annotation, causal effects, or calibrated heuristic scores.

For renderer or manuscript-variable changes, use [authoring](../docs/guides/authoring.md) and real subprocess failure controls in `tests/test_rendering.py`. Preserve numerical placeholders in paper source; report missing and unavailable results explicitly.

Run `uv run pytest tests/ --cov=src --cov-report=term-missing` sequentially with generation. The floor is 90% combined statement/branch coverage. Consult [verification](../docs/reference/verification.md) for captured run evidence rather than copying static test counts.
