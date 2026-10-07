"""Validate and regenerate the independently bound network extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .model import MatrixError
from .study import Protocol, run
from .artifacts import validate_artifacts

__all__ = ["validate_receipt", "ensure_extensions"]


def validate_receipt(root: Path, out: Path, protocol: Protocol) -> None:
    """Reject missing, changed or incomplete source/output inventories."""
    receipt = json.loads((out / "receipt.json").read_text())
    from dataclasses import asdict

    if receipt.get("protocol") != json.loads(json.dumps(asdict(protocol))):
        raise MatrixError("Extension sampling protocol changed")
    expected_code = {str(p.relative_to(root)) for p in Path(__file__).parent.glob("*.py")}
    expected_inputs = expected_code | {
        "data/corpus/abstracts.json",
        "data/corpus/provenance.json",
        "output/data/extracted_terms.json",
        "output/data/concept_map_summary.json",
        "output/data/analysis_manifest.json",
        "uv.lock",
    }
    if expected_inputs != set(receipt.get("inputs", {})):
        raise MatrixError("Extension source inventory changed")
    for name, digest in receipt["inputs"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise MatrixError(f"Extension input changed: {name}")
    actual = {p.name for p in out.iterdir() if p.is_file() and p.name != "receipt.json"}
    required_outputs = {
        "network_robustness.json",
        "chain_statistics.npy",
        "network_robustness.png",
        "network_robustness.md",
    }
    if actual != required_outputs or set(receipt.get("outputs", {})) != required_outputs:
        raise MatrixError("Extension output inventory changed")
    for name, digest in receipt["outputs"].items():
        content = (out / name).read_bytes()
        if not content or hashlib.sha256(content).hexdigest() != digest:
            raise MatrixError(f"Extension output changed: {name}")

    validate_artifacts(root, out, protocol)


def ensure_extensions(root: Path) -> None:
    """Keep both executed protocols coherent before rendering their interpretation."""
    base = root / "output/extensions/network_robustness"
    protocols = [
        (base, Protocol()),
        (base / "sensitivity", Protocol(samples_per_chain=100, burn_sweeps=20, spacing_sweeps=2, seeds=(52, 53, 54))),
    ]
    for out, protocol in protocols:
        try:
            validate_receipt(root, out, protocol)
        except (FileNotFoundError, MatrixError, json.JSONDecodeError) as error:
            print(f"Regenerating network extension: {error}", flush=True)
            run(root, out, protocol)
            validate_receipt(root, out, protocol)
