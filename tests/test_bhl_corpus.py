"""Tests for BHL historical full-text harvesting (src/data/bhl_corpus.py).

Fixture-based only: no live network.  IA/BHL responses are stubbed via
monkeypatched ``urlopen`` (keyless paths) and ``pytest_httpserver``
fixtures (keyed SearchInside paths); file persistence exercises real
tmp_path directories.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError

import pytest
from werkzeug.wrappers import Response

from data.bhl_corpus import (
    BHL_KEYED_QUERY,
    BHL_SEARCH_QUERY,
    CORPUS_FIELDS,
    ERA_BOUNDS,
    BHLHarvester,
    build_provenance,
    era_for_year,
    harvest_bhl,
    is_relevant_bhl_record,
    parse_advancedsearch_doc,
    parse_publication_search_doc,
    read_shard,
    shard_filename,
    shard_paths,
    write_readme,
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


# ── Keyed SearchInside (BHL API v3) tests ─────────────────────────────

FAKE_KEY = "test-key-1234"


def _ok(result) -> dict:
    """Render a successful BHL API v3 response body."""
    return {"Status": "ok", "ErrorMessage": None, "Result": result}


def _pub_item(item_id: int, date: str, title: str = "Ants") -> dict:
    """One PublicationSearch Item hit."""
    return {
        "BHLType": "Item",
        "FoundIn": "Both",
        "ItemID": str(item_id),
        "Title": title,
        "PublicationDate": date,
    }


def _pub_part(part_id: int, date: str, title: str = "Ants part") -> dict:
    """One PublicationSearch Part hit."""
    return {
        "BHLType": "Part",
        "FoundIn": "Both",
        "PartID": str(part_id),
        "Title": title,
        "Date": date,
    }


def _serve_api(httpserver, responses: list, calls: list) -> None:
    """Queue ordered ``/api3`` JSON responses and record request params."""

    for response in responses:

        def handler(request, _response=response):
            calls.append(
                {key: request.args.get(key) for key in request.args.keys()}
            )
            return Response(
                json.dumps(_response), content_type="application/json"
            )

        httpserver.expect_oneshot_request("/api3").respond_with_handler(
            handler
        )


@pytest.fixture
def bhl_api(monkeypatch, httpserver):
    """Point the BHL API base at the local httpserver."""
    monkeypatch.setattr(
        "data.bhl_corpus.BHL_API_BASE", httpserver.url_for("api3")
    )
    return httpserver


class TestParsePublicationSearchDoc:
    def test_keeps_items_parts_in_order(self):
        payload = json.dumps(
            _ok(
                [
                    _pub_item(7, "1868", "On ants"),
                    _pub_part(9, "1901-05"),
                ]
            )
        )
        stubs = parse_publication_search_doc(payload)
        assert stubs == [
            {
                "bhl_type": "Item",
                "item_id": 7,
                "part_id": None,
                "title": "On ants",
                "publication_date": "1868",
                "year": 1868,
                "found_in": "Both",
            },
            {
                "bhl_type": "Part",
                "item_id": None,
                "part_id": 9,
                "title": "Ants part",
                "publication_date": "1901-05",
                "year": 1901,
                "found_in": "Both",
            },
        ]

    def test_skips_unresolvable_and_undated(self):
        payload = json.dumps(
            _ok(
                [
                    {"BHLType": "Title", "TitleID": "3"},
                    {"BHLType": "Item", "Title": "no id"},
                    {"BHLType": "Part", "Title": "no date"},  # undated
                ]
            )
        )
        stubs = parse_publication_search_doc(payload)
        assert stubs == []

    def test_empty_result(self):
        assert parse_publication_search_doc(json.dumps(_ok(None))) == []


class TestSearchInside:
    def test_pages_filters_and_params(self, bhl_api):
        page1 = _ok([_pub_item(1, "1868"), _pub_part(2, "1901")])
        page2 = _ok(
            [
                _pub_part(3, "1975"),  # outside 1850-1970 window
                {"BHLType": "Part", "Title": "undated"},  # undated
            ]
        )
        calls: list = []
        _serve_api(bhl_api, [page1, page2], calls)
        pubs, truncated = BHLHarvester(
            api_key=FAKE_KEY, delay=0
        ).search_inside("Formicidae", date_from=1850, date_to=1970, rows=2)
        assert truncated is False
        assert [p["year"] for p in pubs] == [1868, 1901]
        assert [c["page"] for c in calls] == ["1", "2"]
        for call in calls:
            assert call["op"] == "PublicationSearch"
            assert call["searchterm"] == "Formicidae"
            assert call["searchtype"] == "F"
            assert call["pageSize"] == "2"
            assert call["apikey"] == FAKE_KEY
            assert call["format"] == "json"

    def test_stops_at_api_page_cap(self, bhl_api, monkeypatch):
        monkeypatch.setattr("data.bhl_corpus.BHL_SEARCH_MAX_PAGES", 2)
        full_page = _ok(
            [_pub_item(1, "1868"), _pub_part(2, "1901")]
        )
        calls: list = []
        # Two full pages: the (monkeypatched) 50-page cap stops paging
        # before a short page can.
        _serve_api(bhl_api, [full_page, full_page], calls)
        pubs, truncated = BHLHarvester(api_key=FAKE_KEY, delay=0).search_inside(
            "ants", rows=2
        )
        assert truncated is True
        assert len(pubs) == 4
        assert [c["page"] for c in calls] == ["1", "2"]

    def test_api_error_raises_without_leaking_key(self, bhl_api):
        bhl_api.expect_oneshot_request("/api3").respond_with_json(
            {"Status": "error", "ErrorMessage": "boom", "Result": None}
        )
        with pytest.raises(RuntimeError, match="boom"):
            BHLHarvester(api_key=FAKE_KEY, delay=0).search_inside("ants")


class TestPartAndItemResolution:
    def test_part_resolves_to_item(self, bhl_api):
        calls: list = []
        _serve_api(bhl_api, [_ok([{"PartID": "11", "ItemID": "100"}])], calls)
        assert BHLHarvester(api_key=FAKE_KEY, delay=0).get_part_item_id(
            11
        ) == 100
        assert calls[0]["op"] == "GetPartMetadata"
        assert calls[0]["id"] == "11"

    def test_item_stub_from_ia_source(self, bhl_api):
        bhl_api.expect_oneshot_request("/api3").respond_with_json(
            _ok(
                [
                    {
                        "ItemID": "335118",
                        "Source": "Internet Archive",
                        "SourceIdentifier": "newpanamaeciton1441webe",
                        "Year": "1949",
                        "Title": None,
                    }
                ]
            )
        )
        stub = BHLHarvester(api_key=FAKE_KEY, delay=0).get_item_stub(335118)
        assert stub == {
            "ia_identifier": "newpanamaeciton1441webe",
            "title": "",
            "publication_date": "1949",
            "bhl_item_id": 335118,
        }

    def test_non_ia_item_yields_no_stub(self, bhl_api):
        bhl_api.expect_oneshot_request("/api3").respond_with_json(
            _ok(
                [
                    {
                        "ItemID": "5",
                        "Source": "Other",
                        "SourceIdentifier": "xyz",
                        "Year": "1900",
                    }
                ]
            )
        )
        assert BHLHarvester(api_key=FAKE_KEY, delay=0).get_item_stub(5) is None


class TestCollectSearchInsideCandidates:
    def _queue_enumeration(self, httpserver, calls: list):
        """Term 'terma' hits part 11, 'termb' hits part 12 and item 200."""
        responses = [
            _ok([_pub_part(11, "1900", "Ants of A")]),
            _ok(
                [
                    _pub_part(12, "1901", "Ants of B"),
                    _pub_item(200, "1930", "Superorganism book"),
                ]
            ),
            _ok([{"PartID": "11", "ItemID": "100"}]),  # part 11 -> item 100
            _ok([{"PartID": "12", "ItemID": "100"}]),  # part 12 -> item 100
            # Stub resolution: item 100 is IA-backed, item 200 is not.
            _ok(
                [
                    {
                        "ItemID": "100",
                        "Source": "Internet Archive",
                        "SourceIdentifier": "ia-one",
                        "Year": "1900",
                        "Title": None,
                    }
                ]
            ),
            _ok(
                [
                    {
                        "ItemID": "200",
                        "Source": "Other",
                        "SourceIdentifier": "not-ia",
                        "Year": "1930",
                    }
                ]
            ),
        ]
        _serve_api(httpserver, responses, calls)

    def _collect(self, httpserver, data_dir, cap=2):
        monkeypatch = pytest.MonkeyPatch()
        try:
            monkeypatch.setattr(
                "data.bhl_corpus.SEARCH_INSIDE_TERMS", ("terma", "termb")
            )
            calls: list = []
            self._queue_enumeration(httpserver, calls)
            harvester = BHLHarvester(api_key=FAKE_KEY, delay=0)
            stubs, stats = harvester.collect_search_inside_candidates(
                data_dir, cap=cap
            )
        finally:
            monkeypatch.undo()
        return stubs, stats

    def test_merge_dedupe_and_cap(self, bhl_api, tmp_path):
        stubs, stats = self._collect(bhl_api, tmp_path, cap=2)
        # Both parts resolve to the same item: deduped to item 100 plus
        # the direct item 200 hit; item 200 is non-IA so only one stub.
        assert stats["candidate_items"] == 2
        assert stats["per_term_publications"] == {"terma": 1, "termb": 2}
        assert stats["truncated"] is False
        assert stats["not_ia_sourced"] == 1
        assert [s["ia_identifier"] for s in stubs] == ["ia-one"]
        assert stubs[0]["queries"] == ["terma", "termb"]
        results = json.loads(
            (tmp_path / "searchinside_results.json").read_text()
        )
        assert set(results["terms"]) == {"terma", "termb"}
        items_doc = json.loads(
            (tmp_path / "searchinside_items.json").read_text()
        )
        assert items_doc["part_to_item"] == {"11": 100, "12": 100}

    def test_cap_truncates_highest_relevance(self, bhl_api, tmp_path):
        stubs, stats = self._collect(bhl_api, tmp_path, cap=1)
        assert stats["candidate_items"] == 1
        assert stats["truncated"] is True
        assert [s["ia_identifier"] for s in stubs] == ["ia-one"]

    def test_resume_skips_enumerated_terms(self, bhl_api, tmp_path):
        self._collect(bhl_api, tmp_path, cap=2)
        # Second run re-serves nothing: any unexpected request answers
        # HTTP 500, whose non-ok Status would raise.  No error means
        # enumeration, part resolution, and stub resolution were all
        # served from the checkpoints.
        monkeypatch = pytest.MonkeyPatch()
        try:
            monkeypatch.setattr(
                "data.bhl_corpus.SEARCH_INSIDE_TERMS", ("terma", "termb")
            )
            stubs, stats = BHLHarvester(
                api_key=FAKE_KEY, delay=0
            ).collect_search_inside_candidates(tmp_path, cap=2)
        finally:
            monkeypatch.undo()
        assert [s["ia_identifier"] for s in stubs] == ["ia-one"]
        assert stats["stubs"] == 1


class TestKeyedHarvestMerge:
    def test_harvest_sharded_merges_keyed_stubs(self, bhl_api, tmp_path):
        # Existing corpus already stores ia-one via the keyless run.
        data_dir = tmp_path / "bhl"
        data_dir.mkdir()
        stored = {
            "bhl_id": "ia-one",
            "ia_identifier": "ia-one",
            "title": "Ants of A",
            "publication_date": "1900",
            "year": 1900,
            "era": "era_1900_1949",
            "collections": ["biodiversity"],
            "url": "https://archive.org/details/ia-one",
            "full_text": "ants of a",
        }
        write_shard(data_dir / "bhl_shard_00001.json", [stored])
        # Keyed candidates: ia-one (stored, skipped) and ia-two (new).
        stubs = [
            {
                "ia_identifier": "ia-one",
                "title": "",
                "publication_date": "1900",
                "bhl_item_id": 100,
            },
            {
                "ia_identifier": "ia-two",
                "title": "",
                "publication_date": "1931",
                "bhl_item_id": 101,
            },
        ]
        # Keyless api_check probe, then IA metadata + text for ia-two.
        bhl_api.expect_oneshot_request("/api3").respond_with_json(_ok([]))
        metadata = {
            "metadata": {
                "identifier": "ia-two",
                "title": "Ants of Two",
                "date": "1931",
                "collection": ["biodiversity"],
            },
            "files": [{"name": "ia-two_djvu.txt"}],
        }
        bhl_api.expect_oneshot_request(
            "/ia/metadata/ia-two"
        ).respond_with_json(metadata)
        bhl_api.expect_oneshot_request(
            "/ia/download/ia-two/ia-two_djvu.txt"
        ).respond_with_data("the ants of two colonies " * 5)
        monkeypatch = pytest.MonkeyPatch()
        try:
            monkeypatch.setattr(
                "data.bhl_corpus.IA_METADATA_URL",
                bhl_api.url_for("ia/metadata/{identifier}"),
            )
            monkeypatch.setattr(
                "data.bhl_corpus.IA_DOWNLOAD_URL",
                bhl_api.url_for(
                    "ia/download/{identifier}/{identifier}_djvu.txt"
                ),
            )
            harvester = BHLHarvester(delay=0)
            summary = harvester.harvest_sharded(
                data_dir,
                data_dir / "provenance.json",
                query=BHL_KEYED_QUERY,
                stubs=stubs,
            )
        finally:
            monkeypatch.undo()
        assert summary["candidates"] == 2
        assert summary["already_stored"] == 1
        records = [r for p in shard_paths(data_dir) for r in read_shard(p)]
        assert [r["ia_identifier"] for r in records] == ["ia-one", "ia-two"]
        assert records[1]["title"] == "Ants of Two"
        assert records[1]["era"] == "era_1900_1949"
        provenance = json.loads(
            (data_dir / "provenance.json").read_text(encoding="utf-8")
        )
        assert all(e["query"] == BHL_KEYED_QUERY for e in provenance.values())
        assert FAKE_KEY not in json.dumps(provenance)

    def test_keyed_wrapper_requires_api_key(self, monkeypatch, tmp_path):
        monkeypatch.delenv("BHL_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="requires a BHL API v3 key"):
            harvest_bhl(data_dir=tmp_path, keyed=True)


class TestKeyedReadme:
    def test_readme_documents_keyed_search(self, tmp_path):
        summary = {
            "harvested": 3,
            "candidates": 5,
            "fetched": 3,
            "no_text_derivative": 0,
            "out_of_window": 1,
            "irrelevant": 1,
            "failed_items": 0,
            "api_check": {
                "endpoint": "https://www.biodiversitylibrary.org/api3",
                "keyed": True,
                "status": "ok",
                "ok": True,
            },
            "keyed": {
                "op": "PublicationSearch",
                "searchtype": "F",
                "date_window": [1850, 1970],
                "per_term_publications": {
                    "ants": 120,
                    "division of labour": 7,
                },
                "candidate_items": 3000,
                "cap": 3000,
                "truncated": True,
                "not_ia_sourced": 4,
                "stubs": 2996,
            },
        }
        path = write_readme(tmp_path, summary=summary)
        readme = path.read_text(encoding="utf-8")
        assert "## Keyed full-text search (BHL API v3)" in readme
        assert "op=PublicationSearch&searchtype=F" in readme
        assert "- `ants`: 120 in-window publications" in readme
        assert "truncated=True" in readme
        assert FAKE_KEY not in readme
