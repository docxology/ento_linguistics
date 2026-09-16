"""Behavioral tests for the corpus build pipeline (stage 01).

Covers corpus validation statistics, PubMed retrieval against a local
HTTP server serving real eutils-format responses, and the ``main``
entry point in both its cached and fetch modes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from data.literature_mining import PubMedMiner
from pipeline.corpus_build import (
    ENTOMOLOGY_QUERIES,
    fetch_abstracts_for_query,
    main,
    validate_corpus,
)

CORPUS_PATH = Path(__file__).resolve().parents[1] / "data" / "corpus" / "abstracts.json"

DOMAIN_SEED_KEYS = {
    "unit_of_individuality",
    "behavior_and_identity",
    "power_and_labor",
    "sex_and_reproduction",
    "kin_and_relatedness",
    "economics",
}

ABSTRACT_QUEEN = (
    "The queen ant regulates colony reproduction while workers perform "
    "foraging and brood care tasks within the nest."
)
ABSTRACT_TASKS = (
    "Task allocation among workers emerges from local interactions rather "
    "than centralized control by the queen."
)

ESEARCH_BODY = {"esearchresult": {"idlist": ["111", "222"]}}
ESUMMARY_BODY = {
    "result": {
        "111": {
            "uid": "111",
            "title": "Queen control of colony reproduction in ants",
            "authors": [{"name": "Alice Author"}],
            "pubdate": "2021 Mar",
            "fulljournalname": "Insectes Sociaux",
        },
        "222": {
            "uid": "222",
            "title": "Worker task allocation in social insects",
            "authors": [{"name": "Bob Builder"}],
            "pubdate": "2019 Jun",
            "fulljournalname": "Journal of Insect Behavior",
        },
    }
}
EFETCH_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
  <PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>111</PMID>
      <Article>
        <Abstract>
          <AbstractText>{ABSTRACT_QUEEN}</AbstractText>
        </Abstract>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>222</PMID>
      <Article>
        <Abstract>
          <AbstractText>{ABSTRACT_TASKS}</AbstractText>
        </Abstract>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


@pytest.fixture(scope="module")
def real_abstracts() -> list[str]:
    """Load a real subset of the committed corpus (read-only)."""
    with open(CORPUS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    texts = [a for a in data if isinstance(a, str) and a.strip()]
    assert len(texts) >= 25, "expected the committed corpus to have >= 25 abstracts"
    return texts


@pytest.fixture
def local_pubmed(httpserver, monkeypatch):
    """Serve real eutils-format responses from a local HTTP server."""
    httpserver.expect_request("/esearch.fcgi").respond_with_json(ESEARCH_BODY)
    httpserver.expect_request("/esummary.fcgi").respond_with_json(ESUMMARY_BODY)
    httpserver.expect_request("/efetch.fcgi").respond_with_data(
        EFETCH_XML, content_type="text/xml"
    )
    monkeypatch.setattr(PubMedMiner, "BASE_URL", httpserver.url_for("/"))


class TestValidateCorpus:
    """validate_corpus statistics against real abstracts."""

    def test_real_subset_statistics(self, real_abstracts) -> None:
        subset = real_abstracts[:25]
        stats = validate_corpus(subset)

        assert stats["total_abstracts"] == 25
        assert stats["total_tokens"] > 0
        assert stats["unique_tokens"] <= stats["total_tokens"]
        assert stats["avg_abstract_length_tokens"] == pytest.approx(
            stats["total_tokens"] / 25
        )

        assert set(stats["domain_coverage"]) == DOMAIN_SEED_KEYS
        found_terms = [
            term
            for info in stats["domain_coverage"].values()
            for term in info["terms_found"]
        ]
        assert found_terms, "real abstracts must hit at least one domain seed term"
        for info in stats["domain_coverage"].values():
            assert 0.0 <= info["coverage"] <= 1.0
            assert (info["coverage"] > 0) == bool(info["terms_found"])

        top_tokens = stats["top_tokens"]
        assert 0 < len(top_tokens) <= 30
        counts = [count for _, count in top_tokens]
        assert counts == sorted(counts, reverse=True)
        assert all(isinstance(token, str) for token, _ in top_tokens)

    def test_empty_corpus(self) -> None:
        stats = validate_corpus([])
        assert stats["total_abstracts"] == 0
        assert stats["total_tokens"] == 0
        assert stats["unique_tokens"] == 0
        assert stats["avg_abstract_length_tokens"] == 0
        assert set(stats["domain_coverage"]) == DOMAIN_SEED_KEYS
        for info in stats["domain_coverage"].values():
            assert info["terms_found"] == []
            assert info["coverage"] == 0
        assert stats["top_tokens"] == []


class TestFetchAbstractsForQuery:
    """Retrieval via a real PubMedMiner pointed at a local eutils server."""

    def test_returns_abstracts(self, local_pubmed) -> None:
        miner = PubMedMiner()
        abstracts = fetch_abstracts_for_query(miner, "insect+eusociality")
        assert abstracts == [ABSTRACT_QUEEN, ABSTRACT_TASKS]

    def test_skips_publications_without_abstract(self, httpserver, monkeypatch) -> None:
        httpserver.expect_request("/esearch.fcgi").respond_with_json(ESEARCH_BODY)
        httpserver.expect_request("/esummary.fcgi").respond_with_json(ESUMMARY_BODY)
        httpserver.expect_request("/efetch.fcgi").respond_with_data(
            '<?xml version="1.0"?><PubmedArticleSet></PubmedArticleSet>',
            content_type="text/xml",
        )
        monkeypatch.setattr(PubMedMiner, "BASE_URL", httpserver.url_for("/"))

        miner = PubMedMiner()
        assert fetch_abstracts_for_query(miner, "query", max_per_query=2) == []

    def test_swallows_retrieval_errors(self) -> None:
        # An empty query makes miner.search raise ValueError before any
        # network access; fetch_abstracts_for_query must degrade to [].
        miner = PubMedMiner()
        assert fetch_abstracts_for_query(miner, "", max_per_query=5) == []

    def test_query_catalog_is_nonempty(self) -> None:
        assert len(ENTOMOLOGY_QUERIES) == 8
        assert all(isinstance(q, str) and q for q in ENTOMOLOGY_QUERIES)


class TestMain:
    """main() entry point: cached statistics refresh and fetch mode."""

    def test_cached_corpus_refreshes_statistics(
        self, tmp_path, real_abstracts
    ) -> None:
        corpus_file = tmp_path / "data" / "corpus" / "abstracts.json"
        corpus_file.parent.mkdir(parents=True)
        subset = real_abstracts[:25]
        corpus_file.write_text(json.dumps(subset), encoding="utf-8")

        rc = main(project_root=tmp_path, argv=[])

        assert rc == 0
        stats_file = tmp_path / "output" / "data" / "corpus_statistics.json"
        assert stats_file.exists()
        stats = json.loads(stats_file.read_text(encoding="utf-8"))
        assert stats["total_abstracts"] == 25
        assert stats["total_tokens"] > 0
        assert stats["unique_tokens"] <= stats["total_tokens"]
        assert stats["avg_abstract_length_tokens"] == pytest.approx(
            stats["total_tokens"] / 25
        )
        assert stats["top_tokens"]
        assert all(set(entry) == {"token", "count"} for entry in stats["top_tokens"])
        assert set(stats["domain_coverage"]) == DOMAIN_SEED_KEYS
        for info in stats["domain_coverage"].values():
            assert isinstance(info["coverage"], float)
            assert 0.0 <= info["coverage"] <= 1.0
        # The cached corpus itself must be left untouched.
        assert json.loads(corpus_file.read_text(encoding="utf-8")) == subset

    def test_fetch_mode_merges_into_existing_corpus(
        self, tmp_path, local_pubmed, real_abstracts
    ) -> None:
        existing = tmp_path / "existing_corpus.json"
        existing.write_text(json.dumps(real_abstracts[:5]), encoding="utf-8")
        stats_path = tmp_path / "stats" / "corpus_statistics.json"

        rc = main(
            project_root=tmp_path,
            argv=[
                "--output",
                str(existing),
                "--stats-output",
                str(stats_path),
                "--max-per-query",
                "2",
            ],
        )

        # Fetched abstracts are merged into the existing corpus, never
        # overwriting it; dedupe keeps 2 new (< 20 total → rc 1).
        assert rc == 1
        saved = json.loads(existing.read_text(encoding="utf-8"))
        assert saved[:5] == real_abstracts[:5]
        assert saved[5:] == [ABSTRACT_QUEEN, ABSTRACT_TASKS]
        assert stats_path.exists()
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
        assert stats["total_abstracts"] == 7
        assert stats["top_tokens"]
        assert all(set(entry) == {"token", "count"} for entry in stats["top_tokens"])

    def test_force_preserves_existing_records(
        self, tmp_path, local_pubmed, real_abstracts
    ) -> None:
        """Regression: --force must merge, never destroy grown records."""
        corpus_file = tmp_path / "data" / "corpus" / "abstracts.json"
        corpus_file.parent.mkdir(parents=True)
        existing = real_abstracts[:5]
        corpus_file.write_text(json.dumps(existing), encoding="utf-8")

        rc = main(project_root=tmp_path, argv=["--force"])

        saved = json.loads(corpus_file.read_text(encoding="utf-8"))
        # Every pre-existing record survives the forced re-fetch.
        assert all(a in saved for a in existing)
        assert saved[5:] == [ABSTRACT_QUEEN, ABSTRACT_TASKS]
        assert len(saved) == len(set(saved))  # no duplicates
        # Newly appended records get provenance sidecars.
        prov = json.loads(
            (tmp_path / "data" / "corpus" / "provenance.json").read_text(
                encoding="utf-8"
            )
        )
        assert len(prov["records"]) == 2
        for sidecar in prov["records"].values():
            assert set(sidecar) == {"pmid", "doi", "title", "year", "journal", "query"}
        # rc is 1 only because 5 + 2 < 20.
        assert rc == 1

    def test_grow_appends_records_and_updates_provenance(
        self, tmp_path, local_pubmed, real_abstracts, monkeypatch
    ) -> None:
        corpus_file = tmp_path / "data" / "corpus" / "abstracts.json"
        corpus_file.parent.mkdir(parents=True)
        seed = real_abstracts[:20]
        corpus_file.write_text(json.dumps(seed), encoding="utf-8")
        monkeypatch.setattr(time, "sleep", lambda _: None)

        argv = ["--grow", "--target-new", "5", "--max-per-query", "2"]
        rc = main(project_root=tmp_path, argv=argv)

        assert rc == 0
        after = json.loads(corpus_file.read_text(encoding="utf-8"))
        assert after[:20] == seed
        assert after[20:] == [ABSTRACT_QUEEN, ABSTRACT_TASKS]
        prov = json.loads(
            (tmp_path / "data" / "corpus" / "provenance.json").read_text(
                encoding="utf-8"
            )
        )
        assert len(prov["records"]) == 2
        for sidecar in prov["records"].values():
            assert set(sidecar) == {"pmid", "doi", "title", "year", "journal", "query"}
            assert sidecar["pmid"] in {"111", "222"}
        stats = json.loads(
            (tmp_path / "output" / "data" / "corpus_statistics.json").read_text(
                encoding="utf-8"
            )
        )
        assert stats["total_abstracts"] == 22
        assert stats["most_common_tokens"]
        assert all(
            isinstance(entry, list) and len(entry) == 2
            for entry in stats["most_common_tokens"]
        )

    def test_grow_is_idempotent(self, tmp_path, local_pubmed, real_abstracts, monkeypatch) -> None:
        corpus_file = tmp_path / "data" / "corpus" / "abstracts.json"
        corpus_file.parent.mkdir(parents=True)
        seed = real_abstracts[:20]
        corpus_file.write_text(json.dumps(seed), encoding="utf-8")
        monkeypatch.setattr(time, "sleep", lambda _: None)

        argv = ["--grow", "--target-new", "5", "--max-per-query", "2"]
        assert main(project_root=tmp_path, argv=argv) == 0
        after_first = json.loads(corpus_file.read_text(encoding="utf-8"))
        prov_path = tmp_path / "data" / "corpus" / "provenance.json"
        prov_first = prov_path.read_text(encoding="utf-8")

        # Second run: known PMIDs are excluded, nothing new is appended.
        assert main(project_root=tmp_path, argv=argv) == 0
        after_second = json.loads(corpus_file.read_text(encoding="utf-8"))
        assert after_second == after_first
        assert prov_path.read_text(encoding="utf-8") == prov_first
