# Agent integration context

Ento-Linguistics analyzes stored scientific text through five flat Python packages under `src/`. It provides candidate extraction, six overlapping domain labels, document co-occurrence networks, predefined concept-category overlap, context-cluster entropy, and heuristic CACE/framing indicators. These outputs are descriptive proxies; they do not establish human judgments or causal effects.

## Execute a real example

Run from the repository root with the locked environment and selected NLTK resources installed as described in [setup](docs/guides/setup.md):

```bash
PYTHONPATH=src uv run python - <<'PYTHON'
from analysis.term_extraction import TerminologyExtractor
from analysis.conceptual_mapping import ConceptualMapper

texts = [
    "The queen and worker ants belong to a colony.",
    "Worker ants share colony tasks with nestmates.",
]
terms = TerminologyExtractor().extract_terms(texts, min_frequency=1)
concept_map = ConceptualMapper().build_concept_map(terms)
print(len(terms), len(concept_map.concepts))
PYTHON
```

`build_concept_map` requires the dictionary of `Term` objects returned by the extractor; a list of `(name, term)` pairs is rejected. The example is a controlled demonstration, not a corpus result. Concept categories are predefined; terminology-network edges use shared documents when a source corpus is provided.

## Maintenance and verification

Follow [project guidance](AGENTS.md), [source architecture](src/README.md), and the affected package guidance. Use real text/files/local HTTP, fixed seeds, and demonstrably failing controls. Keep corpus layers separate and preserve source provenance. [Workflow](docs/guides/workflow.md) describes generation, custody auditing, caches, and strict rendering; [reproducibility](docs/reference/reproducibility.md) defines the measurement limits. [Verification](docs/reference/verification.md) distinguishes the unpublished working draft from archived publications.
