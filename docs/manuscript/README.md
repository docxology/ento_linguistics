# Manuscript authoring and rendering

The canonical manuscript is the numbered Markdown sections in this directory, with supplemental sections, glossary, references, BibTeX, publication configuration, and TeX preamble. The standalone renderer owns their explicit order.

## Build from the repository root

~~~bash
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

The PDF is *output/pdf/ento_linguistics_combined.pdf*. Pandoc, XeLaTeX, and BibTeX must execute successfully. Tests and analysis generation should run sequentially. See [the repository README](../../README.md) for dependency and NLTK setup.

## Editing rules

Keep computed numbers as double-brace placeholders resolved by *src/core/manuscript_variables.py* and *src/pipeline/rendering.py*. Statistical exports and domain figures use the same valid sentence-context entropy estimates. A multi-domain term contributes to several domain memberships.

Use bibliography keys from *references.bib*. Both Pandoc citation syntax and the existing LaTeX natbib commands are supported. Keep section and figure labels stable and ensure referenced PNG files are generated and registered. Main sections precede supplements, then glossary and references.

Source changes require analysis regeneration. Manuscript-only edits require another strict PDF build. The renderer validates the content receipt before substituting values and rejects unresolved placeholders, failed toolchain commands, undefined citations/references, and missing glyphs.

## Interpretation

The headline analysis excludes unreconciled legacy strings but preserves the original archive. Retrieval is broad rather than a curated ant-only selection. BHL extraction, framing, and literal rates use all stored documents by default; entropy uses twenty frequent candidates per era. PMC discourse and domain CACE use explicit bounds.

Report these software measurements as descriptive proxies. Do not convert shared-domain labels into semantic drift, predefined categories into discovered ontology, default scores into evidence of clarity, or exploratory tests into calibrated causal conclusions. Theoretical sections describe proposed models, not fitted or measured quantities.

Current evidence and remaining limits are documented in [the dated review](../review_20261005.md) and [reproducibility guide](../reproducibility.md). Existing version and DOI identify prior publication metadata; this local revision is not a new published release.
