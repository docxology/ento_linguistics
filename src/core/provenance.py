"""Content signatures for reproducible analyses, independent of file mtimes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .nltk_resources import nltk_resource_fingerprints


def records_sha256(records: Iterable[Any]) -> str:
    """Hash ordered records with unambiguous lengths and canonical JSON.

    Example:
        >>> records_sha256(["ant"]) == records_sha256(["ant"])
        True
    """
    digest = hashlib.sha256()
    for record in records:
        payload = json.dumps(record, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def files_sha256(paths: Iterable[Path]) -> str:
    """Hash ordered file names and bytes in chunks; missing files raise.

    Example:
        >>> len(files_sha256([Path("uv.lock")]))
        64
    """
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(path.stat().st_size.to_bytes(8, "big"))
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def analysis_signature() -> str:
    """Bind caches to Python sources, locked dependencies and NLTK inputs.

    Example:
        >>> len(analysis_signature())
        64
    """
    root = Path(__file__).resolve().parents[2]
    source_signature = files_sha256([*sorted((root / "src").glob("**/*.py")), root / "uv.lock"])
    return records_sha256([source_signature, nltk_resource_fingerprints()])


def _inventory(root: Path) -> list[Path]:
    """Include corpus files and analysis/figure artifacts, excluding receipts."""
    paths = [*sorted((root / "data").glob("**/*.json")),
             *sorted((root / "output" / "data").glob("*.json")),
             *sorted((root / "output" / "figures").glob("*.png")),
             *sorted((root / "output" / "figures").glob("*.json"))]
    return [path for path in paths if path.name != "analysis_manifest.json"]


def write_analysis_manifest(root: Path) -> dict[str, Any]:
    """Freeze the current inputs and outputs after successful generation.

    Records bind file contents, inventory, and analysis implementation.
    This is a reproducibility receipt, not a scientific-validity certificate.

    Example pipeline use after all required stages succeed::

        validate_generated_artifacts(root)
        receipt = write_analysis_manifest(root)
    """
    paths = _inventory(root)
    if not paths:
        raise ValueError("Cannot certify an empty analysis inventory")
    manifest = {"schema": 2, "analysis_signature": analysis_signature(),
                "nltk_resources": nltk_resource_fingerprints(),
                "files": {str(path.relative_to(root)): files_sha256([path]) for path in paths}}
    target = root / "output" / "data" / "analysis_manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)
    return manifest


def validate_analysis_manifest(root: Path) -> None:
    """Reject missing receipts, changed sources/outputs, or unbound artifacts.

    Example after generation::

        validate_analysis_manifest(Path.cwd())
    """
    target = root / "output" / "data" / "analysis_manifest.json"
    manifest = json.loads(target.read_text(encoding="utf-8"))
    if (manifest.get("schema") != 2 or manifest.get("analysis_signature") != analysis_signature()
            or manifest.get("nltk_resources") != nltk_resource_fingerprints()):
        raise ValueError("Analysis implementation or NLTK resources changed; regenerate analyses")
    expected = manifest.get("files")
    if not isinstance(expected, dict) or not expected:
        raise ValueError("Analysis inventory is empty or invalid")
    paths = _inventory(root)
    if set(expected) != {str(path.relative_to(root)) for path in paths}:
        raise ValueError("Analysis inventory changed; regenerate analyses")
    for path in paths:
        if files_sha256([path]) != expected[str(path.relative_to(root))]:
            raise ValueError(f"Analysis content changed: {path.relative_to(root)}")


def validate_generated_artifacts(root: Path) -> None:
    """Check actual JSON, PNGs and their registry without external templates.

    Example after figure generation::

        validate_generated_artifacts(Path.cwd())
    """
    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-finite JSON value: {value}")

    paths = sorted((root / "output" / "data").glob("*.json"))
    paths += [path for path in (root / "data" / "bhl" / "era_term_usage.json",
                                root / "data" / "corpus" / "arxiv_analysis.json") if path.exists()]
    if not paths:
        raise ValueError("No generated analysis JSON")
    for path in paths:
        data = json.loads(path.read_text(), parse_constant=reject_constant)
        if not isinstance(data, dict) or not data:
            raise ValueError(f"Empty or invalid analysis object: {path.name}")
    figures = root / "output" / "figures"
    registry = json.loads((figures / "figure_registry.json").read_text())
    if not isinstance(registry, dict) or not registry:
        raise ValueError("Empty or invalid figure registry")
    registered = set()
    from PIL import Image
    for label, entry in registry.items():
        filename = entry["filename"]
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ValueError(f"Invalid registry filename for {label}")
        path = figures / filename
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if (entry.get("metadata") or {}).get("sha256") != digest:
            raise ValueError(f"Figure registry hash mismatch: {filename}")
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
        registered.add(filename)
    if registered != {path.name for path in figures.glob("*.png")}:
        raise ValueError("Unregistered or duplicate figure inventory")
