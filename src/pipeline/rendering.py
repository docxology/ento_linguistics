"""PDF rendering for the Ento-Linguistics manuscript.

Importable rendering logic used by the thin orchestrator
``scripts/_render_pdf_override.py``: Pandoc/XeLaTeX build pipeline, Pandoc
output TeX post-processing, frontmatter/title-page LaTeX emission, and
``{{KEY}}`` corpus-variable substitution.
"""
from __future__ import annotations

import logging
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

def _postprocess_combined_tex(tex_path: Path) -> None:
    """Patch Pandoc output: natbib options, red links (override trailing ``hidelinks``).

    Pandoc inserts ``\\usepackage[]{natbib}`` before ``--include-in-header`` and appends
    ``\\hypersetup{..., hidelinks, ...}`` after it, which overrides red ``\\hypersetup`` in
    ``preamble.tex``. Mirrors ``infrastructure.rendering._pdf_combined_renderer.postprocess_latex``.
    """
    text = tex_path.read_text(encoding="utf-8")
    text = text.replace(
        "\\usepackage[]{natbib}",
        "\\usepackage[round,comma,sort&compress]{natbib}",
    )
    if "hidelinks" in text:
        text = text.replace(
            "hidelinks,",
            "colorlinks=true,linkcolor=red,urlcolor=red,citecolor=red,anchorcolor=red,filecolor=red,",
        )
        text = text.replace(
            "  hidelinks,\n",
            "  colorlinks=true,\n  linkcolor=red,\n  urlcolor=red,\n  citecolor=red,\n",
        )
    tex_path.write_text(text, encoding="utf-8")


def _build_frontmatter(config_path: Path, output_dir: Path) -> str:
    r"""Parse config.yaml, emit Pandoc YAML frontmatter and ``_title_page.tex``.

    Pandoc receives a minimal YAML block (title, author names, date).
    A companion ``_title_page.tex`` is written into *output_dir* with
    ``\AtBeginDocument`` overrides for the rich author block (affiliation,
    ORCID, email) and DOI, plus ``\hypersetup`` PDF-metadata fields.
    ``preamble.tex`` includes this file via ``\input{_title_page.tex}``.

    All metadata originates from config.yaml — no values are hardcoded in
    ``preamble.tex``, eliminating dual-source drift.

    Returns:
        YAML frontmatter string (with ``---`` delimiters) or empty string.
    """
    if yaml is None:
        print("  Warning: PyYAML not available, skipping cover page metadata")
        return ""

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    paper = config.get("paper", {})
    title = paper.get("title", "Untitled")
    subtitle = paper.get("subtitle", "")
    raw_date = paper.get("date", "")
    date_str = raw_date if raw_date else datetime.now().strftime("%B %d, %Y")

    authors_cfg = config.get("authors", [])
    author_names = [a.get("name", "") for a in authors_cfg if a.get("name")]

    pub_cfg = config.get("publication", {})
    doi = pub_cfg.get("doi", "")
    keywords_cfg = config.get("keywords", [])

    # ── Generate _title_page.tex from config.yaml ────────────────────
    _write_title_page_tex(
        output_dir, authors_cfg, doi, date_str, title, author_names, keywords_cfg,
    )

    # ── Pandoc YAML frontmatter (plain names only) ───────────────────
    metadata = {"title": title, "date": date_str}
    if subtitle:
        metadata["subtitle"] = subtitle
    if author_names:
        metadata["author"] = author_names

    frontmatter = "---\n" + yaml.dump(metadata, default_flow_style=False) + "---\n"

    print(f"  Cover metadata: title='{title[:50]}...', "
          f"{len(author_names)} author(s), date='{date_str}', doi='{doi}'")

    return frontmatter


def _write_title_page_tex(
    output_dir: Path,
    authors_cfg: list,
    doi: str,
    date_str: str,
    title: str,
    author_names: list,
    keywords: list,
) -> None:
    r"""Write ``_title_page.tex`` with a custom ``\maketitle`` and PDF metadata.

    TeXLive 2026 changed internal tabular handling (LaTeX3 ``\tbl_crcr``),
    breaking the conventional ``\renewcommand{\@author}`` approach that
    relies on ``\\`` and ``\and`` inside the tabular that the default
    ``\maketitle`` creates.  Instead, we redefine ``\maketitle`` itself
    using ``\parbox`` blocks, which sidesteps the tabular entirely.

    Uses ``\ttfamily`` instead of ``\texttt`` because the latter is
    redefined (with ``\colorbox``) for inline-code styling elsewhere in
    the preamble.
    """
    def _tex_escape(s: str) -> str:
        """Escape characters that are special in LaTeX."""
        for ch, repl in [("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")]:
            s = s.replace(ch, repl)
        return s

    # Build per-author parbox blocks
    author_boxes: list[str] = []
    n_authors = len([a for a in authors_cfg if a.get("name")])
    col_width = f"{0.9 / max(n_authors, 1):.2f}\\textwidth"

    for a in authors_cfg:
        name = a.get("name", "")
        if not name:
            continue
        inner: list[str] = [r"      \textbf{" + _tex_escape(name) + r"}\\"]
        if a.get("affiliation"):
            inner.append(r"      {\small " + _tex_escape(a["affiliation"]) + r"}\\")
        detail_bits: list[str] = []
        if a.get("email"):
            detail_bits.append(r"{\ttfamily " + a["email"] + r"}")
        if a.get("orcid"):
            detail_bits.append("ORCID: " + a["orcid"])
        if detail_bits:
            inner.append(
                r"      {\footnotesize "
                + r" \enspace $\cdot$ \enspace ".join(detail_bits)
                + r"}"
            )
        box = (
            r"    \parbox[t]{" + col_width + r"}{\centering"
            + "\n" + "\n".join(inner) + "\n    }"
        )
        author_boxes.append(box)

    authors_block = "\n    \\hfill\n".join(author_boxes) if author_boxes else ""

    # Date line with optional DOI
    date_block = r"    " + date_str
    if doi:
        date_block += r"\\[4pt]" + "\n"
        date_block += (
            r"    {\small DOI: \href{https://doi.org/"
            + doi + r"}{" + doi + r"}}"
        )

    # PDF metadata values
    pdf_author = " and ".join(author_names) if author_names else ""
    pdf_keywords = ", ".join(keywords) if keywords else ""

    lines = [
        r"% Auto-generated from config.yaml — do not edit by hand.",
        r"% Uses a custom \maketitle to avoid TeXLive 2026 tabular/\and breakage.",
        r"\makeatletter",
        r"\renewcommand{\maketitle}{%",
        r"  \begin{center}",
        r"    {\LARGE \@title \par}",
        r"    \vskip 1.5em",
        authors_block,
        r"    \vskip 1em",
        date_block,
        r"  \end{center}",
        r"  \par\vskip 1.5em",
        r"}",
        r"\makeatother",
        r"",
        r"% PDF metadata (synced from config.yaml keywords and authors)",
        r"\hypersetup{%",
        r"  pdfauthor={" + pdf_author + r"},",
        r"  pdfkeywords={" + pdf_keywords + r"},",
        r"}",
    ]

    tex_path = output_dir / "_title_page.tex"
    tex_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Generated {tex_path.name} ({len(lines)} lines)")


def _load_corpus_vars(project_root: Path) -> dict:
    """Load corpus statistics from output/data/ for template substitution.

    Reads corpus_statistics.json for token counts and data/corpus/abstracts.json
    for the publication count. Returns a dict of {{KEY}} -> value mappings that
    are substituted into manuscript markdown files before pandoc is run, ensuring
    all cited numbers always reflect the most recent corpus build.

    Each JSON source logs its path and the number of variables it contributed.
    Missing sources emit a WARNING so problems are visible in CI logs.

    Returns:
        Mapping of template variable names to their formatted string values.
    """
    import json
    import logging

    logger = logging.getLogger("render_pdf.template_vars")
    vars_: dict = {}

    # ── Publication count from the raw corpus ──────────────────────────
    abstracts_path = project_root / "data" / "corpus" / "abstracts.json"
    if abstracts_path.exists():
        with open(abstracts_path) as fh:
            abstracts = json.load(fh)
        vars_["CORPUS_PUBLICATIONS"] = str(len(abstracts))
        logger.info("  ✓ %s → 1 variable (publications=%s)", abstracts_path.name, len(abstracts))
    else:
        vars_["CORPUS_PUBLICATIONS"] = "N/A"
        logger.warning("  ✗ %s NOT FOUND — CORPUS_PUBLICATIONS set to N/A", abstracts_path)

    # ── Token statistics from the processed corpus ─────────────────────
    stats_path = project_root / "output" / "data" / "corpus_statistics.json"
    if stats_path.exists():
        with open(stats_path) as fh:
            stats = json.load(fh)
        vars_["CORPUS_TOTAL_TOKENS"] = str(stats.get("total_tokens", 0))
        vars_["CORPUS_UNIQUE_TOKENS"] = str(stats.get("unique_tokens", 0))
        vars_["CORPUS_TTR"] = f"{stats.get('type_token_ratio', 0):.4f}"
        
        top_terms = stats.get("most_common_tokens", [])
        n_top = 0
        for i in range(5):
            if i < len(top_terms):
                vars_[f"CORPUS_TOP_TERM_{i+1}"] = top_terms[i][0]
                vars_[f"CORPUS_TOP_FREQ_{i+1}"] = str(top_terms[i][1])
                n_top += 2

        # Per-term frequency lookup: TERM_FREQ_<UPPERCASE_TERM>
        term_freq_count = 0
        for term_name, freq in top_terms:
            slug = term_name.upper().replace("-", "_").replace(" ", "_")
            vars_[f"TERM_FREQ_{slug}"] = str(freq)
            term_freq_count += 1
        logger.info("  ✓ %s → %d variables (incl. %d per-term freqs)",
                    stats_path.name, 3 + n_top + term_freq_count, term_freq_count)
    else:
        vars_["CORPUS_TOTAL_TOKENS"] = "N/A"
        vars_["CORPUS_UNIQUE_TOKENS"] = "N/A"
        vars_["CORPUS_TTR"] = "0.000"
        logger.warning("  ✗ %s NOT FOUND — corpus token stats unavailable", stats_path)

    # ── Term extraction counts ─────────────────────────────────────────
    terms_path = project_root / "output" / "data" / "extracted_terms.json"
    if terms_path.exists():
        with open(terms_path) as fh:
            terms_data = json.load(fh)
        candidate_terms = len(terms_data)
        domain_terms = sum(
            1 for v in terms_data.values()
            if isinstance(v, dict) and v.get("domains")
        )
        vars_["CORPUS_CANDIDATE_TERMS"] = str(candidate_terms)
        vars_["CORPUS_DOMAIN_TERMS"] = str(domain_terms)

        # Per-term frequency lookup from extracted terms: TERM_FREQ_<SLUG>
        # These complement the top-20 corpus token frequencies above,
        # providing coverage for domain-specific terms not in the global top-20.
        n_term_freqs = 0
        n_extracted_only = 0
        for term_name, term_info in terms_data.items():
            if isinstance(term_info, dict) and term_info.get("frequency"):
                slug = term_name.upper().replace("-", "_").replace(" ", "_")
                var_key = f"TERM_FREQ_{slug}"
                if var_key not in vars_:  # Don't overwrite corpus-level freq
                    vars_[var_key] = str(term_info["frequency"])
                    n_term_freqs += 1
                # Extraction-local counts (domain pipeline); use for prose that
                # cites lemma frequencies from extracted_terms, not global tokens.
                ext_key = f"EXTRACTED_TERM_FREQ_{slug}"
                vars_[ext_key] = str(term_info["frequency"])
                n_extracted_only += 1
        logger.info(
            "  ✓ %s → %d variables (candidates=%d, domain=%d, term_freqs=%d, extracted_only=%d)",
            terms_path.name,
            2 + n_term_freqs + n_extracted_only,
            candidate_terms,
            domain_terms,
            n_term_freqs,
            n_extracted_only,
        )
    else:
        vars_["CORPUS_CANDIDATE_TERMS"] = "N/A"
        vars_["CORPUS_DOMAIN_TERMS"] = "N/A"
        logger.warning("  ✗ %s NOT FOUND — term counts unavailable", terms_path)
        
    # ── Domain Statistics ──────────────────────────────────────────────
    domain_path = project_root / "output" / "data" / "domain_statistics.json"
    if domain_path.exists():
        with open(domain_path) as fh:
            dstats = json.load(fh)
        
        n_domain_vars = 0
        for dom, v in dstats.items():
            slug = dom.upper()
            vars_[f"DOMAIN_{slug}_TERMS"] = str(v.get("term_count", 0))
            vars_[f"DOMAIN_{slug}_FREQ"] = str(v.get("total_frequency", 0))
            vars_[f"DOMAIN_{slug}_BRIDGING"] = str(v.get("bridging_term_count", 0))
            n_domain_vars += 3
        logger.info("  ✓ %s → %d variables (%d domains)",
                     domain_path.name, n_domain_vars, len(dstats))
    else:
        logger.warning("  ✗ %s NOT FOUND — domain statistics unavailable", domain_path)

    # ── Concept Map Summary (includes terminology network statistics) ──
    concept_path = project_root / "output" / "data" / "concept_map_summary.json"
    if concept_path.exists():
        with open(concept_path) as fh:
            cstats = json.load(fh)
        vars_["CORPUS_CONCEPT_COUNT"] = str(cstats.get("n_concepts", 6))
        vars_["CORPUS_RELATIONSHIP_COUNT"] = str(cstats.get("n_relationships", 8))
        vars_["NETWORK_NODES"] = str(cstats.get("network_nodes", "N/A"))
        vars_["NETWORK_EDGES"] = str(cstats.get("network_edges", "N/A"))
        nc = cstats.get("network_clustering", "N/A")
        vars_["NETWORK_CLUSTERING"] = (
            f"{float(nc):.4f}" if isinstance(nc, (int, float)) else str(nc)
        )
        ad = cstats.get("network_avg_degree", "N/A")
        vars_["NETWORK_AVG_DEGREE"] = (
            f"{float(ad):.2f}" if isinstance(ad, (int, float)) else str(ad)
        )

        # Per-concept term count variables: CONCEPT_<SLUG>_TERMS
        n_concept_vars = 0
        concepts = cstats.get("concepts", {})
        for concept_name, concept_data in concepts.items():
            slug = concept_name.upper()
            vars_[f"CONCEPT_{slug}_TERMS"] = str(concept_data.get("n_terms", 0))
            n_concept_vars += 1
        logger.info("  ✓ %s → %d variables (6 network + %d concept term counts)",
                    concept_path.name, 6 + n_concept_vars, n_concept_vars)
    else:
        vars_["CORPUS_CONCEPT_COUNT"] = "N/A"
        vars_["CORPUS_RELATIONSHIP_COUNT"] = "N/A"
        vars_["NETWORK_NODES"] = "N/A"
        vars_["NETWORK_EDGES"] = "N/A"
        vars_["NETWORK_CLUSTERING"] = "N/A"
        vars_["NETWORK_AVG_DEGREE"] = "N/A"
        logger.warning("  ✗ %s NOT FOUND — concept map stats unavailable", concept_path)

    # ── Domain extended statistics (entropy, anthropomorphic proportion) ──
    domain_path_ext = project_root / "output" / "data" / "domain_statistics.json"
    if domain_path_ext.exists():
        with open(domain_path_ext) as fh:
            dstats_ext = json.load(fh)
        n_ext_vars = 0
        all_entropies = []
        all_term_counts = []
        all_high_counts = []
        for dom, v in dstats_ext.items():
            slug = dom.upper()
            entropy_val = v.get("semantic_entropy", 0.0)
            vars_[f"DOMAIN_{slug}_ENTROPY"] = f"{entropy_val:.2f}"
            anthro = v.get("anthropomorphic_proportion", 0.0)
            vars_[f"DOMAIN_{slug}_ANTHROPOMORPHIC_PROPORTION"] = f"{anthro:.3f}"
            vars_[f"DOMAIN_{slug}_ANTHROPOMORPHIC_PROPORTION_PCT"] = f"{anthro * 100:.1f}"
            high_pct = v.get("high_entropy_pct", 0.0)
            vars_[f"DOMAIN_{slug}_HIGH_ENTROPY_PCT"] = f"{high_pct:.1f}"
            n_ext_vars += 4
            all_entropies.append(entropy_val)
            all_term_counts.append(v.get("term_count", 0))
            all_high_counts.append(v.get("high_entropy_count", 0))

        # Corpus-level entropy aggregates
        total_terms = sum(all_term_counts)
        if total_terms > 0:
            weighted = sum(e * n for e, n in zip(all_entropies, all_term_counts)) / total_terms
            vars_["CORPUS_OVERALL_ENTROPY"] = f"{weighted:.2f}"
            vars_["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] = f"{100 * sum(all_high_counts) / total_terms:.1f}"
        else:
            vars_["CORPUS_OVERALL_ENTROPY"] = "0.00"
            vars_["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] = "0.0"
        n_ext_vars += 2

        # Multi-domain drift percentage
        terms_path_check = project_root / "output" / "data" / "extracted_terms.json"
        if terms_path_check.exists():
            with open(terms_path_check) as fh_t:
                tdata = json.load(fh_t)
            domain_assigned = {
                k: vt for k, vt in tdata.items()
                if isinstance(vt, dict) and vt.get("domains") and len(vt["domains"]) > 0
            }
            multi = sum(1 for vt in domain_assigned.values() if len(vt.get("domains", [])) > 1)
            drift = 100 * multi / max(1, len(domain_assigned))
            vars_["CORPUS_DRIFT_PERCENTAGE"] = f"{drift:.1f}"
            n_ext_vars += 1

        logger.info("  ✓ domain extended stats → %d variables (%d domains)",
                    n_ext_vars, len(dstats_ext))
    else:
        logger.warning("  ✗ domain_statistics.json missing extended stats")

    if "CORPUS_DRIFT_PERCENTAGE" not in vars_:
        vars_["CORPUS_DRIFT_PERCENTAGE"] = "N/A"

    print(f"  Corpus template vars: {len(vars_)} variables loaded")
    print(
        f"    Publications={vars_['CORPUS_PUBLICATIONS']}, "
        f"Tokens={vars_['CORPUS_TOTAL_TOKENS']}, "
        f"Unique={vars_['CORPUS_UNIQUE_TOKENS']}"
    )
    return vars_


def _apply_corpus_vars(content: str, vars_: dict, *, strict: bool = False) -> str:
    """Substitute {{KEY}} placeholders with corpus statistics values.

    After substitution, any remaining ``{{...}}`` patterns are logged as
    warnings to flag template variables that have no data source.
    If *strict* is True, raises ``SystemExit`` when any placeholder remains.
    """
    import re
    import sys

    logger = logging.getLogger("render_pdf.template_vars")
    for key, value in vars_.items():
        content = content.replace("{{" + key + "}}", value)

    # Warn about any unreplaced template variables
    remaining = re.findall(r"\{\{([A-Z0-9_]+)\}\}", content)
    if remaining:
        unique = sorted(set(remaining))
        msg = (
            f"Unreplaced template variable(s): {', '.join(unique)}"
        )
        logger.warning("  ⚠ %d %s", len(unique), msg)
        if strict:
            print(f"ERROR: {msg}", file=sys.stderr)
            sys.exit(1)
    return content


def build_pdf(strict_templates: bool = False) -> None:
    strict = strict_templates or os.environ.get("STRICT_TEMPLATE_VARS", "").lower() in (
        "1",
        "true",
        "yes",
    )
    project_root = Path(__file__).resolve().parent.parent.parent
    manuscript_dir = project_root / "docs" / "manuscript"
    output_dir = project_root / "output" / "pdf"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "ento_linguistics_combined.pdf"

    # Define file order
    files = [
        "01_abstract.md",
        "02_introduction.md",
        "03_methods.md",
        "04a_corpus_and_networks.md",
        "04b_domain_findings.md",
        "05_discussion.md",
        "06_conclusion.md",
        "07_related_work.md",
        "08_acknowledgments.md",
        "98_symbols_glossary.md",
        "99_references.md",
        "S01a_text_and_extraction.md",
        "S01b_analysis_infrastructure.md",
        "S02_supplemental_results.md",
        "S03a_theoretical_extensions.md",
        "S03b_case_studies.md",
    ]

    # ── Parse cover page metadata from config.yaml ────────────────────
    config_path = manuscript_dir / "config.yaml"
    frontmatter = _build_frontmatter(config_path, output_dir)

    # Create a combined markdown file with absolute image paths
    combined_content = frontmatter

    # Load corpus statistics for template variable substitution
    corpus_vars = _load_corpus_vars(project_root)

    # Verify files exist and concatenate
    input_files = []
    for f in files:
        path = manuscript_dir / f
        if path.exists():
            input_files.append(str(path))
        else:
            print(f"Warning: File not found: {path}")

    for f_path in input_files:
        with open(f_path, "r") as f:
            content = f.read()
            # Replace relative paths with absolute paths
            abs_figures = str(output_dir.parent / "figures")
            abs_figures = abs_figures.replace("\\", "/")

            content = content.replace("../figures/", abs_figures + "/")
            content = content.replace("../output/figures/", abs_figures + "/")

            # Substitute {{CORPUS_*}} template variables with live data values
            content = _apply_corpus_vars(content, corpus_vars, strict=strict)

            combined_content += content + "\n\n\\newpage\n\n"

    temp_md = output_dir / "temp_combined.md"
    with open(temp_md, "w") as f:
        f.write(combined_content)

    # Step 1: Generate .tex with Pandoc (natbib mode -> raw \cite commands)
    tex_file = output_dir / "ento_linguistics_combined.tex"

    pandoc_cmd = [
        "pandoc",
        str(temp_md),
        "-o", str(tex_file),
        "--from=markdown+citations+raw_tex",
        "--standalone",
        "--include-in-header=" + str(manuscript_dir / "preamble.tex"),
        "--natbib",
        "--number-sections",
        "--toc",
        "--toc-depth=2",
        "--variable", "geometry:margin=0.85in",
    ]

    print("Step 1/5: Generating LaTeX source with Pandoc...")
    print("Command:", " ".join(pandoc_cmd))

    try:
        subprocess.run(pandoc_cmd, check=True)
        _postprocess_combined_tex(tex_file)
        print("  Post-processed: natbib options + red hyperlinks (hidelinks patch)")
        print(f"  LaTeX source generated: {tex_file}")
    except subprocess.CalledProcessError as e:
        print(f"  Pandoc failed with error code {e.returncode}")
        sys.exit(e.returncode)

    # Step 2: Copy .bib file to build directory (bibtex needs it alongside .tex)
    import shutil
    bib_src = manuscript_dir / "references.bib"
    bib_dst = output_dir / "references.bib"
    shutil.copy2(bib_src, bib_dst)
    print("Step 2/5: Copied bibliography to build directory")

    # Step 3-5: Multi-pass LaTeX compilation for proper citation resolution
    tex_basename = tex_file.stem

    def run_latex(step_label, cmd_list):
        """Run a LaTeX toolchain command, suppressing non-error output."""
        print(f"  {step_label}...")
        result = subprocess.run(
            cmd_list,
            cwd=str(output_dir),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  Warning: {step_label} returned code {result.returncode}")
            if "bibtex" in cmd_list[0].lower():
                bbl_file = output_dir / f"{tex_basename}.bbl"
                if bbl_file.exists() and bbl_file.stat().st_size > 0:
                    print(f"  BibTeX produced .bbl ({bbl_file.stat().st_size} bytes) — continuing")
                    return True
                print(f"  STDERR: {result.stderr[-500:]}")
                return False
        return True

    print("Step 3/5: Running xelatex (pass 1)...")
    # Pass 1: no -halt-on-error so undefined-citation warnings don't abort the
    # run mid-document; we need a complete .aux file for bibtex.
    # Note: with the bgcolor preamble bug fixed, pass 1 should now complete cleanly.
    run_latex("xelatex pass 1", [
        "xelatex", "-interaction=nonstopmode", tex_basename
    ])

    print("Step 4/5: Running bibtex (resolving citations)...")
    bibtex_ok = run_latex("bibtex", ["bibtex", tex_basename])
    if not bibtex_ok:
        print("  BibTeX failed — citations will not be resolved")

    print("Step 5/5: Running xelatex (passes 2-3)...")
    # Passes 2-3: resolve cross-references and citations.
    # NOTE: -halt-on-error is intentionally omitted because harmless font
    # warnings (e.g. from lmodern under xelatex) would otherwise abort the
    # run before all labels are written to the .aux file.
    run_latex("xelatex pass 2", [
        "xelatex", "-interaction=nonstopmode", tex_basename
    ])
    run_latex("xelatex pass 3", [
        "xelatex", "-interaction=nonstopmode", tex_basename
    ])

    # The PDF is generated in output_dir with the tex basename
    generated_pdf = output_dir / f"{tex_basename}.pdf"
    if generated_pdf.exists() and generated_pdf != output_file:
        shutil.move(str(generated_pdf), str(output_file))

    if output_file.exists():
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"\nPDF built successfully: {output_file} ({size_mb:.1f} MB)")
    else:
        print(f"\nPDF build failed — output file not found")
        sys.exit(1)
