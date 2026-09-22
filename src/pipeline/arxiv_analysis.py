"""arXiv preprint layer analysis (unprocessed corpus layer #1).

Runs the shared Ento-Linguistic stack over the 56 arXiv preprint
abstracts in ``data/corpus/arxiv_records.json`` and writes the
``data/corpus/arxiv_analysis.json`` artifact.  The artifact mirrors the
frozen statistical schema of the abstract layer
(``statistical_analysis.json``) and the full-text layer
(``fulltext_analysis.json``) exactly: ``descriptives``/``cace``/
``cace_terms``/``pairwise``/``anova``/``corrections``/``skipped`` —
computed by ``pipeline.statistics_pipeline.build_statistical_analysis``
— plus the layer markers ``layer``/``n_documents``/``documents``/
``min_term_frequency``/``domain_term_counts`` and the
occurrence-context ``framing`` section.

Machinery reuse (documented contract):

- Statistics: ``build_statistical_analysis(terms, texts)`` is imported
  from ``pipeline.statistics_pipeline`` — its signature (extracted
  terms + source texts) fits the arXiv layer directly, so no
  domain-level re-implementation is needed here.  The DOMAIN-level
  APIs (``DomainAnalyzer.iter_domain_term_entropies``,
  ``quantify_ambiguity_metrics``) are exercised inside it.
- Framing: ``add_framing_analysis`` and its deterministic
  vocabulary-reconstruction helpers are imported from
  ``pipeline.fulltext_pipeline`` and run over the arXiv records
  (title + abstract, assembled by the shared ``_document_text`` —
  arXiv records carry no ``body_text`` field, so the text surface is
  title + abstract for both extraction and framing).  The framing
  scan uses the public
  ``analysis.text_analysis.LinguisticFeatureExtractor
  .extract_framing_features`` API internally.

Degenerate statistics (n=56 abstracts, small domains): comparisons
whose per-domain groups hold fewer than 2 valid per-term entropies are
recorded in the artifact's ``skipped`` list by
``build_statistical_analysis`` — never fabricated as zeros.  Domains
with no occurrence contexts are omitted from ``framing``.

Determinism: pure text/token/statistics arithmetic over sorted
serialization; re-running on an unchanged corpus reproduces the file
byte-for-byte (the ``generated`` timestamp excepted).  No ``output/``
writes: the artifact lands in ``data/corpus/``.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from analysis.term_extraction import TerminologyExtractor
from pipeline.fulltext_pipeline import (
    _document_text,
    _domain_term_counts,
    add_framing_analysis,
)
from pipeline.statistics_pipeline import build_statistical_analysis

__all__ = [
    "ARXIV_LAYER",
    "ARTIFACT_NAME",
    "DEFAULT_MIN_TERM_FREQUENCY",
    "load_arxiv_records",
    "build_arxiv_analysis",
    "main",
]

logger = logging.getLogger(__name__)

#: Layer marker stored in the artifact.
ARXIV_LAYER = "arxiv"

#: Artifact filename written next to the corpus records.
ARTIFACT_NAME = "arxiv_analysis.json"

#: Minimum token frequency for term extraction.  Abstracts are short
#: (single paragraphs), so the threshold is far below the full-text
#: layer's 20; with 56 abstracts a term must recur across documents to
#: be admitted, which keeps the entropy passes bounded.
DEFAULT_MIN_TERM_FREQUENCY = 2

# Word-boundary token pattern for per-document token counts (matches
# the full-text layer's convention).
_TOKEN_RE = re.compile(r"\w+")


def load_arxiv_records(path: Path) -> List[Dict[str, Any]]:
    """Load arXiv corpus records in file order.

    Args:
        path: Path to ``arxiv_records.json`` (a list of records with
            ``arxiv_id``, ``title``, ``abstract`` fields).

    Returns:
        The record list.

    Raises:
        ValueError: If the file does not contain a JSON list.
    """
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(
            f"arXiv records file {path} must contain a JSON list"
        )
    return records


def build_arxiv_analysis(
    records: List[Dict[str, Any]],
    min_term_frequency: int = DEFAULT_MIN_TERM_FREQUENCY,
    include_framing: bool = True,
) -> Dict[str, Any]:
    """Build the arXiv-layer analysis artifact.

    Args:
        records: Corpus records from ``data/corpus/arxiv_records.json``
            (``arxiv_id``, ``title``, ``abstract`` fields); must not be
            empty.
        min_term_frequency: Minimum token frequency for term extraction
            (abstracts are short, so the default is low).
        include_framing: Append the anthropomorphic-framing section
            (see ``pipeline.fulltext_pipeline.add_framing_analysis``)
            as the final stage.

    Returns:
        Artifact dict with the frozen statistical sections
        (``descriptives``/``cace``/``cace_terms``/``pairwise``/
        ``anova``/``corrections``/``skipped``) plus ``layer``,
        ``n_documents``, ``documents`` (per-record metadata),
        ``min_term_frequency``, ``domain_term_counts`` and (by default)
        ``framing``.  Deterministic.

    Raises:
        ValueError: If ``records`` is empty.
    """
    if not records:
        raise ValueError("build_arxiv_analysis requires a non-empty record list")

    documents_meta: List[Dict[str, Any]] = []
    texts: List[str] = []
    for record in records:
        text = _document_text(record)
        texts.append(text)
        documents_meta.append(
            {
                "arxiv_id": record.get("arxiv_id", ""),
                "doi": record.get("doi"),
                "title": record.get("title", ""),
                "primary_category": record.get("primary_category", ""),
                "published": record.get("published"),
                "token_count": len(_TOKEN_RE.findall(text)),
            }
        )

    # Terminology extraction over the abstracts (public analysis API).
    extractor = TerminologyExtractor()
    terms = extractor.extract_terms(texts, min_frequency=min_term_frequency)

    # Statistics: identical frozen schema as the abstract-layer
    # statistical_analysis.json artifact (descriptives/cace/cace_terms/
    # pairwise/anova/corrections/skipped).  The statistics_pipeline
    # signature (terms + texts) fits the arXiv layer directly, so the
    # DOMAIN-level entropy/ambiguity APIs are exercised inside it.
    statistics = build_statistical_analysis(terms, texts, layer=ARXIV_LAYER)

    artifact: Dict[str, Any] = {
        "layer": ARXIV_LAYER,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "records": "data/corpus/arxiv_records.json",
            "harvester": "arXiv API (preprint layer)",
            "text_surface": "title + abstract per record",
            "n_documents": len(records),
            "vocabulary_source": (
                "analysis.term_extraction.TerminologyExtractor.DOMAIN_SEEDS"
            ),
        },
        "n_documents": len(records),
        "min_term_frequency": min_term_frequency,
        "documents": documents_meta,
        "domain_term_counts": _domain_term_counts(terms),
        **statistics,
    }
    # Final stage: anthropomorphic-framing proportions over the abstract
    # occurrence contexts (public LinguisticFeatureExtractor API inside
    # the shared full-text helper).
    if include_framing:
        artifact = add_framing_analysis(artifact, records)
    return artifact


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: write ``data/corpus/arxiv_analysis.json``.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--records",
        type=Path,
        default=None,
        help=(
            "arXiv records path "
            "(default: <project root>/data/corpus/arxiv_records.json)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Artifact path "
            "(default: <project root>/data/corpus/arxiv_analysis.json)"
        ),
    )
    parser.add_argument(
        "--min-term-frequency",
        type=int,
        default=DEFAULT_MIN_TERM_FREQUENCY,
        help=(
            "Minimum token frequency for term extraction "
            f"(default: {DEFAULT_MIN_TERM_FREQUENCY})"
        ),
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    project_root = Path(__file__).resolve().parents[2]
    records_path = args.records or project_root / "data" / "corpus" / "arxiv_records.json"
    output = args.output or project_root / "data" / "corpus" / ARTIFACT_NAME

    records = load_arxiv_records(records_path)
    artifact = build_arxiv_analysis(records, min_term_frequency=args.min_term_frequency)
    logger.info(
        "Analyzed %d arXiv records: %d extracted-term domains, "
        "%d pairwise tests, %d skipped comparisons",
        artifact["n_documents"],
        len(artifact["domain_term_counts"]),
        len(artifact["pairwise"]),
        len(artifact["skipped"]),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(output)
    logger.info("Wrote artifact %s", output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
