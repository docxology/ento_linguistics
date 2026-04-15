"""Minimal markdown and image integration utilities."""

from pathlib import Path
from typing import Dict, List, Optional

__all__ = [
    "MarkdownIntegration",
    "ImageManager",
]


class MarkdownIntegration:
    """Lightweight markdown integration for manuscript section management."""

    def __init__(self, manuscript_dir: Path):
        """Initialize with manuscript directory."""
        self.manuscript_dir = manuscript_dir

    def detect_sections(self, markdown_file: Path) -> List[str]:
        """Detect sections in markdown file.

        Returns:
            List of section headings found in the file.
        """
        return []

    def insert_figure_in_section(
        self,
        markdown_file: Path,
        figure_label: str,
        section_name: str,
        position: str = "after",
    ) -> bool:
        """Insert figure in specific section.

        Args:
            markdown_file: Path to markdown file
            figure_label: Figure label
            section_name: Section name
            position: Position relative to section (before, after)

        Returns:
            True if successful
        """
        # Minimal implementation — figure insertion requires infrastructure.documentation
        return False


class ImageManager:
    """Lightweight image registry for figure management."""

    def __init__(self):
        """Initialize image manager."""
        self.images = {}

    def register_image(
        self, filename: str, caption: str, alt_text: Optional[str] = None
    ) -> None:
        """Register an image with caption and alt text."""
        self.images[filename] = {"caption": caption, "alt_text": alt_text}

    def get_image_info(self, filename: str) -> Optional[Dict]:
        """Get image information by filename."""
        return self.images.get(filename)
