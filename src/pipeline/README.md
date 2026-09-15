# pipeline

Pipeline stage modules for the Ento-Linguistics project — importable business
logic invoked by the thin-orchestrator scripts in `scripts/`.

## Contents
Files: `__init__.py`, `corpus_build.py`, `conceptual_mapping_pipeline.py`,
`discourse_pipeline.py`, `domain_analysis_pipeline.py`, `domain_figures.py`,
`literature_pipeline.py`, `rendering.py`, `reporting.py`, `simulation.py`

## Usage

```python
# Corpus building (stage 01 logic)
from pipeline.corpus_build import main
main(project_root=project_root)

# PDF rendering (pure helpers are unit-tested in tests/test_rendering.py)
from pipeline.rendering import build_pdf
build_pdf(strict_templates=True)
```

Each module pairs 1:1 with a thin orchestrator in `scripts/` (see
`scripts/README.md` for the full inventory and commands).
