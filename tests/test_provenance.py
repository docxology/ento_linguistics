"""Content provenance and tamper controls using real files."""
import json
from pathlib import Path

import pytest

from core.provenance import (files_sha256, records_sha256,
                             write_analysis_manifest, validate_analysis_manifest)


def test_record_signatures_bind_order_and_text():
    assert records_sha256([{"a": 1, "b": 2}]) == records_sha256([{"b": 2, "a": 1}])
    assert records_sha256(["ant", "colony"]) != records_sha256(["colony", "ant"])
    assert records_sha256(["ant"]) != records_sha256(["ants"])
    with pytest.raises(ValueError):
        records_sha256([float("nan")])


def test_file_signatures_bind_contents(tmp_path):
    source = tmp_path / "source.json"
    source.write_text("ant")
    original = files_sha256([source])
    source.write_text("bee")
    assert files_sha256([source]) != original
    with pytest.raises(FileNotFoundError):
        files_sha256([tmp_path / "absent"])


def _project(tmp_path: Path) -> Path:
    (tmp_path / "data" / "corpus").mkdir(parents=True)
    (tmp_path / "output" / "data").mkdir(parents=True)
    (tmp_path / "data" / "corpus" / "abstracts.json").write_text('["ant study"]')
    (tmp_path / "output" / "data" / "corpus_statistics.json").write_text('{"total_tokens": 2}')
    return tmp_path


def test_manifest_detects_source_and_output_tampering(tmp_path):
    root = _project(tmp_path)
    write_analysis_manifest(root)
    validate_analysis_manifest(root)
    output = root / "output" / "data" / "corpus_statistics.json"
    output.write_text('{"total_tokens": 3}')
    with pytest.raises(ValueError, match="changed"):
        validate_analysis_manifest(root)
    write_analysis_manifest(root)
    (root / "data" / "corpus" / "abstracts.json").write_text('["bee study"]')
    with pytest.raises(ValueError, match="changed"):
        validate_analysis_manifest(root)


def test_missing_manifest_is_not_a_success(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_analysis_manifest(tmp_path)


def test_manifest_rejects_missing_and_extra_files(tmp_path):
    root = _project(tmp_path)
    write_analysis_manifest(root)
    (root / "output" / "data" / "unbound.json").write_text('{}')
    with pytest.raises(ValueError, match="inventory"):
        validate_analysis_manifest(root)


def test_manifest_rejects_empty_inventory(tmp_path):
    (tmp_path / "output" / "data").mkdir(parents=True)
    with pytest.raises(ValueError, match="empty"):
        write_analysis_manifest(tmp_path)


def test_manifest_discloses_and_checks_selected_nltk_resources(tmp_path):
    # Given a receipt over real project inputs and installed NLTK resources.
    root = _project(tmp_path)
    manifest = write_analysis_manifest(root)
    assert set(manifest["nltk_resources"]) == {
        "punkt_tab_english", "stopwords_english", "wordnet"
    }
    assert all(len(value) == 64 for value in manifest["nltk_resources"].values())
    # When the receipt falsely identifies its dictionary bytes.
    manifest["nltk_resources"]["wordnet"] = "0" * 64
    target = root / "output/data/analysis_manifest.json"
    target.write_text(json.dumps(manifest))
    # Then rendering/custody validation rejects the false resource evidence.
    with pytest.raises(ValueError, match="NLTK resources changed"):
        validate_analysis_manifest(root)
