"""Biodiversity Heritage Library historical full-text layer (1850-1970).

Grounds the manuscript's ``S03b`` longitudinal claims with real
per-era corpora of ant / myrmecology / social-insect literature.

API reality check (2026-09-16)
------------------------------

- BHL API v3 (``https://www.biodiversitylibrary.org/api3``) **requires
  an API key**: keyless calls return
  ``{"Status": "unauthorized", "ErrorMessage": "'' is an invalid or
  unauthorized API key."}``.  A free key can be requested at
  ``https://www.biodiversitylibrary.org/getapikey.aspx``; provide it
  through the ``BHL_API_KEY`` environment variable (or ``--api-key``)
  and :func:`bhl_api3_get` transparently upgrades the harvest to the
  official Search / GetTitleMetadata / GetItemMetadata endpoints.
- Keyless per-page text (``https://www.biodiversitylibrary.org/page/N.txt``)
  is gated by a Cloudflare challenge (HTTP 403) for non-browser
  clients, and ``/data/`` OpenData exports are metadata-only
  (BibTeX/KBART/MODS/RIS/TSV — no full text).
- **Keyless full text therefore comes from the BHL titles mirrored on
  the Internet Archive** (``collection:biodiversity``, which BHL
  ingests) via IA's keyless Search / Metadata / Download endpoints
  (``<identifier>_djvu.txt``).  Records carry the BHL collections each
  item belongs to, so provenance stays BHL-rooted.

Machinery
---------
:func:`harvest_bhl` searches IA for BHL-collection items matching the
ant/myrmecology query with an 1850-1970 publication-date filter,
fetches each item's metadata (``archive.org/metadata/<id>``) and full
text (``archive.org/download/<id>/<id>_djvu.txt``), and shards records
into ``data/bhl/`` (<= ~19 MB per shard, GitHub 100 MB blob limit)
with a provenance sidecar keyed by ``sha256(full_text)`` mapping to
``{bhl_id, ia_identifier, title, publication_date, era, collections,
url}``.  Sharding is resumable: items already stored are skipped.

Era bucketing
-------------
``1850-1899`` -> ``era_1850_1899``, ``1900-1949`` ->
``era_1900_1949``, ``1950-1970`` -> ``era_1950_1970``.  Items outside
the window are dropped (they cannot anchor an era claim).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

__all__ = [
    "BHL_API_BASE",
    "BHL_SEARCH_OP",
    "BHL_FULLTEXT_SEARCHTYPE",
    "BHL_SEARCH_MAX_ROWS",
    "BHL_KEYED_QUERY",
    "SEARCH_INSIDE_TERMS",
    "SEARCH_INSIDE_DATE_FROM",
    "SEARCH_INSIDE_DATE_TO",
    "SEARCH_INSIDE_ITEM_CAP",
    "IA_ADVANCEDSEARCH_URL",
    "IA_METADATA_URL",
    "IA_DOWNLOAD_URL",
    "BHL_SEARCH_QUERY",
    "CORPUS_FIELDS",
    "ERA_BOUNDS",
    "DATA_DIR",
    "SHARD_SIZE",
    "era_for_year",
    "is_relevant_bhl_record",
    "parse_advancedsearch_doc",
    "parse_publication_search_doc",
    "BHLHarvester",
    "shard_paths",
    "read_shard",
    "load_corpus_records",
    "load_provenance",
    "BHL_SEARCH_MAX_PAGES",
    "write_readme",
    "harvest_bhl",
    "main",
]

logger = logging.getLogger(__name__)

# ── API reality-check constants (see module docstring) ────────────────

BHL_API_BASE = "https://www.biodiversitylibrary.org/api3"
#: Page/part ``.txt`` URLs are Cloudflare-gated for non-browser clients.
BHL_PAGE_TEXT_URL = "https://www.biodiversitylibrary.org/page/{pageid}.txt"
#: OpenData exports are metadata-only; no full text is published there.
BHL_OPENDATA_URL = "https://www.biodiversitylibrary.org/data/"
#: Internet Archive endpoints used for the keyless harvest.
IA_ADVANCEDSEARCH_URL = "https://archive.org/advancedsearch.php"
IA_METADATA_URL = "https://archive.org/metadata/{identifier}"
IA_DOWNLOAD_URL = "https://archive.org/download/{identifier}/{identifier}_djvu.txt"

#: API key resolution order: CLI flag > ``BHL_API_KEY`` > none.
BHL_API_KEY_ENV = "BHL_API_KEY"

#: Keyed full-text search.  The BHL API v3 method table names no
#: ``SearchInside`` op (``op=SearchInside`` returns an empty 200
#: response); the corpus-wide full-text search is ``PublicationSearch``
#: with ``searchtype=F`` (``C`` restricts to metadata), paged via
#: ``page``/``pageSize`` (the API rejects ``pageSize`` > 200).
BHL_SEARCH_OP = "PublicationSearch"
BHL_FULLTEXT_SEARCHTYPE = "F"
BHL_SEARCH_MAX_ROWS = 200
#: The API rejects ``page`` > 50 (HTTP 400): at most 50 x 200 =
#: 10,000 relevance-ranked publications are retrievable per term.
BHL_SEARCH_MAX_PAGES = 50

#: Keyed-search terms and date window per the brief (recorded verbatim
#: in ``data/bhl/README.md``).
SEARCH_INSIDE_TERMS: Tuple[str, ...] = (
    "ants",
    "ant",
    "Formicidae",
    "myrmecology",
    "eusocial",
    "social insects",
    "superorganism",
    "division of labour",
)
SEARCH_INSIDE_DATE_FROM = 1850
SEARCH_INSIDE_DATE_TO = 1970
#: Cap on keyed-search candidate items; when the search surfaces more
#: than this many unique items the harvest takes the highest-relevance
#: ``SEARCH_INSIDE_ITEM_CAP`` and says so in the README/report.
SEARCH_INSIDE_ITEM_CAP = 3000

#: Provenance label for keyed-search documents (per-record ``query``
#: field; per-term yields live in ``searchinside_results.json`` and the
#: README).
BHL_KEYED_QUERY = (
    "BHL API v3 PublicationSearch searchtype=F full-text search inside "
    "(" + "; ".join(SEARCH_INSIDE_TERMS) + "), dates "
    f"{SEARCH_INSIDE_DATE_FROM}-{SEARCH_INSIDE_DATE_TO}"
)

# ── Search query (recorded verbatim in data/bhl/README.md) ────────────
# Restrict to the BHL mirror collection on the Internet Archive so every
# hit is a scanned item ingested by the Biodiversity Heritage Library.
# ``mediatype:texts`` guarantees a retrievable OCR text derivative.
# The title/subject clause binds hits to ant / myrmecology / social-insect
# literature; the date range implements the 1850-1970 brief window.
BHL_SEARCH_QUERY = (
    'collection:"biodiversity" AND mediatype:texts '
    'AND (title:(ants OR ant OR Formicidae OR myrmecology) '
    'OR subject:(Formicidae OR ants OR myrmecology OR "social insects" '
    'OR eusocial)) '
    "AND date:[1850-01-01 TO 1970-12-31]"
)

#: Word-boundary relevance filter over title+text (guards against
#: tangential subject hits such as generic "insect" catalogues).
RELEVANCE_TERMS: Tuple[str, ...] = (
    r"\bants?\b",
    r"\bFormicidae\b",
    r"\bmyrmecolog(?:y|ical)\b",
    r"\beusocial(?:ity)?\b",
    r"\bsocial insects?\b",
)
_RELEVANCE_RE = re.compile("|".join(RELEVANCE_TERMS), re.IGNORECASE)

#: Output record fields (order-stable for shard serialization).
CORPUS_FIELDS: Tuple[str, ...] = (
    "bhl_id",
    "ia_identifier",
    "title",
    "publication_date",
    "year",
    "era",
    "collections",
    "url",
    "full_text",
)

#: Era buckets per the brief; years outside these bounds are dropped.
ERA_BOUNDS: Dict[str, Tuple[int, int]] = {
    "era_1850_1899": (1850, 1899),
    "era_1900_1949": (1900, 1949),
    "era_1950_1970": (1950, 1970),
}

#: Shard ceiling: ~19 MB of text per file, under the GitHub 100 MB
#: blob limit (matches the ``data/fulltexts`` sharding convention).
SHARD_SIZE = 40

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "bhl"


# ── Era bucketing ─────────────────────────────────────────────────────


def era_for_year(year: Optional[int]) -> Optional[str]:
    """Map a publication year to its era bucket name.

    Args:
        year: Publication year (``None`` when undatable).

    Returns:
        ``"era_1850_1899"``, ``"era_1900_1949"``, or
        ``"era_1950_1970"``; ``None`` when the year is missing or
        outside the 1850-1970 window.
    """
    if not isinstance(year, int):
        return None
    for era, (low, high) in ERA_BOUNDS.items():
        if low <= year <= high:
            return era
    return None


def is_relevant_bhl_record(record: Dict[str, Any]) -> bool:
    """Return True when the record text mentions a relevance term.

    Checked against the concatenated title/text with word-boundary,
    case-insensitive matching so ``plant``/``antenna`` never match
    while ``ant-mediated`` and ``harvester ants`` do.

    Args:
        record: Record with at least ``title``; ``full_text`` optional.

    Returns:
        True if any relevance term occurs.
    """
    haystack = " ".join(
        str(record.get(field) or "") for field in ("title", "full_text")
    )
    return bool(_RELEVANCE_RE.search(haystack))


# ── JSON parsing ──────────────────────────────────────────────────────


def _as_int(value: Any) -> Optional[int]:
    """Coerce a scalar to int when possible, else ``None``."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _as_date(value: Any) -> Optional[str]:
    """Return a normalized ISO date string for common IA date shapes.

    Accepts ``YYYY``, ``YYYY-MM`` and ``YYYY-MM-DD`` strings and
    four-digit years embedded in longer strings; anything else maps to
    ``None`` (the record is then undatable and dropped).
    """
    if value is None:
        return None
    text = str(value).strip()
    for pattern in (
        r"^(\d{4})-\d{2}-\d{2}",
        r"^(\d{4})-\d{2}",
        r"^(\d{4})$",
    ):
        match = re.match(pattern, text)
        if match:
            year = int(match.group(1))
            return text if 1000 <= year <= 2100 else None
    match = re.search(r"\b(1[89]\d{2}|20[01]\d)\b", text)
    if match:
        return match.group(1)
    return None


def parse_advancedsearch_doc(payload: str) -> List[Dict[str, Any]]:
    """Parse one IA ``advancedsearch.php`` response into candidate stubs.

    Args:
        payload: Raw JSON body from ``advancedsearch.php``.

    Returns:
        One stub per ``doc``: ``{ia_identifier, title, year,
        publication_date, collections}`` in relevance order.  Docs
        without an identifier are skipped (they cannot be fetched).
    """
    response = json.loads(payload).get("response", {})
    stubs: List[Dict[str, Any]] = []
    for doc in response.get("docs", []):
        identifier = doc.get("identifier")
        if not identifier:
            continue
        date_text = _as_date(doc.get("year") or doc.get("date")) or ""
        stubs.append(
            {
                "ia_identifier": str(identifier),
                "title": str(doc.get("title") or ""),
                "publication_date": date_text,
                "year": _as_int(date_text.split("-")[0]) if date_text else None,
                "collections": [
                    str(c) for c in (doc.get("collection") or [])
                ],
            }
        )
    return stubs


def parse_publication_search_doc(payload: str) -> List[Dict[str, Any]]:
    """Parse one BHL ``PublicationSearch`` response into publication stubs.

    Args:
        payload: Raw JSON body from ``api3?op=PublicationSearch``.

    Returns:
        One stub per returned publication, in API (relevance) order:
        ``{bhl_type, item_id, part_id, title, publication_date, year,
        found_in}``.  Publications without a usable ItemID (``Item``)
        or PartID (``Part``) are skipped — they cannot be resolved to
        a harvestable item.
    """
    response = json.loads(payload)
    stubs: List[Dict[str, Any]] = []
    for pub in response.get("Result") or []:
        if not isinstance(pub, dict):
            continue
        bhl_type = str(pub.get("BHLType") or "")
        item_id = _as_int(pub.get("ItemID"))
        part_id = _as_int(pub.get("PartID"))
        if bhl_type == "Item" and item_id:
            pass
        elif bhl_type == "Part" and part_id:
            item_id = None
        else:
            continue
        date_text = _as_date(pub.get("PublicationDate") or pub.get("Date")) or ""
        stubs.append(
            {
                "bhl_type": bhl_type,
                "item_id": item_id,
                "part_id": part_id,
                "title": str(pub.get("Title") or pub.get("ContainerTitle") or ""),
                "publication_date": date_text,
                "year": _as_int(date_text.split("-")[0]) if date_text else None,
                "found_in": str(pub.get("FoundIn") or ""),
            }
        )
    return stubs


# ── Harvester ─────────────────────────────────────────────────────────


class BHLHarvester:
    """Harvest BHL-collection full texts over the Internet Archive.

    All endpoints are keyless; when ``BHL_API_KEY`` (or ``api_key``)
    is provided the harvester additionally verifies BHL API v3 access
    via :meth:`check_api_key` and records the result in the README.

    Attributes:
        DELAY: Seconds between network calls (IA politeness).
        MAX_RETRIES: Attempts per request before ``RuntimeError``.
    """

    DELAY = 1.0
    MAX_RETRIES = 3

    def __init__(
        self,
        api_key: Optional[str] = None,
        delay: Optional[float] = None,
    ):
        """Store API-key and pacing configuration.

        Args:
            api_key: BHL API v3 key; defaults to the ``BHL_API_KEY``
                environment variable.  Unused by the keyless transport
                but verified and reported when present.
            delay: Override for :attr:`DELAY` between calls.
        """
        self.api_key = api_key or os.environ.get(BHL_API_KEY_ENV) or ""
        self.delay = self.DELAY if delay is None else delay

    # ── HTTP plumbing ─────────────────────────────────────────────

    def _get(
        self,
        url: str,
        timeout: int = 120,
        binary: bool = False,
    ) -> Any:
        """GET a URL with retries and backoff.

        Args:
            url: Fully-qualified URL.
            timeout: Socket timeout in seconds.
            binary: Return raw bytes when True, decoded text otherwise.

        Returns:
            Response body (``str`` or ``bytes``).

        Raises:
            RuntimeError: After ``MAX_RETRIES`` failed attempts.
        """
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                request = Request(
                    url, headers={"User-Agent": "ento-linguistics-bhl/1.0"}
                )
                with urlopen(request, timeout=timeout) as response:
                    body = response.read()
                return body if binary else body.decode("utf-8", "replace")
            except (HTTPError, URLError, TimeoutError) as exc:
                last_error = exc
                logger.warning(
                    "Request failed (attempt %d/%d): %s (%s)",
                    attempt,
                    self.MAX_RETRIES,
                    self._redact(url),
                    exc,
                )
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.delay * attempt * 2)
        raise RuntimeError(f"Request failed: {self._redact(url)} ({last_error})")

    def _redact(self, text: str) -> str:
        """Mask the configured API key inside ``text``.

        Keyed BHL calls pass ``apikey`` as a query argument, so any
        URL reaching a log line or exception message is scrubbed
        first: the key must never be written to any file.
        """
        if self.api_key and self.api_key in text:
            return text.replace(self.api_key, "***BHL_API_KEY***")
        return text

    def _api3_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Issue one BHL API v3 JSON call and return the parsed body.

        Raises:
            RuntimeError: When the transport fails or the API answers
                with a non-``ok`` ``Status``.
        """
        params = dict(params)
        if self.api_key:
            params["apikey"] = self.api_key
        params["format"] = "json"
        payload = self._get(f"{BHL_API_BASE}?{urlencode(params)}")
        response = json.loads(payload)
        status = str(response.get("Status", "error"))
        if status.lower() != "ok":
            raise RuntimeError(
                f"BHL API v3 {params.get('op')} failed: "
                f"{response.get('ErrorMessage') or status}"
            )
        return response

    # ── Keyless transports ────────────────────────────────────────

    def check_api_key(self) -> Dict[str, Any]:
        """Probe BHL API v3 with the configured key (or keyless).

        Returns:
            ``{"endpoint", "keyed": bool, "status": <API Status>,
            "ok": bool}`` describing whether the official API
            accepted the credentials.  Never raises: an unreachable
            API maps to ``ok=False`` with the error text in ``status``.
        """
        query = {"op": "GetTitleMetadata", "titleid": "1", "format": "json"}
        if self.api_key:
            query["apikey"] = self.api_key
        url = f"{BHL_API_BASE}?{urlencode(query)}"
        try:
            request = Request(url, headers={"User-Agent": "ento-linguistics-bhl/1.0"})
            with urlopen(request, timeout=60) as response:
                payload = response.read().decode("utf-8", "replace")
            result = json.loads(payload)
            status = str(result.get("Status", "unknown"))
            return {
                "endpoint": BHL_API_BASE,
                "keyed": bool(self.api_key),
                "status": status,
                "ok": status.lower() == "ok",
            }
        except HTTPError as exc:
            return {
                "endpoint": BHL_API_BASE,
                "keyed": bool(self.api_key),
                "status": f"HTTP {exc.code}" + (
                    " (key required)" if exc.code in (401, 403) else ""
                ),
                "ok": False,
            }
        except (URLError, ValueError) as exc:
            return {
                "endpoint": BHL_API_BASE,
                "keyed": bool(self.api_key),
                "status": f"unreachable: {exc}",
                "ok": False,
            }

    def search_titles(
        self,
        query: str = BHL_SEARCH_QUERY,
        rows: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Run the IA advancedsearch for BHL-collection candidates.

        Pages through results with ``start`` offsets until fewer than
        ``rows`` docs return or the hit count is exhausted.

        Args:
            query: Verbatim search query.
            rows: Page size (IA caps at 1000... actually 200 per page
                is the safest supported value).

        Returns:
            Candidate stubs in relevance order (see
            :func:`parse_advancedsearch_doc`).
        """
        page_size = min(rows, 200)
        stubs: List[Dict[str, Any]] = []
        start = 0
        total: Optional[int] = None
        while True:
            params = urlencode(
                {
                    "q": query,
                    "fl[]": ["identifier", "title", "year", "collection"],
                    "rows": page_size,
                    "start": start,
                    "output": "json",
                },
                doseq=True,
            )
            payload = self._get(f"{IA_ADVANCEDSEARCH_URL}?{params}")
            response = json.loads(payload).get("response", {})
            total = response.get("numFound", 0)
            docs = parse_advancedsearch_doc(payload)
            stubs.extend(docs)
            if not docs or start + page_size >= int(total):
                break
            start += page_size
            time.sleep(self.delay)
        logger.info("advancedsearch returned %d candidate items", len(stubs))
        return stubs

    # ── Keyed full-text search (BHL API v3) ───────────────────────

    def search_inside(
        self,
        query: str,
        date_from: int = SEARCH_INSIDE_DATE_FROM,
        date_to: int = SEARCH_INSIDE_DATE_TO,
        rows: int = BHL_SEARCH_MAX_ROWS,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """Run the keyed full-text search for one term.

        Pages through BHL API v3 ``PublicationSearch`` with
        ``searchtype=F`` (full text) until a short page exhausts the
        hit list, then keeps only publications dated inside
        ``[date_from, date_to]`` (the API exposes no server-side date
        filter for this op).  The API rejects ``page`` values above
        :data:`BHL_SEARCH_MAX_PAGES` (HTTP 400), capping retrieval at
        ``BHL_SEARCH_MAX_PAGES * BHL_SEARCH_MAX_ROWS`` relevance-ranked
        publications per term; terms with more hits are recorded as
        truncated.

        Args:
            query: Search term (e.g. ``"Formicidae"``).
            date_from: Inclusive publication-year lower bound.
            date_to: Inclusive publication-year upper bound.
            rows: Page size (capped at :data:`BHL_SEARCH_MAX_ROWS`).

        Returns:
            ``(publications, truncated)`` where ``publications`` are
            in-window stubs (see :func:`parse_publication_search_doc`)
            in API relevance order — undated publications are dropped,
            they cannot be era-bucketed — and ``truncated`` is True
            when the term's hit list exceeded the API page cap.
        """
        page_size = max(1, min(rows, BHL_SEARCH_MAX_ROWS))
        pubs: List[Dict[str, Any]] = []
        truncated = False
        page = 1
        while True:
            response = self._api3_get(
                {
                    "op": BHL_SEARCH_OP,
                    "searchterm": query,
                    "searchtype": BHL_FULLTEXT_SEARCHTYPE,
                    "page": page,
                    "pageSize": page_size,
                }
            )
            docs = parse_publication_search_doc(
                json.dumps({"Result": response.get("Result") or []})
            )
            pubs.extend(docs)
            if len(docs) < page_size:
                break
            if page >= BHL_SEARCH_MAX_PAGES:
                truncated = True
                break
            page += 1
            time.sleep(self.delay)
        in_window = [
            pub
            for pub in pubs
            if pub["year"] is not None and date_from <= pub["year"] <= date_to
        ]
        logger.info(
            "PublicationSearch %r: %d publications, %d within %d-%d%s",
            query,
            len(pubs),
            len(in_window),
            date_from,
            date_to,
            " (truncated at API page cap)" if truncated else "",
        )
        return in_window, truncated

    def get_part_item_id(self, part_id: int) -> Optional[int]:
        """Resolve a BHL PartID to its containing ItemID (keyed).

        Args:
            part_id: BHL part identifier from a search hit.

        Returns:
            The containing BHL ItemID, or ``None`` when the part has
            no item link.
        """
        response = self._api3_get({"op": "GetPartMetadata", "id": part_id})
        result = response.get("Result") or []
        if not isinstance(result, list) or not result:
            return None
        first = result[0]
        return _as_int(first.get("ItemID")) if isinstance(first, dict) else None

    def get_item_stub(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Build a harvest stub for a BHL ItemID (keyed).

        Only items digitized from the Internet Archive carry a
        ``SourceIdentifier`` the existing keyless fetch machinery can
        download; other sources return ``None``.

        Args:
            item_id: BHL item identifier.

        Returns:
            ``{ia_identifier, title, publication_date, bhl_item_id}``
            or ``None`` when the item is not IA-sourced.
        """
        response = self._api3_get({"op": "GetItemMetadata", "id": item_id})
        result = response.get("Result") or []
        if not isinstance(result, list) or not result:
            return None
        item = result[0]
        if not isinstance(item, dict):
            return None
        identifier = str(item.get("SourceIdentifier") or "")
        if str(item.get("Source") or "") != "Internet Archive" or not identifier:
            return None
        return {
            "ia_identifier": identifier,
            "title": str(item.get("Title") or ""),
            "publication_date": _as_date(item.get("Year")) or "",
            "bhl_item_id": _as_int(item.get("ItemID")),
        }

    def collect_search_inside_candidates(
        self,
        data_dir: Path,
        cap: int = SEARCH_INSIDE_ITEM_CAP,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Enumerate, merge, and cap the keyed full-text candidates.

        For each term in :data:`SEARCH_INSIDE_TERMS` the full-text
        search is enumerated to exhaustion (per-term publication
        lists are checkpointed to ``searchinside_results.json``, so an
        interrupted run re-fetches only missing terms).  Publications
        are then merged in interleaved relevance order (rank r of
        every term before rank r+1, so multi-term matches surface
        first), Parts are resolved to Items via
        :meth:`get_part_item_id` (cached in
        ``searchinside_items.json``), and unique BHL item IDs are
        accumulated up to ``cap``.  Finally each candidate item is
        converted to an IA-backed harvest stub via
        :meth:`get_item_stub` (also cached).

        Args:
            data_dir: Corpus directory receiving the checkpoint files.
            cap: Maximum unique candidate items to surface.

        Returns:
            ``(stubs, stats)`` where ``stubs`` is the ranked,
            IA-identifier-deduplicated harvest stub list and ``stats``
            records per-term publication yields, item counts, the
            truncation flag, and non-IA item counts.
        """
        data_dir.mkdir(parents=True, exist_ok=True)
        results_path = data_dir / "searchinside_results.json"
        items_path = data_dir / "searchinside_items.json"

        results: Dict[str, Any] = {"terms": {}}
        if results_path.exists():
            results = json.loads(results_path.read_text(encoding="utf-8"))
        results.setdefault("terms", {})
        results.setdefault("truncated", {})
        per_term_pubs: Dict[str, int] = {}
        per_term_truncated: Dict[str, bool] = {}
        for term in SEARCH_INSIDE_TERMS:
            if term in results["terms"]:
                pubs = results["terms"][term]
                term_truncated = bool(results["truncated"].get(term, False))
            else:
                pubs, term_truncated = self.search_inside(term)
                results["terms"][term] = pubs
                results["truncated"][term] = term_truncated
                _atomic_write_text(
                    results_path,
                    json.dumps(results, ensure_ascii=False, indent=1) + "\n",
                )
            per_term_pubs[term] = len(pubs)
            per_term_truncated[term] = term_truncated
            time.sleep(self.delay)

        items_doc: Dict[str, Any] = {"part_to_item": {}, "items": [], "stubs": {}}
        if items_path.exists():
            items_doc = json.loads(items_path.read_text(encoding="utf-8"))
        items_doc.setdefault("part_to_item", {})
        items_doc.setdefault("items", [])
        items_doc.setdefault("stubs", {})

        def _persist_items() -> None:
            _atomic_write_text(
                items_path,
                json.dumps(items_doc, ensure_ascii=False, indent=1) + "\n",
            )

        part_cache = {
            _as_int(key): value
            for key, value in items_doc["part_to_item"].items()
        }
        item_entries: Dict[int, Dict[str, Any]] = {}
        for entry in items_doc["items"]:
            if isinstance(entry, dict) and _as_int(entry.get("bhl_item_id")):
                item_entries[_as_int(entry["bhl_item_id"])] = entry

        def _terms(pubs_by_term: Dict[str, List[Dict[str, Any]]]) -> Any:
            """Interleave per-term result lists by relevance rank."""
            iterators = [
                (term, iter(pubs)) for term, pubs in pubs_by_term.items()
            ]
            exhausted = {term: False for term, _ in iterators}
            while not all(exhausted.values()):
                for term, iterator in iterators:
                    if exhausted[term]:
                        continue
                    pub = next(iterator, None)
                    if pub is None:
                        exhausted[term] = True
                        continue
                    yield term, pub

        truncated = False
        not_ia_sourced = 0
        for term, pub in _terms(results["terms"]):
            if truncated:
                break
            if pub["bhl_type"] == "Item":
                item_id = pub["item_id"]
            else:
                item_id = part_cache.get(pub["part_id"])
                if item_id is None:
                    item_id = self.get_part_item_id(pub["part_id"])
                    part_cache[pub["part_id"]] = item_id
                    items_doc["part_to_item"][str(pub["part_id"])] = item_id
                    time.sleep(self.delay)
            if item_id is None:
                continue
            entry = item_entries.get(item_id)
            if entry is None:
                if len(item_entries) >= cap:
                    truncated = True
                    break
                entry = {"bhl_item_id": item_id, "queries": []}
                item_entries[item_id] = entry
                items_doc["items"].append(entry)
            queries = entry.setdefault("queries", [])
            if term not in queries:
                queries.append(term)

        _persist_items()

        # Resolve each candidate item to an IA-backed stub (cached).
        stubs: List[Dict[str, Any]] = []
        seen_identifiers: set = set()
        for item_id, entry in item_entries.items():
            key = str(item_id)
            if key in items_doc["stubs"]:
                stub_doc = items_doc["stubs"][key]
            else:
                stub_doc = self.get_item_stub(item_id)
                items_doc["stubs"][key] = stub_doc
                if stub_doc is None:
                    not_ia_sourced += 1
                time.sleep(self.delay)
            if stub_doc is None:
                continue
            stub_doc = dict(stub_doc)
            stub_doc["queries"] = list(entry.get("queries") or [])
            identifier = stub_doc["ia_identifier"]
            if identifier in seen_identifiers:
                continue
            seen_identifiers.add(identifier)
            stubs.append(stub_doc)
        _persist_items()

        stats = {
            "op": BHL_SEARCH_OP,
            "searchtype": BHL_FULLTEXT_SEARCHTYPE,
            "date_window": [SEARCH_INSIDE_DATE_FROM, SEARCH_INSIDE_DATE_TO],
            "per_term_publications": per_term_pubs,
            "per_term_truncated": per_term_truncated,
            "candidate_items": len(item_entries),
            "cap": cap,
            "truncated": truncated,
            "not_ia_sourced": not_ia_sourced,
            "stubs": len(stubs),
        }
        logger.info(
            "Keyed search inside: %d candidate items (cap %d, truncated=%s), "
            "%d IA-backed stubs",
            len(item_entries),
            cap,
            truncated,
            len(stubs),
        )
        return stubs, stats

    def fetch_item_metadata(self, identifier: str) -> Dict[str, Any]:
        """Fetch one item's IA metadata (files, date, collections).

        Args:
            identifier: IA identifier.

        Returns:
            The parsed ``metadata`` mapping plus a ``files`` name list;
            empty dict when the item exposes neither.
        """
        payload = self._get(IA_METADATA_URL.format(identifier=identifier))
        doc = json.loads(payload)
        files = [
            f["name"]
            for f in doc.get("files", [])
            if isinstance(f, dict) and f.get("name")
        ]
        return {"metadata": doc.get("metadata", {}), "files": files}

    def fetch_full_text(self, identifier: str) -> str:
        """Fetch an item's OCR full text (``_djvu.txt`` derivative).

        Args:
            identifier: IA identifier.

        Returns:
            Full text (may be empty when no text derivative exists).

        Raises:
            RuntimeError: When the download fails after retries.
        """
        return self._get(
            IA_DOWNLOAD_URL.format(identifier=identifier),
            timeout=300,
            binary=True,
        ).decode("utf-8", "replace")

    # ── Record assembly ───────────────────────────────────────────

    def build_record(
        self,
        stub: Dict[str, Any],
        item_meta: Dict[str, Any],
        full_text: str,
    ) -> Optional[Dict[str, Any]]:
        """Assemble one corpus record from a candidate stub.

        Publication date prefers the item metadata ``date``/``year``
        (authoritative) over the search stub, then maps the year to
        its era bucket.  Records outside 1850-1970 return ``None``.

        Args:
            stub: Candidate stub from :meth:`search_titles`.
            item_meta: Item metadata from :meth:`fetch_item_metadata`.
            full_text: OCR full text from :meth:`fetch_full_text`.

        Returns:
            Record dict with the ``CORPUS_FIELDS`` keys, or ``None``
            when the item cannot be dated inside the window.
        """
        md = item_meta.get("metadata", {})
        date_text = (
            _as_date(md.get("date"))
            or _as_date(md.get("year"))
            or stub.get("publication_date")
            or ""
        )
        year = _as_int(date_text.split("-")[0]) if date_text else None
        era = era_for_year(year)
        if era is None:
            return None
        collections = [
            str(c)
            for c in (
                md.get("collection")
                or (stub.get("collections") if isinstance(stub.get("collections"), list) else [])
                or []
            )
        ]
        if isinstance(collections, str):
            collections = [collections]
        identifier = stub["ia_identifier"]
        return {
            "bhl_id": identifier,
            "ia_identifier": identifier,
            "title": str(stub.get("title") or md.get("title") or ""),
            "publication_date": date_text,
            "year": year,
            "era": era,
            "collections": collections,
            "url": f"https://archive.org/details/{identifier}",
            "full_text": full_text,
        }

    # ── Harvest loop ──────────────────────────────────────────────

    def harvest_sharded(
        self,
        data_dir: Path,
        provenance_path: Path,
        query: str = BHL_SEARCH_QUERY,
        target: Optional[int] = None,
        stubs: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Resumable sharded harvest of BHL-collection candidates.

        Items already present in ``data_dir`` shards are skipped.
        Each item is fetched (metadata + full text), filtered by the
        relevance guard and the 1850-1970 era window, and appended to
        shard files of at most :data:`SHARD_SIZE` records.  Every
        shard and the provenance sidecar are written atomically, so
        an interrupted run continues where it stopped.

        Args:
            data_dir: Corpus directory holding shard files.
            provenance_path: Provenance sidecar path (single file).
            query: Verbatim search query recorded per document.
            target: Stop after this many NEW records; ``None``
                harvests the entire candidate set.
            stubs: Pre-resolved candidate stubs (keyed-search path).
                When ``None`` the IA ``advancedsearch`` is queried via
                :meth:`search_titles`; when given, the merge with
                already-stored records still applies (stored
                ``ia_identifier``s are skipped).

        Returns:
            Summary mapping with ``candidates``, ``already_stored``,
            ``harvested``, ``fetched``, ``no_text_derivative``,
            ``out_of_window``, ``irrelevant``, ``shards``,
            ``failed_items``, ``api_check``.
        """
        data_dir.mkdir(parents=True, exist_ok=True)
        already = load_corpus_records(data_dir, provenance_path)
        already_ids = {record["ia_identifier"] for record in already}
        if stubs is None:
            stubs = self.search_titles(query)
        else:
            logger.info("Using %d pre-resolved candidate stubs", len(stubs))
        logger.info(
            "advancedsearch returned %d candidate items (%d already stored)",
            len(stubs),
            len(already_ids),
        )

        api_check = self.check_api_key()
        time.sleep(self.delay)

        shards = shard_paths(data_dir)
        buffer: List[Dict[str, Any]] = []
        pending: Optional[Path] = shards[-1] if shards else None
        if shards:
            buffer = read_shard(shards[-1])
        buffer_start = len(buffer)
        next_shard = len(shards)

        provenance = load_provenance(provenance_path)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        harvested = 0
        fetched = 0
        no_text = 0
        out_of_window = 0
        irrelevant = 0
        failed_items = 0

        for stub in stubs:
            if target is not None and harvested >= target:
                break
            identifier = stub["ia_identifier"]
            if identifier in already_ids:
                continue
            try:
                item_meta = self.fetch_item_metadata(identifier)
                full_text = ""
                if not any(name.endswith("_djvu.txt") for name in item_meta["files"]):
                    no_text += 1
                else:
                    full_text = self.fetch_full_text(identifier)
                    fetched += 1
                    time.sleep(self.delay)
            except (RuntimeError, ValueError) as exc:
                logger.warning("Skipping item %s: %s", identifier, exc)
                failed_items += 1
                time.sleep(self.delay)
                continue
            record = self.build_record(stub, item_meta, full_text)
            if record is None:
                out_of_window += 1
                time.sleep(self.delay)
                continue
            if not full_text or not is_relevant_bhl_record(record):
                irrelevant += 1
                time.sleep(self.delay)
                continue
            already_ids.add(identifier)
            harvested += 1
            digest = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
            provenance.setdefault(
                digest,
                {
                    "bhl_id": record["bhl_id"],
                    "ia_identifier": record["ia_identifier"],
                    "title": record["title"],
                    "publication_date": record["publication_date"],
                    "era": record["era"],
                    "collections": record["collections"],
                    "url": record["url"],
                    "query": query,
                    "retrieved_at": retrieved_at,
                },
            )
            buffer.append({field: record.get(field) for field in CORPUS_FIELDS})
            if len(buffer) >= SHARD_SIZE:
                if pending is not None:
                    path = pending
                    pending = None
                else:
                    next_shard += 1
                    path = data_dir / shard_filename(next_shard)
                write_shard(path, buffer)
                buffer = []
                _atomic_write_text(
                    provenance_path,
                    json.dumps(
                        provenance, ensure_ascii=False, indent=1, sort_keys=True
                    )
                    + "\n",
                )
            logger.info(
                "Progress: %d/%d candidates fetched, %d new records (at %s)",
                fetched,
                len(stubs),
                harvested,
                identifier,
            )
            time.sleep(self.delay)

        # Flush the tail shard when the buffer gained records on this
        # run (rewrites the tail shard: stored records + new ones), or
        # when no tail shard existed yet.
        if buffer and (len(buffer) != buffer_start or pending is None):
            if pending is not None:
                path = pending
            else:
                next_shard += 1
                path = data_dir / shard_filename(next_shard)
            write_shard(path, buffer)
        _atomic_write_text(
            provenance_path,
            json.dumps(provenance, ensure_ascii=False, indent=1, sort_keys=True)
            + "\n",
        )
        summary = {
            "candidates": len(stubs),
            "already_stored": len(already_ids) - harvested,
            "harvested": harvested,
            "fetched": fetched,
            "no_text_derivative": no_text,
            "out_of_window": out_of_window,
            "irrelevant": irrelevant,
            "shards": [p.name for p in shard_paths(data_dir)],
            "failed_items": failed_items,
            "api_check": api_check,
        }
        logger.info("Harvest complete: %s", summary)
        return summary


# ── Persistence helpers ───────────────────────────────────────────────


def shard_filename(index: int) -> str:
    """Zero-padded shard filename for a 1-based index."""
    return f"bhl_shard_{index:05d}.json"


def shard_paths(data_dir: Path) -> List[Path]:
    """Shard files in concatenation (filename) order."""
    if not data_dir.exists():
        return []
    return sorted(data_dir.glob("bhl_shard_*.json"))


def write_shard(path: Path, records: List[Dict[str, Any]]) -> None:
    """Atomically write one shard file (tmp file + rename)."""
    _atomic_write_text(
        path, json.dumps(records, ensure_ascii=False, indent=1) + "\n"
    )


def read_shard(path: Path) -> List[Dict[str, Any]]:
    """Read one shard file into a record list (empty when absent)."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_corpus_records(
    data_dir: Path,
    provenance_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Load the whole corpus in shard order.

    Args:
        data_dir: Corpus directory with shard files.
        provenance_path: Unused (kept for signature parity with
            ``pmc_fulltext``); shards are self-contained.

    Returns:
        Records across all shards, filename order (concatenation
        order).  Empty when no shards exist.
    """
    records: List[Dict[str, Any]] = []
    for path in shard_paths(data_dir):
        records.extend(read_shard(path))
    return records


def load_provenance(provenance_path: Path) -> Dict[str, Any]:
    """Load the provenance sidecar (empty mapping when absent)."""
    if not provenance_path.exists():
        return {}
    return json.loads(provenance_path.read_text(encoding="utf-8"))


def build_provenance(
    records: List[Dict[str, Any]],
    query: str,
    retrieved_at: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """Build the ``sha256(full_text)`` -> provenance-entry mapping.

    Args:
        records: Corpus records (``full_text`` and metadata fields).
        query: Verbatim search query recorded per document.
        retrieved_at: ISO-8601 retrieval timestamp; defaults to now.

    Returns:
        Mapping digest -> ``{bhl_id, ia_identifier, title,
        publication_date, era, collections, url, query, retrieved_at}``.
    """
    retrieved_at = retrieved_at or datetime.now(timezone.utc).isoformat()
    provenance: Dict[str, Dict[str, Any]] = {}
    for record in records:
        full_text = record.get("full_text") or ""
        digest = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        provenance[digest] = {
            "bhl_id": record.get("bhl_id", ""),
            "ia_identifier": record.get("ia_identifier", ""),
            "title": record.get("title", ""),
            "publication_date": record.get("publication_date", ""),
            "era": record.get("era"),
            "collections": record.get("collections", []),
            "url": record.get("url", ""),
            "query": query,
            "retrieved_at": retrieved_at,
        }
    return provenance


def _atomic_write_text(path: Path, text: str) -> None:
    """Write text atomically (tmp file + rename) to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


# ── README ────────────────────────────────────────────────────────────


def _coverage_stats(data_dir: Path) -> Dict[str, Any]:
    """Compute corpus coverage statistics streaming over the shards."""
    count = 0
    body_chars = 0
    years: List[int] = []
    eras: Dict[str, int] = {}
    for path in shard_paths(data_dir):
        for record in read_shard(path):
            count += 1
            body_chars += len(record.get("full_text") or "")
            if isinstance(record.get("year"), int):
                years.append(record["year"])
            era = record.get("era") or "unknown"
            eras[era] = eras.get(era, 0) + 1
    return {"count": count, "body_chars": body_chars, "years": years, "eras": eras}


def write_readme(
    output_dir: Path,
    query: str = BHL_SEARCH_QUERY,
    summary: Optional[Dict[str, Any]] = None,
) -> Path:
    """Write ``README.md`` documenting the harvested BHL corpus.

    Records the API reality check, the verbatim search query, applied
    filters, shard layout, resumability behaviour, coverage computed
    by streaming over the actual shards, and the reproduction command.

    Args:
        output_dir: Corpus directory receiving ``README.md``.
        query: Verbatim search query.
        summary: Optional harvest summary from
            ``BHLHarvester.harvest_sharded``.

    Returns:
        The README path.
    """
    stats = _coverage_stats(output_dir)
    shards = [p.name for p in shard_paths(output_dir)]
    era_lines = "\n".join(
        f"- `{era}`: {count} documents"
        for era, count in sorted(stats["eras"].items())
    )
    year_line = (
        f"{min(stats['years'])}-{max(stats['years'])}" if stats["years"] else "n/a"
    )
    shard_lines = "\n".join(f"- `{name}`" for name in shards) or "- (none yet)"
    api_block = ""
    if summary and isinstance(summary.get("api_check"), dict):
        check = summary["api_check"]
        api_block = (
            f"\nAPI check at harvest time: endpoint `{check.get('endpoint')}`, "
            f"keyed={check.get('keyed')}, status=`{check.get('status')}`, "
            f"ok={check.get('ok')}.\n"
        )
    keyed_block = ""
    if summary and isinstance(summary.get("keyed"), dict):
        keyed = summary["keyed"]
        term_lines = "\n".join(
            f"- `{term}`: {count} in-window publications"
            + (
                " (enumeration truncated at the BHL 10,000-result cap)"
                if keyed.get("per_term_truncated", {}).get(term)
                else ""
            )
            for term, count in keyed.get("per_term_publications", {}).items()
        )
        keyed_block = (
            f"\n## Keyed full-text search (BHL API v3)\n\n"
            f"The 2026-09 keyed upgrade enumerates BHL's full-text search\n"
            f"(`api3?op={keyed.get('op')}&searchtype={keyed.get('searchtype')}`;\n"
            f"there is no literal `SearchInside` op — it returns an empty\n"
            f"200 response) for each term below, keeps publications dated\n"
            f"{keyed.get('date_window', [None, None])[0]}-"
            f"{keyed.get('date_window', [None, None])[1]}, resolves matched\n"
            f"Parts to Items, maps Items to their Internet Archive\n"
            f"`SourceIdentifier`, and merges the results into the same\n"
            f"shards as the keyless IA harvest (stored identifiers are\n"
            f"skipped).\n\n"
            f"Candidate items: {keyed.get('candidate_items', 0)} "
            f"(cap {keyed.get('cap', 0)}, truncated="
            f"{keyed.get('truncated', False)}); "
            f"IA-backed stubs: {keyed.get('stubs', 0)}; "
            f"non-IA items (no downloadable text): "
            f"{keyed.get('not_ia_sourced', 0)}.\n\n"
            f"Per-query yields (full enumeration, in-window):\n\n"
            f"{term_lines}\n\n"
        )
    if summary:
        summary_block = (
            f"\nLast harvest run: {summary.get('harvested', 0)} new documents "
            f"from {summary.get('candidates', 0)} candidates "
            f"({summary.get('fetched', 0)} texts fetched, "
            f"{summary.get('no_text_derivative', 0)} without text derivative, "
            f"{summary.get('out_of_window', 0)} out of window, "
            f"{summary.get('irrelevant', 0)} irrelevant, "
            f"{summary.get('failed_items', 0)} failed items skipped).\n"
        )
    readme = f"""# BHL Historical Full-Text Corpus (1850-1970) — data/bhl

Biodiversity Heritage Library historical layer grounding the
manuscript's S03b longitudinal claims (see
`docs/manuscript/S03b_case_studies.md` and
`src/pipeline/bhl_analysis.py`).
{summary_block}

## API reality check

- BHL API v3 (`https://www.biodiversitylibrary.org/api3`) requires an
  API key: keyless calls return `Status: unauthorized` ("'' is an
  invalid or unauthorized API key.").  Request a free key at
  `https://www.biodiversitylibrary.org/getapikey.aspx` and export it
  as `BHL_API_KEY` to upgrade the harvest to the official endpoints
  (`search`, `GetTitleMetadata`, `GetItemMetadata`,
  `GetPageMetadata`/`GetPageText`).
- Keyless per-page text (`https://www.biodiversitylibrary.org/page/N.txt`)
  is Cloudflare-gated (HTTP 403) for non-browser clients.
- The `/data/` OpenData exports (BibTeX/KBART/MODS/RIS/TSV) are
  metadata-only — no full text.
- When a key is available the harvest additionally runs BHL's
  keyed full-text search (`PublicationSearch`, `searchtype=F`) — the
  "Search Inside" capability; the literal `op=SearchInside` returns an
  empty 200 response and is not part of the API method table.
- This corpus therefore harvests the BHL mirror collection on the
  Internet Archive (`collection:"biodiversity"`) via IA's keyless
  Search / Metadata / Download endpoints; each record lists the BHL
  collections its item belongs to.
{api_block}
{keyed_block}
## Files

- `bhl_shard_NNNNN.json` — shard files, at most {SHARD_SIZE} records
  (~19 MB) each (GitHub rejects blobs >100 MB), holding JSON lists of
  records with fields: `bhl_id`, `ia_identifier`, `title`,
  `publication_date`, `year`, `era`, `collections`, `url`,
  `full_text`.  Concatenation order is filename order:

{shard_lines}

- `provenance.json` — sidecar mapping `sha256(full_text)` to
  `{{bhl_id, ia_identifier, title, publication_date, era, collections,
  url, query, retrieved_at}}`.
- `searchinside_results.json` — keyed-search checkpoint: per-term
  in-window publication lists from `PublicationSearch` (resumable:
  terms already present are not re-queried).
- `searchinside_items.json` — keyed-search checkpoint: Part→Item
  resolution cache, the ranked capped candidate item list with the
  queries that matched each item, and the IA-backed harvest stubs.
- `README.md` — this document.

## Search query (verbatim)

```
{query}
```

Issued against `https://archive.org/advancedsearch.php` with
`fl[]=identifier,title,year,collection`, `rows=200`,
`output=json`, paging via `start`.

## Filters

1. `collection:"biodiversity"` — BHL-ingested scans only.
2. `mediatype:texts` — items with retrievable derivatives.
3. Title/subject clause binds hits to ant / Formicidae / myrmecology /
   social-insect / eusocial literature.
4. `date:[1850-01-01 TO 1970-12-31]` — publication-date window;
   item metadata `date`/`year` is authoritative, undatable items are
   dropped.
5. Era buckets: 1850-1899 -> `era_1850_1899`, 1900-1949 ->
   `era_1900_1949`, 1950-1970 -> `era_1950_1970`.
6. Word-boundary relevance guard over title+text: ant/ants,
   Formicidae, myrmecology/myrmecological, eusocial/eusociality,
   "social insects".

## Era coverage ({stats['count']} documents)

- Publication years: {year_line}
- Body text: {stats['body_chars']:,} characters
- Documents per era:

{era_lines}

## Reproduction

```bash
uv run python src/data/bhl_corpus.py
# keyed full-text upgrade (requires BHL_API_KEY; resumable):
BHL_API_KEY=<key> uv run python src/data/bhl_corpus.py --keyed
```

The harvester is resumable: stored `ia_identifier`s are skipped and
re-running continues an interrupted harvest.  Load the corpus with:

```python
from pathlib import Path
from data.bhl_corpus import load_corpus_records
records = load_corpus_records(Path("data/bhl"))
```

The era-stratified analysis is built separately:

```bash
uv run python src/pipeline/bhl_analysis.py
```
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "README.md"
    _atomic_write_text(path, readme)
    return path


# ── CLI ───────────────────────────────────────────────────────────────


def harvest_bhl(
    data_dir: Optional[Path] = None,
    query: str = BHL_SEARCH_QUERY,
    target: Optional[int] = None,
    api_key: Optional[str] = None,
    keyed: bool = False,
) -> Dict[str, Any]:
    """Harvest the BHL historical corpus (search + fetch + shard).

    Convenience wrapper around :class:`BHLHarvester` used by tests and
    the CLI.

    Args:
        data_dir: Corpus directory (default ``data/bhl``).
        query: Verbatim search query.
        target: Stop after this many NEW records.
        api_key: BHL API key (defaults to ``BHL_API_KEY``).
        keyed: Run the keyed full-text upgrade first: enumerate BHL
            API v3 ``PublicationSearch`` (``searchtype=F``) over
            :data:`SEARCH_INSIDE_TERMS`, resolve and cap the candidate
            items (:data:`SEARCH_INSIDE_ITEM_CAP`), and merge the
            resulting IA-backed stubs into the corpus shards.  An API
            key is required; already-stored identifiers are skipped.

    Returns:
        Harvest summary (see ``harvest_sharded``); with ``keyed=True``
        the summary gains a ``keyed`` mapping (per-term yields, item
        counts, cap/truncation flag) recorded in the README.
    """
    data_dir = data_dir or DATA_DIR
    harvester = BHLHarvester(api_key=api_key)
    if keyed:
        if not harvester.api_key:
            raise RuntimeError(
                "keyed harvest requires a BHL API v3 key "
                "($BHL_API_KEY or --api-key)"
            )
        stubs, keyed_stats = harvester.collect_search_inside_candidates(
            data_dir
        )
        summary = harvester.harvest_sharded(
            data_dir,
            data_dir / "provenance.json",
            query=BHL_KEYED_QUERY,
            target=target,
            stubs=stubs,
        )
        summary["keyed"] = keyed_stats
    else:
        summary = harvester.harvest_sharded(
            data_dir,
            data_dir / "provenance.json",
            query=query,
            target=target,
        )
    write_readme(data_dir, query=query, summary=summary)
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: harvest the BHL historical corpus into shards.

    Resumable: stored items are skipped; re-running continues an
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
        "--api-key",
        type=str,
        default=None,
        help="BHL API v3 key (default: $BHL_API_KEY)",
    )
    parser.add_argument(
        "--keyed",
        action="store_true",
        help=(
            "Run the keyed BHL API v3 full-text search upgrade "
            "(requires $BHL_API_KEY or --api-key)"
        ),
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Corpus directory (default: <project root>/data/bhl)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    summary = harvest_bhl(
        data_dir=args.data_dir,
        target=args.target,
        api_key=args.api_key,
        keyed=args.keyed,
    )
    logger.info("Harvest summary: %s", json.dumps(summary, indent=1)[:2000])
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
