"""OpenAlex citation enrichment for the Ento-Linguistic PubMed corpus.

For every DOI-bearing record in the corpus (DOIs come from
``data/corpus/provenance.json``), queries the OpenAlex API
(``https://api.openalex.org/works/doi:<doi>``, polite pool via ``mailto``)
and stores citation metadata in ``data/corpus/citation_metadata.json``.

Output schema (keys are the SHA-256 of the record's abstract string, matching
``provenance.json``; the DOI is carried inside each entry)::

    {
      "<sha256>": {
        "doi": "10.1234/example",
        "status": "ok",
        "cited_by_count": 42,
        "publication_year": 2023,
        "concepts": ["Ecosystem", "Biology", "Ecology"],
        "open_access": {"is_oa": true, "oa_status": "gold"},
        "fetched_at": "2026-09-16T12:00:00+00:00"
      },
      "<sha256>": {"doi": "10.9999/gone", "status": "not_found",
                   "checked_at": "2026-09-16T12:00:01+00:00"}
    }

``not_found`` (OpenAlex 404) and ``error`` (network failure after retries)
are recorded as explicit entries — no DOI is ever silently skipped.

The enrichment is **resumable**: SHA-256 keys already present in the output
file are skipped on re-run, and the file is rewritten after every record, so
an interrupted run can simply be restarted.

Usage (from the project root)::

    python -m data.openalex_enrichment                 # full run (536 DOIs)
    python -m data.openalex_enrichment --limit 10      # first 10 only
    python -m data.openalex_enrichment --dry-run       # plan only, no fetches
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "DEFAULT_MAILTO",
    "OPENALEX_API",
    "collect_doi_records",
    "enrich_corpus",
    "fetch_openalex_work",
    "main",
]

OPENALEX_API = "https://api.openalex.org/works/doi:"
DEFAULT_MAILTO = "daniel@activeinference.institute"
CORPUS_DIR = Path(__file__).resolve().parents[2] / "data" / "corpus"

_CONCEPTS_TOP_N = 3
_RETRIES = 3
_RETRY_BACKOFF_S = 2.0


def _utcnow() -> str:
    """Current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sleep(seconds: float) -> None:
    """Rate-limit hook (patchable in tests)."""
    if seconds > 0:
        time.sleep(seconds)


def collect_doi_records(corpus_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Collect DOI-bearing corpus records from ``provenance.json``.

    Args:
        corpus_dir: Directory containing ``provenance.json``.

    Returns:
        Mapping of abstract SHA-256 (as used in ``provenance.json``) to
        ``{"doi": ..., "title": ...}`` for every record that has a DOI.
    """
    provenance = json.loads(
        (corpus_dir / "provenance.json").read_text(encoding="utf-8")
    )
    doi_records: Dict[str, Dict[str, Any]] = {}
    for sha256, record in provenance.get("records", {}).items():
        doi = (record.get("doi") or "").strip()
        if doi:
            doi_records[sha256] = {"doi": doi, "title": record.get("title")}
    return doi_records


def fetch_openalex_work(
    doi: str,
    mailto: str = DEFAULT_MAILTO,
    base_url: str = OPENALEX_API,
    timeout: float = 30.0,
) -> Optional[Dict[str, Any]]:
    """Fetch one OpenAlex work by DOI.

    Args:
        doi: DOI string (without ``doi:`` prefix).
        mailto: Contact address for the OpenAlex polite pool.
        base_url: API base URL (overridable for tests).
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON dict, or ``None`` on HTTP 404 (DOI unknown to OpenAlex).
        Other HTTP errors are retried, then re-raised.

    Raises:
        urllib.error.HTTPError / URLError: On non-404 failure after retries.
    """
    url = f"{base_url}{doi}?mailto={mailto}"
    request = urllib.request.Request(
        url, headers={"User-Agent": f"EntoLinguisticResearch/1.0 (mailto:{mailto})"}
    )
    last_error: Optional[Exception] = None
    for attempt in range(_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            last_error = exc
        except urllib.error.URLError as exc:
            last_error = exc
        if attempt < _RETRIES - 1:
            _sleep(_RETRY_BACKOFF_S * (attempt + 1))
    assert last_error is not None
    raise last_error


def parse_openalex_work(work: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the enrichment fields we keep from an OpenAlex work payload.

    Args:
        work: Parsed JSON from the OpenAlex ``/works/doi:`` endpoint.

    Returns:
        Dict with ``cited_by_count``, ``publication_year``, ``concepts``
        (top 3 concept display names by score), and ``open_access``
        (``is_oa`` + ``oa_status``).
    """
    concepts_raw = sorted(
        (c for c in work.get("concepts") or [] if c.get("display_name")),
        key=lambda c: c.get("score") or 0.0,
        reverse=True,
    )
    oa = work.get("open_access") or {}
    return {
        "cited_by_count": work.get("cited_by_count"),
        "publication_year": work.get("publication_year"),
        "concepts": [c["display_name"] for c in concepts_raw[:_CONCEPTS_TOP_N]],
        "open_access": {"is_oa": oa.get("is_oa"), "oa_status": oa.get("oa_status")},
    }


def enrich_corpus(
    corpus_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
    mailto: str = DEFAULT_MAILTO,
    base_url: str = OPENALEX_API,
    sleep_s: float = 0.2,
    limit: Optional[int] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Enrich all DOI-bearing corpus records with OpenAlex metadata.

    Resumable: SHA-256 keys already present in the output file are skipped and
    the file is rewritten after each fetched record, so interrupted runs can
    be restarted safely.

    Args:
        corpus_dir: Directory with ``provenance.json`` (default: project corpus).
        output_path: Output file (default: ``<corpus_dir>/citation_metadata.json``).
        sleep_s: Seconds to sleep between API calls.
        limit: Maximum number of records to fetch this run (``None`` = all).
        dry_run: If true, report the plan without fetching or writing.

        ``ok`` and ``not_found`` entries are skipped on resume; ``error``
        entries are retried.

    Returns:
        Summary dict with ``total_doi_records``, ``already_fetched``,
        ``fetched``, ``not_found``, ``errors``, and (unless dry-run)
        ``output``.
    """
    corpus_dir = Path(corpus_dir) if corpus_dir else CORPUS_DIR
    output_path = Path(output_path) if output_path else corpus_dir / "citation_metadata.json"

    doi_records = collect_doi_records(corpus_dir)

    existing: Dict[str, Dict[str, Any]] = {}
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))

    pending = {
        k: v
        for k, v in doi_records.items()
        if k not in existing or existing[k].get("status") == "error"
    }
    summary: Dict[str, Any] = {
        "total_doi_records": len(doi_records),
        "already_fetched": len(doi_records) - len(pending),
        "fetched": 0,
        "not_found": 0,
        "errors": 0,
    }

    if dry_run:
        summary["dry_run"] = True
        summary["pending"] = len(pending)
        return summary

    metadata: Dict[str, Dict[str, Any]] = dict(existing)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for index, (sha256, info) in enumerate(pending.items()):
        if limit is not None and summary["fetched"] + summary["not_found"] + summary["errors"] >= limit:
            break
        doi = info["doi"]
        try:
            work = fetch_openalex_work(doi, mailto=mailto, base_url=base_url)
        except Exception as exc:  # noqa: BLE001 - recorded explicitly, never skipped
            metadata[sha256] = {
                "doi": doi,
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "checked_at": _utcnow(),
            }
            summary["errors"] += 1
        else:
            if work is None:
                metadata[sha256] = {
                    "doi": doi,
                    "status": "not_found",
                    "checked_at": _utcnow(),
                }
                summary["not_found"] += 1
            else:
                entry = {"doi": doi, "status": "ok", **parse_openalex_work(work)}
                entry["fetched_at"] = _utcnow()
                metadata[sha256] = entry
                summary["fetched"] += 1
        # Rewrite after every record so an interrupted run stays resumable.
        output_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        if index < len(pending) - 1:
            _sleep(sleep_s)

    summary["output"] = str(output_path)
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for OpenAlex citation enrichment."""
    parser = argparse.ArgumentParser(
        description="Enrich corpus DOIs with OpenAlex citation metadata."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max records to fetch this run (default: all pending).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Seconds between API calls (default: 0.2).",
    )
    parser.add_argument(
        "--mailto",
        type=str,
        default=DEFAULT_MAILTO,
        help="Contact address for the OpenAlex polite pool.",
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
        help="Report the plan without fetching or writing.",
    )
    args = parser.parse_args(argv)

    summary = enrich_corpus(
        corpus_dir=args.corpus_dir,
        mailto=args.mailto,
        sleep_s=args.sleep,
        limit=args.limit,
        dry_run=args.dry_run,
    )
    mode = "dry-run" if args.dry_run else "done"
    print(f"OpenAlex enrichment [{mode}]: {json.dumps(summary, default=str)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
