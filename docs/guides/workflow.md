# Analyze the corpus and build the paper

[Documentation](../README.md) → Analysis workflow

Complete [setup](setup.md) first. Run commands from the repository root and keep generation and tests sequential: some integration tests inspect generated artifacts.

## 1. Analyze the stored corpus

~~~bash
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m research.network_reading.study --root .
~~~

The separate network-reading command validates the completed core receipt, reconstructs the selected incidence and writes the declared vocabulary/threshold grid and graphical abstract. Rerun it after its implementation or consumed inputs change; strict rendering rejects a stale or absent extension.

The core generator processes the identified abstract selection and separate PMC, BHL, and arXiv layers, exports statistics, generates registered figures, checks manuscript variables, and writes a completed analysis manifest only after required stages succeed.

It reuses expensive layer artifacts when ordered input contents, source code, dependency lock, selected NLTK resources, and relevant development bounds match their fingerprints. Running the generator is therefore not always a cold recomputation. Preserve prior results outside the managed artifact directories before deliberately removing reusable caches for a cold run.

BHL completed-era checkpoints live under output/.checkpoints/bhl/. They are written atomically and include a result digest. An interruption can resume matching completed eras; changed inputs or bounds require recomputation, and corrupted matching checkpoints fail. A checkpoint is not the final four-layer receipt.

## 2. Inspect source custody

~~~bash
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
~~~

Read output/reports/corpus_audit.json. The audit distinguishes stored records from identified headline inputs and reports missing provenance, repeated text, and source-ID disagreement. A successful audit does not mean every gap was reconciled.

See [data lineage](../reference/data-lineage.md) and [interpretation limits](../reference/reproducibility.md) before comparing layers.

## 3. Render the manuscript

~~~bash
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

The renderer validates the content receipt, resolves numerical placeholders, and invokes Pandoc, XeLaTeX, and BibTeX. Required command failures, unresolved variables, missing glyphs, and undefined citations/references fail the build.

Output: [output/pdf/ento_linguistics_combined.pdf](../../output/pdf/ento_linguistics_combined.pdf). Inspect the final TeX log and rasterized pages using the [validation guide](validation.md).

The top-level published PDF is a separate copy. Update it only after validating the new build; publishing to GitHub or Zenodo is a separate action.

## Full runs and development bounds

Leave FULLTEXT_ANALYSIS_LIMIT and BHL_STACK_CHARACTER_BUDGET unset for a default run. The former is a positive PMC document cap; the latter is a positive per-era BHL character cap that selects whole documents. A cap too small for an eligible whole document is rejected.

Both settings enter fingerprints and coverage metadata. Bounded artifacts cannot satisfy a full/default cache identity. Independently of these development settings, BHL entropy uses twenty frequent candidates per era, domain CACE aggregates use at most fifty terms, and PMC discourse uses a deterministic eligible-text sample.

## Acquire more literature

The acquisition entry point is scripts/01_build_corpus.py. Its force and growth modes perform live retrieval and can change the research input; the default can refresh cached statistics without fetching when the corpus is full. Consult its help before choosing growth/force options:

~~~bash
uv run python scripts/01_build_corpus.py --help
~~~

After acquisition, regenerate all affected layers and figures, inspect custody, and rebuild the paper. Preserve original text and report unresolved source associations rather than inventing metadata.
