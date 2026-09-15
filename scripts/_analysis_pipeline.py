#!/usr/bin/env python3
"""Ento-Linguistic analysis pipeline orchestrator — Thin Orchestrator.

Runs the active pipeline stages in order: corpus build (``01_build_corpus.py``)
→ figure generation (``02_generate_figures.py``) → manuscript preflight
(``_manuscript_preflight.py``). Each stage is a real script in this directory;
this module only sequences them and reports results.
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("analysis_pipeline")

# Ordered stage definitions: name -> (script, description)
STAGES: list[tuple[str, Path, str]] = [
    (
        "corpus",
        project_root / "scripts" / "01_build_corpus.py",
        "Build/refresh the literature corpus (data/corpus/abstracts.json)",
    ),
    (
        "figures",
        project_root / "scripts" / "02_generate_figures.py",
        "Regenerate all manuscript figures and analysis data (clean slate)",
    ),
    (
        "preflight",
        project_root / "scripts" / "_manuscript_preflight.py",
        "Validate manuscript figure refs, glossary, and references",
    ),
]


def run_stage(
    stage_name: str, script: Path, dry_run: bool = False
) -> bool:
    """Run a single pipeline stage.

    Args:
        stage_name: Logical stage name (for logging).
        script: Path to the stage script to execute.
        dry_run: If True, only log what would be executed.

    Returns:
        True if the stage completed successfully (or is a dry run).
    """
    command = [sys.executable, str(script)]
    if dry_run:
        logger.info(f"[DRY RUN] Would execute: {' '.join(command)}")
        return True

    logger.info(f"── Stage: {stage_name} ──")
    result = subprocess.run(command, cwd=str(project_root))
    if result.returncode == 0:
        logger.info(f"✅ {stage_name} completed successfully")
        return True
    logger.error(f"❌ {stage_name} failed with exit code {result.returncode}")
    return False


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the Ento-Linguistic analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Run the Ento-Linguistic analysis pipeline "
        "(corpus -> figures -> preflight)."
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=[name for name, _, _ in STAGES] + ["all"],
        default=["all"],
        help="Stages to run, in canonical order (default: all).",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show stages without executing them."
    )
    parser.add_argument(
        "--list-stages", action="store_true", help="List available stages and exit."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point: run selected stages in canonical order."""
    args = _parse_args(argv)

    if args.list_stages:
        logger.info("Available analysis stages:")
        for i, (name, _, description) in enumerate(STAGES, 1):
            logger.info(f"  {i}. {name}: {description}")
        return 0

    if "all" in args.stages:
        stages_to_run = STAGES
    else:
        selected = set(args.stages)
        stages_to_run = [s for s in STAGES if s[0] in selected]

    logger.info("Ento-Linguistic Analysis Pipeline starting")
    logger.info(f"Stages to run: {', '.join(s[0] for s in stages_to_run)}")

    failed = []
    for stage_name, script, _ in stages_to_run:
        if not run_stage(stage_name, script, dry_run=args.dry_run):
            failed.append(stage_name)

    if args.dry_run:
        logger.info(f"Dry run complete — would execute {len(stages_to_run)} stage(s)")
        return 0

    if failed:
        logger.error(f"❌ {len(failed)} stage(s) failed: {', '.join(failed)}")
        return 1
    logger.info("🎉 All stages completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
