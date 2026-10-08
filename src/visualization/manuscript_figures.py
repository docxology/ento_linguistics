"""Manuscript figure generation for the Ento-Linguistic project.

Importable figure-generation, analysis-pipeline, and data-export logic used by
the thin orchestrator ``scripts/02_generate_figures.py``. All business logic
lives here; the script only sets paths and delegates.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from ._style import (
        CANONICAL_DOMAINS,
        MIN_FONT,
        classify_word_formation,
        domain_display_name,
        place_labels,
        publication_style,
    )
except (ImportError, ValueError):
    from visualization._style import (
        CANONICAL_DOMAINS,
        MIN_FONT,
        classify_word_formation,
        domain_display_name,
        place_labels,
        publication_style,
    )

# ── Project root (src/visualization/manuscript_figures.py → project) ──
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# ── Logging ───────────────────────────────────────────────────────────
try:
    from core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

# ── Infrastructure validation (optional) ──────────────────────────────
try:
    from core.validation import validate_figure_registry, verify_output_integrity
    INFRASTRUCTURE_AVAILABLE = True
except ImportError:
    INFRASTRUCTURE_AVAILABLE = False
    validate_figure_registry = None
    verify_output_integrity = None

# ═══════════════════════════════════════════════════════════════════════
#  Corpus Loading
# ═══════════════════════════════════════════════════════════════════════

def load_real_corpus(project_root: Optional[str] = None, require_provenance: bool = False) -> List[str]:
    """Load real entomological corpus from data directory.
    
    Returns:
        List of abstract strings
    """
    if project_root is not None or require_provenance:
        project_root = project_root or _PROJECT_ROOT
        from data.loader import DataLoader
        texts = DataLoader(Path(project_root) / "data").load_corpus("corpus/abstracts.json")
        if require_provenance:
            path = Path(project_root) / "data" / "corpus" / "provenance.json"
            records = json.loads(path.read_text())["records"]
            if not isinstance(records, dict):
                raise ValueError("Abstract provenance records must be a digest mapping")
            texts = [text for text in texts if str(records.get(hashlib.sha256(text.encode()).hexdigest(), {}).get("pmid", "")).isdigit()]
            if not texts:
                raise ValueError("No source-identified abstracts available")
        return texts
    try:
        from data.loader import DataLoader
        loader = DataLoader()
        # Ensure corpus exists
        corpus_path = os.path.join(loader.data_root, "corpus/abstracts.json")
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"Corpus not found at {corpus_path}")
            
        return loader.load_corpus("corpus/abstracts.json")
    except ImportError:
        logger.error("Could not import DataLoader. Ensure src/data/loader.py exists.")
        return []
    except Exception as e:
        logger.error(f"Error loading corpus: {e}")
        return []

# Load real data
REAL_ABSTRACTS: List[str] = load_real_corpus()
if not REAL_ABSTRACTS:
    logger.warning("⚠️  Failed to load real corpus. Pipeline may fail.")



def _setup_directories(project_root: Optional[str] = None) -> Tuple[str, str, str]:
    """Set up output directories, wiping stale figures/data for a clean-slate run.

    Deletes and recreates ``output/figures/`` and ``output/data/`` so that
    every run of this script (and therefore every pipeline analysis stage)
    starts from a verified clean state — no stale or orphaned artefacts.

    Returns:
        Tuple of (output_dir, data_dir, figure_dir) absolute paths
    """
    import shutil

    if project_root is None:
        project_root = _PROJECT_ROOT
    output_dir = os.path.join(project_root, "output")
    data_dir = os.path.join(output_dir, "data")
    figure_dir = os.path.join(output_dir, "figures")

    # ── Wipe regenerated subdirectories ──────────────────────────────────
    # Clean slate for generated artifacts, but tracked documentation
    # (README.md, AGENTS.md) inside output/ survives the wipe: it is
    # versioned project content, not a regenerated artifact.  The
    # fingerprint-guarded analysis artifacts also survive the wipe: the
    # full-text artifact (multi-hour computation) and the abstract-layer
    # statistical artifact are reused whenever their stored corpus
    # fingerprint matches; a stale artifact (mismatched or missing
    # fingerprint) is treated as absent and rebuilt.
    for wipe_dir in (figure_dir, data_dir):
        if os.path.exists(wipe_dir):
            for entry in os.listdir(wipe_dir):
                if entry.endswith(".md") or entry in {"fulltext_analysis.json", "statistical_analysis.json"}:
                    continue
                path = os.path.join(wipe_dir, entry)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            logger.info(f"  🗑️  Cleared stale output: {os.path.relpath(wipe_dir, project_root)}/")

    # ── Recreate clean directories ────────────────────────────────────────
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(figure_dir, exist_ok=True)
    logger.info("  ✅ Output directories initialised (clean slate)")

    return output_dir, data_dir, figure_dir



# ═══════════════════════════════════════════════════════════════════════
#  Analysis Pipeline
# ═══════════════════════════════════════════════════════════════════════

def run_analysis_pipeline(texts: List[str]) -> Dict[str, Any]:
    """Run the complete Ento-Linguistic analysis pipeline on a text corpus.

    Uses real analysis modules from src/ to extract terms, build concept maps,
    analyze domains, and compute co-occurrence networks.

    Args:
        texts: List of text strings (abstracts) to analyze

    Returns:
        Dictionary with all analysis results
    """
    from analysis.text_analysis import TextProcessor
    from analysis.term_extraction import TerminologyExtractor
    from analysis.conceptual_mapping import ConceptualMapper
    from analysis.domain_analysis import DomainAnalyzer

    results: Dict[str, Any] = {}
    # The analyzed texts ride along so downstream stages (e.g. the
    # anthropomorphic-terminology figure's on-the-fly framing fallback)
    # can compute corpus-level features without re-loading the corpus.
    results["texts"] = list(texts)

    # ── Step 1: Text Processing ───────────────────────────────────────
    logger.info("Step 1/4: Processing text corpus...")
    processor = TextProcessor()
    results["corpus_stats"] = processor.get_vocabulary_stats(texts)
    logger.info(f"  Corpus: {len(texts)} documents, "
                f"{results['corpus_stats'].get('total_tokens', '?')} tokens")

    # ── Step 2: Terminology Extraction ────────────────────────────────
    logger.info("Step 2/4: Extracting terminology...")
    extractor = TerminologyExtractor(text_processor=processor)
    terms = extractor.extract_terms(texts, min_frequency=1)
    results["terms"] = terms
    results["domain_seed_stats"] = extractor.get_domain_statistics()
    logger.info(f"  Extracted {len(terms)} terms across "
                f"{len(results['domain_seed_stats'])} domains")

    # ── Step 3: Concept Mapping ───────────────────────────────────────
    logger.info("Step 3/4: Building concept map...")
    mapper = ConceptualMapper()
    concept_map = mapper.build_concept_map(terms)
    results["concept_map"] = concept_map
    logger.info(f"  {len(concept_map.concepts)} concepts, "
                f"{len(concept_map.concept_relationships)} relationships")

    # ── Step 4: Domain Analysis ───────────────────────────────────────
    logger.info("Step 4/4: Analyzing domains...")
    analyzer = DomainAnalyzer()
    domain_analyses = analyzer.analyze_all_domains(terms, texts)
    results["domain_analyses"] = domain_analyses

    # Build domain data summary for visualization
    domain_data: Dict[str, Dict[str, Any]] = {}

    # Pre-compute actual extracted term counts and confidence scores per domain
    actual_term_counts: Dict[str, int] = {}
    actual_avg_freq: Dict[str, float] = {}
    actual_total_freq: Dict[str, int] = {}
    actual_domain_conf: Dict[str, List[float]] = {}
    for term_text, term_obj in terms.items():
        for d in getattr(term_obj, "domains", []):
            actual_term_counts[d] = actual_term_counts.get(d, 0) + 1
            actual_total_freq[d] = actual_total_freq.get(d, 0) + getattr(term_obj, "frequency", 0)
            actual_domain_conf.setdefault(d, []).append(
                float(getattr(term_obj, "confidence", 0.0))
            )
    for d in actual_term_counts:
        if actual_term_counts[d] > 0:
            actual_avg_freq[d] = actual_total_freq[d] / actual_term_counts[d]

    # Reuse the sentence-context entropy already computed by DomainAnalyzer.
    # Short extraction windows and insufficient-context zeros are not the
    # canonical statistical estimand and must not enter these means.
    semantic_entropy_map: Dict[str, float] = {}
    for domain, analysis in domain_analyses.items():
        entries = analysis.ambiguity_metrics.get("term_ambiguity_scores", {})
        valid = [entry["entropy_bits"] for entry in entries.values()
                 if entry.get("status") == "ok"]
        semantic_entropy_map[domain] = float(np.mean(valid)) if valid else 0.0
        for name, entry in entries.items():
            if name in terms:
                terms[name].semantic_entropy = entry["entropy_bits"]
                terms[name].entropy_status = entry.get("status")

    for domain_name, analysis in domain_analyses.items():
        domain_data[domain_name] = {
            # Use actual extracted term count, fall back to key_terms if zero
            "term_count": actual_term_counts.get(domain_name, 0) or (
                len(analysis.key_terms) if hasattr(analysis, "key_terms") else 0
            ),
            "avg_confidence": (
                float(np.mean(actual_domain_conf[domain_name]))
                if domain_name in actual_domain_conf and actual_domain_conf[domain_name]
                else 0.0
            ),
            "total_frequency": actual_total_freq.get(domain_name, sum(
                t.frequency for t in terms.values()
                if domain_name in getattr(t, "domains", [])
            )),
            "bridging_terms": set(),  # Populated below
            "ambiguity_metrics": (
                analysis.ambiguity_metrics
                if hasattr(analysis, "ambiguity_metrics")
                else {}
            ),
            # Semantic entropy H(t) from validated supplemental table
            "semantic_entropy": semantic_entropy_map.get(domain_name, 0.0),
            # Scalar ambiguity score for visualization
            "ambiguity_score": (
                analysis.ambiguity_metrics.get("domain_metrics", {}).get(
                    "average_ambiguity_score",
                    analysis.ambiguity_metrics.get("domain_metrics", {}).get(
                        "average_context_diversity", 0.0
                    ),
                )
                if hasattr(analysis, "ambiguity_metrics") and analysis.ambiguity_metrics
                else 0.0
            ),
        }

    # Find bridging terms (terms in multiple domains)
    for term_text, term_obj in terms.items():
        if len(term_obj.domains) > 1:
            for d in term_obj.domains:
                if d in domain_data:
                    domain_data[d]["bridging_terms"].add(term_text)

    results["domain_data"] = domain_data

    # Document-level observations, independent of domain membership.
    results["relationships"] = document_cooccurrences(terms, texts)

    return results


# ═══════════════════════════════════════════════════════════════════════
#  Figure Generation
# ═══════════════════════════════════════════════════════════════════════

def document_cooccurrences(terms: Dict[str, Any], texts: List[str],
                           max_terms: int = 100) -> Dict[Tuple[str, str], int]:
    """Count documents containing each pair of the top domain-assigned terms.

    Matches are case-insensitive whole words; repeated mentions in a document
    count once. Selection is by decreasing corpus frequency, then term name.
    Domain assignments select vocabulary but never create an edge.
    """
    if max_terms < 2:
        raise ValueError("max_terms must be at least two")
    selected = sorted((name for name, term in terms.items() if term.domains),
                      key=lambda name: (-terms[name].frequency, name))[:max_terms]
    patterns = {name: re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
                for name in selected}
    counts: Counter = Counter()
    for text in texts:
        present = sorted(name for name, pattern in patterns.items() if pattern.search(text))
        counts.update(combinations(present, 2))
    return dict(sorted(counts.items()))


def generate_concept_map(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate concept_map.png using ConceptVisualizer.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    concept_map = results["concept_map"]
    filepath = Path(figure_dir) / "concept_map.png"

    viz = ConceptVisualizer(figsize=(14, 10))
    viz.visualize_concept_map(
        concept_map,
        filepath=filepath,
        title="Ento-Linguistic Concept Map:\nDomain Relationships and Terminology Networks",
    )

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ concept_map.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ concept_map.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def generate_terminology_network(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate terminology_network.png using ConceptVisualizer.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    terms = results["terms"]
    relationships = results["relationships"]
    filepath = Path(figure_dir) / "terminology_network.png"

    viz = ConceptVisualizer(figsize=(16, 12))
    fig = viz.visualize_terminology_network(
        terms=list(terms.items()),
        relationships=relationships,
        filepath=None,  # Save manually at reduced DPI
        title="Ento-Linguistic Terminology Network:\nDocument Co-occurrence (Top 100 Domain-assigned Terms)",
    )
    # Save at 150 DPI (16x12 @ 300 DPI = 3.1MB; 150 DPI keeps quality under 1MB)
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ terminology_network.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ terminology_network.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def generate_domain_comparison(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate domain_comparison.png using the improved 2×3 ConceptVisualizer.

    Passes the full ``terms`` dict so the visualizer can compute real
    semantic entropy and bridging-term counts instead of falling back to
    pre-aggregated (often zero) stale values.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    domain_data = results["domain_data"]
    terms = results["terms"]
    filepath = Path(figure_dir) / "domain_comparison.png"

    viz = ConceptVisualizer(figsize=(16, 18))
    viz.create_domain_comparison_plot(
        domain_data=domain_data,
        filepath=filepath,
        terms=terms,
    )

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ domain_comparison.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ domain_comparison.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def generate_domain_overlap_heatmap(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate domain_overlap_heatmap.png showing cross-domain term sharing.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    terms = results["terms"]
    filepath = Path(figure_dir) / "domain_overlap_heatmap.png"

    # Build overlap matrix from terms using Szymkiewicz-Simpson coefficient
    # to match methodology (eq:overlap_coefficient) and manuscript caption
    domain_names = sorted({d for t in terms.values() for d in t.domains})

    if not domain_names:
        logger.warning("  ⚠️  No domain data available for heatmap generation")
        return ""

    # Use '||' as separator to avoid conflicts with domain names that contain '_and_'
    overlaps: Dict[str, Dict[str, Any]] = {}
    for d1 in domain_names:
        terms_d1 = {t for t, obj in terms.items() if d1 in obj.domains}
        for d2 in domain_names:
            terms_d2 = {t for t, obj in terms.items() if d2 in obj.domains}
            shared = terms_d1 & terms_d2
            min_size = min(len(terms_d1), len(terms_d2)) if terms_d1 and terms_d2 else 1
            overlap_coeff = len(shared) / min_size if min_size > 0 else 0.0
            key = f"{d1}||{d2}"
            overlaps[key] = {
                "overlap_percentage": overlap_coeff * 100 if d1 != d2 else 100.0,
                "overlap_count": len(shared),
                "shared_terms": list(shared)[:10],
                "coefficient": overlap_coeff,
            }

    viz = ConceptVisualizer(figsize=(12, 10))
    viz.create_domain_overlap_heatmap(
        domain_overlaps=overlaps,
        filepath=filepath,
        title="Cross-Domain Term Overlap in Ento-Linguistic Analysis",
    )

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ domain_overlap_heatmap.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ domain_overlap_heatmap.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def generate_anthropomorphic_analysis(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate anthropomorphic_framing.png showing human-derived terminology.

    Data source: the abstract artifact's real per-term framing
    proportions (``framing_terms`` — computed by
    ``pipeline.statistics_pipeline.build_statistical_analysis`` with
    ``layer="abstract"`` from every ±3-token context around each
    domain-term occurrence via
    ``LinguisticFeatureExtractor.extract_framing_features``).  When the
    statistics-stage section is absent, framing proportions are
    computed on the fly from ``results["terms"]`` and
    ``results["texts"]`` via the same machinery.  Categories are the
    six canonical Ento-Linguistic domains; a term appears in a category
    when it is assigned to that domain AND at least one of its
    occurrence contexts carries an anthropomorphic framing pattern
    (proportion > 0), sorted by framing proportion.  No curated word
    list.

    Args:
        results: Analysis pipeline results (``framing_terms`` from the
            statistics stage, or ``terms`` + ``texts`` to compute them).
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    filepath = Path(figure_dir) / "anthropomorphic_framing.png"

    # Real per-term framing proportions, organized by canonical domain.
    # Preferred source: the statistics stage's artifact section
    # (``results["framing_terms"]``).  When absent — e.g. direct
    # generator tests — compute it on the fly from the analyzed terms
    # and texts riding in ``results`` via the same public machinery the
    # statistics stage uses, so the figure never falls back to a
    # curated word list.
    framing_terms: Dict[str, Any] = results.get("framing_terms") or {}
    if not framing_terms:
        texts = results.get("texts") or []
        terms = results.get("terms") or {}
        if terms and texts:
            from pipeline.statistics_pipeline import _framing_section
            _, framing_terms = _framing_section(list(terms.values()), texts)
    if not framing_terms:
        logger.warning(
            "⚠️  anthropomorphic_framing.png skipped: no per-term framing "
            "data available (statistics stage produced no framing_terms "
            "and results carry no texts/terms to compute them)"
        )
        return ""
    # Domain slugs get manuscript-style display labels so the category
    # column stays readable.
    anthropomorphic_data: Dict[str, List[str]] = {}
    present_domains = {d for entry in framing_terms.values() for d in entry.get("domains", [])}
    for domain in [d for d in CANONICAL_DOMAINS if d in present_domains] + sorted(present_domains - set(CANONICAL_DOMAINS)):
        framed_terms = [
            term
            for term, entry in framing_terms.items()
            if domain in entry.get("domains", []) and entry.get("proportion", 0.0) > 0.0
        ]
        framed_terms.sort(
            key=lambda t: (
                -framing_terms[t]["proportion"],
                -framing_terms[t]["n_contexts"],
                t,
            )
        )
        if framed_terms:
            anthropomorphic_data[domain_display_name(domain)] = framed_terms

    if not anthropomorphic_data:
        logger.warning(
            "⚠️  anthropomorphic_framing.png skipped: no domain term shows "
            "anthropomorphic framing in the real extraction"
        )
        return ""

    viz = ConceptVisualizer(figsize=(16, 10))
    viz.create_anthropomorphic_analysis_plot(
        anthropomorphic_data=anthropomorphic_data,
        filepath=filepath,
    )

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ anthropomorphic_framing.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ anthropomorphic_framing.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def generate_concept_hierarchy(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate concept_hierarchy.png as a 2-panel overlap-strength figure.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    concept_map = results["concept_map"]
    filepath = Path(figure_dir) / "concept_hierarchy.png"

    # Weighted degree (strength): the concept categories form a complete
    # graph, so unweighted degree is identical (n-1) for every concept.
    # Strength = sum of overlap-coefficient weights to the other concepts.
    centrality_scores = {}
    term_counts: Dict[str, int] = {}
    for concept_name in concept_map.concepts:
        centrality_scores[concept_name] = float(sum(
            weight for _, weight in concept_map.get_connected_concepts(concept_name)
        ))
        term_counts[concept_name] = len(concept_map.concepts[concept_name].terms)

    hierarchy_data = {
        "centrality_scores": centrality_scores,
        "term_counts": term_counts,
    }

    viz = ConceptVisualizer(figsize=(18, 10))
    viz.visualize_concept_hierarchy(concept_hierarchy=hierarchy_data, filepath=filepath)

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ concept_hierarchy.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ concept_hierarchy.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


@publication_style
def generate_unit_of_individuality_patterns(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate unit_of_individuality_patterns.png.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    import matplotlib.pyplot as plt
    import numpy as np

    terms = results["terms"]
    domain = "unit_of_individuality"
    filepath = Path(figure_dir) / "unit_of_individuality_patterns.png"

    domain_terms = {
        name: t for name, t in terms.items() if domain in t.domains
    }

    if not domain_terms:
        logger.warning("  ⚠️  No terms found for unit_of_individuality domain")
        return ""

    # ── Left panel: term formation patterns ──
    # Shared classifier (same as domain_patterns_grid). The analysis
    # stage's ``term_patterns`` is NOT used: it counts non-exclusive
    # feature hits (compound / numeric / capitalised ...) and never counts
    # plain single words, so its shares are not a partition of the terms.
    formation_counts = Counter(classify_word_formation(name) for name in domain_terms)
    patterns_data = {
        label: formation_counts[label]
        for label, _ in sorted(
            formation_counts.items(), key=lambda kv: (-kv[1], kv[0])
        )
    }

    pattern_labels = list(patterns_data.keys())
    pattern_sizes = list(patterns_data.values())

    # ── Right panel: scale-level distribution ──
    scale_keywords = {
        "Colony\n(Superorganism)": {"colony", "superorganism", "collective",
                                    "nest", "colony-level"},
        "Sub-colony\n(Caste)": {"caste", "division", "worker", "queen",
                                "soldier", "subcaste"},
        "Individual\n(Worker)": {"individual", "nestmate", "ant", "insect",
                                 "worker"},
        "Genomic\n(Gene-level)": {"gene", "genetic", "genomic", "allele",
                                  "epigenetic"},
        "Emergent\n(Collective)": {"emergent", "self-organization", "swarm",
                                   "stigmergy", "distributed"},
    }
    scale_counts = {}
    for label, keywords in scale_keywords.items():
        count = sum(
            1 for name in domain_terms if any(k in name for k in keywords)
        )
        scale_counts[label] = count

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    formation_palette = {
        "Single word": "#4e79a7", "Multiword phrase": "#f28e2b",
        "Hyphenated compound": "#59a14f", "Underscore compound": "#e15759",
        "Contains digits": "#b07aa1",
    }
    pie_colors = [formation_palette.get(lab, "#bab0ac") for lab in pattern_labels]
    wedges, texts, autotexts = ax1.pie(
        pattern_sizes, colors=pie_colors,
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 3 else "",
        startangle=90, textprops={"fontsize": MIN_FONT},
    )
    for at in autotexts:
        at.set_fontweight("bold")
    ax1.legend(
        wedges, [f"{label} ({count})" for label, count in zip(pattern_labels, pattern_sizes)],
        loc="upper center", bbox_to_anchor=(0.5, -0.03),
        fontsize=MIN_FONT, frameon=False,
    )
    ax1.set_title("Term Formation Patterns", fontsize=MIN_FONT + 2,
                  fontweight="bold", pad=14)

    # Bar chart
    scales = list(scale_counts.keys())
    counts = list(scale_counts.values())
    bar_colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(scales)))
    bars = ax2.bar(range(len(scales)), counts, color=bar_colors,
                   edgecolor="white", linewidth=0.5)
    for bar, c in zip(bars, counts):
        ax2.annotate(str(c),
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=MIN_FONT,
                     fontweight="bold")
    ax2.set_xticks(range(len(scales)))
    ax2.set_xticklabels(
        scales, fontsize=MIN_FONT, rotation=30, ha="right",
        rotation_mode="anchor",
    )
    ax2.set_ylabel("Number of Terms", fontsize=MIN_FONT)
    ax2.set_title("Scale-Level Distribution", fontsize=MIN_FONT + 2,
                  fontweight="bold", pad=14)
    ax2.set_ylim(0, max(max(counts), 1) * 1.15)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle("Unit of Individuality — Terminology Patterns",
                 fontsize=MIN_FONT + 4, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ unit_of_individuality_patterns.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ unit_of_individuality_patterns.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


@publication_style
def generate_power_labor_term_frequencies(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate power_and_labor_term_frequencies.png.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    import matplotlib.pyplot as plt
    import numpy as np

    terms = results["terms"]
    domain = "power_and_labor"
    filepath = Path(figure_dir) / "power_and_labor_term_frequencies.png"

    domain_terms = {
        name: t for name, t in terms.items() if domain in t.domains
    }
    sorted_pairs = sorted(
        domain_terms.items(), key=lambda x: x[1].frequency, reverse=True
    )[:15]

    if not sorted_pairs:
        logger.warning("  ⚠️  No terms found for power_and_labor domain")
        return ""

    names = [p[0] for p in sorted_pairs]
    freqs = [p[1].frequency for p in sorted_pairs]

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(names)))
    bars = ax.bar(range(len(names)), freqs, color=colors, edgecolor="white",
                  linewidth=0.5)

    for bar, freq in zip(bars, freqs):
        ax.annotate(str(freq),
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=MIN_FONT,
                    fontweight="bold")

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=MIN_FONT)
    ax.set_ylabel("Frequency in Corpus", fontsize=MIN_FONT)
    ax.set_ylim(0, max(freqs) * 1.15)
    ax.set_title("Term Frequency Distribution — Power & Labor",
                 fontsize=MIN_FONT + 2, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ power_and_labor_term_frequencies.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ power_and_labor_term_frequencies.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


@publication_style
def generate_power_labor_ambiguities(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate power_and_labor_ambiguities.png.

    Two-panel figure:
      Left  — horizontal bar chart of H(t) per term, sorted descending.
      Right — scatter of corpus frequency vs H(t), sized by context count.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    import matplotlib.pyplot as plt
    import numpy as np

    terms = results["terms"]
    domain = "power_and_labor"
    filepath = Path(figure_dir) / "power_and_labor_ambiguities.png"

    domain_terms = {
        name: t for name, t in terms.items() if domain in t.domains
    }

    amb_data = sorted(
        [
            (name, t.semantic_entropy, t.frequency, len(t.contexts))
            for name, t in domain_terms.items()
            if t.semantic_entropy > 0.0
        ],
        key=lambda x: x[1], reverse=True,
    )[:15]

    if not amb_data:
        logger.warning("  ⚠️  No positive-entropy terms for power_and_labor")
        return ""

    names = [a[0] for a in amb_data]
    entropies = [a[1] for a in amb_data]
    freqs = [a[2] for a in amb_data]
    n_ctx = [a[3] for a in amb_data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8),
                                    gridspec_kw={"width_ratios": [1.2, 1]})
    fig.suptitle("Semantic Entropy — Power & Labor Domain",
                 fontsize=18, fontweight="bold", y=1.01)

    # ── Left panel: entropy bar chart ────────────────────────────────
    max_ent = max(entropies)
    min_ent = min(entropies)
    norm_vals = [(e - min_ent) / (max_ent - min_ent) if max_ent > min_ent else 0.5
                 for e in entropies]
    colors = plt.cm.Purples([0.3 + 0.5 * v for v in norm_vals])
    bars = ax1.barh(range(len(names)), entropies, color=colors,
                    edgecolor="white", linewidth=0.5)

    for bar, ent, nc in zip(bars, entropies, n_ctx):
        ax1.text(bar.get_width() + max_ent * 0.02,
                 bar.get_y() + bar.get_height() / 2,
                 f"{ent:.2f}  (n={nc})", ha="left", va="center",
                 fontsize=MIN_FONT, fontweight="bold")

    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names, fontsize=MIN_FONT)
    ax1.set_xlabel("Semantic Entropy H(t) (bits)", fontsize=MIN_FONT)
    ax1.set_title("Per-Term Entropy", fontsize=MIN_FONT + 2, fontweight="bold")
    x_pad = max_ent * 0.25
    ax1.set_xlim(0, max_ent + x_pad)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.tick_params(axis='x', labelsize=MIN_FONT)
    ax1.invert_yaxis()

    med_ent = float(np.median(entropies))
    ax1.axvline(med_ent, color="#888", linestyle="--", linewidth=1, alpha=0.6)
    # Median label sits in headroom above the first bar, clear of all bars.
    ax1.set_ylim(len(names) - 0.5, -1.4)
    ax1.text(med_ent, -0.75, f"median {med_ent:.2f}",
             fontsize=MIN_FONT, color="#555", ha="center", va="center")

    # ── Right panel: frequency vs entropy scatter ────────────────────
    sc_sizes = [max(40, c * 8) for c in n_ctx]
    ax2.margins(x=0.15)
    scatter = ax2.scatter(freqs, entropies, s=sc_sizes, c=entropies,
                          cmap="Purples", edgecolors="#333", linewidths=0.5,
                          alpha=0.85, vmin=0, vmax=max_ent)
    ax2.set_xlabel("Corpus Frequency", fontsize=MIN_FONT)
    ax2.set_ylabel("Semantic Entropy H(t) (bits)", fontsize=MIN_FONT)
    ax2.set_title("Frequency vs Entropy", fontsize=MIN_FONT + 2, fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(labelsize=MIN_FONT)
    fig.colorbar(scatter, ax=ax2, label="H(t) bits", shrink=0.75)

    plt.tight_layout()
    # Deterministic label placement (shared helper): offsets are searched
    # so no label overlaps another label or marker; labels that cannot be
    # placed cleanly are dropped (the point stays readable in the left
    # panel's ranked bars).
    fig.canvas.draw()
    place_labels(
        ax2,
        list(zip(names, zip(freqs, entropies))),
        avoid_points=[tuple(pt) for pt in ax2.transData.transform(
            np.column_stack([freqs, entropies]))],
        drop_on_fail=True,
        fontsize=MIN_FONT, color="#333",
    )

    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ power_and_labor_ambiguities.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ power_and_labor_ambiguities.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)

def generate_domain_overview_grid(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate domain_overview_grid.png: 6-panel top-terms grid (one per domain).

    Replaces the 12 scattered per-domain frequency and ambiguity single-panel
    figures with a single consolidated figure coloured by semantic entropy.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    domain_data = results["domain_data"]
    terms = results["terms"]
    filepath = Path(figure_dir) / "domain_overview_grid.png"

    viz = ConceptVisualizer(figsize=(18, 22))
    viz.create_domain_overview_grid(
        domain_data=domain_data,
        terms=terms,
        filepath=filepath,
    )

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ domain_overview_grid.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ domain_overview_grid.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def generate_domain_patterns_grid(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate domain_patterns_grid.png: 6-panel POS-composition donut grid.

    Replaces the 6 scattered per-domain single-bar patterns figures with an
    informative set of donut charts showing vocabulary structure per domain.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    terms = results["terms"]
    filepath = Path(figure_dir) / "domain_patterns_grid.png"

    viz = ConceptVisualizer(figsize=(16, 20))
    viz.create_domain_patterns_grid(
        terms=terms,
        filepath=filepath,
    )

    if not filepath.exists() or filepath.stat().st_size == 0:
        logger.error("  ❌ domain_patterns_grid.png save failed; figure NOT propagated")
        return ""
    logger.info(f"  ✅ domain_patterns_grid.png ({filepath.stat().st_size / 1024:.1f} KB)")
    return str(filepath)


def save_analysis_data(results: Dict[str, Any], data_dir: str) -> List[str]:
    """Save analysis results as data files.

    Args:
        results: Analysis pipeline results
        data_dir: Output directory for data files

    Returns:
        List of saved file paths
    """
    saved = []

    # Save corpus statistics
    corpus_stats_path = os.path.join(data_dir, "corpus_statistics.json")
    with open(corpus_stats_path, "w") as f:
        json.dump(results["corpus_stats"], f, indent=2, default=str)
    saved.append(corpus_stats_path)

    # The same occurrence-context framing estimand as the statistical layer.
    framing = results.get("framing")
    if framing is None:
        from pipeline.statistics_pipeline import _framing_section
        framing, _ = _framing_section(list(results["terms"].values()), results["texts"])

    domain_stats = {}
    for domain_name, data in results["domain_data"].items():
        # Compute anthropomorphic proportion for this domain
        domain_term_set = [
            t_text for t_text, t_obj in results["terms"].items()
            if domain_name in getattr(t_obj, "domains", [])
        ]
        anthro_proportion = framing.get(domain_name, {}).get("proportion", 0.0)

        # Count high-entropy terms (H > 2.0 bits) for this domain
        n_high_entropy = sum(
            1 for t in domain_term_set
            if t in results["terms"]
            and getattr(results["terms"][t], "semantic_entropy", 0.0) > 2.0
        )
        n_domain = sum(getattr(results["terms"][t], "entropy_status", None) == "ok"
                       for t in domain_term_set)
        high_entropy_pct = round(100 * n_high_entropy / n_domain, 1) if n_domain else 0.0

        from pipeline.statistics_pipeline import _domain_cace_scores
        cace_scores = _domain_cace_scores([results["terms"][name] for name in domain_term_set])
        domain_stats[domain_name] = {
            "cace_mean": float(np.mean([score.aggregate for score in cace_scores])) if cace_scores else None,
            "term_count": data["term_count"],
            "avg_confidence": float(data["avg_confidence"]),
            "total_frequency": data["total_frequency"],
            "bridging_term_count": len(data["bridging_terms"]),
            "bridging_terms": sorted(data["bridging_terms"]),
            "semantic_entropy": float(data.get("semantic_entropy", 0.0)),
            "entropy_valid_terms": n_domain,
            "entropy_excluded_terms": len(domain_term_set) - n_domain,
            "ambiguity_score": float(data.get("ambiguity_score", 0.0)),
            "anthropomorphic_proportion": anthro_proportion,
            "high_entropy_count": n_high_entropy,
            "high_entropy_pct": high_entropy_pct,
        }
    domain_stats_path = os.path.join(data_dir, "domain_statistics.json")
    with open(domain_stats_path, "w") as f:
        json.dump(domain_stats, f, indent=2, default=str)
    saved.append(domain_stats_path)

    # Save extracted terms summary
    terms_summary = {}
    for term_text, term_obj in results["terms"].items():
        terms_summary[term_text] = {
            "lemma": term_obj.lemma,
            "domains": term_obj.domains,
            "frequency": term_obj.frequency,
            "confidence": term_obj.confidence,
            "n_contexts": len(term_obj.contexts),
        }
    terms_path = os.path.join(data_dir, "extracted_terms.json")
    with open(terms_path, "w") as f:
        json.dump(terms_summary, f, indent=2, default=str)
    saved.append(terms_path)

    # Save concept map summary (includes terminology network statistics)
    import networkx as _nx

    _G = _nx.Graph()
    selected = sorted((name for name, term in results["terms"].items() if term.domains),
                      key=lambda name: (-results["terms"][name].frequency, name))[:100]
    _G.add_nodes_from(selected)
    for (_t1, _t2), _w in results["relationships"].items():
        _G.add_edge(_t1, _t2, weight=float(_w))
    _n_nodes = _G.number_of_nodes()
    _n_edges = _G.number_of_edges()
    if _n_nodes > 1 and _n_edges > 0:
        _clustering = round(float(_nx.average_clustering(_G)), 4)
        _avg_degree = round(2 * _n_edges / _n_nodes, 2)
    else:
        _clustering = 0.0
        _avg_degree = 0.0

    concept_summary = {
        "network_method": "document co-occurrence among top 100 domain-assigned terms",
        "n_concepts": len(results["concept_map"].concepts),
        "n_relationships": len(results["concept_map"].concept_relationships),
        "network_nodes": _n_nodes,
        "network_edges": _n_edges,
        "network_clustering": _clustering,
        "network_avg_degree": _avg_degree,
        "concepts": {
            name: {
                "description": c.description,
                "n_terms": len(c.terms),
                "domains": list(c.domains),
                "confidence": c.confidence,
            }
            for name, c in results["concept_map"].concepts.items()
        },
    }
    concept_path = os.path.join(data_dir, "concept_map_summary.json")
    with open(concept_path, "w") as f:
        json.dump(concept_summary, f, indent=2, default=str)
    saved.append(concept_path)

    logger.info(f"\n📊 Saved {len(saved)} data files to {data_dir}")
    for s in saved:
        logger.info(f"   - {os.path.basename(s)}")

    return saved


# ═══════════════════════════════════════════════════════════════════════
#  Figure Registry
# ═══════════════════════════════════════════════════════════════════════

def _register_figures_with_manager(figures: List[str], figure_dir: str) -> None:
    """Register generated figures with FigureManager for cross-referencing."""
    try:
        from visualization.figure_manager import FigureManager

        registry_file = os.path.join(figure_dir, "figure_registry.json")
        fm = FigureManager(registry_file=registry_file)

        figure_metadata = {
            "concept_map.png": {
                "label": "fig:concept_map",
                "caption": (
                    "Concept map of the Ento-Linguistic domains, built by "
                    "clustering the domain-assigned terminology of the "
                    "headline PubMed abstract layer (stored source hundred "
                    "abstracts). Each node is a concept cluster; node size "
                    "is proportional to its term count (annotated below the "
                    "label), node color encodes the concept's primary domain "
                    "(legend at right), and edge width is proportional to "
                    "relationship strength, with numeric weights at edge "
                    "midpoints. Multi-domain hub concepts bridge the domain "
                    "clusters."
                ),
                "section": "introduction",
            },
            "terminology_network.png": {
                "label": "fig:terminology_network",
                "caption": (
                    (
                    'Observed document co-occurrence among the hundred most frequent domain-assigned '
                    'terms. Node area uses a square-root frequency scale; line widths map shared-document '
                    'counts to a bounded range. A companion ranking shows the ten strongest pairs. '
                    'Up to twenty frequent terms are considered for '
                    'collision-filtered labels.'
                    )
                ),
                "section": "experimental_results",
            },
            "domain_comparison.png": {
                "label": "fig:domain_comparison",
                "caption": (
                    (
                    'Domain term counts, heuristic extraction confidence, frequency, mean valid '
                    'sentence-context entropy, bridging labels, and bounded-term heuristic CACE means. '
                    'These quantities are descriptive and do not validate causal framing effects.'
                    )
                ),
                "section": "experimental_results",
            },
            "domain_overlap_heatmap.png": {
                "label": "fig:domain_overlap",
                "caption": (
                    "Symmetric heatmap of Szymkiewicz--Simpson overlap "
                    "coefficients between each pair of the six "
                    "Ento-Linguistic domains, computed from term--domain "
                    "assignments of the headline PubMed abstract layer "
                    "(stored PubMed abstract source layer). Each cell is the "
                    "count of terms assigned to both domains divided by the "
                    "smaller domain's term count; the diagonal is one "
                    "hundred percent by construction; darker cells "
                    "(YlOrRd colormap) indicate higher shared terminology, "
                    "and zero cells are observed zeros of the current "
                    "corpus."
                ),
                "section": "experimental_results",
            },
            "anthropomorphic_framing.png": {
                "label": "fig:anthropomorphic",
                "caption": (
                    (
                    'Distinct extracted terms with at least one anthropomorphic marker-bearing occurrence '
                    'context, grouped by canonical domain, with example terms ranked by matched-context '
                    'proportion. Counts are not curated vocabulary sizes or validated author bias.'
                    )
                ),
                "section": "discussion",
            },
            "concept_hierarchy.png": {
                "label": "fig:concept_hierarchy",
                "caption": (
                    (
                    'Direct-link centrality of predefined concept categories and centrality against '
                    'associated-term counts. The graph describes vocabulary overlap, not biological '
                    'control or hierarchy.'
                    )
                ),
                "section": "discussion",
            },
            "unit_of_individuality_patterns.png": {
                "label": "fig:unit_individuality_patterns",
                "caption": (
                    "Two-panel terminology analysis of the Unit of "
                    "Individuality domain over the headline PubMed "
                    "abstract layer (stored PubMed abstract source layer). "
                    "Left: pie chart of term-formation patterns "
                    "(part-of-speech structure), percentages annotated. "
                    "Right: bar chart of the number of domain terms "
                    "matching keyword groups for five biological scales "
                    "(Colony, Sub-colony, Individual, Genomic, Emergent), "
                    "counts annotated; counts are floored at one for "
                    "display. The distribution across scales grounds the "
                    "scale ambiguity discussed in the manuscript."
                ),
                "section": "experimental_results",
            },
            "unit_of_individuality_term_frequencies.png": {
                "label": "fig:unit_individuality_frequencies",
                "caption": (
                    "Horizontal bar chart of the most frequent Unit of "
                    "Individuality terms by corpus frequency over the "
                    "headline PubMed abstract layer (stored source "
                    "hundred abstracts); bar length encodes frequency, "
                    "annotated at the bar tip."
                ),
            },
            "unit_of_individuality_ambiguities.png": {
                "label": "fig:unit_individuality_ambiguities",
                "caption": (
                    "Two-panel semantic-entropy analysis of Unit of "
                    "Individuality terms over the headline PubMed abstract "
                    "layer (stored PubMed abstract source layer). Left: "
                    "per-term entropy bars sorted descending, annotated "
                    "with entropy and context counts, with a dashed "
                    "median line. Right: corpus frequency versus entropy "
                    "scatter, point area proportional to context count "
                    "and color repeating the entropy scale."
                ),
            },
            "power_and_labor_term_frequencies.png": {
                "label": "fig:power_labor_frequencies",
                "caption": (
                    "Bar chart of the fifteen most frequent Power & Labor "
                    "terms by corpus frequency over the headline PubMed "
                    "abstract layer (stored PubMed abstract source layer). "
                    "Bar height encodes frequency, annotated at the bar "
                    "tip; bars ordered by descending frequency, with "
                    "YlOrRd shading tracking rank order only."
                ),
            },
            "power_and_labor_ambiguities.png": {
                "label": "fig:power_labor_ambiguities",
                "caption": (
                    "Two-panel semantic-entropy analysis of the fifteen "
                    "highest-entropy Power & Labor terms over the headline "
                    "PubMed abstract layer (about nineteen hundred "
                    "abstracts); entropy computed by TF-IDF vectorization "
                    "of each term's usage contexts followed by k-means "
                    "sense clustering. Left: per-term entropy bars sorted "
                    "descending, annotated with entropy and context "
                    "counts; dashed line marks the panel median. Right: "
                    "corpus frequency versus entropy scatter, point area "
                    "proportional to context count, color repeating the "
                    "entropy scale."
                ),
            },
            "domain_overview_grid.png": {
                "label": "fig:domain_overview_grid",
                "caption": (
                    "Six-panel grid (one panel per Ento-Linguistic "
                    "domain) of the ten highest-frequency terms by corpus "
                    "frequency over the headline PubMed abstract layer "
                    "(stored PubMed abstract source layer). Bar length "
                    "encodes corpus frequency (annotated at the bar tip); "
                    "panel titles give each domain's total term count; "
                    "bar color encodes per-term semantic entropy in bits "
                    "on a shared YlOrRd scale with a shared color bar; "
                    "darker bars indicate terms whose usage contexts "
                    "span more sense clusters."
                ),
            },
            "domain_patterns_grid.png": {
                "label": "fig:domain_patterns_grid",
                "caption": (
                    "Six-panel grid of donut charts showing the "
                    "word-formation composition of each Ento-Linguistic "
                    "domain's vocabulary over the headline PubMed "
                    "abstract layer (stored PubMed abstract source layer). "
                    "Each slice is a word-formation class (hyphenated "
                    "compound, multiword phrase, or single word) with "
                    "angle proportional to its share of the domain's "
                    "term counts; categories beyond the six largest are "
                    "grouped as Other; the donut centre annotates the "
                    "domain's term count."
                ),
            },
            "statistical_analysis.png": {
                "label": "fig:statistical_analysis",
                "caption": (
                    (
                    'Exploratory entropy descriptives over source-identified abstract records, nominal '
                    'intervals where estimable, standardized differences and BH threshold flags, and an '
                    'omnibus ANOVA summary. Shared terms and documents limit independence and population '
                    'inference.'
                    )
                ),
                "section": "experimental_results",
            },
            "fulltext_analysis.png": {
                "label": "fig:fulltext_analysis",
                "caption": (
                    (
                    'Exploratory entropy descriptives and numerical comparisons over the stored PMC '
                    'full-text corpus. The same definitions apply as for abstracts; different extraction '
                    'thresholds and source composition limit cross-layer interpretation.'
                    )
                ),
                "section": "supplemental_results",
            },
            "layer_comparison.png": {
                "label": "fig:layer_comparison",
                "caption": (
                    (
                    'Mean successfully computed sentence-context entropy by domain in the abstract and '
                    'full-text layers. Term counts annotate valid estimates. Differences are descriptive '
                    'rather than a matched robustness or causal test.'
                    )
                ),
                "section": "supplemental_results",
            },
            "discourse_comparison.png": {
                "label": "fig:discourse_comparison",
                "caption": (
                    "Grouped bars of corpus-level discourse frequencies "
                    "comparing the headline PubMed abstract layer (solid "
                    "bars, discourse pass over its full analyzed sample) "
                    "with the PMC full-text parallel layer (hatched bars, "
                    "discourse pass over its deterministic 20% text "
                    "sample; per-layer analyzed-text counts are given in "
                    "the legend). Three panels, one per shared discourse "
                    "dimension: discourse patterns (anthropomorphic "
                    "framing, economic metaphors, hierarchical framing, "
                    "scale ambiguity), rhetorical strategies (analogy, "
                    "anecdotal, authority, generalization), and "
                    "persuasive techniques (authoritative citations, "
                    "metaphorical language, quantitative emphasis, "
                    "rhetorical questions). Panels whose plotted maximum "
                    "spans at least two orders of magnitude above their "
                    "smallest positive frequency use a symlog y-axis "
                    "(linear below one occurrence) so both layers remain "
                    "legible. Between-layer differences are descriptive "
                    "of the two corpora and sampling fractions and are "
                    "not significance-tested in this figure."
                ),
                "section": "supplemental_results",
            },
        }


        figure_metadata.update({
            "bhl_term_usage.png": {
                "label": "fig:bhl_term_usage", "section": "supplemental_analysis",
                "caption": "Literal term frequencies per 10,000 OCR tokens across the complete BHL historical source layer; era differences are descriptive, with no causal or representativeness inference.",
            },
            "arxiv_analysis.png": {
                "label": "fig:arxiv_analysis", "section": "supplemental_results",
                "caption": "Exploratory entropy comparisons over all stored arXiv preprint records; overlapping domain groups and shared source documents limit inferential interpretation.",
            },
        })
        # Dynamically register domain figures to ensure full coverage
        valid_domains = [
            "unit_of_individuality",
            "behavior_and_identity",
            "power_and_labor",
            "sex_and_reproduction",
            "kin_and_relatedness",
            "economics",
        ]
        
        for domain in valid_domains:
            # Normalize label keys to match manuscript conventions
            # e.g., unit_of_individuality -> unit_individuality
            # e.g., power_and_labor -> power_labor
            label_base = domain.replace("_and_", "_").replace("unit_of_", "unit_")
            d_title = domain_display_name(domain)
            
            # Register all 3 types if not already manually defined
            display_map = {
                "patterns": (f"fig:{label_base}_patterns", f"{d_title} Term Patterns"),
                "term_frequencies": (f"fig:{label_base}_frequencies", f"{d_title} Term Frequencies"),
                "ambiguities": (f"fig:{label_base}_ambiguities", f"{d_title} Ambiguity Analysis"),
            }
            
            for type_suffix, (label, caption) in display_map.items():
                filename = f"{domain}_{type_suffix}.png"
                if filename not in figure_metadata:
                    figure_metadata[filename] = {
                        "label": label,
                        "caption": caption,
                        "section": "experimental_results",
                    }

        registered = 0
        for fig_path in figures:
            filename = os.path.basename(fig_path)
            # Defense in depth: never register a figure that is not on disk
            if not os.path.isfile(fig_path) or os.path.getsize(fig_path) == 0:
                logger.warning(f"⚠️  Skipping registration of unsaved figure: {fig_path}")
                continue
            if filename in figure_metadata:
                meta = figure_metadata[filename]
                fm.register_figure(
                    filename=filename,
                    caption=meta["caption"],
                    label=meta["label"],
                    section=meta.get("section"),
                    generated_by="src/visualization/manuscript_figures.py",
                    sha256=hashlib.sha256(Path(fig_path).read_bytes()).hexdigest(),
                )
                registered += 1

        logger.info(f"✅ Registered {registered} figures with FigureManager")

    except ImportError:
        raise
    except Exception as e:
        raise RuntimeError(f"Could not register figures: {e}") from e


# ═══════════════════════════════════════════════════════════════════════
#  Full-Text Stage Helpers
# ═══════════════════════════════════════════════════════════════════════

def _fulltext_corpus_fingerprint(
    fulltexts: List[Dict[str, Any]], fulltexts_dir: str
) -> Dict[str, Any]:
    """Fingerprint the full-text corpus for artifact freshness.

    Binds ordered body contents, provenance, implementation, locked
    dependencies, selected NLTK resources and any development limit.
    Metadata equality alone cannot reuse changed document bodies.

    Args:
        fulltexts: Corpus records loaded from the shards.
        fulltexts_dir: Corpus directory holding ``provenance.json``.

    Returns:
        ``{"record_count": int, "provenance_sha256": str, "limit": None}``.
        The ``limit`` key is ``None`` for the unbounded (full-corpus)
        fingerprint; the stage records the applied bound there so a
        bounded artifact can never satisfy the full-corpus guard.
    """
    provenance_path = os.path.join(fulltexts_dir, "provenance.json")
    if os.path.isfile(provenance_path):
        with open(provenance_path, "rb") as f:
            provenance_sha = hashlib.sha256(f.read()).hexdigest()
    else:
        provenance_sha = "absent"
    from core.provenance import records_sha256, analysis_signature

    return {
        "records_sha256": records_sha256(fulltexts),
        "analysis_signature": analysis_signature(),
        "record_count": len(fulltexts),
        "provenance_sha256": provenance_sha,
        "limit": None,
    }


def max_mtime(directory: str, pattern: str) -> Optional[float]:
    """Newest file mtime in ``directory`` among names matching ``pattern``.

    Args:
        directory: Directory to scan (non-recursive).
        pattern: ``fnmatch`` pattern for candidate file names.

    Returns:
        The newest mtime, or ``None`` when the directory holds no match
        (or does not exist).
    """
    import fnmatch

    try:
        candidates = [
            name for name in os.listdir(directory) if fnmatch.fnmatch(name, pattern)
        ]
    except OSError:
        return None
    mtimes = [
        os.path.getmtime(os.path.join(directory, name)) for name in candidates
    ]
    return max(mtimes) if mtimes else None


def _bhl_artifact_summary(project_root: str) -> Optional[Dict[str, Any]]:
    """Load the BHL era-stratified artifact when present.

    Args:
        project_root: Project root holding ``data/bhl``.

    Returns:
        Parsed ``era_term_usage.json``, or ``None`` when the BHL
        historical layer has not been harvested.
    """
    path = os.path.join(project_root, "data", "bhl", "era_term_usage.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        logger.warning("⚠️  Unreadable BHL artifact %s: %s", path, exc)
        return None


# ═══════════════════════════════════════════════════════════════════════
#  Full-Text Corpus Fingerprint Guard
# ═══════════════════════════════════════════════════════════════════════


def _ensure_fulltext_artifact(
    data_dir: str,
    fulltexts_dir: str,
    builder: Optional["Callable[..., Dict[str, Any]]"] = None,
) -> Optional[Dict[str, Any]]:
    """Load or rebuild the full-text analysis artifact under the
    corpus fingerprint freshness guard.

    The corpus is loaded from ``fulltexts_NNNNN.json`` shards and
    fingerprinted (record count + provenance SHA-256, see
    :func:`_fulltext_corpus_fingerprint`).  When the existing
    ``<data_dir>/fulltext_analysis.json`` records the same fingerprint
    the artifact is reused as-is; otherwise it is rebuilt (full corpus
    by default, ``FULLTEXT_ANALYSIS_LIMIT`` bounding quick runs) and
    the applied bound is recorded inside the stored fingerprint so a
    bounded artifact can never satisfy the full-corpus guard.  The
    existing artifact lacking a fingerprint (pre-guard output) counts
    as stale and is regenerated once.

    Args:
        data_dir: Output data directory holding the artifact.
        fulltexts_dir: Corpus directory with shards and provenance.
        builder: Analysis builder override for tests (defaults to
            ``pipeline.fulltext_pipeline.build_fulltext_analysis``).

    Returns:
        The artifact dict (fresh or newly built), or ``None`` when the
        corpus shards are missing.
    """
    shards = sorted(
        p
        for p in os.listdir(fulltexts_dir)
        if p.startswith("fulltexts_") and p.endswith(".json")
    ) if os.path.isdir(fulltexts_dir) else []
    if not shards:
        logger.warning(
            "⚠️  %s holds no fulltexts_*.json shards — full-text layer "
            "stage skipped (run the full-text harvest first)",
            fulltexts_dir,
        )
        return None
    try:
        from data.pmc_fulltext import load_fulltexts
    except (ImportError, ValueError):
        from src.data.pmc_fulltext import load_fulltexts

    corpus = load_fulltexts(Path(fulltexts_dir))
    fingerprint = _fulltext_corpus_fingerprint(corpus, fulltexts_dir)
    limit_env = os.environ.get("FULLTEXT_ANALYSIS_LIMIT")
    limit = int(limit_env) if limit_env else None
    if limit is not None and limit <= 0:
        raise ValueError("FULLTEXT_ANALYSIS_LIMIT must be a positive integer")
    limit = limit if limit is not None and limit < len(corpus) else None
    fingerprint["limit"] = limit
    artifact_path = os.path.join(data_dir, "fulltext_analysis.json")
    existing: Optional[Dict[str, Any]] = None
    if os.path.isfile(artifact_path):
        try:
            with open(artifact_path) as f:
                existing = json.load(f)
        except (OSError, ValueError) as exc:
            logger.warning(
                "⚠️  Unreadable existing artifact %s: %s", artifact_path, exc
            )
    if existing and existing.get("corpus_fingerprint") == fingerprint:
        logger.info(
            "  ✅ fulltext_analysis.json is fresh for corpus fingerprint "
            "%s — skipping regeneration (%d documents)",
            fingerprint,
            existing.get("n_documents", 0),
        )
        return existing

    # Bounded subset for runtime: the FULL corpus is the default (the
    # artifact is expensive and only rebuilt when the corpus changes);
    # override with FULLTEXT_ANALYSIS_LIMIT for quick runs.
    fulltexts = corpus
    if limit and 0 < limit < len(fulltexts):
        logger.info(
            "  FULLTEXT_ANALYSIS_LIMIT=%s: analyzing first %d of %d documents",
            limit,
            limit,
            len(fulltexts),
        )
        fulltexts = fulltexts[:limit]
    bounded_fingerprint = dict(fingerprint, limit=limit)
    logger.info("▶ Building full-text analysis artifact...")
    if builder is None:
        from pipeline.fulltext_pipeline import build_fulltext_analysis

        builder = build_fulltext_analysis
    artifact = builder(fulltexts)
    artifact["corpus_fingerprint"] = bounded_fingerprint
    os.makedirs(data_dir, exist_ok=True)
    with open(artifact_path, "w") as f:
        json.dump(artifact, f, indent=2, default=str)
    logger.info(
        f"  ✅ fulltext_analysis.json: {artifact['n_documents']} "
        f"documents, {len(artifact['pairwise'])} pairwise tests, "
        f"{len(artifact.get('skipped', []))} skipped"
    )
    return artifact


def _abstract_corpus_fingerprint(
    abstracts: List[str], abstracts_path: str
) -> Dict[str, Any]:
    """Fingerprint the abstract corpus for the statistics-stage guard.

    Same convention as :func:`_fulltext_corpus_fingerprint`: record
    count plus the SHA-256 of the corpus file (``corpus/abstracts.json``)
    — two cheap reads that change whenever the harvested corpus changes.

    Args:
        abstracts: Loaded abstract strings.
        abstracts_path: Path of the abstracts JSON file.

    Returns:
        ``{"record_count": int, "abstracts_sha256": str}``.
    """
    if abstracts_path and os.path.isfile(abstracts_path):
        with open(abstracts_path, "rb") as f:
            abstracts_sha = hashlib.sha256(f.read()).hexdigest()
    else:
        abstracts_sha = "absent"
    from core.provenance import records_sha256, analysis_signature
    return {"record_count": len(abstracts), "abstracts_sha256": abstracts_sha,
            "records_sha256": records_sha256(abstracts),
            "analysis_signature": analysis_signature()}


def _abstracts_corpus_path() -> str:
    """Locate ``corpus/abstracts.json`` the same way
    :func:`load_real_corpus` does (best effort; ``""`` when unknown)."""
    try:
        from data.loader import DataLoader

        return os.path.join(DataLoader().data_root, "corpus/abstracts.json")
    except Exception:
        return ""


def _ensure_statistical_artifact(
    data_dir: str,
    terms: "Dict[str, Any]",
    abstracts: List[str],
    builder: Optional["Callable[..., Dict[str, Any]]"] = None,
    corpus_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Load or rebuild the abstract-layer statistical artifact under a
    corpus-fingerprint freshness guard.

    The artifact is expensive (per-term semantic entropy over the whole
    abstract corpus), so it is only rebuilt when the abstract corpus
    actually changes: ``corpus/abstracts.json`` is fingerprinted (record
    count + SHA-256, :func:`_abstract_corpus_fingerprint`) and compared
    against the stored ``corpus_fingerprint`` of the existing artifact.
    A pre-guard artifact (no fingerprint) counts as stale and is
    regenerated once.  The fingerprint is attached to the artifact AFTER
    the frozen-schema build (mirroring the full-text stage), so
    ``build_statistical_analysis``'s own schema contract is untouched.

    Args:
        data_dir: Output data directory holding the artifact.
        terms: Extracted terms (from the abstract analysis pipeline; a
            deterministic function of the abstract corpus).
        abstracts: The real abstract corpus (as loaded for the build).
        builder: Analysis builder override for tests (defaults to
            ``pipeline.statistics_pipeline.build_statistical_analysis``).

    Returns:
        The artifact dict (fresh or reused).
    """
    artifact_path = os.path.join(data_dir, "statistical_analysis.json")
    fingerprint = _abstract_corpus_fingerprint(
        abstracts, corpus_path if corpus_path is not None else _abstracts_corpus_path()
    )
    existing: Optional[Dict[str, Any]] = None
    if os.path.isfile(artifact_path):
        try:
            with open(artifact_path) as f:
                existing = json.load(f)
        except (OSError, ValueError) as exc:
            logger.warning(
                "⚠️  Unreadable existing artifact %s: %s", artifact_path, exc
            )
    if existing and existing.get("corpus_fingerprint") == fingerprint:
        logger.info(
            "  ✅ statistical_analysis.json is fresh for corpus "
            "fingerprint %s — skipping regeneration (%d abstracts)",
            fingerprint["abstracts_sha256"][:12],
            fingerprint["record_count"],
        )
        return existing

    logger.info("▶ Building statistical analysis artifact...")
    if builder is None:
        from pipeline.statistics_pipeline import build_statistical_analysis

        builder = build_statistical_analysis
    artifact = builder(terms, abstracts, layer="abstract")
    artifact["corpus_fingerprint"] = fingerprint
    os.makedirs(data_dir, exist_ok=True)
    with open(artifact_path, "w") as f:
        json.dump(artifact, f, indent=2, default=str)
    return artifact


def _merge_discourse_sections(data_dir: str, fulltexts_dir: str) -> None:
    """Compute and merge the corpus-level ``discourse`` section into BOTH
    layer artifacts on disk.

    The abstract artifact is usually already carrying the section (the
    statistics stage computes it inside
    ``build_statistical_analysis``); it is only recomputed here when the
    on-disk artifact lacks it.  The fingerprint-guarded full-text
    artifact is augmented in place — the discourse pass runs over the
    harvested full-text corpus with the deterministic bounded sample of
    :func:`pipeline.statistics_pipeline.add_discourse_analysis`, so the
    multi-hour statistics stages are NOT recomputed.

    Degenerate inputs (missing artifact, no eligible texts) are logged
    and skipped — never fabricated.

    Args:
        data_dir: Output data directory holding both artifacts.
        fulltexts_dir: Corpus directory with ``fulltexts_NNNNN.json``
            shards.
    """
    from pipeline.statistics_pipeline import add_discourse_analysis

    def _merge(path: str, texts: List[str]) -> None:
        with open(path) as f:
            artifact = json.load(f)
        if artifact.get("discourse"):
            logger.info(
                "  ✅ %s already carries a discourse section — skipping "
                "recompute",
                os.path.basename(path),
            )
            return
        merged = add_discourse_analysis(artifact, texts)
        if not merged.get("discourse"):
            logger.warning(
                "⚠️  %s: no text eligible for discourse analysis "
                "(all below the minimum length) — section omitted",
                os.path.basename(path),
            )
            return
        with open(path, "w") as f:
            json.dump(merged, f, indent=2, default=str)
        section = merged["discourse"]
        logger.info(
            "  ✅ %s: discourse section merged (%d/%d texts analyzed, "
            "sample_fraction %s)",
            os.path.basename(path),
            section["n_texts_analyzed"],
            section["n_texts"],
            section["sample_fraction"],
        )

    # ── Abstract layer ────────────────────────────────────────────────
    stats_path = os.path.join(data_dir, "statistical_analysis.json")
    if os.path.isfile(stats_path):
        _merge(stats_path, load_real_corpus(str(Path(data_dir).parents[1]), require_provenance=True))
    else:
        logger.warning(
            "⚠️  statistical_analysis.json missing — abstract discourse "
            "section skipped (statistics stage failed?)"
        )

    # ── Full-text layer ───────────────────────────────────────────────
    fulltext_path = os.path.join(data_dir, "fulltext_analysis.json")
    if not os.path.isfile(fulltext_path):
        logger.warning(
            "⚠️  fulltext_analysis.json missing — full-text discourse "
            "section skipped"
        )
        return
    try:
        from data.pmc_fulltext import load_fulltexts
    except (ImportError, ValueError):
        from src.data.pmc_fulltext import load_fulltexts
    from pipeline.fulltext_pipeline import _document_text

    records = load_fulltexts(Path(fulltexts_dir))
    _merge(fulltext_path, [_document_text(record) for record in records])


# ═══════════════════════════════════════════════════════════════════════
#  Main Entry Point
# ═══════════════════════════════════════════════════════════════════════
def ensure_auxiliary_artifacts(root: Path) -> Dict[str, Dict[str, Any]]:
    """Rebuild BHL/arXiv artifacts when records or implementation change."""
    from core.provenance import records_sha256, analysis_signature
    output = {}
    arxiv_path = root / "data" / "corpus" / "arxiv_records.json"
    bhl_dir = root / "data" / "bhl"
    sources = []
    if arxiv_path.exists():
        from pipeline.arxiv_analysis import load_arxiv_records, build_arxiv_analysis
        sources.append(("arxiv_analysis.png", arxiv_path.with_name("arxiv_analysis.json"),
                        load_arxiv_records(arxiv_path), build_arxiv_analysis))
    if list(bhl_dir.glob("bhl_shard_*.json")):
        from pipeline.bhl_analysis import load_corpus_records_for_analysis, build_artifact
        sources.append(("bhl_term_usage.png", bhl_dir / "era_term_usage.json",
                        load_corpus_records_for_analysis(bhl_dir),
                        lambda records: build_artifact(bhl_dir, records, root / "output" / ".checkpoints" / "bhl")))
    for filename, destination, records, builder in sources:
        expected = {"record_count": len(records), "records_sha256": records_sha256(records),
                    "analysis_signature": analysis_signature()}
        if filename == "bhl_term_usage.png":
            from pipeline.bhl_analysis import stack_character_budget
            expected["stack_character_budget"] = stack_character_budget()
        existing = json.loads(destination.read_text()) if destination.exists() else {}
        if existing.get("corpus_fingerprint") != expected:
            logger.info("Rebuilding auxiliary layer: %s (%d documents)", filename, len(records))
            existing = builder(records)
            temporary = destination.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(existing, indent=2, sort_keys=True, allow_nan=False) + "\n")
            temporary.replace(destination)
        output[filename] = existing
    return output


def generate_bhl_usage(artifact: Dict[str, Any], figure_dir: str) -> str:
    """Plot complete-corpus literal historical rates without causal labels."""
    selected = ("queen", "worker", "caste", "colony", "superorganism", "kin")
    eras = artifact["eras"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    for ax, term in zip(axes.flat, selected):
        values = [entry["terms_per_10k"][term] for entry in eras.values()]
        ax.bar([era.replace("era_", "").replace("_", "–") for era in eras], values)
        ax.set_title(term, fontsize=MIN_FONT + 2)
        ax.set_ylabel("Matches per 10,000 OCR tokens", fontsize=MIN_FONT)
        ax.tick_params(labelsize=MIN_FONT)
        ax.tick_params(axis="x", labelrotation=30)
    fig.suptitle("BHL historical source layer: complete-corpus literal term usage", fontsize=MIN_FONT + 3)
    fig.tight_layout()
    path = Path(figure_dir) / "bhl_term_usage.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def main(project_root: Optional[str] = None) -> None:
    """Generate all research figures and data using the real analysis pipeline.

    Args:
        project_root: Project root used for output directories and manuscript
            variable filling. Defaults to the project root derived from this
            module's location. Thin orchestrator scripts pass their own
            ``__file__``-derived root so behaviour is identical when the
            script is copied elsewhere.
    """
    if project_root is None:
        project_root = _PROJECT_ROOT
    abstracts = load_real_corpus(project_root, require_provenance=True)
    output_dir, data_dir, figure_dir = _setup_directories(project_root)

    logger.info("=" * 70)

    logger.info("  Ento-Linguistic Research Figure Generation Pipeline")
    logger.info("=" * 70)
    logger.info(f"  Output: {output_dir}")
    logger.info(f"  Corpus: {len(abstracts)} real abstracts")
    logger.info("")

    if not abstracts:
        raise ValueError("Cannot analyze an empty corpus")

    # ── Run analysis pipeline ─────────────────────────────────────────
    logger.info("▶ Running analysis pipeline...")
    results = run_analysis_pipeline(abstracts)
    stored_count = len(load_real_corpus(project_root))
    results["corpus_stats"].update(n_documents=len(abstracts), stored_documents=stored_count,
                                  excluded_unreconciled=stored_count - len(abstracts))
    logger.info("")

    # ── Generate figures ──────────────────────────────────────────────
    logger.info("▶ Generating figures...")
    figures = []

    # ── Statistical analysis stage ────────────────────────────────────
    # Runs after term/domain analysis. Required statistics failures
    # propagate; no successful receipt is written for a partial run.
    #
    # Reuse requires equal ordered inputs, provenance, implementation,
    # dependency lock and selected NLTK resource contents.
    try:
        try:
            from .statistical_visualization import plot_statistical_analysis
        except (ImportError, ValueError):
            from visualization.statistical_visualization import (
                plot_statistical_analysis,
            )

        stats_artifact = _ensure_statistical_artifact(
            data_dir, results["terms"], abstracts,
            corpus_path=str(Path(project_root) / "data" / "corpus" / "abstracts.json")
        )
        logger.info(
            f"  ✅ statistical_analysis.json: {len(stats_artifact['pairwise'])} "
            f"pairwise tests, {len(stats_artifact.get('skipped', []))} skipped"
        )
        # Per-term framing proportions feed the anthropomorphic-terminology
        # figure (real LinguisticFeatureExtractor-derived data, no curated list).
        results["framing_terms"] = stats_artifact.get("framing_terms") or {}
        results["framing"] = stats_artifact["framing"]
        fig_path = plot_statistical_analysis(stats_artifact, figure_dir)
        figures.append(fig_path)
    except Exception as exc:
        raise RuntimeError(f"Statistical analysis stage warning: {exc}") from exc

    # ── Full-text parallel layer stage ────────────────────────────────
    # Builds output/data/fulltext_analysis.json from the PMC full-text
    # corpus shards (data/fulltexts/fulltexts_NNNNN.json), mirroring the
    # abstract-layer statistics schema, and renders the parallel figure.
    # Required-stage failure propagates, preventing a success receipt.
    #
    # Full-text cache reuse binds body contents, provenance, source,
    # dependencies and selected NLTK resources. The default bound is UNSET (full
    # corpus); FULLTEXT_ANALYSIS_LIMIT still bounds for quick runs, and
    # a bounded run records its limit in the fingerprint so it can never
    # satisfy the full-corpus guard.  See
    # :func:`_ensure_fulltext_artifact`.
    fulltexts_dir = os.path.join(project_root, "data", "fulltexts")
    try:
        fulltext_artifact = _ensure_fulltext_artifact(data_dir, fulltexts_dir)
    except Exception as exc:
        fulltext_artifact = None
        raise RuntimeError(f"Full-text analysis stage warning: {exc}") from exc

    if fulltext_artifact is not None:
        try:
            fig_path = plot_statistical_analysis(
                fulltext_artifact, figure_dir, filename="fulltext_analysis.png"
            )
            figures.append(fig_path)
        except Exception as exc:
            raise RuntimeError(f"Full-text figure warning: {exc}") from exc

        # ── Layer-comparison figure ───────────────────────────────────
        # Rendered when BOTH the abstract-layer statistics artifact and
        # the full-text artifact exist on disk.
        try:
            try:
                from .statistical_visualization import plot_layer_comparison
            except (ImportError, ValueError):
                from visualization.statistical_visualization import (
                    plot_layer_comparison,
                )
            stats_disk_path = os.path.join(data_dir, "statistical_analysis.json")
            abstract_artifact: Optional[Dict[str, Any]] = None
            if os.path.isfile(stats_disk_path):
                with open(stats_disk_path) as f:
                    abstract_artifact = json.load(f)
            if abstract_artifact and fulltext_artifact:
                fig_path = plot_layer_comparison(
                    abstract_artifact, fulltext_artifact, figure_dir
                )
                figures.append(fig_path)
            else:
                logger.warning(
                    "⚠️  layer_comparison.png skipped: abstract and/or "
                    "full-text artifacts missing"
                )
        except Exception as exc:
            raise RuntimeError(f"Layer-comparison stage warning: {exc}") from exc

        # ── Discourse-comparison figure ───────────────────────────────
        # Rendered when BOTH artifacts exist (same availability guard as
        # the layer-comparison figure above).  No additional fingerprint
        # treatment needed: the discourse stage merges the ``discourse``
        # sections in place and preserves the full-text artifact's
        # ``corpus_fingerprint`` (see _merge_discourse_sections), so this
        # re-render never clobbers the freshness guard.
        try:
            try:
                from .statistical_visualization import (
                    plot_discourse_comparison,
                )
            except (ImportError, ValueError):
                from visualization.statistical_visualization import (
                    plot_discourse_comparison,
                )
            if abstract_artifact and fulltext_artifact:
                fig_path = plot_discourse_comparison(
                    abstract_artifact, fulltext_artifact, figure_dir
                )
                figures.append(fig_path)
            else:
                logger.warning(
                    "⚠️  discourse_comparison.png skipped: abstract and/or "
                    "full-text artifacts missing"
                )
        except Exception as exc:
            raise RuntimeError(f"Discourse-comparison stage warning: {exc}") from exc
    else:
        logger.warning("⚠️  Discourse-comparison stage warning: full-text artifact unavailable")
    auxiliary = ensure_auxiliary_artifacts(Path(project_root))
    for filename, artifact in auxiliary.items():
        if filename == "arxiv_analysis.png":
            figures.append(plot_statistical_analysis(artifact, figure_dir, filename=filename))
        else:
            figures.append(generate_bhl_usage(artifact, figure_dir))

    # ── Discourse analysis stage ──────────────────────────────────────
    # Adds the corpus-level discourse/rhetorical/persuasive section to
    # BOTH artifacts on disk (abstract + full-text), after the
    # statistics/full-text stages and before figure generation.  The
    # anthropomorphic-terminology figure below reads the real per-term
    # framing proportions from the abstract artifact's framing data.
    try:
        _merge_discourse_sections(data_dir, fulltexts_dir)
    except Exception as exc:
        raise RuntimeError(f"Discourse analysis stage warning: {exc}") from exc

    fig_path = generate_concept_map(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_terminology_network(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_domain_comparison(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_domain_overlap_heatmap(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_anthropomorphic_analysis(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_concept_hierarchy(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_unit_of_individuality_patterns(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_power_labor_term_frequencies(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_power_labor_ambiguities(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_domain_overview_grid(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    fig_path = generate_domain_patterns_grid(results, figure_dir)
    if fig_path:
        figures.append(fig_path)

    logger.info("")

    # ── Save data ─────────────────────────────────────────────────────
    data_files = save_analysis_data(results, data_dir)

    # ── Register figures ──────────────────────────────────────────────
    _register_figures_with_manager(figures, figure_dir)

    # ── Summary ───────────────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"  ✅ Generated {len(figures)} research figures")
    for fig in figures:
        logger.info(f"     - {os.path.basename(fig)}")
    logger.info(f"  ✅ Saved {len(data_files)} data files")
    logger.info(f"  📁 All outputs: {output_dir}")
    logger.info("=" * 70)

    # Also print for subprocess test capture
    print("Integration with src/ modules demonstrated")

    # ── Fill manuscript template variables ─────────────────────────────
    try:
        from core.manuscript_variables import (
            RENDER_STAGE_PREFIXES,
            build_variable_map,
            fill_manuscript,
        )
        logger.info("▶ Filling manuscript template variables...")
        variables = build_variable_map(
            output_data_dir=Path(project_root) / "output" / "data",
            corpus_dir=Path(project_root) / "data" / "corpus",
        )
        # Validate token coverage WITHOUT rewriting the canonical markdown:
        # substitution happens at PDF render time (_render_pdf_override /
        # build_pdf), so writing substituted text back into docs/manuscript
        # would destroy the {{...}} placeholders the editing rule requires.
        manuscript_path = Path(project_root) / "docs" / "manuscript"
        unresolved = sorted({key for path in manuscript_path.glob("*.md")
                             for key in re.findall(r"\{\{([A-Z0-9_]+)\}\}", path.read_text())
                             if key not in variables
                             and not key.startswith(RENDER_STAGE_PREFIXES)})
        if unresolved:
            raise ValueError(f"Unresolved manuscript variables: {unresolved}")
        results_fill = fill_manuscript(
            variables, manuscript_dir=Path(project_root) / "docs" / "manuscript",
            dry_run=True,
        )
        total_subs = sum(results_fill.values())
        logger.info(
            f"  ✅ {total_subs} placeholder occurrences resolvable across "
            f"{len(results_fill)} files (dry run; canonical files unchanged)"
        )
    except Exception as exc:
        raise RuntimeError(f"Manuscript variable fill warning: {exc}") from exc

    from core.provenance import validate_generated_artifacts
    validate_generated_artifacts(Path(project_root))
    logger.info("Local JSON, PNG and registry integrity validation passed")

    from core.manuscript_variables import RENDER_STAGE_FIGURE_DIR
    from core.provenance import write_analysis_manifest
    for path in (Path(project_root) / "docs" / "manuscript").glob("*.md"):
        for image in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", path.read_text()):
            if RENDER_STAGE_FIGURE_DIR in image:
                continue
            figure = Path(figure_dir) / Path(image).name
            if not figure.is_file() or figure.stat().st_size == 0:
                raise ValueError(f"Missing manuscript figure: {figure.name}")
    write_analysis_manifest(Path(project_root))
