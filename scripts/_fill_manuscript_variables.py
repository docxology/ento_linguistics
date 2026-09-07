#!/usr/bin/env python3
"""Fill manuscript template variables from pipeline JSON outputs — Thin Orchestrator.

Delegates variable-map building and ``{{VAR}}`` substitution to
``src/core/manuscript_variables.py``.
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

from core.manuscript_variables import main  # noqa: E402

if __name__ == "__main__":
    main()
