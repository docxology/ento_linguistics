# Manuscript source

[Documentation](../README.md) → Manuscript

This directory is the canonical source for the [current unpublished draft](../../output/pdf/ento_linguistics_combined.pdf). The Markdown deliberately retains computational placeholders; read the built PDF for resolved numbers. The [published paper](../../Ento_Linguistics_manuscript.pdf) is an archived release, not a render of every later edit.

The working source is **1.2.2-dev**, an unpublished revision with editorial, figure and rendering corrections. The linked top-level PDF and [v1.2.1 DOI](https://doi.org/10.5281/zenodo.23215452) identify the archived publication, not this revised source. Read the locally rendered PDF for the updated argument and bibliography.

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

From the repository root, after valid analysis generation:

~~~bash
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

The output is output/pdf/ento_linguistics_combined.pdf. The renderer validates the analysis receipt before resolving placeholders and requires successful toolchain execution. Inspect the final PDF before replacing the published top-level copy.

[Data lineage](../reference/data-lineage.md) traces values to exports. [Reproducibility](../reference/reproducibility.md) distinguishes measured proxies, bounded analyses, proposed theory, and unperformed human validation. [Verification and publication](../reference/verification.md) identifies the published revision.
