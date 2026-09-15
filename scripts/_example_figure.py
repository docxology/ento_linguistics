#!/usr/bin/env python3
"""Example project-specific script for generating figures.

This script demonstrates how to create project-specific scripts that will be
automatically executed by the generic render_pdf.sh system.

The script should:
1. Generate any necessary figures/data
2. Save outputs to the appropriate output directories
3. Print the paths of generated files
4. Fail loudly (no silent fallbacks) when any step cannot complete
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def _setup_paths() -> None:
    """Set up Python paths for src/ and infrastructure modules."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    src_path = os.path.join(project_root, "src")
    repo_root = os.path.dirname(project_root)

    for path in [src_path, project_root, repo_root]:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)


def main() -> None:
    """Generate the example figure and data (self-contained demo)."""
    # Set matplotlib backend for headless operation
    os.environ.setdefault("MPLBACKEND", "Agg")

    # Set up paths dynamically based on execution context
    _setup_paths()

    from core.logging import get_logger

    logger = get_logger(__name__)

    # Self-contained demo computation (no src/ business-logic dependencies).
    logger.info("✅ Running self-contained example computation")

    # Resolve output directories from the project root — no silent fallbacks.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "output")
    data_dir = os.path.join(output_dir, "data")
    figure_dir = os.path.join(output_dir, "figures")

    # Always create output directories before any writes
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(figure_dir, exist_ok=True)

    # Generate and process example data (self-contained demo computation)
    x = np.linspace(0, 10, 100)
    y = (x + 1.0) * 0.5
    y_processed = y * np.sin(x) * np.exp(-x / 5)

    avg_y = float(np.mean(y_processed))
    max_y = float(np.max(y_processed))
    min_y = float(np.min(y_processed))

    logger.info("Data analysis:")
    logger.info(f"  Average: {avg_y:.6f}")
    logger.info(f"  Maximum: {max_y:.6f}")
    logger.info(f"  Minimum: {min_y:.6f}")

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left subplot: Original data
    ax1.plot(x, y, "b-", linewidth=2, label="Processed Data")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_title("Data Processing Demo")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Right subplot: Final result
    ax2.plot(x, y_processed, "r-", linewidth=2, label="Final Result")
    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")
    ax2.set_title("Example Project Figure")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Add statistics as text
    ax2.text(
        0.05,
        0.95,
        f"Avg: {avg_y:.3f}\nMax: {max_y:.3f}\nMin: {min_y:.3f}",
        transform=ax2.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()

    # Save figure
    figure_path = os.path.join(figure_dir, "example_figure.png")
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Register figure with FigureManager for cross-referencing (failures raise).
    from visualization.figure_manager import FigureManager

    fm = FigureManager(registry_file=os.path.join(figure_dir, "figure_registry.json"))
    fm.register_figure(
        filename="example_figure.png",
        caption="Example project figure showing a demo data-processing pipeline",
        label="fig:example_figure",
        section="introduction",
        generated_by="_example_figure.py",
    )
    logger.info("  Registered figure: fig:example_figure")

    # Save data
    data_path = os.path.join(data_dir, "example_data.npz")
    np.savez(
        data_path,
        x=x,
        y=y,
        y_processed=y_processed,
        avg_y=avg_y,
        max_y=max_y,
        min_y=min_y,
    )

    csv_path = os.path.join(data_dir, "example_data.csv")
    with open(csv_path, "w") as f:
        f.write("x,y,y_processed\n")
        for xi, yi, ypi in zip(x, y, y_processed):
            f.write(f"{xi:.6f},{yi:.6f},{ypi:.6f}\n")

    # Print generated paths (this is what the render system captures)
    print(f"Generated: {figure_path}")
    print(f"Generated: {data_path}")
    print(f"Generated: {csv_path}")

    logger.info(f"✅ Generated example figure: {figure_path}")
    logger.info(f"✅ Generated example data: {data_path}")
    logger.info(f"✅ Generated example CSV: {csv_path}")


if __name__ == "__main__":
    main()
