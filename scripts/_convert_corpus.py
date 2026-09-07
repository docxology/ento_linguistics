#!/usr/bin/env python3
"""Convert literature corpus JSON into a plain abstracts list — Thin Orchestrator.

Delegates conversion logic to ``src/data/loader.py`` (``convert_corpus``).
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

from data.loader import convert_corpus  # noqa: E402

if __name__ == "__main__":
    convert_corpus()
