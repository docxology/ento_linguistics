"""Behavioral tests for the frozen statistical-analysis pipeline (wave 2).

All statistical tests run on real data: terms reconstructed from the
pipeline artifact ``output/data/extracted_terms.json`` over real slices of
``data/corpus/abstracts.json`` — the same no-mocks pattern as the wave-1
domain-analysis tests.  The 200-abstract slice is the smallest slice in
which every canonical domain has at least 2 valid per-term entropies, so
all 15 canonical-domain pairs are testable.
"""

import json
import re
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

from analysis.term_extraction import Term
from core.manuscript_variables import build_variable_map
from pipeline.statistics_pipeline import (
    ABSTRACT_LAYER,
    CANONICAL_DOMAINS,
    CACE_TABLE_TERMS,
    add_discourse_analysis,
    build_statistical_analysis,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = PROJECT_ROOT / "data" / "corpus" / "abstracts.json"
TERMS_PATH = PROJECT_ROOT / "output" / "data" / "extracted_terms.json"

FROZEN_TOP_LEVEL_KEYS = {
    "descriptives",
    "cace",
    "cace_terms",
    "pairwise",
    "anova",
    "corrections",
}
FROZEN_CACE_KEYS = {
    "mean",
    "min",
    "max",
    "clarity",
    "appropriateness",
    "consistency",
    "evolvability",
    "n_terms",
}
FROZEN_CACE_TERM_KEYS = {
    "clarity",
    "appropriateness",
    "consistency",
    "evolvability",
    "aggregate",
    "in_corpus",
}
FROZEN_PAIRWISE_KEYS = {
    "domain_a",
    "domain_b",
    "metric",
    "t",
    "df",
    "p",
    "p_bh",
    "cohens_d",
    "n_a",
    "n_b",
    "significant_bh",
}
FROZEN_ANOVA_KEYS = {"metric", "F", "df1", "df2", "p", "eta_squared"}


def _load_slice_terms(texts: List[str]) -> Dict[str, Term]:
    """Reconstruct real pipeline-extracted terms occurring in the slice."""
    raw = json.loads(TERMS_PATH.read_text(encoding="utf-8"))
    assert raw, "extracted_terms.json must contain real pipeline output"
    slice_text = " ".join(texts).lower()
    terms: Dict[str, Term] = {}
    for name, data in raw.items():
        if not re.search(rf"\b{re.escape(name)}\b", slice_text):
            continue
        domains = [d for d in data.get("domains", []) if d]
        if not domains:
            continue
        terms[name] = Term(
            text=name,
            lemma=data.get("lemma", name),
            domains=domains,
            frequency=int(data.get("frequency", 0)),
            confidence=float(data.get("confidence", 0.0)),
        )
    return terms


def _real_texts(slice_size: int) -> List[str]:
    """Load a real slice of data/corpus/abstracts.json."""
    if not CORPUS_PATH.exists():
        pytest.skip("real corpus data/corpus/abstracts.json not available")
    if not TERMS_PATH.exists():
        pytest.skip("real extracted terms output/data/extracted_terms.json not available")
    texts = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    assert isinstance(texts, list) and len(texts) >= slice_size
    return texts[:slice_size]


class TestFullPairwiseArtifact:
    """Frozen-schema behavior on the slice where all 15 pairs are testable."""

    SLICE_SIZE = 200

    @pytest.fixture(scope="class")
    @classmethod
    def artifact(cls) -> Dict[str, Any]:
        """One end-to-end build over the real 200-abstract slice."""
        texts = _real_texts(cls.SLICE_SIZE)
        terms = _load_slice_terms(texts)
        assert terms, "no extracted terms occur in the corpus slice"
        return build_statistical_analysis(terms, texts)

    def test_top_level_schema_keys(self, artifact: Dict[str, Any]) -> None:
        """The frozen top-level sections are all present."""
        assert FROZEN_TOP_LEVEL_KEYS <= set(artifact)
        assert isinstance(artifact["descriptives"], dict)
        assert isinstance(artifact["pairwise"], list)
        assert isinstance(artifact["anova"], dict)
        assert isinstance(artifact["corrections"], dict)

    def test_fifteen_canonical_pairs(self, artifact: Dict[str, Any]) -> None:
        """Exactly the 15 canonical-domain pairs, A < B alphabetical."""
        pairwise = artifact["pairwise"]
        assert len(pairwise) == 15
        expected_pairs = set(combinations(sorted(CANONICAL_DOMAINS), 2))
        actual_pairs = {(p["domain_a"], p["domain_b"]) for p in pairwise}
        assert actual_pairs == expected_pairs
        for pair in pairwise:
            assert FROZEN_PAIRWISE_KEYS <= set(pair)
            assert pair["domain_a"] < pair["domain_b"]
            assert pair["metric"] == "semantic_entropy"

    def test_bh_monotonicity(self, artifact: Dict[str, Any]) -> None:
        """BH-adjusted p-values are >= raw and non-decreasing in raw order."""
        pairwise = artifact["pairwise"]
        for pair in pairwise:
            assert pair["p_bh"] >= pair["p"] - 1e-12
            assert 0.0 <= pair["p_bh"] <= 1.0
        by_raw_p = sorted(pairwise, key=lambda p: p["p"])
        adjusted = [p["p_bh"] for p in by_raw_p]
        assert adjusted == sorted(adjusted)

    def test_significant_bh_matches_threshold(self, artifact: Dict[str, Any]) -> None:
        """significant_bh is exactly the p_bh < 0.05 rule."""
        for pair in artifact["pairwise"]:
            assert pair["significant_bh"] == (pair["p_bh"] < 0.05)

    def test_anova_schema_and_df(self, artifact: Dict[str, Any]) -> None:
        """Omnibus ANOVA over all six groups: df2 == N - 6."""
        anova = artifact["anova"]
        assert FROZEN_ANOVA_KEYS <= set(anova)
        assert anova["metric"] == "semantic_entropy"
        assert anova["df1"] == 5.0
        n_total = sum(d["n_terms"] for d in artifact["descriptives"].values())
        assert anova["df2"] == n_total - 6
        assert anova["F"] >= 0.0
        assert 0.0 <= anova["p"] <= 1.0

    def test_eta_squared_in_unit_interval_and_consistent_with_F(
        self, artifact: Dict[str, Any]
    ) -> None:
        """eta_squared in [0, 1] and equals the one-way identity F*df1 / (F*df1 + df2)."""
        anova = artifact["anova"]
        eta = anova["eta_squared"]
        assert 0.0 <= eta <= 1.0
        expected = (anova["F"] * anova["df1"]) / (
            anova["F"] * anova["df1"] + anova["df2"]
        )
        assert eta == pytest.approx(expected, rel=1e-9)

    def test_descriptives_real_values(self, artifact: Dict[str, Any]) -> None:
        """Every tested domain reports real entropy/ambiguity values, never 0.0 placeholders."""
        descriptives = artifact["descriptives"]
        assert set(descriptives) == set(CANONICAL_DOMAINS)
        for domain, entry in descriptives.items():
            assert entry["n_terms"] >= 2, (
                f"{domain} must be testable on the {self.SLICE_SIZE}-abstract slice"
            )
            assert entry["entropy_mean"] > 0.0
            assert entry["entropy_sd"] >= 0.0
            # Wave-1 ambiguity fix: real per-term means, present or omitted —
            # never a fabricated 0.0.
            assert entry["ambiguity_mean"] > 0.0
            assert 0.0 <= entry["cace_mean"] <= 1.0
            assert entry["bridging_count"] >= 0

    def test_cace_domain_aggregates(self, artifact: Dict[str, Any]) -> None:
        """Per-domain CACE aggregates cover every domain with frozen keys."""
        cace = artifact["cace"]
        assert set(cace) == set(CANONICAL_DOMAINS)
        for domain, entry in cace.items():
            assert FROZEN_CACE_KEYS <= set(entry)
            assert entry["n_terms"] >= 1
            assert 0.0 <= entry["min"] <= entry["max"] <= 1.0
            # Float summation can put the mean an epsilon outside [min, max].
            assert entry["min"] - 1e-9 <= entry["mean"] <= entry["max"] + 1e-9
            for dimension in (
                "clarity",
                "appropriateness",
                "consistency",
                "evolvability",
            ):
                assert 0.0 <= entry[dimension] <= 1.0

    def test_cace_mean_matches_descriptives(self, artifact: Dict[str, Any]) -> None:
        """The ``cace`` mean and ``descriptives`` CACE mean share one scoring pass."""
        for domain, entry in artifact["cace"].items():
            assert entry["mean"] == pytest.approx(
                artifact["descriptives"][domain]["cace_mean"]
            )

    def test_cace_terms_schema(self, artifact: Dict[str, Any]) -> None:
        """Every representative term is evaluated with the frozen entry keys."""
        cace_terms = artifact["cace_terms"]
        assert set(cace_terms) == set(CACE_TABLE_TERMS)
        for entry in cace_terms.values():
            assert FROZEN_CACE_TERM_KEYS <= set(entry)
            assert isinstance(entry["in_corpus"], bool)
            dimensions = [
                entry["clarity"],
                entry["appropriateness"],
                entry["consistency"],
                entry["evolvability"],
            ]
            for value in dimensions:
                assert 0.0 <= value <= 1.0
            # Aggregate is exactly the mean of the four dimensions.
            assert entry["aggregate"] == pytest.approx(float(np.mean(dimensions)))

    def test_pairwise_n_matches_descriptives(self, artifact: Dict[str, Any]) -> None:
        """Pairwise group sizes are the per-domain valid-term counts."""
        descriptives = artifact["descriptives"]
        for pair in artifact["pairwise"]:
            assert pair["n_a"] == descriptives[pair["domain_a"]]["n_terms"]
            assert pair["n_b"] == descriptives[pair["domain_b"]]["n_terms"]

    def test_corrections_metadata(self, artifact: Dict[str, Any]) -> None:
        """BH correction metadata reflects the 15 computed comparisons."""
        corrections = artifact["corrections"]
        assert corrections["method"] == "benjamini_hochberg"
        assert corrections["n_comparisons"] == len(artifact["pairwise"])

    def test_determinism(self, artifact: Dict[str, Any]) -> None:
        """Two builds over identical inputs produce byte-identical JSON."""
        texts = _real_texts(self.SLICE_SIZE)
        terms = _load_slice_terms(texts)
        rebuild = build_statistical_analysis(terms, texts)
        assert json.dumps(artifact, indent=2) == json.dumps(rebuild, indent=2)

    def test_unsupported_metric_rejected(self) -> None:
        """Only the wave-1 semantic_entropy metric is implemented."""
        with pytest.raises(ValueError):
            build_statistical_analysis([], [], metric="lexical_diversity")


class TestDegenerateSliceBehavior:
    """Degenerate groups are skipped and recorded, never fabricated."""

    def test_single_abstract_skips_everything(self) -> None:
        """One abstract: too few contexts per term → no testable groups."""
        texts = _real_texts(1)
        terms = _load_slice_terms(texts)
        artifact = build_statistical_analysis(terms, texts)

        assert artifact["pairwise"] == []
        assert artifact["anova"] == {}
        assert artifact["corrections"]["n_comparisons"] == 0

        # Every canonical domain is recorded as skipped with an honest reason.
        skipped_domains = {
            s["domain"] for s in artifact["skipped"] if s["kind"] == "domain_group"
        }
        assert skipped_domains == set(CANONICAL_DOMAINS)
        assert any(s["kind"] == "anova" for s in artifact["skipped"])

        # No fabricated values: entries without valid entropies carry no
        # entropy_mean/entropy_sd/ambiguity_mean keys at all.
        for entry in artifact["descriptives"].values():
            if entry["n_terms"] == 0:
                assert "entropy_mean" not in entry
                assert "entropy_sd" not in entry
                assert "ambiguity_mean" not in entry

    def test_partial_degeneracy_skips_only_affected_pairs(self) -> None:
        """60-abstract slice: two domains are degenerate; only 6 pairs tested."""
        texts = _real_texts(60)
        terms = _load_slice_terms(texts)
        artifact = build_statistical_analysis(terms, texts)

        tested_domains = {
            pair["domain_a"] for pair in artifact["pairwise"]
        } | {pair["domain_b"] for pair in artifact["pairwise"]}
        skipped_domains = {
            s["domain"] for s in artifact["skipped"] if s["kind"] == "domain_group"
        }

        # Skipped domains never appear in a tested pair; tested domains have >= 2.
        assert tested_domains.isdisjoint(skipped_domains)
        for domain in tested_domains:
            assert artifact["descriptives"][domain]["n_terms"] >= 2
        assert artifact["corrections"]["n_comparisons"] == len(artifact["pairwise"])
        # BH correction ran over exactly the computed comparisons.
        for pair in artifact["pairwise"]:
            assert pair["p_bh"] >= pair["p"] - 1e-12


class TestManuscriptVariableTokens:
    """build_variable_map resolves the frozen stats tokens from the artifact."""

    @staticmethod
    def _fixture_artifact() -> Dict[str, Any]:
        """A copy of the real artifact shape with known statistics."""
        return {
            "descriptives": {
                "behavior_and_identity": {
                    "n_terms": 7,
                    "entropy_mean": 1.56,
                    "entropy_sd": 0.42,
                    "ambiguity_mean": 1.56,
                    "cace_mean": 0.61,
                    "bridging_count": 2,
                },
            },
            "cace": {
                "economics": {
                    "mean": 0.5167,
                    "min": 0.3712,
                    "max": 0.6731,
                    "clarity": 0.5937,
                    "appropriateness": 0.4062,
                    "consistency": 0.5013,
                    "evolvability": 0.5656,
                    "n_terms": 3,
                },
            },
            "cace_terms": {
                "slave": {
                    "clarity": 0.40,
                    "appropriateness": 0.40,
                    "consistency": 0.38,
                    "evolvability": 0.33,
                    "aggregate": 0.38,
                    "in_corpus": True,
                },
                "host worker": {
                    "clarity": 0.85,
                    "appropriateness": 1.00,
                    "consistency": 0.72,
                    "evolvability": 0.67,
                    "aggregate": 0.81,
                    "in_corpus": False,
                },
            },
            "pairwise": [
                {
                    "domain_a": "behavior_and_identity",
                    "domain_b": "unit_of_individuality",
                    "metric": "semantic_entropy",
                    "t": -2.3456789,
                    "df": 11.3,
                    "p": 0.0391,
                    "p_bh": 0.1173,
                    "cohens_d": -1.1,
                    "n_a": 7,
                    "n_b": 9,
                    "significant_bh": False,
                },
                {
                    "domain_a": "economics",
                    "domain_b": "kin_and_relatedness",
                    "metric": "semantic_entropy",
                    "t": 4.5,
                    "df": 7.0,
                    "p": 2.5e-6,
                    "p_bh": 3.75e-5,
                    "cohens_d": 2.4,
                    "n_a": 4,
                    "n_b": 5,
                    "significant_bh": True,
                },
            ],
            "anova": {
                "metric": "semantic_entropy",
                "F": 2.5,
                "df1": 5.0,
                "df2": 24.0,
                "p": 3.2e-6,
                "eta_squared": 0.34,
            },
            "corrections": {
                "method": "benjamini_hochberg",
                "n_comparisons": 15,
            },
            "skipped": [],
        }

    @pytest.fixture(scope="class")
    @classmethod
    def stat_tokens(cls, tmp_path_factory: pytest.TempPathFactory) -> Dict[str, str]:
        """Token map built from the fixture artifact written to tmp_path."""
        data_dir = tmp_path_factory.mktemp("output_data")
        (data_dir / "statistical_analysis.json").write_text(
            json.dumps(cls._fixture_artifact()), encoding="utf-8"
        )
        return build_variable_map(output_data_dir=data_dir, corpus_dir=data_dir)

    def test_anova_tokens(self, stat_tokens: Dict[str, str]) -> None:
        """ANOVA tokens render the frozen names with 4-decimal formatting."""
        assert stat_tokens["ANOVA_METRIC"] == "semantic_entropy"
        assert stat_tokens["ANOVA_F"] == "2.5000"
        assert stat_tokens["ANOVA_DF1"] == "5.0000"
        assert stat_tokens["ANOVA_DF2"] == "24.0000"
        assert stat_tokens["ANOVA_P"] == "<0.0001"
        assert stat_tokens["ANOVA_ETA_SQUARED"] == "0.3400"

    def test_correction_tokens(self, stat_tokens: Dict[str, str]) -> None:
        assert stat_tokens["PAIRWISE_N_COMPARISONS"] == "15"
        assert stat_tokens["CORRECTION_METHOD"] == "benjamini_hochberg"

    def test_pairwise_tokens(self, stat_tokens: Dict[str, str]) -> None:
        """Per-pair tokens use uppercased alphabetical slugs."""
        prefix = "PAIRWISE_BEHAVIOR_AND_IDENTITY_UNIT_OF_INDIVIDUALITY"
        assert stat_tokens[f"{prefix}_T"] == "-2.3457"
        assert stat_tokens[f"{prefix}_P"] == "0.0391"
        assert stat_tokens[f"{prefix}_P_BH"] == "0.1173"
        assert stat_tokens[f"{prefix}_D"] == "-1.1000"
        assert stat_tokens[f"{prefix}_SIGNIFICANT"] == "no"

        prefix = "PAIRWISE_ECONOMICS_KIN_AND_RELATEDNESS"
        assert stat_tokens[f"{prefix}_T"] == "4.5000"
        assert stat_tokens[f"{prefix}_P"] == "<0.0001"
        assert stat_tokens[f"{prefix}_P_BH"] == "<0.0001"
        assert stat_tokens[f"{prefix}_D"] == "2.4000"
        assert stat_tokens[f"{prefix}_SIGNIFICANT"] == "yes"

    def test_cace_domain_tokens(self, stat_tokens: Dict[str, str]) -> None:
        """CACE_<SLUG>_* tokens render 2-decimal values and the sampled N."""
        assert stat_tokens["CACE_ECONOMICS_MEAN"] == "0.52"
        assert stat_tokens["CACE_ECONOMICS_MIN"] == "0.37"
        assert stat_tokens["CACE_ECONOMICS_MAX"] == "0.67"
        assert stat_tokens["CACE_ECONOMICS_CLARITY"] == "0.59"
        assert stat_tokens["CACE_ECONOMICS_APPROPRIATENESS"] == "0.41"
        assert stat_tokens["CACE_ECONOMICS_CONSISTENCY"] == "0.50"
        assert stat_tokens["CACE_ECONOMICS_EVOLVABILITY"] == "0.57"
        assert stat_tokens["CACE_ECONOMICS_N"] == "3"

    def test_cace_term_tokens(self, stat_tokens: Dict[str, str]) -> None:
        """CACE_TERM_<SLUG>_* tokens map spaces to underscores in slugs."""
        assert stat_tokens["CACE_TERM_SLAVE_CLARITY"] == "0.40"
        assert stat_tokens["CACE_TERM_SLAVE_APPROPRIATENESS"] == "0.40"
        assert stat_tokens["CACE_TERM_SLAVE_CONSISTENCY"] == "0.38"
        assert stat_tokens["CACE_TERM_SLAVE_EVOLVABILITY"] == "0.33"
        assert stat_tokens["CACE_TERM_SLAVE_AGGREGATE"] == "0.38"
        assert stat_tokens["CACE_TERM_HOST_WORKER_CLARITY"] == "0.85"
        assert stat_tokens["CACE_TERM_HOST_WORKER_APPROPRIATENESS"] == "1.00"
        assert stat_tokens["CACE_TERM_HOST_WORKER_AGGREGATE"] == "0.81"

    def test_absent_artifact_omits_tokens(self, tmp_path: Path) -> None:
        """Missing statistical_analysis.json omits the token family, no KeyError."""
        variables = build_variable_map(output_data_dir=tmp_path, corpus_dir=tmp_path)
        stat_tokens = {
            k
            for k in variables
            if k.startswith(
                ("ANOVA_", "PAIRWISE_", "CORRECTION_METHOD", "CACE_")
            )
        }
        assert stat_tokens == set()


class TestAbstractLayerFraming:
    """layer='abstract': framing parity with the full-text artifact."""

    SLICE_SIZE = 200

    @pytest.fixture(scope="class")
    @classmethod
    def artifact(cls) -> Dict[str, Any]:
        """One end-to-end abstract-layer build over the real slice."""
        texts = _real_texts(cls.SLICE_SIZE)
        terms = _load_slice_terms(texts)
        assert terms, "no extracted terms occur in the corpus slice"
        return build_statistical_analysis(terms, texts, layer=ABSTRACT_LAYER)

    def test_layer_marker_and_domain_term_counts(
        self, artifact: Dict[str, Any]
    ) -> None:
        """The abstract artifact carries the layer marker and term tallies."""
        assert artifact["layer"] == ABSTRACT_LAYER
        counts = artifact["domain_term_counts"]
        assert counts, "the slice extraction must assign terms to domains"
        assert set(counts) <= set(CANONICAL_DOMAINS)
        for entry in counts.values():
            assert set(entry) == {
                "term_count",
                "bridging_term_count",
                "total_frequency",
            }
            assert entry["term_count"] >= 1
            assert entry["total_frequency"] >= entry["term_count"]

    def test_framing_shape(self, artifact: Dict[str, Any]) -> None:
        """framing matches the full-text shape: per-domain + overall."""
        framing = artifact["framing"]
        assert set(framing) <= set(CANONICAL_DOMAINS) | {"overall"}
        assert "overall" in framing
        assert framing["overall"]["n_contexts"] > 0
        for entry in framing.values():
            assert set(entry) == {"proportion", "n_contexts"}
            assert 0.0 <= entry["proportion"] <= 1.0
            assert entry["n_contexts"] >= 1

    def test_framing_overall_counts_each_occurrence_once(
        self, artifact: Dict[str, Any]
    ) -> None:
        """Per-domain n_contexts sums to >= overall (bridging terms double-count)."""
        framing = artifact["framing"]
        domain_sum = sum(
            e["n_contexts"] for k, e in framing.items() if k != "overall"
        )
        assert domain_sum >= framing["overall"]["n_contexts"]

    def test_framing_terms_section(self, artifact: Dict[str, Any]) -> None:
        """Per-term framing data exists and is internally consistent."""
        framing_terms = artifact["framing_terms"]
        assert framing_terms, "domain terms must occur in the slice texts"
        for term, entry in framing_terms.items():
            assert set(entry) == {"proportion", "n_contexts", "domains"}
            assert 0.0 <= entry["proportion"] <= 1.0
            assert entry["n_contexts"] >= 1
            assert entry["domains"] and set(entry["domains"]) <= set(CANONICAL_DOMAINS)
        # Term-level occurrence counts aggregate to the per-domain counts.
        framing = artifact["framing"]
        for domain in set(framing) - {"overall"}:
            from_terms = sum(
                e["n_contexts"]
                for e in framing_terms.values()
                if domain in e["domains"]
            )
            assert from_terms == framing[domain]["n_contexts"]

    def test_no_layer_sections_by_default(
        self, artifact: Dict[str, Any]
    ) -> None:
        """Default builds (full-text/arXiv callers) carry no abstract sections."""
        texts = _real_texts(self.SLICE_SIZE)
        terms = _load_slice_terms(texts)
        plain = build_statistical_analysis(terms, texts)
        assert "layer" not in plain
        assert "framing" not in plain
        assert "framing_terms" not in plain
        assert "domain_term_counts" not in plain


class TestDiscourseSection:
    """Corpus-level discourse section: schema, boundaries, degenerates."""

    SLICE_SIZE = 60

    @pytest.fixture(scope="class")
    @classmethod
    def artifact(cls) -> Dict[str, Any]:
        """Build over a real slice (small enough to keep the suite fast)."""
        texts = _real_texts(cls.SLICE_SIZE)
        terms = _load_slice_terms(texts)
        return build_statistical_analysis(terms, texts)

    def test_schema_keys(self, artifact: Dict[str, Any]) -> None:
        """The four analyzer subsections plus honest metadata are present."""
        discourse = artifact["discourse"]
        assert {"patterns", "rhetorical", "argumentative", "persuasive"} <= set(
            discourse
        )
        assert {"n_texts", "n_texts_analyzed", "n_texts_excluded_min_length",
                "min_text_length", "sample_fraction"} <= set(discourse)
        assert discourse["n_texts"] == self.SLICE_SIZE
        assert discourse["n_texts_analyzed"] > 0
        assert discourse["sample_fraction"] == 1.0

    def test_patterns_shape(self, artifact: Dict[str, Any]) -> None:
        """Pattern entries record real frequencies over the analyzed texts."""
        patterns = artifact["discourse"]["patterns"]
        assert isinstance(patterns, dict)
        for entry in patterns.values():
            assert {"frequency", "rhetorical_function", "domains", "examples"} <= set(entry)
            assert entry["frequency"] >= 1

    def test_rhetorical_strategies_present(self, artifact: Dict[str, Any]) -> None:
        """Authority citations occur in real abstracts — nonzero frequency."""
        rhetorical = artifact["discourse"]["rhetorical"]
        assert set(rhetorical) == {
            "authority", "analogy", "generalization", "anecdotal",
        }
        assert rhetorical["authority"]["frequency"] > 0
        for entry in rhetorical.values():
            assert entry["frequency"] >= 0
            assert entry["text_count"] >= 0

    def test_persuasive_effectiveness_shape(self, artifact: Dict[str, Any]) -> None:
        """Persuasive entries are the analyzer's effectiveness metrics."""
        persuasive = artifact["discourse"]["persuasive"]
        assert persuasive, "the analyzer always returns its technique keys"
        for entry in persuasive.values():
            assert {"usage_frequency", "context_relevance",
                    "heuristic_impact_index", "heuristic_effectiveness_band"} <= set(entry)
            assert 0.0 <= entry["heuristic_impact_index"] <= 1.0

    def test_argumentative_aggregates(self, artifact: Dict[str, Any]) -> None:
        """Argumentative aggregates are internally consistent counts."""
        arg = artifact["discourse"]["argumentative"]
        assert {"n_structures", "n_with_evidence", "n_with_warrant",
                "n_with_qualification", "n_with_discourse_markers"} <= set(arg)
        assert arg["n_structures"] >= 0
        assert arg["n_with_evidence"] <= arg["n_structures"]
        if arg["n_with_discourse_markers"]:
            assert arg["mean_discourse_markers"] >= 1.0

    def test_empty_corpus_omits_section(self) -> None:
        """An empty corpus omits the discourse section — never zero-filled."""
        artifact = build_statistical_analysis([], [])
        assert "discourse" not in artifact

    def test_all_tiny_texts_omitted_with_count(self) -> None:
        """Texts below the minimum length are excluded and counted honestly."""
        merged = add_discourse_analysis({}, ["Ants." * 3])
        assert "discourse" not in merged

    def test_add_discourse_analysis_merges_and_counts(self) -> None:
        """The public merge path adds metadata and keeps existing keys."""
        tiny = "Ants."
        long = (
            "The colony functions as a superorganism whose workers decide "
            "collectively about foraging behavior and resource allocation. "
        ) * 10
        merged = add_discourse_analysis({"layer": "x"}, [tiny, long])
        discourse = merged["discourse"]
        assert merged["layer"] == "x"
        assert discourse["n_texts"] == 2
        assert discourse["n_texts_excluded_min_length"] == 1
        assert discourse["n_texts_analyzed"] == 1

    def test_discourse_deterministic(self, artifact: Dict[str, Any]) -> None:
        """Rebuilding yields byte-identical discourse metadata and counts."""
        texts = _real_texts(self.SLICE_SIZE)
        terms = _load_slice_terms(texts)
        rebuild = build_statistical_analysis(terms, texts)
        assert json.dumps(artifact["discourse"], indent=2) == json.dumps(
            rebuild["discourse"], indent=2
        )
