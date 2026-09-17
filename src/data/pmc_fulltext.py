"""PMC Open-Access full-text corpus harvesting (parallel analysis layer).

Harvests full-text articles from PubMed Central via the E-utilities
(esearch ``db=pmc`` + efetch ``db=pmc``) as a PARALLEL corpus layer: the
abstract corpus (``data/corpus/abstracts.json``) remains the headline
corpus; this module builds and documents the full-text layer stored in
``data/fulltexts/``.

Corpus record schema (``fulltexts.json`` is a JSON list of)::

    {
        "pmcid": "PMC13411904",
        "doi": "10.1371/journal.pone.0000001",
        "title": "...",
        "year": 2026,
        "journal": "PLOS One",
        "license": "http://creativecommons.org/licenses/by/4.0/",
        "abstract": "...",
        "body_text": "..."
    }
Reproduce the harvest from the project root::

    uv run python src/data/pmc_fulltext.py --target 500
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from http.client import IncompleteRead
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

__all__ = [
    "PMC_SEARCH_QUERY",
    "PMCFulltextHarvester",
    "SHARD_SIZE",
    "dedupe_by_pmcid",
    "is_relevant",
    "load_citation_counts",
    "load_corpus_pmcids",
    "load_fulltexts",
    "order_by_citation",
    "parse_article",
    "parse_fulltext_xml",
    "shard_filename",
    "write_corpus",
    "write_readme",
    "write_shard",
]

logger = logging.getLogger(__name__)

# ── Search query (recorded verbatim in data/fulltexts/README.md) ──────
# Ant / myrmecology / eusocial relevance terms restricted to the PMC
# open-access subset so every hit has a retrievable full text.
PMC_SEARCH_QUERY = (
    '("ant"[Title/Abstract] OR "ants"[Title/Abstract] '
    'OR "Formicidae"[Title/Abstract] OR "myrmecolog*"[Title/Abstract] '
    'OR "eusocial"[Title/Abstract] OR "eusociality"[Title/Abstract] '
    'OR "social insect"[Title/Abstract]) AND "open access"[Filter]'
)

# Relevance filter applied to parsed records: a record is kept only when
# its title/abstract/body contains one of these (word-boundary,
# case-insensitive) terms.  Guards against tangential PMC search hits.
RELEVANCE_TERMS: tuple = (
    r"\bants?\b",
    r"\bformicidae\b",
    r"\bmyrmecolog\w*\b",
    r"\beusocial(?:ity)?\b",
    r"\bsocial insects?\b",
    r"\bformicinae\b",
    r"\bmyrmicinae\b",
    r"\bdorylinae\b",
    r"\blinepithema\b",
    r"\bsolenopsis\b",
)

_RELEVANCE_RE = re.compile("|".join(RELEVANCE_TERMS), re.IGNORECASE)

CORPUS_FIELDS: tuple = (
    "pmcid",
    "doi",
    "title",
    "year",
    "journal",
    "license",
    "abstract",
    "body_text",
)


# ── Sharding (GitHub rejects blobs >100 MB) ──────────────────────────

# Maximum corpus records per shard file (~19 MB each at ~36 KB of body
# text per record).
SHARD_SIZE = 1000

# Shard filename glob (relative to the corpus directory).
SHARD_GLOB = "fulltexts_*.json"


def shard_filename(index: int) -> str:
    """Return the zero-padded shard filename for a 1-based index.

    Args:
        index: 1-based shard index.

    Returns:
        ``fulltexts_00001.json`` for index 1, and so on.

    Examples:
        >>> shard_filename(12)
        'fulltexts_00012.json'
    """
    return f"fulltexts_{index:05d}.json"


def shard_paths(data_dir: Path) -> List[Path]:
    """List shard files in a corpus directory in concatenation order.

    Args:
        data_dir: Corpus directory (``data/fulltexts``).

    Returns:
        Shard paths sorted by filename (numerical order == lexical
        order because of the zero padding).
    """
    return sorted(data_dir.glob(SHARD_GLOB))


def _atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically (tmp file + rename).

    Args:
        path: Destination file.
        text: Full file content.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def write_shard(path: Path, records: List[Dict[str, Any]]) -> None:
    """Write one shard file atomically.

    Args:
        path: Destination shard path.
        records: Corpus records for this shard (at most ``SHARD_SIZE``).
    """
    corpus = [
        {field: record.get(field) for field in CORPUS_FIELDS} for record in records
    ]
    _atomic_write_text(
        path, json.dumps(corpus, ensure_ascii=False, indent=1) + "\n"
    )


def read_shard(path: Path) -> List[Dict[str, Any]]:
    """Read one shard file.

    Args:
        path: Shard path.

    Returns:
        The shard's corpus records.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def load_fulltexts(data_dir: Path) -> List[Dict[str, Any]]:
    """Load the full-text corpus by concatenating shards in order.

    Frozen name: the pipeline layer loads the corpus through this
    helper, so it must not be renamed.

    Args:
        data_dir: Corpus directory containing ``fulltexts_NNNNN.json``
            shard files.

    Returns:
        All corpus records, shard 1 first.
    """
    records: List[Dict[str, Any]] = []
    for path in shard_paths(data_dir):
        records.extend(read_shard(path))
    return records


def load_corpus_pmcids(data_dir: Path, provenance_path: Path) -> set:
    """Collect every PMCID already present in the corpus.

    Reads provenance plus each shard's ``pmcid`` field (one shard in
    memory at a time), so an interrupted harvest can skip previously
    stored documents.

    Args:
        data_dir: Corpus directory with shard files.
        provenance_path: Provenance sidecar path.

    Returns:
        Set of PMCIDs (``PMC`` prefix) present anywhere in shards or
        provenance.
    """
    pmcids: set = set()
    for path in shard_paths(data_dir):
        for record in read_shard(path):
            if record.get("pmcid"):
                pmcids.add(record["pmcid"])
    if provenance_path.exists():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        for entry in provenance.values():
            if entry.get("pmcid"):
                pmcids.add(entry["pmcid"])
    return pmcids


def load_provenance(provenance_path: Path) -> Dict[str, Any]:
    """Load the provenance sidecar (empty mapping when absent).

    Args:
        provenance_path: Provenance sidecar path.

    Returns:
        Mapping ``sha256(body_text)`` -> provenance entry.
    """
    if not provenance_path.exists():
        return {}
    return json.loads(provenance_path.read_text(encoding="utf-8"))


def build_provenance(
    records: List[Dict[str, Any]],
    query: str,
    retrieved_at: str,
) -> Dict[str, Any]:
    """Build provenance entries for corpus records.

    Args:
        records: Corpus records.
        query: Verbatim search query recorded per document.
        retrieved_at: ISO-8601 retrieval timestamp.

    Returns:
        Mapping ``sha256(body_text)`` ->
        ``{pmcid, doi, query, retrieved_at}``.
    """
    provenance: Dict[str, Any] = {}
    for record in records:
        digest = hashlib.sha256(
            (record["body_text"] or "").encode("utf-8")
        ).hexdigest()
        provenance[digest] = {
            "pmcid": record["pmcid"],
            "doi": record["doi"],
            "query": query,
            "retrieved_at": retrieved_at,
        }
    return provenance


def order_by_citation(
    pmcids: List[str],
    cited_by: Dict[str, int],
) -> List[str]:
    """Order PMCIDs highest-cited first where citation counts are known.

    PMCIDs present in ``cited_by`` are sorted by descending count;
    unknown PMCIDs keep their original (esearch relevance) order after
    the known ones.

    Args:
        pmcids: Candidate PMCIDs in relevance order.
        cited_by: Mapping PMCID -> OpenAlex ``cited_by_count``.

    Returns:
        Reordered PMCID list.

    Examples:
        >>> order_by_citation(["PMC1", "PMC2"], {"PMC2": 5})
        ['PMC2', 'PMC1']
    """
    indexed = list(enumerate(pmcids))
    indexed.sort(
        key=lambda item: (
            0 if item[1] in cited_by else 1,
            -cited_by.get(item[1], 0),
            item[0],
        )
    )
    return [pmcid for _, pmcid in indexed]


def is_relevant(record: Dict[str, Any]) -> bool:
    """Return True when the record mentions a relevance term.

    Checked against the concatenated title/abstract/body text with
    word-boundary, case-insensitive matching so ``plant``/``antenna``
    never match while ``ant-mediated`` does.

    Args:
        record: Corpus record (at least ``title``; abstract/body optional).

    Returns:
        True if any relevance term occurs.
    """
    haystack = " ".join(
        str(record.get(field) or "") for field in ("title", "abstract", "body_text")
    )
    return bool(_RELEVANCE_RE.search(haystack))


def dedupe_by_pmcid(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop records whose PMCID was already seen, keeping first occurrence.

    Args:
        records: Corpus records.

    Returns:
        Deduplicated list preserving input order.
    """
    seen: set = set()
    unique: List[Dict[str, Any]] = []
    for record in records:
        pmcid = record.get("pmcid")
        if not pmcid or pmcid in seen:
            continue
        seen.add(pmcid)
        unique.append(record)
    return unique


# ── XML parsing (namespace-agnostic JATS handling) ────────────────────


def _local(tag: str) -> str:
    """Return the local name of a possibly namespaced XML tag."""
    return tag.rsplit("}", 1)[-1]


def _children(element: ET.Element, name: str) -> List[ET.Element]:
    """Direct children of ``element`` whose local tag name is ``name``."""
    return [child for child in element if _local(child.tag) == name]


def _first_descendant(element: ET.Element, *path: str) -> Optional[ET.Element]:
    """First descendant matching the local-name path, else None."""
    current: List[ET.Element] = [element]
    for name in path:
        next_level: List[ET.Element] = []
        for node in current:
            next_level.extend(_children(node, name))
        current = next_level
        if not current:
            return None
    return current[0]


def _descendants(element: ET.Element, name: str) -> List[ET.Element]:
    """All descendants (any depth) with the given local tag name."""
    return [node for node in element.iter() if _local(node.tag) == name]


def _text(element: Optional[ET.Element]) -> str:
    """Whitespace-normalized itertext of an element ('' when None)."""
    if element is None:
        return ""
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def _body_text(article: ET.Element) -> str:
    """Extract body text with markup stripped, paragraphs separated.

    Args:
        article: JATS ``<article>`` element.

    Returns:
        Paragraph texts joined by blank lines; ``""`` when no body.
    """
    body = _first_descendant(article, "body")
    if body is None:
        return ""
    paragraphs = [
        re.sub(r"\s+", " ", "".join(p.itertext())).strip()
        for p in _descendants(body, "p")
    ]
    if not paragraphs:
        # Degenerate body without <p> wrappers: fall back to itertext.
        paragraphs = [re.sub(r"\s+", " ", "".join(body.itertext())).strip()]
    return "\n\n".join(p for p in paragraphs if p)


def _article_ids(article: ET.Element) -> Dict[str, str]:
    """Map pub-id-type -> identifier for the article's ``article-id`` tags."""
    ids: Dict[str, str] = {}
    for element in _descendants(article, "article-id"):
        id_type = element.attrib.get("pub-id-type", "")
        value = _text(element)
        if id_type and value and id_type not in ids:
            ids[id_type] = value
    return ids


def _license_text(article: ET.Element) -> str:
    """Best-available license identifier for the article.

    Preference order: ``ali:license_ref`` URL, license element attributes
    (``license-type``/``content-type``), then the license paragraph text.
    Returns ``"unknown"`` when the article declares no license — the
    open-access filter makes this rare but it is reported honestly.
    """
    for license_el in _descendants(article, "license"):
        for ref in _descendants(license_el, "license_ref"):
            url = _text(ref)
            if url:
                return url
        for attr in ("license-type", "content-type", "specific-use"):
            value = license_el.attrib.get(attr)
            if value:
                return value
        text = _text(license_el)
        if text:
            return text[:200]
    return "unknown"


def parse_article(article: ET.Element) -> Dict[str, Any]:
    """Parse one JATS ``<article>`` element into a corpus record.

    Args:
        article: Parsed ``<article>`` element from an efetch ``db=pmc``
            response.

    Returns:
        Record dict with the ``CORPUS_FIELDS`` keys.  ``year`` is an int
        when a pub-date year is present, else ``None``.  Missing DOI maps
        to ``""``; a missing license maps to ``"unknown"``.
    """

    def first_any(element: ET.Element, name: str) -> Optional[ET.Element]:
        found = _descendants(element, name)
        return found[0] if found else None

    front = first_any(article, "front")
    if front is None:
        front = article
    ids = _article_ids(article)

    pub_date = first_any(front, "pub-date")
    year_text = _text(
        _first_descendant(pub_date if pub_date is not None else article, "year")
    )
    try:
        year: Optional[int] = int(year_text)
    except ValueError:
        year = None

    journal_title = _text(first_any(front, "journal-title"))
    if not journal_title:
        journal_title = _text(first_any(front, "journal-id"))

    return {
        "pmcid": ids.get("pmcid", ""),
        "doi": ids.get("doi", ""),
        "title": _text(first_any(front, "article-title")),
        "year": year,
        "journal": journal_title,
        "license": _license_text(article),
        "abstract": _text(first_any(front, "abstract")),
        "body_text": _body_text(article),
    }


def parse_fulltext_xml(xml_text: str) -> List[Dict[str, Any]]:
    """Parse an efetch ``db=pmc`` response into corpus records.

    Args:
        xml_text: Raw XML response (a ``pmc-articleset`` document or a
            bare ``<article>``).

    Returns:
        One record per ``<article>`` in document order.  Articles whose
        PMCID cannot be determined are skipped (they cannot be
        attributed or deduplicated).
    """
    root = ET.fromstring(xml_text)
    articles = _descendants(root, "article")
    if _local(root.tag) == "article":
        articles = [root]
    records: List[Dict[str, Any]] = []
    for article in articles:
        record = parse_article(article)
        if record["pmcid"]:
            records.append(record)
    return records


# ── Harvester ─────────────────────────────────────────────────────────


class PMCFulltextHarvester:
    """Harvest PMC open-access full texts over the E-utilities.

    Attributes:
        BASE_URL: E-utilities base URL (monkeypatched in tests).
        BATCH_SIZE: PMCIDs requested per efetch call.
        REQUEST_DELAY: Seconds to sleep between efetch batches.
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    BATCH_SIZE = 10
    REQUEST_DELAY = 0.5
    MAX_RETRIES = 3

    def __init__(
        self,
        tool: str = "ento-linguistics-fulltext",
        email: str = "daniel@activeinference.institute",
        delay: Optional[float] = None,
    ):
        """Store NCBI identification parameters.

        Args:
            tool: NCBI ``tool`` parameter identifying this harvester.
            email: NCBI ``email`` contact parameter.
            delay: Override for ``REQUEST_DELAY`` between batches.
        """
        self.tool = tool
        self.email = email
        self.delay = self.REQUEST_DELAY if delay is None else delay

    # ── HTTP plumbing ─────────────────────────────────────────────

    def _get(self, endpoint: str, params: Dict[str, Any]) -> str:
        """GET an E-utilities endpoint with retries and backoff.

        Args:
            endpoint: Script name appended to ``BASE_URL``
                (``"esearch.fcgi"``, ``"efetch.fcgi"``).
            params: Query parameters (tool/email added here).

        Returns:
            Response body as text.

        Raises:
            RuntimeError: After ``MAX_RETRIES`` failed attempts.
        """
        query = dict(params)
        query.setdefault("tool", self.tool)
        query.setdefault("email", self.email)
        url = f"{self.BASE_URL}{endpoint}?{urlencode(query)}"
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                request = Request(url, headers={"User-Agent": f"{self.tool}/1.0"})
                with urlopen(request, timeout=120) as response:
                    return response.read().decode("utf-8")
            except (HTTPError, URLError, TimeoutError, IncompleteRead) as exc:
                last_error = exc
                logger.warning(
                    "E-utilities request failed (attempt %d/%d): %s",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.delay * attempt * 2)
        raise RuntimeError(f"E-utilities request failed: {url} ({last_error})")

    # ── E-utilities operations ────────────────────────────────────

    def search_pmcids(self, query: str = PMC_SEARCH_QUERY, retmax: int = 600) -> List[str]:
        """Run esearch ``db=pmc`` ranked by relevance.

        Args:
            query: Verbatim PMC search query.
            retmax: Maximum number of PMCIDs to request.

        Returns:
            PMCIDs in relevance rank order.
        """
        payload = self._get(
            "esearch.fcgi",
            {
                "db": "pmc",
                "term": query,
                "retmax": retmax,
                "retmode": "json",
                "sort": "relevance",
            },
        )
        idlist = json.loads(payload).get("esearchresult", {}).get("idlist", [])
        return [f"PMC{pmcid}" for pmcid in idlist]

    def fetch_fulltext_batch(self, pmcids: List[str]) -> List[Dict[str, Any]]:
        """Fetch and parse one batch of full-text XML.

        Args:
            pmcids: PMCIDs for this efetch call (``BATCH_SIZE`` at most).

        Returns:
            Parsed corpus records for articles whose PMCID is stated in
            the response (the authoritative attribution source).
        """
        xml_text = self._get(
            "efetch.fcgi",
            {
                "db": "pmc",
                "id": ",".join(pmcid.removeprefix("PMC") for pmcid in pmcids),
                "retmode": "xml",
            },
        )
        return parse_fulltext_xml(xml_text)

    def harvest(
        self,
        query: str = PMC_SEARCH_QUERY,
        target: int = 500,
        retmax: int = 600,
    ) -> List[Dict[str, Any]]:
        """Search, fetch, filter, and deduplicate full-text records.

        Batches of ``BATCH_SIZE`` PMCIDs are fetched with
        ``REQUEST_DELAY`` pauses.  Records are kept only when their
        PMCID resolves, the article has a non-empty body, and the
        relevance filter passes; duplicates by PMCID are dropped.

        Args:
            query: Verbatim PMC search query.
            target: Stop once this many records are collected.
            retmax: esearch ``retmax`` (upper bound on candidates).

        Returns:
            At most ``target`` deduplicated, relevance-filtered records
            in esearch relevance order.

        Raises:
            RuntimeError: When the esearch call fails after retries.
        """
        pmcids = self.search_pmcids(query, retmax=retmax)
        logger.info("esearch returned %d candidate PMCIDs", len(pmcids))

        records: List[Dict[str, Any]] = []
        seen: set = set()
        for start in range(0, len(pmcids), self.BATCH_SIZE):
            if len(records) >= target:
                break
            batch = pmcids[start : start + self.BATCH_SIZE]
            try:
                batch_records = self.fetch_fulltext_batch(batch)
            except (RuntimeError, ET.ParseError) as exc:
                logger.warning("Skipping batch %s: %s", batch[0], exc)
                time.sleep(self.delay)
                continue
            for record in batch_records:
                pmcid = record["pmcid"]
                if (
                    pmcid not in seen
                    and record["body_text"]
                    and is_relevant(record)
                ):
                    seen.add(pmcid)
                    records.append(record)
            logger.info(
                "Progress: %d/%d records (batch at %s)", len(records), target, batch[0]
            )
            time.sleep(self.delay)
        return records[:target]

    def harvest_sharded(
        self,
        data_dir: Path,
        provenance_path: Path,
        query: str = PMC_SEARCH_QUERY,
        target: Optional[int] = None,
        retmax: int = 10000,
        cited_by: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """Resumable sharded harvest of the full candidate set.

        Skips PMCIDs already present in ``data_dir`` shards or
        ``provenance_path``, fetches the remaining candidates in
        batches (highest-cited first where citation counts are known,
        relevance order otherwise), and appends records to shard files
        of at most ``SHARD_SIZE`` records.  Every shard and the
        provenance sidecar are written atomically after each shard
        fill, so an interrupted run continues where it stopped and no
        partial file is ever left behind.

        Args:
            data_dir: Corpus directory holding shard files.
            provenance_path: Provenance sidecar path (single file).
            query: Verbatim search query recorded per document.
            target: Stop after this many NEW records; ``None`` harvests
                the entire candidate set.
            retmax: esearch ``retmax`` (upper bound on candidates).
            cited_by: Optional PMCID -> OpenAlex ``cited_by_count``
                map used to prioritize the fetch order.

        Returns:
            Summary mapping with ``candidates``, ``already_stored``,
            ``harvested``, ``shards``, ``failed_batches``.
        """
        data_dir.mkdir(parents=True, exist_ok=True)
        already = load_corpus_pmcids(data_dir, provenance_path)
        pmcids = self.search_pmcids(query, retmax=retmax)
        if cited_by:
            pmcids = order_by_citation(pmcids, cited_by)
        logger.info(
            "esearch returned %d candidate PMCIDs (%d already stored)",
            len(pmcids),
            len(already),
        )

        # Seed the write buffer from the tail shard (or the legacy
        # single-file corpus when no shards exist yet) so shards stay
        # full; ``pending`` is the partially-filled shard file to
        # overwrite on the first flush.
        shards = shard_paths(data_dir)
        pending: Optional[Path] = shards[-1] if shards else None
        if shards:
            buffer = read_shard(shards[-1])
        elif (data_dir / "fulltexts.json").exists():
            buffer = json.loads(
                (data_dir / "fulltexts.json").read_text(encoding="utf-8")
            )
            already.update(
                record["pmcid"] for record in buffer if record.get("pmcid")
            )
        else:
            buffer = []
        buffer_start = len(buffer)
        next_shard = len(shards)

        provenance = load_provenance(provenance_path)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        harvested = 0
        failed_batches = 0
        for start in range(0, len(pmcids), self.BATCH_SIZE):
            if target is not None and harvested >= target:
                break
            batch = pmcids[start : start + self.BATCH_SIZE]
            if all(pmcid in already for pmcid in batch):
                continue  # resume: nothing new in this batch, skip fetch
            try:
                batch_records = self.fetch_fulltext_batch(batch)
            except (RuntimeError, ET.ParseError) as exc:
                logger.warning("Skipping batch %s: %s", batch[0], exc)
                failed_batches += 1
                time.sleep(self.delay)
                continue
            new_records = []
            for record in batch_records:
                pmcid = record["pmcid"]
                if (
                    pmcid in already
                    or not record["body_text"]
                    or not is_relevant(record)
                ):
                    continue
                already.add(pmcid)
                new_records.append(record)
            if new_records:
                harvested += len(new_records)
                for digest, entry in build_provenance(
                    new_records, query, retrieved_at
                ).items():
                    provenance.setdefault(digest, entry)
                buffer.extend(new_records)
                while len(buffer) >= SHARD_SIZE:
                    chunk = buffer[:SHARD_SIZE]
                    buffer = buffer[SHARD_SIZE:]
                    if pending is not None:
                        path = pending
                        pending = None
                    else:
                        next_shard += 1
                        path = data_dir / shard_filename(next_shard)
                    write_shard(path, chunk)
                    _atomic_write_text(
                        provenance_path,
                        json.dumps(
                            provenance, ensure_ascii=False, indent=1,
                            sort_keys=True,
                        ) + "\n",
                    )
            logger.info(
                "Progress: %d/%d candidates fetched, %d new records "
                "(batch at %s)",
                start + len(batch),
                len(pmcids),
                harvested,
                batch[0],
            )
            time.sleep(self.delay)

        # Flush the tail only when it differs from the stored tail shard.
        if buffer and (len(buffer) != buffer_start or pending is None):
            if pending is not None:
                path = pending
            else:
                next_shard += 1
                path = data_dir / shard_filename(next_shard)
            write_shard(path, buffer)
        _atomic_write_text(
            provenance_path,
            json.dumps(
                provenance, ensure_ascii=False, indent=1, sort_keys=True
            ) + "\n",
        )
        summary = {
            "candidates": len(pmcids),
            "already_stored": len(already) - harvested,
            "harvested": harvested,
            "shards": [p.name for p in shard_paths(data_dir)],
            "failed_batches": failed_batches,
        }
        logger.info("Harvest complete: %s", summary)
        return summary



# ── Persistence ───────────────────────────────────────────────────────


def write_corpus(
    records: List[Dict[str, Any]],
    corpus_path: Path,
    provenance_path: Path,
    query: str = PMC_SEARCH_QUERY,
    retrieved_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Write the full-text corpus and its provenance sidecar.

    Args:
        records: Deduplicated corpus records.
        corpus_path: Destination ``fulltexts.json`` path (created).
        provenance_path: Destination ``provenance.json`` path (created).
        query: Verbatim search query recorded per document.
        retrieved_at: ISO-8601 retrieval timestamp; defaults to now (UTC).

    Returns:
        The provenance mapping ``sha256(body_text)`` ->
        ``{pmcid, doi, query, retrieved_at}`` that was written.
    """
    retrieved_at = retrieved_at or datetime.now(timezone.utc).isoformat()
    corpus = [{field: record.get(field) for field in CORPUS_FIELDS} for record in records]

    provenance = build_provenance(corpus, query, retrieved_at)

    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.write_text(
        json.dumps(corpus, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    provenance_path.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "Wrote %d full texts to %s (provenance: %s)",
        len(corpus),
        corpus_path,
        provenance_path,
    )
    return provenance


def load_citation_counts(
    provenance_path: Path,
    citation_metadata_path: Path,
) -> Dict[str, int]:
    """Map PMCID -> OpenAlex ``cited_by_count`` where DOI matching allows.

    ``citation_metadata.json`` is keyed by abstract SHA-256 and carries
    DOIs; PMCID/DOI pairs are only locally known from the provenance
    sidecar, so citation-ordered harvesting covers exactly those
    documents.  Unmatched candidates keep esearch relevance order.

    Args:
        provenance_path: Provenance sidecar (``pmcid``/``doi`` pairs).
        citation_metadata_path: OpenAlex enrichment sidecar (DOI ->
            ``cited_by_count``).

    Returns:
        Mapping PMCID -> cited_by_count for every matchable document.
    """
    if not citation_metadata_path.exists():
        return {}
    metadata = json.loads(citation_metadata_path.read_text(encoding="utf-8"))
    doi_counts = {
        entry["doi"]: entry.get("cited_by_count", 0)
        for entry in metadata.values()
        if entry.get("doi")
    }
    counts: Dict[str, int] = {}
    for entry in load_provenance(provenance_path).values():
        doi = entry.get("doi")
        pmcid = entry.get("pmcid")
        if doi and pmcid and doi in doi_counts:
            counts[pmcid] = doi_counts[doi]
    return counts


def _coverage_stats(data_dir: Path) -> Dict[str, Any]:
    """Compute corpus coverage statistics streaming over the shards.

    Args:
        data_dir: Corpus directory with shard files.

    Returns:
        Mapping with ``count``, ``body_chars``, ``years``,
        ``journals``, ``license_counts``.
    """
    count = 0
    body_chars = 0
    years: List[int] = []
    journals: set = set()
    license_counts: Dict[str, int] = {}
    for path in shard_paths(data_dir):
        for record in read_shard(path):
            count += 1
            body = record.get("body_text") or ""
            body_chars += len(body)
            if isinstance(record.get("year"), int):
                years.append(record["year"])
            journals.add(record.get("journal") or "unknown")
            license_counts[record.get("license") or "unknown"] = (
                license_counts.get(record.get("license") or "unknown", 0) + 1
            )
    return {
        "count": count,
        "body_chars": body_chars,
        "years": years,
        "journals": journals,
        "license_counts": license_counts,
    }


def write_readme(
    output_dir: Path,
    query: str = PMC_SEARCH_QUERY,
    summary: Optional[Dict[str, Any]] = None,
) -> Path:
    """Write ``README.md`` documenting the sharded harvested corpus.

    Records the search query verbatim, the applied filters, shard
    layout, resumability behaviour, coverage computed by streaming
    over the actual shards, and the reproduction command.

    Args:
        output_dir: Corpus directory receiving ``README.md``.
        query: Verbatim search query.
        summary: Optional harvest summary (``candidates``,
            ``harvested``, ``failed_batches``) from
            ``PMCFulltextHarvester.harvest_sharded``.

    Returns:
        The README path.
    """
    stats = _coverage_stats(output_dir)
    shards = [p.name for p in shard_paths(output_dir)]
    license_lines = "\n".join(
        f"- `{license}`: {count} documents"
        for license, count in sorted(
            stats["license_counts"].items(), key=lambda item: (-item[1], item[0])
        )
    )
    year_line = (
        f"{min(stats['years'])}–{max(stats['years'])}" if stats["years"] else "n/a"
    )
    shard_lines = "\n".join(f"- `{name}`" for name in shards) or "- (none yet)"
    summary_block = ""
    if summary:
        summary_block = (
            f"\nLast harvest run: {summary.get('harvested', 0)} new documents "
            f"from {summary.get('candidates', 0)} candidates "
            f"({summary.get('failed_batches', 0)} failed batches skipped).\n"
        )
    readme = f"""# PMC Open-Access Full-Text Corpus (parallel layer)

Parallel analysis layer harvested from PubMed Central via the
E-utilities; the abstract corpus (`data/corpus/abstracts.json`) remains
the headline corpus.

## Files

- `fulltexts_NNNNN.json` — shard files, at most {SHARD_SIZE} records
  each (~39 MB at full-text length), holding JSON lists of full-text
  records (`pmcid`, `doi`, `title`, `year`, `journal`, `license`,
  `abstract`, `body_text`).  Concatenation order is the filename
  order:

{shard_lines}

- `provenance.json` — single sidecar mapping `sha256(body_text)` to
  `{{pmcid, doi, query, retrieved_at}}`.
- `README.md` — this document.

## Search query (verbatim)

```
{query}
```

Applied against `esearch db=pmc` with `retmode=json`,
`sort=relevance`, `retmax=10000`, and the project's NCBI `tool`/`email`
identification.  The `open access[Filter]` clause restricts hits to the
PMC open-access subset, so every hit has a retrievable full text.

## Filters

1. esearch relevance ranking over `{query}`; harvest order prioritizes
   documents with a locally matchable OpenAlex `cited_by_count`
   (highest cited first), relevance order otherwise.
2. `efetch db=pmc retmode=xml` in batches of
   {PMCFulltextHarvester.BATCH_SIZE} PMCIDs, spaced
   {PMCFulltextHarvester.REQUEST_DELAY}s apart (NCBI politeness).
3. Record kept only when: PMCID resolves in the response, the article
   has a non-empty body, and a word-boundary relevance term
   (ant/ants, Formicidae, myrmecology*, eusocial/eusociality,
   social insects, Formicinae, Myrmicinae, Dorylinae, Linepithema,
   Solenopsis) occurs in title/abstract/body.
4. Duplicates dropped by PMCID (first occurrence kept).
5. Target: every candidate from the relevance esearch (no cap).

## Sharding and resumability

- Shards hold at most {SHARD_SIZE} records (GitHub rejects blobs
  >100 MB).  Each shard and the provenance sidecar are written
  atomically (tmp file + rename) after every shard fill.
- The harvester skips any PMCID already present in the shards or
  provenance, so an interrupted run resumes where it stopped:

```bash
uv run python src/data/pmc_fulltext.py
```

- Load the whole corpus in order with the frozen helper:

```python
from data.pmc_fulltext import load_fulltexts
records = load_fulltexts(Path("data/fulltexts"))
```
{summary_block}
## Coverage ({stats['count']} documents)

- Publication years: {year_line}
- Distinct journals: {len(stats['journals'])}
- Body text: {stats['body_chars']:,} characters
- License coverage:

{license_lines}

The analysis layer is built separately:

```bash
uv run python src/pipeline/fulltext_pipeline.py
```
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "README.md"
    _atomic_write_text(path, readme)
    return path


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: harvest the PMC full-text corpus into shards.

    Resumable: existing shard PMCIDs are skipped; re-running continues an
    interrupted harvest.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--target",
        type=int,
        default=None,
        help="Stop after this many NEW records (default: all candidates)",
    )
    parser.add_argument(
        "--retmax",
        type=int,
        default=10000,
        help="esearch candidate cap (default: 10000, the full set)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Corpus directory (default: <project root>/data/fulltexts)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    project_root = Path(__file__).resolve().parents[2]
    output_dir = args.output_dir or project_root / "data" / "fulltexts"
    provenance_path = output_dir / "provenance.json"
    harvester = PMCFulltextHarvester()
    summary = harvester.harvest_sharded(
        output_dir,
        provenance_path,
        target=args.target,
        retmax=args.retmax,
        cited_by=load_citation_counts(
            provenance_path,
            project_root / "data" / "corpus" / "citation_metadata.json",
        ),
    )
    write_readme(output_dir, query=PMC_SEARCH_QUERY, summary=summary)
    total = sum(len(read_shard(p)) for p in shard_paths(output_dir))
    legacy = output_dir / "fulltexts.json"
    if legacy.exists() and shard_paths(output_dir):
        legacy.unlink()
        logger.info("Removed legacy fulltexts.json (migrated into shards)")
    print(f"Harvested {summary['harvested']} new; {total} total in {output_dir}")
    return 0



if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
