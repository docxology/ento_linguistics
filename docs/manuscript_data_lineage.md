# Manuscript Data Lineage: `src/` to `docs/manuscript/`

This document details precisely how the components of the analytical pipeline (`src/`) structure, populate, and dictate the final contents of the academic PDF (`docs/manuscript/`). Every figure, injected statistic, and API reference traces back directly to validated source code mechanisms.

## Source Code (`src/`) Components

The Ento-Linguistic framework organizes its operational logic into the following packages:

- **`src/__init__.py`**: Marks the source directory as a Python package, exporting top-level versioning and metadata accessible to the orchestration scripts.
- **`src/AGENTS.md` & `src/README.md`**: Foundational documentation governing code conventions and the modular architecture. These guides dictate the API structure, which directly feeds the auto-generated components of the manuscript.
- **`src/ento_linguistic_research.egg-info`**: Packaging metadata generated during local installation (`uv pip install -e .`), enabling scripts to resolve `src.*` absolute imports.
- **`src/data` / `src/pipeline`**:
  - `data` handles data generation, corpus loading, and text scrubbing.
  - `pipeline` orchestrates the flow of data through analysis and reporting tools.
  - *Manuscript Injection*: Together, these generate `output/data/corpus_statistics.json`, which pushes raw baseline metrics (e.g., token counts, document counts) into the abstract, methodology, and results via `{{CORPUS_*}}` template variables.
- **`src/analysis`**: Performs term extraction, semantic entropy calculation, CACE scoring, and discourse pattern identification.
  - *Manuscript Injection*: Powers the domain metrics and analytical relationships. It outputs metrics like `term_frequencies`, `domain_assignments`, and `entropy` to JSON files, dynamically injecting the values `{{CORPUS_CANDIDATE_TERMS}}` and `{{CORPUS_DOMAIN_TERMS}}` into the manuscript text.
- **`src/core`**: Supplies centralized logging, metric definitions, and exception handling. Serves as the backbone ensuring deterministic runs, meaning figures and counts generated for the manuscript are reproducible.
- **`src/visualization`**: Implements matplotlib/seaborn plot generators for concept mapping, statistical distributions, and network graphs.
  - *Manuscript Injection*: Writes the figure assets under `output/figures/` that the manuscript references via `\includegraphics`. Enforces manuscript requirements like 16pt font floors.

## Manuscript (`docs/manuscript/`) Linkages

The rendered PDF is a compilation of the following files, populated strictly by the `src/` pipeline output:

### Core Text (01–08)

- **`01_abstract.md` & `02_introduction.md`**: Define the scope and background of the research. These consume pipeline-injected counts (`{{CORPUS_PUBLICATIONS}}`, `{{CORPUS_TOTAL_TOKENS}}`) created by `src/data` and `src/pipeline`.
- **`03_methods.md`**: Provides the mathematical formulation behind the python files in `src/analysis/`. All equations reflect the literal computational implementations.
- **`04a_corpus_and_networks.md`**: Hosts corpus-level results, terminology network figures (`terminology_network.png`, `domain_overlap_heatmap.png`, `anthropomorphic_framing.png`), and framing analysis. Textual analysis derives exclusively from the pipeline JSON outputs.
- **`04b_domain_findings.md`**: Domain-by-domain findings with domain-specific figures (`concept_hierarchy.png`, `domain_overview_grid.png`, `domain_patterns_grid.png`) and longitudinal case studies.
- **`05_discussion.md` & `06_conclusion.md`**: Distills the outcomes from `src/analysis` into theoretical takeaways regarding anthropomorphic terminology and the Active Inference framework. Corpus-derived statistics use the same `{{KEY}}` mechanism as the rest of the manuscript.
- **`07_related_work.md` & `08_acknowledgments.md`**: Situate the findings within the existing literature and acknowledge institutional support. Provide the cross-reference keys resolved against `references.bib`.

### Supplemental Material (S01–S04)

- **`S01a_text_and_extraction.md`**: Bridges the paper and the code for text processing, term extraction, and semantic entropy. Maps equations to exact Python files and classes (e.g., `src/analysis/semantic_entropy.py::calculate_semantic_entropy`).
- **`S01b_analysis_infrastructure.md`**: Documents statistical, scoring (CACE), rhetorical analysis, visualization, and core infrastructure modules.
- **`S02_supplemental_results.md`**: Provides the deep-dive statistics, ANOVA derivations, and granular CACE scoring distributions that overflow the core results section. All metrics trace to `src/analysis` outputs.
- **`S03a_theoretical_extensions.md`**: Theoretical extensions (Markov Blankets, discourse frameworks, ambiguity classification, network analysis).
- **`S03b_case_studies.md` & `S04_supplemental_applications.md`**: Case studies, validation frameworks, and worked examples of the pipeline applied to outside fields.

### Reference & Metadata Files

- **`98_symbols_glossary.md`**: Mathematical notation and theoretical term definitions (maintained as markdown tables; not auto-generated from `src/`).
- **`99_references.md` & `references.bib`**: Maintain LaTeX citation formats. The pipeline's PDF builder (`_render_pdf_override.py`) uses pandoc and `bibtex` to resolve citations cleanly into the references section.
- **`AGENTS.md` & `README.md`**: Internal documentation governing the structural components and editing behavior of the manuscript directory itself.
- **`config.yaml` & `config.yaml.example`**: Standardized parameter files. They define the document title, authors, DOI, and keywords fed into the LaTeX front matter during build.
- **`preamble.md` & `preamble.tex`**: The rendering engine. `preamble.tex` maintains the typography, margins, coloring, and `fancyvrb`/`listings` code block parsing rules used centrally by `_render_pdf_override.py`.

## Template injection (`_render_pdf_override.py`)

The combined markdown is built by `projects/ento_linguistics/scripts/_render_pdf_override.py`. **`_load_corpus_vars()`** reads JSON from `data/corpus/` and `output/data/` and returns a dict of `{{KEY}}` → string value. **`_apply_corpus_vars()`** substitutes those placeholders into each manuscript section before Pandoc runs. Optional **strict** mode (`--strict-templates` or `STRICT_TEMPLATE_VARS=1`) fails the build if any `{{KEY}}` remains after substitution, preventing silent drift in CI.

## Validation Guarantee

Every statistical claim, reference, and figure in the compiled manuscript operates under a "no phantom data" guarantee:

1. Corpus-derived integers and floats in the main sections and supplemental materials (S01–S03) are pipeline-driven `{{KEY}}` placeholders populated at PDF build time from `output/data/*.json` (not hardcoded literals).
2. All visualizations (`output/figures/*.png`) are regenerated from scratch by `src/visualization` via `02_generate_figures.py` when the full analysis pipeline runs.
3. Sections that are purely theoretical (equations, literature positioning) or illustrative case-study text may omit corpus numbers by design; `S04_supplemental_applications.md` is reserved for optional extensions and is not part of the default combined build list in `_render_pdf_override.py`.
