# docs/manuscript/ - Research Manuscript

## Purpose

The `docs/manuscript/` directory contains research manuscript sections in markdown format. These files are processed by `scripts/03_render_pdf.py` to generate individual section PDFs and a combined manuscript document.

## Template variables (corpus statistics)

The Ento-Linguistics PDF build uses **`scripts/_render_pdf_override.py`** (not the generic infrastructure renderer alone). Before Pandoc runs, **`_load_corpus_vars(project_root)`** reads JSON under `data/corpus/` and `output/data/` and returns a flat mapping; **`_apply_corpus_vars(content, vars_, strict=...)`** replaces every `{{KEY}}` in the concatenated markdown with the corresponding string.

**Sources of truth:** `abstracts.json` (publication count), `output/data/corpus_statistics.json`, `extracted_terms.json`, `domain_statistics.json`, `concept_map_summary.json`. Extended keys include per-domain `DOMAIN_<SLUG>_ENTROPY`, `_HIGH_ENTROPY_PCT`, `_ANTHROPOMORPHIC_PROPORTION_PCT`, per-concept `CONCEPT_<CONCEPT_SLUG>_TERMS`, network `NETWORK_*`, `CORPUS_TOP_TERM_1`…`5`, `TERM_FREQ_<TOKEN_SLUG>` (corpus top-token frequencies), and `EXTRACTED_TERM_FREQ_<SLUG>` for extraction-local lemma counts.

**Strict mode:** `build_pdf(strict_templates=True)`, the CLI flag `--strict-templates`, or environment variable `STRICT_TEMPLATE_VARS=1`/`true`/`yes` causes an unresolved placeholder after substitution to print to stderr and **`sys.exit(1)`** (use in CI to catch missing keys).

**Editing rule:** any number that should track the latest pipeline run must be a `{{KEY}}` present in `_load_corpus_vars`; do not duplicate corpus statistics as literals in markdown.

## File Structure

### Manuscript Sections (Generate PDFs)

| File | Purpose | Generates PDF |
|------|---------|---------------|
| `01_abstract.md` | Research overview and key contributions | ✅ |
| `02_introduction.md` | Project structure and motivation | ✅ |
| `03_methods.md` | Methods: mixed-methodology framework | ✅ |
| `04a_corpus_and_networks.md` | Results: corpus analysis and terminology networks | ✅ |
| `04b_domain_findings.md` | Results: domain-specific findings | ✅ |
| `05_discussion.md` | Theoretical implications and comparisons | ✅ |
| `06_conclusion.md` | Summary and future directions | ✅ |
| `07_related_work.md` | Literature review and positioning | ✅ |
| `08_acknowledgments.md` | Funding, collaborators, and acknowledgments | ✅ |

| **Supplemental Sections** | | |
| `S01a_text_and_extraction.md` | Supplemental methods: text processing and term extraction | ✅ |
| `S01b_analysis_infrastructure.md` | Supplemental methods: statistical and scoring infrastructure | ✅ |
| `S02_supplemental_results.md` | Additional experimental results | ✅ |
| `S03a_theoretical_extensions.md` | Supplemental analysis: theoretical extensions | ✅ |
| `S03b_case_studies.md` | Supplemental analysis: case studies and validation | ✅ |
| `S04_supplemental_applications.md` | *(removed — content was speculative)* | — |
| **Reference Sections** | | |
| `98_symbols_glossary.md` | Mathematical notation and domain terminology glossary | ✅ |
| `99_references.md` | Bibliography and cited works (always last) | ✅ |

### Supporting Files (No PDF Generation)

| File | Purpose |
|------|---------|
| `preamble.md` | LaTeX preamble and document styling |
| `references.bib` | BibTeX bibliography database |
| `config.yaml` | Paper metadata configuration (title, authors, DOI, etc.) |
| `config.yaml.example` | Configuration template with all options documented |

## Numbering Convention

Files are numbered to control document ordering:

### Main Sections (01-09)

- `01-08`: Core manuscript sections (Abstract through Related Work; Conclusion is `06`, Related Work is `07`)
- `08`: Acknowledgments
- `09`: Appendix

### Supplemental Sections (S01-S0N)

- `S01-S99`: Supplemental material (methods, results, etc.)
- Prefix `S` identifies supplemental content
- Numbered sequentially: `S01`, `S02`, `S03`, etc.

### Reference Sections (98-99)

- `98`: Symbols and notation glossary (manually curated; not auto-generated)
- `99`: Bibliography (always last section)

**Ordering guarantees:**

1. Main sections (01-09) appear first
2. Supplemental sections (S01-S0N) appear after main content
3. References (99) always appears last
4. Glossary (98) appears just before references

**Adding new sections:**

- Main sections: Use next available number (e.g., `07_`, `10_`)
- Supplemental sections: Use next `S##` number (e.g., `S03_`, `S04_`)
- References: Always keep as `99_references.md`
- Glossary: Always keep as `98_symbols_glossary.md`

## preamble.md - LaTeX Styling

The `preamble.md` file contains LaTeX configuration wrapped in markdown code blocks:

```markdown
# LaTeX Preamble

```latex
\usepackage{amsmath}
\usepackage{graphicx}
% ... additional LaTeX commands ...
```

```

**Key features:**
- Custom LaTeX packages
- Document styling
- Mathematical notation setup
- Figure and table formatting
- Cross-reference configuration

**Note:** Does NOT generate a separate PDF - content is extracted and injected into document preambles.

## references.bib - Bibliography

BibTeX format bibliography file:

```bibtex
@article{author2023,
  title={Title},
  author={Author, Name},
  journal={Journal},
  year={2023},
  volume={1},
  pages={1-10}
}
```

Citations in markdown:

```markdown
According to \cite{author2023}, the method...
```

### Bibliography Processing Workflow

The citation system uses **BibTeX with plainnat style** for robust bibliography management:

**Processing Flow:**

1. Manuscript markdown files contain `\cite{key}` commands
2. During PDF rendering, Pandoc preserves these LaTeX citation commands (no `--citeproc`)
3. The `references.bib` file is **copied into the build directory** to satisfy BibTeX security constraints
4. XeLaTeX generates `.aux` file listing all citations
5. BibTeX processes the `.aux` file and generates `.bbl` (bibliography list) file
6. XeLaTeX performs multiple compilation passes to resolve all citations and cross-references

**Key Points:**

- Citation keys are **case-sensitive** (use exact keys from `references.bib`)
- All cited entries must exist in `references.bib`
- The References section uses `\bibliography{references}` and `\nocite{*}` commands in `99_references.md`
- Bibliography style is `plainnat` (natbib author--year in the reference list; in-text form depends on `\cite` vs `\citep` / Pandoc `[@key]` vs `@key`)

**Bibliography Security:**

- BibTeX operates in "paranoid" security mode by default
- It restricts file access across directories
- Solution: Copy `references.bib` into the compilation directory before running BibTeX
- This ensures all files are local to the execution context

## Cross-Referencing

### Section References

```markdown
## Introduction {#sec:introduction}

As discussed in \ref{sec:introduction}...

Supplemental methods in \ref{sec:supplemental_methods}...
```

### Equation References

```markdown
\begin{equation}
\label{eq:myequation}
f(x) = x^2
\end{equation}

Using \eqref{eq:myequation}, we derive...
```

### Figure References

```markdown
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{../output/figures/terminology_network.png}
\caption{Terminology network generated by the src/ analysis pipeline.}
\label{fig:terminology_network}
\end{figure}

As shown in \ref{fig:terminology_network}...
```

### Figure Insertion and Path Resolution

**Figure Storage:**

- All figures are generated to or placed in `output/figures/`
- Supported formats: PNG, PDF, JPG, JPEG

**Path References:**

- Use relative paths from the manuscript build directory (e.g., `../output/figures/domain_comparison.png`)
- Paths are resolved relative to the manuscript compilation directory
- The rendering system handles path resolution automatically

**Figure Generation Workflow:**

1. Scripts in `scripts/` generate figures to `output/figures/`
2. Figures are registered with `FigureManager` for cross-referencing
3. Markdown files include figures using the LaTeX includegraphics command with figure path
4. Figure labels use LaTeX label command with `fig:` prefix for cross-referencing
5. References use the LaTeX ref command pointing to figure labels

**Available Generated Figures:**

- `concept_map.png` - Conceptual map of Ento-Linguistic domains
- `terminology_network.png` - Cross-domain terminology co-occurrence network
- `domain_overlap_heatmap.png` - Szymkiewicz-Simpson overlap coefficient between domains
- `domain_comparison.png` - Cross-domain term frequency and metrics comparison
- `domain_overview_grid.png` - Top-10 terms per domain (3×2 grid)
- `domain_patterns_grid.png` - POS composition per domain (3×2 grid)
- `concept_hierarchy.png` - Hierarchical concept organization (Power & Labor)
- `anthropomorphic_framing.png` - Anthropomorphic framing analysis
- `unit_of_individuality_patterns.png` - Unit of Individuality domain analysis
- `power_and_labor_term_frequencies.png` - Term frequencies (Power & Labor)
- `power_and_labor_ambiguities.png` - Ambiguity patterns (Power & Labor)

**Figure Registry:**

- `output/figures/figure_registry.json` maintains a record of all generated figures
- Includes metadata for each figure (path, label, description)
- Used by validation systems to verify all figure references

### Table References

```markdown
\begin{table}[h]
\centering
\begin{tabular}{ll}
Item & Value \\
\hline
A & 1 \\
B & 2 \\
\end{tabular}
\caption{Example table.}
\label{tab:example}
\end{table}

Table \ref{tab:example} shows...
```

## LaTeX Integration

### Mathematical Notation

**Inline math:**

```markdown
The variable $x$ represents...
```

**Display equations:**

```markdown
\begin{equation}
\label{eq:name}
f(x) = \int_0^x t^2 dt
\end{equation}
```

**Do NOT use:**

- Double dollar signs for display math—use equation environment instead
- Backslash square brackets for display math—use equation environment instead

### Figure Integration

Figures must reference files in `output/figures/`:

```markdown
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/domain_comparison.png}
\caption{Cross-domain comparison of terminology characteristics.}
\label{fig:domain_comparison}
\end{figure}
```

**Requirements:**

- Path: `../output/figures/` (relative to docs/manuscript/)
- Generated by scripts in `scripts/`
- Registered with `FigureManager` for validation
- PNG format recommended
- Descriptive labels (e.g., `fig:convergence_plot`)

## 98_symbols_glossary.md - Notation and Terminology Reference

This file is a **manually curated** glossary containing:

- **Mathematical notation** — definitions of symbols used in equations (e.g., $H(t)$, $O_{ij}$, CACE sub-scores)
- **Module reference** — table mapping `src/` modules to their analysis functions and pipeline roles
- **Domain terminology** — the six Ento-Linguistic domains and their scope

The glossary cross-references equation labels defined in `03_methods.md` and `S03a_theoretical_extensions.md`. Update this file when adding new notation or modules.

## Building PDFs

### Individual Section PDFs

```bash
# Builds all individual section PDFs
python3 scripts/03_render_pdf.py
```

Output: `project/output/pdf/01_abstract.pdf`, `02_introduction.pdf`, `S01a_text_and_extraction.pdf`, etc.

### Combined Manuscript PDF

```bash
# Builds combined manuscript
python3 scripts/03_render_pdf.py
```

Output: `output/pdf/project_combined.pdf`

**Combined PDF includes:**

- Custom title page
- Abstract (before TOC)
- Table of contents
- All numbered main sections (01-09)
- All supplemental sections (S01-S0N)
- API glossary (98)
- Bibliography (99, always last)

## Editing Workflow

### 1. Edit Markdown Files

Edit any `*.md` file in `docs/manuscript/` directory:

```bash
vim docs/manuscript/02_introduction.md
vim docs/manuscript/S01a_text_and_extraction.md
```

### 2. Generate Figures (if needed)

If adding new figures, create script in `scripts/`:

```
# scripts/my_figure.py
from example import calculate_average
# ... generate figure ...
plt.savefig("output/figures/my_figure.png")
```

### 3. Reference Figure in Markdown

```markdown
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{../output/figures/domain_comparison.png}
\caption{Cross-domain comparison of terminology characteristics.}
\label{fig:domain_comparison_example}
\end{figure}
```

### 4. Validate and Build

```bash
# Clean previous outputs  
python3 scripts/execute_pipeline.py --clean

# Build everything (recommended)
python3 scripts/execute_pipeline.py --core-only

# Or run individual stages
python3 scripts/03_render_pdf.py
```

### 5. Review Output

```bash
# Open combined PDF
open output/pdf/project_combined.pdf

# Or HTML version (better for IDEs)
open output/project_combined.html
```

## Adding New Sections

### Adding Main Sections

1. Create file with next available number:

   ```bash
   vim docs/manuscript/07_new_section.md
   ```

2. Include section header with label:

   ```markdown
   # New Section {#sec:newsection}
   
   Content here...
   ```

3. Build and verify ordering:

   ```bash
   python3 scripts/03_render_pdf.py
   ```

### Adding Supplemental Sections

1. Create file with `S##` prefix:

   ```bash
   vim docs/manuscript/S03_supplemental_figures.md
   ```

2. Include section header with label:

   ```markdown
   # Supplemental Figures {#sec:supplemental_figures}
   
   Extended figures and visualizations...
   ```

3. Reference from main text:

   ```markdown
   Additional results in \ref{sec:supplemental_figures}...
   ```

4. Build and verify:

   ```bash
   python3 scripts/03_render_pdf.py
   ```

## Configuration

### Configuration File (Recommended)

The manuscript configuration is managed through `project/docs/manuscript/config.yaml`, which provides a centralized, version-controllable way to manage all paper metadata.

**Location**: `docs/manuscript/config.yaml`

**Template**: `docs/manuscript/config.yaml.example` (copy and customize)

**Example configuration**:

```yaml
paper:
  title: "Advanced Research Framework"
  subtitle: ""  # Optional
  version: "1.0"

authors:
  - name: "Dr. Jane Smith"
    orcid: "0000-0000-0000-1234"
    email: "jane.smith@university.edu"
    affiliation: "University of Example"
    corresponding: true

publication:
  doi: "10.5281/zenodo.12345678"  # Optional
  journal: ""  # Optional
  volume: ""  # Optional
  pages: ""  # Optional

keywords:
  - "optimization"
  - "machine learning"

metadata:
  license: "Apache-2.0"
  language: "en"
```

**Benefits**:

- ✅ Version controllable (can be committed to git)
- ✅ Single file for all metadata
- ✅ Supports multiple authors
- ✅ Structured format (YAML)
- ✅ Easy to edit and maintain

### Environment Variables (Alternative Method)

Environment variables are supported as an alternative configuration method and take precedence over config file values:

```bash
export AUTHOR_NAME="Dr. Jane Smith"
export AUTHOR_ORCID="0000-0000-0000-1234"
export AUTHOR_EMAIL="jane.smith@university.edu"
export PROJECT_TITLE="Advanced Research Framework"
export DOI="10.5281/zenodo.12345678"  # Optional

python3 scripts/03_render_pdf.py
```

**Priority order**:

1. Environment variables (highest priority)
2. Config file (`project/docs/manuscript/config.yaml`)
3. Default values (lowest priority)

### Multiple Authors

The config file supports multiple authors:

```yaml
authors:
  - name: "Dr. Jane Smith"
    orcid: "0000-0000-0000-1234"
    email: "jane.smith@university.edu"
    affiliation: "University of Example"
    corresponding: true
  - name: "Dr. John Doe"
    orcid: "0000-0000-0000-5678"
    email: "john.doe@university.edu"
    affiliation: "Another University"
    corresponding: false
```

The first author (or the one marked `corresponding: true`) is used for PDF metadata.

## Validation

### Markdown Validation

```bash
# Check for issues (from template root)
uv run python -m infrastructure.validation.cli markdown projects/ento_linguistics/manuscript/

# Strict mode (fail on any issues)
uv run python -m infrastructure.validation.cli markdown projects/ento_linguistics/manuscript/ --strict
```

**Validates:**

- Image references exist
- Cross-references are valid
- Equation labels are unique
- No bare URLs
- LaTeX equation syntax

### PDF Validation

```bash
# Check rendered PDF (from template root)
uv run python -m infrastructure.validation.cli pdf projects/ento_linguistics/output/pdf/

# Specific section
uv run python -m infrastructure.validation.cli pdf projects/ento_linguistics/output/pdf/01_abstract.pdf
```

**Detects:**

- Unresolved references (??)
- Missing citations ([?])
- LaTeX warnings
- Rendering issues

### Quality & Preflight

- `uv run python scripts/_manuscript_preflight.py --strict` verifies figures exist, glossary markers are present, and bibliography commands are intact before rendering.
- `uv run python scripts/_quality_report.py` aggregates readability metrics, integrity checks, and reproducibility snapshots.
- `validate_figure_registry` and `verify_output_integrity` guard against missing figures or corrupted outputs prior to PDF compilation.

## Best Practices

For formatting standards, see [`.cursorrules/manuscript_style.md`](../../.cursorrules/manuscript_style.md).

### Markdown Writing

- Use descriptive cross-reference labels
- Always label equations, figures, and tables
- Keep section structure hierarchical
- Use consistent heading levels

### Figure Integration

- Generate figures from scripts (reproducible)
- Save to `output/figures/`
- Use descriptive filenames
- Include captions and labels

### Cross-References

- Use `\ref{}` for sections, figures, tables
- Use `\eqref{}` for equations
- Use `\cite{}` for bibliography
- Ensure all references have labels

### LaTeX Math

- Use equation environment for display math
- Label all important equations
- Use `\eqref{}` to reference equations
- Avoid double dollar signs or backslash square brackets for display math

### Supplemental Material

- Use for extended methods, additional results
- Reference from main text appropriately
- Maintain consistent formatting with main text
- Number supplemental figures/tables distinctly (e.g., S1, S2)

## Output Formats

### Standard PDF (`project_combined.pdf`)

- Professional printing quality
- Full LaTeX rendering
- cross-references
- Publication-ready

### IDE-Friendly PDF (`project_combined_ide_friendly.pdf`)

- Optimized for text editor viewing
- Better font rendering
- Simplified layout

### HTML Version (`project_combined.html`)

- Web browser compatible
- IDE integration
- Interactive features
- Faster loading

## Troubleshooting

### Missing Figures

```bash
# Ensure scripts generated figures
ls output/figures/

# Check figure path in markdown
grep "includegraphics" docs/manuscript/*.md
```

### Unresolved References

```bash
# Validate all references
python3 -m infrastructure.validation.cli markdown docs/manuscript/

# Check for ?? in PDF
python3 -m infrastructure.validation.cli pdf output/pdf/
```

### LaTeX Errors

```bash
# Check compilation log
cat output/pdf/*_compile.log
```

### Section Ordering Issues

```bash
# List sections in order
ls -1 docs/manuscript/*.md | grep -E '[0-9]{2}_|S[0-9]{2}_'

# Verify order matches:
# 01-09: Main sections
# S01-S0N: Supplemental sections
# 98: Glossary
# 99: References
```

## See Also

- [`preamble.md`](preamble.md) - LaTeX configuration
- [`references.bib`](references.bib) - Bibliography
- [`../../.cursorrules/manuscript_style.md`](../../.cursorrules/manuscript_style.md) - manuscript formatting and style guide
- [`../../docs/MARKDOWN_TEMPLATE_GUIDE.md`](../../docs/MARKDOWN_TEMPLATE_GUIDE.md) - Markdown guide
- [`../scripts/README.md`](../scripts/README.md) - Entry point orchestrators
- [`../AGENTS.md`](../AGENTS.md) - system documentation
