# Standalone paper build

`ento_linguistics_combined.pdf` is the active unpublished 1.2.2-dev draft (49 pages in the recorded 8 October build). `temp_combined.md` is the resolved Markdown input written by the current renderer; generated TeX, bibliography and logs support its build. `_combined_manuscript.md` is a retained legacy snapshot navigation file, not the active renderer input.

Run `uv run python scripts/_render_pdf_override.py --strict-templates` after matching receipt validation. Inspect the final TeX diagnostics and rasterized pages. The top-level published PDF and external DOI/release are distinct; a local render does not replace them.

See [output map](../README.md), [workflow](../../docs/guides/workflow.md), [validation](../../docs/guides/validation.md), and [captured verification](../../docs/reference/verification.md).
