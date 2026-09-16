"""arXiv preprint layer for the Ento-Linguistic corpus.

Harvests arXiv preprints via the existing :class:`~data.literature_mining.ArXivMiner`
(restricted to the ``q-bio.PE`` and ``nlin.AO`` categories) and stores them as a
**separate source layer** in ``data/corpus/arxiv_records.json``. Records are
deduplicated against the PubMed corpus (``abstracts.json`` + ``provenance.json``)
by DOI, normalized title, and normalized abstract prefix, and internally by
arXiv ID and normalized title.

A provenance sidecar (``arxiv_provenance.json``) maps the SHA-256 of each
abstract string to its arXiv identifiers and the originating query, mirroring
the convention used by ``provenance.json`` for the PubMed corpus.

The layer is intentionally **not merged** into ``abstracts.json``: PubMed
records and arXiv preprints are distinct sources with different metadata
coverage, and keeping them separate preserves per-source provenance.

Usage (from the project root)::

    python -m data.arxiv_corpus --target 100          # live harvest
    python -m data.arxiv_corpus --dry-run             # plan only, no writes
    python -m data.arxiv_corpus --target 150 --max-per-query 100
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    from .literature_mining import ArXivMiner, is_relevant_social_insect_text
except (ImportError, ValueError):  # pragma: no cover - direct-script fallback
    from data.literature_mining import ArXivMiner, is_relevant_social_insect_text

__all__ = [
    "ARXIV_QUERIES",
    "CORPUS_DIR",
    "EnrichedArXivMiner",
    "abstract_key",
    "build_record",
    "dedupe_against_pubmed",
    "harvest_arxiv",
    "load_pubmed_keys",
    "main",
    "normalize_title",
]

CORPUS_DIR = Path(__file__).resolve().parents[2] / "data" / "corpus"

#: Category-restricted arXiv queries, one per ento-linguistic topic.
#: ``cat:`` filters keep results inside quantitative biology (population &
#: evolutionary biology) and nonlinear sciences (adaptation & organization).
ARXIV_QUERIES: Dict[str, str] = {
    "ant_colonies": '(cat:q-bio.PE OR cat:nlin.AO) AND all:"ant colonies"',
    "eusociality": '(cat:q-bio.PE OR cat:nlin.AO) AND all:"eusociality"',
    "superorganisms": '(cat:q-bio.PE OR cat:nlin.AO) AND all:"superorganisms"',
    "collective_behavior": '(cat:q-bio.PE OR cat:nlin.AO) AND all:"collective behavior"',
    "stigmergy": '(cat:q-bio.PE OR cat:nlin.AO) AND all:"stigmergy"',
}

_ABSTRACT_KEY_CHARS = 100  # matches the PubMed corpus dedupe convention


def _utcnow() -> str:
    """Current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sleep(seconds: float) -> None:
    """Rate-limit hook (patchable in tests)."""
    if seconds > 0:
        time.sleep(seconds)


def normalize_title(title: str) -> str:
    """Lowercase and collapse whitespace in a title for dedupe comparisons.

    >>> normalize_title("  Colony  Organization\\tin Ants ")
    'colony organization in ants'
    """
    return re.sub(r"\s+", " ", title).strip().lower()


def abstract_key(abstract: str) -> str:
    """First N whitespace-normalized characters of an abstract (dedupe key).

    >>> abstract_key("The  Argentine ant is invasive.")
    'the argentine ant is invasive.'
    """
    return re.sub(r"\s+", " ", abstract).strip().lower()[:_ABSTRACT_KEY_CHARS]


class EnrichedArXivMiner(ArXivMiner):
    """ArXivMiner subclass that also captures fields the base parser drops.

    The base :meth:`ArXivMiner.search` returns ``Publication`` objects without
    the arXiv ID, primary category, or raw publication timestamp; this subclass
    parses the same Atom feed into full record dicts instead, reusing the base
    class's ``BASE_URL`` and error policy.
    """

    # arXiv's own extension namespace, distinct from the Atom 2005 namespace
    # used by the base class (primary_category lives here).
    AX_NS = {"ax": "http://arxiv.org/schemas/atom"}

    def search_full(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search arXiv and return raw record dicts with arXiv-specific fields.

        Args:
            query: arXiv API search query (may include ``cat:`` filters).
            max_results: Maximum number of entries to request.

        Returns:
            List of record dicts with keys ``arxiv_id``, ``doi``, ``title``,
            ``abstract``, ``primary_category``, ``published``, ``authors``.
            Empty list on network or parse errors (base-class error policy).

        Examples:
            >>> miner = EnrichedArXivMiner()  # doctest: +SKIP
            >>> records = miner.search_full('all:"ant colonies"', 10)  # doctest: +SKIP
        """
        url = (
            f"{self.BASE_URL}search_query={quote(query)}"
            f"&start=0&max_results={max_results}"
            f"&sortBy=submittedDate&sortOrder=descending"
        )
        try:
            with urlopen(
                Request(url, headers={"User-Agent": "Python-EntoLinguistic"})
            ) as response:
                content = response.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001 - mirrors base-class error policy
            self._log_error(f"Error searching arXiv: {exc}")
            return []

        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:
            self._log_error(f"Error parsing arXiv response: {exc}")
            return []

        ns = {"arxiv": "http://www.w3.org/2005/Atom"}
        records: List[Dict[str, Any]] = []
        for entry in root.findall("arxiv:entry", ns):
            record = self._parse_entry_full(entry, ns)
            if record is not None:
                records.append(record)
        return records

    def _parse_entry_full(
        self, entry: ET.Element, ns: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Parse one Atom ``<entry>`` into a record dict, or ``None``."""
        title_el = entry.find("arxiv:title", ns)
        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        if not title:
            return None

        authors = [
            name.text.strip()
            for author in entry.findall("arxiv:author", ns)
            for name in author.findall("arxiv:name", ns)
            if name is not None and name.text
        ]
        summary_el = entry.find("arxiv:summary", ns)
        abstract = (
            summary_el.text.strip()
            if summary_el is not None and summary_el.text
            else None
        )
        doi_el = entry.find("arxiv:doi", ns)
        if doi_el is None or not doi_el.text:
            doi_el = entry.find("ax:doi", self.AX_NS)
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

        arxiv_id: Optional[str] = None
        id_el = entry.find("arxiv:id", ns)
        if id_el is not None and id_el.text:
            match = re.search(r"arxiv\.org/abs/(.+?)\s*$", id_el.text.strip())
            if match:
                arxiv_id = re.sub(r"v\d+$", "", match.group(1))

        primary_category: Optional[str] = None
        pc_el = entry.find("ax:primary_category", self.AX_NS)
        if pc_el is not None and pc_el.get("term"):
            primary_category = pc_el.get("term")
        else:
            for cat_el in entry.findall("arxiv:category", ns):
                term = cat_el.get("term")
                if term:
                    primary_category = term
                    break

        published: Optional[str] = None
        pub_el = entry.find("arxiv:published", ns)
        if pub_el is not None and pub_el.text:
            published = pub_el.text.strip()

        return {
            "arxiv_id": arxiv_id,
            "doi": doi,
            "title": title,
            "abstract": abstract,
            "primary_category": primary_category,
            "published": published,
            "authors": authors,
        }

    def _log_error(self, message: str) -> None:
        """Log through the literature_mining module logger."""
        from data.literature_mining import logger

        logger.error(message)


def load_pubmed_keys(corpus_dir: Path) -> Dict[str, set]:
    """Load dedupe keys for the PubMed corpus.

    Reads ``abstracts.json`` (abstract strings) and ``provenance.json``
    (records keyed by abstract SHA-256 with ``doi``/``title``).

    Returns:
        Dict with sets: ``titles`` (normalized), ``dois`` (normalized),
        ``abstract_keys`` (normalized prefixes).
    """
    titles: set = set()
    dois: set = set()
    abstract_keys: set = set()

    abstracts_path = corpus_dir / "abstracts.json"
    if abstracts_path.exists():
        abstracts = json.loads(abstracts_path.read_text(encoding="utf-8"))
        for abstract in abstracts:
            if isinstance(abstract, str) and abstract.strip():
                abstract_keys.add(abstract_key(abstract))

    provenance_path = corpus_dir / "provenance.json"
    if provenance_path.exists():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        for record in provenance.get("records", {}).values():
            if record.get("doi"):
                dois.add(record["doi"].strip().lower())
            if record.get("title"):
                titles.add(normalize_title(record["title"]))

    return {"titles": titles, "dois": dois, "abstract_keys": abstract_keys}


def dedupe_against_pubmed(
    records: List[Dict[str, Any]], pubmed_keys: Dict[str, set]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split records into kept vs. duplicates of the PubMed corpus.

    A record is a duplicate if its DOI, normalized title, or normalized
    abstract prefix matches a PubMed record.

    Returns:
        ``(kept, duplicates)`` tuple of record lists.
    """
    kept: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []
    for record in records:
        doi = (record.get("doi") or "").strip().lower() or None
        title = normalize_title(record.get("title") or "")
        akey = abstract_key(record.get("abstract") or "")
        if (
            (doi and doi in pubmed_keys["dois"])
            or (title and title in pubmed_keys["titles"])
            or (akey and akey in pubmed_keys["abstract_keys"])
        ):
            duplicates.append(record)
        else:
            kept.append(record)
    return kept, duplicates


def build_record(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate and normalize a raw arXiv record dict.

    Returns ``None`` if the record lacks an arXiv ID, title, or abstract.
    """
    if not raw.get("arxiv_id") or not raw.get("title") or not raw.get("abstract"):
        return None
    return {
        "arxiv_id": raw["arxiv_id"],
        "doi": raw.get("doi"),
        "title": raw["title"],
        "abstract": raw["abstract"],
        "primary_category": raw.get("primary_category"),
        "published": raw.get("published"),
        "authors": list(raw.get("authors") or []),
    }


def harvest_arxiv(
    target: int = 100,
    max_per_query: int = 80,
    corpus_dir: Optional[Path] = None,
    miner: Optional[EnrichedArXivMiner] = None,
    query_sleep: float = 3.0,
    dry_run: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """Harvest arXiv preprints into ``arxiv_records.json`` (+ provenance).

    Resumable: arXiv IDs already present in ``arxiv_records.json`` are skipped,
    so re-running only fetches what is missing.

    Args:
        target: Target number of new (deduped) records to collect.
        max_per_query: ``max_results`` passed to each arXiv query.
        miner: Miner instance (defaults to :class:`EnrichedArXivMiner`).
        query_sleep: Seconds to sleep between queries (arXiv politeness).
        dry_run: If true, compute but do not write anything.

    Returns:
        ``(records, provenance, stats)`` where ``records`` is the full record
        list (existing + new), ``provenance`` the sidecar payload, and
        ``stats`` a summary with per-query kept/duplicate counts.
    """
    corpus_dir = Path(corpus_dir) if corpus_dir else CORPUS_DIR
    miner = miner or EnrichedArXivMiner()
    records_path = corpus_dir / "arxiv_records.json"
    provenance_path = corpus_dir / "arxiv_provenance.json"

    existing: List[Dict[str, Any]] = []
    existing_provenance_records: Dict[str, Dict[str, Any]] = {}
    if records_path.exists():
        existing = json.loads(records_path.read_text(encoding="utf-8"))
    if provenance_path.exists():
        prior = json.loads(provenance_path.read_text(encoding="utf-8"))
        existing_provenance_records = prior.get("records", {})
    seen_ids = {r["arxiv_id"] for r in existing}
    seen_titles = {normalize_title(r["title"]) for r in existing}
    seen_akeys = {abstract_key(r["abstract"]) for r in existing}

    pubmed_keys = load_pubmed_keys(corpus_dir)

    new_records: List[Dict[str, Any]] = []
    query_of: Dict[str, str] = {}  # arxiv_id -> originating query name
    query_stats: Dict[str, Dict[str, int]] = {}
    retrieved_at = _utcnow()

    for query_name, query in ARXIV_QUERIES.items():
        if len(new_records) >= target:
            break
        raw_results = miner.search_full(query, max_results=max_per_query)
        kept = 0
        dupes = 0
        for raw in raw_results:
            if len(new_records) >= target:
                break
            record = build_record(raw)
            if record is None:
                continue
            if not is_relevant_social_insect_text(
                record["title"] + " " + (record["abstract"] or "")
            ):
                continue
            # Internal dedupe (within this run and against existing records).
            if record["arxiv_id"] in seen_ids:
                dupes += 1
                continue
            ntitle = normalize_title(record["title"])
            akey = abstract_key(record["abstract"])
            if ntitle in seen_titles or akey in seen_akeys:
                dupes += 1
                continue
            # Dedupe against the PubMed corpus (DOI / title / abstract prefix).
            pubmed_kept, _pubmed_dupes = dedupe_against_pubmed([record], pubmed_keys)
            if not pubmed_kept:
                dupes += 1
                continue
            new_records.append(record)
            query_of[record["arxiv_id"]] = query_name
            seen_ids.add(record["arxiv_id"])
            seen_titles.add(ntitle)
            seen_akeys.add(akey)
            kept += 1
        query_stats[query_name] = {"kept": kept, "duplicates": dupes}
        _sleep(query_sleep)

    records = existing + new_records
    provenance = {
        "_note": (
            "Provenance for the arXiv preprint layer. Keys are SHA-256 of the "
            "exact abstract string in arxiv_records.json. arXiv records are a "
            "separate source layer and are NOT merged into abstracts.json."
        ),
        "retrieved_at": retrieved_at,
        "queries": dict(ARXIV_QUERIES),
        "query_stats": query_stats,
        "records": {
            **existing_provenance_records,
            **{
                hashlib.sha256(r["abstract"].encode("utf-8")).hexdigest(): {
                    "arxiv_id": r["arxiv_id"],
                    "doi": r["doi"],
                    "title": r["title"],
                    "primary_category": r["primary_category"],
                    "published": r["published"],
                    "query": query_of.get(r["arxiv_id"], "unknown"),
                    "retrieved_at": retrieved_at,
                }
                for r in new_records
            },
        },
    }
    stats = {
        "existing": len(existing),
        "new": len(new_records),
        "total": len(records),
        "query_stats": query_stats,
    }

    if not dry_run and new_records:
        corpus_dir.mkdir(parents=True, exist_ok=True)
        records_path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        provenance_path.write_text(
            json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return records, provenance, stats


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for the arXiv harvest layer."""
    parser = argparse.ArgumentParser(
        description="Harvest arXiv preprints into the Ento-Linguistic corpus."
    )
    parser.add_argument(
        "--target",
        type=int,
        default=100,
        help="Target number of new deduped records (default: 100).",
    )
    parser.add_argument(
        "--max-per-query",
        type=int,
        default=80,
        help="Max results per arXiv query (default: 80).",
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=None,
        help="Corpus directory (default: project data/corpus).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan the harvest without writing any files.",
    )
    args = parser.parse_args(argv)

    records, _provenance, stats = harvest_arxiv(
        target=args.target,
        max_per_query=args.max_per_query,
        corpus_dir=args.corpus_dir,
        dry_run=args.dry_run,
    )
    mode = "dry-run" if args.dry_run else "written"
    print(
        f"arXiv harvest [{mode}]: existing={stats['existing']} "
        f"new={stats['new']} total={stats['total']}"
    )
    for name, counts in stats["query_stats"].items():
        print(f"  {name}: kept={counts['kept']} duplicates={counts['duplicates']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
