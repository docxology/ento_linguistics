"""Tests for BHL historical full-text harvesting (src/data/bhl_corpus.py).

Fixture-based only: no live network.  IA/BHL responses are stubbed via
monkeypatched ``urlopen``; file persistence exercises real tmp_path
directories.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError

import pytest

from data.bhl_corpus import (
    BHL_SEARCH_QUERY,
    CORPUS_FIELDS,
    ERA_BOUNDS,
    BHLHarvester,
    build_provenance,
    era_for_year,
    harvest_bhl,
    is_relevant_bhl_record,
    parse_advancedsearch_doc,
    read_shard,
    shard_filename,
    shard_paths,
    write_shard,
)


def _search_payload(*docs: dict, num_found: int = None) -> str:
    """Render an advancedsearch response body.

    ``numFound`` defaults to the number of docs on the page; pass an
    explicit total to fixture multi-page results.
    """
    return json.dumps(
        {
            "response": {
                "numFound": num_found if num_found is not None else len(docs),
                "docs": list(docs),
            }
        }
    )


def _doc(identifier: str, year: str, title: str = "Ants") -> dict:
    """One IA search hit."""
    return {
        "identifier": identifier,
        "title": title,
        "year": year,
        "collection": ["biodiversity"],
    }


def _metadata_payload(identifier: str, date: str) -> str:
    """Render an IA metadata response with a text derivative."""
    return json.dumps(
        {
            "metadata": {
                "identifier": identifier,
                "title": "Ants",
                "date": date,
                "collection": ["biodiversity"],
            },
            "files": [
                {"name": f"{identifier}_djvu.txt"},
                {"name": f"{identifier}.pdf"},
            ],
        }
    )


class TestEraBucketing:
    @pytest.mark.parametrize(
        "year,expected",
        [
            (1850, "era_1850_1899"),
            (1899, "era_1850_1899"),
            (1900, "era_1900_1949"),
            (1949, "era_1900_1949"),
            (1950, "era_1950_1970"),
            (1970, "era_1950_1970"),
        ],
    )
    def test_in_window_years(self, year: int, expected: str):
        assert era_for_year(year) == expected

    @pytest.mark.parametrize("year", [1849, 1971, 2024])
    def test_out_of_window_years(self, year: int):
        assert era_for_year(year) is None

    def test_undatable(self):
        assert era_for_year(None) is None

    def test_bounds_are_contiguous_1850_1970(self):
        assert ERA_BOUNDS["era_1850_1899"] == (1850, 1899)
        assert ERA_BOUNDS["era_1900_1949"] == (1900, 1949)
        assert ERA_BOUNDS["era_1950_1970"] == (1950, 1970)


class TestRelevance:
    @pytest.mark.parametrize(
        "text",
        [
            "the ants foraged",
            "Formicidae diversity",
            "myrmecological notes",
            "a eusocial colony",
            "social insects of Brazil",
        ],
    )
    def test_relevant(self, text: str):
        assert is_relevant_bhl_record({"title": "x", "full_text": text})

    @pytest.mark.parametrize(
        "text", ["plant tissues", "antenna morphology", "pantry stores"]
    )
    def test_irrelevant(self, text: str):
        assert not is_relevant_bhl_record({"title": "x", "full_text": text})


class TestParseAdvancedsearch:
    def test_parses_stubs_in_order(self):
        payload = _search_payload(
            _doc("a1", "1868-01-01"),
            {"title": "no identifier here"},
            _doc("b2", "1951", title="Myrmecology"),
        )
        stubs = parse_advancedsearch_doc(payload)
        assert [s["ia_identifier"] for s in stubs] == ["a1", "b2"]
        assert stubs[0]["publication_date"] == "1868-01-01"
        assert stubs[0]["year"] == 1868
        assert stubs[1]["publication_date"] == "1951"
        assert stubs[1]["year"] == 1951

    def test_collections_list(self):
        doc = _doc("a1", "1868")
        doc["collection"] = ["biodiversity", "americanmuseumnaturalhistory"]
        stubs = parse_advancedsearch_doc(_search_payload(doc))
        assert stubs[0]["collections"] == [
            "biodiversity",
            "americanmuseumnaturalhistory",
        ]

    def test_empty_response(self):
        assert parse_advancedsearch_doc(_search_payload()) == []


class TestCheckApiKey:
    def test_keyless_reports_401_key_required(self, monkeypatch):
        def fake_urlopen(request, timeout=60):
            raise HTTPError(request.full_url, 401, "Unauthorized", None, None)

        monkeypatch.setattr("data.bhl_corpus.urlopen", fake_urlopen)
        harvester = BHLHarvester(delay=0)
        result = harvester.check_api_key()
        assert result["ok"] is False
        assert result["keyed"] is False
        assert "key required" in result["status"]
        assert "401" in result["status"]

    def test_keyed_reports_api_status(self, monkeypatch):
        def fake_urlopen(request, timeout=60):
            body = json.dumps({"Status": "unauthorized"}).encode()
            return _FakeResponse(body)

        monkeypatch.setattr("data.bhl_corpus.urlopen", fake_urlopen)
        harvester = BHLHarvester(api_key="bad-key", delay=0)
        result = harvester.check_api_key()
        assert result["ok"] is False
        assert result["keyed"] is True
        assert result["status"] == "unauthorized"

    def test_ok(self, monkeypatch):
        def fake_urlopen(request, timeout=60):
            return _FakeResponse(json.dumps({"Status": "ok"}).encode())

        monkeypatch.setattr("data.bhl_corpus.urlopen", fake_urlopen)
        result = BHLHarvester(api_key="k", delay=0).check_api_key()
        assert result["ok"] is True


class _FakeResponse:
    """Minimal context-manager response for monkeypatched urlopen."""

    def __init__(self, body: bytes):
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class TestSearchTitles:
    def _install(self, monkeypatch, pages: list[str]):
        """Serve successive search pages; record encoded URLs."""
        seen_urls: list[str] = []

        def fake_urlopen(request, timeout=120):
            seen_urls.append(request.full_url)
            return _FakeResponse(pages[len(seen_urls) - 1].encode())

        monkeypatch.setattr("data.bhl_corpus.urlopen", fake_urlopen)
        return seen_urls

    def test_single_page(self, monkeypatch):
        page = _search_payload(_doc("a1", "1868"), _doc("a2", "1901"))
        self._install(monkeypatch, [page])
        stubs = BHLHarvester(delay=0).search_titles()
        assert [s["ia_identifier"] for s in stubs] == ["a1", "a2"]

    def test_pages_until_total(self, monkeypatch):
        page1 = _search_payload(
            *[_doc(f"a{i}", "1868") for i in range(200)], num_found=201
        )
        page2 = _search_payload(_doc("b1", "1868"), num_found=201)
        seen = self._install(monkeypatch, [page1, page2])
        stubs = BHLHarvester(delay=0).search_titles()
        assert len(stubs) == 201
        assert len(seen) == 2
        # Paging advances via `start`.
        assert "start=0" in seen[0]
        assert "start=200" in seen[1]
        # fl[] encodes as repeated params (doseq), not a list literal.
        assert "fl%5B%5D=identifier" in seen[0]

    def test_query_defaults_to_bhl_query(self, monkeypatch):
        seen = self._install(monkeypatch, [_search_payload()])
        BHLHarvester(delay=0).search_titles()
        assert "collection%3A%22biodiversity%22" in seen[0]


class TestHarvestSharded:
    def _install(
        self,
        monkeypatch,
        search_page: str,
        metadata_by_id: dict,
        texts_by_id: dict,
        metadata_404: set = (),
    ):
        """Serve search, metadata, and full-text requests from fixtures."""

        def fake_urlopen(request, timeout=120):
            url = request.full_url
            if "biodiversitylibrary.org/api3" in url:
                # Keyless BHL API: the documented unauthorized verdict.
                return _FakeResponse(
                    b'{"Status": "unauthorized", '
                    b'"ErrorMessage": "unauthorized API key."}'
                )
            if "advancedsearch" in url:
                return _FakeResponse(search_page.encode())
            if "/metadata/" in url:
                identifier = url.rsplit("/metadata/", 1)[1]
                if identifier in metadata_404:
                    raise HTTPError(url, 404, "Not Found", None, None)
                return _FakeResponse(metadata_by_id[identifier].encode())
            if "/download/" in url:
                identifier = url.split("/download/")[1].rsplit("/", 1)[0]
                text = texts_by_id.get(identifier)
                if text is None:
                    raise HTTPError(url, 404, "Not Found", None, None)
                return _FakeResponse(text.encode())
            raise AssertionError(f"unexpected URL: {url}")

        monkeypatch.setattr("data.bhl_corpus.urlopen", fake_urlopen)

    def test_end_to_end_shards_and_provenance(self, monkeypatch, tmp_path):
        page = _search_payload(
            _doc("ant1868", "1868-06-01"),
            _doc("ant1931", "1931"),
            _doc("ant1965", "1965-12-17"),
            _doc("out1980", "1980"),
        )
        texts = {
            "ant1868": "On the habits of ants, a social insect study. " * 5,
            "ant1931": "The colony of ants exhibits eusocial organization. " * 5,
            "ant1965": "Formicidae of the southwest. " * 5,
            "out1980": "Formicidae outside the window. " * 5,
        }
        metadata = {
            f"{k}": _metadata_payload(k, d)
            for k, d in (("ant1868", "1868-06-01"), ("ant1931", "1931"),
                         ("ant1965", "1965-12-17"), ("out1980", "1980"))
        }
        self._install(monkeypatch, page, metadata, texts)
        data_dir = tmp_path / "bhl"
        harvester = BHLHarvester(delay=0)
        summary = harvester.harvest_sharded(
            data_dir, data_dir / "provenance.json"
        )
        assert summary["candidates"] == 4
        assert summary["harvested"] == 3
        assert summary["out_of_window"] == 1
        shards = shard_paths(data_dir)
        records = [r for p in shards for r in read_shard(p)]
        eras = sorted(r["era"] for r in records)
        assert eras == [
            "era_1850_1899",
            "era_1900_1949",
            "era_1950_1970",
        ]
        provenance = json.loads(
            (data_dir / "provenance.json").read_text(encoding="utf-8")
        )
        assert len(provenance) == 3
        entry = next(iter(provenance.values()))
        assert set(entry) >= {
            "bhl_id", "ia_identifier", "title", "publication_date",
            "era", "collections", "url", "query",
        }
        assert entry["query"] == BHL_SEARCH_QUERY
        for record in records:
            assert set(record) == set(CORPUS_FIELDS)

    def test_is_resumable(self, monkeypatch, tmp_path):
        page = _search_payload(_doc("ant1868", "1868"), _doc("ant1931", "1931"))
        texts = {
            "ant1868": "ants ants ants",
            "ant1931": "ants again but stored",
        }
        metadata = {
            "ant1868": _metadata_payload("ant1868", "1868"),
            "ant1931": _metadata_payload("ant1931", "1931"),
        }
        data_dir = tmp_path / "bhl"
        self._install(monkeypatch, page, metadata, texts)
        harvester = BHLHarvester(delay=0)
        first = harvester.harvest_sharded(
            data_dir, data_dir / "provenance.json", target=1
        )
        assert first["harvested"] == 1
        second = harvester.harvest_sharded(
            data_dir, data_dir / "provenance.json"
        )
        assert second["harvested"] == 1
        assert second["already_stored"] == 1
        records = [
            r for p in shard_paths(data_dir) for r in read_shard(p)
        ]
        assert len(records) == 2

    def test_shard_fill_boundary(self, monkeypatch, tmp_path):
        ids = [f"item{i:02d}" for i in range(5)]
        page = _search_payload(*[_doc(i, "1868") for i in ids])
        texts = {i: f"ants {i} " * 10 for i in ids}
        metadata = {i: _metadata_payload(i, "1868") for i in ids}
        data_dir = tmp_path / "bhl"
        self._install(monkeypatch, page, metadata, texts)
        harvester = BHLHarvester(delay=0)
        # Force a tiny shard size so one run fills and spills a shard.
        monkeypatch.setattr("data.bhl_corpus.SHARD_SIZE", 2)
        summary = harvester.harvest_sharded(
            data_dir, data_dir / "provenance.json"
        )
        assert summary["harvested"] == 5
        shards = shard_paths(data_dir)
        sizes = [len(read_shard(p)) for p in shards]
        assert all(size <= 2 for size in sizes)
        assert sum(sizes) == 5

    def test_failed_item_is_skipped(self, monkeypatch, tmp_path):
        page = _search_payload(_doc("good", "1868"), _doc("gone", "1868"))
        texts = {"good": "ants good"}
        metadata = {"good": _metadata_payload("good", "1868")}
        self._install(
            monkeypatch, page, metadata, texts, metadata_404={"gone"}
        )
        data_dir = tmp_path / "bhl"
        summary = BHLHarvester(delay=0).harvest_sharded(
            data_dir, data_dir / "provenance.json"
        )
        assert summary["harvested"] == 1
        assert summary["failed_items"] == 1

    def test_no_text_derivative_counted(self, monkeypatch, tmp_path):
        page = _search_payload(_doc("notext", "1868"), _doc("good", "1869"))
        texts = {"good": "ants good"}
        metadata = {
            "notext": json.dumps(
                {
                    "metadata": {"date": "1868"},
                    "files": [{"name": "notext.pdf"}],
                }
            ),
            "good": _metadata_payload("good", "1869"),
        }
        self._install(monkeypatch, page, metadata, texts)
        data_dir = tmp_path / "bhl"
        summary = BHLHarvester(delay=0).harvest_sharded(
            data_dir, data_dir / "provenance.json"
        )
        assert summary["no_text_derivative"] == 1
        assert summary["harvested"] == 1

    def test_irrelevant_text_dropped(self, monkeypatch, tmp_path):
        page = _search_payload(_doc("plant", "1868", title="Mosses of Norway"))
        texts = {"plant": "mosses and liverworts of Norway " * 10}
        metadata = {"plant": _metadata_payload("plant", "1868")}
        self._install(monkeypatch, page, metadata, texts)
        data_dir = tmp_path / "bhl"
        summary = BHLHarvester(delay=0).harvest_sharded(
            data_dir, data_dir / "provenance.json"
        )
        assert summary["harvested"] == 0
        assert summary["irrelevant"] == 1


class TestPersistence:
    def test_shard_filename_zero_pads(self):
        assert shard_filename(1) == "bhl_shard_00001.json"

    def test_read_shard_missing(self, tmp_path):
        assert read_shard(tmp_path / "absent.json") == []

    def test_write_then_read_roundtrip(self, tmp_path):
        path = tmp_path / "shard.json"
        write_shard(path, [{"ia_identifier": "a", "era": "era_1850_1899"}])
        assert read_shard(path)[0]["ia_identifier"] == "a"

    def test_shard_paths_sorted(self, tmp_path):
        write_shard(tmp_path / "bhl_shard_00002.json", [])
        write_shard(tmp_path / "bhl_shard_00001.json", [])
        assert [p.name for p in shard_paths(tmp_path)] == [
            "bhl_shard_00001.json",
            "bhl_shard_00002.json",
        ]

    def test_build_provenance_digests(self):
        records = [
            {"ia_identifier": "a", "full_text": "x", "era": "era_1850_1899"},
            {"ia_identifier": "b", "full_text": "y", "era": "era_1900_1949"},
        ]
        import hashlib

        provenance = build_provenance(records, "Q", "2026-09-16T00:00:00+00:00")
        assert len(provenance) == 2
        assert set(provenance) == {
            hashlib.sha256(b"x").hexdigest(),
            hashlib.sha256(b"y").hexdigest(),
        }
        assert all(e["query"] == "Q" for e in provenance.values())


class TestHarvestBhlWrapper:
    def test_wrapper_runs_and_writes_readme(self, monkeypatch, tmp_path):
        page = _search_payload(_doc("a1", "1868"))
        texts = {"a1": "ants a1"}
        metadata = {"a1": _metadata_payload("a1", "1868")}

        def fake_urlopen(request, timeout=120):
            url = request.full_url
            if "biodiversitylibrary.org/api3" in url:
                return _FakeResponse(
                    b'{"Status": "unauthorized", '
                    b'"ErrorMessage": "unauthorized API key."}'
                )
            if "advancedsearch" in url:
                return _FakeResponse(page.encode())
            if "/metadata/" in url:
                return _FakeResponse(metadata["a1"].encode())
            if "/download/" in url:
                return _FakeResponse(texts["a1"].encode())
            raise AssertionError(url)

        monkeypatch.setattr("data.bhl_corpus.urlopen", fake_urlopen)
        data_dir = tmp_path / "bhl"
        summary = harvest_bhl(data_dir=data_dir)
        assert summary["harvested"] == 1
        readme = (data_dir / "README.md").read_text(encoding="utf-8")
        assert "collection:\"biodiversity\"" in readme
        assert BHL_SEARCH_QUERY in readme
        assert "1 new documents" in readme
