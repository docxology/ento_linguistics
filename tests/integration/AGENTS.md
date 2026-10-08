# Integration-test maintenance

Follow [project standards](../../AGENTS.md) and [test guidance](../AGENTS.md). Use real temporary files, subprocesses, corpus slices, and local HTTP servers; seed numerical examples and verify independent expected values. Include failure cases that demonstrably reject invalid inputs.

Run integration tests with `uv run pytest tests/integration/ -v`; run full coverage with `uv run pytest tests/ --cov=src --cov-report=term-missing`. Keep tests and generation sequential. Report external parent-template skips explicitly and distinguish integration-subset execution from full-suite coverage.

Derive current figure inventory from `output/figures/figure_registry.json` and test counts from collection or the matching run. A decoded image is not proof of visual correctness. See [validation](../../docs/guides/validation.md) for receipt and paper checks, and [verification](../../docs/reference/verification.md) for captured publication evidence.

When changing pipeline behavior, inspect [source guidance](../../src/AGENTS.md) and [script interfaces](../../scripts/README.md). Keep mathematical and analysis logic in source modules rather than test drivers or scripts.
