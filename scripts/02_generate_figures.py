#!/usr/bin/env python3
"""Generate comprehensive research figures for the manuscript — Thin Orchestrator.

Sets up paths and delegates all figure-generation, analysis-pipeline, and
data-export logic to ``src/visualization/manuscript_figures.py``.
"""
from __future__ import annotations

import os
import sys

# ── Path setup ────────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
repo_root = os.path.abspath(os.path.join(project_root, ".."))
src_path = os.path.join(project_root, "src")
for p in (project_root, src_path, repo_root):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("MPLBACKEND", "Agg")

from visualization.manuscript_figures import main  # noqa: E402

if __name__ == "__main__":
    main(project_root=project_root)
