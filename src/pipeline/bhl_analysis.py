"""Era-stratified term-usage analysis over the BHL historical layer.

Consumes the ``data/bhl`` corpus shards produced by
``src/data/bhl_corpus.py`` and computes, for each era bucket
(1850-1899, 1900-1949, 1950-1970), normalized term frequencies (per
10k tokens) for the six canonical Ento-Linguistic domain
vocabularies.  The result is written to
``data/bhl/era_term_usage.json`` as::

    {"layer": "bhl_historical", "generated": ..., "source": {...},
     "eras": {era: {"documents", "tokens", "terms_per_10k",
                    "domains_per_10k"}},
     "terms": {term: {"era_1850_1899": count, "era_1900_1949": count,
                      "era_1950_1970": count, "domains": [...],
                      "total": n}}}

Normalized per-10k frequencies live under ``eras``; ``terms``
carries the raw per-era occurrence counts plus each term's domain
memberships.

Vocabulary source
-----------------
The canonical per-domain seed vocabularies are reused from
``analysis.term_extraction.TerminologyExtractor.DOMAIN_SEEDS``
(imported lazily; it is the project's single source of truth for the
six domains).  Matching is a documented deterministic procedure:

1. Normalize each document's ``full_text``: NFC-fold, lowercase, join
   hyphenated line breaks (``word-\\ncontinuation`` -> ``wordcontinuation``),
   collapse all whitespace to single spaces.
2. Tokenize into word tokens with
   ``[a-z]+(?:-[a-z]+)*`` (hyphenated compounds kept whole).
3. Vocabulary terms are matched as token sequences: single-word terms
   by token equality, multi-word terms (e.g. ``division of labor``,
   ``kin selection``) as exact consecutive token windows.  Matches are
   non-overlapping per term, counted per era.
4. Frequencies are ``count / era_tokens * 10000``, rounded to 4
   decimals.  Zero-count terms are kept (absence is historically
   meaningful, e.g. ``haplodiploidy`` in 1850-1899).  Eras with no
   documents report zero tokens and zero frequencies.

Determinism: pure string/token arithmetic, no randomness, sorted
serialization; re-running on an unchanged corpus reproduces the file
byte-for-byte (the ``generated`` timestamp excepted).

Known limitation (documented, deterministic): hyphenated spellings
such as ``super-organism`` do not match the vocabulary term
``superorganism``; OCR-era texts use both spellings, and counts are
literal-token counts by design.  NO ``output/`` writes: the artifact
lands in ``data/bhl/``; figure/token wiring belongs to the
integration wave.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "ERA_KEYS",
    "ARTIFACT_NAME",
    "normalize_text",
    "tokenize",
    "domain_vocabularies",
    "analyze_eras",
    "build_artifact",
    "load_corpus_records_for_analysis",
    "main",
]

logger = logging.getLogger(__name__)

#: Era buckets, canonical order (must match ``bhl_corpus.ERA_BOUNDS``).
ERA_KEYS: Tuple[str, ...] = (
    "era_1850_1899",
    "era_1900_1949",
    "era_1950_1970",
)

#: Artifact filename written next to the corpus shards.
ARTIFACT_NAME = "era_term_usage.json"

_TOKEN_RE = re.compile(r"[a-z]+(?:-[a-z]+)*")
_HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\s*\n\s*(\w)")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize OCR text for deterministic token matching.

    NFC-fold, lowercase, join hyphenated line breaks, collapse
    whitespace.

    Args:
        text: Raw OCR full text.

    Returns:
        Normalized text.
    """
    text = unicodedata.normalize("NFC", text).lower()
    text = _HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def tokenize(text: str) -> List[str]:
    """Split normalized text into word tokens (hyphenated kept whole).

    Args:
        text: Normalized text (see :func:`normalize_text`).

    Returns:
        Token list; empty for text with no word characters.
    """
    return _TOKEN_RE.findall(text.lower())


def _term_tokens(term: str) -> Tuple[str, ...]:
    """Tokenize one vocabulary term for window matching."""
    return tuple(tokenize(term))


def domain_vocabularies() -> Dict[str, Tuple[str, ...]]:
    """Return the canonical six-domain seed vocabularies.

    Reuses ``analysis.term_extraction.TerminologyExtractor.DOMAIN_SEEDS``
    (project-internal source of truth) with deterministic ordering.

    Returns:
        Mapping domain name -> tuple of vocabulary terms.
    """
    # Lazy import: keeps the module import-light and avoids pulling
    # the analysis package into harvest-only contexts.
    try:
        from analysis.term_extraction import TerminologyExtractor
    except (ImportError, ValueError):  # pragma: no cover - fallback path
        from src.analysis.term_extraction import TerminologyExtractor
    seeds = TerminologyExtractor.DOMAIN_SEEDS
    return {
        domain: tuple(sorted(terms))
        for domain, terms in seeds.items()
    }


def _count_term(tokens: List[str], term: Tuple[str, ...]) -> int:
    """Count non-overlapping occurrences of a term token window.

    Args:
        tokens: Document token list.
        term: Term token tuple (length >= 1).

    Returns:
        Non-overlapping match count.
    """
    span = len(term)
    if span == 0 or len(tokens) < span:
        return 0
    count = 0
    i = 0
    limit = len(tokens) - span + 1
    while i < limit:
        if tuple(tokens[i : i + span]) == term:
            count += 1
            i += span  # non-overlapping
        else:
            i += 1
    return count


def load_corpus_records_for_analysis(data_dir: Path) -> List[Dict[str, Any]]:
    """Load BHL corpus records in shard order.

    Args:
        data_dir: Corpus directory with ``bhl_shard_*.json`` files.

    Returns:
        Record list (empty when the corpus has not been harvested).
    """
    try:
        from data.bhl_corpus import load_corpus_records
    except (ImportError, ValueError):  # pragma: no cover - fallback path
        from src.data.bhl_corpus import load_corpus_records
    return load_corpus_records(data_dir)


def analyze_eras(
    records: List[Dict[str, Any]],
    vocabularies: Optional[Dict[str, Tuple[str, ...]]] = None,
) -> Dict[str, Any]:
    """Compute per-era term and domain frequencies over corpus records.

    Args:
        records: BHL corpus records (``era``, ``full_text`` fields).
        vocabularies: Domain -> terms mapping; defaults to
            :func:`domain_vocabularies`.

    Returns:
        ``{"eras": {...}, "terms": {...}}``:
        ``eras[era]`` holds ``documents``, ``tokens``,
        ``terms_per_10k`` (term -> per-10k frequency, 4 decimals) and
        ``domains_per_10k`` (domain -> summed member-term frequency);
        ``terms[term]`` holds per-era frequencies, the ``domains``
        list it belongs to, and its absolute ``total`` count.  All
        three canonical eras are always present.
    """
    if vocabularies is None:
        vocabularies = domain_vocabularies()

    # term -> domains; multi-domain terms appear once per membership.
    term_domains: Dict[str, List[str]] = {}
    term_token_cache: Dict[str, Tuple[str, ...]] = {}
    for domain, terms in vocabularies.items():
        for term in terms:
            term_domains.setdefault(term, [])
            if domain not in term_domains[term]:
                term_domains[term].append(domain)
            term_token_cache.setdefault(term, _term_tokens(term))

    eras: Dict[str, Dict[str, Any]] = {
        era: {
            "documents": 0,
            "tokens": 0,
            "terms_per_10k": {},
            "domains_per_10k": {},
        }
        for era in ERA_KEYS
    }
    term_counts: Dict[str, Dict[str, int]] = {
        term: {era: 0 for era in ERA_KEYS} for term in term_domains
    }

    for record in records:
        era = record.get("era")
        if era not in eras:
            continue  # defensive: corpus guarantees canonical eras
        tokens = tokenize(normalize_text(record.get("full_text") or ""))
        eras[era]["documents"] += 1
        eras[era]["tokens"] += len(tokens)
        seen_terms = set()
        for term, term_tokens in term_token_cache.items():
            if term in seen_terms:
                continue  # same term matched once per record
            seen_terms.add(term)
            count = _count_term(tokens, term_tokens)
            if count:
                term_counts[term][era] += count

    # Frequencies per 10k tokens, deterministic rounding.
    for era in ERA_KEYS:
        era_tokens = eras[era]["tokens"]
        freqs: Dict[str, float] = {}
        for term in sorted(term_counts):
            count = term_counts[term][era]
            freqs[term] = (
                round(count / era_tokens * 10000, 4) if era_tokens else 0.0
            )
        eras[era]["terms_per_10k"] = freqs
        domains_per_10k: Dict[str, float] = {}
        for domain, terms in sorted(vocabularies.items()):
            total = sum(freqs.get(term, 0.0) for term in terms)
            domains_per_10k[domain] = round(total, 4)
        eras[era]["domains_per_10k"] = domains_per_10k

    terms: Dict[str, Dict[str, Any]] = {}
    for term in sorted(term_counts):
        counts = term_counts[term]
        terms[term] = {
            **{era: round(counts[era], 4) for era in ERA_KEYS},
            "domains": sorted(term_domains[term]),
            "total": sum(counts.values()),
        }
    return {"eras": eras, "terms": terms}


def build_artifact(
    data_dir: Path,
    records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build the era-stratified artifact dict for the BHL corpus.

    Args:
        data_dir: Corpus directory with ``bhl_shard_*.json`` files.
        records: Pre-loaded records (loaded from ``data_dir`` when
            ``None``).

    Returns:
        Artifact dict: ``{"layer": "bhl_historical", "generated",
        "source", "eras", "terms"}``.
    """
    if records is None:
        records = load_corpus_records_for_analysis(data_dir)
    vocabulary_source = "analysis.term_extraction.TerminologyExtractor.DOMAIN_SEEDS"
    eras_terms = analyze_eras(records)
    return {
        "layer": "bhl_historical",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "data_dir": str(data_dir),
            "documents": len(records),
            "harvester": "src/data/bhl_corpus.py",
            "vocabulary_source": vocabulary_source,
            "matching": (
                "deterministic token-window matching over normalized "
                "(NFC, lowercased, hyphen-break-joined) OCR text; "
                "frequencies per 10k era tokens, 4 decimals"
            ),
        },
        **eras_terms,
    }


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: write ``data/bhl/era_term_usage.json``.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="BHL corpus directory (default: <project root>/data/bhl)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Artifact path (default: <data-dir>/era_term_usage.json)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    project_root = Path(__file__).resolve().parents[2]
    data_dir = args.data_dir or project_root / "data" / "bhl"
    output = args.output or data_dir / ARTIFACT_NAME

    artifact = build_artifact(data_dir)
    era_docs = {
        era: stats["documents"] for era, stats in artifact["eras"].items()
    }
    logger.info(
        "Analyzed %d documents across eras: %s",
        artifact["source"]["documents"],
        era_docs,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=1, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    tmp.replace(output)
    logger.info("Wrote artifact %s", output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
