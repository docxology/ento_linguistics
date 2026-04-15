#!/usr/bin/env python3
"""Fill manuscript template variables from pipeline JSON outputs.

Reads corpus_statistics.json, domain_statistics.json, concept_map_summary.json,
and extracted_terms.json, then substitutes all {{VAR}} placeholders in
manuscript/*.md files.

This script is a thin orchestrator: it reads data, builds a variable map,
and performs string substitution. No business logic.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
MANUSCRIPT_DIR = PROJECT_DIR / "manuscript"
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


def build_variable_map() -> dict[str, str]:
    """Build the complete variable map from pipeline outputs."""
    corpus_stats = load_json(OUTPUT_DATA_DIR / "corpus_statistics.json")
    domain_stats = load_json(OUTPUT_DATA_DIR / "domain_statistics.json")
    concept_map = load_json(OUTPUT_DATA_DIR / "concept_map_summary.json")
    extracted_terms = load_json(OUTPUT_DATA_DIR / "extracted_terms.json")

    # Count publications
    num_publications = count_publications(CORPUS_DIR)

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

    return variables


def fill_manuscript(variables: dict[str, str], dry_run: bool = False) -> dict[str, int]:
    """Substitute {{VAR}} placeholders in all manuscript .md files.

    Args:
        variables: Mapping of variable names to values.
        dry_run: If True, report substitutions without writing.

    Returns:
        Dict mapping filename to number of substitutions made.
    """
    results: dict[str, int] = {}
    pattern = re.compile(r"\{\{([A-Z_0-9]+)\}\}")

    md_files = sorted(MANUSCRIPT_DIR.glob("*.md"))
    if not md_files:
        print("  WARNING: No .md files found in manuscript/")
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
        print(f"\nERROR: Missing required data files:")
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
    print(f"\nResults:")
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


if __name__ == "__main__":
    main()
