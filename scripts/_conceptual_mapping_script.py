#!/usr/bin/env python3
"""Conceptual mapping — Thin Orchestrator.

Delegates concept-map and terminology-network generation to
``src/pipeline/conceptual_mapping_pipeline.py``.
"""
from __future__ import annotations

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (project_root, os.path.join(project_root, "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from pipeline.conceptual_mapping_pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
