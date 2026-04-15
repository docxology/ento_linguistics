# Project Source Code

Research-specific algorithms, data generation, and analysis functions for the Ento-Linguistic research project. This directory contains **36 modules** organized across **5 subpackage** directories.

## Directory Structure

```text
src/
├── __init__.py
├── analysis/              # Text analysis, NLP, and domain-specific modules
│   ├── cace_scoring.py        # CACE (Clarity, Appropriateness, Consistency, Evolvability) framework
│   ├── conceptual_mapping.py  # Concept maps, hierarchies, cross-domain bridges
│   ├── discourse_analysis.py  # Discourse pattern detection (hedging, authority, etc.)
│   ├── discourse_patterns.py  # Argumentative structure extraction
│   ├── domain_analysis.py     # Six-domain Ento-Linguistic framework analysis
│   ├── performance.py         # Convergence analysis, complexity estimation, benchmarking
│   ├── persuasive_analysis.py # Persuasive technique detection and effectiveness
│   ├── rhetorical_analysis.py # Rhetorical strategy quantification
│   ├── semantic_entropy.py    # TF-IDF + KMeans + Shannon entropy for term ambiguity
│   ├── statistics.py          # Welch t-test, ANOVA, Benjamini-Hochberg, confidence intervals
│   ├── term_extraction.py     # Automated terminology extraction with domain seeds
│   └── text_analysis.py       # NLP feature extraction (POS, readability, vocabulary)
├── core/                  # Core utilities, validation, metrics
│   ├── example.py             # Example arithmetic functions (template/testing)
│   ├── exceptions.py          # Custom exceptions with context and suggestions
│   ├── logging.py             # Structured logging with stage/progress tracking
│   ├── markdown_integration.py # Markdown section detection and figure insertion
│   ├── metrics.py             # Scientific metrics: RMSE, PSNR, SSIM, SNR, coherence
│   ├── parameters.py          # Parameter management with constraints, sweeps, serialization
│   ├── validation.py          # Validation framework (bounds, sanity, convergence, markdown)
│   └── validation_utils.py    # Infrastructure validation wrappers (markdown, figures, PDF)
├── data/                  # Data loading, generation, literature mining
│   ├── data_generator.py      # Synthetic data generation with configurable distributions
│   ├── data_processing.py     # Data cleaning, normalization, outlier removal
│   ├── literature_mining.py   # PubMed/arXiv API miners with caching
│   └── loader.py              # Corpus loading from files and data directories
├── pipeline/              # Simulation and reporting
│   ├── reporting.py           # Report generation (Markdown, LaTeX, HTML, JSON)
│   └── simulation.py          # Configurable simulation engine with checkpointing
└── visualization/         # Visualization and figure generation
    ├── concept_visualization.py  # Concept maps, terminology networks, domain visualizations
    ├── figure_manager.py         # Figure registry with cross-referencing and validation
    ├── plots.py                  # Core plotting utilities (convergence, comparison, etc.)
    ├── statistical_visualization.py # Statistical plots (distributions, correlations, heatmaps)
    └── visualization.py          # Multi-panel figure engine with configurable layouts
```

## Key Analytical Components

### CACE Scoring Framework (`analysis/cace_scoring.py`)
Four-dimension evaluation protocol for terminological quality:
- **Clarity**: Inverse of semantic entropy (low ambiguity = high clarity)
- **Appropriateness**: Penalizes anthropomorphic terms (queen, worker, slave, etc.)
- **Consistency**: Cross-context usage stability via cosine similarity
- **Evolvability**: Multi-domain and multi-scale applicability

### Semantic Entropy (`analysis/semantic_entropy.py`)
Information-theoretic measure of term ambiguity:
1. Extract usage contexts via sliding window
2. Compute TF-IDF vectors for each context
3. Cluster contexts via KMeans (k = min(5, |contexts|))
4. Calculate Shannon entropy over cluster distribution

### Six-Domain Framework (`analysis/domain_analysis.py`)
Decomposes entomological terminology into analytically tractable themes:
1. Unit of Individuality
2. Behavior & Identity
3. Power & Labor
4. Sex & Reproduction
5. Kin & Relatedness
6. Economics

## Key Principles

- **No mocks** - all functions use real computations and data
- **Deterministic** - reproducible results with fixed seeds (`random_state=42`)
- **Tested** - 90%+ test coverage required for all modules
- **Thin orchestrator** - scripts import from here; no business logic in scripts

## Usage in Scripts

```python
from analysis.term_extraction import TerminologyExtractor
from analysis.domain_analysis import DomainAnalyzer
from analysis.cace_scoring import evaluate_term_cace
from visualization.concept_visualization import ConceptVisualizer

extractor = TerminologyExtractor()
terms = extractor.extract_terms(texts)
cace = evaluate_term_cace("queen", contexts, domains=["Power & Labor"])
```

## Testing

```bash
cd /path/to/ento_linguistics
.venv/bin/python -m pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90
```

## See Also

- [AGENTS.md](AGENTS.md) - Detailed module documentation
- [../tests/](../tests/) - Test suite
- [../scripts/](../scripts/) - Analysis scripts
