"""Tests for core.manuscript_variables.

Covers JSON loading, publication counting, variable-map construction
(defaults, full data, and empty-data paths), manuscript substitution
(write, dry-run, unknown variables), and the CLI entry point. All inputs
are written to tmp_path using JSON shapes modeled on the project's
``output/data/*.json`` files; no project files are modified.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.manuscript_variables as manuscript_variables_module
from core.manuscript_variables import (
    build_statistical_tokens,
    build_variable_map,
    count_publications,
    fill_manuscript,
    load_json,
)

CORPUS_STATISTICS = {
    "total_tokens": 48787,
    "unique_tokens": 7105,
    "total_characters": 537133,
    "avg_token_length": 7.32,
    "most_common_tokens": [
        ["ant", 1033],
        ["colony", 850],
        ["worker", 831],
        ["queen", 602],
        ["social", 583],
        ["caste", 200],
    ],
    "type_token_ratio": 0.1456,
}

DOMAIN_STATISTICS = {
    "power_and_labor": {
        "term_count": 63,
        "avg_confidence": 0.81,
        "total_frequency": 905,
        "bridging_term_count": 43,
        "semantic_entropy": 0.36,
        "anthropomorphic_proportion": 0.4062,
        "high_entropy_count": 1,
        "high_entropy_pct": 1.6,
    },
    "economics": {
        "term_count": 37,
        "avg_confidence": 0.77,
        "total_frequency": 300,
        "bridging_term_count": 12,
        "semantic_entropy": 0.64,
        "anthropomorphic_proportion": 0.25,
        "high_entropy_count": 3,
        "high_entropy_pct": 8.1,
    },
}

CONCEPT_MAP_SUMMARY = {
    "n_concepts": 6,
    "n_relationships": 9,
    "network_nodes": 894,
    "network_edges": 514,
    "network_clustering": 0.1948,
    "network_avg_degree": 1.15,
    "concepts": {
        "biological_individuality": {
            "description": "What constitutes a biological individual",
            "n_terms": 75,
            "domains": ["unit_of_individuality"],
            "confidence": 0.0,
        },
        "social_organization": {
            "description": "Principles of social organization",
            "n_terms": 98,
            "domains": ["power_and_labor"],
            "confidence": 0.0,
        },
    },
}

EXTRACTED_TERMS = {
    "queen": {
        "lemma": "queen",
        "domains": ["power_and_labor", "sex_and_reproduction"],
        "frequency": 602,
        "confidence": 0.9,
        "n_contexts": 5,
    },
    "worker": {
        "lemma": "worker",
        "domains": ["power_and_labor"],
        "frequency": 831,
        "confidence": 0.8,
        "n_contexts": 4,
    },
    "caste": {
        "lemma": "caste",
        "domains": ["power_and_labor", "behavior_and_identity"],
        "frequency": 125,
        "confidence": 0.8,
        "n_contexts": 3,
    },
    "nest": {
        "lemma": "nest",
        "domains": ["unit_of_individuality"],
        "frequency": 204,
        "confidence": 0.9,
        "n_contexts": 2,
    },
    "forage": {
        "lemma": "forage",
        "domains": [],
        "frequency": 10,
        "confidence": 0.5,
        "n_contexts": 1,
    },
}

ABSTRACTS_LIST = [
    {
        "title": "Colony organization in ants",
        "abstract": "The queen and workers organize the colony.",
    },
    {"title": "Caste determination", "abstract": "Caste fate depends on larval diet."},
    {"title": "Foraging economics", "abstract": "Workers allocate foraging effort."},
]


def _write_json(path: Path, data) -> None:
    """Write a JSON fixture file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@pytest.fixture
def data_dirs(tmp_path) -> tuple[Path, Path]:
    """Create output/data and data/corpus directories with realistic fixtures."""
    output_data = tmp_path / "output" / "data"
    corpus_dir = tmp_path / "data" / "corpus"
    _write_json(output_data / "corpus_statistics.json", CORPUS_STATISTICS)
    _write_json(output_data / "domain_statistics.json", DOMAIN_STATISTICS)
    _write_json(output_data / "concept_map_summary.json", CONCEPT_MAP_SUMMARY)
    _write_json(output_data / "extracted_terms.json", EXTRACTED_TERMS)
    _write_json(corpus_dir / "abstracts.json", ABSTRACTS_LIST)
    return output_data, corpus_dir


class TestLoadJson:
    """Tests for load_json."""

    def test_missing_file_returns_empty_dict(self, tmp_path, capsys) -> None:
        """A missing file yields {} and a visible warning."""
        missing = tmp_path / "nope.json"
        assert load_json(missing) == {}
        assert "WARNING" in capsys.readouterr().out

    def test_round_trips_json_content(self, tmp_path) -> None:
        """Existing JSON files are parsed into their Python value."""
        path = tmp_path / "ok.json"
        _write_json(path, {"a": 1, "b": ["x"]})
        assert load_json(path) == {"a": 1, "b": ["x"]}


class TestCountPublications:
    """Tests for count_publications."""

    def test_counts_list_corpus(self, tmp_path) -> None:
        """A list-shaped abstracts.json is counted by length."""
        abstracts = tmp_path / "abstracts.json"
        _write_json(abstracts, [{"title": "a"}, {"title": "b"}, {"title": "c"}])
        assert count_publications(tmp_path) == 3

    def test_counts_dict_with_abstracts_key(self, tmp_path) -> None:
        """A dict-shaped corpus with an 'abstracts' key counts that list."""
        abstracts = tmp_path / "abstracts.json"
        _write_json(abstracts, {"abstracts": [{"title": "a"}, {"title": "b"}]})
        assert count_publications(tmp_path) == 2

    def test_missing_corpus_returns_zero(self, tmp_path) -> None:
        """No abstracts.json means zero publications."""
        assert count_publications(tmp_path) == 0

    def test_unrecognized_shape_returns_zero(self, tmp_path) -> None:
        """A dict without an 'abstracts' key counts as zero."""
        abstracts = tmp_path / "abstracts.json"
        _write_json(abstracts, {"records": [{"title": "a"}]})
        assert count_publications(tmp_path) == 0


class TestBuildVariableMap:
    """Tests for build_variable_map."""

    def test_full_variable_map_from_realistic_outputs(self, data_dirs) -> None:
        """Every variable family reflects the fixture data and formatting."""
        output_data, corpus_dir = data_dirs
        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)

        # Corpus-level variables
        assert variables["CORPUS_PUBLICATIONS"] == "3"
        assert variables["CORPUS_TOTAL_TOKENS"] == "48787"
        assert variables["CORPUS_UNIQUE_TOKENS"] == "7105"
        assert variables["CORPUS_TTR"] == "0.1456"
        assert variables["CORPUS_CANDIDATE_TERMS"] == "5"
        # 4 of 5 terms have domains; 2 of those span multiple domains
        assert variables["CORPUS_DOMAIN_TERMS"] == "4"
        assert variables["CORPUS_DRIFT_PERCENTAGE"] == "50.0"

        # Concept-map and network variables
        assert variables["CORPUS_CONCEPT_COUNT"] == "6"
        assert variables["CORPUS_RELATIONSHIP_COUNT"] == "9"
        assert variables["NETWORK_NODES"] == "894"
        assert variables["NETWORK_EDGES"] == "514"
        assert variables["NETWORK_CLUSTERING"] == "0.1948"
        assert variables["NETWORK_AVG_DEGREE"] == "1.15"

        # Top terms, capped at five
        assert variables["CORPUS_TOP_TERM_1"] == "ant"
        assert variables["CORPUS_TOP_FREQ_1"] == "1033"
        assert variables["CORPUS_TOP_TERM_5"] == "social"
        assert variables["CORPUS_TOP_FREQ_5"] == "583"
        assert "CORPUS_TOP_TERM_6" not in variables

        # Domain-level variables
        assert variables["DOMAIN_POWER_AND_LABOR_TERMS"] == "63"
        assert variables["DOMAIN_POWER_AND_LABOR_N_TERMS"] == "63"
        assert variables["DOMAIN_POWER_AND_LABOR_FREQ"] == "905"
        assert variables["DOMAIN_POWER_AND_LABOR_BRIDGING"] == "43"
        assert variables["DOMAIN_POWER_AND_LABOR_ENTROPY"] == "0.36"
        assert variables["DOMAIN_POWER_AND_LABOR_ANTHROPOMORPHIC_PROPORTION_PCT"] == "40.6"
        assert variables["DOMAIN_POWER_AND_LABOR_HIGH_ENTROPY_PCT"] == "1.6"
        assert variables["DOMAIN_ECONOMICS_TERMS"] == "37"
        assert variables["DOMAIN_ECONOMICS_N_TERMS"] == "37"
        assert variables["DOMAIN_ECONOMICS_ENTROPY"] == "0.64"
        assert variables["DOMAIN_ECONOMICS_ANTHROPOMORPHIC_PROPORTION_PCT"] == "25.0"
        assert variables["DOMAIN_ECONOMICS_HIGH_ENTROPY_PCT"] == "8.1"

        # Corpus entropy aggregates: frequency-weighted across domains
        expected_entropy = (0.36 * 63 + 0.64 * 37) / (63 + 37)
        assert variables["CORPUS_OVERALL_ENTROPY"] == f"{expected_entropy:.2f}"
        assert variables["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] == "4.0"
        # Overall N is the exact sum of the per-domain N column.
        assert variables["CORPUS_OVERALL_N_TERMS"] == "100"

        # Concept-level variables (missing concepts default to 0)
        assert variables["CONCEPT_BIOLOGICAL_INDIVIDUALITY_TERMS"] == "75"
        assert variables["CONCEPT_SOCIAL_ORGANIZATION_TERMS"] == "98"
        assert variables["CONCEPT_KINSHIP_SYSTEMS_TERMS"] == "0"

        # Specific term frequencies (absent terms default to 0)
        assert variables["TERM_FREQ_QUEEN"] == "602"
        assert variables["TERM_FREQ_WORKER"] == "831"
        assert variables["TERM_FREQ_CASTE"] == "125"
        assert variables["TERM_FREQ_ALLOCATION"] == "0"
        assert variables["TERM_FREQ_RESOURCE"] == "0"

    def test_empty_outputs_fall_back_to_defaults(self, tmp_path) -> None:
        """Missing/empty JSON inputs produce zero-valued defaults."""
        output_data = tmp_path / "output" / "data"
        corpus_dir = tmp_path / "data" / "corpus"
        output_data.mkdir(parents=True)
        corpus_dir.mkdir(parents=True)

        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)

        assert variables["CORPUS_PUBLICATIONS"] == "0"
        assert variables["CORPUS_TOTAL_TOKENS"] == "0"
        assert variables["CORPUS_UNIQUE_TOKENS"] == "0"
        assert variables["CORPUS_TTR"] == "0.0000"
        assert variables["CORPUS_CANDIDATE_TERMS"] == "0"
        assert variables["CORPUS_DOMAIN_TERMS"] == "0"
        assert variables["CORPUS_DRIFT_PERCENTAGE"] == "0.0"
        assert variables["CORPUS_CONCEPT_COUNT"] == "0"
        assert variables["CORPUS_OVERALL_ENTROPY"] == "0.00"
        assert variables["CORPUS_OVERALL_HIGH_ENTROPY_PCT"] == "0.0"
        assert variables["CORPUS_OVERALL_N_TERMS"] == "0"
        assert variables["DOMAIN_ECONOMICS_TERMS"] == "0"
        assert variables["DOMAIN_ECONOMICS_N_TERMS"] == "0"
        assert variables["DOMAIN_ECONOMICS_FREQ"] == "0"
        assert variables["CONCEPT_KINSHIP_SYSTEMS_TERMS"] == "0"
        assert variables["TERM_FREQ_QUEEN"] == "0"
        assert "CORPUS_TOP_TERM_1" not in variables

    def test_defaults_to_project_directories(self) -> None:
        """With no arguments, the real project output/corpus dirs are used."""
        variables = build_variable_map()
        expected_pubs = str(count_publications(manuscript_variables_module.CORPUS_DIR))
        assert variables["CORPUS_PUBLICATIONS"] == expected_pubs
        # The real project output exists and is non-trivial
        assert int(variables["CORPUS_PUBLICATIONS"]) > 0
        live_top = json.load(
            open(manuscript_variables_module.OUTPUT_DATA_DIR / "corpus_statistics.json")
        ).get("most_common_tokens", [[None, 0]])[0][0]
        assert variables["CORPUS_TOP_TERM_1"] == str(live_top)

class TestCaceStatisticalTokens:
    """CACE tokens resolve from statistical_analysis.json through build_variable_map."""

    ARTIFACT = {
        "descriptives": {},
        "cace": {
            "economics": {
                "mean": 0.5167,
                "min": 0.3712,
                "max": 0.6731,
                "clarity": 0.5937,
                "appropriateness": 0.4062,
                "consistency": 0.5013,
                "evolvability": 0.5656,
                "n_terms": 9,
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
            "non-reproductive helper": {
                "clarity": 0.82,
                "appropriateness": 1.00,
                "consistency": 0.70,
                "evolvability": 0.67,
                "aggregate": 0.80,
                "in_corpus": False,
            },
        },
        "pairwise": [],
        "anova": {},
        "corrections": {},
        "skipped": [],
    }

    def test_cace_tokens_render_from_artifact(self, data_dirs) -> None:
        """Domain and term CACE tokens render 2-decimal values via slugs."""
        output_data, corpus_dir = data_dirs
        _write_json(output_data / "statistical_analysis.json", self.ARTIFACT)
        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)

        assert variables["CACE_ECONOMICS_MEAN"] == "0.52"
        assert variables["CACE_ECONOMICS_MIN"] == "0.37"
        assert variables["CACE_ECONOMICS_MAX"] == "0.67"
        assert variables["CACE_ECONOMICS_CLARITY"] == "0.59"
        assert variables["CACE_ECONOMICS_APPROPRIATENESS"] == "0.41"
        assert variables["CACE_ECONOMICS_CONSISTENCY"] == "0.50"
        assert variables["CACE_ECONOMICS_EVOLVABILITY"] == "0.57"
        assert variables["CACE_ECONOMICS_N"] == "9"
        assert variables["CACE_TERM_SLAVE_AGGREGATE"] == "0.38"
        assert variables["CACE_TERM_HOST_WORKER_CLARITY"] == "0.85"
        assert variables["CACE_TERM_HOST_WORKER_APPROPRIATENESS"] == "1.00"
        assert variables["CACE_TERM_NON_REPRODUCTIVE_HELPER_CONSISTENCY"] == "0.70"

    def test_absent_artifact_omits_cace_tokens(self, data_dirs) -> None:
        """No statistical_analysis.json → no CACE tokens, no KeyError."""
        output_data, corpus_dir = data_dirs
        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)
        cace_tokens = [k for k in variables if k.startswith("CACE_")]
        assert cace_tokens == []


class TestFulltextStatisticalTokens:
    """FULLTEXT_* tokens resolve from fulltext_analysis.json alongside the
    abstract-layer inferential tokens (parallel layer, shared machinery)."""

    FULLTEXT_ARTIFACT = {
        "layer": "fulltext",
        "n_documents": 3,
        "min_term_frequency": 20,
        "documents": [
            {"pmcid": "PMC1", "token_count": 100},
            {"pmcid": "PMC2", "token_count": 200},
            {"pmcid": "PMC3", "token_count": 301},
        ],
        "domain_term_counts": {},
        "descriptives": {
            "economics": {
                "n_terms": 6,
                "entropy_mean": 2.1685123,
            },
            "power_and_labor": {
                "n_terms": 15,
                "entropy_mean": 1.99965,
            },
        },
        "pairwise": [{"domain_a": "a", "domain_b": "b"}] * 2,
        "anova": {"metric": "entropy_mean", "F": 0.69523, "p": 0.62861},
    }

    def test_fulltext_tokens_render_from_artifact(self, data_dirs) -> None:
        """FULLTEXT_* tokens resolve through build_variable_map."""
        output_data, corpus_dir = data_dirs
        _write_json(
            output_data / "statistical_analysis.json",
            {"pairwise": [], "anova": {}, "corrections": {}, "skipped": []},
        )
        _write_json(
            output_data / "fulltext_analysis.json", self.FULLTEXT_ARTIFACT
        )
        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)

        assert variables["FULLTEXT_DOCUMENTS"] == "3"
        assert variables["FULLTEXT_TOTAL_TOKENS"] == "601"
        assert variables["FULLTEXT_MEDIAN_TOKENS"] == "200.0000"
        assert variables["FULLTEXT_DOMAIN_ECONOMICS_TERMS"] == "6"
        assert variables["FULLTEXT_DOMAIN_ECONOMICS_ENTROPY"] == "2.1685"
        assert variables["FULLTEXT_DOMAIN_POWER_AND_LABOR_TERMS"] == "15"
        assert variables["FULLTEXT_DOMAIN_POWER_AND_LABOR_ENTROPY"] == "1.9996"
        assert variables["FULLTEXT_ANOVA_F"] == "0.6952"
        assert variables["FULLTEXT_ANOVA_P"] == "0.6286"

    def test_fulltext_tokens_direct_call(self) -> None:
        """build_statistical_tokens emits the family for an explicit artifact."""
        tokens = build_statistical_tokens(
            {}, fulltext_artifact=self.FULLTEXT_ARTIFACT
        )
        assert tokens["FULLTEXT_DOCUMENTS"] == "3"
        assert tokens["FULLTEXT_ANOVA_P"] == "0.6286"

    def test_absent_fulltext_artifact_omits_tokens(self, data_dirs) -> None:
        """No fulltext_analysis.json → no FULLTEXT_* tokens, no KeyError."""
        output_data, corpus_dir = data_dirs
        _write_json(
            output_data / "statistical_analysis.json",
            {"pairwise": [], "anova": {}, "corrections": {}, "skipped": []},
        )
        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)
        assert [k for k in variables if k.startswith("FULLTEXT_")] == []

    def test_empty_fulltext_artifact_omits_tokens(self) -> None:
        """Empty artifact dict → no FULLTEXT_* tokens."""
        tokens = build_statistical_tokens({}, fulltext_artifact={})
        assert [k for k in tokens if k.startswith("FULLTEXT_")] == []


class TestFillManuscript:
    """Tests for fill_manuscript."""

    def test_substitutes_known_variables_and_writes(self, tmp_path) -> None:
        """Known placeholders are replaced in place; unknown ones survive."""
        md = tmp_path / "manuscript.md"
        md.write_text(
            "We analyzed {{CORPUS_PUBLICATIONS}} publications about {{CORPUS_TOP_TERM_1}}."
            " The {{UNKNOWN_VARIABLE}} stays.",
            encoding="utf-8",
        )
        results = fill_manuscript(
            {"CORPUS_PUBLICATIONS": "12", "CORPUS_TOP_TERM_1": "ant"},
            manuscript_dir=tmp_path,
        )

        assert results == {"manuscript.md": 2}
        content = md.read_text(encoding="utf-8")
        assert "We analyzed 12 publications about ant." in content
        assert "{{UNKNOWN_VARIABLE}}" in content

    def test_dry_run_counts_without_writing(self, tmp_path) -> None:
        """dry_run reports substitution counts but leaves files untouched."""
        md = tmp_path / "manuscript.md"
        original = "Total tokens: {{CORPUS_TOTAL_TOKENS}}."
        md.write_text(original, encoding="utf-8")

        results = fill_manuscript(
            {"CORPUS_TOTAL_TOKENS": "999"}, dry_run=True, manuscript_dir=tmp_path
        )

        assert results == {"manuscript.md": 1}
        assert md.read_text(encoding="utf-8") == original

    def test_no_substitutions_means_no_result_entry(self, tmp_path) -> None:
        """Files without any known placeholders are omitted from results."""
        md = tmp_path / "manuscript.md"
        md.write_text("No placeholders here.", encoding="utf-8")
        results = fill_manuscript({"CORPUS_PUBLICATIONS": "1"}, manuscript_dir=tmp_path)
        assert results == {}

    def test_no_md_files_returns_empty(self, tmp_path, monkeypatch, capsys) -> None:
        """An empty manuscript directory yields no substitutions and a warning."""
        empty_dir = tmp_path / "docs"
        empty_dir.mkdir()
        monkeypatch.setattr(manuscript_variables_module, "MANUSCRIPT_DIR", empty_dir)

        results = fill_manuscript({"CORPUS_PUBLICATIONS": "1"})

        assert results == {}
        assert "No .md files found" in capsys.readouterr().out

    def test_multiple_files_are_processed_sorted(self, tmp_path) -> None:
        """Every .md file is processed and counts are reported per file."""
        (tmp_path / "a_intro.md").write_text("{{CORPUS_PUBLICATIONS}}", encoding="utf-8")
        (tmp_path / "b_methods.md").write_text(
            "{{CORPUS_PUBLICATIONS}}-{{CORPUS_PUBLICATIONS}}", encoding="utf-8"
        )
        (tmp_path / "notes.txt").write_text("{{CORPUS_PUBLICATIONS}}", encoding="utf-8")

        results = fill_manuscript(
            {"CORPUS_PUBLICATIONS": "7"}, manuscript_dir=tmp_path
        )

        assert results == {"a_intro.md": 1, "b_methods.md": 2}
        assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "{{CORPUS_PUBLICATIONS}}"


class TestMainEntryPoint:
    """Tests for the module's CLI entry point."""

    @pytest.fixture
    def cli_dirs(self, tmp_path, monkeypatch) -> tuple[Path, Path]:
        """Point the module's global directories at tmp_path fixtures."""
        output_data = tmp_path / "output" / "data"
        manuscript_dir = tmp_path / "docs" / "manuscript"
        for path, data in (
            (output_data / "corpus_statistics.json", CORPUS_STATISTICS),
            (output_data / "domain_statistics.json", DOMAIN_STATISTICS),
            (output_data / "concept_map_summary.json", CONCEPT_MAP_SUMMARY),
            (output_data / "extracted_terms.json", EXTRACTED_TERMS),
        ):
            _write_json(path, data)
        (corpus_dir := tmp_path / "data" / "corpus").mkdir(parents=True)
        _write_json(corpus_dir / "abstracts.json", ABSTRACTS_LIST)
        manuscript_dir.mkdir(parents=True)

        monkeypatch.setattr(
            manuscript_variables_module, "OUTPUT_DATA_DIR", output_data
        )
        monkeypatch.setattr(manuscript_variables_module, "MANUSCRIPT_DIR", manuscript_dir)
        monkeypatch.setattr(manuscript_variables_module, "CORPUS_DIR", corpus_dir)
        return output_data, manuscript_dir

    def test_missing_required_files_exits_nonzero(self, tmp_path, monkeypatch) -> None:
        """Absent pipeline outputs abort with SystemExit(1) before any write."""
        output_data = tmp_path / "output" / "data"
        manuscript_dir = tmp_path / "docs" / "manuscript"
        manuscript_dir.mkdir(parents=True)
        monkeypatch.setattr(manuscript_variables_module, "OUTPUT_DATA_DIR", output_data)
        monkeypatch.setattr(manuscript_variables_module, "MANUSCRIPT_DIR", manuscript_dir)

        with pytest.raises(SystemExit) as excinfo:
            manuscript_variables_module.main()
        assert excinfo.value.code == 1

    def test_main_fills_manuscript_and_reports(self, cli_dirs, capsys) -> None:
        """A successful run substitutes placeholders and verifies completion."""
        _, manuscript_dir = cli_dirs
        (manuscript_dir / "results.md").write_text(
            "Publications: {{CORPUS_PUBLICATIONS}}; top term: {{CORPUS_TOP_TERM_1}}.",
            encoding="utf-8",
        )
        (manuscript_dir / "partial.md").write_text(
            "Unmapped: {{NOT_A_REAL_VARIABLE}}.", encoding="utf-8"
        )

        manuscript_variables_module.main()

        out = capsys.readouterr().out
        assert "All template variables successfully filled." not in out
        assert "template variables remain unfilled" in out
        results_md = (manuscript_dir / "results.md").read_text(encoding="utf-8")
        assert results_md.startswith("Publications: 3; top term: ant.")
        partial_md = (manuscript_dir / "partial.md").read_text(encoding="utf-8")
        assert partial_md == "Unmapped: {{NOT_A_REAL_VARIABLE}}."
        assert "TOTAL: 2 substitutions across 1 file" in out

    def test_main_all_variables_filled(self, cli_dirs, capsys) -> None:
        """When no placeholders remain, the success message is printed."""
        _, manuscript_dir = cli_dirs
        (manuscript_dir / "full.md").write_text(
            "{{CORPUS_PUBLICATIONS}} {{CORPUS_TOP_TERM_1}} {{TERM_FREQ_QUEEN}}",
            encoding="utf-8",
        )

        manuscript_variables_module.main()

        out = capsys.readouterr().out
        assert "All template variables successfully filled." in out
        assert "remain unfilled" not in out


class TestBhlTokens:
    """BHL_* tokens resolve from data/bhl/era_term_usage.json (BHL
    historical layer, era-stratified)."""

    @staticmethod
    def _bhl_artifact() -> dict:
        """Realistic era_term_usage.json fixture (subset of eras/terms)."""
        canonical = manuscript_variables_module.BHL_CANONICAL_TERMS
        terms = {
            term: {
                "era_1850_1899": 0,
                "era_1900_1949": 0,
                "era_1950_1970": 0,
                "domains": [],
                "total": 0,
            }
            for term in canonical
        }
        terms["xylophagy"] = {
            "era_1850_1899": 7,
            "era_1900_1949": 0,
            "era_1950_1970": 0,
            "domains": [],
            "total": 7,
        }
        return {
            "layer": "bhl_historical",
            "source": {"documents": 2, "data_dir": "data/bhl"},
            "eras": {
                "era_1850_1899": {
                    "documents": 1,
                    "tokens": 1000,
                    "terms_per_10k": {
                        "caste": 0.5,
                        "queen": 10.25,
                        "superorganism": 0.0,
                        "xylophagy": 3.0,
                    },
                    "domains_per_10k": {},
                },
                "era_1900_1949": {
                    "documents": 1,
                    "tokens": 2000,
                    "terms_per_10k": {
                        "caste": 1.5,
                        "queen": 0.0,
                        "superorganism": 0.0,
                    },
                    "domains_per_10k": {},
                },
                # era_1950_1970 absent → no tokens for that era.
            },
            "terms": terms,
        }

    def test_bhl_tokens_direct_call(self, tmp_path) -> None:
        """BHL_* tokens resolve from a bhl_data_dir via build_statistical_tokens."""
        bhl_dir = tmp_path / "bhl"
        _write_json(bhl_dir / "era_term_usage.json", self._bhl_artifact())
        tokens = build_statistical_tokens({}, bhl_data_dir=bhl_dir)

        assert tokens["BHL_DOCUMENTS"] == "2"
        assert tokens["BHL_ERA_1850_1899_DOCS"] == "1"
        assert tokens["BHL_ERA_1900_1949_DOCS"] == "1"
        assert tokens["BHL_ERA_1850_1899_CASTE_PER_10K"] == "0.5000"
        assert tokens["BHL_ERA_1900_1949_CASTE_PER_10K"] == "1.5000"
        assert tokens["BHL_ERA_1850_1899_QUEEN_PER_10K"] == "10.2500"
        # Zero-frequency canonical terms are kept (absence is signal).
        assert tokens["BHL_ERA_1850_1899_SUPERORGANISM_PER_10K"] == "0.0000"
        # Multi-word term slugified like the CACE_TERM convention.
        assert tokens["BHL_ERA_1850_1899_DIVISION_OF_LABOR_PER_10K"] == "0.0000"
        # Non-canonical terms emit no tokens.
        assert "BHL_ERA_1850_1899_XYLOPHAGY_PER_10K" not in tokens
        # Absent era emits no tokens.
        assert not [k for k in tokens if "ERA_1950_1970" in k]

    def test_absent_bhl_artifact_omits_tokens(self, tmp_path) -> None:
        """No era_term_usage.json → no BHL_* tokens, no KeyError."""
        tokens = build_statistical_tokens({}, bhl_data_dir=tmp_path / "absent")
        assert [k for k in tokens if k.startswith("BHL_")] == []

    def test_bhl_tokens_render_through_variable_map(
        self, data_dirs, monkeypatch
    ) -> None:
        """BHL_* tokens resolve through build_variable_map."""
        output_data, corpus_dir = data_dirs
        bhl_dir = output_data.parent / "bhl_data"
        _write_json(bhl_dir / "era_term_usage.json", self._bhl_artifact())
        monkeypatch.setattr(
            manuscript_variables_module, "BHL_DATA_DIR", bhl_dir
        )
        variables = build_variable_map(
            output_data_dir=output_data, corpus_dir=corpus_dir
        )
        assert variables["BHL_DOCUMENTS"] == "2"
        assert variables["BHL_ERA_1850_1899_CASTE_PER_10K"] == "0.5000"
        assert variables["BHL_ERA_1900_1949_QUEEN_PER_10K"] == "0.0000"

    def test_real_artifact_tokens_resolve(self) -> None:
        """Spot-verify the BHL_* family against the real data/bhl artifact."""
        artifact = manuscript_variables_module.load_json(
            manuscript_variables_module.BHL_DATA_DIR / "era_term_usage.json"
        )
        if not artifact:
            pytest.skip("real BHL artifact not harvested yet")
        tokens = build_statistical_tokens({})
        eras = artifact["eras"]
        assert (
            tokens["BHL_DOCUMENTS"]
            == str(artifact.get("source", {}).get("documents"))
        )
        for era, entry in eras.items():
            era_upper = era.upper()
            assert (
                tokens[f"BHL_{era_upper}_DOCS"] == str(entry["documents"])
            )
            frequencies = entry["terms_per_10k"]
            for term in manuscript_variables_module.BHL_CANONICAL_TERMS:
                if term not in frequencies:
                    continue
                slug = term.upper().replace("-", "_").replace(" ", "_")
                expected = f"{float(frequencies[term]):.4f}"
                assert tokens[f"BHL_{era_upper}_{slug}_PER_10K"] == expected


class TestFulltextFramingTokens:
    """FULLTEXT_*_ANTHROPOMORPHIC / FULLTEXT_ANTHROPOMORPHIC_OVERALL
    resolve from the full-text artifact's ``framing`` section."""

    FRAMING_ARTIFACT = {
        "layer": "fulltext",
        "n_documents": 3,
        "min_term_frequency": 20,
        "documents": [{"pmcid": "PMC1", "token_count": 100}],
        "domain_term_counts": {},
        "descriptives": {},
        "framing": {
            "economics": {"proportion": 0.123456, "n_contexts": 900},
            "power_and_labor": {"proportion": 0.424242, "n_contexts": 1200},
            "overall": {"proportion": 0.25, "n_contexts": 2100},
        },
        "pairwise": [],
        "anova": {},
    }

    def test_framing_tokens_direct_call(self) -> None:
        """Per-domain and overall framing tokens emit from the section."""
        tokens = build_statistical_tokens(
            {}, fulltext_artifact=self.FRAMING_ARTIFACT
        )
        assert tokens["FULLTEXT_DOMAIN_ECONOMICS_ANTHROPOMORPHIC"] == "0.1235"
        assert tokens["FULLTEXT_DOMAIN_POWER_AND_LABOR_ANTHROPOMORPHIC"] == "0.4242"
        assert tokens["FULLTEXT_ANTHROPOMORPHIC_OVERALL"] == "0.2500"
        # The "overall" key must not double as a domain slug.
        assert "FULLTEXT_DOMAIN_OVERALL_ANTHROPOMORPHIC" not in tokens

    def test_framing_tokens_resolve_via_variable_map(self, data_dirs) -> None:
        """Tokens resolve through build_variable_map against the artifact file."""
        output_data, corpus_dir = data_dirs
        _write_json(output_data / "fulltext_analysis.json", self.FRAMING_ARTIFACT)
        variables = build_variable_map(output_data_dir=output_data, corpus_dir=corpus_dir)
        assert variables["FULLTEXT_ANTHROPOMORPHIC_OVERALL"] == "0.2500"
        assert variables["FULLTEXT_DOMAIN_ECONOMICS_ANTHROPOMORPHIC"] == "0.1235"

    def test_absent_framing_section_omits_tokens(self) -> None:
        """Artifact without a ``framing`` section → no framing tokens,
        other FULLTEXT_* tokens unaffected (no KeyError)."""
        artifact = dict(self.FRAMING_ARTIFACT)
        artifact.pop("framing")
        artifact["anova"] = {"F": 1.23456, "p": 0.012345}
        tokens = build_statistical_tokens({}, fulltext_artifact=artifact)
        assert [k for k in tokens if "ANTHROPOMORPHIC" in k] == []
        assert tokens["FULLTEXT_ANOVA_F"] == "1.2346"

    def test_empty_framing_section_omits_tokens(self) -> None:
        """Empty ``framing`` mapping (degenerate corpus) → no framing tokens."""
        artifact = dict(self.FRAMING_ARTIFACT)
        artifact["framing"] = {}
        tokens = build_statistical_tokens({}, fulltext_artifact=artifact)
        assert [k for k in tokens if "ANTHROPOMORPHIC" in k] == []
