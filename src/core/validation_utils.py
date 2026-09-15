"""Validation utilities - thin wrapper around infrastructure validation."""

from __future__ import annotations

import importlib.util
import json

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .logging import get_logger

__all__ = [
    "validate_markdown",
    "validate_figure_registry",
    "verify_output_integrity",
    "validate_pdf_rendering",
    "IntegrityReport",
]

_logger = get_logger(__name__)


def _repo_root() -> Path:
    """Return the repository root, derived from this file's location.

    Walks up from ``validation_utils.py``:
    core/ -> src/ -> ento_linguistics/ -> projects/ -> template/

    Returns:
        Path to the repository root
    """
    return Path(__file__).resolve().parent.parent.parent.parent.parent


# Lazy imports to avoid import issues during test collection
def _get_infra_validate_markdown():
    # Ensure infrastructure is available
    _ensure_infrastructure_path()
    from infrastructure.validation.content.markdown_validator import validate_markdown

    return validate_markdown


def _get_infra_verify_output_integrity():
    # Ensure infrastructure is available
    _ensure_infrastructure_path()
    from infrastructure.validation.integrity import verify_output_integrity

    return verify_output_integrity


def _get_infra_validate_pdf_rendering():
    # Ensure infrastructure is available
    _ensure_infrastructure_path()
    from infrastructure.core.exceptions import PDFValidationError
    from infrastructure.validation.content.pdf_validator import validate_pdf_rendering

    return validate_pdf_rendering, PDFValidationError


def _get_infra_validate_figure_registry():
    # Ensure infrastructure is available
    _ensure_infrastructure_path()
    from infrastructure.validation.content.figure_validator import (
        validate_figure_registry,
    )

    return validate_figure_registry


def _ensure_infrastructure_path():
    """Ensure the infrastructure module is available in sys.path."""
    import sys

    # Check if infrastructure is already available
    if importlib.util.find_spec("infrastructure") is not None:
        return

    repo_root = str(_repo_root())
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def validate_markdown(markdown_path: str, strict: bool = False) -> Dict[str, Any]:
    """Validate markdown files using infrastructure validation.

    Args:
        markdown_path: Path to markdown files
        strict: Whether to use strict validation

    Returns:
        Validation results dictionary with "status", "issues" (list of
        serialized problem dictionaries), "summary", and "path"
    """
    try:
        infra_validate_markdown = _get_infra_validate_markdown()
    except ImportError as e:
        return {"status": "error", "error": str(e), "path": markdown_path}

    try:
        # Infrastructure function requires both markdown_dir and repo_root
        problems, exit_code = infra_validate_markdown(
            Path(markdown_path), _repo_root(), strict=strict
        )
        # The infrastructure reports DiagnosticEvent objects; serialize them
        # so this wrapper's result stays a plain, JSON-serializable dictionary.
        issues = [event.to_dict() for event in problems]
        return {
            "status": "validated" if exit_code == 0 else "issues_found",
            "issues": issues,
            "summary": {"total_issues": len(issues), "exit_code": exit_code},
            "path": markdown_path,
        }
    except (OSError, ValueError) as e:
        # Expected: missing/unreadable paths, malformed content
        return {"status": "error", "error": str(e), "path": markdown_path}
    except Exception:
        _logger.exception(
            "Unexpected error in validate_markdown for %s", markdown_path
        )
        raise


def _registry_input_error(registry_path: Path) -> Optional[str]:
    """Return an error message when the registry input is missing or corrupt.

    The infrastructure loader converts unreadable or malformed registries into
    a failed result instead of raising; probing the input here lets genuine
    input failures surface as an "error" status instead of "issues_found".

    Args:
        registry_path: Path to figure registry JSON file

    Returns:
        Human-readable error message, or None when the input is readable
    """
    if not registry_path.is_file():
        return f"Figure registry not found: {registry_path}"
    try:
        with open(registry_path, encoding="utf-8") as f:
            json.load(f)
    except (OSError, ValueError) as e:
        return f"Failed to load figure registry: {e}"
    return None



def validate_figure_registry(
    registry_path: Path, manuscript_dir: Path
) -> Dict[str, Any]:
    """Validate figure registry using infrastructure validation.

    Args:
        registry_path: Path to figure registry JSON file
        manuscript_dir: Path to manuscript directory containing markdown files

    Returns:
        Validation results dictionary with status, issues, and summary
    """
    try:
        infra_validate_figure_registry = _get_infra_validate_figure_registry()
    except ImportError as e:
        return {"status": "error", "error": str(e), "success": False, "issues": []}

    registry_path = Path(registry_path)
    input_error = _registry_input_error(registry_path)
    if input_error is not None:
        return {
            "status": "error",
            "error": input_error,
            "success": False,
            "issues": [],
        }

    try:
        success, issues = infra_validate_figure_registry(registry_path, manuscript_dir)
    except (OSError, ValueError) as e:
        # Expected: missing registry/manuscript paths, malformed registry JSON
        return {
            "status": "error",
            "error": str(e),
            "success": False,
            "issues": [],
        }
    except Exception:
        _logger.exception(
            "Unexpected error in validate_figure_registry for %s", registry_path
        )
        raise

    return {
        "status": "validated" if success else "issues_found",
        "success": success,
        "issues": issues,
        "summary": {"total_issues": len(issues), "validated": success},
    }


def verify_output_integrity(output_path: Path) -> Dict[str, Any]:
    """Verify output integrity using infrastructure validation.

    Args:
        output_path: Path to output directory

    Returns:
        Integrity report
    """
    try:
        infra_verify_output_integrity = _get_infra_verify_output_integrity()
    except ImportError as e:
        return {"status": "error", "error": str(e), "path": str(output_path)}

    try:
        report = infra_verify_output_integrity(output_path)
    except (OSError, TypeError, ValueError) as e:
        # Expected: unreadable output paths, malformed report payloads
        return {"status": "error", "error": str(e), "path": str(output_path)}
    except Exception:
        _logger.exception(
            "Unexpected error in verify_output_integrity for %s", output_path
        )
        raise

    # The infrastructure returns an IntegrityReport dataclass; adapt it
    return {
        "status": "validated" if report.overall_integrity else "issues_found",
        "issues": list(report.issues),
        "warnings": list(report.warnings),
        "summary": {
            "overall_integrity": report.overall_integrity,
            "total_issues": len(report.issues),
        },
        "path": str(output_path),
    }


def validate_pdf_rendering(pdf_path: Union[str, Path]) -> Dict[str, Any]:
    """Validate PDF rendering using infrastructure validation.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Validation results
    """
    try:
        infra_validate_pdf_rendering, PDFValidationError = (
            _get_infra_validate_pdf_rendering()
        )
    except ImportError as e:
        return {"status": "error", "error": str(e), "path": pdf_path}

    try:
        results = infra_validate_pdf_rendering(Path(pdf_path))
        return {
            "status": "validated" if not results.get("issues") else "issues_found",
            "issues": results.get("issues", []),
            "warnings": results.get("warnings", []),
            "path": pdf_path,
        }
    except (PDFValidationError, OSError, ValueError) as e:
        # Expected: missing/corrupt PDF files, extraction failures
        return {"status": "error", "error": str(e), "path": pdf_path}
    except Exception:
        _logger.exception(
            "Unexpected error in validate_pdf_rendering for %s", pdf_path
        )
        raise


class IntegrityReport:
    """Compatibility wrapper for infrastructure integrity reports."""

    def __init__(self, results: Optional[Dict[str, Any]] = None):
        """Initialize from an infrastructure results dictionary.

        Args:
            results: Optional infrastructure results dictionary
        """
        if results:
            self.status = results.get("status", "unknown")
            self.summary = results.get("summary", "")
            self.issues = results.get("issues", [])
        else:
            self.status = "not_validated"
            self.summary = "No validation performed"
            self.issues = []

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"IntegrityReport(status='{self.status}', issues={len(self.issues)})"
