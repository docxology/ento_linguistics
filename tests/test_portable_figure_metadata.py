"""Check the portable registry's separation of visible captions and alt text."""

from pathlib import Path
from runpy import run_path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREPARE = run_path(str(ROOT / "scripts/_prepare_template_manuscript.py"))


@pytest.mark.parametrize(
    ("label", "caption", "expected_topic"),
    [
        (
            "fig:terminology_network",
            r"Visual edge weights (Eq.~\ref{eq:network_edge_weight}).",
            "co-occurrence",
        ),
        (
            "fig:domain_overlap",
            r"Overlap (Eq.~\ref{eq:overlap_coefficient}).",
            "Heatmap",
        ),
        (
            "fig:domain_patterns_grid",
            r"Same classifier as Figure \ref{fig:unit_individuality_patterns}.",
            "single words",
        ),
        (
            "fig:concept_hierarchy",
            r"Weighted degree (Eq.~\ref{eq:overlap_coefficient}).",
            "summed vocabulary overlap",
        ),
    ],
)
def test_cross_referenced_caption_has_independent_alt(label, caption, expected_topic):
    record = PREPARE["portable_figure_record"]("figure.png", label, caption, "abc")
    assert record["caption"] == caption
    assert expected_topic in record["alt_text"]
    assert "\\" not in record["alt_text"]
    assert record["metadata"] == {"sha256": "abc"}


def test_plain_caption_remains_the_default_alt():
    caption = "Counts by category."
    record = PREPARE["portable_figure_record"]("figure.png", "fig:counts", caption, "def")
    assert record["alt_text"] == caption
