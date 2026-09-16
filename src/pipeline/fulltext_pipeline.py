"""Full-text analysis pipeline (parallel PMC layer).

Builds ``output/data/fulltext_analysis.json`` — the full-text-layer
sibling of the abstract-layer statistical artifact
(``output/data/statistical_analysis.json``).  The artifact shape mirrors
the abstract layer exactly (``descriptives``/``cace``/``cace_terms``/
``pairwise``/``anova``/``corrections``/``skipped``) and adds the
parallel-layer markers:

- ``"layer": "fulltext"``,
- ``n_documents`` and per-document metadata with token counts,
- ``domain_term_counts`` per-domain extracted-term counts.

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
from pathlib import Path
from typing import Any, Dict, List, Optional

from analysis.term_extraction import TerminologyExtractor
from pipeline.statistics_pipeline import build_statistical_analysis

__all__ = [
    "FULLTEXT_LAYER",
    "build_fulltext_analysis",
    "main",
]

# Layer marker stored in every full-text artifact.
FULLTEXT_LAYER = "fulltext"

# Word-boundary token pattern for per-document token counts.
_TOKEN_RE = re.compile(r"\w+")


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


def build_fulltext_analysis(
    fulltexts: List[Dict[str, Any]],
    min_term_frequency: int = 20,
) -> Dict[str, Any]:
    """Build the full-text-layer analysis artifact.

    Args:
        fulltexts: Corpus records (list of ``fulltexts.json`` entries);
            must not be empty.
        min_term_frequency: Minimum token frequency for term extraction.
            Higher than the abstract layer because full texts are much
            longer; keeps the entropy passes tractable.

    Returns:
        Artifact dict: abstract-layer statistics sections (from
        ``build_statistical_analysis``) plus ``layer``, ``n_documents``,
        ``documents`` (per-document pmcid/doi/year/journal/license/token
        count), and ``domain_term_counts``.  Deterministic.

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
        help="fulltexts.json path (default: <project root>/data/fulltexts/fulltexts.json)",
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
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    corpus_path = args.corpus or project_root / "data" / "fulltexts" / "fulltexts.json"
    output_path = args.output or project_root / "output" / "data" / "fulltext_analysis.json"

    fulltexts = json.loads(corpus_path.read_text(encoding="utf-8"))
    artifact = build_fulltext_analysis(fulltexts, min_term_frequency=args.min_term_frequency)

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
