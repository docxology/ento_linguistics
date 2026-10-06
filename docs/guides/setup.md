# Set up the project

[Documentation](../README.md) → Setup

## Python environment

Use Python 3.10 or newer and uv. From the repository root:

~~~bash
uv sync --frozen --extra dev
uv run python -m nltk.downloader -d .venv/nltk_data stopwords punkt_tab wordnet omw-1.4
~~~

The dev extra includes pytest, coverage support, and the local HTTP test server. A default sync without that extra may remove test dependencies.

The English pipeline consumes punkt_tab, English stopwords, and WordNet. Open Multilingual WordNet is included in the installation command for compatibility with other NLTK uses, but is outside this English pipeline's resource receipt.

NLTK searches its configured locations in order. A user-level installation may shadow the project-local download; the analysis identity hashes the resources actually selected. Missing, empty, or whitespace-only selected resources fail. Hashes identify contents but do not vendor or automatically restore those downloads.

## Corpus files and resources

The analyses use the stored files under data/. They do not substitute synthetic literature when a layer is absent. [Data lineage](../reference/data-lineage.md) identifies the inputs and exports.

Full BHL processing retains raw records and cleaned era text in memory; memory requirements grow with stored text. Per-document counting reduces intermediate allocations but does not make the pipeline constant-memory.

For constrained machines, reduce parallel work before generation:

~~~bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export ENTO_ANALYSIS_WORKERS=1
~~~

One analysis worker selects the serial path. [Workflow](workflow.md) distinguishes full runs from explicit development limits.

## PDF toolchain

Rendering requires working installations of Pandoc, XeLaTeX, and BibTeX. Poppler is used for visual validation.

~~~bash
pandoc --version
xelatex --version
bibtex --version
pdftoppm -v
pdfinfo -v
~~~

These invocations check that each executable runs; installation alone does not establish that the paper compiles. Python dependencies do not install the external TeX or Poppler tools.

Continue with [analysis and rendering](workflow.md), or [validation](validation.md) if inspecting an existing build.
