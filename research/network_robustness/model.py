"""Fixed-margin document/term randomization and projection statistics.

Curveball trades keep both binary incidence margins exactly fixed. The sampled
chain is finite; preservation of margins is not a proof of adequate mixing.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

__all__ = ["MatrixError", "Projection", "validate_rows", "curveball_trade", "project"]


class MatrixError(ValueError):
    """An invalid binary document/term incidence configuration."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True, slots=True)
class Projection:
    """Unweighted projection summaries and its invariant total edge weight."""

    edges: int
    clustering: float
    total_weight: int


def validate_rows(rows: list[set[int]], n_terms: int) -> None:
    """Reject malformed/empty incidence data before sampling."""
    if n_terms < 2 or len(rows) < 2:
        raise MatrixError("At least two terms and two documents are required")
    if any(type(value) is not int or not 0 <= value < n_terms for row in rows for value in row):
        raise MatrixError("Term indices must be integers within the vocabulary")
    if not any(rows):
        raise MatrixError("The incidence matrix has no occurrences")


def curveball_trade(rows: list[set[int]], rng: np.random.Generator) -> bool:
    """Redistribute the exclusive terms of two rows uniformly, allowing self-loops.

    Common terms stay in both rows. Row sizes and every column total are
    preserved. Rows mutate in place; the return value records an actual change.
    Empty and identical rows yield legitimate no-op transitions.
    """
    if len(rows) < 2:
        raise MatrixError("A trade requires two distinct documents")
    first = int(rng.integers(len(rows)))
    second = int(rng.integers(len(rows) - 1))
    second += second >= first
    left, right = rows[first], rows[second]
    common = left & right
    only_left = left - common
    only_right = right - common
    if not only_left or not only_right:
        return False
    pool = np.array(sorted(only_left | only_right), dtype=np.int64)
    rng.shuffle(pool)
    new_left = common | set(map(int, pool[: len(only_left)]))
    changed = new_left != left
    rows[first] = new_left
    rows[second] = common | set(map(int, pool[len(only_left) :]))
    return changed


def project(rows: list[set[int]], n_terms: int) -> Projection:
    """Project binary incidence and compute mean local unweighted clustering.

    Includes all selected terms, with zero clustering for degree-zero/one
    nodes. Int64 multiplication prevents occurrence-count overflow.
    """
    validate_rows(rows, n_terms)
    doc_ids, term_ids = [], []
    for i, row in enumerate(rows):
        doc_ids.extend([i] * len(row))
        term_ids.extend(sorted(row))
    matrix = csr_matrix((np.ones(len(term_ids), dtype=np.int64), (doc_ids, term_ids)), shape=(len(rows), n_terms))
    weights: NDArray[np.int64] = (matrix.T @ matrix).toarray()
    np.fill_diagonal(weights, 0)
    adjacent = (weights > 0).astype(np.float64)
    degree = adjacent.sum(axis=1)
    triangles_twice = ((adjacent @ adjacent) * adjacent).sum(axis=1)
    denominator = degree * (degree - 1)
    clustering = np.divide(triangles_twice, denominator, out=np.zeros(n_terms), where=denominator > 0)
    return Projection(int(np.count_nonzero(np.triu(weights, 1))), float(clustering.mean()), int(weights.sum() // 2))
