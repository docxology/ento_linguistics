"""Tests for the arXiv preprint layer analysis (arxiv_analysis.py).

Fixture-based only: records are synthetic dicts; the artifact write is
exercised against tmp_path.  No live network, no ``output/`` writes.
The rich-corpus artifact is built once (module scope) — the shared
stack behind it is expensive relative to the assertions.
"""

from __future__ import annotations

import json

import pytest

from pipeline.arxiv_analysis import (
    ARXIV_LAYER,
    ARTIFACT_NAME,
    DEFAULT_MIN_TERM_FREQUENCY,
    build_arxiv_analysis,
    load_arxiv_records,
    main,
)

FROZEN_SECTIONS = (
    "descriptives",
    "cace",
    "cace_terms",
    "pairwise",
    "anova",
    "corrections",
    "skipped",
)


def _record(arxiv_id: str, abstract: str) -> dict:
    """One minimal arXiv corpus record."""
    return {
        "arxiv_id": arxiv_id,
        "doi": None,
        "title": f"Preprint {arxiv_id}",
        "abstract": abstract,
        "primary_category": "q-bio.PE",
        "published": "2025-01-01T00:00:00Z",
    }


def _rich_records() -> list:
    """Records whose abstracts repeat domain terms (extraction viable)."""
    return [
        _record(
            "2501.00001",
            "The ant colony exhibits division of labor. Worker ants "
            "forage for the colony while the queen ant lays eggs in "
            "the nest.",
        ),
        _record(
            "2501.00002",
            "Ant colony organization emerges from local interactions. "
            "The queen and the workers show division of labor; colony "
            "success depends on foraging workers.",
        ),
        _record(
            "2501.00003",
            "Haplodiploidy shapes kin structure in ant societies. The "
            "ant queen founds the colony and the nest; worker ants "
            "raise the brood.",
        ),
    ]


def _noise_records() -> list:
    """Records with no recurring vocabulary (degenerate extraction)."""
    return [
        _record("2501.00009", "Zz9 qwerty frobnicate glorp."),
        _record("2501.00010", "Blorf snix quuxle wibble."),
    ]


@pytest.fixture(scope="module")
def rich_artifact():
    """One shared full-stack artifact over the rich synthetic corpus."""
    return build_arxiv_analysis(_rich_records())


@pytest.fixture(scope="module")
def noise_artifact():
    """One shared artifact over the no-recurring-vocabulary corpus."""
    return build_arxiv_analysis(_noise_records())


class TestBuildArxivAnalysisSchema:
    def test_layer_and_counts(self, rich_artifact):
        assert rich_artifact["layer"] == ARXIV_LAYER
        assert rich_artifact["n_documents"] == 3
        assert rich_artifact["min_term_frequency"] == DEFAULT_MIN_TERM_FREQUENCY
        assert len(rich_artifact["documents"]) == 3
        assert rich_artifact["documents"][0]["arxiv_id"] == "2501.00001"
        assert rich_artifact["documents"][0]["token_count"] > 0

    def test_frozen_sections_present(self, rich_artifact):
        for section in FROZEN_SECTIONS:
            assert section in rich_artifact

    def test_extraction_nonempty(self, rich_artifact):
        counts = rich_artifact["domain_term_counts"]
        assert counts, "recurring domain vocabulary must be extracted"
        for domain, entry in counts.items():
            assert entry["term_count"] >= 1
            assert entry["total_frequency"] >= entry["term_count"]
            assert 0 <= entry["bridging_term_count"] <= entry["term_count"]

    def test_skipped_entries_honest(self, rich_artifact):
        for entry in rich_artifact["skipped"]:
            assert entry["kind"]
            assert entry["reason"]

    def test_degenerate_corpora_reported_not_fabricated(self, noise_artifact):
        assert noise_artifact["domain_term_counts"] == {}
        assert noise_artifact["pairwise"] == []
        assert noise_artifact["anova"] == {}
        kinds = {entry["kind"] for entry in noise_artifact["skipped"]}
        assert "domain_group" in kinds
        assert "anova" in kinds
        # Framing with no domain vocabulary: no occurrence contexts.
        assert noise_artifact["framing"] == {}


class TestFraming:
    def test_framing_over_occurrence_contexts(self, rich_artifact):
        framing = rich_artifact["framing"]
        assert framing["overall"]["n_contexts"] > 0
        for domain, entry in framing.items():
            assert 0.0 <= entry["proportion"] <= 1.0
            assert entry["n_contexts"] > 0

    def test_no_terms_no_framing_contexts(self, noise_artifact):
        assert "overall" not in noise_artifact["framing"]


class TestDeterminism:
    def test_repeated_build_identical_except_generated(self):
        first = build_arxiv_analysis(_noise_records())
        second = build_arxiv_analysis(_noise_records())
        first.pop("generated")
        second.pop("generated")
        assert first == second


class TestGuards:
    def test_empty_records_raise(self):
        with pytest.raises(ValueError):
            build_arxiv_analysis([])

    def test_load_rejects_non_list(self, tmp_path):
        path = tmp_path / "records.json"
        path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
        with pytest.raises(ValueError):
            load_arxiv_records(path)


class TestMainCli:
    def test_writes_artifact(self, tmp_path):
        records_path = tmp_path / "records.json"
        records_path.write_text(
            json.dumps(_noise_records()), encoding="utf-8"
        )
        output = tmp_path / ARTIFACT_NAME
        rc = main(["--records", str(records_path), "--output", str(output)])
        assert rc == 0
        artifact = json.loads(output.read_text(encoding="utf-8"))
        assert artifact["layer"] == ARXIV_LAYER
        assert artifact["n_documents"] == 2

    def test_min_term_frequency_flag_recorded(self, tmp_path):
        records_path = tmp_path / "records.json"
        records_path.write_text(
            json.dumps(_rich_records()), encoding="utf-8"
        )
        output = tmp_path / "arxiv_min3.json"
        rc = main(
            [
                "--records",
                str(records_path),
                "--output",
                str(output),
                "--min-term-frequency",
                "3",
            ]
        )
        assert rc == 0
        artifact = json.loads(output.read_text(encoding="utf-8"))
        assert artifact["min_term_frequency"] == 3
