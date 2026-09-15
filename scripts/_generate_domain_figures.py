#!/usr/bin/env python3
"""Domain figure generation — Thin Orchestrator.

Delegates per-domain figure generation to
``src/pipeline/domain_figures.py``.
"""
from __future__ import annotations

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (project_root, os.path.join(project_root, "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from pipeline.domain_figures import main  # noqa: E402

if __name__ == "__main__":
    main()
