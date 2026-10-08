"""Receipted vocabulary/threshold diagnostics for reading a lexical network."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import networkx as nx
import numpy as np

from research.network_robustness.study import load_study

__all__ = ["profile", "run", "ensure", "template_values"]
SIZES = (25, 50, 75, 100)
THRESHOLDS = (1, 2, 5, 10, 20)


def profile(
    rows: Sequence[frozenset[int]], n_terms: int, sizes: Sequence[int], thresholds: Sequence[int]
) -> list[dict[str, Any]]:
    """Measure nested vocabularies with isolates retained and inclusive thresholds.

    Density divides edges by all selected pairs. Clustering includes degree-zero
    and degree-one terms as zero. These are representation diagnostics, not
    complexity indices or estimates of biological interactions.
    """
    if type(n_terms) is not int or n_terms < 2 or len(rows) < 2 or not any(rows):
        raise ValueError("Require at least two terms/documents and an occurrence")
    if any(type(v) is not int or not 0 <= v < n_terms for row in rows for v in row):
        raise ValueError("Invalid incidence index")
    if (
        not sizes
        or not thresholds
        or len(set(sizes)) != len(sizes)
        or len(set(thresholds)) != len(thresholds)
        or any(type(n) is not int or not 2 <= n <= n_terms for n in sizes)
        or any(type(t) is not int or t < 1 for t in thresholds)
    ):
        raise ValueError("Invalid unique vocabulary sizes or positive thresholds")
    incidence = np.zeros((len(rows), n_terms), dtype=np.int64)
    for i, row in enumerate(rows):
        incidence[i, list(row)] = 1
    weights = incidence.T @ incidence
    output = []
    for n in sizes:
        selected = weights[:n, :n].copy()
        np.fill_diagonal(selected, 0)
        for threshold in thresholds:
            graph = nx.from_numpy_array((selected >= threshold).astype(np.int8))
            output.append(
                {
                    "terms": n,
                    "threshold_documents": threshold,
                    "edges": graph.number_of_edges(),
                    "possible_pairs": n * (n - 1) // 2,
                    "density": nx.density(graph),
                    "mean_local_clustering": nx.average_clustering(graph),
                    "components": nx.number_connected_components(graph),
                    "largest_component_terms": max(map(len, nx.connected_components(graph))),
                    "isolated_terms": len(list(nx.isolates(graph))),
                    "documents_with_selected_terms": int((incidence[:, :n].sum(axis=1) > 0).sum()),
                }
            )
    return output


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inputs(root: Path, paths: Sequence[Path]) -> dict[str, str]:
    files = list(paths) + [
        Path(__file__).resolve(),
        root / "research/network_robustness/study.py",
        root / "research/network_robustness/model.py",
    ]
    return {str(p.relative_to(root)): _hash(p) for p in files}


def _figures(out: Path, report: dict[str, Any], root: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for n, color, marker in zip(SIZES, ["#0072B2", "#E69F00", "#009E73", "#6554A4"], ["o", "s", "^", "D"]):
        cells = [x for x in report["cells"] if x["terms"] == n]
        axes[0].plot(
            THRESHOLDS,
            [x["density"] for x in cells],
            marker=marker,
            color=color,
            linewidth=2.5,
            markersize=8,
            label=f"{n} terms",
        )
        axes[1].plot(
            THRESHOLDS,
            [x["mean_local_clustering"] for x in cells],
            marker=marker,
            color=color,
            linewidth=2.5,
            markersize=8,
            label=f"{n} terms",
        )
    for ax, label in zip(axes, ["Edge density (all selected pairs)", "Mean local clustering (isolates = 0)"]):
        ax.set(xlabel="Minimum shared documents (inclusive)", ylabel=label, ylim=(0, 1.03))
        ax.grid(alpha=0.2)
        ax.legend(fontsize=15)
        ax.set_xticks(THRESHOLDS)
        ax.tick_params(labelsize=15)
        ax.xaxis.label.set_size(17)
        ax.yaxis.label.set_size(17)
    fig.suptitle("Vocabulary and threshold sensitivity of the observed lexical network", fontsize=19)
    fig.text(
        0.5,
        0.01,
        "Deterministic representation diagnostic on identified abstracts; no new randomization or causal inference.",
        ha="center",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(out / "network_reading.png", dpi=240)
    plt.close(fig)

    _graphical_abstract(out, report)


def _graphical_abstract(out: Path, report: dict[str, Any]) -> None:
    """Render an explanatory graphical abstract from receipted source counts."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

    colors = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#6554A4"]
    fig = plt.figure(figsize=(16, 9), dpi=240, facecolor="#F7F5EF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 16), ylim=(0, 9))
    ax.axis("off")

    def text(x: float, y: float, s: str, size: int = 16, color: str = "#183040", **kwargs: Any) -> None:
        ax.text(x, y, s, fontsize=size, color=color, va="center", **kwargs)

    def box(x: float, y: float, w: float, h: float, color: str = "#FFFFFF") -> None:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12", fc=color, ec="none"))

    def arrow(a: tuple[float, float], b: tuple[float, float], color: str = "#007D80") -> None:
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=19, lw=2, color=color))

    text(0.55, 8.45, "ENTO-LINGUISTICS", 15, "#007D80", fontweight="bold")
    text(0.55, 7.8, "Complex systems meet scientific language", 30, fontweight="bold")
    text(0.55, 7.23, "Make units explicit. Trace relationships. Test interpretations.", 18)
    box(0.55, 3.7, 7.1, 2.85)
    box(8.1, 3.7, 7.3, 2.85)
    text(0.85, 6.13, "BIOLOGICAL PROCESSES", 15, "#007D80", fontweight="bold")
    for x, y, label in [
        (1.75, 5.1, "Individual\nstate"),
        (4.1, 5.1, "Local\ninteractions"),
        (6.3, 5.1, "Collective\nresponse"),
    ]:
        ax.add_patch(Circle((x, y), 0.54, fc="#E0F0ED", ec="#007D80", lw=2))
        text(x, y, label, 12, ha="center")
    arrow((2.25, 5.1), (3.57, 5.1))
    arrow((4.62, 5.1), (5.77, 5.1))
    arrow((6.3, 4.56), (1.75, 4.56))
    text(4.05, 4.13, "Ecology · information · feedback · scale", 14, ha="center")
    text(8.4, 6.13, "OBSERVED SCIENTIFIC DISCOURSE", 15, "#007D80", fontweight="bold")
    for x, label in [(9.05, "Documents"), (11.65, "Terms &\ncontexts"), (14.2, "Measured\nproxies")]:
        box(x - 0.75, 4.68, 1.5, 0.88, "#EDF1F5")
        text(x, 5.12, label, 13, ha="center")
    arrow((9.82, 5.12), (10.85, 5.12))
    arrow((12.45, 5.12), (13.4, 5.12))
    text(11.75, 4.13, "Co-occurrence · occupancy entropy · CACE", 13, ha="center")
    text(8, 3.28, "Different observational units require separate evidence", 17, ha="center", fontweight="bold")
    domains = [
        "Individuality",
        "Behavior &\nidentity",
        "Power &\nlabor",
        "Sex &\nreproduction",
        "Kin &\nrelatedness",
        "Economics",
    ]
    for i, (name, color) in enumerate(zip(domains, colors)):
        x = 0.6 + i * 2.5
        box(x, 2.2, 2.32, 0.65)
        ax.plot([x, x + 2.32], [2.9, 2.9], color=color, lw=4)
        text(x + 1.16, 2.53, name, 13, ha="center")
    text(
        0.65,
        1.68,
        f"{report['documents']:,} identified abstracts · 4 separate source layers · 6 overlapping domains",
        17,
        fontweight="bold",
    )
    text(
        0.65,
        1.2,
        "Architecture: units & relations   ·   Fertilization: exchange questions   ·   Expansion: validate transfer",
        12,
    )
    text(0.65, 0.72, "Observe → represent → compare → validate", 15, "#007D80", fontweight="bold")
    fig.savefig(out / "graphical_abstract.png", dpi=240)
    plt.close(fig)


def run(root: Path) -> dict[str, Any]:
    """Rebuild a finite deterministic diagnostic with independent input custody."""
    root = root.resolve()
    data = load_study(root)
    out = root / "output/extensions/network_reading"
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": 1,
        "documents": len(data.rows),
        "vocabulary": list(data.terms),
        "protocol": {"sizes": list(SIZES), "thresholds": list(THRESHOLDS), "isolates": "retained"},
        "cells": profile(data.rows, len(data.terms), SIZES, THRESHOLDS),
        "interpretation": "Representation sensitivity, not a scalar complexity measure or biological network.",
    }
    (out / "network_reading.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    _figures(out, report, root)
    receipt = {
        "inputs": _inputs(root, data.input_files),
        "outputs": {
            name: _hash(out / name)
            for name in ["network_reading.json", "network_reading.png", "graphical_abstract.png"]
        },
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return report


def ensure(root: Path) -> dict[str, Any]:
    """Reject changed/self-hashed numerical artifacts and malformed figure streams."""
    from PIL import Image

    root = root.resolve()
    out = root / "output/extensions/network_reading"
    data = load_study(root)
    if not (out / "receipt.json").exists():
        raise ValueError("Network-reading receipt absent; execute research.network_reading.study")
    receipt = json.loads((out / "receipt.json").read_text())
    if set(receipt) != {"inputs", "outputs"} or set(receipt["outputs"]) != {
        "network_reading.json",
        "network_reading.png",
        "graphical_abstract.png",
    }:
        raise ValueError("Incomplete network-reading receipt inventory")
    if receipt["inputs"] != _inputs(root, data.input_files):
        raise ValueError("Network-reading input/source identity changed")
    for name, digest in receipt["outputs"].items():
        if _hash(out / name) != digest:
            raise ValueError("Network-reading artifact bytes changed")
        if name.endswith(".png"):
            with Image.open(out / name) as im:
                im.load()
                if im.format != "PNG" or min(im.size) < 1000:
                    raise ValueError("Invalid network-reading figure format or geometry")
    report = json.loads((out / "network_reading.json").read_text())
    expected = {
        "schema": 1,
        "documents": len(data.rows),
        "vocabulary": list(data.terms),
        "protocol": {"sizes": list(SIZES), "thresholds": list(THRESHOLDS), "isolates": "retained"},
        "cells": profile(data.rows, len(data.terms), SIZES, THRESHOLDS),
        "interpretation": "Representation sensitivity, not a scalar complexity measure or biological network.",
    }
    if report != expected:
        raise ValueError("Network-reading report disagrees with reconstructed observations")
    return report


def template_values(root: Path) -> dict[str, str]:
    """Return manuscript quantities only after complete receipt/numerical checks."""
    report = ensure(root)
    base = next(x for x in report["cells"] if x["terms"] == 100 and x["threshold_documents"] == 1)
    strict = next(x for x in report["cells"] if x["terms"] == 100 and x["threshold_documents"] == 20)
    return {
        "NETREAD_CELLS": str(len(report["cells"])),
        "NETREAD_DOCUMENTS": str(report["documents"]),
        "NETREAD_BASE_DENSITY": f"{base['density']:.4f}",
        "NETREAD_THRESHOLD20_EDGES": str(strict["edges"]),
        "NETREAD_THRESHOLD20_DENSITY": f"{strict['density']:.4f}",
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    run(args.root)
    ensure(args.root)
