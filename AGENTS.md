# Ento-Linguistics maintenance

This standalone research repository analyzes scientific terminology across identified PubMed abstracts and separate PMC, BHL OCR, and arXiv layers. The six predefined, overlapping domains are Unit of Individuality, Behavior and Identity, Power and Labor, Sex and Reproduction, Kin and Relatedness, and Economics.

## Work and verification

Preserve unrelated working-tree edits and historical scientific evidence. Reproduce defects before changing source, use real files and local HTTP instead of mocks, and verify negative controls as well as successful execution. Use `uv run` for Python commands. Public APIs require type hints and documented behavior. The configured coverage floor is 90% combined statement/branch coverage.

- Analysis changes: read [data lineage](docs/reference/data-lineage.md) and [reproducibility](docs/reference/reproducibility.md), then the affected directory's AGENTS.md. Regenerate affected artifacts and validate their content receipts.
- Manuscript changes: read [authoring](docs/guides/authoring.md) and [manuscript guidance](docs/manuscript/AGENTS.md). Preserve computational placeholders and render strictly. Separate descriptive proxies, executed network comparisons, and proposed theory.
- Documentation changes: read [documentation guidance](docs/AGENTS.md). Verify paths and commands against the checkout. Keep current procedures in guides and definitions in reference pages.

## Active workflow

Run from the repository root, with tests and generation sequential:

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m research.network_reading.study --root .
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
```

`scripts/01_build_corpus.py` handles acquisition; inspect its help before changing the stored corpus. `scripts/02_generate_figures.py` delegates the four-layer analysis and figure build to `src/visualization/manuscript_figures.py`. The renderer delegates to `src/pipeline/rendering.py` and verifies the separately receipted fixed-margin companions in `research/network_robustness/` and vocabulary/threshold diagnostics in `research/network_reading/`. Underscore-prefixed scripts are manually invoked entry points; the renderer is part of the paper workflow.

The generated paper is `output/pdf/ento_linguistics_combined.pdf`. The top-level PDF and external releases have separate publication identities. Release versions must identify the exact reviewed source/PDF/media set. Retain archived DOI and release records; do not assign an earlier version DOI to a new GitHub edition.

## Evidence and outputs

`output/figures/` and `output/data/` contain managed build artifacts. Other output directories retain execution logs, checkpoints, independent reviews, and release receipts. Preserve this evidence rather than treating the whole output tree as disposable. Cold recomputation and bounded development runs have different meanings; follow [workflow](docs/guides/workflow.md).

See [script interfaces](scripts/README.md), [source architecture](src/AGENTS.md), [test guidance](tests/AGENTS.md), and [verification records](docs/reference/verification.md).
