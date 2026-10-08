# Manuscript source

[Documentation](../README.md) → Manuscript

This directory is the canonical source for [Ento-Linguistics v1.3.0](../../Ento_Linguistics_manuscript.pdf). The Markdown retains computational placeholders; the built PDF resolves them from verified core and extension exports. The current edition adds a graphical abstract, vocabulary/threshold sensitivity methods and source-checked Complexity / Complex Systems framing.

[The v1.3.0 GitHub release](https://github.com/docxology/ento_linguistics/releases/tag/v1.3.0) identifies the matched paper and lecture artifacts. The [v1.2.1 DOI](https://doi.org/10.5281/zenodo.23215452) retains the earlier archived paper and media identity; it is not the DOI of the new edition.

## Reading map

| Part | Sections |
| --- | --- |
| Research question | [Abstract](01_abstract.md), [introduction](02_introduction.md) |
| Methods | [Main methods](03_methods.md), [text and extraction](S01a_text_and_extraction.md), [statistical infrastructure](S01b_analysis_infrastructure.md) |
| Results | [Corpus and networks](04a_corpus_and_networks.md), [domain findings](04b_domain_findings.md), [supplemental results](S02_supplemental_results.md) |
| Interpretation | [Discussion](05_discussion.md), [conclusion](06_conclusion.md), [related work](07_related_work.md) |
| Proposed extensions | [Theoretical extensions](S03a_theoretical_extensions.md), [case studies and validation agenda](S03b_case_studies.md) |
| Supporting material | [Acknowledgments](08_acknowledgments.md), [glossary](98_symbols_glossary.md), [references](99_references.md) |

The renderer orders main sections, supplements, glossary, then bibliography. README.md and AGENTS.md are documentation, not paper sections.

## Build and edit

Follow [manuscript authoring](../guides/authoring.md) for variables, captions, equations, and citations. The active configuration is [config.yaml](config.yaml); [references.bib](references.bib) and [preamble.tex](preamble.tex) provide bibliography and styling.

From the repository root, after valid core and network-reading generation:

~~~bash
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

The output is output/pdf/ento_linguistics_combined.pdf. The renderer validates the analysis receipt before resolving placeholders and requires successful toolchain execution. Inspect the final PDF before replacing the published top-level copy.

[Data lineage](../reference/data-lineage.md) traces values to exports. [Reproducibility](../reference/reproducibility.md) distinguishes measured proxies, bounded analyses, proposed theory, and unperformed human validation. [Verification and publication](../reference/verification.md) identifies the published revision.
