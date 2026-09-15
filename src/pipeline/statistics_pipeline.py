"""Statistical analysis pipeline for Ento-Linguistic research.

Builds the frozen ``statistical_analysis.json`` artifact from real
term/domain analysis outputs:

- per-domain descriptive statistics over valid per-term semantic
  entropies (``DomainAnalyzer.iter_domain_term_entropies``),
- all 15 canonical-domain pairwise Welch t-tests with Cohen's d
  (Hedges-corrected) and Benjamini-Hochberg FDR correction,
- a one-way omnibus ANOVA over the per-domain entropy groups with an
  explicitly computed eta-squared.

Every value in the artifact is computed from real data: groups too small
to test (fewer than 2 valid per-term entropies) are recorded in the
artifact's ``skipped`` list instead of being fabricated as 0.0.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, List, Union

import numpy as np

from analysis.cace_scoring import evaluate_term_cace
from analysis.domain_analysis import DomainAnalyzer
from analysis.statistics import (
    anova_test,
    benjamini_hochberg_correction,
    cohens_d,
    t_test,
)
from analysis.term_extraction import Term

__all__ = [
    "CANONICAL_DOMAINS",
    "CACE_SAMPLE_SIZE",
    "build_statistical_analysis",
]

# The six canonical Ento-Linguistic domains.  Mirrors
# ``visualization._style.CANONICAL_DOMAINS`` (imported here by value, not by
# reference, so this pipeline module stays import-light — no matplotlib).
CANONICAL_DOMAINS: tuple = (
    "unit_of_individuality",
    "behavior_and_identity",
    "power_and_labor",
    "sex_and_reproduction",
    "kin_and_relatedness",
    "economics",
)

# Upper bound on terms scored per domain for the CACE aggregate.  Matches the
# 50-term sampling bound used by the CACE panel in
# ``visualization/concept_visualization.py``.
CACE_SAMPLE_SIZE = 50

# BH significance threshold applied to the corrected pairwise p-values.
BH_ALPHA = 0.05


def _as_term_list(
    terms: Union[List[Term], Dict[str, Term]],
) -> List[Term]:
    """Normalize the terms argument to a list of ``Term`` objects.

    Args:
        terms: Terms as a list or as a name -> Term mapping (the shape the
            analysis pipeline produces).

    Returns:
        List of ``Term`` in insertion order (deterministic for dict input).
    """
    return list(terms.values()) if isinstance(terms, dict) else list(terms)


def _group_terms_by_domain(terms: List[Term]) -> Dict[str, List[Term]]:
    """Group terms by domain assignment, preserving term iteration order.

    Args:
        terms: Terms to group.

    Returns:
        Mapping from domain name to the terms assigned to it (a term in
        several domains appears in each of them).
    """
    grouped: Dict[str, List[Term]] = {}
    for term in terms:
        for domain in term.domains:
            grouped.setdefault(domain, []).append(term)
    return grouped


def _cace_sample(domain_terms: List[Term]) -> List[Term]:
    """Select the bounded, deterministically ordered CACE sample.

    Sampling rule (documented contract): order the domain's terms by
    descending extraction frequency, breaking ties by term text ascending,
    and keep the first ``CACE_SAMPLE_SIZE``.

    Args:
        domain_terms: All terms assigned to the domain.

    Returns:
        At most ``CACE_SAMPLE_SIZE`` terms in the deterministic order.
    """
    ordered = sorted(domain_terms, key=lambda t: (-t.frequency, t.text))
    return ordered[:CACE_SAMPLE_SIZE]


def _format_domain_descriptives(
    domain: str,
    entropy_values: List[float],
    domain_terms: List[Term],
    analyzer: DomainAnalyzer,
    texts: List[str],
) -> Dict[str, Any]:
    """Build one domain's entry of the ``descriptives`` section.

    Args:
        domain: Canonical domain name.
        entropy_values: Valid per-term entropies for the domain (from
            ``iter_domain_term_entropies``).
        domain_terms: All terms assigned to the domain.
        analyzer: Shared ``DomainAnalyzer`` (used for ambiguity metrics).
        texts: Source texts for context.

    Returns:
        Frozen-schema descriptive entry.  ``entropy_mean``/``entropy_sd``/
        ``ambiguity_mean`` are present only when the domain has at least one
        valid per-term entropy — absent keys mean "no data", never a
        fabricated 0.0.
    """
    entry: Dict[str, Any] = {
        "n_terms": len(entropy_values),
        "bridging_count": sum(1 for t in domain_terms if len(t.domains) > 1),
    }
    if entropy_values:
        values = np.asarray(entropy_values, dtype=float)
        entry["entropy_mean"] = float(np.mean(values))
        # ddof=1 sample SD; a single observation has no spread, report 0.0.
        entry["entropy_sd"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        # Wave-1 contract: the domain ambiguity score is the mean of valid
        # per-term entropies (real values; omitted entirely when no term in
        # the domain had enough contexts).
        metrics = analyzer.quantify_ambiguity_metrics(domain_terms, texts)
        ambiguity = metrics.get("domain_metrics", {}).get("average_ambiguity_score")
        if ambiguity is not None:
            entry["ambiguity_mean"] = float(ambiguity)

    sample = _cace_sample(domain_terms)
    if sample:
        cace_scores = [
            evaluate_term_cace(
                term=t.text,
                semantic_entropy=float(getattr(t, "semantic_entropy", 0.0)),
                contexts=list(getattr(t, "contexts", []))[:10],
                domains=list(t.domains),
            ).aggregate
            for t in sample
        ]
        entry["cace_mean"] = float(np.mean(cace_scores))
    return entry


def build_statistical_analysis(
    terms: Union[List[Term], Dict[str, Term]],
    texts: List[str],
    metric: str = "semantic_entropy",
) -> Dict[str, Any]:
    """Build the frozen statistical-analysis artifact from real term data.

    Computes, over the six canonical Ento-Linguistic domains:

    - ``descriptives``: per-domain per-term entropy mean/SD (ddof=1),
      ambiguity mean (wave-1 ambiguity metrics; omitted when no valid
      terms), CACE mean over a bounded deterministic term sample, and the
      bridging-term count from domain assignments.
    - ``pairwise``: every canonical-domain pair tested with Welch's
      t-test and Cohen's d (Hedges-corrected) on the per-term entropies;
      raw p-values are Benjamini-Hochberg corrected across all computed
      comparisons.  Pairs involving a degenerate group (fewer than 2
      valid entropies) are skipped, not fabricated.
    - ``anova``: one-way omnibus F-test over the per-domain entropy
      groups with eta-squared = SS_between / SS_total.  Omitted when
      fewer than two testable groups remain.
    - ``corrections``: multiple-comparison metadata.
    - ``skipped``: honest record of every comparison/test omitted for
      degenerate (n < 2) groups.

    Args:
        terms: Extracted terms (list of ``Term`` or name -> Term mapping).
            ``Term.semantic_entropy`` (when attached by the pipeline) feeds
            the CACE clarity dimension; per-term entropies for the
            statistical tests are recomputed here from ``texts`` via
            ``DomainAnalyzer.iter_domain_term_entropies``.
        texts: Source texts used to compute per-term semantic entropies.
        metric: Statistical metric under test.  Only
            ``"semantic_entropy"`` is supported by the wave-1 entropy
            implementation.

    Returns:
        Artifact dict matching the frozen ``statistical_analysis.json``
        schema.  Deterministic for identical inputs.

    Raises:
        ValueError: If ``metric`` is not ``"semantic_entropy"``.
    """
    if metric != "semantic_entropy":
        raise ValueError(
            f"Unsupported metric {metric!r}: only 'semantic_entropy' is "
            "implemented by the wave-1 entropy contract"
        )

    analyzer = DomainAnalyzer()
    term_list = _as_term_list(terms)
    grouped = _group_terms_by_domain(term_list)

    # Wave-1 contract: only terms whose entropy was actually computed
    # (status == "ok") contribute a value; domains with no valid terms
    # map to an empty list.
    domain_entropies = analyzer.iter_domain_term_entropies(term_list, texts)

    descriptives: Dict[str, Any] = {}
    entropy_groups: Dict[str, np.ndarray] = {}
    skipped: List[Dict[str, str]] = []

    for domain in sorted(CANONICAL_DOMAINS):
        domain_terms = grouped.get(domain, [])
        values = domain_entropies.get(domain, [])
        descriptives[domain] = _format_domain_descriptives(
            domain, values, domain_terms, analyzer, texts
        )
        if len(values) >= 2:
            entropy_groups[domain] = np.asarray(values, dtype=float)
        else:
            skipped.append(
                {
                    "kind": "domain_group",
                    "domain": domain,
                    "reason": (
                        f"only {len(values)} valid per-term entropy value(s); "
                        "n < 2 groups cannot be tested"
                    ),
                }
            )

    # ── Pairwise Welch t-tests + BH correction ────────────────────────
    pairwise: List[Dict[str, Any]] = []
    tested: List[str] = sorted(entropy_groups)
    for domain_a, domain_b in combinations(tested, 2):
        x = entropy_groups[domain_a]
        y = entropy_groups[domain_b]
        result = t_test(x, y, equal_var=False)
        pairwise.append(
            {
                "domain_a": domain_a,
                "domain_b": domain_b,
                "metric": metric,
                "t": float(result["t_statistic"]),
                "df": float(result["degrees_of_freedom"]),
                "p": float(result["p_value"]),
                "p_bh": 0.0,  # filled in below after BH correction
                "cohens_d": cohens_d(x, y, correction=True),
                "n_a": int(len(x)),
                "n_b": int(len(y)),
                "significant_bh": False,  # filled in below
            }
        )

    p_values = [entry["p"] for entry in pairwise]
    correction = benjamini_hochberg_correction(p_values, q=BH_ALPHA)
    for entry, p_bh in zip(pairwise, correction["adjusted_p_values"]):
        entry["p_bh"] = float(p_bh)
        entry["significant_bh"] = bool(p_bh < BH_ALPHA)

    # ── Omnibus one-way ANOVA with explicit eta-squared ───────────────
    anova: Dict[str, Any] = {}
    group_list = [entropy_groups[d] for d in tested]
    if len(group_list) >= 2:
        f_result = anova_test(group_list)
        all_values = np.concatenate(group_list)
        overall_mean = float(np.mean(all_values))
        ss_between = sum(
            len(g) * (float(np.mean(g)) - overall_mean) ** 2 for g in group_list
        )
        ss_total = float(np.sum((all_values - overall_mean) ** 2))
        eta_squared = ss_between / ss_total if ss_total > 0 else 0.0
        anova = {
            "metric": metric,
            "F": float(f_result["f_statistic"]),
            "df1": float(f_result["df_between"]),
            "df2": float(f_result["df_within"]),
            "p": float(f_result["p_value"]),
            "eta_squared": float(eta_squared),
        }
    else:
        skipped.append(
            {
                "kind": "anova",
                "reason": (
                    f"only {len(group_list)} testable domain group(s); "
                    "one-way ANOVA requires at least 2"
                ),
            }
        )

    return {
        "descriptives": descriptives,
        "pairwise": pairwise,
        "anova": anova,
        "corrections": {
            "method": "benjamini_hochberg",
            "n_comparisons": len(p_values),
        },
        "skipped": skipped,
    }
