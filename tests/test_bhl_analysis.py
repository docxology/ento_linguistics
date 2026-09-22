"""Tests for era-stratified BHL analysis (src/pipeline/bhl_analysis.py).

Fixture-based only: records are synthetic dicts; the artifact write is
exercised against tmp_path.  No live network, no ``output/`` writes.
"""

from __future__ import annotations

import json

import pytest
from pipeline.bhl_analysis import (
    ARTIFACT_NAME,
    ENTROPY_TOP_TERMS,
    ERA_KEYS,
    OCR_MIN_TERM_FREQUENCY,
    analyze_eras,
    analyze_era_stack,
    build_artifact,
    clean_ocr_text,
    domain_vocabularies,
    main,
    normalize_text,
    tokenize,
)


def _record(era: str, text: str) -> dict:
    """One minimal corpus record."""
    return {"era": era, "full_text": text, "ia_identifier": "x"}


VOCAB = {
    "unit_of_individuality": ("colony", "superorganism"),
    "behavior_and_identity": ("division of labor", "foraging"),
    "economics": ("cost", "benefit"),
}


class TestNormalizeTokenize:
    def test_lowercase_and_whitespace(self):
        assert normalize_text("  The  COLONY\r\nforages\t") == "the colony forages"

    def test_hyphen_linebreak_joined(self):
        assert normalize_text("super-\norganism") == "superorganism"

    def test_keeps_hyphenated_tokens(self):
        assert tokenize("colony-level selection") == ["colony-level", "selection"]

    def test_tokenize_drops_punct_and_digits(self):
        assert tokenize("ants, 12; (Formicidae)!") == ["ants", "formicidae"]

    def test_empty(self):
        assert tokenize("") == []


class TestDomainVocabularies:
    def test_six_canonical_domains(self):
        vocab = domain_vocabularies()
        assert sorted(vocab) == [
            "behavior_and_identity",
            "economics",
            "kin_and_relatedness",
            "power_and_labor",
            "sex_and_reproduction",
            "unit_of_individuality",
        ]

    def test_nonempty_terms(self):
        assert all(len(terms) > 0 for terms in domain_vocabularies().values())


class TestAnalyzeEras:
    def test_per_10k_normalization(self):
        tokens = ["colony"] * 100  # 100 tokens
        text = " ".join(tokens)
        records = [_record("era_1850_1899", text)]
        result = analyze_eras(records, vocabularies=VOCAB)
        era = result["eras"]["era_1850_1899"]
        # 100 colony tokens in 100 tokens -> 100/100*10000 = 10000/10k.
        assert era["terms_per_10k"]["colony"] == 10000.0
        assert era["documents"] == 1
        assert era["tokens"] == 100

    def test_counts_deterministic_and_sorted(self):
        records = [
            _record("era_1900_1949", "the colony foraging cost benefit colony"),
        ]
        one = analyze_eras(records, vocabularies=VOCAB)
        two = analyze_eras(records, vocabularies=VOCAB)
        assert one == two
        assert one["terms"]["colony"]["era_1900_1949"] == 2

    def test_multiword_window_non_overlapping(self):
        records = [_record("era_1950_1970", "division of labor of labor")]
        result = analyze_eras(records, vocabularies=VOCAB)
        # "division of labor" matches once; the trailing "of labor" is
        # not a standalone vocabulary term.
        assert result["terms"]["division of labor"]["total"] == 1

    def test_term_domains_membership(self):
        result = analyze_eras([], vocabularies=VOCAB)
        assert result["terms"]["colony"]["domains"] == ["unit_of_individuality"]

    def test_degenerate_empty_corpus(self):
        result = analyze_eras([], vocabularies=VOCAB)
        for era in ERA_KEYS:
            stats = result["eras"][era]
            assert stats["documents"] == 0
            assert stats["tokens"] == 0
            assert stats["terms_per_10k"] == {
                t: 0.0 for t in ("colony", "superorganism", "division of labor",
                                 "foraging", "cost", "benefit")
            }
            assert stats["domains_per_10k"] == {
                "unit_of_individuality": 0.0,
                "behavior_and_identity": 0.0,
                "economics": 0.0,
            }

    def test_degenerate_era_with_zero_tokens(self):
        # One era populated, others empty: empty eras report 0.0, not
        # ZeroDivisionError.
        records = [_record("era_1850_1899", "colony cost")]
        result = analyze_eras(records, vocabularies=VOCAB)
        assert result["eras"]["era_1900_1949"]["tokens"] == 0
        assert result["eras"]["era_1900_1949"]["terms_per_10k"]["colony"] == 0.0

    def test_non_canonical_era_dropped(self):
        records = [_record("era_1849", "colony"), _record(None, "colony")]
        result = analyze_eras(records, vocabularies=VOCAB)
        assert sum(s["documents"] for s in result["eras"].values()) == 0

    def test_all_three_eras_present(self):
        result = analyze_eras([], vocabularies=VOCAB)
        assert tuple(result["eras"]) == ERA_KEYS

    def test_hyphen_linebreak_counted(self):
        records = [_record("era_1850_1899", "super-\norganism theory")]
        result = analyze_eras(records, vocabularies=VOCAB)
        assert result["terms"]["superorganism"]["total"] == 1

    def test_domains_per_10k_sum_of_members(self):
        records = [_record("era_1850_1899", "colony cost benefit colony")]
        result = analyze_eras(records, vocabularies=VOCAB)
        era = result["eras"]["era_1850_1899"]
        # 4 tokens: colony 2, cost 1, benefit 1 -> 5000 each.
        assert era["domains_per_10k"]["unit_of_individuality"] == 5000.0
        assert era["domains_per_10k"]["economics"] == 5000.0
        assert era["terms_per_10k"]["colony"] == 5000.0


class TestBuildArtifact:
    def test_schema(self, tmp_path):
        # No shards: degenerate but schema-complete artifact.
        artifact = build_artifact(tmp_path)
        assert artifact["layer"] == "bhl_historical"
        assert "generated" in artifact
        assert artifact["source"]["documents"] == 0
        assert tuple(artifact["eras"]) == ERA_KEYS
        assert isinstance(artifact["terms"], dict)

    def test_preloaded_records_used(self, tmp_path):
        records = [_record("era_1850_1899", "colony " * 10)]
        artifact = build_artifact(tmp_path, records=records)
        assert artifact["source"]["documents"] == 1
        era = artifact["eras"]["era_1850_1899"]
        assert era["documents"] == 1
        assert era["terms_per_10k"]["colony"] == 10000.0


class TestMainCli:
    def test_writes_artifact_next_to_corpus(self, monkeypatch, tmp_path):
        # Seed one shard so main() has something to analyze.
        from data.bhl_corpus import write_shard

        data_dir = tmp_path / "bhl"
        data_dir.mkdir()
        write_shard(
            data_dir / "bhl_shard_00001.json",
            [_record("era_1900_1949", "colony foraging cost")],
        )
        output = tmp_path / "era_term_usage.json"
        rc = main(["--data-dir", str(data_dir), "--output", str(output)])
        assert rc == 0
        artifact = json.loads(output.read_text(encoding="utf-8"))
        assert artifact["layer"] == "bhl_historical"
        assert artifact["eras"]["era_1900_1949"]["documents"] == 1
        assert artifact["eras"]["era_1900_1949"]["terms_per_10k"]["colony"] > 0

    def test_default_output_is_data_dir(self, monkeypatch, tmp_path):
        from data.bhl_corpus import write_shard

        data_dir = tmp_path / "bhl"
        data_dir.mkdir()
        write_shard(
            data_dir / "bhl_shard_00001.json",
            [_record("era_1950_1970", "colony")],
        )
        rc = main(["--data-dir", str(data_dir)])
        assert rc == 0
        assert (data_dir / ARTIFACT_NAME).exists()
# ── Full-stack extension (clean_ocr_text + analyze_era_stack) ────────

_RICH_ERA_TEXTS = [
    (
        "The ant colony exhibits division of labor. The queen ant lays "
        "eggs in the brood chamber. Worker ants forage for food. The "
        "colony has a caste system. Soldier ants defend the nest. Ant "
        "workers tend the brood. The queen ant controls the colony. "
        "Foraging ants return to the nest. The ant society grows. "
        "Worker ants clean the nest. The queen lays many eggs. Ants "
        "cooperate in the colony."
    ),
    (
        "Ant colonies organize through local rules. The queen ant "
        "founds the colony alone. Workers perform division of labor "
        "tasks. The caste structure includes soldiers. Foraging "
        "workers collect seeds for the colony. The ant queen lays "
        "eggs daily. Young ants develop in the brood nest. The "
        "colony defends its nest. Ant workers feed the queen. The "
        "ant society reproduces when the queen lays eggs."
    ),
]


def _era_records(era: str = "era_1850_1899") -> list:
    """Two records of one era with a viable recurring vocabulary."""
    return [_record(era, text) for text in _RICH_ERA_TEXTS]


def _noise_era_records(era: str = "era_1850_1899") -> list:
    """Records of one era with no recurring vocabulary."""
    return [
        _record(era, "Zz9 qwerty frobnicate glorp blorf."),
        _record(era, "Snix quuxle wibble vox nix."),
    ]


@pytest.fixture(scope="module")
def rich_stack():
    """One shared full-stack result over the rich synthetic era."""
    return analyze_era_stack(_era_records())


@pytest.fixture(scope="module")
def expanded_artifact(tmp_path_factory):
    """Shared artifact: one populated era, two degenerate eras."""
    records = _era_records() + _noise_era_records("era_1900_1949")
    return build_artifact(
        tmp_path_factory.mktemp("bhl_build"), records=records
    )

class TestCleanOcrText:
    def test_drops_digit_runs_and_single_letters(self):
        # Page numbers, folio letters, stray glyphs: no vocabulary
        # signal (every domain seed term is >=2 alphabetic chars).
        assert clean_ocr_text("page 12; fol. a v 3, ANTS") == "page fol. ants"

    def test_keeps_words_and_hyphen_compounds(self):
        assert clean_ocr_text("The COLONY-LEVEL x foraging.") == (
            "the colony-level foraging."
        )

    def test_keeps_letters_inside_words(self):
        # OCR mangle "iiV" is not a folio single letter: kept whole.
        assert clean_ocr_text("iiV ants 1910,") == "iiv ants"

    def test_hyphen_linebreak_still_joined(self):
        assert clean_ocr_text("super-\norganism 2.") == "superorganism"


class TestAnalyzeEraStack:
    def test_extraction_section(self, rich_stack):
        extraction = rich_stack["extraction"]
        assert extraction["n_terms"] > 0
        assert extraction["min_frequency"] == OCR_MIN_TERM_FREQUENCY
        for domain, entry in extraction["domains"].items():
            assert entry["term_count"] >= 1
            assert entry["total_frequency"] >= entry["term_count"]

    def test_entropy_section(self, rich_stack):
        entropy = rich_stack["entropy"]
        assert entropy is not None
        assert entropy["n_terms_evaluated"] <= ENTROPY_TOP_TERMS
        assert (
            entropy["n_valid"] + entropy["n_excluded"]
            == entropy["n_terms_evaluated"]
        )
        assert entropy["n_valid"] >= 1, (
            "the synthetic era repeats terms across sentences, so at "
            "least one bounded term must reach ok status"
        )
        for value in entropy["terms"].values():
            assert value >= 0.0
        for domain in entropy["domains"]:
            assert domain in {
                "unit_of_individuality",
                "behavior_and_identity",
                "power_and_labor",
                "sex_and_reproduction",
                "kin_and_relatedness",
                "economics",
            }

    def test_framing_section(self, rich_stack):
        framing = rich_stack["framing"]
        assert framing is not None
        assert framing["overall"]["n_contexts"] > 0
        for entry in framing.values():
            assert 0.0 <= entry["proportion"] <= 1.0
            assert entry["n_contexts"] > 0

    def test_degenerate_era_omits_honestly(self):
        stack = analyze_era_stack(_noise_era_records())
        assert stack["extraction"]["n_terms"] == 0
        assert stack["extraction"]["domains"] == {}
        assert stack["entropy"] is None
        assert stack["framing"] is None
        assert stack["skipped"], "omission must be recorded, not silent"

    def test_deterministic(self):
        records = _era_records()
        one = analyze_era_stack(records)
        two = analyze_era_stack(records)
        assert one == two


class TestBuildArtifactExpanded:
    def test_expanded_schema(self, expanded_artifact):
        artifact = expanded_artifact
        assert artifact["layer"] == "bhl_historical"
        assert "ocr_cleaning" in artifact["source"]
        assert "stack" in artifact["source"]
        populated = artifact["eras"]["era_1850_1899"]
        for section in ("extraction", "entropy", "framing"):
            assert section in populated
        assert isinstance(artifact["skipped"], list)
        for entry in artifact["skipped"]:
            assert entry["kind"]
            assert entry["reason"]

    def test_backward_compatible_per_10k(self, expanded_artifact):
        for era in ERA_KEYS:
            stats = expanded_artifact["eras"][era]
            assert "terms_per_10k" in stats
            assert "domains_per_10k" in stats
        assert isinstance(expanded_artifact["terms"], dict)

    def test_degenerate_era_skips_stack(self, expanded_artifact):
        artifact = expanded_artifact
        empty_era = artifact["eras"]["era_1950_1970"]
        assert "extraction" not in empty_era
        assert "entropy" not in empty_era
        assert "framing" not in empty_era
        kinds = {(e["kind"], e.get("era")) for e in artifact["skipped"]}
        assert ("era_stack", "era_1950_1970") in kinds
        # Noise era: stack runs, extraction finds nothing -> omissions.
        noise_era = artifact["eras"]["era_1900_1949"]
        assert noise_era["extraction"]["n_terms"] == 0
        assert noise_era["entropy"] is None
        assert noise_era["framing"] is None
        noise_skips = {
            e["kind"] for e in artifact["skipped"] if e.get("era") == "era_1900_1949"
        }
        assert "era_stack" in noise_skips
