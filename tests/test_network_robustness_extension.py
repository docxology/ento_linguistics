"""Independent numerical controls for fixed-margin network randomization."""

from collections import Counter
from itertools import combinations

import networkx as nx
import numpy as np
import pytest

from research.network_robustness.model import MatrixError, curveball_trade, project, validate_rows


def test_projection_matches_independent_networkx_and_document_counts():
    rows = [{0, 1, 2}, {0, 1}, {2, 3}, set()]
    counts = Counter(pair for row in rows for pair in combinations(sorted(row), 2))
    graph = nx.Graph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from(counts)
    actual = project(rows, 5)
    assert actual.edges == len(counts) == 4
    assert actual.total_weight == sum(counts.values()) == 5
    assert actual.clustering == pytest.approx(nx.average_clustering(graph))


def test_trades_preserve_both_margins_and_invariant_weight():
    rows = [{0, 1, 2}, {0, 3}, {1, 4}, {2, 3, 4}, set()]
    sizes = list(map(len, rows))
    columns = Counter(value for row in rows for value in row)
    rng = np.random.default_rng(42)
    original = [row.copy() for row in rows]
    for _ in range(1000):
        curveball_trade(rows, rng)
        assert list(map(len, rows)) == sizes
        assert Counter(value for row in rows for value in row) == columns
    assert rows != original
    assert project(rows, 5).total_weight == sum(size * (size - 1) // 2 for size in sizes)


def test_two_row_chain_visits_all_six_states_including_self_loops():
    rows = [{0, 1}, {2, 3}]
    rng = np.random.default_rng(7)
    counts = Counter()
    for _ in range(6000):
        curveball_trade(rows, rng)
        counts[tuple(sorted(rows[0]))] += 1
    assert set(counts) == set(combinations(range(4), 2))
    assert all(800 < count < 1200 for count in counts.values())


def test_seed_is_reproducible_and_empty_identical_rows_do_not_change():
    results = []
    for _ in range(2):
        rows = [{0}, {1}, {0, 1}, set()]
        rng = np.random.default_rng(11)
        for _ in range(50):
            curveball_trade(rows, rng)
        results.append(rows)
    assert results[0] == results[1]
    assert not curveball_trade([{0}, {0}], np.random.default_rng(1))
    assert not curveball_trade([set(), {0}], np.random.default_rng(1))


@pytest.mark.parametrize(
    "rows,n_terms", [([], 2), ([set(), set()], 2), ([{2}, {0}], 2), ([{0}, {True}], 2), ([{0}, {1}], 1)]
)
def test_invalid_matrix_fails(rows, n_terms):
    with pytest.raises(MatrixError):
        validate_rows(rows, n_terms)


def test_trade_requires_two_rows():
    with pytest.raises(MatrixError):
        curveball_trade([{0}], np.random.default_rng(1))


def test_degenerate_chain_preserves_fixed_matrix_and_reports_undefined_rhat():
    from research.network_robustness.study import Protocol, StudyData, sample_chain, summarize

    data = StudyData((frozenset({0, 1}), frozenset({0, 1})), ("queen", "worker"), (), 1, 0.0)
    protocol = Protocol(samples_per_chain=20, burn_sweeps=1)
    values = np.stack([sample_chain(data, protocol, seed) for seed in protocol.seeds])
    assert np.all(values[:, :, 0] == 1)
    assert np.all(values[:, :, 1] == 0)
    assert summarize(values[:, :, 0], 1).rhat is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"samples_per_chain": 0},
        {"burn_sweeps": True},
        {"spacing_sweeps": 0},
        {"seeds": (1, 1, 2)},
        {"seeds": (-1, 2, 3)},
    ],
)
def test_invalid_protocol_rejected(kwargs):
    from research.network_robustness.study import Protocol

    with pytest.raises(MatrixError):
        Protocol(**kwargs)


def receipt_fixture(out):
    import hashlib
    import json
    from dataclasses import asdict
    from pathlib import Path
    from research.network_robustness.study import Protocol

    root = Path(__file__).resolve().parents[1]
    names = [
        "data/corpus/abstracts.json",
        "data/corpus/provenance.json",
        "output/data/extracted_terms.json",
        "output/data/concept_map_summary.json",
        "output/data/analysis_manifest.json",
        "uv.lock",
    ]
    inputs = [root / name for name in names] + list((root / "research/network_robustness").glob("*.py"))
    for name in ["network_robustness.json", "chain_statistics.npy", "network_robustness.png", "network_robustness.md"]:
        (out / name).write_bytes((root / "output/extensions/network_robustness" / name).read_bytes())
    receipt = {
        "protocol": asdict(Protocol()),
        "inputs": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "outputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()},
    }
    (out / "receipt.json").write_text(json.dumps(receipt))
    return root, receipt


def test_receipt_rejects_changed_real_output(tmp_path):
    from research.network_robustness.receipt import validate_receipt
    from research.network_robustness.study import Protocol

    root, _ = receipt_fixture(tmp_path)
    validate_receipt(root, tmp_path, Protocol())
    (tmp_path / "network_robustness.json").write_text('{"edges":5}')
    with pytest.raises(MatrixError, match="output changed"):
        validate_receipt(root, tmp_path, Protocol())


def test_empty_extension_inventory_is_rejected(tmp_path):
    import json
    from research.network_robustness.receipt import validate_receipt
    from research.network_robustness.study import Protocol

    root, receipt = receipt_fixture(tmp_path)
    receipt["outputs"] = {}
    (tmp_path / "receipt.json").write_text(json.dumps(receipt))
    with pytest.raises(MatrixError):
        validate_receipt(root, tmp_path, Protocol())


@pytest.mark.parametrize("artifact", ["chain_statistics.npy", "network_robustness.json", "network_robustness.png"])
def test_self_hashed_corruption_is_rejected(tmp_path, artifact):
    import hashlib
    import json
    from research.network_robustness.receipt import validate_receipt
    from research.network_robustness.study import Protocol

    root, receipt = receipt_fixture(tmp_path)
    target = tmp_path / artifact
    if artifact.endswith("json"):
        report = json.loads(target.read_text())
        report["metrics"]["edges"]["null_mean"] += 1
        target.write_text(json.dumps(report))
    else:
        target.write_bytes(b"invalid but nonempty artifact")
    receipt["outputs"][artifact] = hashlib.sha256(target.read_bytes()).hexdigest()
    (tmp_path / "receipt.json").write_text(json.dumps(receipt))
    with pytest.raises(MatrixError):
        validate_receipt(root, tmp_path, Protocol())


@pytest.mark.parametrize(
    "mutation", ["nan", "shape", "fractional_edges", "clustering", "status", "documents", "markdown"]
)
def test_self_hashed_semantic_inconsistency_is_rejected(tmp_path, mutation):
    import hashlib
    import json
    from research.network_robustness.receipt import validate_receipt
    from research.network_robustness.study import Protocol

    root, receipt = receipt_fixture(tmp_path)
    if mutation in {"nan", "shape", "fractional_edges", "clustering"}:
        target = tmp_path / "chain_statistics.npy"
        values = np.load(target, allow_pickle=False)
        if mutation == "nan":
            values[0, 0, 0] = np.nan
        elif mutation == "shape":
            values = values[:, :-1, :]
        elif mutation == "fractional_edges":
            values[0, 0, 0] = 0.5
        else:
            values[0, 0, 1] = 1.01
        np.save(target, values, allow_pickle=False)
    elif mutation == "markdown":
        target = tmp_path / "network_robustness.md"
        target.write_text("# Results\nNo statistics retained.\n")
    else:
        target = tmp_path / "network_robustness.json"
        report = json.loads(target.read_text())
        report[mutation] = "pending" if mutation == "status" else report[mutation] - 1
        target.write_text(json.dumps(report))
    receipt["outputs"][target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    (tmp_path / "receipt.json").write_text(json.dumps(receipt))
    with pytest.raises(MatrixError):
        validate_receipt(root, tmp_path, Protocol())


def test_summary_matches_analytical_three_chain_control():
    from research.network_robustness.study import summarize

    values = np.stack([np.arange(1, 21), np.arange(2, 22), np.arange(3, 23)])
    summary = summarize(values, 11)
    assert summary.null_mean == 11.5
    assert summary.chain_means == (10.5, 11.5, 12.5)
    assert (summary.null_q025, summary.null_q975) == (2, 21)
    assert summary.rhat == pytest.approx((685 / 700) ** 0.5)
    assert summary.upper_tail_fraction == 33 / 60
    assert summary.lower_tail_fraction == 30 / 60


def test_png_with_valid_checksums_but_invalid_pixel_stream_is_rejected(tmp_path):
    import hashlib
    import json
    import struct
    import zlib
    from PIL import Image
    from research.network_robustness.receipt import validate_receipt
    from research.network_robustness.study import Protocol

    root, receipt = receipt_fixture(tmp_path)
    target = tmp_path / "network_robustness.png"
    source = target.read_bytes()
    chunks = [source[:8]]
    offset = 8
    while offset < len(source):
        size = struct.unpack(">I", source[offset : offset + 4])[0]
        kind = source[offset + 4 : offset + 8]
        content = source[offset + 8 : offset + 8 + size]
        if kind == b"IDAT":
            content = b"not a zlib stream"
        chunks.append(struct.pack(">I", len(content)) + kind + content + struct.pack(">I", zlib.crc32(kind + content)))
        offset += size + 12
    target.write_bytes(b"".join(chunks))
    # PNG container/CRC verification alone accepts this broken pixel stream.
    with Image.open(target) as figure:
        figure.verify()
    receipt["outputs"][target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    (tmp_path / "receipt.json").write_text(json.dumps(receipt))
    with pytest.raises(MatrixError, match="cannot be decoded"):
        validate_receipt(root, tmp_path, Protocol())
