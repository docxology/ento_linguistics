"""Statistical analysis pipeline for Ento-Linguistic research.

Builds the frozen ``statistical_analysis.json`` artifact from real
term/domain analysis outputs:

- per-domain descriptive statistics over valid per-term semantic
  entropies (``DomainAnalyzer.iter_domain_term_entropies``),
- all 15 canonical-domain pairwise Welch t-tests with Cohen's d
  (Hedges-corrected) and Benjamini-Hochberg FDR correction,
- a one-way omnibus ANOVA over the per-domain entropy groups with an
  explicitly computed eta-squared.

When ``build_statistical_analysis`` is called with ``layer="abstract"``
the artifact additionally carries the abstract-layer sections:

- ``layer`` / ``domain_term_counts``: layer marker and per-domain
  extracted-term tallies (same semantics as the full-text artifact).
- ``framing``: anthropomorphic-framing proportions over the abstract
  corpus (same shape and occurrence-context semantics as the full-text
  artifact's ``add_framing_analysis`` section: every ±3-token context
  around a domain-term occurrence is evaluated with the public
  ``LinguisticFeatureExtractor.extract_framing_features`` API).
- ``framing_terms``: per-term framing proportions feeding the
  anthropomorphic-terminology figure.

Every layer also gains a ``discourse`` section (see
:func:`add_discourse_analysis`) computed over the corpus texts with the
public ``DiscourseAnalyzer`` API, deterministically bounded by corpus
size.

Every value in the artifact is computed from real data: groups too small
to test (fewer than 2 valid per-term entropies) are recorded in the
artifact's ``skipped`` list instead of being fabricated as 0.0.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from analysis.cace_scoring import CACEScore, evaluate_term_cace
from analysis.discourse_analysis import DiscourseAnalyzer
from analysis.domain_analysis import DomainAnalyzer
from analysis.text_analysis import LinguisticFeatureExtractor, TextProcessor
from analysis.statistics import (
    anova_test,
    benjamini_hochberg_correction,
    cohens_d,
    t_test,
)
from analysis.term_extraction import Term

__all__ = [
    "ABSTRACT_LAYER",
    "CANONICAL_DOMAINS",
    "CACE_SAMPLE_SIZE",
    "CACE_TABLE_TERMS",
    "add_discourse_analysis",
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

# Layer marker for the abstract corpus artifact.  The full-text and
# arXiv builders (which spread this module's statistics dict into their
# own artifacts) set their own layer markers, so ``layer`` is only
# emitted when the caller asks for the abstract layer explicitly.
ABSTRACT_LAYER = "abstract"

# Half-width (in tokens) of the term-occurrence context window scanned
# for anthropomorphic framing features.  Mirrors
# ``pipeline.fulltext_pipeline.FRAMING_CONTEXT_WINDOW`` (imported there
# by value: importing the module here would be circular because it
# imports this one), and matches the ``window_size=3`` context
# definition ``TerminologyExtractor`` records for every extracted term.
FRAMING_CONTEXT_WINDOW = 3

# Minimum character length for a text to enter the discourse-analysis
# pass.  Tiny texts (one-line abstracts, stubs) would pollute the
# sentence-level argumentative-structure detection with degenerate
# claims; they are excluded and the exclusion is counted in the
# section's metadata — never silently dropped.
DISCOURSE_MIN_TEXT_LENGTH = 200

# Deterministic runtime bound for the discourse pass, expressed as the
# total character volume of the analyzed texts: a static proxy for the
# brief's "~30 minutes per pass" budget that keeps the artifact fully
# deterministic (no wall-clock-dependent sampling decisions).  When the
# eligible corpus exceeds this volume, every k-th text is analyzed (k
# chosen so at most ``DISCOURSE_SAMPLE_TARGET`` texts are read) and the
# covered fraction is recorded as ``sample_fraction``.
DISCOURSE_BUDGET_CHARS = 20_000_000
DISCOURSE_SAMPLE_TARGET = 1500

# Cap on recorded examples per discourse pattern / argumentative
# structure in the artifact (the analyzer's own frequency counts stay
# unbounded; only the stored example strings are capped).
DISCOURSE_EXAMPLE_CAP = 10

# Representative terms evaluated per-term in the CACE section of the frozen
# artifact (the S02 ``tab:cace_full`` supplement table).  Terms present in
# the extraction are scored from their real entropy/contexts/domains;
# proposed replacement terms absent from the corpus are still scored
# deterministically from their text features (empty contexts, zero
# entropy) and recorded with ``in_corpus: false``.
CACE_TABLE_TERMS: tuple = (
    "queen",
    "primary reproductive",
    "worker",
    "non-reproductive helper",
    "slave",
    "host worker",
    "caste",
    "task group",
    "soldier",
    "major worker",
    "colony",
    "haplodiploidy",
    "trophallaxis",
)


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
    cace_scores: Optional[List[CACEScore]] = None,
) -> Dict[str, Any]:
    """Build one domain's entry of the ``descriptives`` section.

    Args:
        domain: Canonical domain name.
        entropy_values: Valid per-term entropies for the domain (from
            ``iter_domain_term_entropies``).
        domain_terms: All terms assigned to the domain.
        analyzer: Shared ``DomainAnalyzer`` (used for ambiguity metrics).
        texts: Source texts for context.
        cace_scores: Precomputed per-term CACE scores for the domain's
            bounded sample (from :func:`_domain_cace_scores`).  Computed
            here when omitted.

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

    scores = (
        cace_scores
        if cace_scores is not None
        else _domain_cace_scores(domain_terms)
    )
    if scores:
        entry["cace_mean"] = float(np.mean([s.aggregate for s in scores]))
    return entry


def _domain_cace_scores(domain_terms: List[Term]) -> List[CACEScore]:
    """Score the bounded, deterministic CACE sample for one domain.

    Shared by the ``descriptives`` CACE mean and the per-domain ``cace``
    aggregates so both artifacts report values computed from one scoring
    pass.
    """
    return [
        evaluate_term_cace(
            term=t.text,
            semantic_entropy=float(getattr(t, "semantic_entropy", 0.0)),
            contexts=list(getattr(t, "contexts", []))[:10],
            domains=list(t.domains),
        )
        for t in _cace_sample(domain_terms)
    ]


def _format_domain_cace_entry(scores: List[CACEScore]) -> Dict[str, Any]:
    """Build one domain's entry of the ``cace`` section.

    Args:
        scores: Per-term CACE scores for the domain's bounded sample
            (from :func:`_domain_cace_scores`).

    Returns:
        Frozen-schema entry with the aggregate mean/min/max over the
        sample, the per-dimension means, and the sampled term count.
        Domains with no sampled terms map to an empty dict — the key is
        omitted entirely rather than reported as fabricated zeros.
    """
    if not scores:
        return {}
    aggregates = [s.aggregate for s in scores]
    return {
        "mean": float(np.mean(aggregates)),
        "min": float(np.min(aggregates)),
        "max": float(np.max(aggregates)),
        "clarity": float(np.mean([s.clarity for s in scores])),
        "appropriateness": float(np.mean([s.appropriateness for s in scores])),
        "consistency": float(np.mean([s.consistency for s in scores])),
        "evolvability": float(np.mean([s.evolvability for s in scores])),
        "n_terms": len(scores),
    }


def _format_cace_term_entry(term: str, term_data: Optional[Term]) -> Dict[str, Any]:
    """Build one entry of the ``cace_terms`` section.

    Args:
        term: Representative term name.
        term_data: The extracted ``Term`` for ``term`` when it occurs in
            the current extraction, else ``None``.

    Returns:
        Frozen-schema entry with all four CACE dimensions, the aggregate,
        and an ``in_corpus`` flag.  Terms absent from the corpus are scored
        deterministically from their text features (zero entropy, empty
        contexts), never fabricated from hard-coded numbers.
    """
    if term_data is not None:
        score = evaluate_term_cace(
            term=term_data.text,
            semantic_entropy=float(getattr(term_data, "semantic_entropy", 0.0)),
            contexts=list(getattr(term_data, "contexts", []))[:10],
            domains=list(term_data.domains),
        )
        in_corpus = True
    else:
        score = evaluate_term_cace(
            term=term, semantic_entropy=0.0, contexts=[], domains=[]
        )
        in_corpus = False
    return {
        "clarity": score.clarity,
        "appropriateness": score.appropriateness,
        "consistency": score.consistency,
        "evolvability": score.evolvability,
        "aggregate": score.aggregate,
        "in_corpus": in_corpus,
    }


def _domain_term_counts(terms: List[Term]) -> Dict[str, Dict[str, Any]]:
    """Count extracted terms per canonical domain assignment.

    Same semantics as ``pipeline.fulltext_pipeline._domain_term_counts``:
    a term assigned to several domains contributes to each of them.

    Args:
        terms: Extracted terms.

    Returns:
        Mapping from domain name to ``{"term_count",
        "bridging_term_count", "total_frequency"}``, sorted by domain.
    """
    counts: Dict[str, Dict[str, Any]] = {}
    for term in terms:
        for domain in term.domains:
            entry = counts.setdefault(
                domain,
                {"term_count": 0, "bridging_term_count": 0, "total_frequency": 0},
            )
            entry["term_count"] += 1
            entry["bridging_term_count"] += 1 if len(term.domains) > 1 else 0
            entry["total_frequency"] += term.frequency
    return dict(sorted(counts.items()))


def _framing_section(
    terms: List[Term], texts: List[str]
) -> "Tuple[Dict[str, Any], Dict[str, Any]]":
    """Compute abstract-layer anthropomorphic-framing proportions.

    Occurrence-context semantics identical to the full-text layer's
    ``add_framing_analysis``: every occurrence of a domain-assigned term
    in the corpus token stream (``TextProcessor.process_text(text,
    lemmatize=False)`` — the exact stream ``TerminologyExtractor``
    counts) contributes one ±``FRAMING_CONTEXT_WINDOW``-token context,
    evaluated with the public
    ``LinguisticFeatureExtractor.extract_framing_features`` API.  A
    context is a framing match when it contains at least one
    anthropomorphic framing pattern match.

    Unlike the full-text pass, no term-vocabulary reconstruction is
    needed: the abstract layer's extracted ``Term`` objects (with their
    domain assignments) are the artifact's own extraction, so their
    ``text``/``domains`` are used directly.

    Args:
        terms: Extracted terms with domain assignments.
        texts: Abstract corpus the terms were extracted from.

    Returns:
        ``(framing, framing_terms)``: ``framing`` maps each domain with
        at least one evaluated occurrence context to ``{"proportion":
        float, "n_contexts": int}`` plus an ``"overall"`` entry counting
        each occurrence once; ``framing_terms`` maps each term with at
        least one occurrence context to ``{"proportion": float,
        "n_contexts": int, "domains": [..]}`` (the per-term data behind
        the anthropomorphic-terminology figure).
    """
    token_domains: Dict[str, List[str]] = {
        term.text: list(term.domains) for term in terms if term.domains
    }
    if not token_domains or not texts:
        return {}, {}

    processor = TextProcessor()
    feature_extractor = LinguisticFeatureExtractor()
    domain_contexts: Dict[str, int] = {}
    domain_framed: Dict[str, int] = {}
    term_contexts: Dict[str, int] = {}
    term_framed: Dict[str, int] = {}
    overall_contexts = 0
    overall_framed = 0
    for text in texts:
        if not isinstance(text, str) or not text.strip():
            continue
        tokens = processor.process_text(text, lemmatize=False)
        n_tokens = len(tokens)
        for position, token in enumerate(tokens):
            domains = token_domains.get(token)
            if not domains:
                continue
            start = max(0, position - FRAMING_CONTEXT_WINDOW)
            end = min(n_tokens, position + FRAMING_CONTEXT_WINDOW + 1)
            context = " ".join(tokens[start:end])
            is_framed = bool(
                feature_extractor.extract_framing_features(context)[
                    "anthropomorphic_terms"
                ]
            )
            for domain in domains:
                domain_contexts[domain] = domain_contexts.get(domain, 0) + 1
                if is_framed:
                    domain_framed[domain] = domain_framed.get(domain, 0) + 1
            term_contexts[token] = term_contexts.get(token, 0) + 1
            if is_framed:
                term_framed[token] = term_framed.get(token, 0) + 1
            overall_contexts += 1
            if is_framed:
                overall_framed += 1

    framing: Dict[str, Any] = {}
    for domain in sorted(domain_contexts):
        n_contexts = domain_contexts[domain]
        if not n_contexts:
            continue
        framing[domain] = {
            "proportion": round(domain_framed.get(domain, 0) / n_contexts, 6),
            "n_contexts": n_contexts,
        }
    if overall_contexts:
        framing["overall"] = {
            "proportion": round(overall_framed / overall_contexts, 6),
            "n_contexts": overall_contexts,
        }

    framing_terms: Dict[str, Any] = {}
    for term_text in sorted(term_contexts):
        n_contexts = term_contexts[term_text]
        if not n_contexts:
            continue
        framing_terms[term_text] = {
            "proportion": round(term_framed.get(term_text, 0) / n_contexts, 6),
            "n_contexts": n_contexts,
            "domains": list(token_domains[term_text]),
        }
    return framing, framing_terms


def _discourse_sample(texts: List[str]) -> "Tuple[List[str], int, float]":
    """Select the deterministic discourse-analysis sample.

    Texts below ``DISCOURSE_MIN_TEXT_LENGTH`` characters are excluded
    (counted, never silently dropped).  When the eligible corpus exceeds
    the ``DISCOURSE_BUDGET_CHARS`` runtime proxy, every k-th text is
    analyzed with k chosen so at most ``DISCOURSE_SAMPLE_TARGET`` texts
    are read — a static, corpus-determined bound standing in for the
    brief's "~30 minutes per pass" budget, so the artifact stays
    deterministic.

    Args:
        texts: Candidate corpus texts.

    Returns:
        ``(analysis_texts, n_excluded, sample_fraction)``.
    """
    eligible = [
        t for t in texts if isinstance(t, str) and len(t) >= DISCOURSE_MIN_TEXT_LENGTH
    ]
    n_excluded = len(texts) - len(eligible)
    if not eligible:
        return [], n_excluded, 0.0
    total_chars = sum(len(t) for t in eligible)
    if (
        total_chars > DISCOURSE_BUDGET_CHARS
        and len(eligible) > DISCOURSE_SAMPLE_TARGET
    ):
        stride = -(-len(eligible) // DISCOURSE_SAMPLE_TARGET)  # ceil division
        sample = eligible[::stride]
        fraction = round(len(sample) / len(eligible), 6)
        return sample, n_excluded, fraction
    return eligible, n_excluded, 1.0


def _discourse_section(texts: List[str]) -> Optional[Dict[str, Any]]:
    """Compute the corpus-level ``discourse`` section.

    Aggregates, over the (deterministically bounded) eligible texts:

    - ``patterns``: per-discourse-pattern totals from
      ``DiscourseAnalyzer.analyze_discourse_patterns`` — ``frequency``
      (instance count), ``rhetorical_function``, ``domains``, and up to
      ``DISCOURSE_EXAMPLE_CAP`` recorded examples.
    - ``rhetorical``: per-strategy ``frequency`` (total matches) and
      ``text_count`` (distinct texts containing the strategy) from
      ``analyze_rhetorical_strategies``.
    - ``argumentative``: aggregate structure statistics from
      ``analyze_argumentative_structures`` (structure counts, evidence/
      warrant/qualification/marker presence, top discourse markers, and
      up to five recorded claims).
    - ``persuasive``: per-technique effectiveness from
      ``measure_persuasive_effectiveness`` verbatim.

    Corpus-level aggregation only: per-domain breakdowns would require
    term-context scoping per domain (multiplied analyzer passes) and are
    deliberately not computed.  Deterministic.

    Args:
        texts: Candidate corpus texts.

    Returns:
        The section dict with metadata (``n_texts``,
        ``n_texts_analyzed``, ``n_texts_excluded_min_length``,
        ``min_text_length``, ``sample_fraction``), or ``None`` when no
        text survives the minimum-length guard (empty/degenerate corpus
        is omitted honestly, never zero-filled).
    """
    analysis_texts, n_excluded, sample_fraction = _discourse_sample(texts)
    if not analysis_texts:
        return None

    analyzer = DiscourseAnalyzer()

    # Patterns — per-pattern instance counts over the corpus.
    patterns: Dict[str, Any] = {}
    for pattern_type, pattern in sorted(
        analyzer.analyze_discourse_patterns(analysis_texts).items()
    ):
        patterns[pattern_type] = {
            "frequency": int(pattern.frequency),
            "rhetorical_function": pattern.rhetorical_function,
            "domains": sorted(pattern.domains),
            "examples": list(pattern.examples[:DISCOURSE_EXAMPLE_CAP]),
        }

    # Rhetorical strategies — frequencies and text coverage.
    rhetorical: Dict[str, Any] = {}
    for strategy, data in sorted(
        analyzer.analyze_rhetorical_strategies(analysis_texts).items()
    ):
        rhetorical[strategy] = {
            "frequency": int(data.get("frequency", 0)),
            "text_count": int(data.get("text_count", 0)),
        }

    # Argumentative structures — aggregate statistics.
    structures = analyzer.analyze_argumentative_structures(analysis_texts)
    marker_counts: Dict[str, int] = {}
    n_with_evidence = 0
    n_with_warrant = 0
    n_with_qualification = 0
    n_with_markers = 0
    marker_total = 0
    for structure in structures:
        if structure.evidence:
            n_with_evidence += 1
        if structure.warrant:
            n_with_warrant += 1
        if structure.qualification:
            n_with_qualification += 1
        if structure.discourse_markers:
            n_with_markers += 1
            marker_total += len(structure.discourse_markers)
            for marker in structure.discourse_markers:
                marker_counts[marker] = marker_counts.get(marker, 0) + 1
    n_structures = len(structures)
    argumentative: Dict[str, Any] = {
        "n_structures": n_structures,
        "n_with_evidence": n_with_evidence,
        "n_with_warrant": n_with_warrant,
        "n_with_qualification": n_with_qualification,
        "n_with_discourse_markers": n_with_markers,
        "mean_discourse_markers": (
            round(marker_total / n_with_markers, 6) if n_with_markers else 0.0
        ),
        "top_discourse_markers": dict(
            sorted(marker_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
        ),
        "example_claims": [
            claim[:200] for claim in (s.claim for s in structures) if claim
        ][:5],
    }

    # Persuasive techniques — effectiveness metrics verbatim.
    persuasive: Dict[str, Any] = {
        technique: dict(data)
        for technique, data in sorted(
            analyzer.measure_persuasive_effectiveness(analysis_texts).items()
        )
    }

    return {
        "n_texts": len(texts),
        "n_texts_excluded_min_length": n_excluded,
        "n_texts_analyzed": len(analysis_texts),
        "min_text_length": DISCOURSE_MIN_TEXT_LENGTH,
        "sample_fraction": sample_fraction,
        "patterns": patterns,
        "rhetorical": rhetorical,
        "argumentative": argumentative,
        "persuasive": persuasive,
    }


def add_discourse_analysis(
    artifact: Dict[str, Any], texts: List[str]
) -> Dict[str, Any]:
    """Merge the corpus-level ``discourse`` section into an artifact.

    Public merge path used by the figure pipeline to add the discourse
    section to an existing on-disk artifact (e.g. the fingerprint-guarded
    full-text artifact) without recomputing the statistics stages.

    Args:
        artifact: Artifact dict (read-only; the returned copy carries
            the new section).
        texts: Corpus texts of the artifact's layer.

    Returns:
        A copy of ``artifact`` with ``"discourse"`` added — omitted when
        no text survives the minimum-length guard (degenerate corpora
        are never zero-filled).
    """
    merged = dict(artifact)
    section = _discourse_section(texts)
    if section is not None:
        merged["discourse"] = section
    return merged


def build_statistical_analysis(
    terms: Union[List[Term], Dict[str, Term]],
    texts: List[str],
    metric: str = "semantic_entropy",
    layer: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the frozen statistical-analysis artifact from real term data.

    Computes, over the six canonical Ento-Linguistic domains:

    - ``descriptives``: per-domain per-term entropy mean/SD (ddof=1),
      ambiguity mean (wave-1 ambiguity metrics; omitted when no valid
      terms), CACE mean over a bounded deterministic term sample, and the
      bridging-term count from domain assignments.
    - ``cace``: per-domain CACE aggregates over the same bounded sample —
      aggregate mean/min/max, per-dimension means (clarity/appropriateness/
      consistency/evolvability), and the sampled term count.  Domains with
      no sampled terms are omitted, never fabricated.
    - ``cace_terms``: per-term CACE evaluations for the frozen
      representative-term list (``CACE_TABLE_TERMS``) with an ``in_corpus``
      flag; terms absent from the extraction are scored deterministically
      from their text features.
    - ``pairwise``: every canonical-domain pair tested with Welch's
      t-test and Cohen's d (Hedges-corrected) on the per-term entropies;
      raw p-values are Benjamini-Hochberg corrected across all computed
      comparisons.  Pairs involving a degenerate group (fewer than 2
      valid entropies) are skipped, not fabricated.
    - ``anova``: one-way omnibus F-test over the per-domain entropy
      groups with eta-squared = SS_between / SS_total.  Omitted when
      fewer than two testable groups remain.
    - ``skipped``: honest record of every comparison/test omitted for
      degenerate (n < 2) groups.
    - ``discourse`` (any layer with eligible texts): corpus-level
      discourse/rhetorical/persuasive analysis over ``texts`` — see
      :func:`add_discourse_analysis` for the exact shape.  Omitted when
      no text survives the minimum-length guard.

    When ``layer`` is set (the abstract layer passes
    ``layer="abstract"``) the artifact additionally carries:

    - ``layer``: the layer marker.
    - ``domain_term_counts``: per-domain extracted-term tallies (same
      semantics as the full-text artifact's section).
    - ``framing``: anthropomorphic-framing proportions with the SAME
      shape and occurrence-context semantics as the full-text artifact's
      ``add_framing_analysis`` section (per-domain + ``overall``).
    - ``framing_terms``: per-term framing proportions (figure data).

    Layers that set their own marker (full-text, arXiv) keep the
    default ``layer=None``: their builders emit their own
    ``layer``/``domain_term_counts`` and framing sections, so nothing
    here would override them.
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
        layer: Optional layer marker.  ``"abstract"`` adds the
            abstract-layer sections (see above); the default ``None``
            emits the shared statistics + ``discourse`` sections only.

    Returns:
        Artifact dict matching the frozen ``statistical_analysis.json``
        schema (plus the documented abstract-layer / discourse
        additions).  Deterministic for identical inputs.

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
    cace: Dict[str, Any] = {}
    entropy_groups: Dict[str, np.ndarray] = {}
    skipped: List[Dict[str, str]] = []

    for domain in sorted(CANONICAL_DOMAINS):
        domain_terms = grouped.get(domain, [])
        values = domain_entropies.get(domain, [])
        domain_cace = _domain_cace_scores(domain_terms)
        descriptives[domain] = _format_domain_descriptives(
            domain, values, domain_terms, analyzer, texts, cace_scores=domain_cace
        )
        if domain_cace:
            cace[domain] = _format_domain_cace_entry(domain_cace)
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

    # ── Representative-term CACE evaluations (S02 table) ───────────────
    term_lookup = {t.text.lower().strip(): t for t in term_list}
    cace_terms: Dict[str, Any] = {
        name: _format_cace_term_entry(name, term_lookup.get(name))
        for name in CACE_TABLE_TERMS
    }

    artifact: Dict[str, Any] = {
        "descriptives": descriptives,
        "cace": cace,
        "cace_terms": cace_terms,
        "pairwise": pairwise,
        "anova": anova,
        "corrections": {
            "method": "benjamini_hochberg",
            "n_comparisons": len(p_values),
        },
        "skipped": skipped,
    }

    # ── Corpus-level discourse analysis (both layers) ─────────────────
    # Omitted honestly when no text survives the minimum-length guard.
    discourse = _discourse_section(texts)
    if discourse is not None:
        artifact["discourse"] = discourse

    # ── Abstract-layer parity sections (layer marker requested) ───────
    if layer is not None:
        artifact["layer"] = layer
        artifact["domain_term_counts"] = _domain_term_counts(term_list)
        framing, framing_terms = _framing_section(term_list, texts)
        artifact["framing"] = framing
        artifact["framing_terms"] = framing_terms
    return artifact
