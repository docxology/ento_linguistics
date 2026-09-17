"""Tests for the full-text analysis pipeline (src/pipeline/fulltext_pipeline.py).

Fixture-based: small synthetic full-text records (no live network, no
mocked analysis — the pipeline runs its real term-extraction and
statistic passes over the fixture corpus).
"""

import json
from pathlib import Path

import pytest

from pipeline.fulltext_pipeline import (
    FULLTEXT_LAYER,
    add_framing_analysis,
    build_fulltext_analysis,
    main,
)


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


FRAMING_BODY = (
    "The colony is a superorganism whose nestmates form a collective. "
    "Workers choose to forage and decide among tasks; the queen prefers "
    "to signal and communicate. Relatedness and kinship drive altruism "
    "through haplodiploidy, and mating shapes reproduction. "
) * 3


@pytest.fixture()
def framing_fulltexts() -> list:
    """Corpus with anthropomorphic framing verbs next to domain seeds."""
    return [
        _record("PMC1", FRAMING_BODY),
        _record("PMC2", FRAMING_BODY, doi="10.1234/y", year=2024),
        _record("PMC3", FRAMING_BODY, doi="10.1234/z"),
    ]


class TestFramingAnalysis:
    """add_framing_analysis: anthropomorphic-framing proportions over the
    full texts, aggregated over domain-assigned terms' occurrence
    contexts (the occurrence-context analogue of the abstract layer's
    term-level anthropomorphic_proportion)."""

    def test_section_shape_and_values(self, framing_fulltexts):
        base = build_fulltext_analysis(
            framing_fulltexts, min_term_frequency=2, include_framing=False
        )
        assert "framing" not in base
        merged = add_framing_analysis(base, framing_fulltexts)
        framing = merged["framing"]
        # Canonical domains plus the aggregate; no fabricated entries.
        assert "overall" in framing
        assert set(framing) <= {
            "behavior_and_identity",
            "economics",
            "kin_and_relatedness",
            "power_and_labor",
            "sex_and_reproduction",
            "unit_of_individuality",
            "overall",
        }
        for entry in framing.values():
            assert set(entry) == {"proportion", "n_contexts"}
            assert 0.0 <= entry["proportion"] <= 1.0
            assert entry["n_contexts"] > 0
        # Real computation, not vacuous zeros: the fixture plants
        # anthropomorphic verbs (choose/decide/prefer/signal/communicate)
        # inside term contexts, so at least one domain must fire.
        domain_entries = {k: v for k, v in framing.items() if k != "overall"}
        assert any(e["proportion"] > 0 for e in domain_entries.values())
        assert framing["overall"]["proportion"] > 0
        # Bridging terms (queen, worker) contribute their occurrences to
        # every assigned domain, so the per-domain totals overshoot the
        # once-per-occurrence overall count.
        assert framing["overall"]["n_contexts"] <= sum(
            e["n_contexts"] for e in domain_entries.values()
        )

    def test_degenerate_domain_omitted(self):
        # No economics seed/pattern terms anywhere -> zero contexts ->
        # the domain is omitted, never zero-filled.
        body = (
            "The colony is a superorganism. Workers choose tasks. The "
            "queen prefers to signal. Relatedness and kinship drive "
            "altruism; mating shapes reproduction. "
        ) * 3
        fulltexts = [
            _record("PMC1", body),
            _record("PMC2", body, doi="10.1234/y", year=2024),
            _record("PMC3", body, doi="10.1234/z"),
        ]
        base = build_fulltext_analysis(fulltexts, min_term_frequency=2)
        # Sanity: the fixture is not vacuous for the other domains.
        assert "economics" not in base["domain_term_counts"]
        assert base["domain_term_counts"]
        merged = add_framing_analysis(base, fulltexts)
        assert "economics" not in merged["framing"]
        assert merged["framing"]["overall"]["n_contexts"] > 0

    def test_deterministic(self, framing_fulltexts):
        base = build_fulltext_analysis(
            framing_fulltexts, min_term_frequency=2, include_framing=False
        )
        assert add_framing_analysis(base, framing_fulltexts) == add_framing_analysis(
            base, framing_fulltexts
        )

    def test_default_build_includes_framing_and_matches_merge(
        self, framing_fulltexts
    ):
        merged = build_fulltext_analysis(
            framing_fulltexts, min_term_frequency=2, include_framing=False
        )
        merged = add_framing_analysis(merged, framing_fulltexts)
        assert build_fulltext_analysis(framing_fulltexts, min_term_frequency=2) == merged

    def test_corpus_artifact_mismatch_rejected(self, framing_fulltexts):
        base = build_fulltext_analysis(
            framing_fulltexts, min_term_frequency=2, include_framing=False
        )
        with pytest.raises(ValueError, match="domain_term_counts"):
            add_framing_analysis(base, framing_fulltexts[:1])

    def test_empty_corpus_rejected(self, framing_fulltexts):
        base = build_fulltext_analysis(
            framing_fulltexts, min_term_frequency=2, include_framing=False
        )
        with pytest.raises(ValueError, match="non-empty"):
            add_framing_analysis(base, [])

    def test_merge_cli_appends_framing_without_rebuild(
        self, tmp_path: Path, framing_fulltexts
    ):
        corpus_path = tmp_path / "fulltexts.json"
        corpus_path.write_text(json.dumps(framing_fulltexts), encoding="utf-8")
        output_path = tmp_path / "out" / "fulltext_analysis.json"
        # Stage an artifact WITHOUT the framing section (the frozen
        # pre-framing artifact), then merge through the CLI flag.
        base = build_fulltext_analysis(
            framing_fulltexts, min_term_frequency=2, include_framing=False
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(base), encoding="utf-8")
        code = main(
            [
                "--corpus",
                str(corpus_path),
                "--output",
                str(output_path),
                "--merge-framing",
            ]
        )
        assert code == 0
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        assert merged["framing"] == add_framing_analysis(
            base, framing_fulltexts
        )["framing"]
        # Everything outside the framing section is untouched.
        merged.pop("framing")
        assert merged == base
