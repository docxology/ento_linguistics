"""Integration tests for the self-contained ``scripts/_example_figure.py``.

The script no longer imports business logic from ``src/example.py``; it runs a
self-contained demo computation and writes its outputs relative to the project
root implied by its own location. These tests exercise the real script in an
isolated sandbox (a copy of the script in a tmp project tree) with the real
project's ``src/`` on ``PYTHONPATH`` — the only project modules the script
imports are ``core.logging`` and ``visualization.figure_manager``.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

SUBPROCESS_TIMEOUT_SECONDS = 1800


def run_subprocess(*args, **kwargs):
    """subprocess.run with a hard timeout; raises pytest.fail.TestFailed on expiry."""
    kwargs.setdefault("timeout", SUBPROCESS_TIMEOUT_SECONDS)
    try:
        return subprocess.run(*args, **kwargs)
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"Subprocess timed out after {SUBPROCESS_TIMEOUT_SECONDS}s: {exc.cmd}")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_SRC = PROJECT_ROOT / "src"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "_example_figure.py"


def _run_in_sandbox(tmp_path: Path, name: str):
    """Copy the script into an isolated sandbox project and run it.

    Returns (sandbox_path, CompletedProcess). The script resolves its output
    directories from its own location, so outputs land in
    ``sandbox/output/{data,figures}``.
    """
    sandbox = tmp_path / name
    (sandbox / "scripts").mkdir(parents=True)
    shutil.copy2(SCRIPT_PATH, sandbox / "scripts" / "_example_figure.py")

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(PROJECT_SRC)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )

    result = run_subprocess([sys.executable, str(sandbox / "scripts" / "_example_figure.py")],
    cwd=str(sandbox),
    capture_output=True,
    text=True,
    env=env,)
    return sandbox, result


class TestExampleFigureScript:
    """Test the example_figure.py script functionality."""

    def test_script_exists_and_executable(self):
        """Test that the example_figure.py script exists."""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "scripts", "_example_figure.py"
        )
        assert os.path.exists(script_path)

    def test_script_has_shebang(self):
        """Test that script has proper Python shebang."""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "scripts", "_example_figure.py"
        )
        with open(script_path, "r") as f:
            first_line = f.readline().strip()
            assert first_line == "#!/usr/bin/env python3"

    def test_setup_paths_adds_project_paths(self):
        """Test _setup_paths adds the project src/, project root, and repo root
        to sys.path so the script's project imports can resolve."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "_example_figure_under_test", str(SCRIPT_PATH)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        original_path = sys.path.copy()
        try:
            module._setup_paths()
            expected = {
                str(PROJECT_SRC),
                str(PROJECT_ROOT),
                str(PROJECT_ROOT.parent),
            }
            assert expected.issubset(set(sys.path))
        finally:
            sys.path[:] = original_path

    def test_main_function_self_contained_computation(self, tmp_path):
        """Test the script runs its self-contained computation (no
        src/example.py dependency) and reports all generated artifacts."""
        sandbox, result = _run_in_sandbox(tmp_path, "self_contained")

        assert result.returncode == 0, (
            f"script failed\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )

        combined_output = result.stdout + result.stderr
        assert "Running self-contained example computation" in combined_output

        # All three artifacts are reported as generated
        assert "✅ Generated example figure" in combined_output
        assert "✅ Generated example data" in combined_output
        assert "✅ Generated example CSV" in combined_output

        # The old src/example.py import messages must be gone
        assert "src/example.py" not in combined_output

        # Output files were created inside the sandbox project
        assert (sandbox / "output" / "figures" / "example_figure.png").exists()
        assert (sandbox / "output" / "data" / "example_data.npz").exists()
        assert (sandbox / "output" / "data" / "example_data.csv").exists()

    def test_main_function_reports_data_statistics(self, tmp_path):
        """Test the self-contained computation reports real summary statistics
        derived from the demo data."""
        _, result = _run_in_sandbox(tmp_path, "statistics")

        assert result.returncode == 0
        # Logging goes to stderr; the statistics live in the combined output
        combined_output = result.stdout + result.stderr
        assert "Data analysis:" in combined_output
        assert "Average:" in combined_output
        assert "Maximum:" in combined_output
        assert "Minimum:" in combined_output

    def test_main_function_creates_proper_output_structure(self, tmp_path):
        """Test that the script creates the expected output directory
        structure, including the figure registry."""
        sandbox, result = _run_in_sandbox(tmp_path, "structure")

        assert result.returncode == 0

        output_dir = sandbox / "output"
        data_dir = output_dir / "data"
        figure_dir = output_dir / "figures"

        assert output_dir.exists()
        assert data_dir.exists()
        assert figure_dir.exists()

        # The script registers the figure with FigureManager
        assert (figure_dir / "figure_registry.json").exists()

    def test_main_function_generates_valid_png(self, tmp_path):
        """Test that generated PNG file is valid."""
        sandbox, result = _run_in_sandbox(tmp_path, "png")

        assert result.returncode == 0

        figure_path = sandbox / "output" / "figures" / "example_figure.png"
        assert figure_path.exists()

        # Check file size is reasonable (not empty)
        assert figure_path.stat().st_size > 1000  # At least 1KB for a real image

        # Verify the PNG magic number and that the IHDR header parses
        with open(figure_path, "rb") as f:
            header = f.read(24)
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        width = int.from_bytes(header[16:20], "big")
        height = int.from_bytes(header[20:24], "big")
        assert width > 0 and height > 0

    def test_main_function_generates_valid_data_files(self, tmp_path):
        """Test that generated data files contain expected, self-consistent
        data."""
        sandbox, result = _run_in_sandbox(tmp_path, "data")

        assert result.returncode == 0

        # Check NPZ file
        npz_path = sandbox / "output" / "data" / "example_data.npz"
        assert npz_path.exists()

        # Load and verify contents
        data = np.load(npz_path)
        assert "x" in data
        assert "y" in data
        assert "y_processed" in data
        assert "avg_y" in data
        assert "max_y" in data
        assert "min_y" in data

        # Check that arrays have expected shapes
        assert len(data["x"]) == 100  # From linspace(0, 10, 100)
        assert len(data["y"]) == 100
        assert len(data["y_processed"]) == 100

        # The reported statistics must be consistent with the stored arrays
        assert np.isclose(float(data["avg_y"]), float(np.mean(data["y_processed"])))
        assert np.isclose(float(data["max_y"]), float(np.max(data["y_processed"])))
        assert np.isclose(float(data["min_y"]), float(np.min(data["y_processed"])))

        # Check CSV file
        csv_path = sandbox / "output" / "data" / "example_data.csv"
        assert csv_path.exists()

        # Read and verify CSV structure and consistency with the NPZ data
        with open(csv_path, "r") as f:
            lines = f.readlines()
            assert lines[0].strip() == "x,y,y_processed"
            assert len(lines) == 101  # Header + 100 data points

        first_x, first_y, first_yp = data["x"][0], data["y"][0], data["y_processed"][0]
        expected_row = f"{first_x:.6f},{first_y:.6f},{first_yp:.6f}\n"
        assert lines[1] == expected_row

    def test_main_function_deterministic_output(self, tmp_path):
        """Test that running the script multiple times produces identical
        results."""
        sandbox, result1 = _run_in_sandbox(tmp_path, "deterministic")

        assert result1.returncode == 0

        # Preserve first-run artifacts before the second run overwrites them
        csv_path = sandbox / "output" / "data" / "example_data.csv"
        npz_path = sandbox / "output" / "data" / "example_data.npz"
        csv_bytes_1 = csv_path.read_bytes()
        data1 = {k: np.load(npz_path)[k] for k in ("x", "y", "y_processed")}

        result2 = run_subprocess([sys.executable, str(sandbox / "scripts" / "_example_figure.py")],
        cwd=str(sandbox),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_SRC)},)
        assert result2.returncode == 0

        # CSV output must be byte-for-byte identical across runs
        assert csv_path.read_bytes() == csv_bytes_1

        # NPZ arrays must be exactly equal
        data2 = np.load(npz_path)
        np.testing.assert_array_equal(data1["x"], data2["x"])
        np.testing.assert_array_equal(data1["y"], data2["y"])
        np.testing.assert_array_equal(data1["y_processed"], data2["y_processed"])

    def test_main_function_error_handling(self, tmp_path):
        """Test the script fails loudly when its output directories cannot be
        created (no silent fallbacks)."""
        sandbox = tmp_path / "errors"
        (sandbox / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT_PATH, sandbox / "scripts" / "_example_figure.py")

        # Make output/ unwritable so os.makedirs(output/data) must fail
        output_dir = sandbox / "output"
        output_dir.mkdir(mode=0o555)
        try:
            result = run_subprocess([sys.executable, str(sandbox / "scripts" / "_example_figure.py")],
            cwd=str(sandbox),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(PROJECT_SRC)},)
            assert result.returncode != 0
            assert "PermissionError" in result.stderr
        finally:
            os.chmod(output_dir, 0o755)

    def test_main_function_matplotlib_backend_setting(self, tmp_path):
        """Test the script runs headless by defaulting MPLBACKEND to Agg."""
        env = os.environ.copy()
        env.pop("MPLBACKEND", None)  # exercise the script's own default
        env["PYTHONPATH"] = str(PROJECT_SRC)

        sandbox = tmp_path / "backend"
        (sandbox / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT_PATH, sandbox / "scripts" / "_example_figure.py")

        result = run_subprocess([sys.executable, str(sandbox / "scripts" / "_example_figure.py")],
        cwd=str(sandbox),
        capture_output=True,
        text=True,
        env=env,)

        # Headless run must succeed and produce the figure
        assert result.returncode == 0
        assert (sandbox / "output" / "figures" / "example_figure.png").exists()


if __name__ == "__main__":
    pytest.main([__file__])
