"""A separately receipted extension of the frozen published abstract network."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from .model import MatrixError, curveball_trade, project

__all__ = ["Protocol", "StudyData", "load_study", "sample_chain", "summarize", "run"]


@dataclass(frozen=True, slots=True)
class Protocol:
    """Prespecified finite-chain settings; trades include legitimate no-ops."""

    samples_per_chain: int = 200
    burn_sweeps: int = 10
    spacing_sweeps: int = 1
    seeds: tuple[int, ...] = (42, 43, 44)

    def __post_init__(self) -> None:
        if (
            any(type(v) is not int for v in (self.samples_per_chain, self.burn_sweeps, self.spacing_sweeps))
            or self.samples_per_chain < 20
            or self.burn_sweeps < 1
            or self.spacing_sweeps < 1
        ):
            raise MatrixError("Require at least 20 samples and positive burn/spacing sweeps")
        if (
            len(self.seeds) < 3
            or len(set(self.seeds)) != len(self.seeds)
            or any(type(seed) is not int or seed < 0 for seed in self.seeds)
        ):
            raise MatrixError("Require at least three distinct chain seeds")


@dataclass(frozen=True, slots=True)
class StudyData:
    """Full identified abstracts, vocabulary and frozen input identity."""

    rows: tuple[frozenset[int], ...]
    terms: tuple[str, ...]
    input_files: tuple[Path, ...]
    expected_edges: int
    expected_clustering: float


def load_study(root: Path) -> StudyData:
    """Validate the published receipt and independently rebuild all incidences."""
    from core.provenance import validate_analysis_manifest

    validate_analysis_manifest(root)
    paths = (
        root / "data/corpus/abstracts.json",
        root / "data/corpus/provenance.json",
        root / "output/data/extracted_terms.json",
        root / "output/data/concept_map_summary.json",
        root / "output/data/analysis_manifest.json",
        root / "uv.lock",
    )
    texts = json.loads(paths[0].read_text())
    records = json.loads(paths[1].read_text())["records"]
    terms = json.loads(paths[2].read_text())
    expected = json.loads(paths[3].read_text())
    identified = [
        text
        for text in texts
        if str(records.get(hashlib.sha256(text.encode()).hexdigest(), {}).get("pmid", "")).isdigit()
    ]
    selected = tuple(
        sorted(
            (name for name, term in terms.items() if term["domains"]),
            key=lambda name: (-terms[name]["frequency"], name),
        )[:100]
    )
    patterns = [re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE) for name in selected]
    rows = tuple(frozenset(i for i, pattern in enumerate(patterns) if pattern.search(text)) for text in identified)
    if not identified or len(selected) != expected["network_nodes"]:
        raise MatrixError("Published vocabulary or identified corpus is incomplete")
    observed = project([set(row) for row in rows], len(selected))
    if observed.edges != expected["network_edges"] or round(observed.clustering, 4) != expected["network_clustering"]:
        raise MatrixError("Independent reconstruction disagrees with the published network")
    return StudyData(rows, selected, paths, observed.edges, observed.clustering)


def sample_chain(data: StudyData, protocol: Protocol, seed: int) -> NDArray[np.float64]:
    """Sample projected statistics while verifying exact margins every draw."""
    rows = [set(row) for row in data.rows]
    rng = np.random.default_rng(seed)
    n = len(rows)
    sizes = tuple(map(len, rows))
    column = np.bincount([v for row in rows for v in row], minlength=len(data.terms))
    invariant = sum(size * (size - 1) // 2 for size in sizes)
    output = []
    for _ in range(protocol.burn_sweeps * n):
        curveball_trade(rows, rng)
    for i in range(protocol.samples_per_chain):
        for _ in range(protocol.spacing_sweeps * n):
            curveball_trade(rows, rng)
        current = np.bincount([v for row in rows for v in row], minlength=len(data.terms))
        if sizes != tuple(map(len, rows)) or not np.array_equal(column, current):
            raise MatrixError("Randomization changed an incidence margin")
        projected = project(rows, len(data.terms))
        if projected.total_weight != invariant:
            raise MatrixError("Projection violated the analytical total-weight invariant")
        output.append([projected.edges, projected.clustering])
        if (i + 1) % 50 == 0:
            print(f"Seed {seed}: {i + 1}/{protocol.samples_per_chain} samples", flush=True)
    return np.asarray(output, dtype=np.float64)


@dataclass(frozen=True, slots=True)
class MetricSummary:
    """Descriptive finite-chain diagnostics, not calibrated population inference."""

    observed: float
    null_mean: float
    null_q025: float
    null_q975: float
    chain_means: tuple[float, ...]
    rhat: float | None
    upper_tail_fraction: float
    lower_tail_fraction: float


def summarize(values: NDArray[np.float64], observed: float) -> MetricSummary:
    """Compare observation with finite-chain distributions and between-chain spread."""
    chains, samples = values.shape
    within = float(np.var(values, axis=1, ddof=1).mean())
    between = float(samples * np.var(values.mean(axis=1), ddof=1))
    rhat = float(np.sqrt(((samples - 1) * within / samples + between / samples) / within)) if within > 0 else None
    flat = values.reshape(-1)
    return MetricSummary(
        observed,
        float(flat.mean()),
        float(np.quantile(flat, 0.025)),
        float(np.quantile(flat, 0.975)),
        tuple(map(float, values.mean(axis=1))),
        rhat,
        float(np.mean(flat >= observed)),
        float(np.mean(flat <= observed)),
    )


def run(root: Path, out: Path, protocol: Protocol) -> None:
    """Execute the full-corpus extension, source receipt, plot and readable report."""
    from .report import write_report

    data = load_study(root)
    frozen_paths = (*data.input_files, *sorted(Path(__file__).parent.glob("*.py")))
    frozen_inputs = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen_paths}
    print(f"Reproduced {len(data.rows)} documents, {len(data.terms)} terms, {data.expected_edges} edges", flush=True)
    observed = project([set(row) for row in data.rows], len(data.terms))
    values = np.stack([sample_chain(data, protocol, seed) for seed in protocol.seeds])
    sizes = {
        count: asdict(project([set(v for v in row if v < count) for row in data.rows], count))
        for count in (25, 50, 100)
    }
    report = {
        "status": "completed",
        "layer": "identified abstracts",
        "documents": len(data.rows),
        "vocabulary": list(data.terms),
        "method": "Curveball binary incidence trades with fixed document and term margins",
        "protocol": asdict(protocol),
        "observed": asdict(observed),
        "metrics": {
            "edges": asdict(summarize(values[:, :, 0], observed.edges)),
            "clustering": asdict(summarize(values[:, :, 1], observed.clustering)),
        },
        "vocabulary_sensitivity": sizes,
        "limits": [
            "Conditional on the selected vocabulary and identified convenience corpus.",
            "Finite correlated Markov-chain draws; diagnostics do not prove convergence.",
            "Tail fractions are descriptive, not confirmatory population p-values.",
            "A structural departure does not measure author beliefs or causal framing.",
        ],
    }
    for name, digest in frozen_inputs.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise MatrixError(f"Input changed during network sampling: {name}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "network_robustness.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    np.save(out / "chain_statistics.npy", values, allow_pickle=False)
    write_report(
        len(data.rows),
        protocol,
        {
            "edges": summarize(values[:, :, 0], observed.edges),
            "clustering": summarize(values[:, :, 1], observed.clustering),
        },
        values,
        out,
    )
    files = frozen_inputs
    artifacts = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.iterdir())
        if p.name != "receipt.json" and p.is_file()
    }
    (out / "receipt.json").write_text(
        json.dumps(
            {"inputs": files, "outputs": artifacts, "protocol": asdict(protocol), "published_core_unchanged": True},
            indent=2,
        )
        + "\n"
    )
