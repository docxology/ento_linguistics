"""Tests for PMC open-access full-text harvesting (src/data/pmc_fulltext.py).

Fixture-based: pytest-httpserver simulates the E-utilities network; no
live HTTP.  XML fixtures are synthetic JATS article sets.
"""

import hashlib
import json
from pathlib import Path

import pytest

from data.pmc_fulltext import (
    PMC_SEARCH_QUERY,
    PMCFulltextHarvester,
    dedupe_by_pmcid,
    is_relevant,
    parse_fulltext_xml,
    write_corpus,
    write_readme,
)

def _article(
    pmcid: str,
    title: str,
    abstract: str,
    body_paragraphs: tuple,
    doi: str = "10.1234/example.001",
    year: str = "2025",
    journal: str = "Journal of Myrmecology",
) -> str:
    """Render one synthetic JATS ``<article>`` element."""
    body = "".join(f"<p>{p}</p>" for p in body_paragraphs)
    return f"""
    <article xml:lang="en" article-type="research-article">
      <front>
        <journal-meta>
          <journal-title>{journal}</journal-title>
        </journal-meta>
        <article-meta>
          <article-id pub-id-type="pmcid">{pmcid}</article-id>
          <article-id pub-id-type="doi">{doi}</article-id>
          <pub-date><year>{year}</year></pub-date>
          <title-group><article-title>{title}</article-title></title-group>
          <abstract><p>{abstract}</p></abstract>
          <permissions>
            <license>
              <ali:license_ref xmlns:ali="http://www.niso.org/schemas/ali/1.0/">
                http://creativecommons.org/licenses/by/4.0/
              </ali:license_ref>
            </license>
          </permissions>
        </article-meta>
      </front>
      <body>{body}</body>
    </article>
    """


def _articleset(*articles: str) -> str:
    """Wrap article elements in an efetch ``pmc-articleset`` response."""
    return "<pmc-articleset>" + "".join(articles) + "</pmc-articleset>"


RELEVANT_ARTICLE = _article(
    "PMC111",
    "Ant colony organization and task allocation",
    "We study ant foraging behavior in eusocial colonies.",
    (
        "Workers of the ant <italic>Formica</italic> species forage collectively.",
        "Caste ratios depend on <bold>queen</bold> pheromone signaling.",
    ),
)

IRRELEVANT_ARTICLE = _article(
    "PMC222",
    "Marine algae photosynthesis",
    "Photosynthetic efficiency of marine algae.",
    ("Chloroplast dynamics under varying light.",),
    doi="10.1234/example.002",
)


class TestParsing:
    def test_parse_fulltext_xml_extracts_fields(self):
        records = parse_fulltext_xml(_articleset(RELEVANT_ARTICLE))
        assert len(records) == 1
        record = records[0]
        assert record["pmcid"] == "PMC111"
        assert record["doi"] == "10.1234/example.001"
        assert record["title"] == "Ant colony organization and task allocation"
        assert record["year"] == 2025
        assert record["journal"] == "Journal of Myrmecology"
        assert record["license"] == "http://creativecommons.org/licenses/by/4.0/"
        assert "eusocial colonies" in record["abstract"]

    def test_body_text_strips_markup_and_separates_paragraphs(self):
        record = parse_fulltext_xml(_articleset(RELEVANT_ARTICLE))[0]
        assert "<italic>" not in record["body_text"]
        assert "<bold>" not in record["body_text"]
        assert record["body_text"].count("\n\n") == 1
        assert "Formica" in record["body_text"]
        assert "queen" in record["body_text"]

    def test_parse_skips_articles_without_pmcid(self):
        orphan = RELEVANT_ARTICLE.replace(
            '<article-id pub-id-type="pmcid">PMC111</article-id>', ""
        )
        records = parse_fulltext_xml(_articleset(orphan, RELEVANT_ARTICLE))
        assert [r["pmcid"] for r in records] == ["PMC111"]

    def test_parse_empty_body_is_empty_string(self):
        no_body = RELEVANT_ARTICLE.replace(
            "<body><p>Workers of the ant <italic>Formica</italic> species forage collectively.</p>"
            "<p>Caste ratios depend on <bold>queen</bold> pheromone signaling.</p></body>",
            "",
        )
        record = parse_fulltext_xml(_articleset(no_body))[0]
        assert record["body_text"] == ""


class TestRelevanceFilter:
    @pytest.mark.parametrize(
        "text",
        [
            "The ant colony forages at dawn.",
            "ant-mediated seed dispersal",
            "Formicidae phylogeny",
            "eusociality evolved repeatedly",
            "myrmecology in the tropics",
            "social insects communicate chemically",
        ],
    )
    def test_relevant_texts_pass(self, text):
        assert is_relevant({"title": text})

    @pytest.mark.parametrize(
        "text",
        [
            "Marine algae photosynthesis",
            "The plant wants water",  # 'ant' substring must not match
            "Antennal morphology of beetles",
            "Antarctic ice cores",
        ],
    )
    def test_irrelevant_texts_fail(self, text):
        assert not is_relevant({"title": text})

    def test_checks_title_abstract_and_body(self):
        assert is_relevant({"title": "x", "abstract": "", "body_text": "an ant walked"})
        assert not is_relevant({"title": "x", "abstract": "y", "body_text": "no matches"})

    def test_harvested_irrelevant_article_is_excluded(self):
        assert is_relevant(parse_fulltext_xml(_articleset(RELEVANT_ARTICLE))[0])
        assert not is_relevant(parse_fulltext_xml(_articleset(IRRELEVANT_ARTICLE))[0])


class TestDedupe:
    def test_keeps_first_occurrence_in_order(self):
        records = [
            {"pmcid": "PMC1", "title": "first"},
            {"pmcid": "PMC2", "title": "second"},
            {"pmcid": "PMC1", "title": "duplicate"},
        ]
        result = dedupe_by_pmcid(records)
        assert [r["title"] for r in result] == ["first", "second"]

    def test_drops_records_without_pmcid(self):
        records = [{"pmcid": "", "title": "x"}, {"pmcid": "PMC1", "title": "y"}]
        assert [r["title"] for r in dedupe_by_pmcid(records)] == ["y"]

    def test_empty_input(self):
        assert dedupe_by_pmcid([]) == []


class TestHarvest:
    def _install(self, httpserver, monkeypatch, idlist, articles_xml):
        httpserver.expect_request("/esearch.fcgi").respond_with_json(
            {"esearchresult": {"idlist": idlist}}
        )
        httpserver.expect_request("/efetch.fcgi").respond_with_data(articles_xml)
        harvester = PMCFulltextHarvester(delay=0)
        monkeypatch.setattr(harvester, "BASE_URL", httpserver.url_for("/"))
        return harvester

    def test_harvest_filters_dedupes_and_preserves_rank(self, httpserver, monkeypatch):
        # Rank order: PMC111, PMC222 (irrelevant), PMC111 again (duplicate).
        harvester = self._install(
            httpserver,
            monkeypatch,
            ["111", "222", "111"],
            _articleset(RELEVANT_ARTICLE, IRRELEVANT_ARTICLE, RELEVANT_ARTICLE),
        )
        records = harvester.harvest(target=10)
        assert [r["pmcid"] for r in records] == ["PMC111"]

    def test_harvest_stops_at_target(self, httpserver, monkeypatch):
        third = _article(
            "PMC333",
            "Ant queens and reproductive division of labor",
            "Queen reproduction in ants.",
            ("Ant workers police reproduction.",),
            doi="10.1234/example.003",
        )
        harvester = self._install(
            httpserver,
            monkeypatch,
            ["111", "333"],
            _articleset(RELEVANT_ARTICLE, third),
        )
        records = harvester.harvest(target=1)
        assert [r["pmcid"] for r in records] == ["PMC111"]

    def test_harvest_skips_empty_body_records(self, httpserver, monkeypatch):
        no_body = RELEVANT_ARTICLE.replace(
            "<body><p>Workers of the ant <italic>Formica</italic> species forage collectively.</p>"
            "<p>Caste ratios depend on <bold>queen</bold> pheromone signaling.</p></body>",
            "",
        )
        harvester = self._install(
            httpserver, monkeypatch, ["111"], _articleset(no_body)
        )
        assert harvester.harvest(target=5) == []

    def test_search_uses_relevance_sorted_pmc_query(self, httpserver, monkeypatch):
        seen_queries = []

        def _capture(request):
            seen_queries.append(request.args["term"])
            return json.dumps({"esearchresult": {"idlist": ["111"]}})

        httpserver.expect_request("/esearch.fcgi").respond_with_handler(_capture)
        httpserver.expect_request("/efetch.fcgi").respond_with_data(
            _articleset(RELEVANT_ARTICLE)
        )
        harvester = PMCFulltextHarvester(delay=0)
        monkeypatch.setattr(harvester, "BASE_URL", httpserver.url_for("/"))
        harvester.harvest(target=1)
        assert seen_queries == [PMC_SEARCH_QUERY]


class TestWriteCorpus:
    def test_writes_corpus_and_provenance(self, tmp_path: Path):
        records = parse_fulltext_xml(_articleset(RELEVANT_ARTICLE, IRRELEVANT_ARTICLE))
        corpus_path = tmp_path / "fulltexts.json"
        provenance_path = tmp_path / "provenance.json"
        provenance = write_corpus(
            records,
            corpus_path,
            provenance_path,
            query="TEST QUERY",
            retrieved_at="2026-09-16T00:00:00+00:00",
        )

        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        assert [r["pmcid"] for r in corpus] == ["PMC111", "PMC222"]
        assert set(corpus[0]) == {
            "pmcid",
            "doi",
            "title",
            "year",
            "journal",
            "license",
            "abstract",
            "body_text",
        }

        sidecar = json.loads(provenance_path.read_text(encoding="utf-8"))
        assert sidecar == provenance
        digest = hashlib.sha256(
            corpus[0]["body_text"].encode("utf-8")
        ).hexdigest()
        assert sidecar[digest] == {
            "pmcid": "PMC111",
            "doi": "10.1234/example.001",
            "query": "TEST QUERY",
            "retrieved_at": "2026-09-16T00:00:00+00:00",
        }

    def test_provenance_distinguishes_distinct_bodies(self, tmp_path: Path):
        records = parse_fulltext_xml(_articleset(RELEVANT_ARTICLE, IRRELEVANT_ARTICLE))
        provenance = write_corpus(
            records, tmp_path / "c.json", tmp_path / "p.json"
        )
        digests = {entry["pmcid"]: digest for digest, entry in provenance.items()}
        assert digests["PMC111"] != digests["PMC222"]


class TestWriteReadme:
    def test_documents_query_filters_and_license_coverage(self, tmp_path: Path):
        records = parse_fulltext_xml(
            _articleset(RELEVANT_ARTICLE, IRRELEVANT_ARTICLE)
        )
        readme = write_readme(records, tmp_path, query=PMC_SEARCH_QUERY)
        text = readme.read_text(encoding="utf-8")
        assert PMC_SEARCH_QUERY in text
        assert "open access[Filter]" in text
        assert "`: 2 documents" in text
        assert "src/data/pmc_fulltext.py --target 500" in text
