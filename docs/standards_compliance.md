# Standards Compliance — Ento-Linguistics

Current project quality metrics and compliance status. Corpus figures below match `output/data/*.json` and `data/corpus/abstracts.json` after a full pipeline run (see `manuscript_data_lineage.md` for how `{{KEY}}` placeholders are substituted at PDF build time).

## Test Suite

| Metric | Value |
|--------|-------|
| **Total tests** | Run `uv run pytest tests/ --collect-only -q` from `projects/ento_linguistics/` for the current count |
| **Mock usage** | None — all tests use real data |
| **Coverage method** | Branch coverage (enabled in `pyproject.toml`, `[tool.coverage.run] branch = true`); measure with `uv run pytest tests/ --cov=src` |

### Test File Coverage

| Subpackage | Test Files | Modules Covered |
|------------|-----------|-----------------|
| `analysis/` | `test_term_extraction.py`, `test_text_analysis.py`, `test_discourse_analysis.py`, `test_domain_analysis.py`, `test_conceptual_mapping.py`, `test_semantic_entropy.py`, `test_cace_scoring.py`, `test_performance.py` (tests `analysis/performance.py`) + expanded/coverage variants | All 12 analysis modules |
| `visualization/` | `test_concept_visualization.py`, `test_statistical_visualization.py`, `test_visualization.py`, `test_plots.py` + expanded/coverage variants | All 5 visualization modules |
| `core/` | `test_exceptions.py`, `test_metrics.py`, `test_parameters.py`, `test_validation.py`, `test_core_validation.py` | All 7 core modules |
| `data/` | `test_literature_mining.py`, `test_arxiv_corpus.py`, `test_openalex_enrichment.py`, `test_pmc_fulltext.py`, `test_data_generator.py`, `test_data_processing.py` + expanded/coverage variants | All 6 data modules |
| `pipeline/` | `test_simulation.py`, `test_reporting.py`, `test_pipeline_init.py`, `test_statistics_pipeline.py`, `test_fulltext_pipeline.py` | All 5 pipeline modules |
| Integration | `tests/integration/` (4 files) | Cross-module workflows |

## Code Quality

| Standard | Status | Notes |
|----------|--------|-------|
| **Type hints** | ✅ | All public APIs typed (`from __future__ import annotations`) |
| **Docstrings** | ✅ | Google-style on all exported functions/classes |
| **Structured logging** | ✅ | `src/core/logging.py` with `get_logger(__name__)` |
| **Custom exceptions** | ✅ | `src/core/exceptions.py` — `EntoLinguisticError` hierarchy |
| **No mock policy** | ✅ | Tests use real data fixtures (no mocks) |
| **Deterministic seeds** | ✅ | `random_state=42` in KMeans; `np.random.default_rng(seed)` in data generation |
| **Clean-slate output** | ✅ | `output/figures/` and `output/data/` wiped and recreated on every pipeline run |

## Manuscript Quality

| Standard | Status | Notes |
|----------|--------|-------|
| **Figure references** | ✅ | `\ref{fig:...}` with matching `\label{fig:...}` |
| **Figure captions** | ✅ | Descriptive, multi-sentence captions on all 13 generated figures |
| **16pt font floor** | ✅ | Enforced by a shared matplotlib style applied across all visualization modules at figure-creation time (not per-module comments) |
| **Figure registry** | ✅ | `output/figures/figure_registry.json` tracks all generated figures |
| **Section numbering** | ✅ | 01–06 main, S01–S04 supplemental, 98–99 references |
| **Config metadata** | ✅ | `config.yaml` with title, author, ORCID, keywords |
| **Real corpus stats** | ✅ | Manuscript uses `{{KEY}}` placeholders; `scripts/_render_pdf_override.py` substitutes from `output/data/*.json` at render time (`--strict-templates` catches drift) |

## Figure Generation

Current pipeline run generates **14 figures** (all sourced from real data):

| Figure | File | Size | Status |
|--------|------|------|--------|
| Concept map | `concept_map.png` | 466 KB | ✅ Real TF-IDF/KMeans data |
| Terminology network | `terminology_network.png` | 2.6 MB | ✅ Real Jaccard co-occurrence |
| Domain comparison | `domain_comparison.png` | 751 KB | ✅ Real entropy + CACE scores |
| Domain overlap heatmap | `domain_overlap_heatmap.png` | 229 KB | ✅ Real cross-domain data |
| Anthropomorphic framing | `anthropomorphic_framing.png` | 317 KB | ✅ Real LinguisticFeatureExtractor data |
| Concept hierarchy | `concept_hierarchy.png` | 307 KB | ✅ Real NetworkX centrality |
| Domain overview grid | `domain_overview_grid.png` | 691 KB | ✅ 6-panel top-terms grid |
| Domain patterns grid | `domain_patterns_grid.png` | 509 KB | ✅ 6-panel POS donut charts |
| Power & Labor ambiguities | `power_and_labor_ambiguities.png` | 159 KB | ✅ Real ambiguity metrics |
| Power & Labor frequencies | `power_and_labor_term_frequencies.png` | 206 KB | ✅ Real term frequencies |
| Unit of Individuality patterns | `unit_of_individuality_patterns.png` | 166 KB | ✅ Real pattern data |
| Statistical analysis | `statistical_analysis.png` | — | ✅ Real entropy descriptives, pairwise Welch $t$-tests (BH-corrected, Cohen's $d$), ANOVA |
| Full-text parallel layer | `fulltext_analysis.png` | — | ✅ Same frozen schema over the PMC full-text corpus (`data/fulltexts/fulltexts.json`); registered as `fig:fulltext_analysis` |
| Layer comparison | `layer_comparison.png` | — | ✅ Grouped per-domain entropy bars, abstract layer vs PMC full-text layer (rendered when both `statistical_analysis.json` and `fulltext_analysis.json` exist); registered as `fig:layer_comparison` |

## Live Corpus Statistics

| Metric | Source | Value (current pipeline run) |
|--------|--------|------------------------------|
| Publications | `data/corpus/abstracts.json` | Run `python3 -c "import json; print(len(json.load(open('data/corpus/abstracts.json'))))"` for the current count (corpus growth via `scripts/01_build_corpus.py --grow` is append-only; provenance sidecars in `data/corpus/provenance.json`) |
| Total tokens | `output/data/corpus_statistics.json` | 48,787 |
| Unique token types | `corpus_statistics.json` | 7,105 |
| Type–token ratio | `corpus_statistics.json` | 0.1456 |
| Total characters | `corpus_statistics.json` | 537,133 |
| Avg token length | `corpus_statistics.json` | 7.32 chars |
| Extracted candidate terms | `extracted_terms.json` (key count) | 888 |
| Domain-assigned terms | `extracted_terms.json` | 261 |
| Concept map | `concept_map_summary.json` | 6 concepts, 9 relationships |
| Terminology network | `concept_map_summary.json` | 894 nodes, 514 edges |
| Full-text layer | `data/fulltexts/` shards + `output/data/fulltext_analysis.json` | PMC Open Access full texts (count: `python3 -c "from pathlib import Path; from data.pmc_fulltext import load_fulltexts; print(len(load_fulltexts(Path('data/fulltexts'))))"`); artifact guarded by a corpus fingerprint (record count + provenance SHA-256) — rebuilt only when the corpus changes, **full corpus by default** (`FULLTEXT_ANALYSIS_LIMIT` bounds quick runs; bounded artifacts record their limit and never satisfy the full-corpus guard); rendered via `FULLTEXT_*` tokens |
| BHL historical layer | `data/bhl/` + `data/bhl/era_term_usage.json` | Biodiversity Heritage Library mirror texts 1850-1970 (count: `python3 -c "import json; print(json.load(open('data/bhl/era_term_usage.json'))['source']['documents'])"`); era-stratified artifact produced by `src/pipeline/bhl_analysis.py`; rendered via `BHL_*` tokens (`BHL_DOCUMENTS`, `BHL_<ERA>_<TERM>_PER_10K`) |
| arXiv preprint layer | `data/corpus/arxiv_records.json` + `arxiv_provenance.json` | Separate source layer (not merged into `abstracts.json`); count: `python3 -c "import json; print(len(json.load(open('data/corpus/arxiv_records.json'))))"`; harvested by `src/data/arxiv_corpus.py` (`python -m data.arxiv_corpus`) |
| Citation enrichment | `data/corpus/citation_metadata.json` | OpenAlex `cited_by_count`/concepts/OA status per DOI-bearing corpus record, keyed by abstract SHA-256; produced by `src/data/openalex_enrichment.py` (`python -m data.openalex_enrichment`, resumable) |

## Validation Commands

Command lists below reference `scripts/01_build_corpus.py`, `scripts/02_generate_figures.py`, and the `_`-prefixed helper scripts. Helpers are subject to consolidation — if one is missing, consult `scripts/README.md` for its current replacement before treating the command as stale.

```bash
# Full pipeline (entry point — also clears and regenerates output/; runs the
# statistics stage via src/visualization/manuscript_figures.py::main(), writing
# output/data/statistical_analysis.json and output/figures/statistical_analysis.png;
# when data/fulltexts/fulltexts_NNNNN.json shards exist, the full-text stage
# reuses or rebuilds output/data/fulltext_analysis.json under the corpus
# fingerprint freshness guard and renders fulltext_analysis.png +
# layer_comparison.png)
uv run python scripts/02_generate_figures.py

# Tests
uv run pytest tests/ -x -q

# Build corpus (stage 1)
uv run python scripts/01_build_corpus.py

# Manuscript preflight
uv run python scripts/_manuscript_preflight.py --strict

# PDF (template substitution + XeLaTeX); fail if any {{KEY}} unresolved
uv run python scripts/_render_pdf_override.py --strict-templates

# Quality report
uv run python scripts/_quality_report.py
```

## Known Compliance Items

| Item | Status | Notes |
|------|--------|-------|
| `infrastructure.*` imports | ✅ Removed | All imports use local `src/` modules |
| Mock/fake data in scripts | ✅ Removed | Real Jaccard co-occurrence, real entropy scores |
| Hardcoded corpus statistics | ✅ | Manuscript markdown uses `{{KEY}}`; values are not edited as literals in prose |
| Font size compliance | ✅ | 16pt floor enforced via shared style application across visualization modules |
| Clean-slate execution | ✅ | `_setup_directories()` wipes output before rebuild |
| Stale figures | ✅ | No stale artefacts — wiped on every run |

---

**Last Verified:** 2026-09-15 (corpus table synced to `output/data/*.json`; test counts via `uv run pytest tests/ --collect-only -q`; coverage via `uv run pytest tests/ --cov=src`; inferential-statistics stage added, see `CHANGELOG.md` 1.1.0)

- [development_workflow.md](development_workflow.md) — Environment and commands
- [validation_guide.md](validation_guide.md) — Validation pipeline details
- [refactor_playbook.md](refactor_playbook.md) — Module dependencies
