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
    "dedupe_by_pmcid",
    "is_relevant",
    "parse_article",
    "parse_fulltext_xml",
    "write_corpus",
    "write_readme",
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

    front = first_any(article, "front") or article
    ids = _article_ids(article)

    year_text = _text(
        _first_descendant(first_any(front, "pub-date") or article, "year")
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

    provenance: Dict[str, Any] = {}
    for record in corpus:
        digest = hashlib.sha256(
            (record["body_text"] or "").encode("utf-8")
        ).hexdigest()
        provenance[digest] = {
            "pmcid": record["pmcid"],
            "doi": record["doi"],
            "query": query,
            "retrieved_at": retrieved_at,
        }

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


def write_readme(
    records: List[Dict[str, Any]],
    output_dir: Path,
    query: str = PMC_SEARCH_QUERY,
) -> Path:
    """Write ``README.md`` documenting the harvested corpus.

    Records the search query verbatim, the applied filters, license
    coverage computed from the actual records, and the reproduction
    command.

    Args:
        records: Harvested corpus records.
        output_dir: Corpus directory receiving ``README.md``.
        query: Verbatim search query.

    Returns:
        The README path.
    """
    license_counts: Dict[str, int] = {}
    years = [r["year"] for r in records if isinstance(r.get("year"), int)]
    journals = {r.get("journal") or "unknown" for r in records}
    for record in records:
        license_counts[record.get("license") or "unknown"] = (
            license_counts.get(record.get("license") or "unknown", 0) + 1
        )
    license_lines = "\n".join(
        f"- `{license}`: {count} documents"
        for license, count in sorted(
            license_counts.items(), key=lambda item: (-item[1], item[0])
        )
    )
    year_line = (
        f"{min(years)}–{max(years)}" if years else "n/a"
    )
    readme = f"""# PMC Open-Access Full-Text Corpus (parallel layer)

Parallel analysis layer harvested from PubMed Central via the
E-utilities; the abstract corpus (`data/corpus/abstracts.json`) remains
the headline corpus.

## Files

- `fulltexts.json` — JSON list of full-text records
  (`pmcid`, `doi`, `title`, `year`, `journal`, `license`, `abstract`,
  `body_text`).
- `provenance.json` — sidecar mapping `sha256(body_text)` to
  `{{pmcid, doi, query, retrieved_at}}`.
- `README.md` — this document.

## Search query (verbatim)

```
{query}
```

Applied against `esearch db=pmc` with `retmode=json`,
`sort=relevance`, `retmax=600`, and the project's NCBI `tool`/`email`
identification.  The `open access[Filter]` clause restricts hits to the
PMC open-access subset, so every hit has a retrievable full text.

## Filters

1. esearch relevance ranking over `{query}`.
2. `efetch db=pmc retmode=xml` in batches of
   {PMCFulltextHarvester.BATCH_SIZE} PMCIDs, spaced
   {PMCFulltextHarvester.REQUEST_DELAY}s apart (NCBI politeness).
3. Record kept only when: PMCID resolves in the response, the article
   has a non-empty body, and a word-boundary relevance term
   (ant/ants, Formicidae, myrmecology*, eusocial/eusociality,
   social insects, Formicinae, Myrmicinae, Dorylinae, Linepithema,
   Solenopsis) occurs in title/abstract/body.
4. Duplicates dropped by PMCID (first occurrence kept).
5. Target cap: 500 documents.

## Coverage ({len(records)} documents)

- Publication years: {year_line}
- Distinct journals: {len(journals)}
- License coverage:

{license_lines}

## Reproduction

```bash
uv run python src/data/pmc_fulltext.py --target 500
```

The analysis layer is built separately:

```bash
uv run python src/pipeline/fulltext_pipeline.py
```
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "README.md"
    path.write_text(readme, encoding="utf-8")
    return path


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point: harvest the PMC full-text corpus.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--target", type=int, default=500, help="Number of full texts to harvest"
    )
    parser.add_argument(
        "--retmax", type=int, default=600, help="esearch candidate cap"
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
    harvester = PMCFulltextHarvester()
    records = harvester.harvest(target=args.target, retmax=args.retmax)
    write_corpus(
        records,
        corpus_path=output_dir / "fulltexts.json",
        provenance_path=output_dir / "provenance.json",
        query=PMC_SEARCH_QUERY,
    )
    write_readme(records, output_dir, query=PMC_SEARCH_QUERY)
    print(f"Harvested {len(records)} full texts into {output_dir}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
