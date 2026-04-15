# Skill Descriptor — Ento-Linguistic Research Project

## Project Overview

Research project examining the entanglement of speech and thought in entomology. Investigates how scientific terminology creates conceptual frameworks across six Ento-Linguistic domains.

## Capabilities

- **Terminology Extraction**: Extract domain-specific terms from entomological literature
- **Domain Analysis**: Analyze terminology patterns across six core domains (Unit of Individuality, Behavior & Identity, Power & Labor, Sex & Reproduction, Kin & Relatedness, Economics)
- **Concept Mapping**: Build and visualize concept networks with similarity analysis and centrality metrics
- **Discourse Analysis**: Quantitative rhetorical pattern analysis and framing effect measurement
- **CACE Scoring**: Evaluate terminology using Clarity, Appropriateness, Consistency, Evolvability framework
- **Literature Mining**: Collect and process scientific literature from PubMed

## Use Cases

1. **Analyze entomological terminology**: Use `src/analysis/term_extraction.py` to extract domain-specific terms
2. **Build concept networks**: Use `src/analysis/conceptual_mapping.py` for network construction
3. **Run analysis pipeline**: Execute `scripts/01_build_corpus.py` then `scripts/02_generate_figures.py`
4. **Validate manuscript**: Run `scripts/_manuscript_preflight.py --strict`

## Integration Points

- Requires Python 3.10+, numpy, scipy, pandas, matplotlib, spacy, networkx
- Test coverage: 90%+ required
- Uses pytest-httpserver for HTTP testing (no mocks)

## Current Status

- **Location**: `projects_in_progress/ento_linguistics/` (not yet active in pipeline)
- **Tests**: 1013 passing
- **Coverage**: 90.3%
- **Figures**: 11 generated

## Promotion to Active

To move to `projects/` for pipeline execution:
```bash
mv projects_in_progress/ento_linguistics projects/ento_linguistics
```

## See Also

- [`AGENTS.md`](AGENTS.md) - Full project documentation
- [`docs/README.md`](docs/README.md) - Quick reference guide
- [`src/AGENTS.md`](src/AGENTS.md) - Scientific code documentation