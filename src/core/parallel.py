"""Bounded process-pool helper for embarrassingly parallel per-item maps.

Every call site that uses this module maps a PURE per-item function whose
results merge deterministically in item order (integer counters, per-term
independent scores).  :func:`map_ordered` therefore guarantees the same
result as a serial ``[fn(i) for i in items]`` while spreading the work over
a process pool once the item count justifies the pool startup cost.
"""
from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import Any, Callable, List, Optional, Sequence

# Below this many items, pool startup (spawn + module re-import) dominates
# the per-item work — run serially instead.
MIN_PARALLEL_ITEMS = 64

# Leave headroom for the parent process, OS, and OpenMP threads inside
# workers (sklearn KMeans uses its own OpenMP thread team per call).
DEFAULT_MAX_WORKERS = max(2, min(8, (os.cpu_count() or 4) - 2))


def map_ordered(
    fn: Callable[[Any], Any],
    items: Sequence[Any],
    *,
    min_items: int = MIN_PARALLEL_ITEMS,
    max_workers: Optional[int] = None,
    initializer: Optional[Callable[..., None]] = None,
    initargs: Sequence[Any] = (),
) -> List[Any]:
    """Map ``fn`` over ``items``, parallel when the item count warrants it.

    Args:
        fn: Module-level, picklable per-item function.  Pure per item:
            results must not depend on other items or on call order.
        items: Items to map.
        min_items: Run serially when ``len(items) < min_items``.
        max_workers: Optional worker override (default: bounded CPU count).
        initializer: Optional per-worker pool initializer with ``initargs``
            (per-process singletons, e.g. shared tokenizers).

    Returns:
        Results in ``items`` order — identical to
        ``[fn(item) for item in items]``.

    Falls back to the serial map if pool creation or execution fails, so a
    restricted environment can only cost speed, never correctness.
    """
    if len(items) <= 1:
        return [fn(item) for item in items]
    if len(items) < min_items:
        return [fn(item) for item in items]
    try:
        workers = max_workers or DEFAULT_MAX_WORKERS
        context = get_context("spawn")
        chunksize = max(1, len(items) // (workers * 8))
        with ProcessPoolExecutor(
            max_workers=workers,
            mp_context=context,
            initializer=initializer,
            initargs=initargs,
        ) as pool:
            return list(pool.map(fn, items, chunksize=chunksize))
    except Exception:  # pragma: no cover - restricted-environment fallback
        return [fn(item) for item in items]
