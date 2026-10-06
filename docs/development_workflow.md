# Standalone development workflow

Work from the repository root. Preserve unrelated local changes and inspect local guidance before editing. Python dependencies use uv and uv.lock.

## Prepare the environment

~~~bash
uv sync --frozen --extra dev
uv run python -m nltk.downloader -d .venv/nltk_data stopwords punkt_tab wordnet omw-1.4
~~~

The selected English tokenizer, stopword and WordNet bytes enter cache signatures and the schema-2 receipt. NLTK's actual search order applies. Resource custody identifies installed bytes; it does not vendor downloads.

## Change and verify

Reproduce a defect before changing its implementation. Use real files, actual text slices, independent numerical checks and fixed seeds. Run the affected tests first; mocking frameworks are not permitted.

~~~bash
PYTHONPATH=src uv run pytest tests/test_provenance.py tests/test_nltk_resources.py --no-cov
uv run python scripts/02_generate_figures.py
uv run pytest tests/ --cov=src --cov-report=term-missing
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

Generation and tests run sequentially because existing tests consume exports. The configured coverage gate measures combined statements and branches. Report branch-only coverage separately when relevant.

BHL era recovery is automatic in the manuscript pipeline under output/.checkpoints/bhl. The standalone BHL CLI also accepts --checkpoint-dir. Completed checkpoints are content-bound; partial calculations never become completed-era checkpoints.

Generation refreshes exported data and registered figures, reusing expensive layer artifacts only when their full fingerprints agree. To verify a cold rebuild without changing definitions, preserve existing artifacts outside the pipeline output directories and remove their reusable cache copies. A default run leaves FULLTEXT_ANALYSIS_LIMIT and BHL_STACK_CHARACTER_BUDGET unset; bounded development runs are labeled and cannot satisfy default fingerprints.

## Finish the paper

Read the custody audit and content receipt before interpreting results. Render the final source, inspect all figure PNGs and PDF pages, and check the final TeX log for missing glyphs, undefined references/citations and layout overflow. Corpus-derived values remain template tokens in manuscript Markdown.

Document execution logs, source/output hashes, negative controls, coverage and remaining research limits in a dated report. Independent review follows completed manual QA when a rigorous review is requested. Local build evidence does not imply publication, license clearance or human validation.

See reproducibility.md and validation_guide.md for interpretation and artifact checks.
