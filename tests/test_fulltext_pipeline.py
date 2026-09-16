"""Tests for the full-text analysis pipeline (src/pipeline/fulltext_pipeline.py).

Fixture-based: small synthetic full-text records (no live network, no
mocked analysis — the pipeline runs its real term-extraction and
statistic passes over the fixture corpus).
"""

import json
from pathlib import Path

import pytest

from pipeline.fulltext_pipeline import FULLTEXT_LAYER, build_fulltext_analysis, main


def _record(pmcid: str, body: str, doi: str = "10.1234/x", year: int = 2025) -> dict:
    """One synthetic full-text corpus record rich in domain seed terms."""
    return {
        "pmcid": pmcid,
        "doi": doi,
        "title": f"Ant colony {pmcid}: caste and reproduction",
        "year": year,
        "journal": "Journal of Myrmecology",
        "license": "http://creativecommons.org/licenses/by/4.0/",
        "abstract": (
            "The ant colony allocates workers among foraging and brood care. "
            "Queen dominance shapes caste ratios and colony reproduction."
        ),
        "body_text": body,
    }


BODY = (
    "The colony is a superorganism whose nestmates form a collective. "
    "Workers perform foraging behavior while the queen lays eggs; caste "
    "determination divides reproductive labor. Relatedness and kinship "
    "drive altruism through haplodiploidy. Resource allocation and "
    "investment efficiency govern colony economics. "
) * 3


@pytest.fixture()
def fulltexts() -> list:
    return [
        _record("PMC1", BODY),
        _record("PMC2", BODY, doi="10.1234/y", year=2024),
        _record("PMC3", BODY, doi="10.1234/z"),
    ]


class TestArtifactSchema:
    def test_top_level_shape_mirrors_abstract_layer(self, fulltexts):
        artifact = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        # Abstract-layer statistics sections, verbatim.
        assert set(artifact) >= {
            "descriptives",
            "cace",
            "cace_terms",
            "pairwise",
            "anova",
            "corrections",
            "skipped",
        }
        # Parallel-layer markers.
        assert artifact["layer"] == FULLTEXT_LAYER
        assert artifact["n_documents"] == 3

    def test_descriptives_covers_six_canonical_domains(self, fulltexts):
        artifact = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        assert set(artifact["descriptives"]) == {
            "unit_of_individuality",
            "behavior_and_identity",
            "power_and_labor",
            "sex_and_reproduction",
            "kin_and_relatedness",
            "economics",
        }
        for entry in artifact["descriptives"].values():
            assert set(entry) >= {"n_terms", "bridging_count"}
            assert entry["n_terms"] >= 0

    def test_domain_term_counts(self, fulltexts):
        artifact = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        counts = artifact["domain_term_counts"]
        assert counts, "domain term counts must be non-empty for seed-rich fixtures"
        for entry in counts.values():
            assert entry["term_count"] > 0
            assert entry["bridging_term_count"] >= 0
            assert entry["total_frequency"] > 0

    def test_documents_carry_token_counts_and_metadata(self, fulltexts):
        artifact = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        assert len(artifact["documents"]) == 3
        for meta, record in zip(artifact["documents"], fulltexts):
            assert meta["pmcid"] == record["pmcid"]
            assert meta["doi"] == record["doi"]
            assert meta["year"] == record["year"]
            assert meta["journal"] == record["journal"]
            assert meta["license"] == record["license"]
            expected_tokens = len(
                __import__("re").findall(r"\w+", record["body_text"])
            )
            # The analyzed text is title+abstract+body, so at least the body.
            assert meta["token_count"] > expected_tokens

    def test_degenerate_terms_yield_honest_empty_sections(self):
        # One record, no repeated domain terms -> no extraction, no
        # fabricated statistics; sections stay empty/honest.
        bare = {
            "pmcid": "PMC1",
            "doi": "",
            "title": "Nothing relevant here.",
            "year": None,
            "journal": "",
            "license": "unknown",
            "abstract": "",
            "body_text": "Nothing relevant here.",
        }
        artifact = build_fulltext_analysis([bare], min_term_frequency=2)
        assert artifact["domain_term_counts"] == {}
        assert artifact["pairwise"] == []
        assert artifact["anova"] == {}
        assert artifact["skipped"], "degenerate groups must be recorded as skipped"


class TestBehavior:
    def test_deterministic(self, fulltexts):
        first = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        second = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        assert first == second

    def test_empty_corpus_rejected(self):
        with pytest.raises(ValueError):
            build_fulltext_analysis([])

    def test_real_terms_extracted_over_full_texts(self, fulltexts):
        artifact = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        # Seed terms occur >= min frequency in every record.
        counts = artifact["domain_term_counts"]
        for domain in ("power_and_labor", "kin_and_relatedness", "economics"):
            assert domain in counts
            assert counts[domain]["term_count"] >= 2


class TestCLI:
    def test_main_writes_artifact(self, tmp_path: Path, fulltexts):
        corpus_path = tmp_path / "fulltexts.json"
        corpus_path.write_text(json.dumps(fulltexts), encoding="utf-8")
        output_path = tmp_path / "out" / "fulltext_analysis.json"
        code = main(
            [
                "--corpus",
                str(corpus_path),
                "--output",
                str(output_path),
                "--min-term-frequency",
                "2",
            ]
        )
        assert code == 0
        artifact = json.loads(output_path.read_text(encoding="utf-8"))
        assert artifact["layer"] == FULLTEXT_LAYER
        assert artifact["n_documents"] == 3
