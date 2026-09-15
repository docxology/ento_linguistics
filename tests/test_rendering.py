"""Behavioral tests for src/pipeline/rendering.py pure logic.

Covers TeX post-processing (natbib/hypersetup patching), frontmatter and
title-page emission, {{KEY}} corpus-variable substitution, and corpus
variable loading from real files on disk (tmp_path). Subprocess-invoking
build paths are intentionally not covered here.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.rendering import (
    _apply_corpus_vars,
    _build_frontmatter,
    _load_corpus_vars,
    _postprocess_combined_tex,
    _write_title_page_tex,
)


# ═══════════════════════════════════════════════════════════════════════
#  _postprocess_combined_tex
# ═══════════════════════════════════════════════════════════════════════


class TestPostprocessCombinedTex:
    """natbib option and hidelinks patching on real files."""

    def test_natbib_options_replaced(self, tmp_path: Path):
        tex = tmp_path / "combined.tex"
        tex.write_text("\\usepackage[]{natbib}\n\\begin{document}\n", encoding="utf-8")

        _postprocess_combined_tex(tex)

        text = tex.read_text(encoding="utf-8")
        assert "\\usepackage[round,comma,sort&compress]{natbib}" in text
        assert "\\usepackage[]{natbib}" not in text

    def test_hidelinks_inline_replaced(self, tmp_path: Path):
        tex = tmp_path / "combined.tex"
        tex.write_text(
            "\\hypersetup{pdfborder={0 0 0}, hidelinks, pdfpagenumberstyle=Alphadecimal}",
            encoding="utf-8",
        )

        _postprocess_combined_tex(tex)

        text = tex.read_text(encoding="utf-8")
        assert "hidelinks" not in text
        assert "colorlinks=true" in text
        assert "linkcolor=red" in text
        assert "citecolor=red" in text

    def test_hidelinks_replaced_inside_multiline_block(self, tmp_path: Path):
        tex = tmp_path / "combined.tex"
        tex.write_text(
            "\\hypersetup{\n  hidelinks,\n  pdfborder={0 0 0},\n}", encoding="utf-8"
        )

        _postprocess_combined_tex(tex)

        text = tex.read_text(encoding="utf-8")
        assert "hidelinks" not in text
        # The inline option-list replacement is applied wherever "hidelinks,"
        # occurs, including inside a multi-line \\hypersetup block.
        assert "colorlinks=true,linkcolor=red,urlcolor=red,citecolor=red" in text

    def test_no_hidelinks_leaves_text_untouched(self, tmp_path: Path):
        tex = tmp_path / "combined.tex"
        original = "\\usepackage{hyperref}\n\\begin{document}\nHello\n"
        tex.write_text(original, encoding="utf-8")

        _postprocess_combined_tex(tex)

        assert tex.read_text(encoding="utf-8") == original


# ═══════════════════════════════════════════════════════════════════════
#  _build_frontmatter / _write_title_page_tex
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """A realistic config.yaml with paper, authors, publication metadata."""
    config = tmp_path / "config.yaml"
    config.write_text(
        "paper:\n"
        "  title: 'Ento-Linguistics: A Study'\n"
        "  subtitle: 'Language of Social Insects'\n"
        "  date: January 1, 2026\n"
        "authors:\n"
        "  - name: Jane Doe\n"
        "    affiliation: University of Somewhere\n"
        "    email: jane@example.edu\n"
        "    orcid: 0000-0002-0000-0000\n"
        "  - name: John Smith & Co\n"
        "    affiliation: Institute 100%\n"
        "  - name: ''\n"
        "    affiliation: skipped, no name\n"
        "publication:\n"
        "  doi: 10.1234/ento.2026\n"
        "keywords:\n"
        "  - entomology\n"
        "  - sociolinguistics\n",
        encoding="utf-8",
    )
    return config


class TestBuildFrontmatter:
    """Frontmatter YAML emission and title-page generation."""

    def test_returns_yaml_frontmatter(self, config_file: Path, tmp_path: Path):
        out_dir = tmp_path / "pdf"
        out_dir.mkdir()

        frontmatter = _build_frontmatter(config_file, out_dir)

        assert frontmatter.startswith("---\n")
        assert frontmatter.rstrip().endswith("---")
        assert "title: 'Ento-Linguistics: A Study'" in frontmatter
        assert "subtitle: Language of Social Insects" in frontmatter
        assert "date: January 1, 2026" in frontmatter
        assert "Jane Doe" in frontmatter

    def test_writes_title_page_tex(self, config_file: Path, tmp_path: Path):
        out_dir = tmp_path / "pdf"
        out_dir.mkdir()

        _build_frontmatter(config_file, out_dir)

        tex = (out_dir / "_title_page.tex").read_text(encoding="utf-8")
        assert "\\renewcommand{\\maketitle}" in tex
        assert "\\textbf{Jane Doe}" in tex
        assert "University of Somewhere" in tex
        assert "jane@example.edu" in tex
        assert "ORCID: 0000-0002-0000-0000" in tex
        # DOI block
        assert "\\href{https://doi.org/10.1234/ento.2026}{10.1234/ento.2026}" in tex
        # PDF metadata synced from config
        assert "pdfauthor={Jane Doe and John Smith & Co}" in tex
        assert "pdfkeywords={entomology, sociolinguistics}" in tex

    def test_tex_special_chars_escaped(self, config_file: Path, tmp_path: Path):
        out_dir = tmp_path / "pdf"
        out_dir.mkdir()

        _build_frontmatter(config_file, out_dir)

        tex = (out_dir / "_title_page.tex").read_text(encoding="utf-8")
        # "&" in name and "%" in affiliation must be escaped
        assert "\\textbf{John Smith \\& Co}" in tex
        assert "Institute 100\\%" in tex
        # Raw unescaped specials must not survive inside author boxes
        assert "\\textbf{John Smith & Co}" not in tex

    def test_default_date_when_missing(self, tmp_path: Path):
        config = tmp_path / "config.yaml"
        config.write_text("paper:\n  title: No Date Paper\n", encoding="utf-8")
        out_dir = tmp_path / "pdf"
        out_dir.mkdir()

        frontmatter = _build_frontmatter(config, out_dir)

        assert "title: No Date Paper" in frontmatter
        # A date was auto-generated (non-empty date line in the YAML)
        assert "date: " in frontmatter


class TestWriteTitlePageTex:
    """Direct title-page emission edge cases."""

    def test_no_authors_emits_empty_author_block(self, tmp_path: Path):
        out_dir = tmp_path / "pdf"
        out_dir.mkdir()

        _write_title_page_tex(out_dir, [], "10.1/xyz", "May 2026", "T", [], ["k"])

        tex = (out_dir / "_title_page.tex").read_text(encoding="utf-8")
        assert "pdfauthor={" + "}" in tex  # empty pdfauthor
        assert "\\href{https://doi.org/10.1/xyz}{10.1/xyz}" in tex

    def test_no_doi_omits_doi_line(self, tmp_path: Path):
        out_dir = tmp_path / "pdf"
        out_dir.mkdir()

        _write_title_page_tex(out_dir, [{"name": "A"}], "", "May 2026", "T", ["A"], [])

        tex = (out_dir / "_title_page.tex").read_text(encoding="utf-8")
        assert "doi.org" not in tex
        assert "pdfkeywords={" + "}" in tex


# ═══════════════════════════════════════════════════════════════════════
#  _apply_corpus_vars
# ═══════════════════════════════════════════════════════════════════════


class TestApplyCorpusVars:
    """{{KEY}} substitution behavior."""

    def test_substitutes_known_keys(self):
        content = "The corpus holds {{CORPUS_PUBLICATIONS}} abstracts (TTR {{CORPUS_TTR}})."
        result = _apply_corpus_vars(content, {"CORPUS_PUBLICATIONS": "370", "CORPUS_TTR": "0.1456"})

        assert result == "The corpus holds 370 abstracts (TTR 0.1456)."

    def test_unknown_keys_left_in_place(self):
        content = "Known {{KNOWN}} and unknown {{MYSTERY_KEY}}."
        result = _apply_corpus_vars(content, {"KNOWN": "yes"})

        assert "{{KNOWN}}" not in result
        assert "{{MYSTERY_KEY}}" in result

    def test_strict_mode_raises_on_remaining(self):
        with pytest.raises(SystemExit):
            _apply_corpus_vars("Dangling {{UNRESOLVED_VAR}}.", {}, strict=True)

    def test_strict_mode_passes_when_all_substituted(self):
        result = _apply_corpus_vars("All {{A}} {{B}} filled.", {"A": "1", "B": "2"}, strict=True)
        assert result == "All 1 2 filled."


# ═══════════════════════════════════════════════════════════════════════
#  _load_corpus_vars
# ═══════════════════════════════════════════════════════════════════════


def _make_project(tmp_path: Path, *, with_stats=True, with_terms=True,
                  with_domains=True, with_concepts=True) -> Path:
    """Materialize a fake project tree with real corpus/statistics JSON files."""
    (tmp_path / "data" / "corpus").mkdir(parents=True)
    (tmp_path / "output" / "data").mkdir(parents=True)

    abstracts = [f"Abstract text number {i} about ants and queens." for i in range(3)]
    (tmp_path / "data" / "corpus" / "abstracts.json").write_text(json.dumps(abstracts))

    if with_stats:
        stats = {
            "total_tokens": 48787,
            "unique_tokens": 7105,
            "type_token_ratio": 0.1456,
            "most_common_tokens": [["ants", 950], ["colony", 800], ["queen-", 640]],
        }
        (tmp_path / "output" / "data" / "corpus_statistics.json").write_text(json.dumps(stats))


    if with_terms:
        terms = {
            "queen-mating": {"lemma": "queen-mating", "domains": ["sex_and_reproduction"],
                             "frequency": 12, "confidence": 0.99, "n_contexts": 12},
            "worker-laid": {"lemma": "worker-laid", "domains": ["sex_and_reproduction",
                                                                  "power_and_labor"],
                            "frequency": 7, "confidence": 0.95, "n_contexts": 7},
        }
        (tmp_path / "output" / "data" / "extracted_terms.json").write_text(json.dumps(terms))

    if with_domains:
        domains = {
            "sex_and_reproduction": {
                "term_count": 64, "total_frequency": 605, "bridging_term_count": 26,
                "semantic_entropy": 0.2458, "anthropomorphic_proportion": 0.0175,
                "high_entropy_count": 1, "high_entropy_pct": 1.8,
            },
            "power_and_labor": {
                "term_count": 63, "total_frequency": 905, "bridging_term_count": 43,
                "semantic_entropy": 0.5, "anthropomorphic_proportion": 0.02,
                "high_entropy_count": 2, "high_entropy_pct": 3.2,
            },
        }
        (tmp_path / "output" / "data" / "domain_statistics.json").write_text(json.dumps(domains))

    if with_concepts:
        concepts = {
            "n_concepts": 6, "n_relationships": 9, "network_nodes": 894,
            "network_edges": 1200, "network_clustering": 0.3142, "network_avg_degree": 2.68,
            "concepts": {
                "Reproduction": {"description": "d", "n_terms": 30,
                                 "domains": ["sex_and_reproduction"], "confidence": 0.9},
                "Labor": {"description": "d", "n_terms": 25,
                          "domains": ["power_and_labor"], "confidence": 0.9},
            },
        }
        (tmp_path / "output" / "data" / "concept_map_summary.json").write_text(json.dumps(concepts))

    return tmp_path


class TestLoadCorpusVars:
    """Corpus template-variable loading from real JSON files."""

    def test_loads_all_sources(self, tmp_path: Path):
        root = _make_project(tmp_path)

        vars_ = _load_corpus_vars(root)

        # Publication count from raw corpus
        assert vars_["CORPUS_PUBLICATIONS"] == "3"
        # Token statistics
        assert vars_["CORPUS_TOTAL_TOKENS"] == "48787"
        assert vars_["CORPUS_UNIQUE_TOKENS"] == "7105"
        assert vars_["CORPUS_TTR"] == "0.1456"
        # Top terms (1-indexed)
        assert vars_["CORPUS_TOP_TERM_1"] == "ants"
        assert vars_["CORPUS_TOP_FREQ_1"] == "950"
        assert vars_["CORPUS_TOP_TERM_3"] == "queen-"
        # Per-term slugs from corpus stats
        assert vars_["TERM_FREQ_ANTS"] == "950"
        assert vars_["TERM_FREQ_QUEEN_"] == "640"
        # Extracted terms: corpus-level slug not overwritten; extracted-only added
        assert vars_["EXTRACTED_TERM_FREQ_QUEEN_MATING"] == "12"
        assert vars_["EXTRACTED_TERM_FREQ_WORKER_LAID"] == "7"
        assert vars_["TERM_FREQ_QUEEN_MATING"] == "12"  # not in corpus top tokens
        assert vars_["TERM_FREQ_WORKER_LAID"] == "7"
        anthro = 0.0175
        assert vars_["DOMAIN_SEX_AND_REPRODUCTION_ANTHROPOMORPHIC_PROPORTION"] == f"{anthro:.3f}"
        assert vars_["DOMAIN_SEX_AND_REPRODUCTION_ANTHROPOMORPHIC_PROPORTION_PCT"] == f"{anthro * 100:.1f}"
        assert vars_["DOMAIN_POWER_AND_LABOR_HIGH_ENTROPY_PCT"] == "3.2"
        # Domain statistics (basic)
        assert vars_["DOMAIN_SEX_AND_REPRODUCTION_TERMS"] == "64"
        assert vars_["DOMAIN_POWER_AND_LABOR_FREQ"] == "905"
        assert vars_["DOMAIN_POWER_AND_LABOR_BRIDGING"] == "43"
        # Domain extended stats
        assert vars_["DOMAIN_SEX_AND_REPRODUCTION_ENTROPY"] == "0.25"
        assert vars_["DOMAIN_SEX_AND_REPRODUCTION_ANTHROPOMORPHIC_PROPORTION"] == f"{0.0175:.3f}"
        assert vars_["DOMAIN_SEX_AND_REPRODUCTION_ANTHROPOMORPHIC_PROPORTION_PCT"] == f"{0.0175 * 100:.1f}"
        # Corpus-level entropy: weighted by term counts (64*0.2458 + 63*0.5) / 127
        expected_entropy = (64 * 0.2458 + 63 * 0.5) / 127
        assert vars_["CORPUS_OVERALL_ENTROPY"] == f"{expected_entropy:.2f}"
        expected_high = 100 * (1 + 2) / 127
        assert vars_["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] == f"{expected_high:.1f}"
        # Drift: 1 of 2 domain-assigned terms spans multiple domains
        assert vars_["CORPUS_DRIFT_PERCENTAGE"] == "50.0"
        # Concept map / network stats
        assert vars_["CORPUS_CONCEPT_COUNT"] == "6"
        assert vars_["CORPUS_RELATIONSHIP_COUNT"] == "9"
        assert vars_["NETWORK_NODES"] == "894"
        assert vars_["NETWORK_EDGES"] == "1200"
        assert vars_["NETWORK_CLUSTERING"] == "0.3142"
        assert vars_["NETWORK_AVG_DEGREE"] == "2.68"
        assert vars_["CONCEPT_REPRODUCTION_TERMS"] == "30"
        assert vars_["CONCEPT_LABOR_TERMS"] == "25"

    def test_missing_abstracts_file_yields_na(self, tmp_path: Path):
        root = _make_project(tmp_path)
        (root / "data" / "corpus" / "abstracts.json").unlink()

        vars_ = _load_corpus_vars(root)

        assert vars_["CORPUS_PUBLICATIONS"] == "N/A"

    def test_missing_stats_files_yield_na(self, tmp_path: Path):
        root = _make_project(tmp_path, with_stats=False, with_terms=False,
                             with_domains=False, with_concepts=False)

        vars_ = _load_corpus_vars(root)

        assert vars_["CORPUS_TOTAL_TOKENS"] == "N/A"
        assert vars_["CORPUS_UNIQUE_TOKENS"] == "N/A"
        assert vars_["CORPUS_TTR"] == "0.000"
        assert vars_["CORPUS_CANDIDATE_TERMS"] == "N/A"
        assert vars_["CORPUS_DOMAIN_TERMS"] == "N/A"
        assert vars_["CORPUS_CONCEPT_COUNT"] == "N/A"
        assert vars_["NETWORK_CLUSTERING"] == "N/A"
        # Drift has no source and no domain stats → N/A
        assert vars_["CORPUS_DRIFT_PERCENTAGE"] == "N/A"

    def test_missing_extracted_terms_leaves_drift_unavailable(self, tmp_path: Path):
        root = _make_project(tmp_path)
        # Drift is derived from extracted_terms.json; without it, drift is N/A
        (root / "output" / "data" / "extracted_terms.json").unlink()

        vars_ = _load_corpus_vars(root)

        assert vars_["CORPUS_DRIFT_PERCENTAGE"] == "N/A"

    def test_non_numeric_network_stats_pass_through(self, tmp_path: Path):
        root = _make_project(tmp_path)
        concepts = json.loads(
            (root / "output" / "data" / "concept_map_summary.json").read_text()
        )
        concepts["network_clustering"] = "N/A"
        concepts["network_avg_degree"] = "N/A"
        (root / "output" / "data" / "concept_map_summary.json").write_text(
            json.dumps(concepts)
        )

        vars_ = _load_corpus_vars(root)

        assert vars_["NETWORK_CLUSTERING"] == "N/A"
        assert vars_["NETWORK_AVG_DEGREE"] == "N/A"
