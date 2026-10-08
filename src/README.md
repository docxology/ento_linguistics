# Source architecture

Five packages own text analysis, source loading, workflow computation, artifact validation, and visualization. Scripts delegate to these modules; the separately receipted fixed-margin extension lives in `research/network_robustness/`.

| Package | Responsibility | Key entry points |
| --- | --- | --- |
| `analysis/` | Candidate extraction, domain assignment, context-cluster entropy, heuristic CACE and lexical indicators | `term_extraction.py`, `semantic_entropy.py`, `cace_scoring.py` |
| `core/` | Validation, manuscript variables, content signatures, resources, and shared utilities | `provenance.py`, `manuscript_variables.py`, `nltk_resources.py` |
| `data/` | Corpus loaders, retrieval, sidecars, and controlled data generation | `loader.py`, `literature_mining.py`, `bhl_corpus.py`, `arxiv_corpus.py` |
| `pipeline/` | Layer analysis, custody auditing, statistics, and paper rendering | `statistics_pipeline.py`, `fulltext_pipeline.py`, `bhl_analysis.py`, `corpus_audit.py`, `rendering.py` |
| `visualization/` | Core manuscript figures and registry management | `manuscript_figures.py`, `figure_manager.py`, `concept_visualization.py` |

## Implemented measurements

Term extraction assigns six predefined, overlapping domains. Short extraction windows support heuristic scoring; sentence contexts support entropy. TF-IDF and seeded KMeans partition usable sentence contexts, with the bounded square-root cluster rule specified in [methods](../docs/manuscript/03_methods.md). The normalized entropy denominator uses occupied clusters, with zero for a single occupied cluster. These partitions are not independently annotated word senses.

The observed terminology network counts shared documents; the separate conceptual map encodes configured category/vocabulary overlap. CACE uses inspectable Clarity, Appropriateness, Consistency, and Evolvability rules. Its penalties, weights, and missing-data conventions are heuristic choices. Lexical framing matches are not measured causal effects or author intention. See [reproducibility](../docs/reference/reproducibility.md) for complete definitions and limits.

## APIs and execution

With `src/` on the import path, packages use names such as `analysis.term_extraction` and `pipeline.rendering`. `evaluate_term_cace` accepts a numerical `semantic_entropy` as its second argument and a separate `contexts` keyword. Use explicit keywords to distinguish measured entropy, short extraction contexts, and domain labels; disclose defaults for missing estimates.

Run maintained commands from the repository root through `uv run`. See [script interfaces](../scripts/README.md), [workflow](../docs/guides/workflow.md), and [development](../docs/guides/development.md). For complete measured source coverage:

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
```

The configured floor is 90% combined statement/branch coverage. Captured publication results are recorded in [verification](../docs/reference/verification.md). Public APIs require type hints and documented behavior; tests use real inputs and fixed seeds. Read [source maintenance](AGENTS.md) and the affected package's AGENTS.md before changing computation.
