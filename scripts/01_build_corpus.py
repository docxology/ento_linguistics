#!/usr/bin/env python3
"""Build a domain-appropriate entomological corpus — Thin Orchestrator.

Delegates PubMed retrieval, deduplication, corpus validation, and persistence
to ``src/pipeline/corpus_build.py``.
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

from pipeline.corpus_build import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(project_root=project_root))
