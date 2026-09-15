"""Shared publication style for the visualization sub-package.

Single source of truth for:

- the canonical six Ento-Linguistic domains and their colour palette,
- the 16 pt minimum font floor enforced on every figure path,
- deterministic primary-domain selection,
- scoped rcParams styling (no global ``rcParams`` mutation).

Every figure-producing module applies these settings through
:func:`publication_style` (decorator) or :func:`publication_rc` (context
manager), so the font floor is genuinely enforced rather than merely claimed.
"""

from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path

import functools
from typing import Any, Dict, Iterable, List, Optional

import matplotlib.pyplot as plt

__all__ = [
    "MIN_FONT",
    "CANONICAL_DOMAINS",
    "DOMAIN_PALETTE",
    "FALLBACK_COLOR",
    "STYLE_CONFIG",
    "publication_style",
    "save_and_verify",
]

# Publication-quality minimum font size in points (template standard).
# Every text element in every figure path must be >= this floor.
MIN_FONT: float = 16.0

# The six canonical Ento-Linguistic domains, in manuscript display order.
CANONICAL_DOMAINS: List[str] = [
    "unit_of_individuality",
    "behavior_and_identity",
    "power_and_labor",
    "sex_and_reproduction",
    "kin_and_relatedness",
    "economics",
]

# Single shared domain palette keyed by canonical domain names.
DOMAIN_PALETTE: Dict[str, str] = {
    "unit_of_individuality": "#1f77b4",  # Blue
    "behavior_and_identity": "#ff7f0e",  # Orange
    "power_and_labor": "#2ca02c",  # Green
    "sex_and_reproduction": "#d62728",  # Red
    "kin_and_relatedness": "#9467bd",  # Purple
    "economics": "#8c564b",  # Brown
}

# Neutral colour for nodes whose domains are missing or non-canonical.
FALLBACK_COLOR: str = "#7f7f7f"

# Publication style applied to every figure path. All font sizes >= MIN_FONT.
STYLE_CONFIG: Dict[str, Any] = {
    "font.size": MIN_FONT,
    "axes.labelsize": MIN_FONT,
    "axes.titlesize": MIN_FONT + 2,
    "figure.titlesize": MIN_FONT + 4,
    "xtick.labelsize": MIN_FONT,
    "ytick.labelsize": MIN_FONT,
    "legend.fontsize": MIN_FONT,
    "savefig.dpi": 300,
}


def primary_domain(domains: Optional[Iterable[str]]) -> Optional[str]:
    """Deterministically pick the primary domain from a membership iterable.

    Selection is ``sorted(domains)[0]``, so the result is independent of set
    iteration order (``PYTHONHASHSEED``) and of insertion order.

    Args:
        domains: Domain membership iterable (set or list); may be None/empty.

    Returns:
        Lexicographically smallest domain, or None when empty or None.
    """
    if not domains:
        return None
    return sorted(domains)[0]


@contextmanager
def publication_rc(extra: Optional[Dict[str, Any]] = None):
    """Apply the shared publication style as a scoped ``rc_context`` block.

    Args:
        extra: Optional additional rcParams merged on top of STYLE_CONFIG.
    """
    config = dict(STYLE_CONFIG)
    if extra:
        config.update(extra)
    with plt.rc_context(config):
        yield


def publication_style(func):
    """Decorate a figure-producing function to run inside a scoped ``rc_context``.

    The wrapped function sees the publication style (16 pt font floor) without
    any global ``rcParams`` mutation: settings are restored on exit, including
    on exception.

    Args:
        func: Figure-producing function.

    Returns:
        Wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with plt.rc_context(STYLE_CONFIG):
            return func(*args, **kwargs)

    return wrapper


def save_and_verify(fig: "plt.Figure", filepath, dpi: int = 300) -> int:
    """Save *fig* to *filepath* and verify the write landed.

    Shared save-and-verify pattern: the file must exist and be non-empty
    after ``savefig``, otherwise a :class:`RuntimeError` is raised so a
    silently corrupt figure never propagates downstream.

    Args:
        fig: Matplotlib figure to save.
        filepath: Destination path (``str`` or ``Path``).
        dpi: Resolution for raster output.

    Returns:
        Size of the written file in bytes.

    Raises:
        RuntimeError: If the file is missing or empty after saving.
    """
    path = Path(filepath)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    size = path.stat().st_size if path.exists() else 0
    if size == 0:
        raise RuntimeError(f"Figure save failed for {path}")
    return size
