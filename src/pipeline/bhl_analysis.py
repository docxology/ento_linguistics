"""Era-stratified term-usage analysis over the BHL historical layer.

Consumes the ``data/bhl`` corpus shards produced by
``src/data/bhl_corpus.py`` and computes, for each era bucket
(1850-1899, 1900-1949, 1950-1970), normalized term frequencies (per
10k tokens) for the six canonical Ento-Linguistic domain
vocabularies.  The result is written to
``data/bhl/era_term_usage.json`` as::

    {"layer": "bhl_historical", "generated": ..., "source": {...},
     "eras": {era: {"documents", "tokens", "terms_per_10k",
                    "domains_per_10k", "extraction", "entropy",
                    "framing"}},
     "terms": {term: {"era_1850_1899": count, "era_1900_1949": count,
                      "era_1950_1970": count, "domains": [...],
                      "total": n}},
     "skipped": [{kind, era?, reason}, ...]}

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
   decimals.  Zero-count terms are kept (absence is a literal
   corpus observation, not proof of historical nonexistence; e.g. ``haplodiploidy`` in 1850-1899).  Eras with no
   documents report zero tokens and zero frequencies.

Determinism: pure string/token arithmetic, no randomness, sorted
serialization; re-running on an unchanged corpus reproduces the file
byte-for-byte (the ``generated`` timestamp excepted).

Expanded schema (full linguistic stack, per era)
------------------------------------------------
Beyond the per-10k frequencies above, ``build_artifact`` runs the
stack per era over all stored documents by default; an explicit development
character budget selects a disclosed whole-document subset:

1. **Extraction** — ``TerminologyExtractor`` over
   :func:`clean_ocr_text` output with ``min_frequency=2``
   (``OCR_MIN_TERM_FREQUENCY``): single occurrences in OCR text are
   dominated by scanning flukes, so the guard excludes them.  The
   section records ``n_terms``, ``min_frequency`` and the per-domain
   term tallies (same shape as the full-text layer's
   ``domain_term_counts``).
2. **Entropy** — per-term semantic entropy via the public
   ``DomainAnalyzer.quantify_ambiguity_metrics`` API, bounded to the
   top ``ENTROPY_TOP_TERMS`` (20) most frequent extracted terms per
   era (documented bounded fraction: entropy is TF-IDF -> KMeans ->
   Shannon over sentence contexts, infeasible over the full multi-gigabyte
   OCR scan).  Only terms with ``status == "ok"`` (enough usable
   sentence contexts) report a value; excluded terms are counted in
   ``n_excluded``, never folded in as 0.0.  Per-domain means are
   computed over the same valid terms.
3. **Framing** — occurrence-context anthropomorphic-framing
   proportions (same shape and semantics as the full-text layer's
   ``framing`` section): every occurrence of a domain-assigned term is
   evaluated with the public
   ``analysis.text_analysis.LinguisticFeatureExtractor
   .extract_framing_features`` API over a +-``FRAMING_CONTEXT_WINDOW``
   (3)-token window.  The domain-assigned term vocabulary is
   reconstructed from the identical token stream
   ``TerminologyExtractor`` counts and cross-checked against the era
   extraction's per-domain tallies (mismatch raises).

Degenerate eras omit honestly: an era with no documents contributes no
``extraction``/``entropy``/``framing`` sections and is recorded in the
artifact's ``skipped`` list; an era whose bounded entropy sample
yields no valid entropies omits the term/domain maps (exclusion
counts remain).

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
import os
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from analysis.domain_analysis import DomainAnalyzer
from analysis.term_extraction import Term, TerminologyExtractor
from analysis.text_analysis import TextProcessor
from pipeline.fulltext_pipeline import (
    _domain_term_counts,
    _framing_token_domains,
    _framing_worker_init,
    _framing_count_tokens_task,
    _framing_contexts_task,
)
from core.parallel import map_ordered
__all__ = [
    "ERA_KEYS",
    "ARTIFACT_NAME",
    "OCR_MIN_TERM_FREQUENCY",
    "ENTROPY_TOP_TERMS",
    "normalize_text",
    "clean_ocr_text",
    "tokenize",
    "domain_vocabularies",
    "analyze_eras",
    "analyze_era_stack",
    "build_artifact",
    "load_corpus_records_for_analysis",
    "main",
]

#: Minimum per-era token frequency for the extraction/entropy/framing
#: stack.  Single occurrences in OCR text are dominated by scanning
#: flukes, so the guard excludes them.
OCR_MIN_TERM_FREQUENCY = 2

#: Bounded entropy pass: per-term semantic entropy is evaluated for at
#: most this many most-frequent extracted terms per era (documented
#: bounded term sample over the complete era corpus by default).
ENTROPY_TOP_TERMS = 20

# The complete OCR layer exceeds 2 GB. Full-corpus literal frequencies
# and the computational stack are streamed over every document by default.
# An explicit development cap selects complete documents with coverage metadata.
STACK_CHARACTER_BUDGET = 10_000_000


def stack_character_budget() -> Optional[int]:
    """Return the explicit development cap, or None for the full corpus."""
    value = os.environ.get("BHL_STACK_CHARACTER_BUDGET")
    budget = int(value) if value else None
    if budget is not None and budget <= 0:
        raise ValueError("BHL_STACK_CHARACTER_BUDGET must be a positive integer")
    return budget

logger = logging.getLogger(__name__)

#: Era buckets, canonical order (must match ``bhl_corpus.ERA_BOUNDS``).
ERA_KEYS: Tuple[str, ...] = (
    "era_1850_1899",
    "era_1900_1949",
    "era_1950_1970",
)

#: Artifact filename written next to the corpus shards.
ARTIFACT_NAME = "era_term_usage.json"

#: OCR speck tokens: standalone digit runs (page/plate numbers) and
#: single letters (roman-numeral folios, stray glyphs).  Domain seed
#: terms are >=2 alphabetic characters, so these tokens carry no
#: vocabulary signal.  Lookarounds keep digits/letters inside words
#: and hyphenated compounds intact.
_OCR_NOISE_TOKEN_RE = re.compile(r"(?<![\w-])(?:\d[\d.,:;%]*|[A-Za-z])(?![\w-])")


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


def clean_ocr_text(text: str) -> str:
    """Normalize OCR text for the extraction/entropy/framing stack.

    OCR noise handling (documented deterministic procedure):

    1. :func:`normalize_text`: NFC-fold, lowercase, join hyphenated
       line breaks, collapse whitespace.
    2. Drop OCR speck tokens matched by ``_OCR_NOISE_TOKEN_RE``:
       standalone digit runs (page/plate numbers, dates used as
       folios) and single letters (roman-numeral folios, stray
       glyphs).  Every domain seed term is at least two alphabetic
       characters long, so these tokens carry no vocabulary signal;
       lookarounds keep letters/digits inside words (``iiv``, ``x1a``)
       and hyphenated compounds (``x-ray``) intact.

    Args:
        text: Raw OCR ``full_text`` of one corpus record.

    Returns:
        Cleaned text used by the per-era stack (extraction, entropy,
        framing).  The per-10k frequency pass keeps using
        :func:`normalize_text` unchanged (backward compatible).
    """
    normalized = normalize_text(text)
    cleaned = _OCR_NOISE_TOKEN_RE.sub(" ", normalized)
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


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


def _count_terms(tokens: List[str], vocabulary: Dict[str, Tuple[str, ...]]) -> Dict[str, int]:
    """Count the same non-overlapping phrase matches in one token pass."""
    by_first: Dict[str, List[Tuple[str, Tuple[str, ...]]]] = {}
    for name, phrase in vocabulary.items():
        if phrase:
            by_first.setdefault(phrase[0], []).append((name, phrase))
    counts: Counter = Counter()
    ends: Dict[str, int] = {}
    for position, token in enumerate(tokens):
        for name, phrase in by_first.get(token, ()):
            if position < ends.get(name, 0):
                continue
            if tuple(tokens[position:position + len(phrase)]) == phrase:
                counts[name] += 1
                ends[name] = position + len(phrase)
    return {name: counts[name] for name in vocabulary}


def select_stack_records(records: List[Dict[str, Any]],
                         character_budget: int = STACK_CHARACTER_BUDGET) -> List[Dict[str, Any]]:
    """Select whole documents evenly across shard order under a stated budget.

    Complete eras below the budget are retained. Oversize single documents
    are excluded, never truncated; no eligible documents raises.
    """
    if character_budget <= 0:
        raise ValueError("character_budget must be positive")
    if sum(len(r.get("full_text") or "") for r in records) <= character_budget:
        return records
    # Dyadic traversal covers the entire ordered era before filling gaps.
    order = []
    intervals = [(0, len(records))]
    while intervals:
        next_intervals = []
        for start, end in intervals:
            if start < end:
                midpoint = (start + end) // 2
                order.append(midpoint)
                next_intervals.extend(((start, midpoint), (midpoint + 1, end)))
        intervals = next_intervals
    selected = []
    used = 0
    for index in order:
        size = len(records[index].get("full_text") or "")
        if size and used + size <= character_budget:
            selected.append(index)
            used += size
    if not selected:
        raise ValueError("No whole BHL document fits the stack character budget")
    return [records[index] for index in sorted(selected)]


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
        for term, count in _count_terms(tokens, term_token_cache).items():
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


def analyze_era_stack(
    era_records: List[Dict[str, Any]],
    min_term_frequency: int = OCR_MIN_TERM_FREQUENCY,
    entropy_top_terms: int = ENTROPY_TOP_TERMS,
) -> Dict[str, Any]:
    """Run the full linguistic stack over one era's OCR texts.

    Stages (all deterministic):

    1. ``clean_ocr_text`` over each record's ``full_text``.
    2. ``TerminologyExtractor`` extraction with the
       ``min_term_frequency`` OCR guard.
    3. Bounded per-term semantic entropy (public
       ``DomainAnalyzer.quantify_ambiguity_metrics`` API) over the
       ``entropy_top_terms`` most frequent extracted terms (descending
       frequency, ties by term text ascending).
    4. Occurrence-context anthropomorphic-framing proportions via the
       public ``LinguisticFeatureExtractor.extract_framing_features``
       API; the domain-assigned term vocabulary is reconstructed from
       the identical token stream the extractor counts and
       cross-checked against stage 2's per-domain tallies.

    Args:
        era_records: Corpus records of one era (``full_text`` field).
        min_term_frequency: Minimum token frequency for extraction.
        entropy_top_terms: Bound on the entropy sample.

    Returns:
        ``{"extraction": {...}, "entropy": {...}|None,
        "framing": {...}|None, "skipped": [...]}``.  ``entropy`` /
        ``framing`` are ``None`` when the era is degenerate (no
        extracted terms, or no valid entropies / occurrence contexts);
        every omission carries a ``skipped`` entry.
    """
    cleaned = [clean_ocr_text(r.get("full_text") or "") for r in era_records]
    skipped: List[Dict[str, str]] = []

    # ── 1. Extraction (OCR-guarded) ──────────────────────────────────
    # Keep only document counters, not the full corpus token-position map.
    # The latter grows with every occurrence and exceeds memory on the
    # complete multi-gigabyte OCR layer. The candidate and classification
    # rules remain the canonical extractor's own rules.
    extractor = TerminologyExtractor()
    _framing_worker_init()
    counts: Counter = Counter()
    for counter in map_ordered(_framing_count_tokens_task, cleaned,
                               initializer=_framing_worker_init):
        counts.update(counter)
    terms = {
        name: Term(text=name, lemma=name, frequency=counts[name],
                   domains=extractor.classify_term_domains(name))
        for name in sorted(counts)
        if counts[name] >= min_term_frequency and extractor._is_candidate_term(name)
    }
    extraction: Dict[str, Any] = {
        "min_frequency": min_term_frequency,
        "n_terms": len(terms),
        "domains": _domain_term_counts(terms),
    }
    if not terms:
        reason = (
            f"no domain-assigned terms extracted at min_frequency="
            f"{min_term_frequency}; entropy and framing omitted"
        )
        skipped.append({"kind": "era_stack", "reason": reason})
        return {"extraction": extraction, "entropy": None, "framing": None, "skipped": skipped}

    # ── 2. Bounded per-term entropy ──────────────────────────────────
    ranked = sorted(terms.values(), key=lambda t: (-t.frequency, t.text))[
        :entropy_top_terms
    ]
    analyzer = DomainAnalyzer()
    metrics = analyzer.quantify_ambiguity_metrics(ranked, cleaned)
    scores = metrics.get("term_ambiguity_scores", {})
    per_term_entropy: Dict[str, float] = {}
    domain_values: Dict[str, List[float]] = {}
    for term in ranked:
        result = scores.get(term.text.lower())
        if not result or result.get("status") != "ok":
            continue  # insufficient contexts or error: excluded, not 0.0
        entropy = float(result["entropy_bits"])
        per_term_entropy[term.text] = round(entropy, 6)
        for domain in term.domains:
            domain_values.setdefault(domain, []).append(entropy)
    entropy: Optional[Dict[str, Any]] = {
        "bounded_to_top_terms": min(entropy_top_terms, len(ranked)),
        "n_terms_evaluated": len(ranked),
        "n_valid": len(per_term_entropy),
        "n_excluded": len(ranked) - len(per_term_entropy),
        "terms": dict(sorted(per_term_entropy.items())),
        "domains": {
            domain: round(sum(values) / len(values), 6)
            for domain, values in sorted(domain_values.items())
        },
    }
    if not per_term_entropy:
        entropy = None
        skipped.append(
            {
                "kind": "era_entropy",
                "reason": (
                    f"none of the top-{len(ranked)} terms had enough "
                    "sentence contexts for semantic entropy; per-term "
                    "entropies omitted (n_excluded recorded in extraction)"
                ),
            }
        )

    # ── 3. Framing proportions over occurrence contexts ──────────────
    framing = _era_framing_proportions(
        cleaned, terms, min_term_frequency, skipped, counts=counts
    )

    return {
        "extraction": extraction,
        "entropy": entropy,
        "framing": framing,
        "skipped": skipped,
    }


def _era_framing_proportions(
    cleaned_texts: List[str],
    terms: Dict[str, Any],
    min_term_frequency: int,
    skipped: List[Dict[str, str]],
    counts: Optional[Counter] = None,
) -> Optional[Dict[str, Any]]:
    """Compute anthropomorphic-framing proportions for one era.

    Mirrors ``pipeline.fulltext_pipeline.add_framing_analysis`` over
    BHL records (the shared helper assembles texts from
    title/abstract/body fields, which OCR records do not carry): the
    domain-assigned term vocabulary is reconstructed with the identical
    normalized token stream ``TerminologyExtractor`` counts and
    cross-checked against the extraction's per-domain tallies, then
    every domain-term occurrence is scanned with the public
    ``LinguisticFeatureExtractor.extract_framing_features`` API over a
    +-``FRAMING_CONTEXT_WINDOW``-token window.  A term assigned to
    several domains contributes every occurrence to each of them; the
    ``overall`` entry counts each occurrence once.

    Returns:
        ``{domain: {"proportion", "n_contexts"}, ..., "overall": {...}}``
        or ``None`` (with a ``skipped`` entry appended) when no
        domain-term occurrence context exists in the era.
    """
    processor = TextProcessor()
    classifier = TerminologyExtractor(text_processor=processor)
    if counts is None:
        counts = Counter()
        for text in cleaned_texts:
            counts.update(processor.process_text(text, lemmatize=False))
    token_domains, tallies = _framing_token_domains(
        counts, classifier, min_term_frequency
    )
    expected = _domain_term_counts(terms)
    if tallies != expected:
        raise ValueError(
            "_era_framing_proportions: reconstructed per-domain term counts "
            "do not match the era extraction; the token stream diverged from "
            "the extraction pass"
        )

    domain_contexts: Counter = Counter()
    domain_framed: Counter = Counter()
    overall_contexts = 0
    overall_framed = 0
    # Reuse the PMC layer's exact occurrence-context scanner. Results are
    # small counters merged in document order; token lists live per task.
    _framing_worker_init(token_domains)
    for contexts, framed, total, total_framed in map_ordered(
        _framing_contexts_task, cleaned_texts, initializer=_framing_worker_init,
        initargs=(token_domains,),
    ):
        domain_contexts.update(contexts)
        domain_framed.update(framed)
        overall_contexts += total
        overall_framed += total_framed

    if not overall_contexts:
        skipped.append(
            {
                "kind": "era_framing",
                "reason": (
                    "no domain-assigned term occurrence contexts in the "
                    "era; framing proportions omitted"
                ),
            }
        )
        return None
    proportions: Dict[str, Any] = {}
    for domain in sorted(domain_contexts):
        n_contexts = domain_contexts[domain]
        proportions[domain] = {
            "proportion": round(domain_framed.get(domain, 0) / n_contexts, 6),
            "n_contexts": n_contexts,
        }
    proportions["overall"] = {
        "proportion": round(overall_framed / overall_contexts, 6),
        "n_contexts": overall_contexts,
    }
    return proportions


def build_artifact(
    data_dir: Path,
    records: Optional[List[Dict[str, Any]]] = None,
    checkpoint_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Build full-era results, optionally resuming verified local checkpoints.

    Checkpoints bind corpus contents, source/resources and explicit bounds.
    The returned scientific schema is unchanged. No checkpoint is required
    for the public API; the manuscript pipeline supplies its recovery path.
    """
    from .bhl_artifact import build_artifact as build_checkpointed_artifact

    return build_checkpointed_artifact(data_dir, records, checkpoint_dir)


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
    parser.add_argument(
        "--checkpoint-dir", type=Path, default=None,
        help="Optional recovery directory for completed, content-bound eras",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    project_root = Path(__file__).resolve().parents[2]
    data_dir = args.data_dir or project_root / "data" / "bhl"
    output = args.output or data_dir / ARTIFACT_NAME

    artifact = build_artifact(data_dir, checkpoint_dir=args.checkpoint_dir)
    era_docs = {
        era: stats["documents"] for era, stats in artifact["eras"].items()
    }
    logger.info(
        "Analyzed %d documents across eras: %s",
        artifact["source"]["documents"],
        era_docs,
    )
    logger.info(
        "Full-stack sections: %d honest omissions recorded in 'skipped'",
        len(artifact.get("skipped", [])),
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
