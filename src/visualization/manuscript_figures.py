"""Manuscript figure generation for the Ento-Linguistic project.

Importable figure-generation, analysis-pipeline, and data-export logic used by
the thin orchestrator ``scripts/02_generate_figures.py``. All business logic
lives here; the script only sets paths and delegates.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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

def load_real_corpus() -> List[str]:
    """Load real entomological corpus from data directory.
    
    Returns:
        List of abstract strings
    """
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
    for wipe_dir in (figure_dir, data_dir):
        if os.path.exists(wipe_dir):
            shutil.rmtree(wipe_dir)
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

    # Semantic entropy H(t) per domain — computed at runtime from term contexts
    from analysis.semantic_entropy import calculate_corpus_entropy
    context_dict: Dict[str, List[str]] = {
        t: list(getattr(term_obj, "contexts", []))
        for t, term_obj in terms.items()
    }
    entropy_results = calculate_corpus_entropy(context_dict)

    # Back-populate per-term semantic entropy on Term objects so downstream
    # figure generators (e.g. generate_power_labor_ambiguities) can read it.
    for t_name, t_obj in terms.items():
        if t_name in entropy_results:
            t_obj.semantic_entropy = entropy_results[t_name].entropy_bits

    semantic_entropy_map: Dict[str, float] = {}
    for _d in set(d for term_obj in terms.values() for d in getattr(term_obj, "domains", [])):
        _entropies = [
            entropy_results[t].entropy_bits
            for t, term_obj in terms.items()
            if _d in getattr(term_obj, "domains", []) and t in entropy_results
        ]
        semantic_entropy_map[_d] = float(np.mean(_entropies)) if _entropies else 0.0

    for domain_name, analysis in domain_analyses.items():
        if domain_name.startswith("_"):
            continue  # Skip cross-domain meta-analysis
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

    # Build co-occurrence relationships for the terminology network
    relationships: Dict[Tuple[str, str], float] = {}
    for (c1, c2), weight in concept_map.concept_relationships.items():
        relationships[(c1, c2)] = weight

    # Also build term-level co-occurrence from the extracted terms
    term_items = list(terms.items())
    for i, (t1_name, t1) in enumerate(term_items):
        for j in range(i + 1, min(i + 30, len(term_items))):
            t2_name, t2 = term_items[j]
            # Compute co-occurrence based on shared domains
            shared_domains = set(t1.domains) & set(t2.domains)
            if shared_domains:
                weight = len(shared_domains) / max(len(t1.domains), len(t2.domains), 1)
                if weight > 0.1:
                    relationships[(t1_name, t2_name)] = weight

    results["relationships"] = relationships

    return results


# ═══════════════════════════════════════════════════════════════════════
#  Figure Generation
# ═══════════════════════════════════════════════════════════════════════

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

    if filepath.exists():
        logger.info(f"  ✅ concept_map.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  concept_map.png was not saved")
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
        title="Ento-Linguistic Terminology Network:\nCo-occurrence and Domain Clustering",
    )
    # Save at 150 DPI (16x12 @ 300 DPI = 3.1MB; 150 DPI keeps quality under 1MB)
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    if filepath.exists():
        logger.info(f"  ✅ terminology_network.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  terminology_network.png was not saved")
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

    if filepath.exists():
        logger.info(f"  ✅ domain_comparison.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  domain_comparison.png was not saved")
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

    if filepath.exists():
        logger.info(f"  ✅ domain_overlap_heatmap.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  domain_overlap_heatmap.png was not saved (insufficient data)")
    return str(filepath)


def generate_anthropomorphic_analysis(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate anthropomorphic_framing.png showing human-derived terminology.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    filepath = Path(figure_dir) / "anthropomorphic_framing.png"

    # Curated anthropomorphic concepts organized by category
    anthropomorphic_data: Dict[str, List[str]] = {
        "Hierarchical Terms": [
            "queen", "king", "worker", "soldier", "slave",
            "master", "caste", "rank", "dominance", "subordinate",
        ],
        "Economic Metaphors": [
            "investment", "trade", "market", "efficiency",
            "resource allocation", "returns", "expenditure",
        ],
        "Kinship Language": [
            "mother", "sister", "daughter", "family",
            "kin", "altruism", "selflessness",
        ],
        "Identity Labels": [
            "forager", "nurse", "guard", "scout",
            "recruit", "specialist", "generalist",
        ],
        "Agency Attribution": [
            "decides", "chooses", "communicates", "signals",
            "cooperates", "competes", "sacrifices",
        ],
    }

    viz = ConceptVisualizer(figsize=(14, 10))
    viz.create_anthropomorphic_analysis_plot(
        anthropomorphic_data=anthropomorphic_data,
        filepath=filepath,
    )

    if filepath.exists():
        logger.info(f"  ✅ anthropomorphic_framing.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  anthropomorphic_framing.png was not saved")
    return str(filepath)


def generate_concept_hierarchy(results: Dict[str, Any], figure_dir: str) -> str:
    """Generate concept_hierarchy.png as a 2-panel centrality figure.

    Passes ``term_counts`` so the scatter panel has real y-axis values
    instead of all-1 defaults.

    Args:
        results: Analysis pipeline results
        figure_dir: Output directory for figures

    Returns:
        Path to generated figure
    """
    from visualization.concept_visualization import ConceptVisualizer

    concept_map = results["concept_map"]
    terms = results["terms"]
    filepath = Path(figure_dir) / "concept_hierarchy.png"

    # Build centrality from connection count
    centrality_scores = {}
    term_counts: Dict[str, int] = {}
    for concept_name in concept_map.concepts:
        connections = len(concept_map.get_connected_concepts(concept_name))
        centrality_scores[concept_name] = connections
        # Count terms mapped into this concept
        term_counts[concept_name] = len(concept_map.concepts[concept_name].terms)

    # Core = above-average centrality; peripheral = below
    core_concepts = []
    peripheral_concepts = []
    if centrality_scores:
        vals = list(centrality_scores.values())
        threshold = sum(vals) / len(vals)
        core_concepts = [c for c, s in centrality_scores.items() if s > threshold]
        peripheral_concepts = [c for c, s in centrality_scores.items() if s <= threshold]

    hierarchy_data = {
        "centrality_scores": centrality_scores,
        "core_concepts": core_concepts,
        "peripheral_concepts": peripheral_concepts,
        "term_counts": term_counts,
        "hierarchy_depth": 2,
    }

    viz = ConceptVisualizer(figsize=(18, 10))
    viz.visualize_concept_hierarchy(concept_hierarchy=hierarchy_data, filepath=filepath)

    if filepath.exists():
        logger.info(f"  ✅ concept_hierarchy.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  concept_hierarchy.png was not saved")
    return str(filepath)


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
    domain_analyses = results["domain_analyses"]
    domain = "unit_of_individuality"
    filepath = Path(figure_dir) / "unit_of_individuality_patterns.png"

    domain_terms = {
        name: t for name, t in terms.items() if domain in t.domains
    }

    if not domain_terms:
        logger.warning("  ⚠️  No terms found for unit_of_individuality domain")
        return ""

    # ── Left panel: term formation patterns ──
    analysis = domain_analyses.get(domain)
    if analysis and hasattr(analysis, "term_patterns") and analysis.term_patterns:
        patterns_data = analysis.term_patterns
    else:
        # Derive from POS tags in extracted terms
        patterns_data = {}
        for t in domain_terms.values():
            for tag in t.pos_tags:
                key = tag.title()
                patterns_data[key] = patterns_data.get(key, 0) + 1

    if not patterns_data:
        patterns_data = {"compound": 1}

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
        scale_counts[label] = max(count, 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    pie_colors = plt.cm.Set2(np.linspace(0, 1, max(len(pattern_labels), 1)))
    wedges, texts, autotexts = ax1.pie(
        pattern_sizes, labels=pattern_labels, colors=pie_colors,
        autopct="%1.1f%%", startangle=90, textprops={"fontsize": 11},
    )
    for at in autotexts:
        at.set_fontweight("bold")
    ax1.set_title("Term Formation Patterns", fontsize=13, fontweight="bold")

    # Bar chart
    scales = list(scale_counts.keys())
    counts = list(scale_counts.values())
    bar_colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(scales)))
    bars = ax2.bar(range(len(scales)), counts, color=bar_colors,
                   edgecolor="white", linewidth=0.5)
    for bar, c in zip(bars, counts):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                 str(c), ha="center", va="bottom", fontsize=10,
                 fontweight="bold")
    ax2.set_xticks(range(len(scales)))
    ax2.set_xticklabels(scales, fontsize=9)
    ax2.set_ylabel("Number of Terms", fontsize=11)
    ax2.set_title("Scale-Level Distribution", fontsize=13, fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle("Unit of Individuality — Terminology Patterns",
                 fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if filepath.exists():
        logger.info(f"  ✅ unit_of_individuality_patterns.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  unit_of_individuality_patterns.png was not saved")
    return str(filepath)


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
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(freq), ha="center", va="bottom", fontsize=10,
                fontweight="bold")

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=10)
    ax.set_ylabel("Frequency in Corpus", fontsize=12)
    ax.set_title("Term Frequency Distribution — Power & Labor",
                 fontsize=14, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if filepath.exists():
        logger.info(f"  ✅ power_and_labor_term_frequencies.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  power_and_labor_term_frequencies.png was not saved")
    return str(filepath)


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
                 fontsize=12, fontweight="bold")

    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names, fontsize=14)
    ax1.set_xlabel("Semantic Entropy H(t) (bits)", fontsize=14)
    ax1.set_title("Per-Term Entropy", fontsize=15, fontweight="bold")
    x_pad = max_ent * 0.25
    ax1.set_xlim(0, max_ent + x_pad)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.tick_params(axis='x', labelsize=12)
    ax1.invert_yaxis()

    med_ent = float(np.median(entropies))
    ax1.axvline(med_ent, color="#888", linestyle="--", linewidth=1, alpha=0.6)
    ax1.text(med_ent, len(names) - 0.3, f"median {med_ent:.2f}",
             fontsize=10, color="#555", ha="center")

    # ── Right panel: frequency vs entropy scatter ────────────────────
    sc_sizes = [max(40, c * 8) for c in n_ctx]
    scatter = ax2.scatter(freqs, entropies, s=sc_sizes, c=entropies,
                          cmap="Purples", edgecolors="#333", linewidths=0.5,
                          alpha=0.85, vmin=0, vmax=max_ent)
    for name, f, e in zip(names, freqs, entropies):
        ax2.annotate(name, (f, e), xytext=(4, 3), textcoords="offset points",
                     fontsize=9, color="#333")

    ax2.set_xlabel("Corpus Frequency", fontsize=14)
    ax2.set_ylabel("Semantic Entropy H(t) (bits)", fontsize=14)
    ax2.set_title("Frequency vs Entropy", fontsize=15, fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(labelsize=12)
    fig.colorbar(scatter, ax=ax2, label="H(t) bits", shrink=0.75)

    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if filepath.exists():
        logger.info(f"  ✅ power_and_labor_ambiguities.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  power_and_labor_ambiguities.png was not saved")
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

    if filepath.exists():
        logger.info(f"  ✅ domain_overview_grid.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  domain_overview_grid.png was not saved")
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

    if filepath.exists():
        logger.info(f"  ✅ domain_patterns_grid.png ({filepath.stat().st_size / 1024:.1f} KB)")
    else:
        logger.warning("  ⚠️  domain_patterns_grid.png was not saved")
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

    # Save domain statistics
    from analysis.cace_scoring import ANTHROPOMORPHIC_TERMS as _ANTHROPO_TERMS

    def _term_is_anthropomorphic(t_text: str) -> bool:
        words = set(t_text.lower().replace("-", " ").replace("_", " ").split())
        return bool(words & _ANTHROPO_TERMS)

    domain_stats = {}
    for domain_name, data in results["domain_data"].items():
        # Compute anthropomorphic proportion for this domain
        domain_term_set = [
            t_text for t_text, t_obj in results["terms"].items()
            if domain_name in getattr(t_obj, "domains", [])
        ]
        n_anthropo = sum(1 for t in domain_term_set if _term_is_anthropomorphic(t))
        anthro_proportion = round(n_anthropo / len(domain_term_set), 4) if domain_term_set else 0.0

        # Count high-entropy terms (H > 2.0 bits) for this domain
        n_high_entropy = sum(
            1 for t in domain_term_set
            if t in results["terms"]
            and getattr(results["terms"][t], "semantic_entropy", 0.0) > 2.0
        )
        n_domain = len(domain_term_set)
        high_entropy_pct = round(100 * n_high_entropy / n_domain, 1) if n_domain else 0.0

        domain_stats[domain_name] = {
            "term_count": data["term_count"],
            "avg_confidence": float(data["avg_confidence"]),
            "total_frequency": data["total_frequency"],
            "bridging_term_count": len(data["bridging_terms"]),
            "bridging_terms": list(data["bridging_terms"]),
            "semantic_entropy": float(data.get("semantic_entropy", 0.0)),
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
    for _t_name in results["terms"]:
        _G.add_node(_t_name)
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
                "caption": "Ento-Linguistic Concept Map",
                "section": "introduction",
            },
            "terminology_network.png": {
                "label": "fig:terminology_network",
                "caption": "Terminology Network with Domain Clustering",
                "section": "experimental_results",
            },
            "domain_comparison.png": {
                "label": "fig:domain_comparison",
                "caption": "Cross-Domain Terminology Comparison",
                "section": "experimental_results",
            },
            "domain_overlap_heatmap.png": {
                "label": "fig:domain_overlap",
                "caption": "Domain Term Overlap Heatmap",
                "section": "experimental_results",
            },
            "anthropomorphic_framing.png": {
                "label": "fig:anthropomorphic",
                "caption": "Anthropomorphic Framing Analysis",
                "section": "discussion",
            },
            "concept_hierarchy.png": {
                "label": "fig:concept_hierarchy",
                "caption": "Conceptual Hierarchy Analysis",
                "section": "discussion",
            },
            "unit_of_individuality_patterns.png": {
                "label": "fig:unit_individuality_patterns",
                "caption": "Unit of Individuality Terminology Patterns",
                "section": "experimental_results",
            },
            "unit_of_individuality_term_frequencies.png": {
                "label": "fig:unit_individuality_frequencies",
                "caption": "Unit of Individuality Term Frequencies",
                "section": "experimental_results",
            },
            "unit_of_individuality_ambiguities.png": {
                "label": "fig:unit_individuality_ambiguities",
                "caption": "Unit of Individuality Ambiguity Analysis",
                "section": "experimental_results",
            },
            "power_and_labor_term_frequencies.png": {
                "label": "fig:power_labor_frequencies",
                "caption": "Power & Labor Term Frequencies",
                "section": "experimental_results",
            },
            "power_and_labor_ambiguities.png": {
                "label": "fig:power_labor_ambiguities",
                "caption": "Power & Labor Ambiguity Analysis",
                "section": "experimental_results",
            },
            "domain_overview_grid.png": {
                "label": "fig:domain_overview_grid",
                "caption": "Domain Terminology Overview: Top Terms by Frequency & Semantic Entropy",
                "section": "experimental_results",
            },
            "domain_patterns_grid.png": {
                "label": "fig:domain_patterns_grid",
                "caption": "Domain POS-Composition Patterns: Vocabulary Structure by Domain",
                "section": "experimental_results",
            },
        }

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
            d_title = domain.replace("_", " ").title()
            
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
            if filename in figure_metadata:
                meta = figure_metadata[filename]
                fm.register_figure(
                    filename=filename,
                    caption=meta["caption"],
                    label=meta["label"],
                    section=meta["section"],
                )
                registered += 1

        logger.info(f"✅ Registered {registered} figures with FigureManager")

    except ImportError:
        logger.warning("⚠️  FigureManager not available, skipping registration")
    except Exception as e:
        logger.warning(f"⚠️  Could not register figures: {e}")


# ═══════════════════════════════════════════════════════════════════════
#  Main Entry Point
# ═══════════════════════════════════════════════════════════════════════

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
    output_dir, data_dir, figure_dir = _setup_directories(project_root)

    logger.info("=" * 70)
    logger.info("  Ento-Linguistic Research Figure Generation Pipeline")
    logger.info("=" * 70)
    logger.info(f"  Output: {output_dir}")
    logger.info(f"  Corpus: {len(REAL_ABSTRACTS)} real abstracts")
    logger.info("")

    # ── Run analysis pipeline ─────────────────────────────────────────
    logger.info("▶ Running analysis pipeline...")
    results = run_analysis_pipeline(REAL_ABSTRACTS)
    logger.info("")

    # ── Generate figures ──────────────────────────────────────────────
    logger.info("▶ Generating figures...")
    figures = []

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
        from core.manuscript_variables import build_variable_map, fill_manuscript
        logger.info("▶ Filling manuscript template variables...")
        variables = build_variable_map(
            output_data_dir=Path(project_root) / "output" / "data",
            corpus_dir=Path(project_root) / "data" / "corpus",
        )
        results_fill = fill_manuscript(
            variables, manuscript_dir=Path(project_root) / "docs" / "manuscript"
        )
        total_subs = sum(results_fill.values())
        logger.info(f"  ✅ {total_subs} substitutions across {len(results_fill)} files")
    except Exception as exc:
        logger.warning(f"⚠️  Manuscript variable fill warning: {exc}")

    # ── Validation (if infrastructure available) ──────────────────────
    if INFRASTRUCTURE_AVAILABLE and validate_figure_registry:
        try:
            registry_path = Path(figure_dir) / "figure_registry.json"
            manuscript_dir = Path(project_root) / "docs" / "manuscript"
            validate_figure_registry(registry_path, manuscript_dir)
            logger.info("✅ Figure registry validation passed")
        except Exception as exc:
            logger.warning(f"⚠️  Figure registry validation warning: {exc}")

    if INFRASTRUCTURE_AVAILABLE and verify_output_integrity:
        try:
            verify_output_integrity(Path(output_dir))
            logger.info("✅ Output integrity check passed")
        except Exception as exc:
            logger.warning(f"⚠️  Output integrity warning: {exc}")
