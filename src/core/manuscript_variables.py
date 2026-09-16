"""Manuscript template-variable mapping and substitution.

Importable logic used by the thin orchestrator
``scripts/_fill_manuscript_variables.py``: builds a ``{{VAR}}`` → value map
from pipeline JSON outputs and substitutes it into the manuscript markdown.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
MANUSCRIPT_DIR = PROJECT_DIR / "docs" / "manuscript"
OUTPUT_DATA_DIR = PROJECT_DIR / "output" / "data"
CORPUS_DIR = PROJECT_DIR / "data" / "corpus"

def load_json(path: Path) -> dict:
    """Load a JSON file, returning empty dict if missing."""
    if not path.exists():
        print(f"  WARNING: {path} not found, skipping")
        return {}
    with open(path) as f:
        return json.load(f)


def count_publications(corpus_dir: Path) -> int:
    """Count publications in the corpus."""
    abstracts_path = corpus_dir / "abstracts.json"
    if not abstracts_path.exists():
        return 0
    with open(abstracts_path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and "abstracts" in data:
        return len(data["abstracts"])
    return 0

def _fmt_stat(value) -> str:
    """Format a numeric statistic with 4 decimals.

    Args:
        value: Numeric value or None when the statistic was not computed.

    Returns:
        Formatted string; empty string when the value is missing so that
        absent data never renders as a fabricated 0.0000.
    """
    if value is None:
        return ""
    return f"{float(value):.4f}"


def _fmt_p(value) -> str:
    """Format a p-value with 4 decimals or the ``<0.0001`` reporting floor.

    Args:
        value: P-value or None when not computed.

    Returns:
        ``"<0.0001"`` for values below the 4-decimal reporting floor
        (including exact 0.0), otherwise the 4-decimal rendering.
    """
    if value is None:
        return ""
    p = float(value)
    if p < 1e-4:
        return "<0.0001"
    return f"{p:.4f}"

def _fmt_cace(value) -> str:
    """Format a CACE dimension score with 2 decimals.

    CACE scores are reported in manuscript tables at 2-decimal precision.

    Args:
        value: Numeric score or None when not computed.

    Returns:
        Formatted string; empty string when the value is missing so that
        absent data never renders as a fabricated 0.00.
    """
    if value is None:
        return ""
    return f"{float(value):.2f}"


def build_variable_map(
    output_data_dir: Path | None = None,
    corpus_dir: Path | None = None,
) -> dict[str, str]:
    """Build the complete variable map from pipeline outputs.

    Reads the pipeline JSON artifacts from ``output_data_dir`` (including
    the optional ``statistical_analysis.json``; when that artifact is
    absent the ANOVA/pairwise tokens are simply not emitted, never a
    KeyError) and maps them onto ``{{...}}`` manuscript tokens.

    Args:
        output_data_dir: Directory containing pipeline JSON outputs.
            Defaults to the project's ``output/data``.
        corpus_dir: Directory containing the raw corpus. Defaults to the
            project's ``data/corpus``.
    """
    if output_data_dir is None:
        output_data_dir = OUTPUT_DATA_DIR
    if corpus_dir is None:
        corpus_dir = CORPUS_DIR
    corpus_stats = load_json(output_data_dir / "corpus_statistics.json")
    domain_stats = load_json(output_data_dir / "domain_statistics.json")
    concept_map = load_json(output_data_dir / "concept_map_summary.json")
    extracted_terms = load_json(output_data_dir / "extracted_terms.json")

    # Count publications
    num_publications = count_publications(corpus_dir)

    # Count candidate terms and domain-assigned terms
    num_candidate_terms = len(extracted_terms)
    domain_assigned = {
        k: v
        for k, v in extracted_terms.items()
        if v.get("domains") and len(v["domains"]) > 0
    }
    num_domain_terms = len(domain_assigned)

    # Multi-domain terms (context-dependent drift)
    multi_domain = {
        k: v for k, v in domain_assigned.items() if len(v.get("domains", [])) > 1
    }
    drift_pct = (
        f"{100 * len(multi_domain) / max(1, len(domain_assigned)):.1f}"
        if domain_assigned
        else "0.0"
    )

    # Top terms from corpus_stats
    top_tokens = corpus_stats.get("most_common_tokens", [])
    ttr = corpus_stats.get("type_token_ratio", 0)

    variables: dict[str, str] = {}

    # --- Corpus-level variables ---
    variables["CORPUS_PUBLICATIONS"] = str(num_publications)
    variables["CORPUS_TOTAL_TOKENS"] = str(corpus_stats.get("total_tokens", 0))
    variables["CORPUS_UNIQUE_TOKENS"] = str(corpus_stats.get("unique_tokens", 0))
    variables["CORPUS_TTR"] = f"{ttr:.4f}"
    variables["CORPUS_CANDIDATE_TERMS"] = str(num_candidate_terms)
    variables["CORPUS_DOMAIN_TERMS"] = str(num_domain_terms)
    variables["CORPUS_DRIFT_PERCENTAGE"] = drift_pct

    # Concept map variables
    variables["CORPUS_CONCEPT_COUNT"] = str(concept_map.get("n_concepts", 0))
    variables["CORPUS_RELATIONSHIP_COUNT"] = str(concept_map.get("n_relationships", 0))

    # Network variables
    variables["NETWORK_NODES"] = str(concept_map.get("network_nodes", 0))
    variables["NETWORK_EDGES"] = str(concept_map.get("network_edges", 0))
    variables["NETWORK_CLUSTERING"] = str(concept_map.get("network_clustering", 0))
    variables["NETWORK_AVG_DEGREE"] = str(concept_map.get("network_avg_degree", 0))

    # Top terms (corpus-level)
    for i, (token, freq) in enumerate(top_tokens[:5], start=1):
        variables[f"CORPUS_TOP_TERM_{i}"] = token
        variables[f"CORPUS_TOP_FREQ_{i}"] = str(freq)

    # --- Domain-level variables ---
    domain_key_map = {
        "POWER_AND_LABOR": "power_and_labor",
        "UNIT_OF_INDIVIDUALITY": "unit_of_individuality",
        "SEX_AND_REPRODUCTION": "sex_and_reproduction",
        "BEHAVIOR_AND_IDENTITY": "behavior_and_identity",
        "KIN_AND_RELATEDNESS": "kin_and_relatedness",
        "ECONOMICS": "economics",
    }

    for var_prefix, json_key in domain_key_map.items():
        domain = domain_stats.get(json_key, {})
        variables[f"DOMAIN_{var_prefix}_TERMS"] = str(domain.get("term_count", 0))
        variables[f"DOMAIN_{var_prefix}_N_TERMS"] = str(domain.get("term_count", 0))
        variables[f"DOMAIN_{var_prefix}_FREQ"] = str(domain.get("total_frequency", 0))
        variables[f"DOMAIN_{var_prefix}_BRIDGING"] = str(
            domain.get("bridging_term_count", 0)
        )
        variables[f"DOMAIN_{var_prefix}_ENTROPY"] = (
            f"{domain.get('semantic_entropy', 0):.2f}"
        )
        anthropomorphic_pct = domain.get("anthropomorphic_proportion", 0) * 100
        variables[f"DOMAIN_{var_prefix}_ANTHROPOMORPHIC_PROPORTION_PCT"] = (
            f"{anthropomorphic_pct:.1f}"
        )
        variables[f"DOMAIN_{var_prefix}_HIGH_ENTROPY_PCT"] = (
            f"{domain.get('high_entropy_pct', 0.0):.1f}"
        )

    # --- Corpus-level entropy aggregates ---
    all_entropies = [
        d.get("semantic_entropy", 0) for d in domain_stats.values()
    ]
    all_term_counts = [d.get("term_count", 0) for d in domain_stats.values()]
    if all_entropies and all_term_counts and sum(all_term_counts) > 0:
        weighted_entropy = sum(
            e * n for e, n in zip(all_entropies, all_term_counts)
        ) / sum(all_term_counts)
        variables["CORPUS_OVERALL_ENTROPY"] = f"{weighted_entropy:.2f}"
    else:
        variables["CORPUS_OVERALL_ENTROPY"] = "0.00"

    all_high_counts = [d.get("high_entropy_count", 0) for d in domain_stats.values()]
    total_domain_terms = sum(all_term_counts)
    total_high = sum(all_high_counts)
    if total_domain_terms > 0:
        variables["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] = (
            f"{100 * total_high / total_domain_terms:.1f}"
        )
    else:
        variables["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] = "0.0"

    # Per-domain entropy-table N: sum of the per-domain term counts, so the
    # S02 Overall row is the exact total of the rows above it.
    variables["CORPUS_OVERALL_N_TERMS"] = str(sum(all_term_counts))

    # --- Concept-level variables ---
    concepts = concept_map.get("concepts", {})
    concept_key_map = {
        "BIOLOGICAL_INDIVIDUALITY": "biological_individuality",
        "SOCIAL_ORGANIZATION": "social_organization",
        "REPRODUCTIVE_BIOLOGY": "reproductive_biology",
        "KINSHIP_SYSTEMS": "kinship_systems",
        "RESOURCE_ECONOMICS": "resource_economics",
        "BEHAVIORAL_ECOLOGY": "behavioral_ecology",
    }

    for var_suffix, json_key in concept_key_map.items():
        concept = concepts.get(json_key, {})
        variables[f"CONCEPT_{var_suffix}_TERMS"] = str(concept.get("n_terms", 0))

    # --- Specific term frequencies ---
    term_freq_map = {
        "TERM_FREQ_QUEEN": "queen",
        "TERM_FREQ_WORKER": "worker",
        "TERM_FREQ_CASTE": "caste",
        "TERM_FREQ_ALLOCATION": "allocation",
        "TERM_FREQ_INVESTMENT": "investment",
        "TERM_FREQ_RESOURCES": "resources",
        "TERM_FREQ_RESOURCE": "resource",
    }

    for var_name, term_key in term_freq_map.items():
        term_data = extracted_terms.get(term_key, {})
        variables[var_name] = str(term_data.get("frequency", 0))
    variables.update(
        build_statistical_tokens(
            load_json(output_data_dir / "statistical_analysis.json")
        )
    )
    return variables


def build_statistical_tokens(stats_artifact: dict) -> dict:
    """Map the statistical-analysis artifact onto inferential template tokens.

    Emits ANOVA_*, CORRECTION_METHOD, PAIRWISE_N_COMPARISONS,
    PAIRWISE_<SLUG_A>_<SLUG_B>_{T,P,P_BH,D,SIGNIFICANT} (SLUG = canonical
    domain slug uppercased, A < B alphabetical), the per-domain CACE
    aggregates CACE_<SLUG>_{MEAN,MIN,MAX,CLARITY,APPROPRIATENESS,CONSISTENCY,
    EVOLVABILITY,N}, and the per-term CACE evaluations
    CACE_TERM_<SLUG>_{CLARITY,APPROPRIATENESS,CONSISTENCY,EVOLVABILITY,
    AGGREGATE} (SLUG = term uppercased, spaces/hyphens mapped to
    underscores).  Shared by :func:`build_variable_map` and the PDF
    renderer so both substitution paths resolve the identical token set.

    Args:
        stats_artifact: Parsed ``statistical_analysis.json`` contents.

    Returns:
        Mapping of token names to formatted string values.
    """
    variables: dict = {}
    if not stats_artifact:
        return variables
    anova = stats_artifact.get("anova") or {}
    if anova:
        variables["ANOVA_METRIC"] = str(anova.get("metric", ""))
        variables["ANOVA_F"] = _fmt_stat(anova.get("F"))
        variables["ANOVA_DF1"] = _fmt_stat(anova.get("df1"))
        variables["ANOVA_DF2"] = _fmt_stat(anova.get("df2"))
        variables["ANOVA_P"] = _fmt_p(anova.get("p"))
        variables["ANOVA_ETA_SQUARED"] = _fmt_stat(anova.get("eta_squared"))

    corrections = stats_artifact.get("corrections") or {}
    if corrections:
        variables["PAIRWISE_N_COMPARISONS"] = str(
            corrections.get("n_comparisons", 0)
        )
        variables["CORRECTION_METHOD"] = str(corrections.get("method", ""))

    # Pairwise tokens: PAIRWISE_<SLUG_A>_<SLUG_B>_{T,P,P_BH,D,SIGNIFICANT}
    # with SLUG = canonical domain slug uppercased and A < B alphabetical
    # (the artifact emits pairs in that order).
    for pair in stats_artifact.get("pairwise") or []:
        slug_a = str(pair.get("domain_a", "")).upper()
        slug_b = str(pair.get("domain_b", "")).upper()
        prefix = f"PAIRWISE_{slug_a}_{slug_b}"
        variables[f"{prefix}_T"] = _fmt_stat(pair.get("t"))
        variables[f"{prefix}_P"] = _fmt_p(pair.get("p"))
        variables[f"{prefix}_P_BH"] = _fmt_p(pair.get("p_bh"))
        variables[f"{prefix}_D"] = _fmt_stat(pair.get("cohens_d"))
        variables[f"{prefix}_SIGNIFICANT"] = (
            "yes" if pair.get("significant_bh") else "no"
        )

    # Per-domain CACE aggregate tokens.  Domains with no sampled CACE
    # terms are absent from the ``cace`` section and emit no tokens.
    for domain, entry in (stats_artifact.get("cace") or {}).items():
        slug = str(domain).upper()
        variables[f"CACE_{slug}_MEAN"] = _fmt_cace(entry.get("mean"))
        variables[f"CACE_{slug}_MIN"] = _fmt_cace(entry.get("min"))
        variables[f"CACE_{slug}_MAX"] = _fmt_cace(entry.get("max"))
        variables[f"CACE_{slug}_CLARITY"] = _fmt_cace(entry.get("clarity"))
        variables[f"CACE_{slug}_APPROPRIATENESS"] = _fmt_cace(
            entry.get("appropriateness")
        )
        variables[f"CACE_{slug}_CONSISTENCY"] = _fmt_cace(entry.get("consistency"))
        variables[f"CACE_{slug}_EVOLVABILITY"] = _fmt_cace(entry.get("evolvability"))
        variables[f"CACE_{slug}_N"] = str(entry.get("n_terms", 0))

    # Per-term CACE tokens for the representative-term supplement table.
    for term, entry in (stats_artifact.get("cace_terms") or {}).items():
        slug = str(term).upper().replace("-", "_").replace(" ", "_")
        variables[f"CACE_TERM_{slug}_CLARITY"] = _fmt_cace(entry.get("clarity"))
        variables[f"CACE_TERM_{slug}_APPROPRIATENESS"] = _fmt_cace(
            entry.get("appropriateness")
        )
        variables[f"CACE_TERM_{slug}_CONSISTENCY"] = _fmt_cace(
            entry.get("consistency")
        )
        variables[f"CACE_TERM_{slug}_EVOLVABILITY"] = _fmt_cace(
            entry.get("evolvability")
        )
        variables[f"CACE_TERM_{slug}_AGGREGATE"] = _fmt_cace(entry.get("aggregate"))
    return variables




def fill_manuscript(
    variables: dict[str, str],
    dry_run: bool = False,
    manuscript_dir: Path | None = None,
) -> dict[str, int]:
    """Substitute {{VAR}} placeholders in all manuscript .md files.

    Args:
        variables: Mapping of variable names to values.
        dry_run: If True, report substitutions without writing.

    Returns:
        Dict mapping filename to number of substitutions made.
    """
    results: dict[str, int] = {}
    pattern = re.compile(r"\{\{([A-Z_0-9]+)\}\}")

    if manuscript_dir is None:
        manuscript_dir = MANUSCRIPT_DIR
    md_files = sorted(manuscript_dir.glob("*.md"))
    if not md_files:
        print("  WARNING: No .md files found in docs/manuscript/")
        return results

    for md_path in md_files:
        content = md_path.read_text(encoding="utf-8")
        count = 0

        def replacer(match: re.Match) -> str:
            nonlocal count
            var_name = match.group(1)
            if var_name in variables:
                count += 1
                return variables[var_name]
            print(f"  WARNING: Unknown variable {{{{{var_name}}}}} in {md_path.name}")
            return match.group(0)  # Leave unknown variables unchanged

        new_content = pattern.sub(replacer, content)

        if count > 0:
            if not dry_run:
                md_path.write_text(new_content, encoding="utf-8")
            results[md_path.name] = count

    return results
def main() -> None:
    """Fill manuscript template variables from pipeline outputs."""
    print("=" * 60)
    print("FILLING MANUSCRIPT TEMPLATE VARIABLES")
    print("=" * 60)

    # Check required files exist
    required = [
        OUTPUT_DATA_DIR / "corpus_statistics.json",
        OUTPUT_DATA_DIR / "domain_statistics.json",
        OUTPUT_DATA_DIR / "concept_map_summary.json",
        OUTPUT_DATA_DIR / "extracted_terms.json",
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("\nERROR: Missing required data files:")
        for p in missing:
            print(f"  - {p}")
        print("\nRun the analysis pipeline first (02_generate_figures.py)")
        raise SystemExit(1)

    # Build variable map
    print(f"\nLoading data from {OUTPUT_DATA_DIR}/")
    variables = build_variable_map()
    print(f"  Built {len(variables)} variable mappings")

    # Fill manuscripts
    print(f"\nSubstituting variables in {MANUSCRIPT_DIR}/")
    results = fill_manuscript(variables)

    total = sum(results.values())
    print("\nResults:")
    for filename, count in sorted(results.items()):
        print(f"  {filename}: {count} substitutions")
    print(f"\n  TOTAL: {total} substitutions across {len(results)} files")

    # Verify no remaining placeholders
    remaining = 0
    for md_path in sorted(MANUSCRIPT_DIR.glob("*.md")):
        content = md_path.read_text(encoding="utf-8")
        matches = re.findall(r"\{\{[A-Z_]+\}\}", content)
        if matches:
            remaining += len(matches)
            print(f"\n  WARNING: {len(matches)} unfilled in {md_path.name}:")
            for m in sorted(set(matches)):
                print(f"    - {m}")

    if remaining == 0:
        print("\n  All template variables successfully filled.")
    else:
        print(f"\n  WARNING: {remaining} template variables remain unfilled.")

    print("=" * 60)
