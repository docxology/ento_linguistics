# Architecture

[Documentation](../README.md) → Architecture

The project runs independently of the parent research template. Scripts expose commands; source modules own computation and rendering.

## Artifact flow

~~~mermaid
flowchart LR
    A[Stored corpus and provenance] --> B[Layer analyses]
    R[Python source, lock and NLTK resources] --> B
    B --> C[Statistics and terminology exports]
    C --> D[Registered figures]
    C --> E[Completed content receipt]
    D --> E
    M[Manuscript sections and bibliography] --> P[Strict renderer]
    E --> P
    P --> F[PDF]
~~~

## Responsibilities

| Package | Role | Useful entry points |
| --- | --- | --- |
| analysis/ | Processing, extraction, domain assignment, entropy, statistics, and heuristic scores | [term extraction](../../src/analysis/term_extraction.py), [semantic entropy](../../src/analysis/semantic_entropy.py), [CACE](../../src/analysis/cace_scoring.py) |
| data/ | Literature acquisition, loading, and preprocessing | [loader](../../src/data/loader.py), [literature mining](../../src/data/literature_mining.py) |
| core/ | Resource/content identity, validation, and manuscript variables | [provenance](../../src/core/provenance.py), [NLTK resources](../../src/core/nltk_resources.py), [variables](../../src/core/manuscript_variables.py) |
| pipeline/ | Source-layer orchestration, recovery, custody, and PDF rendering | [BHL recovery](../../src/pipeline/bhl_artifact.py), [custody audit](../../src/pipeline/corpus_audit.py), [renderer](../../src/pipeline/rendering.py) |
| visualization/ | Shared analysis-to-figure orchestration, charts, and registry | [manuscript figures](../../src/visualization/manuscript_figures.py), [statistical plots](../../src/visualization/statistical_visualization.py) |

Package names above are relative to src/. The synthetic-data generator ([data_generator](../../src/data/data_generator.py)) serves tests and the [simulation script](../../scripts/_scientific_simulation.py); the manuscript pipeline analyzes only stored source text.

## Public workflow entry points

- [01_build_corpus.py](../../scripts/01_build_corpus.py): acquisition; changes inputs through live retrieval.
- [02_generate_figures.py](../../scripts/02_generate_figures.py): analyses, figures, exports, and completed receipt.
- [pipeline.corpus_audit](../../src/pipeline/corpus_audit.py): read-only custody and optional receipt validation.
- [_render_pdf_override.py](../../scripts/_render_pdf_override.py): the active standalone PDF command.

An underscore prefix identifies a helper rather than an automatically numbered stage. The PDF override is explicitly invoked despite its prefix. Other helpers may describe older workflows; consult their actual interface before using them.

See [workflow](../guides/workflow.md) for operation and [data lineage](data-lineage.md) for source/output relationships.
