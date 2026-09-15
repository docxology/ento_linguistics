#!/usr/bin/env python3
"""Literature analysis pipeline — Thin Orchestrator.

Delegates the full mining→extraction→mapping→visualization workflow to
``src/pipeline/literature_pipeline.py``.
"""
from __future__ import annotations

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (project_root, os.path.join(project_root, "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from pipeline.literature_pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
