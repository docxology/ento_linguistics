"""Decode retained evidence and verify numerical agreement beyond byte identity."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from .model import MatrixError, project
from .study import Protocol, load_study, summarize


def validate_artifacts(root: Path, out: Path, protocol: Protocol) -> None:
    """Reject unreadable artifacts, invalid draws and inconsistent summaries.

    Reconstruct the observed graph from identified abstracts and replay summaries
    from every retained draw. This checks internal consistency, not chain mixing.
    """
    try:
        report = json.loads((out / "network_robustness.json").read_text())
        values = np.load(out / "chain_statistics.npy", allow_pickle=False)
        with Image.open(out / "network_robustness.png") as figure:
            if figure.format != "PNG" or min(figure.size) < 100:
                raise MatrixError("Extension figure is not a usable PNG")
            figure.load()
        markdown = (out / "network_robustness.md").read_text()
    except (ValueError, OSError, EOFError, UnicodeError, UnidentifiedImageError) as error:
        raise MatrixError(f"Extension artifact cannot be decoded: {error}") from error
    if (
        not isinstance(values, np.ndarray)
        or values.shape != (len(protocol.seeds), protocol.samples_per_chain, 2)
        or values.dtype.kind not in "fiu"
        or not np.isfinite(values).all()
    ):
        raise MatrixError("Extension retained draws have invalid shape, type or finite values")
    data = load_study(root)
    observed = project([set(row) for row in data.rows], len(data.terms))
    maximum_edges = len(data.terms) * (len(data.terms) - 1) // 2
    if (
        np.any(values[:, :, 0] < 0)
        or np.any(values[:, :, 0] > maximum_edges)
        or np.any(values[:, :, 0] != np.floor(values[:, :, 0]))
        or np.any(values[:, :, 1] < 0)
        or np.any(values[:, :, 1] > 1)
    ):
        raise MatrixError("Extension retained statistics violate graph bounds")
    expected_metrics = {
        name: asdict(summarize(values[:, :, index], value))
        for index, (name, value) in enumerate((("edges", observed.edges), ("clustering", observed.clustering)))
    }
    sensitivity = {
        str(count): asdict(project([set(v for v in row if v < count) for row in data.rows], count))
        for count in (25, 50, 100)
    }
    expected = {
        "status": "completed",
        "documents": len(data.rows),
        "vocabulary": list(data.terms),
        "protocol": asdict(protocol),
        "observed": asdict(observed),
        "metrics": expected_metrics,
        "vocabulary_sensitivity": sensitivity,
    }
    expected = json.loads(json.dumps(expected, allow_nan=False))
    if not isinstance(report, dict) or any(report.get(key) != value for key, value in expected.items()):
        raise MatrixError("Extension report disagrees with reconstructed inputs or retained draws")
    for name, summary in expected_metrics.items():
        rhat = f"{summary['rhat']:.4f}" if summary["rhat"] is not None else "Undefined: zero within-chain variance"
        row = (
            f"| {name} | {summary['observed']:.6g} | {summary['null_mean']:.6g} | "
            f"{summary['null_q025']:.6g}–{summary['null_q975']:.6g} | {rhat} |"
        )
        if row not in markdown:
            raise MatrixError("Extension readable report disagrees with retained draws")
