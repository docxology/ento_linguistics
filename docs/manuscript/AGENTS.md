# Manuscript maintenance

For a paper edit, read [authoring](../guides/authoring.md). For methods, results, or captions, also read [data lineage](../reference/data-lineage.md) and [reproducibility](../reference/reproducibility.md).

Keep numbered section paths stable. The standalone renderer selects the paper sections explicitly; main sections precede supplements, glossary, and bibliography. README.md and this file are navigation/maintenance guidance, not rendered content.

- Computed quantities remain supported double-brace tokens resolved from project exports; preserve valid zero values and explicit unavailable estimates.
- Figure references resolve to registered, decoded PNGs whose captions disclose the plotted sample and measure.
- Distinguish observed terminology co-occurrence from predefined concept categories, occupancy entropy from validated word senses, and heuristic CACE/framing from human judgments.
- Describe theoretical extensions as proposals unless the pipeline actually fits or measures them.
- Cite verified primary bibliographic metadata through references.bib and existing citation keys.
- Keep publication metadata in config.yaml and styling in preamble.tex.

After paper content changes, validate the matching analysis receipt, render with --strict-templates, inspect final toolchain diagnostics and PDF pages, and compare displayed values with exports. Editing this guidance or README alone does not change the paper.
