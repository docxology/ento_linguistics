"""Inventory every tracked Markdown file and inspect Pandoc-parsed local links."""
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterator
import subprocess
import argparse
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd()
TRACKED = set(subprocess.check_output(["git", "ls-files"], text=True).splitlines())

def links(node: Any) -> Iterator[str]:
    """Yield explicit Markdown links/images from Pandoc AST nodes."""
    if isinstance(node, dict):
        if node.get("t") in ("Link", "Image"):
            yield node["c"][-1][0]
        for v in node.values():
            yield from links(v)
    elif isinstance(node, list):
        for v in node:
            yield from links(v)

def inspect_link(source: Path, target: str) -> dict[str, str] | None:
    """Return a missing/local-only issue for a local link; otherwise None."""
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    resolved = Path(os.path.normpath(str(source.parent / unquote(parsed.path))))
    name = resolved.as_posix()
    if not resolved.exists():
        return {"source": str(source), "target": target, "resolved": name, "issue": "missing"}
    if name not in TRACKED and not any(x.startswith(name.rstrip("/") + "/") for x in TRACKED):
        return {"source": str(source), "target": target, "resolved": name, "issue": "local_only"}
    return None

def main() -> None:
    """Write the tracked-file receipt and fail on local-link issues."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/review-docs-20261008/inventory-final.json"))
    args = parser.parse_args()
    files = sorted(x for x in TRACKED if x.endswith(".md"))
    rows, issues, warnings = [], [], []
    for name in files:
        p = Path(name)
        run = subprocess.run(["pandoc", "--from=markdown", "--to=json", name], text=True, capture_output=True, check=True)
        ast = json.loads(run.stdout)
        targets = list(links(ast))
        rows.append({"path": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "lines": len(p.read_text().splitlines()), "links": len(targets)})
        if run.stderr:
            warnings.append({"path": name, "stderr": run.stderr})
        issues.extend(v for t in targets if (v := inspect_link(p, t)))
    # Real missing and real local-only controls: neither may pass.
    assert inspect_link(Path("README.md"), "output/review-docs-20261008/nonexistent-negative-control.md")["issue"] == "missing"
    marker = Path("output/review-docs-20261008/negative-control-local.txt")
    marker.write_text("Real local-only link negative control.\n")
    assert inspect_link(Path("README.md"), str(marker))["issue"] == "local_only"
    result = {"files": rows, "total": len(rows), "local_link_issues": issues, "pandoc_warnings": warnings, "negative_controls": "PASS"}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"total": len(rows), "issues": issues, "warnings": warnings}, indent=2))
    if issues:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
