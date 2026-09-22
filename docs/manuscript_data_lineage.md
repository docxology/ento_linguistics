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
- **`src/pipeline/statistics_pipeline.py`** (statistics stage): orchestrated by `src/visualization/manuscript_figures.py::main()` between the analysis pipeline and figure generation; computes Welch $t$-tests (Benjamini–Hochberg corrected, Cohen's $d$) and a one-way ANOVA from per-term domain entropies and writes `output/data/statistical_analysis.json` (frozen schema: `descriptives`, `pairwise`, `anova`, `corrections`, plus the corpus-level `discourse` section — patterns, rhetorical, argumentative, persuasive — merged into both layer artifacts by the figure orchestrator's discourse stage and exposed as the `ABSTRACT_*`/`FULLTEXT_*` discourse token families).
- **`src/pipeline/fulltext_pipeline.py`** (full-text parallel layer): applies the same frozen statistics schema to the PMC Open Access full-text corpus (shards `data/fulltexts/fulltexts_NNNNN.json`, loaded in order) via the shared `build_statistical_analysis` machinery, adding the parallel-layer markers (`layer`, `n_documents`, per-document `token_count`, `domain_term_counts`, and the stage's `corpus_fingerprint`). Orchestrated by the full-text stage in `src/visualization/manuscript_figures.py::main()` (after the statistics stage; failure warns and continues). The stage is guarded by a **corpus fingerprint** (record count + provenance SHA-256, see `manuscript_figures._ensure_fulltext_artifact`): the existing artifact is reused when its fingerprint matches the current corpus, and rebuilt — **full corpus by default** (`FULLTEXT_ANALYSIS_LIMIT` bounds quick runs; a bounded run stores its limit inside the fingerprint so it can never satisfy the full-corpus guard) — otherwise. Writing `output/data/fulltext_analysis.json`, rendering `fulltext_analysis.png` (registered as `fig:fulltext_analysis`), and — when both layer artifacts exist — `layer_comparison.png` (registered as `fig:layer_comparison`, produced by `visualization/statistical_visualization.py::plot_layer_comparison`).
- **`src/pipeline/bhl_analysis.py`** (BHL historical layer, era-stratified): consumes the `data/bhl/` shard corpus (2,460 ant/myrmecology texts across three eras — 1013/1247/200 documents in 1850-1899 / 1900-1949 / 1950-1970 — harvested by `src/data/bhl_corpus.py` from the BHL mirror collection on the Internet Archive) and computes per-era normalized term frequencies (per 10k tokens) for the six canonical domain seed vocabularies **plus a per-era full linguistic stack** — OCR-cleaned `TerminologyExtractor` extraction (`extraction`), bounded top-20 per-term semantic entropy (`entropy`), and occurrence-context anthropomorphic-framing proportions (`framing`) — into `data/bhl/era_term_usage.json`. Feeds the `BHL_*` manuscript token family (`BHL_DOCUMENTS`, `BHL_<ERA>_<TERM>_PER_10K` for 18 canonical domain-seed terms, and the expanded-era tokens `BHL_ERA_<ERA>_TERMS`/`BHL_ERA_<ERA>_ENTROPY_MEAN`/`BHL_ERA_<ERA>_FRAMING`) emitted by `core/manuscript_variables.py::build_statistical_tokens`, grounding the S03b era narratives.
- **`src/data/arxiv_corpus.py`** (arXiv preprint layer): harvests arXiv preprints (`q-bio.PE`/`nlin.AO` categories) into `data/corpus/arxiv_records.json` with a SHA-256-keyed provenance sidecar (`arxiv_provenance.json`); a **separate source layer** documented as not merged into `abstracts.json`. Consumed by analysis notebooks/pipelines that concatenate layers; no manuscript tokens depend on it yet.
- **`src/data/openalex_enrichment.py`** (citation enrichment): resolves every DOI-bearing corpus record against the OpenAlex API into `data/corpus/citation_metadata.json` (keyed by abstract SHA-256; explicit `not_found`/`error` entries; resumable). No manuscript tokens depend on it yet.
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
- **`S02_supplemental_results.md`**: Provides the deep-dive statistics, ANOVA derivations, and granular CACE scoring distributions that overflow the core results section. All metrics trace to `src/analysis` outputs. The inferential tables (pairwise Welch $t$-tests, ANOVA) are produced by the statistics stage (`src/pipeline/statistics_pipeline.py`) from per-term entropies into `output/data/statistical_analysis.json`; that artifact is consumed both by the `statistical_analysis.png` figure and by the `ANOVA_*`/`PAIRWISE_*`/`CORRECTION_METHOD`/`PAIRWISE_N_COMPARISONS` manuscript tokens substituted into the S02 tables. The "Full-Text Parallel Layer" subsection is token-driven from `output/data/fulltext_analysis.json` via the `FULLTEXT_*` family (documents, token counts, per-domain descriptives, framing proportions, ANOVA/pairwise). The "Discourse and Rhetorical Layer" subsection is token-driven from both artifacts' `discourse` sections via the `ABSTRACT_*`/`FULLTEXT_*` discourse token families (`DISCOURSE_N_ANALYZED`, `DISCOURSE_SAMPLE_FRACTION`, `PATTERNS_*`, `RHETORICAL_*`, `ARG_STRUCTURES`, `PERSUASIVE_METAPHORICAL`), whose comparison figure is `discourse_comparison.png` (`fig:discourse_comparison`, rendered by the full-text stage when both artifacts exist).
- **`S03a_theoretical_extensions.md`**: Theoretical extensions (Markov Blankets, discourse frameworks, ambiguity classification, network analysis).
- **`S03b_case_studies.md` & `S04_supplemental_applications.md`**: Case studies, validation frameworks, and worked examples of the pipeline applied to outside fields. S03b's era narratives (caste terminology evolution, superorganism concept evolution) are grounded in the BHL historical layer: document counts and per-era term frequencies (per 10k tokens) resolve from `data/bhl/era_term_usage.json` via the `BHL_*` token family (see `src/pipeline/bhl_analysis.py`).

### Reference & Metadata Files

- **`98_symbols_glossary.md`**: Mathematical notation and theoretical term definitions (maintained as markdown tables; not auto-generated from `src/`).
- **`99_references.md` & `references.bib`**: Maintain LaTeX citation formats. The pipeline's PDF builder (`_render_pdf_override.py`) uses pandoc and `bibtex` to resolve citations cleanly into the references section.
- **`AGENTS.md` & `README.md`**: Internal documentation governing the structural components and editing behavior of the manuscript directory itself.
- **`config.yaml` & `config.yaml.example`**: Standardized parameter files. They define the document title, authors, DOI, and keywords fed into the LaTeX front matter during build.
- **`preamble.md` & `preamble.tex`**: The rendering engine. `preamble.tex` maintains the typography, margins, coloring, and `fancyvrb`/`listings` code block parsing rules used centrally by `_render_pdf_override.py`.

## Template injection (`_render_pdf_override.py`)

The combined markdown is built by `projects/ento_linguistics/scripts/_render_pdf_override.py`. **`_load_corpus_vars()`** reads JSON from `data/corpus/` and `output/data/` and returns a dict of `{{KEY}}` → string value. **`_apply_corpus_vars()`** substitutes those placeholders into each manuscript section before Pandoc runs. Optional **strict** mode (`--strict-templates` or `STRICT_TEMPLATE_VARS=1`) fails the build if any `{{KEY}}` remains after substitution, preventing silent drift in CI. The inferential tokens (`ANOVA_METRIC`, `ANOVA_F`, `ANOVA_DF1`, `ANOVA_DF2`, `ANOVA_P`, `ANOVA_ETA_SQUARED`, `CORRECTION_METHOD`, `PAIRWISE_N_COMPARISONS`, and per-pair `PAIRWISE_<SLUG_A>_<SLUG_B>_{T,P,P_BH,D,SIGNIFICANT}`) are populated from `output/data/statistical_analysis.json`. The same shared builder (`core.manuscript_variables.build_statistical_tokens`, also called by the renderer's `_load_corpus_vars`) additionally emits the `FULLTEXT_*` family (`FULLTEXT_DOCUMENTS`, `FULLTEXT_TOTAL_TOKENS`, `FULLTEXT_MEDIAN_TOKENS`, `FULLTEXT_DOMAIN_<SLUG>_TERMS`, `FULLTEXT_DOMAIN_<SLUG>_ENTROPY`, `FULLTEXT_PAIRWISE_N`, `FULLTEXT_ANOVA_F`, `FULLTEXT_ANOVA_P`) from `output/data/fulltext_analysis.json` when that artifact exists — absent artifact yields no tokens, never a KeyError.

## Validation Guarantee

Every statistical claim, reference, and figure in the compiled manuscript operates under a "no phantom data" guarantee:

1. Corpus-derived integers and floats in the main sections and supplemental materials (S01–S03) are pipeline-driven `{{KEY}}` placeholders populated at PDF build time from `output/data/*.json` (not hardcoded literals).
2. All visualizations (`output/figures/*.png`) are regenerated from scratch by `src/visualization` via `02_generate_figures.py` when the full analysis pipeline runs.
3. Sections that are purely theoretical (equations, literature positioning) or illustrative case-study text may omit corpus numbers by design; `S04_supplemental_applications.md` is reserved for optional extensions and is not part of the default combined build list in `_render_pdf_override.py`.
