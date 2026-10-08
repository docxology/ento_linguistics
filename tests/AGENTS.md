# Test maintenance

Follow [project guidance](../AGENTS.md) and [development](../docs/guides/development.md). Tests exercise real numerical examples, files, subprocesses, corpus slices, images, and local HTTP. Mocking frameworks are prohibited. Use `tmp_path` for isolation and fixed seeds where algorithms are stochastic.

## Run and interpret checks

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run pytest tests/test_rendering.py tests/test_concept_visualization.py --no-cov
uv run pytest tests/integration/ --no-cov -v
uv run pytest tests/ --collect-only -q
```

Run generation and tests sequentially. The configured floor is **90% combined statement/branch coverage across measured source**, not 90% for every module or a branch-only floor. Focused subsets do not establish whole-suite coverage. The renderer does not run the suite automatically. Record actual pass/skip/warning counts and source identity; see [captured verification](../docs/reference/verification.md). Eight external parent-template cases skipped in the latest recorded full run; do not count them as exercised standalone behavior. Runtime depends on inputs, resources and machine; the complete suite is not a sub-30-second check.

## Add meaningful controls

Reproduce the failure before changing implementation. Compare numerical results with an independent expected value or oracle, rather than another call to the same implementation. Check invalid input and legitimate zeros separately. For acquisition, use real local HTTP and verify request arguments, pagination, retained records and failures. For caching/provenance, change bytes while retaining metadata, tamper actual receipts/resources, and verify rejection.

For plotting, inspect intended plotted values/labels and decoded pixels; file existence alone does not verify correct values or readable geometry. For rendering, invoke real Pandoc or a real failing subprocess and ensure an old PDF cannot mask failure. Preserve failing logs before successful corrections. [Validation](../docs/guides/validation.md) defines the receipt and manual page/figure checks.

Use behavior-based names such as `test_rejects_missing_receipt`. Avoid exact incidental prose pins, implementation-only assertions, empty test bodies, and tests that merely repeat the production formula. Public APIs and error paths need real evidence.

## Scope

[Test inventory](README.md) maps maintained packages and cross-cutting controls. [Integration guidance](integration/AGENTS.md) covers temporary workflow trees and external-template cases. Read [source guidance](../src/AGENTS.md) before changing computation. Source changes require matching generation/receipt/render checks; Markdown guidance changes alone do not alter scientific analysis or the paper.
