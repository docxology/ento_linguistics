"""Tests for the arXiv preprint layer (fixture-based, no live network)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import data.arxiv_corpus as arxiv_corpus
from data.arxiv_corpus import (
    ARXIV_QUERIES,
    EnrichedArXivMiner,
    abstract_key,
    build_record,
    dedupe_against_pubmed,
    harvest_arxiv,
    load_pubmed_keys,
    main,
    normalize_title,
)

# ── Fixtures ────────────────────────────────────────────────────────────

FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:ax="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v2</id>
    <title>Collective Foraging in Ant Colonies</title>
    <author><name>A. Author</name></author>
    <author><name>B. Author</name></author>
    <summary>Ant colonies coordinate foraging with pheromone trails and
    division of labor.</summary>
    <published>2024-01-15T00:00:00Z</published>
    <ax:primary_category term="q-bio.PE"/>
    <category term="q-bio.PE"/>
    <ax:doi>10.9999/ant-doi-1</ax:doi>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2402.00002v1</id>
    <title>Superorganism Homeostasis</title>
    <author><name>C. Author</name></author>
    <summary>The colony behaves as a superorganism regulating nest
    temperature.</summary>
    <published>2024-02-20T00:00:00Z</published>
    <category term="nlin.AO"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2403.00003v1</id>
    <title>Concrete Rheology Measurements</title>
    <author><name>D. Author</name></author>
    <summary>We measure the viscosity of fresh concrete mixtures.</summary>
    <published>2024-03-01T00:00:00Z</published>
    <category term="physics.flu-dyn"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2404.00004v1</id>
    <title>Duplicate Foraging Study</title>
    <author><name>E. Author</name></author>
    <summary>Ant colonies coordinate foraging with pheromone trails and
    division of labor.</summary>
    <published>2024-04-01T00:00:00Z</published>
    <category term="q-bio.PE"/>
  </entry>
</feed>
"""


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Never actually sleep in tests."""
    monkeypatch.setattr(arxiv_corpus, "_sleep", lambda seconds: None)


@pytest.fixture
def miner(httpserver) -> EnrichedArXivMiner:
    """EnrichedArXivMiner pointed at a local fixture server serving FEED_XML."""
    httpserver.expect_request("/api/query").respond_with_data(
        FEED_XML, content_type="application/xml"
    )
    miner = EnrichedArXivMiner()
    miner.BASE_URL = httpserver.url_for("/api/query?")
    return miner


@pytest.fixture
def corpus_dir(tmp_path: Path) -> Path:
    """Temporary corpus dir with a small PubMed abstracts + provenance pair."""
    abstracts = [
        "Published abstract about nestmate recognition in ants " * 3,
    ]
    provenance = {
        "_note": "test",
        "records": {
            "a" * 64: {
                "pmid": "1",
                "doi": "10.1000/pubmed-doi",
                "title": "A Published Study of Ant Workers",
                "year": 2023,
                "journal": "Journal",
                "query": "kin_recognition",
            },
            "b" * 64: {
                "pmid": "2",
                "doi": None,
                "title": "A Second Study Without DOI",
                "year": 2022,
                "journal": "Journal",
                "query": "kin_recognition",
            },
        },
    }
    (tmp_path / "abstracts.json").write_text(json.dumps(abstracts), encoding="utf-8")
    (tmp_path / "provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    return tmp_path


# ── Text normalization ──────────────────────────────────────────────────


class TestNormalization:
    def test_normalize_title(self):
        assert normalize_title("  Colony\tOrganization  in  Ants ") == (
            "colony organization in ants"
        )

    def test_abstract_key_truncates(self):
        assert len(abstract_key("word " * 200)) == 100

    def test_abstract_key_normalizes_whitespace(self):
        assert abstract_key("The  Argentine\nant") == "the argentine ant"


# ── Record building ─────────────────────────────────────────────────────


class TestBuildRecord:
    def test_valid_record(self):
        record = build_record(
            {
                "arxiv_id": "2401.00001",
                "doi": "10.9999/x",
                "title": "T",
                "abstract": "A",
                "primary_category": "q-bio.PE",
                "published": "2024-01-15T00:00:00Z",
                "authors": ["A"],
            }
        )
        assert record is not None
        assert set(record) == {
            "arxiv_id",
            "doi",
            "title",
            "abstract",
            "primary_category",
            "published",
            "authors",
        }

    def test_missing_id_rejected(self):
        assert build_record({"title": "T", "abstract": "A"}) is None

    def test_missing_title_rejected(self):
        assert build_record({"arxiv_id": "x", "abstract": "A"}) is None

    def test_missing_abstract_rejected(self):
        assert build_record({"arxiv_id": "x", "title": "T"}) is None


# ── Miner parsing over the fixture server ───────────────────────────────


class TestEnrichedArXivMiner:
    def test_search_full_parses_arxiv_fields(self, miner):
        records = miner.search_full("test", max_results=10)
        assert len(records) == 4
        first = records[0]
        assert first["arxiv_id"] == "2401.00001"  # version stripped
        assert first["primary_category"] == "q-bio.PE"
        assert first["published"] == "2024-01-15T00:00:00Z"
        assert first["doi"] == "10.9999/ant-doi-1"  # ax-namespace doi found
        assert first["authors"] == ["A. Author", "B. Author"]

    def test_category_fallback(self, miner):
        # Entry 2 has no ax:primary_category, only an Atom <category>.
        records = miner.search_full("test")
        assert records[1]["primary_category"] == "nlin.AO"
        assert records[1]["doi"] is None

    def test_error_returns_empty(self, httpserver):
        httpserver.expect_request("/api/query").respond_with_data("boom", status=500)
        miner = EnrichedArXivMiner()
        miner.BASE_URL = httpserver.url_for("/api/query?")
        assert miner.search_full("test") == []


# ── PubMed dedupe ───────────────────────────────────────────────────────


class TestPubmedDedupe:
    def test_load_pubmed_keys(self, corpus_dir):
        keys = load_pubmed_keys(corpus_dir)
        assert "10.1000/pubmed-doi" in keys["dois"]
        assert normalize_title("A Published Study of Ant Workers") in keys["titles"]
        assert keys["abstract_keys"]  # from abstracts.json strings

    def test_doi_overlap_dropped(self, corpus_dir):
        keys = load_pubmed_keys(corpus_dir)
        record = {"doi": "10.1000/PUBMED-DOI", "title": "Unrelated", "abstract": "x"}
        kept, dupes = dedupe_against_pubmed([record], keys)
        assert kept == []
        assert len(dupes) == 1

    def test_title_overlap_dropped(self, corpus_dir):
        keys = load_pubmed_keys(corpus_dir)
        record = {
            "doi": None,
            "title": "a published study of ANT workers",
            "abstract": "x",
        }
        kept, _ = dedupe_against_pubmed([record], keys)
        assert kept == []

    def test_abstract_prefix_overlap_dropped(self, corpus_dir):
        keys = load_pubmed_keys(corpus_dir)
        record = {
            "doi": None,
            "title": "Unrelated title",
            "abstract": "Published abstract about nestmate recognition in ants " * 3,
        }
        kept, _ = dedupe_against_pubmed([record], keys)
        assert kept == []

    def test_new_record_kept(self, corpus_dir):
        keys = load_pubmed_keys(corpus_dir)
        record = {
            "doi": "10.5555/new",
            "title": "Novel stigmergy model",
            "abstract": "A brand new model of stigmergy in robot swarms.",
        }
        kept, dupes = dedupe_against_pubmed([record], keys)
        assert kept == [record]
        assert dupes == []


# ── Harvest (end-to-end over the fixture server) ────────────────────────


class TestHarvest:
    def test_harvest_writes_records_and_provenance(self, corpus_dir, miner):
        records, provenance, stats = harvest_arxiv(
            target=10, corpus_dir=corpus_dir, miner=miner
        )
        # Off-topic "Concrete Rheology" filtered; no internal dupes.
        assert [r["arxiv_id"] for r in records] == ["2401.00001", "2402.00002"]
        record = records[0]
        assert set(record) == {
            "arxiv_id",
            "doi",
            "title",
            "abstract",
            "primary_category",
            "published",
            "authors",
        }
        # Provenance: sha256-of-abstract keys with query attribution.
        assert len(provenance["records"]) == 2
        import hashlib

        sha = hashlib.sha256(records[0]["abstract"].encode("utf-8")).hexdigest()
        assert provenance["records"][sha]["arxiv_id"] == "2401.00001"
        assert provenance["records"][sha]["query"] == "ant_colonies"
        assert ARXIV_QUERIES == provenance["queries"]
        assert stats["new"] == 2 and stats["total"] == 2

        on_disk = json.loads(
            (corpus_dir / "arxiv_records.json").read_text(encoding="utf-8")
        )
        assert on_disk == records
        prov_disk = json.loads(
            (corpus_dir / "arxiv_provenance.json").read_text(encoding="utf-8")
        )
        assert prov_disk["records"] == provenance["records"]

    def test_harvest_dedupes_internally(self, corpus_dir, miner):
        # Entry 4 duplicates entry 1's abstract text -> dropped.
        records, _, stats = harvest_arxiv(
            target=10, corpus_dir=corpus_dir, miner=miner
        )
        ids = [r["arxiv_id"] for r in records]
        assert len(ids) == len(set(ids))
        assert "2404.00004" not in ids

    def test_harvest_resumable(self, corpus_dir, miner):
        first, provenance, _ = harvest_arxiv(target=10, corpus_dir=corpus_dir, miner=miner)
        # Re-run: everything already fetched, nothing new.
        second, provenance2, stats = harvest_arxiv(
            target=10, corpus_dir=corpus_dir, miner=miner
        )
        assert stats["existing"] == len(first)
        assert stats["new"] == 0
        assert second == first
        # Provenance must keep covering every record across runs.
        import hashlib

        expected_shas = {
            hashlib.sha256(r["abstract"].encode("utf-8")).hexdigest() for r in second
        }
        assert set(provenance2["records"]) == expected_shas

    def test_harvest_dry_run_writes_nothing(self, corpus_dir, miner):
        records, _, stats = harvest_arxiv(
            target=10, corpus_dir=corpus_dir, miner=miner, dry_run=True
        )
        assert records and stats["new"] > 0
        assert not (corpus_dir / "arxiv_records.json").exists()
        assert not (corpus_dir / "arxiv_provenance.json").exists()

    def test_harvest_target_cap(self, corpus_dir, miner):
        records, _, stats = harvest_arxiv(target=1, corpus_dir=corpus_dir, miner=miner)
        assert stats["new"] == 1
        assert len(records) == 1


# ── CLI ─────────────────────────────────────────────────────────────────


class TestMain:
    def test_dry_run_flag(self, monkeypatch, corpus_dir, capsys):
        captured = {}

        def fake_harvest(**kwargs):
            captured.update(kwargs)
            return [], {"records": {}}, {
                "existing": 0,
                "new": 0,
                "total": 0,
                "query_stats": {},
            }

        monkeypatch.setattr(arxiv_corpus, "harvest_arxiv", fake_harvest)
        rc = main(["--dry-run", "--target", "5", "--corpus-dir", str(corpus_dir)])
        assert rc == 0
        assert captured["target"] == 5
        assert captured["dry_run"] is True
        assert "dry-run" in capsys.readouterr().out
