# manuscript/ - Research Manuscript

Research manuscript sections in markdown format, converted to PDFs.

## Quick Start

**Citations (Pandoc + natbib):** use `[@citationKey]` in markdown for parenthetical *(Author, year)* citations; use `@citationKey` without brackets for narrative *Author (year)* form. Keys must exist in `references.bib`. The PDF build loads `natbib` with `round,comma,sort&compress` and uses the `plainnat` bibliography style (from the Pandoc LaTeX template). Red hyperlinks are applied in `_render_pdf_override.py` after Pandoc (Pandoc’s default `hidelinks` would otherwise override `preamble.tex`).

### Edit Manuscript

```bash
vim manuscript/02_introduction.md
vim manuscript/S01a_text_and_extraction.md
```

### Build PDFs

```bash
# Recommended: Full pipeline (tests + analysis + PDF + validation)
python3 scripts/execute_pipeline.py --core-only

# Or use interactive menu
./run.sh

# Render PDF only (after tests and analysis)
python3 scripts/03_render_pdf.py

# View output
open output/pdf/project_combined.pdf
# Or
open project/output/pdf/project_combined.pdf
```

## Manuscript Structure

This project includes the following sections:

### Main Sections

- `01_abstract.md` - Research overview and key contributions
- `02_introduction.md` - Project structure and motivation
- `03_methods.md` - Methods: mixed-methodology framework
- `04a_corpus_and_networks.md` - Results: corpus analysis and terminology networks
- `04b_domain_findings.md` - Results: domain-specific findings
- `05_discussion.md` - Theoretical implications and comparisons
- `06_conclusion.md` - Summary and future work
- `07_related_work.md` - Literature review and positioning
- `08_acknowledgments.md` - Funding and acknowledgments

### Supplemental Materials

- `S01a_text_and_extraction.md` - Supplemental methods: text processing and term extraction
- `S01b_analysis_infrastructure.md` - Supplemental methods: statistical and scoring infrastructure
- `S02_supplemental_results.md` - Additional experimental results
- `S03a_theoretical_extensions.md` - Supplemental analysis: theoretical extensions
- `S03b_case_studies.md` - Supplemental analysis: case studies and validation

### Supporting Files

- `references.bib` - Bibliography entries in BibTeX format
- `99_references.md` (~1.4 KB) - References section (auto-generated from .bib)
- `98_symbols_glossary.md` - Notation and terminology glossary (manually curated)

### Configuration

- `config.yaml` - Paper metadata (title, authors, DOI)
- `preamble.md` - LaTeX preamble customizations

## Rendering Process

The manuscript is rendered through these stages:

1. **Discovery**: All `.md` and `.tex` files are discovered and categorized
2. **Individual Rendering**: Each section rendered to PDF separately
3. **Combination**: All sections combined into single manuscript PDF
4. **Output**: Generated files placed in `../output/pdf/`

View detailed rendering logs to see which sections were included.

## Template variables (corpus-driven numbers)

Numeric results that depend on the analyzed corpus (token counts, network metrics, domain statistics, per-term frequencies, concept map counts) are **not** written as literals in the manuscript. They use `{{KEY}}` placeholders substituted at PDF build time by `scripts/_render_pdf_override.py` (`_load_corpus_vars` reads `data/corpus/` and `output/data/*.json`; `_apply_corpus_vars` performs the replacement).

**Workflow:** run the analysis pipeline (or `scripts/02_generate_figures.py` as part of it) so `output/data/` matches the run you intend to cite, then build the PDF.

**CI / fail-closed builds:** set `STRICT_TEMPLATE_VARS=1` or pass `--strict-templates` to `scripts/_render_pdf_override.py` so any unresolved `{{KEY}}` after substitution exits non-zero. See `manuscript/AGENTS.md` for the variable families (`CORPUS_*`, `NETWORK_*`, `DOMAIN_*`, `TERM_FREQ_*`, `EXTRACTED_TERM_FREQ_*`, `CONCEPT_*`, etc.).

## File Structure

### Main Sections (01-09)

- `01_abstract.md` - Research overview
- `02_introduction.md` - Project structure
- `03_methods.md` - Methods
- `04a_corpus_and_networks.md` - Results: corpus and networks
- `04b_domain_findings.md` - Results: domain findings
- `05_discussion.md` - Theoretical implications
- `06_conclusion.md` - Summary and future work
- `07_related_work.md` - Literature review and positioning
- `08_acknowledgments.md` - Funding and acknowledgments

### Supplemental Sections (S01-S0N)

- `S01a_text_and_extraction.md` - Text processing and term extraction
- `S01b_analysis_infrastructure.md` - Statistical and scoring infrastructure
- `S02_supplemental_results.md` - Additional experimental results
- `S03a_theoretical_extensions.md` - Theoretical extensions
- `S03b_case_studies.md` - Case studies and validation

### Reference Sections (98-99)

- `98_symbols_glossary.md` - Symbols and notation glossary
- `99_references.md` - Bibliography (always last)

### Supporting Files

- `preamble.md` - LaTeX configuration (no PDF)
- `references.bib` - BibTeX bibliography
- `config.yaml` - Paper metadata configuration (version-controllable)
- `config.yaml.example` - Configuration template

## Numbering Convention

**Main sections:** 01-09 (core manuscript)
**Supplemental sections:** S01-S0N (additional material)
**Reference sections:** 98 (glossary), 99 (bibliography - always last)

**Adding new sections:**

- Main: Use next number (e.g., `07_new_section.md`)
- Supplemental: Use next S## (e.g., `S03_new_supplement.md`)
- Keep references as `99_references.md`
- Keep glossary as `98_symbols_glossary.md`

## Cross-Referencing

### Sections

```markdown
## Introduction {#sec:intro}
See \ref{sec:intro} for details.
See \ref{sec:supplemental_methods} for extended methods.
```

### Equations

```markdown
\begin{equation}
\label{eq:myeq}
f(x) = x^2
\end{equation}
Using \eqref{eq:myeq}...
```

### Figures

```markdown
\begin{figure}[h]
\includegraphics[width=0.8\textwidth]{../output/figures/concept_map.png}
\caption{Conceptual map of Ento-Linguistic domains generated by scripts/generate_research_figures.py.}
\label{fig:concept_map}
\end{figure}
See \ref{fig:concept_map}...
```

## Configuration

### Method 1: Configuration File (Recommended)

Edit `config.yaml` in the `manuscript/` directory:

```yaml
paper:
  title: "My Research Paper"

authors:
  - name: "Dr. Jane Smith"
    orcid: "0000-0000-0000-1234"
    email: "jane@example.edu"
    affiliation: "University of Example"
    corresponding: true

publication:
  doi: "10.5281/zenodo.12345678"  # Optional
```

See `config.yaml.example` for all available options.

### Method 2: Environment Variables (Alternative)

```bash
export AUTHOR_NAME="Dr. Jane Smith"
export PROJECT_TITLE="My Research"
export AUTHOR_EMAIL="jane@example.edu"
python3 scripts/03_render_pdf.py
```

**Priority**: Environment variables override config file values.

## Validation

```bash
# Check markdown
python3 -m infrastructure.validation.cli markdown project/manuscript/

# Check PDF
python3 -m infrastructure.validation.cli pdf project/output/pdf/
```

## Quality Validation

- Run `python3 project/scripts/manuscript_preflight.py --strict` before rendering to ensure figures, glossary markers, and references are present.
- Generate consolidated metrics with `python3 project/scripts/quality_report.py` (readability, integrity, reproducibility snapshots).
- Figure registry and anchors are validated with `validate_figure_registry` and `validate_markdown` as part of the pipeline.

## Section Ordering

The build system automatically orders sections:

1. **Main sections** (`01`--`08`) - Core manuscript (this project: Conclusion = `06`, Related Work = `07`)
2. **Supplemental sections** (S01-S0N) - Additional material
3. **Glossary** (98) - Symbols and notation
4. **References** (99) - Bibliography (always last)

This ensures proper document flow with supplemental material clearly separated from main content.

## Citation Management

### Adding Citations

1. Add the bibliography entry to `references.bib`:

```bibtex
@article{mykey2024,
  title={Paper Title},
  author={Author, Name},
  journal={Journal Name},
  year={2024}
}
```

1. Cite in markdown using `\cite{}`:

```markdown
According to recent research \cite{mykey2024}, this technique...
```

### Bibliography Processing

- Citations are processed using **BibTeX** with the `plainnat` style (author--year reference list; use Pandoc `[@key]` for parenthetical in-text form where appropriate)
- The bibliography file (`references.bib`) is copied into the build directory to satisfy BibTeX security constraints
- In-text citations are resolved by **natbib** during PDF compilation
- The References section lists entries from `references.bib` (plus `\nocite{*}` in `99_references.md` for completeness)

## Figure Management

### Adding Figures

1. Generate figures using scripts in `scripts/` (e.g., `generate_research_figures.py`)
2. Figures are saved to `../output/figures/`
3. Reference in markdown using LaTeX includegraphics:

```markdown
\includegraphics[width=0.9\textwidth]{../output/figures/domain_comparison.png}
Figure \ref{fig:domain_comparison} shows the relative frequency of entomological metaphors across four major scientific domains.
\label{fig:domain_comparison}
```

1. Add labels to your figures:

```markdown
\label{fig:convergence_plot}
```

### Figure Path Resolution

- Figure paths use relative references (`../output/figures/filename.png`)
- The rendering system resolves paths relative to the `project/` directory
- All referenced figures must exist before PDF generation

## Troubleshooting

### Citations showing as [?]

- Verify bibliography entry exists in `references.bib`
- Check for typos in citation keys (case-sensitive)
- Run `python3 scripts/execute_pipeline.py --core-only` to regenerate from scratch
- Or use `./run.sh` and select option 4 (full pipeline)

### Figures not appearing

- Verify file exists in `project/output/figures/`
- Check path references use correct relative paths
- Ensure image format is supported (PNG, PDF, JPG)

## See Also

- [`AGENTS.md`](AGENTS.md) - Detailed documentation
- [`../../.cursorrules/manuscript_style.md`](../../.cursorrules/manuscript_style.md) - manuscript formatting and style guide
- [`preamble.md`](preamble.md) - LaTeX configuration
- [`../../docs/MARKDOWN_TEMPLATE_GUIDE.md`](../../docs/MARKDOWN_TEMPLATE_GUIDE.md) - Full guide
