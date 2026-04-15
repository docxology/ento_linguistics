"""Tests for src/utils/figure_manager.py to improve coverage."""

import json
import tempfile
from pathlib import Path

import pytest
from visualization.figure_manager import FigureManager, FigureMetadata


class TestFigureMetadata:
    """Test FigureMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating figure metadata."""
        metadata = FigureMetadata(
            filename="test.png",
            caption="Test figure",
            label="fig:test",
            section="Introduction",
        )
        assert metadata.filename == "test.png"
        assert metadata.caption == "Test figure"
        assert metadata.label == "fig:test"
        assert metadata.section == "Introduction"

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        fig_meta = FigureMetadata(
            filename="test.png",
            caption="Test",
            label="fig:test",
            metadata={"param1": "value1"},
        )
        data = fig_meta.to_dict()
        assert data["filename"] == "test.png"
        assert data["caption"] == "Test"
        assert data["label"] == "fig:test"
        assert data["metadata"] == {"param1": "value1"}


class TestFigureManager:
    """Test FigureManager class."""

    def test_manager_initialization_default(self, tmp_path):
        """Test initializing manager with default registry path structure."""
        # Use a temporary registry file to ensure isolation from existing data
        registry_file = tmp_path / "test_registry.json"
        manager = FigureManager(str(registry_file))
        assert manager.registry_file == registry_file
        assert len(manager.figures) == 0

    def test_manager_initialization_custom(self, tmp_path):
        """Test initializing manager with custom registry path."""
        registry_file = tmp_path / "custom_registry.json"
        manager = FigureManager(str(registry_file))
        assert manager.registry_file == registry_file
        assert len(manager.figures) == 0

    def test_register_figure_with_label(self, tmp_path):
        """Test registering a figure with explicit label."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        metadata = manager.register_figure(
            filename="test.png",
            caption="Test figure",
            label="fig:test",
            section="Introduction",
        )

        assert metadata.label == "fig:test"
        assert metadata.filename == "test.png"
        assert "fig:test" in manager.figures

    def test_register_figure_auto_label(self, tmp_path):
        """Test registering a figure with auto-generated label."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        metadata = manager.register_figure(
            filename="my_figure.png", caption="My figure"
        )

        assert metadata.label == "fig:my_figure"
        assert metadata.filename == "my_figure.png"
        assert "fig:my_figure" in manager.figures

    def test_register_figure_with_metadata(self, tmp_path):
        """Test registering a figure with additional metadata."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        fig_meta = manager.register_figure(
            filename="test.png", caption="Test", param1="value1", param2=42
        )

        assert fig_meta.metadata == {"param1": "value1", "param2": 42}

    def test_get_figure_existing(self, tmp_path):
        """Test getting an existing figure."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        manager.register_figure(filename="test.png", caption="Test", label="fig:test")

        metadata = manager.get_figure("fig:test")
        assert metadata is not None
        assert metadata.filename == "test.png"

    def test_get_figure_nonexistent(self, tmp_path):
        """Test getting a non-existent figure."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        metadata = manager.get_figure("fig:nonexistent")
        assert metadata is None

    def test_load_registry_existing(self, tmp_path):
        """Test loading existing registry file."""
        registry_file = tmp_path / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        # Create registry file
        registry_data = {
            "fig:test": {
                "filename": "test.png",
                "caption": "Test figure",
                "label": "fig:test",
            }
        }
        registry_file.write_text(json.dumps(registry_data))

        manager = FigureManager(str(registry_file))
        assert "fig:test" in manager.figures
        assert manager.figures["fig:test"].filename == "test.png"

    def test_load_registry_corrupted(self, tmp_path):
        """Test loading corrupted registry file."""
        registry_file = tmp_path / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        # Create corrupted registry file
        registry_file.write_text("invalid json content {")

        manager = FigureManager(str(registry_file))
        # Should start fresh with empty registry
        assert len(manager.figures) == 0

    def test_save_registry(self, tmp_path):
        """Test saving registry to file."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        manager.register_figure(filename="test.png", caption="Test", label="fig:test")

        # Verify file was created and contains data
        assert registry_file.exists()
        data = json.loads(registry_file.read_text())
        assert "fig:test" in data
        assert data["fig:test"]["filename"] == "test.png"

    def test_list_figures(self, tmp_path):
        """Test listing all registered figures."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))

        manager.register_figure(filename="b.png", caption="B", label="fig:b")
        manager.register_figure(filename="a.png", caption="A", label="fig:a")

        figures = manager.list_figures()
        assert len(figures) == 2
        # Should be sorted by label
        assert figures[0] == ("fig:a", "a.png")
        assert figures[1] == ("fig:b", "b.png")

    def test_validate_registry_all_valid(self, tmp_path):
        """Test validate_registry when all registered figures exist on disk."""
        figure_dir = tmp_path / "figures"
        figure_dir.mkdir()
        registry_file = figure_dir / "figure_registry.json"

        manager = FigureManager(str(registry_file))
        # Create actual figure files
        (figure_dir / "fig1.png").write_bytes(b"\x89PNG")
        (figure_dir / "fig2.png").write_bytes(b"\x89PNG")

        manager.register_figure(filename="fig1.png", caption="Figure 1", label="fig:1")
        manager.register_figure(filename="fig2.png", caption="Figure 2", label="fig:2")

        results = manager.validate_registry(figure_dir)
        assert len(results["valid"]) == 2
        assert len(results["missing"]) == 0
        assert len(results["orphaned"]) == 0

    def test_validate_registry_missing_files(self, tmp_path):
        """Test validate_registry when registered figures are missing from disk."""
        figure_dir = tmp_path / "figures"
        figure_dir.mkdir()
        registry_file = figure_dir / "figure_registry.json"

        manager = FigureManager(str(registry_file))
        # Register a figure but don't create the file
        manager.register_figure(filename="missing.png", caption="Missing", label="fig:miss")

        results = manager.validate_registry(figure_dir)
        assert len(results["valid"]) == 0
        assert "missing.png" in results["missing"]

    def test_validate_registry_orphaned_files(self, tmp_path):
        """Test validate_registry detects unregistered image files."""
        figure_dir = tmp_path / "figures"
        figure_dir.mkdir()
        registry_file = figure_dir / "figure_registry.json"

        manager = FigureManager(str(registry_file))
        # Create a figure file but don't register it
        (figure_dir / "orphan.png").write_bytes(b"\x89PNG")

        results = manager.validate_registry(figure_dir)
        assert "orphan.png" in results["orphaned"]

    def test_validate_registry_default_dir(self, tmp_path):
        """Test validate_registry with default figure_dir (None)."""
        figure_dir = tmp_path / "figures"
        figure_dir.mkdir()
        registry_file = figure_dir / "figure_registry.json"

        manager = FigureManager(str(registry_file))
        (figure_dir / "fig.png").write_bytes(b"\x89PNG")
        manager.register_figure(filename="fig.png", caption="Fig", label="fig:f")

        # Use default directory (parent of registry file)
        results = manager.validate_registry()
        assert len(results["valid"]) == 1

    def test_save_reload_roundtrip(self, tmp_path):
        """Test that figures survive save-and-reload cycle."""
        registry_file = tmp_path / "registry.json"
        manager1 = FigureManager(str(registry_file))
        manager1.register_figure(
            filename="fig.png", caption="Cap", label="fig:rt",
            section="Intro", generated_by="test_script.py",
        )

        # Create a new manager that loads from the same file
        manager2 = FigureManager(str(registry_file))
        assert "fig:rt" in manager2.figures
        fig = manager2.figures["fig:rt"]
        assert fig.filename == "fig.png"
        assert fig.section == "Intro"
        assert fig.generated_by == "test_script.py"

    def test_register_figure_generated_by(self, tmp_path):
        """Test the generated_by field is stored correctly."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))
        meta = manager.register_figure(
            filename="fig.png", caption="X", generated_by="02_generate_figures.py",
        )
        assert meta.generated_by == "02_generate_figures.py"

    def test_clear_registry(self, tmp_path):
        """Test clearing the registry empties all figures."""
        registry_file = tmp_path / "registry.json"
        manager = FigureManager(str(registry_file))
        manager.register_figure(filename="a.png", caption="A", label="fig:a")
        manager.register_figure(filename="b.png", caption="B", label="fig:b")
        assert len(manager.figures) == 2

        manager.clear_registry()
        assert len(manager.figures) == 0

        # Verify persistence: reload from disk should also be empty
        manager2 = FigureManager(str(registry_file))
        assert len(manager2.figures) == 0


