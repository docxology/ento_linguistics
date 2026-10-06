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
        (out / name).write_bytes(b"numerical receipt control")
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
