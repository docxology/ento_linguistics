"""Full-text analysis pipeline (parallel PMC layer).

Builds ``output/data/fulltext_analysis.json`` — the full-text-layer
sibling of the abstract-layer statistical artifact
(``output/data/statistical_analysis.json``).  The artifact shape mirrors
the abstract layer exactly (``descriptives``/``cace``/``cace_terms``/
``pairwise``/``anova``/``corrections``/``skipped``) and adds the
parallel-layer markers:

- ``"layer": "fulltext"``,
- ``n_documents`` and per-document metadata with token counts,
- ``domain_term_counts`` per-domain extracted-term counts,
- ``framing`` per-domain and overall anthropomorphic-framing
  proportions over the full texts (:func:`add_framing_analysis`).

Reuse contract: terminology is extracted over the full texts with the
public ``analysis.term_extraction`` API (``TerminologyExtractor``), and
all statistics are delegated to
``pipeline.statistics_pipeline.build_statistical_analysis``, which in
turn uses the public ``analysis.domain_analysis`` APIs
(``DomainAnalyzer.iter_domain_term_entropies`` and the ambiguity
metrics) over the six canonical Ento-Linguistic domains.  Nothing here
re-implements domain statistics.

Deterministic for identical inputs (KMeans clustering is seeded inside
the canonical entropy implementation; extraction and grouping are
order-stable).

This module is NOT wired into ``manuscript_figures`` — a later wave
integrates the parallel layer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from analysis.term_extraction import TerminologyExtractor
from analysis.text_analysis import LinguisticFeatureExtractor, TextProcessor
from data.pmc_fulltext import load_fulltexts
from pipeline.statistics_pipeline import build_statistical_analysis

__all__ = [
    "FULLTEXT_LAYER",
    "FRAMING_CONTEXT_WINDOW",
    "add_framing_analysis",
    "build_fulltext_analysis",
    "main",
]

# Layer marker stored in every full-text artifact.
FULLTEXT_LAYER = "fulltext"

# Word-boundary token pattern for per-document token counts.
_TOKEN_RE = re.compile(r"\w+")

# Half-width (in tokens) of the term-occurrence context window scanned for
# anthropomorphic framing features.  Matches the ``window_size=3`` context
# definition ``TerminologyExtractor`` records for every extracted term, so a
# framing "context" is exactly the extractor's own usage-context surface.
FRAMING_CONTEXT_WINDOW = 3


def _document_text(record: Dict[str, Any]) -> str:
    """Assemble the analyzed text for one full-text record.

    Args:
        record: Corpus record from ``data/fulltexts/fulltexts.json``.

    Returns:
        Title, abstract, and body joined with blank lines (missing
        fields skipped) so term extraction sees the same surface the
        statistics passes do.
    """
    parts = [
        str(record.get(field) or "") for field in ("title", "abstract", "body_text")
    ]
    return "\n\n".join(part for part in parts if part.strip())


def _domain_term_counts(terms: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Count extracted terms per canonical domain assignment.

    Args:
        terms: Extracted terms (name -> ``Term``).

    Returns:
        Mapping from domain name to ``{"term_count", "bridging_term_count",
        "total_frequency"}``.  Domains with no assigned terms map to an
        empty entry — never fabricated counts.
    """
    counts: Dict[str, Dict[str, Any]] = {}
    for term in terms.values():
        for domain in term.domains:
            entry = counts.setdefault(
                domain, {"term_count": 0, "bridging_term_count": 0, "total_frequency": 0}
            )
            entry["term_count"] += 1
            entry["bridging_term_count"] += 1 if len(term.domains) > 1 else 0
            entry["total_frequency"] += term.frequency
    return dict(sorted(counts.items()))


def _framing_token_domains(
    counts: Counter,
    classifier: TerminologyExtractor,
    min_term_frequency: int,
) -> "Tuple[Dict[str, List[str]], Dict[str, Dict[str, Any]]]":
    """Reconstruct the full-text layer's domain-assigned term vocabulary.
    Runs the same candidate filter and domain classification
    ``TerminologyExtractor.extract_terms`` applies (frequency >=
    ``min_term_frequency`` on the identical normalized token stream,
    candidate-term test, seed/pattern domain classification), so the
    domain-assigned term set — and its per-domain tallies — are provably
    the artifact's own extraction without recomputing contexts or
    entropies.

    Args:
        counts: Global token counts over the corpus (the same token
            stream ``extract_terms`` counts).
        classifier: ``TerminologyExtractor`` providing the public
            ``classify_term_domains`` and the candidate test.
        min_term_frequency: Minimum token frequency for term inclusion.

    Returns:
        ``(token_domains, tallies)``: ``token_domains`` maps each
        domain-assigned term to its sorted domain list; ``tallies`` maps
        each domain to the same ``{"term_count", "bridging_term_count",
        "total_frequency"}`` shape as :func:`_domain_term_counts`.
    """
    token_domains: Dict[str, List[str]] = {}
    tallies: Dict[str, Dict[str, Any]] = {}
    for token in sorted(counts):
        if counts[token] < min_term_frequency:
            continue
        # ``_is_candidate_term`` mirrors the extractor's candidate filter
        # (read-only use of its private helper: no public API exposes the
        # filter alone, and skipping it would mis-classify seed terms the
        # extractor never admitted, e.g. "ant").
        if not classifier._is_candidate_term(token):
            continue
        domains = classifier.classify_term_domains(token)
        if not domains:
            continue
        token_domains[token] = domains
        for domain in domains:
            entry = tallies.setdefault(
                domain,
                {"term_count": 0, "bridging_term_count": 0, "total_frequency": 0},
            )
            entry["term_count"] += 1
            entry["bridging_term_count"] += 1 if len(domains) > 1 else 0
            entry["total_frequency"] += counts[token]
    return token_domains, dict(sorted(tallies.items()))


def add_framing_analysis(
    artifact: Dict[str, Any],
    fulltexts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute anthropomorphic-framing proportions over the full texts.

    Metric: for every occurrence in the corpus of a domain-assigned term
    — the full-text layer's extracted terms (frequency >= the artifact's
    ``min_term_frequency``) classified into a canonical domain — the
    ±``FRAMING_CONTEXT_WINDOW``-token context window around the
    occurrence is evaluated with the public
    ``analysis.text_analysis.LinguisticFeatureExtractor.extract_framing_features``
    API.  A term context is a *framing match* when it contains at least
    one anthropomorphic framing pattern match.  Per domain,
    ``proportion`` = framing matches / term contexts and ``n_contexts`` =
    term occurrence contexts evaluated.  This is the occurrence-context
    analogue of the abstract layer's term-level
    ``anthropomorphic_proportion`` (fraction of a domain's terms that are
    anthropomorphic).

    The domain-assigned term set is reconstructed deterministically from
    the identical normalized token stream ``TerminologyExtractor``
    counts (``TextProcessor.process_text(text, lemmatize=False)``) and
    cross-checked against the artifact's ``domain_term_counts`` when that
    section is present, so a corpus other than the artifact's own raises
    instead of silently merging mismatched numbers.

    A term assigned to several domains contributes every occurrence to
    each of its domains (mirroring ``domain_term_counts``); the
    ``overall`` entry counts each occurrence once, so per-domain
    ``n_contexts`` sums to more than ``overall`` when bridging terms
    exist.  Deterministic; domains with no occurrence contexts are
    omitted — never zero-filled.

    Args:
        artifact: Full-text-layer artifact dict (read-only; returned
            copy carries the new section).
        fulltexts: Corpus records the artifact was built from; must not
            be empty.

    Returns:
        A copy of ``artifact`` with ``"framing"`` added:
        ``{"<domain>": {"proportion": float, "n_contexts": int}, ...,
        "overall": {"proportion": float, "n_contexts": int}}``.

    Raises:
        ValueError: If ``fulltexts`` is empty, or the reconstructed
            per-domain term tallies do not match the artifact's
            ``domain_term_counts``.
    """
    if not fulltexts:
        raise ValueError("add_framing_analysis requires a non-empty full-text corpus")

    min_term_frequency = int(artifact.get("min_term_frequency") or 20)
    processor = TextProcessor()
    classifier = TerminologyExtractor(text_processor=processor)

    # Pass 1 — global token counts over the exact stream the extractor
    # counts, so the reconstructed term set is the artifact's own.
    counts: Counter = Counter()
    for record in fulltexts:
        counts.update(processor.process_text(_document_text(record), lemmatize=False))

    token_domains, tallies = _framing_token_domains(
        counts, classifier, min_term_frequency
    )
    expected_counts = artifact.get("domain_term_counts") or {}
    if expected_counts and tallies != expected_counts:
        raise ValueError(
            "add_framing_analysis: reconstructed per-domain term counts do not "
            "match the artifact's domain_term_counts; the corpus passed is not "
            "the corpus the artifact was built from"
        )

    # Pass 2 — scan every domain-term occurrence context for framing
    # features via the public LinguisticFeatureExtractor API.
    feature_extractor = LinguisticFeatureExtractor()
    domain_contexts: Dict[str, int] = {}
    domain_framed: Dict[str, int] = {}
    overall_contexts = 0
    overall_framed = 0
    for record in fulltexts:
        tokens = processor.process_text(_document_text(record), lemmatize=False)
        n_tokens = len(tokens)
        for position, token in enumerate(tokens):
            domains = token_domains.get(token)
            if not domains:
                continue
            start = max(0, position - FRAMING_CONTEXT_WINDOW)
            end = min(n_tokens, position + FRAMING_CONTEXT_WINDOW + 1)
            context = " ".join(tokens[start:end])
            is_framed = (
                feature_extractor.extract_framing_features(context)[
                    "anthropomorphic_terms"
                ]
                > 0
            )
            for domain in domains:
                domain_contexts[domain] = domain_contexts.get(domain, 0) + 1
                if is_framed:
                    domain_framed[domain] = domain_framed.get(domain, 0) + 1
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

    merged = dict(artifact)
    merged["framing"] = framing
    return merged


def build_fulltext_analysis(
    fulltexts: List[Dict[str, Any]],
    min_term_frequency: int = 20,
    include_framing: bool = True,
) -> Dict[str, Any]:
    """Build the full-text-layer analysis artifact.

    Args:
        fulltexts: Corpus records (list of ``fulltexts.json`` entries);
            must not be empty.
        min_term_frequency: Minimum token frequency for term extraction.
            Higher than the abstract layer because full texts are much
            longer; keeps the entropy passes tractable.
        include_framing: Append the anthropomorphic-framing section
            (see :func:`add_framing_analysis`) as the final stage.

    Returns:
        Artifact dict: abstract-layer statistics sections (from
        ``build_statistical_analysis``) plus ``layer``, ``n_documents``,
        ``documents`` (per-document pmcid/doi/year/journal/license/token
        count), ``domain_term_counts``, and (by default) ``framing``.
        Deterministic.

    Raises:
        ValueError: If ``fulltexts`` is empty (the degenerate corpus is
            reported by the caller, never analyzed into a fabricated
            artifact).
    """
    if not fulltexts:
        raise ValueError(
            "build_fulltext_analysis requires a non-empty full-text corpus"
        )

    documents_meta: List[Dict[str, Any]] = []
    texts: List[str] = []
    for record in fulltexts:
        text = _document_text(record)
        texts.append(text)
        documents_meta.append(
            {
                "pmcid": record.get("pmcid", ""),
                "doi": record.get("doi", ""),
                "year": record.get("year"),
                "journal": record.get("journal", ""),
                "license": record.get("license", "unknown"),
                "token_count": len(_TOKEN_RE.findall(text)),
            }
        )

    # Terminology extraction over the full texts (public analysis API).
    extractor = TerminologyExtractor()
    terms = extractor.extract_terms(texts, min_frequency=min_term_frequency)

    # Statistics: identical frozen schema as the abstract-layer
    # statistical_analysis.json artifact (descriptives/cace/cace_terms/
    # pairwise/anova/corrections/skipped), computed via DomainAnalyzer's
    # public entropy APIs inside statistics_pipeline.
    statistics = build_statistical_analysis(terms, texts)

    artifact: Dict[str, Any] = {
        "layer": FULLTEXT_LAYER,
        "n_documents": len(fulltexts),
        "min_term_frequency": min_term_frequency,
        "documents": documents_meta,
        "domain_term_counts": _domain_term_counts(terms),
        **statistics,
    }
    # Final stage: anthropomorphic-framing proportions over the full texts
    # (optional; the merge path appends it to an existing artifact without
    # recomputing the statistics stages).
    if include_framing:
        artifact = add_framing_analysis(artifact, fulltexts)
    return artifact


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: analyze the harvested full-text corpus.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--corpus",
        type=Path,
        default=None,
        help="fulltexts corpus path: directory of fulltexts_NNNNN.json "
        "shards or a legacy single-file corpus (default: "
        "<project root>/data/fulltexts)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Artifact path (default: <project root>/output/data/fulltext_analysis.json)",
    )
    parser.add_argument(
        "--min-term-frequency",
        type=int,
        default=20,
        help="Minimum token frequency for term extraction",
    )
    parser.add_argument(
        "--merge-framing",
        action="store_true",
        help="Merge the anthropomorphic-framing section into the EXISTING "
        "artifact at --output without recomputing the terminology/entropy "
        "statistics stages (runs only the framing pass)",
    )
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    corpus_path = args.corpus or project_root / "data" / "fulltexts"
    output_path = args.output or project_root / "output" / "data" / "fulltext_analysis.json"

    if corpus_path.is_dir():
        fulltexts = load_fulltexts(corpus_path)
    else:
        fulltexts = json.loads(corpus_path.read_text(encoding="utf-8"))
    if args.merge_framing:
        if not output_path.exists():
            parser.error(
                f"--merge-framing requires an existing artifact at {output_path}"
            )
        artifact = json.loads(output_path.read_text(encoding="utf-8"))
        artifact = add_framing_analysis(artifact, fulltexts)
    else:
        artifact = build_fulltext_analysis(
            fulltexts, min_term_frequency=args.min_term_frequency
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote full-text analysis for {artifact['n_documents']} documents "
        f"to {output_path}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
