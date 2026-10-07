# Documentation

Start with the [paper](../Ento_Linguistics_manuscript.pdf) for the research argument, or choose a task below. Commands in these guides run from the repository root.

## Guides: complete a task

| Guide | Use it to |
| --- | --- |
| [Setup](guides/setup.md) | Install Python dependencies, NLTK data, and the PDF toolchain |
| [Analysis workflow](guides/workflow.md) | Reproduce stored corpus analyses, use recovery checkpoints, and render the paper |
| [Validation](guides/validation.md) | Test software behavior, inspect source custody, and verify figures/PDFs |
| [Development](guides/development.md) | Change methods safely and select relevant regression controls |
| [Manuscript authoring](guides/authoring.md) | Edit sections, variables, citations, equations, and figures |

## Reference: understand the system

| Reference | Covers |
| --- | --- |
| [Architecture](reference/architecture.md) | Entry points, package responsibilities, and artifact flow |
| [Data lineage](reference/data-lineage.md) | Stored sources, exported results, figures, and manuscript bindings |
| [Reproducibility and interpretation](reference/reproducibility.md) | Computational definitions, sampling, custody, and research limits |
| [Verification and publication](reference/verification.md) | Recorded verification, authoritative receipts, and published PDF identity |

## Manuscript source

[manuscript/](manuscript/README.md) holds the canonical numbered Markdown sections, supplements, bibliography, configuration, and preamble. Its paths remain stable because the renderer uses them directly. [Methods](manuscript/03_methods.md), [corpus results](manuscript/04a_corpus_and_networks.md), and [domain findings](manuscript/04b_domain_findings.md) are useful starting points; numerical placeholders resolve in the built paper.

Documentation contains reusable instructions and definitions. Historical review narratives and speculative refactoring/testing plans have been removed; recorded execution and publication receipts remain under [output/review-20261006/](../output/review-20261006/). Read [verification](reference/verification.md) for how to use those records without treating an old run as a new one.

Return to the [repository overview](../README.md).

[Current validation patch and verification](reference/release-v1.2.1.md).
