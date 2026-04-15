# Supplemental Methods: Text Processing and Term Extraction {#sec:supplemental_methods}

This supplement documents the implementation architecture of the Ento-Linguistic analysis pipeline. Every entry corresponds to a real module, class, or function in `src/`. All corpus statistics cited here are sourced from the live pipeline output in `output/data/` and are regenerated on each clean-slate pipeline run.

---

## Package Architecture

```text
src/
├── analysis/
│   ├── cace_scoring.py         # CACE dimension scoring
│   ├── conceptual_mapping.py   # Concept map construction & analysis
│   ├── discourse_analysis.py   # Discourse-level analysis
│   ├── discourse_patterns.py   # Discourse pattern detection
│   ├── domain_analysis.py      # Six-domain specialist analysis
│   ├── performance.py          # Pipeline performance metrics
│   ├── persuasive_analysis.py  # Persuasive strategy analysis
│   ├── rhetorical_analysis.py  # Rhetorical strategy & narrative analysis
│   ├── semantic_entropy.py     # Semantic entropy H(t) computation
│   ├── statistics.py           # Statistical tests (t-test, ANOVA, CI)
│   ├── term_extraction.py      # Term extraction & classification
│   └── text_analysis.py        # Text normalization & tokenization
├── core/
│   ├── exceptions.py           # Custom exception hierarchy
│   ├── logging.py              # Logging infrastructure
│   ├── markdown_integration.py # Manuscript markdown integration
│   ├── metrics.py              # Pipeline metrics collection
│   ├── parameters.py           # Configurable pipeline parameters
│   ├── validation.py           # Input validation
│   └── validation_utils.py     # Validation helpers
├── data/
│   ├── data_generator.py       # Synthetic data generation for testing
│   ├── data_processing.py      # Data loading and transformation
│   ├── literature_mining.py    # Literature corpus mining
│   └── loader.py               # Corpus file loader
├── pipeline/
│   ├── reporting.py            # Pipeline output reporting
│   └── simulation.py           # Simulation framework
└── visualization/
    ├── concept_visualization.py     # Multi-panel concept figures
    ├── figure_manager.py            # Figure registry & integrity
    ├── plots.py                     # Low-level plot utilities
    ├── statistical_visualization.py # Statistical plots
    └── visualization.py            # Visualization utilities
```

---

## Text Processing (`src/analysis/text_analysis.py`)

### `TextProcessor`

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | `str` | `"english"` | NLTK processing language |
| `custom_stop_words` | `Optional[Set[str]]` | `None` | Additional domain stop-words |

Stop-word vocabulary = NLTK English stop-words ∪ `SCIENTIFIC_STOP_WORDS` (24 domain meta-language tokens: *fig, table, et, al, etc, ie, eg, vs, cf, respectively, however, therefore, thus, although, whereas, furthermore, moreover, addition, similarly, consequently, subsequently, accordingly, nevertheless, nonetheless*).

Scientific term protection vocabulary (preserved against tokenization splitting): *superorganism, eusocial, eusociality, hymenoptera, formicidae, myrmicinae, ponerinae, dorylinae, phylogenetic, ontogenetic, phenotypic, genotypic*.

**Methods:**

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `normalize_text` | `(text: str) → str` | Normalized string | NFKC → lowercase → punctuation removal (retaining hyphens) → whitespace collapse |
| `tokenize_sentences` | `(text: str) → List[str]` | Sentence list | NLTK `sent_tokenize` |
| `tokenize_words` | `(text: str, preserve_scientific: bool) → List[str]` | Token list | NLTK `word_tokenize` + sliding-window scientific-term merge |
| `remove_punctuation` | `(tokens: List[str]) → List[str]` | Clean tokens | Regex `[^\w\-_]` removal; retains alphanumeric content |
| `remove_stop_words` | `(tokens: List[str]) → List[str]` | Filtered tokens | Lowercased lookup against combined stop-word set |
| `lemmatize_tokens` | `(tokens: List[str]) → List[str]` | Lemmatized tokens | NLTK `WordNetLemmatizer.lemmatize` |
| `process_text` | `(text: str, lemmatize=True, remove_stops=True) → List[str]` | Processed tokens | Full pipeline: normalize → tokenize → remove punct → [stop removal] → [lemmatize] |
| `extract_ngrams` | `(tokens, n=2, min_freq=1) → Dict[str,int]` | N-gram counts | Sliding window; filters by `min_freq` |
| `get_vocabulary_stats` | `(texts: List[str]) → Dict` | Stats dict | total_tokens, unique_tokens, total_characters, avg_token_length, most_common_tokens (top 20), type_token_ratio |

**Corpus vocabulary statistics (current run, sourced from `output/data/corpus_statistics.json`):**

| Metric | Value |
|--------|-------|
| Total tokens | **48787** |
| Unique token types | **7105** |
| Type–token ratio | **0.1456** |
| Top 5 tokens | ant (1033), colony (850), worker (831), queen (602), social (583) |

### `LinguisticFeatureExtractor`

Regex-based framing feature extraction. Three pattern sets (16 patterns total):

- **Anthropomorphic** (4 patterns): `\b(choose|decide|prefer|select|opt)\b`, `\b(communicate|signal|inform|warn)\b`, `\b(cooperate|compete|negotiate|trade)\b`, `\b(recognize|identify|distinguish|know)\b`
- **Hierarchical** (4 patterns): `\b(superior|inferior|dominant|subordinate)\b`, `\b(command|control|authority|obey)\b`, `\b(leader|follower|boss|worker)\b`, `\b(ruler|subject|governor|citizen)\b`
- **Economic** (4 patterns): `\b(invest|profit|cost|benefit)\b`, `\b(trade|exchange|transaction|market)\b`, `\b(resource|allocation|distribution|share)\b`, `\b(value|worth|price|commodity)\b`

`extract_framing_features(text)` → dict with raw counts + normalized densities (count / total_words).

Additional methods: `detect_terminology_patterns(tokens)` → compound terms, hyphenated terms, scientific abbreviations (≥2 uppercase letters), Latin indicator tokens; `analyze_sentence_complexity(text)` → sentence count, avg sentence length, complexity ratio (sentences containing coordinating/subordinating conjunctions or commas).

---

## Terminology Extraction (`src/analysis/term_extraction.py`)

### `Term` Dataclass

```python
@dataclass
class Term:
    text: str               # Surface form
    lemma: str              # WordNet lemma
    domains: List[str]      # Ento-Linguistic domain list
    frequency: int          # Corpus-wide occurrence count
    contexts: List[str]     # Deduplicated context sentences
    pos_tags: List[str]     # Part-of-speech tags
    confidence: float       # Extraction confidence
    semantic_entropy: float # Shannon entropy H(t) in bits
```

Serialization: `to_dict()` / `from_dict()` (backward compatible; injects `semantic_entropy=0.0` for older records).

### `TerminologyExtractor`

Domain seed lexicons (partial list):

| Domain | Example Seeds |
|--------|---------------|
| `unit_of_individuality` | ant, nestmate, colony, superorganism, eusocial, individual, collective, organism |
| `behavior_and_identity` | behavior, caste, task, forager, nurse, soldier, identity, polyethism |
| `power_and_labor` | queen, worker, dominance, hierarchy, division of labor, subordinate, control |
| `sex_and_reproduction` | sex, reproduction, mating, haplodiploidy, queen, egg, sperm, parthenogenesis |
| `kin_and_relatedness` | kin, relatedness, altruism, inclusive fitness, nepotism, sibling |
| `economics` | cost, benefit, foraging, resource, allocation, efficiency, trade, investment |

Extraction: normalize → tokenize → match against domain seed sets → extend via co-occurrence proximity (3-token window) → deduplicate contexts → assign confidence. `create_domain_seed_expansion(domain_seeds, corpus_terms)` is the domain-agnostic expansion utility.

**Pipeline run results (sourced from `output/data/domain_statistics.json`):**

| Domain | Term Count | Total Frequency | Bridging Terms |
|--------|------------|-----------------|----------------|
| Power & Labor | 63 | 905 | 43 |
| Unit of Individuality | 73 | 769 | 2 |
| Sex & Reproduction | 64 | 605 | 26 |
| Behavior & Identity | 40 | 948 | 19 |
| Kin & Relatedness | 57 | 459 | 0 |
| Economics | 10 | 201 | 0 |
| **Total (all domains)** | **261** | — | — |

---

## Semantic Entropy (`src/analysis/semantic_entropy.py`)

### Constants

```python
HIGH_ENTROPY_THRESHOLD = 2.0  # bits; corresponds to ≥4 equiprobable senses
```

### `SemanticEntropyResult` Dataclass

```python
@dataclass
class SemanticEntropyResult:
    term: str
    entropy_bits: float            # Shannon H(t) in bits (base 2)
    n_clusters: int                # KMeans k actually used
    cluster_distribution: List[float]  # Empirical p(c_i) per cluster
    is_high_entropy: bool          # True if entropy_bits > 2.0
    n_contexts: int                # Valid contexts used
```

### `calculate_semantic_entropy`

```python
def calculate_semantic_entropy(
    term: str,
    contexts: List[str],
    max_clusters: int = 5,
    min_contexts: int = 5,
    random_state: int = 42,
    threshold: float = 2.0,
) -> SemanticEntropyResult
```

**Algorithm:**

1. Filter to contexts with ≥3 whitespace-delimited words.
2. If valid contexts < `min_contexts`: return H=0.0, n_clusters=1 (or 0 if empty).
3. TF-IDF: `TfidfVectorizer(stop_words="english", min_df=1, max_features=1000)`.
4. KMeans: `k = min(max_clusters, len(valid_contexts))`; if k < 2 return H=0.0.
5. `KMeans(n_clusters=k, random_state=42, n_init=10)` → labels.
6. Empirical distribution: $p_i = n_i / N$.
7. $H =$ `scipy.stats.entropy(probabilities, base=2)`.
8. Exception guard: any sklearn/scipy failure → H=0.0.

### Corpus-Level Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `calculate_corpus_entropy(terms_contexts, ...)` | `Dict[str, SemanticEntropyResult]` | Runs per-term entropy for all terms |
| `get_high_entropy_terms(results)` | `List[SemanticEntropyResult]` | Filters `is_high_entropy=True`, sorted descending by `entropy_bits` |
