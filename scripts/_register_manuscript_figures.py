#!/usr/bin/env python3
"""Register all generated manuscript figures in the figure registry.

Derives the figure set from the actual PNGs in ``output/figures/`` and merges
metadata (caption, label, section) already recorded in the FigureManager
registry. Files that cannot be registered are skipped with an explicit
logged reason; a missing figures directory is a hard failure.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
repo_root = project_root.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(repo_root))

from visualization.figure_manager import FigureManager  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def register_all_manuscript_figures(figures_dir: Path | None = None) -> int:
    """Register every PNG found in the figures directory.

    Args:
        figures_dir: Figures directory. Defaults to ``project/output/figures``.

    Returns:
        Number of figures registered. Exits non-zero if the directory is
        missing or contains no PNGs.
    """
    logger.info("Registering all generated manuscript figures...")

    figures_dir = figures_dir or project_root / "output" / "figures"
    if not figures_dir.is_dir():
        logger.error(f"Figures directory not found: {figures_dir}")
        logger.error("Run scripts/02_generate_figures.py first.")
        sys.exit(1)

    png_files = sorted(figures_dir.glob("*.png"))
    if not png_files:
        logger.error(f"No PNG figures found in: {figures_dir}")
        logger.error("Run scripts/02_generate_figures.py first.")
        sys.exit(1)

    figure_manager = FigureManager(
        registry_file=str(figures_dir / "figure_registry.json")
    )

    # Reuse metadata already recorded for a filename, if any.
    existing_by_filename = {
        meta.filename: meta for meta in figure_manager.figures.values()
    }

    registered = 0
    skipped = 0
    for png_path in png_files:
        filename = png_path.name
        existing = existing_by_filename.get(filename)
        try:
            figure_manager.register_figure(
                filename=filename,
                caption=(
                    existing.caption
                    if existing and existing.caption
                    else f"Figure {png_path.stem.replace('_', ' ')}"
                ),
                label=existing.label if existing and existing.label else None,
                section=existing.section if existing else None,
                generated_by=(
                    existing.generated_by if existing else "02_generate_figures.py"
                ),
            )
            registered += 1
        except Exception as e:
            skipped += 1
            logger.warning(f"  Skipped {filename}: registration failed ({e})")

    logger.info(f"✅ Registered {registered}/{len(png_files)} figures")
    if skipped:
        logger.warning(f"   Skipped {skipped} figure(s) — see warnings above")
    logger.info(f"   Registry saved to: {figures_dir / 'figure_registry.json'}")
    return registered


def main() -> None:
    """Main entry point."""
    register_all_manuscript_figures()


if __name__ == "__main__":
    main()
