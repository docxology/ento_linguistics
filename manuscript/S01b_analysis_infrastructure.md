# Supplemental Methods: Statistical and Scoring Infrastructure {#sec:supplemental_infrastructure}

## Statistical Analysis (`src/analysis/statistics.py`)

All functions implemented from mathematical first principles via NumPy and SciPy.

### `DescriptiveStats`

`calculate_descriptive_stats(data: np.ndarray)` → `DescriptiveStats(mean, std, median, min, max, q25, q75, count)`.

### `t_test`

```python
def t_test(sample1, sample2=None, mu=None, alternative="two-sided") -> Dict
# Returns: t_statistic, p_value, degrees_of_freedom, alternative
```

- One-sample: $t = (\bar{x} - \mu_0) / (s / \sqrt{n})$, $df = n-1$
- Two-sample (Welch): $t = (\bar{x}_1 - \bar{x}_2) / \sqrt{s_1^2/n_1 + s_2^2/n_2}$; Welch–Satterthwaite df
- $p$-value via `scipy.stats.t.sf`

### `anova_test`

`anova_test(groups: List[np.ndarray])` → `f_statistic, p_value, df_between, df_within`. From-scratch SS computation; $p$ via `scipy.stats.f.sf`.

### `calculate_correlation`

`method="pearson"`: `numpy.corrcoef` + t-distribution p-value. `method="spearman"`: `scipy.stats.spearmanr`.

### `calculate_confidence_interval`

$\bar{x} \pm t_{0.975, n-1} \cdot s/\sqrt{n}$; critical value via `scipy.stats.t.ppf(0.975, n-1)`.

### `fit_distribution`

Supports `"normal"` (MLE: μ, σ), `"exponential"` (MLE: λ=1/mean), `"uniform"` (min, max).

---

## Domain Analysis (`src/analysis/domain_analysis.py`)

### `DomainAnalysis` Dataclass

Fields: `domain_name`, `key_terms` (top-10 by frequency), `term_patterns` (compound/multi_word/capitalized/abbreviation/numeric counts), `framing_assumptions`, `conceptual_structure` (domain ontology), `ambiguities` (term/contexts/issue triplets), `recommendations`, `frequency_stats` (mean/median/SD/histogram), `cooccurrence_analysis`, `ambiguity_metrics`, `confidence_scores`, `conceptual_metrics`, `statistical_significance`.

### `DomainAnalyzer` Methods

`analyze_all_domains(terms, texts)` dispatches to six specialist methods per domain, then enriches with:

1. `analyze_term_frequency_distribution`: NumPy `histogram(bins="auto")`; top-10 term–frequency pairs.
2. `analyze_term_cooccurrence`: sliding-window co-occurrence matrix.
3. `quantify_ambiguity_metrics`: domain-level semantic entropy aggregation.
4. `calculate_statistical_significance`: $\chi^2$/Fisher's on pattern distributions.

Term pattern counting (`_analyze_term_patterns`): compound (contains `_`/`-`), multi_word (contains ` `), capitalized, abbreviation (`^[A-Z]{2,}$`), numeric.

---

## Conceptual Mapping (`src/analysis/conceptual_mapping.py`)

### Data Structures

`Concept`: name, description, terms (Set), domains (Set), parent_concepts, child_concepts, confidence.
`ConceptMap`: `concepts: Dict[str, Concept]`, `term_to_concepts: Dict[str, Set[str]]`, `concept_relationships: Dict[Tuple[str,str], float]`.

### `ConceptualMapper`

`build_concept_map(terms)`: (1) instantiate 6 base concept nodes; (2) domain- and keyword-based term assignment; (3) overlap-coefficient edge creation.

`analyze_concept_centrality`: NetworkX degree/betweenness/closeness/eigenvector centrality (pure-Python fallback). `quantify_relationship_strength`: composite = base×0.4 + term_overlap×0.3 + domain_overlap×0.2 + hierarchical×0.1. `identify_cross_domain_bridges`: concepts spanning ≥2 domains. `calculate_concept_similarity`: Jaccard + domain overlap bonus (max 0.3). `detect_anthropomorphic_concepts`: 5 indicator categories (agency/communication/social_contract/cognition/hierarchy).

**Pipeline results (sourced from `output/data/concept_map_summary.json`):**

| Concept | Terms | Domains |
|---------|-------|---------|
| `biological_individuality` | 75 | Unit of Individuality |
| `social_organization` | 98 | Power & Labor; Behavior & Identity |
| `reproductive_biology` | 67 | Sex & Reproduction |
| `kinship_systems` | 64 | Kin & Relatedness |
| `resource_economics` | 15 | Economics |
| `behavioral_ecology` | 56 | Behavior & Identity; Economics |
| **Concept relationships** | **9** | |

---

## CACE Scoring (`src/analysis/cace_scoring.py`)

`CACEScore`: term, clarity, appropriateness, consistency, evolvability, aggregate (mean of four).

| Function | Formula |
|----------|---------|
| `score_clarity` | `max(0, 1 - entropy_bits / log2(10))` — `log2(10) ≈ 3.32` = `DEFAULT_MAX_ENTROPY` |
| `score_appropriateness` | `1 - (0.4 × 𝟙[term ∩ 𝒜] + 0.1 × overlap + 0.05 × max(domains−1, 0))` — graduated penalty, never zeroed |
| `score_consistency` | Mean pairwise cosine similarity of TF-IDF context vectors (high = consistent) |
| `score_evolvability` | `0.5 × min(1, domains/3) + 0.5 × min(1, scale_levels_in_contexts/3)` |
| `evaluate_term_cace` | All four scorers → `CACEScore` |
| `compare_terms_cace` | Ranked `List[CACEScore]` by aggregate descending |

`ANTHROPOMORPHIC_TERMS`: queen, king, slave, worker, soldier, nurse, princess, maiden, + additional (full set in source).

---

## Rhetorical Analysis (`src/analysis/rhetorical_analysis.py`)

`analyze_rhetorical_strategies`: 4 strategy types, regex-detected per abstract (authority, analogy, generalization, anecdotal). `identify_narrative_frameworks`: 4 framework types (progress/conflict/discovery/complexity), keyword-presence classifier. `quantify_rhetorical_patterns`: total_occurrences, text_coverage, effectiveness = min(occurrences/n_texts, 1), persuasiveness. `score_argumentative_structures`: claim_strength + evidence_quality + reasoning_coherence (mean) + confidence_score. `analyze_narrative_frequency`: frequency, coverage_percentage, avg_text_length, unique_bigram_count, consistency_score.

---

## Visualization (`src/visualization/`)

`ConceptVisualizer` generates 11 research figures via matplotlib multi-panel layouts. `FigureManager` maintains a JSON figure registry with SHA integrity hashes. `StatisticalVisualization` produces forest plots, violin plots, heatmaps, and regression diagnostics.

**Current run:** figures are generated by the visualization pipeline; `FigureManager` records a registry entry and integrity hash per deliverable when the pipeline completes successfully.

---

## Core Infrastructure (`src/core/`)

`parameters.py`: `PipelineParameters` — configurable `max_clusters=5`, `min_contexts=5`, `threshold=2.0`, `random_state=42`, `window_size=5`, `max_features=1000`. `validation.py`/`validation_utils.py`: type checks and domain membership guards on all public API entry points. `metrics.py`: wall-clock, memory, throughput per stage. `markdown_integration.py`: `\ref{}` resolution and cross-reference validation.

---

## Reproducibility

- **Deterministic**: `random_state=42` in all KMeans calls.
- **Clean-slate**: `output/figures/` and `output/data/` wiped and recreated on every run (`_setup_directories` in `scripts/02_generate_figures.py`).
- **Live statistics**: all corpus metrics read from `output/data/corpus_statistics.json`, `domain_statistics.json`, `concept_map_summary.json` — not hardcoded anywhere in the manuscript.
- **Dependency pinning**: all Python dependencies pinned in `pyproject.toml`.
- **Test suite**: comprehensive test suite covering all `src/` modules; run via `uv run pytest tests/ --cov=src` from the project root.
