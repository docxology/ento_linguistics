"""Tests for OpenAlex citation enrichment (fixture-based, no live network)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import urllib.error

import data.openalex_enrichment as openalex_enrichment
from data.openalex_enrichment import (
    collect_doi_records,
    enrich_corpus,
    fetch_openalex_work,
    main,
    parse_openalex_work,
)

# ── Fixtures ────────────────────────────────────────────────────────────

WORK_JSON = {
    "id": "https://openalex.org/W123",
    "doi": "https://doi.org/10.1000/one",
    "cited_by_count": 42,
    "publication_year": 2023,
    "concepts": [
        {"display_name": "Ecosystem", "score": 0.9},
        {"display_name": "Biology", "score": 0.5},
        {"display_name": "Ecology", "score": 0.7},
        {"display_name": "Lowest", "score": 0.1},
    ],
    "open_access": {"is_oa": True, "oa_status": "gold"},
}


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Never actually sleep in tests (including retry backoff)."""
    monkeypatch.setattr(openalex_enrichment, "_sleep", lambda seconds: None)


@pytest.fixture
def corpus_dir(tmp_path: Path) -> Path:
    """Temporary corpus with two DOI-bearing and one DOI-less record."""
    abstracts = ["Abstract one.", "Abstract two.", "Abstract three."]
    provenance = {
        "_note": "test",
        "records": {
            "c" * 64: {
                "pmid": "1",
                "doi": "10.1000/one",
                "title": "Study One",
                "year": 2023,
                "journal": "J",
                "query": "superorganism",
            },
            "d" * 64: {
                "pmid": "2",
                "doi": "10.1000/gone",
                "title": "Study Two (404)",
                "year": 2022,
                "journal": "J",
                "query": "superorganism",
            },
            "e" * 64: {
                "pmid": "3",
                "doi": None,
                "title": "Study Three (no DOI)",
            },
        },
    }
    (tmp_path / "abstracts.json").write_text(json.dumps(abstracts), encoding="utf-8")
    (tmp_path / "provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    return tmp_path


@pytest.fixture
def server(httpserver):
    """Local OpenAlex stand-in URL matching ``<base>doi:<doi>`` requests."""
    httpserver.expect_request("/works/doi:10.1000/one").respond_with_json(WORK_JSON)
    httpserver.expect_request("/works/doi:10.1000/gone").respond_with_json(
        {"error": "not found"}, status=404
    )
    return httpserver.url_for("/works/doi:")


# ── Record collection ───────────────────────────────────────────────────


class TestCollectDoiRecords:
    def test_only_doi_records(self, corpus_dir):
        records = collect_doi_records(corpus_dir)
        assert set(records) == {"c" * 64, "d" * 64}
        assert records["c" * 64] == {"doi": "10.1000/one", "title": "Study One"}


# ── Fetch + parse ───────────────────────────────────────────────────────
class TestFetchOpenAlexWork:
    def test_success(self, server):
        work = fetch_openalex_work("10.1000/one", base_url=server)
        assert work["cited_by_count"] == 42

    def test_404_returns_none(self, server):
        assert fetch_openalex_work("10.1000/gone", base_url=server) is None

    def test_server_error_raises_after_retries(self, httpserver):
        httpserver.expect_request("/works/doi:10.1000/err").respond_with_data(
            "boom", status=500
        )
        with pytest.raises(urllib.error.HTTPError):
            fetch_openalex_work("10.1000/err", base_url=httpserver.url_for("/works/doi:"))

    def test_parse_top_concepts_by_score(self):
        parsed = parse_openalex_work(WORK_JSON)
        assert parsed["concepts"] == ["Ecosystem", "Ecology", "Biology"]
        assert parsed["cited_by_count"] == 42
        assert parsed["publication_year"] == 2023
        assert parsed["open_access"] == {"is_oa": True, "oa_status": "gold"}

    def test_parse_missing_fields(self):
        parsed = parse_openalex_work({})
        assert parsed == {
            "cited_by_count": None,
            "publication_year": None,
            "concepts": [],
            "open_access": {"is_oa": None, "oa_status": None},
        }


# ── Enrichment (end-to-end over the fixture server) ─────────────────────


class TestEnrichCorpus:
    def test_enrich_writes_schema(self, corpus_dir, server):
        summary = enrich_corpus(
            corpus_dir=corpus_dir, base_url=server
        )
        assert summary["fetched"] == 1
        assert summary["not_found"] == 1
        assert summary["errors"] == 0

        metadata = json.loads(
            (corpus_dir / "citation_metadata.json").read_text(encoding="utf-8")
        )
        assert set(metadata) == {"c" * 64, "d" * 64}  # DOI-less record untouched

        ok = metadata["c" * 64]
        assert ok["doi"] == "10.1000/one"
        assert ok["status"] == "ok"
        assert ok["cited_by_count"] == 42
        assert ok["concepts"] == ["Ecosystem", "Ecology", "Biology"]
        assert ok["open_access"]["is_oa"] is True

        missing = metadata["d" * 64]
        assert missing["doi"] == "10.1000/gone"
        assert missing["status"] == "not_found"

    def test_enrich_resumable(self, corpus_dir, server):
        enrich_corpus(corpus_dir=corpus_dir, base_url=server)
        # Second run: both keys already present; a new server with no
        # expectations means any HTTP request would fail the test.
        summary = enrich_corpus(corpus_dir=corpus_dir, base_url="http://127.0.0.1:1/")
        assert summary["already_fetched"] == 2
        assert summary["fetched"] == 0
        metadata = json.loads(
            (corpus_dir / "citation_metadata.json").read_text(encoding="utf-8")
        )
        assert metadata["c" * 64]["status"] == "ok"

    def test_enrich_limit(self, corpus_dir, server):
        summary = enrich_corpus(
            corpus_dir=corpus_dir, base_url=server, limit=1
        )
        assert summary["fetched"] + summary["not_found"] == 1
        metadata = json.loads(
            (corpus_dir / "citation_metadata.json").read_text(encoding="utf-8")
        )
        assert len(metadata) == 1

    def test_enrich_dry_run(self, corpus_dir, server):
        summary = enrich_corpus(
            corpus_dir=corpus_dir, base_url=server, dry_run=True
        )
        assert summary["dry_run"] is True
        assert summary["pending"] == 2
        assert not (corpus_dir / "citation_metadata.json").exists()

    def test_enrich_network_error_recorded(self, corpus_dir, httpserver):
        # Port 1: connection refused -> explicit error entries, never silent.
        summary = enrich_corpus(corpus_dir=corpus_dir, base_url="http://127.0.0.1:1/")
        assert summary["errors"] == 2
        metadata = json.loads(
            (corpus_dir / "citation_metadata.json").read_text(encoding="utf-8")
        )
        assert all(m["status"] == "error" for m in metadata.values())
        assert "error" in metadata["c" * 64]

    def test_error_entries_retried_on_resume(self, corpus_dir, httpserver):
        enrich_corpus(corpus_dir=corpus_dir, base_url="http://127.0.0.1:1/")
        # Server now answers: previously errored entries are retried.
        httpserver.expect_request("/works/doi:10.1000/one").respond_with_json(WORK_JSON)
        httpserver.expect_request("/works/doi:10.1000/gone").respond_with_json(
            {"error": "not found"}, status=404
        )
        summary = enrich_corpus(
            corpus_dir=corpus_dir, base_url=httpserver.url_for("/works/doi:")
        )
        assert summary["fetched"] == 1 and summary["not_found"] == 1
        metadata = json.loads(
            (corpus_dir / "citation_metadata.json").read_text(encoding="utf-8")
        )
        assert metadata["c" * 64]["status"] == "ok"


# ── CLI ─────────────────────────────────────────────────────────────────


class TestMain:
    def test_dry_run_flag(self, monkeypatch, corpus_dir, capsys):
        captured = {}

        def fake_enrich(**kwargs):
            captured.update(kwargs)
            return {"dry_run": True, "pending": 2, "total_doi_records": 2}

        monkeypatch.setattr(openalex_enrichment, "enrich_corpus", fake_enrich)
        rc = main(["--dry-run", "--limit", "5", "--corpus-dir", str(corpus_dir)])
        assert rc == 0
        assert captured["limit"] == 5
        assert captured["dry_run"] is True
        assert "dry-run" in capsys.readouterr().out
