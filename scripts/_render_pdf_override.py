#!/usr/bin/env python3
"""Build the Ento-Linguistics PDF manuscript — Thin Orchestrator.

Delegates the Pandoc/XeLaTeX build pipeline, TeX post-processing,
frontmatter/title-page emission, and ``{{KEY}}`` corpus-variable
substitution to ``src/pipeline/rendering.py``.
"""
from __future__ import annotations

import argparse
import os
import sys

# ── Path setup ────────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
repo_root = os.path.abspath(os.path.join(project_root, ".."))
src_path = os.path.join(project_root, "src")
for p in (project_root, src_path, repo_root):
    if p not in sys.path:
        sys.path.insert(0, p)

from pipeline.rendering import build_pdf  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build Ento-Linguistics PDF with optional strict template checks.",
    )
    parser.add_argument(
        "--strict-templates",
        action="store_true",
        help="Exit with code 1 if any {{VAR}} placeholder remains after substitution "
        "(also enabled by STRICT_TEMPLATE_VARS=1).",
    )
    args = parser.parse_args()
    build_pdf(strict_templates=args.strict_templates)
