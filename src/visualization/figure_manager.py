"""Minimal figure management utilities for the Ento-Linguistic Research Project.

This module provides basic figure registration functionality with validation
and logging for tracking generated figures across the pipeline.
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

__all__ = [
    "FigureMetadata",
    "FigureManager",
]


@dataclass
class FigureMetadata:
    """Metadata for a registered figure."""

    filename: str
    caption: str
    label: Optional[str] = None
    section: Optional[str] = None
    generated_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class FigureManager:
    """Minimal figure manager for registering figures.

    Provides registration, retrieval, listing, and validation of
    generated figures with on-disk integrity checks.
    """

    def __init__(self, registry_file: Optional[str] = None):
        """Initialize figure manager.

        Args:
            registry_file: Path to figure registry file
        """
        if registry_file is None:
            registry_file = "output/figures/figure_registry.json"

        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.figures: Dict[str, FigureMetadata] = {}
        self._load_registry()

    def register_figure(
        self,
        filename: str,
        caption: str,
        label: Optional[str] = None,
        section: Optional[str] = None,
        generated_by: Optional[str] = None,
        **kwargs,
    ) -> FigureMetadata:
        """Register a figure.

        Args:
            filename: Figure filename
            caption: Figure caption
            label: Figure label (auto-generated if None)
            section: Section where figure appears
            generated_by: Script that generated the figure
            **kwargs: Additional parameters

        Returns:
            FigureMetadata object
        """
        # Generate label if not provided
        if label is None:
            base_name = Path(filename).stem
            label = f"fig:{base_name}"

        # Create metadata
        metadata = FigureMetadata(
            filename=filename,
            caption=caption,
            label=label,
            section=section,
            generated_by=generated_by,
            metadata=kwargs if kwargs else None,
        )

        # Register
        self.figures[label] = metadata
        self._save_registry()
        logger.info(f"Registered figure: {label} -> {filename}")

        return metadata

    def clear_registry(self) -> None:
        """Clear all registered figures (for clean-slate pipeline runs).

        Removes all in-memory figure entries and persists the empty
        registry to disk.
        """
        self.figures.clear()
        self._save_registry()
        logger.info("Figure registry cleared")

    def get_figure(self, label: str) -> Optional[FigureMetadata]:
        """Get figure metadata by label.

        Args:
            label: Figure label

        Returns:
            FigureMetadata if found, None otherwise
        """
        return self.figures.get(label)

    def list_figures(self) -> List[Tuple[str, str]]:
        """List all registered figures.

        Returns:
            List of (label, filename) tuples sorted by label
        """
        return sorted(
            [(label, fig.filename) for label, fig in self.figures.items()]
        )

    def validate_registry(
        self, figure_dir: Optional[Path] = None,
    ) -> Dict[str, List[str]]:
        """Validate that all registered figures exist on disk.

        Args:
            figure_dir: Directory containing figure files. If None,
                uses the parent directory of the registry file.

        Returns:
            Dictionary with 'valid', 'missing', and 'orphaned' keys,
            each mapping to a list of filenames.
        """
        if figure_dir is None:
            figure_dir = self.registry_file.parent

        figure_dir = Path(figure_dir)
        results: Dict[str, List[str]] = {
            "valid": [],
            "missing": [],
            "orphaned": [],
        }

        # Check registered figures exist on disk
        for label, fig in self.figures.items():
            filepath = figure_dir / fig.filename
            if filepath.exists():
                results["valid"].append(fig.filename)
            else:
                results["missing"].append(fig.filename)
                logger.warning(f"Registered figure missing on disk: {fig.filename}")

        # Check for unregistered files in the directory
        registered_filenames = {fig.filename for fig in self.figures.values()}
        if figure_dir.exists():
            for path in figure_dir.iterdir():
                if path.suffix.lower() in {".png", ".pdf", ".svg", ".eps"}:
                    if path.name not in registered_filenames:
                        results["orphaned"].append(path.name)

        logger.info(
            f"Registry validation: {len(results['valid'])} valid, "
            f"{len(results['missing'])} missing, "
            f"{len(results['orphaned'])} orphaned"
        )
        return results

    def _load_registry(self) -> None:
        """Load figure registry from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    for label, fig_data in data.items():
                        self.figures[label] = FigureMetadata(**fig_data)
                logger.debug(f"Loaded {len(self.figures)} figures from registry")
            except Exception:
                # Start fresh if registry is corrupted
                self.figures = {}
                logger.warning("Figure registry corrupted, starting fresh")

    def _save_registry(self) -> None:
        """Save figure registry to file."""
        data = {label: fig.to_dict() for label, fig in self.figures.items()}
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

