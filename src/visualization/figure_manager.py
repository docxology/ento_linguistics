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
            registry_file: Path to figure registry file. Defaults to
                ``<project_root>/output/figures/figure_registry.json`` where
                the project root is derived from this module's location
                (``src/visualization/``), never from the current working
                directory.
        """
        if registry_file is None:
            project_root = Path(__file__).resolve().parents[2]
            registry_file = project_root / "output" / "figures" / "figure_registry.json"

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

        Duplicate labels never silently overwrite a different figure: if the
        label is already taken by another filename, a numeric suffix
        (``_2``, ``_3``, ...) is appended and a warning is logged. Re-registering
        the same filename under the same label updates the entry in place.

        Args:
            filename: Figure filename
            caption: Figure caption
            label: Figure label (auto-generated if None)
            section: Section where figure appears
            generated_by: Script that generated the figure
            **kwargs: Additional parameters

        Returns:
            FigureMetadata object (with the effective, possibly suffixed, label)
        """
        # Generate label if not provided
        if label is None:
            base_name = Path(filename).stem
            label = f"fig:{base_name}"

        # Duplicate-label policy: never silently clobber a different figure
        existing = self.figures.get(label)
        if existing is not None and existing.filename != filename:
            suffix = 2
            base_label = label
            while f"{base_label}_{suffix}" in self.figures:
                suffix += 1
            new_label = f"{base_label}_{suffix}"
            logger.warning(
                f"Duplicate figure label '{label}' for different file "
                f"({filename} vs {existing.filename}); using '{new_label}'"
            )
            label = new_label
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
        """Load figure registry from file, skipping corrupt entries.

        A file-level parse failure starts an empty registry with a warning; a
        single bad entry is skipped with a warning while every well-formed
        entry is preserved.
        """
        if not self.registry_file.exists():
            return
        try:
            with open(self.registry_file, "r") as f:
                data = json.load(f)
        except Exception:
            self.figures = {}
            logger.warning(
                f"Figure registry unreadable ({self.registry_file}); "
                "starting fresh"
            )
            return

        skipped = 0
        for label, fig_data in data.items():
            try:
                self.figures[label] = FigureMetadata(**fig_data)
            except Exception:
                skipped += 1
                logger.warning(
                    f"Skipping corrupt registry entry '{label}': "
                    f"{fig_data!r}"
                )
        if skipped:
            logger.warning(
                f"Skipped {skipped} corrupt registry entries; "
                f"loaded {len(self.figures)} valid figures"
            )
        else:
            logger.debug(f"Loaded {len(self.figures)} figures from registry")

    def _save_registry(self) -> None:
        """Save figure registry to file."""
        data = {label: fig.to_dict() for label, fig in self.figures.items()}
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

