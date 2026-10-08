# Pipeline maintenance

Follow [project guidance](../../AGENTS.md) and [source guidance](../AGENTS.md). [Module inventory](README.md) maps layer analyses, custody, recovery, helper workflows and rendering. Keep commands in thin scripts and reusable computation here.

For corpus, statistics or receipt changes, read [data lineage](../../docs/reference/data-lineage.md) and [reproducibility](../../docs/reference/reproducibility.md); reproduce with real inputs and inspect downstream callers. Preserve source-layer boundaries, ordered content identities and full/bounded cache distinctions. Completed checkpoints are recovery evidence, not final completion receipts.

For rendering changes, read [authoring](../../docs/guides/authoring.md). Verify failed subprocesses, stale receipts, missing extension results and unresolved-placeholder controls. `build_pdf` shells out to Pandoc/XeLaTeX/BibTeX; the maintained rendering script first ensures both network companions. Preserve canonical manuscript tokens and separately identify the unpublished draft and archived published PDF.

Packages import sibling names such as `analysis.*`, `core.*`, `data.*`, and `visualization.*`. Direct module commands need `PYTHONPATH=src`; scripts bootstrap that path and pytest config supplies it for tests. Run `uv run pytest tests/ --cov=src --cov-report=term-missing` sequentially with generation. Guide-only Markdown changes do not require corpus recomputation, but documented paths/interfaces and links must be checked.
