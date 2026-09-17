"""Tests for era-stratified BHL analysis (src/pipeline/bhl_analysis.py).

Fixture-based only: records are synthetic dicts; the artifact write is
exercised against tmp_path.  No live network, no ``output/`` writes.
"""

from __future__ import annotations

import json

from pipeline.bhl_analysis import (
    ARTIFACT_NAME,
    ERA_KEYS,
    analyze_eras,
    build_artifact,
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
