"""Interrupted-era recovery using real text and local checkpoint files."""
import json
from pathlib import Path

import pytest

from pipeline.bhl_analysis import ERA_KEYS, analyze_eras, build_artifact


def _records() -> list[dict[str, str]]:
    """Use archived literature text; era assignment is a recovery-test fixture."""
    corpus = Path(__file__).resolve().parents[1] / "data/corpus/abstracts.json"
    texts = json.loads(corpus.read_text())
    return [{"era": era, "full_text": texts[index] * 10}
            for index, era in enumerate(ERA_KEYS)]


def test_checkpointed_build_matches_independent_literal_counts(tmp_path: Path):
    # Given real text spanning all three canonical eras.
    records = _records()
    checkpoint_dir = tmp_path / "checkpoints"
    # When an era-checkpointed build finishes and is then resumed.
    first = build_artifact(tmp_path, records, checkpoint_dir=checkpoint_dir)
    checkpoints = sorted(checkpoint_dir.glob("*.json"))
    assert len(checkpoints) == 3
    mtimes = {p.name: p.stat().st_mtime_ns for p in checkpoints}
    second = build_artifact(tmp_path, records, checkpoint_dir=checkpoint_dir)
    # Then completed eras are reused and literal results match the original API.
    assert mtimes == {p.name: p.stat().st_mtime_ns for p in checkpoints}
    assert first["eras"] == second["eras"]
    reference = analyze_eras(records)
    assert first["terms"] == reference["terms"]
    for era in ERA_KEYS:
        for key, value in reference["eras"][era].items():
            assert first["eras"][era][key] == value


def test_changed_era_does_not_reuse_its_checkpoint(tmp_path: Path):
    # Given a completed real corpus snapshot.
    records = _records()
    directory = tmp_path / "checkpoints"
    build_artifact(tmp_path, records, checkpoint_dir=directory)
    # When only one era's text changes with the same record count.
    previous_count = analyze_eras(records)["terms"]["queen"][ERA_KEYS[0]]
    records[0]["full_text"] += " queen " * 20
    second = build_artifact(tmp_path, records, checkpoint_dir=directory)
    # Then its new literal count is observed, not the preceding cached value.
    assert second["terms"]["queen"][ERA_KEYS[0]] == previous_count + 20


def test_tampered_completed_era_fails_instead_of_certifying_it(tmp_path: Path):
    # Given a completed checkpoint with a body-bound result digest.
    directory = tmp_path / "checkpoints"
    build_artifact(tmp_path, _records(), checkpoint_dir=directory)
    target = directory / (ERA_KEYS[0] + ".json")
    payload = json.loads(target.read_text())
    # When the saved scientific output changes without its receipt digest.
    payload["result"]["era"]["documents"] = 999
    target.write_text(json.dumps(payload))
    # Then a subsequent full build fails visibly.
    with pytest.raises(ValueError, match="checkpoint content"):
        build_artifact(tmp_path, _records(), checkpoint_dir=directory)


def test_development_checkpoint_cannot_satisfy_full_default(tmp_path: Path, monkeypatch):
    # Given a completed explicitly bounded calculation.
    directory = tmp_path / "checkpoints"
    records = _records()
    budget = max(len(record["full_text"]) for record in records)
    monkeypatch.setenv("BHL_STACK_CHARACTER_BUDGET", str(budget))
    bounded = build_artifact(tmp_path, records, checkpoint_dir=directory)
    assert bounded["eras"][ERA_KEYS[0]]["stack_coverage"]["character_budget"] == budget
    # When the default unbounded calculation is requested.
    monkeypatch.delenv("BHL_STACK_CHARACTER_BUDGET")
    complete = build_artifact(tmp_path, records, checkpoint_dir=directory)
    # Then bounded checkpoint coverage is not reused.
    assert complete["eras"][ERA_KEYS[0]]["stack_coverage"]["character_budget"] is None


@pytest.mark.parametrize("contents", ["[]", "NaN", "{broken json"])
def test_invalid_checkpoint_fails_visibly(tmp_path: Path, contents: str):
    # Given a malformed local recovery file.
    directory = tmp_path / "checkpoints"
    directory.mkdir()
    (directory / (ERA_KEYS[0] + ".json")).write_text(contents)
    # When a build encounters it, then parsing cannot become a false success.
    with pytest.raises(ValueError):
        build_artifact(tmp_path, _records(), checkpoint_dir=directory)
