"""Manuscript template-variable mapping and substitution.

Importable logic used by the thin orchestrator
``scripts/_fill_manuscript_variables.py``: builds a ``{{VAR}}`` → value map
from pipeline JSON outputs and substitutes it into the manuscript markdown.
"""
from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Optional

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
            load_json(output_data_dir / "statistical_analysis.json"),
            load_json(output_data_dir / "fulltext_analysis.json"),
        )
    )
    return variables


def build_statistical_tokens(
    stats_artifact: dict,
    fulltext_artifact: Optional[dict] = None,
    bhl_data_dir: Optional[Path] = None,
) -> dict:
    """Map the statistical-analysis artifact onto inferential template tokens.

    Emits ANOVA_*, CORRECTION_METHOD, PAIRWISE_N_COMPARISONS,
    PAIRWISE_<SLUG_A>_<SLUG_B>_{T,P,P_BH,D,SIGNIFICANT} (SLUG = canonical
    domain slug uppercased, A < B alphabetical), the abstract layer's
    ABSTRACT_* discourse tokens (see :func:`_build_discourse_tokens`),
    the per-domain CACE
    aggregates CACE_<SLUG>_{MEAN,MIN,MAX,CLARITY,APPROPRIATENESS,CONSISTENCY,
    EVOLVABILITY,N}, and the per-term CACE evaluations
    CACE_TERM_<SLUG>_{CLARITY,APPROPRIATENESS,CONSISTENCY,EVOLVABILITY,
    AGGREGATE} (SLUG = term uppercased, spaces/hyphens mapped to
    underscores).  Shared by :func:`build_variable_map` and the PDF
    renderer so both substitution paths resolve the identical token set.

    When the parallel full-text layer artifact is available, the additional
    FULLTEXT_* token family is emitted (see :func:`_build_fulltext_tokens`).
    When the BHL historical-layer artifact is available
    (``<bhl_data_dir>/era_term_usage.json``, default
    ``BHL_DATA_DIR``), the BHL_* token family is emitted (see
    :func:`_build_bhl_tokens`).

    Args:
        stats_artifact: Parsed ``statistical_analysis.json`` contents.
        fulltext_artifact: Parsed ``fulltext_analysis.json`` contents, or
            ``None`` to load it from the default output-data location
            (missing file resolves to no FULLTEXT_* tokens, never KeyError).
        bhl_data_dir: Directory holding the BHL historical layer
            (``era_term_usage.json``); ``None`` defaults to
            :data:`BHL_DATA_DIR` (the project ``data/bhl``).

    Returns:
        Mapping of token names to formatted string values.
    """
    variables: dict = {}
    variables.update(_build_fulltext_tokens(fulltext_artifact))
    variables.update(_build_bhl_tokens(_load_bhl_artifact(bhl_data_dir)))
    if not stats_artifact:
        return variables
    # Abstract-layer discourse tokens (FULLTEXT_* twins are emitted
    # inside _build_fulltext_tokens from the same shared builder).
    variables.update(_build_discourse_tokens(stats_artifact, "ABSTRACT"))
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


def _build_fulltext_tokens(fulltext_artifact: Optional[dict]) -> dict:
    """Map the full-text-layer artifact onto the FULLTEXT_* token family.

    Emits (all omitted when the artifact is absent/empty, never KeyError):

    - ``FULLTEXT_DOCUMENTS``: number of analyzed full texts.
    - ``FULLTEXT_TOTAL_TOKENS`` / ``FULLTEXT_MEDIAN_TOKENS``: corpus token
      volume and per-document median token count.
    - ``FULLTEXT_DOMAIN_<SLUG>_TERMS`` / ``FULLTEXT_DOMAIN_<SLUG>_ENTROPY``:
      per-domain extracted-term count and mean semantic entropy from the
      artifact's ``descriptives`` section (SLUG = canonical domain slug
      uppercased).
    - ``FULLTEXT_PAIRWISE_N``: number of pairwise comparisons.
    - The FULLTEXT_* discourse-token family (see
      :func:`_build_discourse_tokens`), emitted from the artifact's
      ``discourse`` section when present.
    - ``FULLTEXT_DOMAIN_<SLUG>_ANTHROPOMORPHIC`` /
      ``FULLTEXT_ANTHROPOMORPHIC_OVERALL``: per-domain and overall
      anthropomorphic-framing proportions from the artifact's
      ``framing`` section (4-decimal; omitted when the artifact carries
      no ``framing`` section).
    - ``FULLTEXT_PAIRWISE_N``: number of pairwise comparisons.
    - ``FULLTEXT_ANOVA_F`` / ``FULLTEXT_ANOVA_P``: omnibus ANOVA statistic
      and p-value (formatted with the shared ``_fmt_stat``/``_fmt_p``
      helpers).

    Args:
        fulltext_artifact: Parsed ``fulltext_analysis.json`` contents, or
            ``None`` to load from ``OUTPUT_DATA_DIR/fulltext_analysis.json``.

    Returns:
        Mapping of FULLTEXT_* token names to formatted string values.
    """
    if fulltext_artifact is None:
        fulltext_artifact = load_json(OUTPUT_DATA_DIR / "fulltext_analysis.json")
    variables: dict = {}
    variables.update(_build_discourse_tokens(fulltext_artifact, "FULLTEXT"))
    if not fulltext_artifact:
        return variables
    variables["FULLTEXT_DOCUMENTS"] = str(fulltext_artifact.get("n_documents", 0))
    token_counts = [
        int(doc.get("token_count", 0))
        for doc in fulltext_artifact.get("documents") or []
    ]
    if token_counts:
        variables["FULLTEXT_TOTAL_TOKENS"] = str(sum(token_counts))
        variables["FULLTEXT_MEDIAN_TOKENS"] = _fmt_stat(statistics.median(token_counts))
    for domain, entry in (fulltext_artifact.get("descriptives") or {}).items():
        slug = str(domain).upper()
        variables[f"FULLTEXT_DOMAIN_{slug}_TERMS"] = str(entry.get("n_terms", 0))
        variables[f"FULLTEXT_DOMAIN_{slug}_ENTROPY"] = _fmt_stat(
            entry.get("entropy_mean")
        )
    for domain, entry in (fulltext_artifact.get("framing") or {}).items():
        if domain == "overall":
            continue
        variables[f"FULLTEXT_DOMAIN_{str(domain).upper()}_ANTHROPOMORPHIC"] = (
            _fmt_stat(entry.get("proportion"))
        )
    overall = (fulltext_artifact.get("framing") or {}).get("overall")
    if overall:
        variables["FULLTEXT_ANTHROPOMORPHIC_OVERALL"] = _fmt_stat(
            overall.get("proportion")
        )
    variables["FULLTEXT_PAIRWISE_N"] = str(
        len(fulltext_artifact.get("pairwise") or [])
    )
    anova = fulltext_artifact.get("anova") or {}
    if anova:
        variables["FULLTEXT_ANOVA_F"] = _fmt_stat(anova.get("F"))
        variables["FULLTEXT_ANOVA_P"] = _fmt_p(anova.get("p"))
    return variables


#: Canonical key ordering for the discourse-section token emission:
#: canonical members first (fixed manuscript order), then any extras
#: lexicographically.  Deterministic regardless of JSON key order.
_DISCOURSE_CANONICAL_ORDER: dict[str, tuple[str, ...]] = {
    "patterns": (
        "anthropomorphic_framing",
        "economic_metaphors",
        "hierarchical_framing",
        "scale_ambiguity",
    ),
    "rhetorical": (
        "analogy",
        "anecdotal",
        "authority",
        "generalization",
    ),
    "persuasive": (
        "authoritative_citations",
        "metaphorical_language",
        "quantitative_emphasis",
        "rhetorical_questions",
    ),
}


def _discourse_order(section: str, keys: dict) -> list[str]:
    """Order discourse-section keys canonically first, extras sorted."""
    canonical = _DISCOURSE_CANONICAL_ORDER.get(section, ())
    return [k for k in canonical if k in keys] + sorted(
        k for k in keys if k not in canonical
    )


def _build_discourse_tokens(artifact: Optional[dict], prefix: str) -> dict:
    """Map a layer artifact's ``discourse`` section onto a token family.

    Bounded, documented emission (all omitted when the artifact or its
    ``discourse`` section is absent/empty, never KeyError):

    - ``<PREFIX>_DISCOURSE_N_ANALYZED``: ``n_texts_analyzed`` (the
      corpus texts that entered the discourse pass after the
      ``min_text_length`` filter).
    - ``<PREFIX>_DISCOURSE_SAMPLE_FRACTION``: ``sample_fraction`` (4
      decimals; 1.0 = full corpus, 0.2 = the full-text layer's
      deterministic 20% sample).
    - ``<PREFIX>_PATTERNS_<SLUG>``: per-pattern ``frequency`` for every
      key the section carries (e.g. ``PATTERNS_HIERARCHICAL_FRAMING``).
    - ``<PREFIX>_RHETORICAL_<SLUG>``: per-strategy ``frequency`` for
      every key the section carries (e.g. ``RHETORICAL_AUTHORITY``).
    - ``<PREFIX>_ARG_STRUCTURES``: ``argumentative.n_structures``.
    - ``<PREFIX>_PERSUASIVE_METAPHORICAL``:
      ``persuasive.metaphorical_language.usage_frequency``.

    Args:
        artifact: Parsed layer artifact (abstract or full-text).
        prefix: Token family prefix (``ABSTRACT`` or ``FULLTEXT``).

    Returns:
        Mapping of ``<PREFIX>_*`` discourse token names to string values.
    """
    variables: dict = {}
    discourse: dict = (artifact or {}).get("discourse") or {}
    if not discourse:
        return variables
    n_analyzed = discourse.get("n_texts_analyzed")
    if n_analyzed is not None:
        variables[f"{prefix}_DISCOURSE_N_ANALYZED"] = str(int(n_analyzed))
    sample_fraction = discourse.get("sample_fraction")
    if sample_fraction is not None:
        variables[f"{prefix}_DISCOURSE_SAMPLE_FRACTION"] = _fmt_stat(
            sample_fraction
        )
    for section, value_key in (("patterns", "frequency"), ("rhetorical", "frequency")):
        members: dict = discourse.get(section) or {}
        for key in _discourse_order(section, members):
            entry = members.get(key) or {}
            frequency = entry.get(value_key)
            if frequency is not None:
                slug = str(key).upper()
                variables[f"{prefix}_{section.upper()}_{slug}"] = str(
                    int(frequency)
                )
    argumentative: dict = discourse.get("argumentative") or {}
    n_structures = argumentative.get("n_structures")
    if n_structures is not None:
        variables[f"{prefix}_ARG_STRUCTURES"] = str(int(n_structures))
    metaphorical = (discourse.get("persuasive") or {}).get(
        "metaphorical_language"
    ) or {}
    usage = metaphorical.get("usage_frequency")
    if usage is not None:
        variables[f"{prefix}_PERSUASIVE_METAPHORICAL"] = str(int(usage))
    return variables

BHL_DATA_DIR = PROJECT_DIR / "data" / "bhl"

#: Era buckets emitted by the BHL layer artifact, in canonical order.
BHL_ERA_KEYS: tuple[str, ...] = (
    "era_1850_1899",
    "era_1900_1949",
    "era_1950_1970",
)

#: The 18 canonical domain-seed terms (3 per Ento-Linguistic domain)
#: that receive BHL_<ERA>_<TERM>_PER_10K tokens.  Frozen names: every
#: member is a seed of the canonical
#: ``analysis.term_extraction.TerminologyExtractor.DOMAIN_SEEDS`` for
#: its domain, and all are present in the harvested artifact.
BHL_CANONICAL_TERMS: tuple[str, ...] = (
    # unit_of_individuality
    "colony",
    "nestmate",
    "superorganism",
    # behavior_and_identity
    "division of labor",
    "foraging",
    "worker",
    # power_and_labor
    "caste",
    "hierarchy",
    "queen",
    # sex_and_reproduction
    "brood",
    "mating",
    "reproduction",
    # kin_and_relatedness
    "altruism",
    "kin",
    "relatedness",
    # economics
    "allocation",
    "cost",
    "resource",
)


def _load_bhl_artifact(data_dir: Optional[Path] = None) -> dict:
    """Load the BHL era-stratified artifact.

    Args:
        data_dir: Directory containing ``era_term_usage.json``;
            ``None`` defaults to :data:`BHL_DATA_DIR`.

    Returns:
        Parsed artifact, or empty dict when the file is absent (the
        caller then emits no BHL_* tokens).
    """
    directory = data_dir if data_dir is not None else BHL_DATA_DIR
    return load_json(directory / "era_term_usage.json")


def _build_bhl_tokens(bhl_artifact: Optional[dict]) -> dict:
    """Map the BHL historical-layer artifact onto the BHL_* token family.

    Emits (all omitted when the artifact is absent/empty, never KeyError):

    - ``BHL_DOCUMENTS``: total analyzed BHL historical documents
      (``source.documents``, falling back to the sum of per-era counts).
    - ``BHL_ERA_<ERA>_DOCS``: per-era document counts (ERA in
      ``ERA_1850_1899``, ``ERA_1900_1949``, ``ERA_1950_1970``).
    - ``BHL_<ERA>_<TERM>_PER_10K``: per-era normalized term frequency
      (per 10k tokens, 4 decimals) for the
      :data:`BHL_CANONICAL_TERMS` that the artifact carries (TERM
      slugified like the CACE_TERM convention: uppercased,
      spaces/hyphens mapped to underscores).
    - Expanded per-era full-stack sections (emitted only when the era
      carries them; degenerate eras omit, never fabricated):
      ``BHL_ERA_<ERA>_TERMS`` (``extraction.n_terms``), and
      ``BHL_ERA_<ERA>_ENTROPY_MEAN`` (unweighted mean of the era's
      valid per-term semantic entropies in the bounded top-terms
      sample) / ``BHL_ERA_<ERA>_FRAMING`` (overall anthropomorphic
      framing proportion over occurrence contexts, 4 decimals) when
      those sections carry data.

    Args:
        bhl_artifact: Parsed ``era_term_usage.json`` contents, or
            ``None`` to load from the default ``data/bhl`` location.

    Returns:
        Mapping of BHL_* token names to formatted string values.
    """
    if bhl_artifact is None:
        bhl_artifact = _load_bhl_artifact()
    variables: dict = {}
    if not bhl_artifact:
        return variables
    eras: dict = bhl_artifact.get("eras") or {}
    source: dict = bhl_artifact.get("source") or {}
    total_documents = source.get("documents")
    if total_documents is None:
        total_documents = sum(
            int((eras.get(era) or {}).get("documents", 0))
            for era in BHL_ERA_KEYS
        )
    variables["BHL_DOCUMENTS"] = str(total_documents)
    for era in BHL_ERA_KEYS:
        era_upper = era.upper()
        entry = eras.get(era) or {}
        if not entry:
            continue
        variables[f"BHL_{era_upper}_DOCS"] = str(entry.get("documents", 0))
        frequencies = entry.get("terms_per_10k") or {}
        carried_terms = bhl_artifact.get("terms") or {}
        for term in BHL_CANONICAL_TERMS:
            if term not in carried_terms:
                continue
            slug = term.upper().replace("-", "_").replace(" ", "_")
            variables[f"BHL_{era_upper}_{slug}_PER_10K"] = _fmt_stat(
                frequencies.get(term, 0.0)
            )
        # Expanded per-era full-stack sections (omit when absent or
        # degenerate — the empty eras of an earlier harvest carry
        # none of these keys).
        extraction = entry.get("extraction") or {}
        if extraction:
            variables[f"BHL_{era_upper}_TERMS"] = str(
                int(extraction.get("n_terms", 0))
            )
        term_entropies = (entry.get("entropy") or {}).get("terms") or {}
        if term_entropies:
            mean_entropy = (
                sum(float(v) for v in term_entropies.values())
                / len(term_entropies)
            )
            variables[f"BHL_{era_upper}_ENTROPY_MEAN"] = _fmt_stat(
                mean_entropy
            )
        overall_framing = (entry.get("framing") or {}).get("overall") or {}
        if overall_framing:
            variables[f"BHL_{era_upper}_FRAMING"] = _fmt_stat(
                overall_framing.get("proportion")
            )
    return variables


def fill_manuscript(
    variables: dict[str, str],
    dry_run: bool = True,
    manuscript_dir: Path | None = None,
) -> dict[str, int]:
    """Validate {{VAR}} placeholder resolvability in manuscript .md files.

    Dry-run validation only: the canonical manuscript markdown must keep
    its ``{{VAR}}`` placeholders (the corpus-statistics editing rule —
    substitution happens in-memory at PDF render time via
    ``pipeline.rendering.build_pdf``), so this function NEVER writes
    substituted text back into the source markdown.  ``dry_run=False``
    raises instead of writing, so callers that relied on the old
    in-place baking fail loudly rather than corrupting the manuscript.

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
                raise RuntimeError(
                    "fill_manuscript no longer rewrites manuscript markdown "
                    "in place: baked-in statistics would violate the "
                    "corpus-statistics editing rule (see docs/manuscript/"
                    "AGENTS.md). Substitution happens at PDF build time "
                    "(pipeline.rendering.build_pdf); this call only "
                    "validates token coverage. Re-run with dry_run=True."
                )
            results[md_path.name] = count
    return results


def main() -> None:
    """Validate manuscript template variables (dry run; files unchanged)."""
    print("=" * 60)
    print("VALIDATING MANUSCRIPT TEMPLATE VARIABLES (dry run; files unchanged)")
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

    # Validate token coverage WITHOUT rewriting the canonical markdown
    # (see fill_manuscript: in-place baking would violate the editing rule).
    print(f"\nValidating variables in {MANUSCRIPT_DIR}/")
    results = fill_manuscript(variables, dry_run=True)

    total = sum(results.values())
    print("\nResults:")
    for filename, count in sorted(results.items()):
        print(f"  {filename}: {count} occurrences resolvable")
    print(f"\n  TOTAL: {total} placeholder occurrences resolvable across {len(results)} files")

    # Report any placeholders NOT covered by the variable map.  Placeholders
    # that resolved still sit in the markdown by design (substitution is
    # in-memory at PDF build); only unknown-variable names are warnings.
    unresolved = 0
    for md_path in sorted(MANUSCRIPT_DIR.glob("*.md")):
        content = md_path.read_text(encoding="utf-8")
        matches = sorted(set(re.findall(r"\{\{([A-Z_0-9]+)\}\}", content)))
        unknown = [m for m in matches if m not in variables]
        if unknown:
            unresolved += len(unknown)
            print(f"\n  WARNING: {len(unknown)} unknown variables in {md_path.name}:")
            for m in unknown:
                print(f"    - {{{{{m}}}}}")

    if unresolved == 0:
        print("\n  All template variables resolve.")
    else:
        print(f"\n  WARNING: {unresolved} template variables remain unresolved.")

    print("=" * 60)
