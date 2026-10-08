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
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional

import matplotlib.pyplot as plt
import matplotlib.text

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.text import Annotation
    from matplotlib.transforms import Bbox

__all__ = [
    "MIN_FONT",
    "CANONICAL_DOMAINS",
    "DOMAIN_PALETTE",
    "FALLBACK_COLOR",
    "STYLE_CONFIG",
    "DOMAIN_DISPLAY_NAMES",
    "WORD_FORMATION_LABELS",
    "domain_display_name",
    "ordered_domains",
    "classify_word_formation",
    "place_labels",
    "LABEL_OFFSETS",
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

# Canonical display names (manuscript style) keyed by internal domain key.
DOMAIN_DISPLAY_NAMES: Dict[str, str] = {
    "unit_of_individuality": "Unit of Individuality",
    "behavior_and_identity": "Behavior & Identity",
    "power_and_labor": "Power & Labor",
    "sex_and_reproduction": "Sex & Reproduction",
    "kin_and_relatedness": "Kin & Relatedness",
    "economics": "Economics",
}

_SMALL_WORDS = {"and": "&", "of": "of"}


def domain_display_name(key: str, wrap: bool = False) -> str:
    """Return the canonical display name for a domain key.

    Canonical keys map to the manuscript names ("Behavior & Identity").
    Non-canonical keys fall back to a title-cased form in which ``and``
    becomes ``&`` and ``of`` stays lower-case.

    Args:
        key: Internal domain key (e.g. ``"power_and_labor"``).
        wrap: Insert a newline after ``&`` / ``of`` for narrow tick labels.

    Returns:
        Human-readable domain name.
    """
    name = DOMAIN_DISPLAY_NAMES.get(key)
    if name is None:
        words = [
            _SMALL_WORDS.get(w, w.capitalize()) for w in str(key).split("_") if w
        ]
        name = " ".join(words)
    if wrap:
        name = name.replace(" & ", " &\n").replace(" of ", " of\n")
    return name


def ordered_domains(domains: Iterable[str]) -> List[str]:
    """Order domain keys canonically first, then any extras alphabetically."""
    present = set(domains)
    return [d for d in CANONICAL_DOMAINS if d in present] + sorted(
        d for d in present if d not in CANONICAL_DOMAINS
    )


# One label vocabulary for surface word-formation classes.
WORD_FORMATION_LABELS: List[str] = [
    "Single word",
    "Multiword phrase",
    "Hyphenated compound",
    "Underscore compound",
    "Contains digits",
]


def classify_word_formation(text: str) -> str:
    """Classify a term's surface form into exactly one word-formation class.

    Mutually exclusive, so class counts partition the terms. Precedence:
    digits, underscore compound, hyphenated compound, multiword phrase,
    single word.

    Args:
        text: Term text.

    Returns:
        One of :data:`WORD_FORMATION_LABELS`.
    """
    text = (text or "").strip()
    if any(ch.isdigit() for ch in text):
        return "Contains digits"
    if "_" in text:
        return "Underscore compound"
    if "-" in text:
        return "Hyphenated compound"
    if " " in text:
        return "Multiword phrase"
    return "Single word"


# Single shared domain palette keyed by canonical domain names.
DOMAIN_PALETTE: Dict[str, str] = {
    "unit_of_individuality": "#0072B2",
    "behavior_and_identity": "#E69F00",
    "power_and_labor": "#009E73",
    "sex_and_reproduction": "#D55E00",
    "kin_and_relatedness": "#CC79A7",
    "economics": "#6554A4",
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


#: Candidate label offsets (dx, dy in points, ha, va), tried in order.
LABEL_OFFSETS: List[tuple] = [
    (8, 6, "left", "bottom"), (8, -6, "left", "top"),
    (-8, 6, "right", "bottom"), (-8, -6, "right", "top"),
    (0, 12, "center", "bottom"), (0, -12, "center", "top"),
    (16, 0, "left", "center"), (-16, 0, "right", "center"),
    (22, 16, "left", "bottom"), (-22, 16, "right", "bottom"),
    (22, -16, "left", "top"), (-22, -16, "right", "top"),
]


def place_labels(
    ax: Axes,
    specs: Iterable[tuple[str, tuple[float, float]]],
    offsets: Optional[Iterable[tuple[float, float, str, str]]] = None,
    *,
    avoid_points: Optional[Iterable[tuple[float, float]]] = None,
    avoid_boxes: Optional[Iterable[Bbox]] = None,
    drop_on_fail: bool = False,
    **text_kw: Any,
) -> List[Optional[Annotation]]:
    """Place text labels next to points without overlaps (deterministic).

    For each ``(text, (x, y))`` spec, in priority order, the candidate
    offsets are tried in order and the first whose rendered box overlaps
    no previously placed label, no ``avoid_boxes`` and no ``avoid_points``
    (display-space marker centres, other than the label's own) is kept.
    If none fits, the label is dropped (``drop_on_fail``) or kept at the
    least-colliding candidate.

    Args:
        ax: Target axes (limits must already be final).
        specs: Iterable of ``(text, (x, y))`` in data coordinates.
        offsets: Candidate offsets; defaults to :data:`LABEL_OFFSETS`.
        avoid_points: Optional list of display-space (x, y) marker centres.
        avoid_boxes: Optional list of display-space ``Bbox`` obstacles.
        drop_on_fail: Drop labels that cannot be placed cleanly.
        **text_kw: Passed to ``ax.annotate``.

    Returns:
        List aligned with ``specs`` holding the kept annotation or None.

    Invalid coordinates or annotation options propagate Matplotlib errors.
    Call only after the axes geometry and layout have been finalized.
    """
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    offsets = list(offsets or LABEL_OFFSETS)
    placed = list(avoid_boxes or [])
    points = list(avoid_points or [])
    own_px = ax.transData
    result = []
    for text, xy in specs:
        own = own_px.transform(xy)
        best = None
        best_hits = None
        for dx, dy, ha, va in offsets:
            ann = ax.annotate(
                text, xy, xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, zorder=6, **text_kw,
            )
            ann.update_positions(renderer)
            # Text-only box (Annotation.get_window_extent would include any
            # leader-line arrow patch).
            box = matplotlib.text.Text.get_window_extent(ann, renderer)
            hits = sum(box.overlaps(o) for o in placed)
            axbox = ax.get_window_extent(renderer)
            if box.x0 < axbox.x0 or box.x1 > axbox.x1 or box.y1 > axbox.y1 or box.y0 < axbox.y0:
                hits += 1
            hits += sum(
                1 for (mx, my) in points
                if abs(mx - own[0]) + abs(my - own[1]) > 1.0
                and box.x0 - 4 <= mx <= box.x1 + 4
                and box.y0 - 4 <= my <= box.y1 + 4
            )
            if hits == 0:
                if best is not None:
                    best[0].remove()
                best, best_hits = (ann, box), 0
                break
            if best_hits is None or hits < best_hits:
                if best is not None:
                    best[0].remove()
                best, best_hits = (ann, box), hits
            else:
                ann.remove()
        if best is None:
            result.append(None)
            continue
        if best_hits and drop_on_fail:
            best[0].remove()
            result.append(None)
            continue
        placed.append(best[1])
        result.append(best[0])
    return result


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
