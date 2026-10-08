# Test suite

Tests cover the five `src/` packages and the separately receipted fixed-margin extension. Use the locked development environment from [setup](../docs/guides/setup.md), run from the repository root, and follow [test maintenance](AGENTS.md).

```bash
uv run pytest tests/ --collect-only -q
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run pytest tests/integration/ --no-cov -v
uv run pytest tests/test_rendering.py tests/test_concept_visualization.py --no-cov
```

The configured floor is **90% combined statement/branch coverage** across measured source. Subset passes and image existence do not establish full coverage or visual correctness. Tests and artifact generation run sequentially. The [8 October draft run](../output/review-main-20261008/SUMMARY.md) recorded 1,820 passes, eight external-template skips, 83 warnings and 92.00% combined coverage in about 408 seconds; this is a captured run, not a timing guarantee for later checkouts.

## Find the relevant controls

| Area | Tests |
| --- | --- |
| Extraction, entropy, domains, CACE and graphs | `test_term_extraction.py`, `test_semantic_entropy.py`, `test_domain_analysis.py`, `test_cace_scoring.py`, `test_conceptual_mapping.py`, `test_statistics.py` |
| Corpus retrieval and layer analyses | `test_corpus_build.py`, `test_literature_mining.py`, `test_pmc_fulltext.py`, `test_fulltext_pipeline.py`, `test_bhl_corpus.py`, `test_bhl_analysis.py`, `test_arxiv_corpus.py`, `test_arxiv_analysis.py`, `test_openalex_enrichment.py` |
| Content/resource identity and recovery | `test_provenance.py`, `test_artifact_integrity.py`, `test_nltk_resources.py`, `test_bhl_checkpoints.py`, `test_review_controls.py` |
| Statistics and shared manuscript inputs | `test_statistics_pipeline.py`, `test_manuscript_variables.py`, `test_manuscript_figures.py`, `test_statistical_analysis_figure.py` |
| Figure geometry and registration | `test_concept_visualization.py`, `test_statistical_visualization.py`, `test_figure_manager.py`, `test_plots.py`, `test_visualization.py` |
| Strict rendering and helpers | `test_rendering.py`, `test_manuscript_preflight.py`, `test_quality_report.py`, `test_reporting.py` |
| Fixed-margin draws and decoded receipts | `test_network_robustness_extension.py` |
| Cross-module workflow | [integration/](integration/README.md), pipeline-specific tests, `test_package_imports.py` |
| Synthetic demonstrations and shared utilities | `test_data_generator.py`, `test_data_processing.py`, `test_simulation.py`, `test_metrics.py`, `test_parameters.py`, `test_validation.py`, `test_logging.py`, `test_exceptions.py` |

This is a navigation map, not a frozen exhaustive test count. Collection is authoritative. Tests use real input and independent numerical checks, fixed RNG seeds, temporary files and local HTTP. Some integration cases require an external parent-template checkout and skip when absent. Pandoc and selected NLTK resources are needed by affected tests; Python package installation alone does not supply them.

See [development](../docs/guides/development.md), [validation](../docs/guides/validation.md), and [integration guidance](integration/AGENTS.md) for error-path controls, artifact checks and scope limits.
