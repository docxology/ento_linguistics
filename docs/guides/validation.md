# Validation guide

[Documentation](../README.md) → Validation guide

Run from the repository root after installing development dependencies and NLTK resources.

~~~bash
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m research.network_reading.study --root .
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

Keep tests and regeneration sequential: some historical tests inspect generated artifacts. Development and manuscript builds must use the same source snapshot. The full analysis command regenerates figures and small data exports, preserves fingerprint-checked expensive caches, and rebuilds auxiliary source layers when their inputs or implementation change.

## Gates and failure controls

The configured floor is 90% combined statement/branch coverage. Report branch-only coverage separately rather than treating this floor as a separate branch threshold. Focused tests alone do not establish whole-suite coverage.

*tests/test_loader.py* rejects non-text and empty records. Full-text cache tests edit actual corpus text while retaining metadata and record count, verify bounded-run reuse, reject invalid limits, and ensure bounded artifacts do not satisfy a full run. *tests/test_provenance.py* rejects missing receipts, changed source/output content, altered file inventories and falsified resource hashes. *tests/test_nltk_resources.py* uses real installed files and fresh subprocesses to reject missing, empty, and whitespace-only resources and detect changed tokenizer bytes. *tests/test_review_controls.py* checks the optimized literal counter against a separate non-overlapping matcher and verifies a real failing renderer subprocess cannot be masked by an old PDF.

The analysis manifest is written only after required stages, variable coverage and manuscript figure checks. It binds corpus JSON, data JSON, figures and registry to the implementation, dependency lock and selected English NLTK resource contents. Missing resources fail; changed tokenizer/dictionary bytes invalidate cache and receipt signatures. The receipt records the resource hashes without vendoring them. Rendering validates the manifest before invoking Pandoc, XeLaTeX and BibTeX. Any nonzero toolchain exit fails, and final unresolved references/citations or missing glyphs fail.

## Manual artifact checks

Inspect all registered figures for faithful labels, readable text, non-fabricated zeros, and stated sampling. Confirm plotted means and manuscript values against JSON. Render PDF pages with Poppler and inspect layouts, reference tables and figures; text extraction alone cannot verify visual quality.

The custody audit reports all stored records and explicit gaps. It does not silently repair or fabricate provenance. A zero process exit does not establish that every source is relevant, fully reconciled, or licensed for redistribution.

Use *output/reports/corpus_audit.json*, *output/figures/figure_registry.json*, *output/data/analysis_manifest.json* and the run logs as the evidence trail. The [verification reference](../reference/verification.md) identifies the captured results and their scope.

## Rasterize a paper for inspection

~~~bash
mkdir -p output/pdf/pages
pdftoppm -png -scale-to 1600 output/pdf/ento_linguistics_combined.pdf output/pdf/pages/page
pdfinfo output/pdf/ento_linguistics_combined.pdf
~~~

Inspect every page and any small figure at higher resolution. Check the final TeX log for missing glyphs, undefined references/citations, overfull boxes, and oversized floats. File size, text extraction, or a green subprocess alone cannot establish a readable figure.

Historical generic reports elsewhere in output/reports/ may describe an earlier template build. Use the matching analysis manifest and current run logs rather than inferring freshness from their filenames.
