# Ento-Linguistic research

A descriptive research pipeline for examining terminology across six domains: Unit of Individuality, Behavior and Identity, Power and Labor, Sex and Reproduction, Kin and Relatedness, and Economics.

The repository contains four separate source layers: a source-identified PubMed abstract selection alongside its preserved archive, PMC full-text shards, BHL historical OCR volumes, and arXiv preprint records. Analyses report corpus frequencies, rule-based assignments, document co-occurrence, context-cluster entropy, and heuristic discourse/CACE scores. These measurements do not establish causal effects of language, independently validated senses, or field-wide representativeness.

## Paper and publication

[Read the updated paper](Ento_Linguistics_manuscript.pdf) · [Zenodo revision](https://zenodo.org/records/23193499) · [Concept DOI](https://doi.org/10.5281/zenodo.19574117)

The 2026-10-06 revision contains 46 pages and 17 figures. Headline results use 7,540 identified abstracts from 7,609 archived strings; separate analyses cover 7,073 PMC records, 2,430 BHL documents and 61 arXiv records. Full/default BHL extraction and framing includes 2,317,721,403 OCR characters; entropy remains a twenty-candidate sample per era.

Verification: 1,774 tests passed, eight external-template tests skipped; 91.93% combined statement/branch coverage. The strict PDF build and independent local revision review passed. See [revision report](docs/review_20261006.md) and [publication receipt](output/review-20261006/zenodo/publication-receipt.json). Corpus custody, relevance/licensing, OCR and human-validation limits remain disclosed in the paper.

## Run locally

Install dependencies and the NLTK data prerequisites:

~~~bash
uv sync --frozen --extra dev
uv run python -m nltk.downloader -d .venv/nltk_data stopwords punkt_tab wordnet omw-1.4
~~~

NLTK resources are installed separately from the Python lock. The analysis signature and schema-2 receipt hash the actually selected English punkt_tab files, English stopwords and WordNet dictionary/archive. Resource changes invalidate cached analyses; missing resources fail instead of downloading silently. See [NLTK data installation](https://www.nltk.org/data). The pipeline requires the actual corpus files under *data/*; it does not substitute synthetic text for missing literature.

Run tests, generate analyses, inspect custody, and render the manuscript:

~~~bash
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

These commands run from this repository; no parent research template is required. Run tests and regeneration sequentially because some legacy tests inspect the generated artifacts. Coverage must reach the configured 90% floor. Older tests for external template infrastructure can skip when that infrastructure is absent; the standalone pipeline is verified separately by running the commands above.

For CPU or memory constrained machines:

~~~bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export ENTO_ANALYSIS_WORKERS=2
~~~

For development only, *BHL_STACK_CHARACTER_BUDGET* sets a positive per-era whole-document character cap. It is recorded in the cache fingerprint and cannot satisfy a full run. One worker forces the serial path. Required worker failures propagate; process-pool availability failures are logged before a serial retry. The full PMC analysis is the default. *FULLTEXT_ANALYSIS_LIMIT* is an explicit positive document limit for development runs and is recorded in the fingerprint; a bounded cache cannot satisfy an unbounded run.

To acquire or expand the stored abstract corpus, use *scripts/01_build_corpus.py*. Its growth and force options perform live retrieval; they change the research input and require subsequent complete regeneration. Source-layer harvesters and historical query definitions are documented under *data/*.

## What is measured

| Output | Definition and boundary |
|--------|-------------------------|
| Abstract statistics | Digest-identified PubMed abstracts; unreconciled legacy strings retained but excluded; surface-token extraction threshold one |
| PMC statistics | All stored full texts by default; threshold twenty |
| arXiv statistics | Separate preprint title/abstract layer; threshold two |
| BHL literal frequencies | All stored historical documents; exact seed-phrase matches per 10,000 OCR tokens by era |
| BHL computational stack | All stored documents by default; streamed extraction and framing; entropy restricted to twenty frequent candidates per era; coverage recorded |
| Terminology graph | Actual document co-occurrence among the hundred most frequent domain-assigned terms |
| Concept graph | Six predefined categories connected by shared vocabulary |
| Domain entropy | Mean successful TF-IDF/KMeans sentence-context entropy estimates; insufficient and failed estimates excluded |
| Discourse | Lexical proxies; PMC uses an approximately one-fifth deterministic eligible-text sample |
| CACE | Four heuristic dimensions, with at most fifty terms in domain aggregates; not validated human judgments |
| Framing | Fraction of extracted term-occurrence windows matching anthropomorphic patterns; not a measure of author bias |

Welch/ANOVA outputs are exploratory: domain groups overlap and share document-derived observations. Multiple labels measure classification overlap rather than semantic drift. Historical OCR frequencies do not establish a concept's date of origin.

## Source custody and regeneration

*output/reports/corpus_audit.json* reports missing digest provenance, duplicate text, source-ID mismatches, and unused sidecar entries. Its success means records were inspected without malformed text, not that every source is reconciled or relevant. The stored archive contains documented provenance gaps; the headline analysis excludes strings without an identified PubMed record, and broad retrieval includes adjacent biology and computational uses. Digest-indexed sidecars can collapse distinct IDs with identical text. Source bytes are preserved for reconciliation.

Reusable artifacts are bound to ordered corpus content, project Python source, and *uv.lock*. A completed *output/data/analysis_manifest.json* binds corpus and output inventories and file hashes. The renderer rejects missing or changed receipts and failed toolchain commands. A receipt establishes reproducibility, not scientific validity.

The main pipeline generates and registers figures for all available layers. It fails on required analysis/figure/variable errors and checks manuscript figure availability. Markdown retains numerical placeholders; substitution happens during PDF rendering.

## Layout

- *src/analysis/*: extraction, domain analysis, entropy and heuristic scoring.
- *src/data/*: loaders and source harvesters.
- *src/pipeline/*: layer analyses, custody audit and rendering.
- *src/core/*: manuscript variables, content provenance and ordered execution.
- *src/visualization/*: manuscript and statistical figures.
- *tests/*: numerical, real-file, local-HTTP and real-corpus checks.
- *docs/manuscript/*: canonical manuscript, bibliography and publication metadata.
- *output/*: generated analysis, registered figures, reports and PDF.

See [validation guide](docs/validation_guide.md), [reproducibility boundaries](docs/reproducibility.md), and [review evidence](docs/review_20261005.md).
