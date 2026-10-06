"""Read-only corpus custody checks with bounded memory and explicit gaps."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from core.provenance import validate_analysis_manifest


def audit_layer(paths: list[Path], provenance: dict[str, Any],
                text_field: str | None, id_field: str | None) -> dict[str, Any]:
    """Audit every stored record without inferring scientific relevance.

    Digest-indexed provenance can collapse identical texts under distinct
    IDs. Both coverage and ID mismatches are retained rather than repaired.

    Example with a stored abstract shard::

        result = audit_layer(paths, digest_provenance, None, None)
        invalid = result["invalid_records"]
    """
    ids: Counter = Counter()
    digests: Counter = Counter()
    invalid = []
    missing = []
    mismatched = []
    metadata_examples = []
    characters = 0
    eras: Counter = Counter()
    records = 0
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a record list")
        for index, record in enumerate(data):
            records += 1
            text = record if text_field is None else record.get(text_field)
            if not isinstance(text, str) or not text.strip():
                invalid.append({"file": path.name, "record": index})
                continue
            characters += len(text)
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            digests[digest] += 1
            entry = provenance.get(digest)
            if entry is None:
                missing.append({"file": path.name, "record": index, "sha256": digest})
            elif id_field and entry.get(id_field) != record.get(id_field):
                mismatched.append({"file": path.name, "record": index,
                                   "record_id": record.get(id_field),
                                   "provenance_id": entry.get(id_field)})
            if id_field:
                ids[record.get(id_field)] += 1
                if record.get("era"):
                    eras[record["era"]] += 1
            if len(metadata_examples) < 5 and entry:
                metadata_examples.append(entry)
    return {"records": records, "characters": characters,
            "files": [path.name for path in paths], "provenance_entries": len(provenance),
            "records_without_provenance": len(missing), "missing_examples": missing[:10],
            "provenance_id_mismatches": len(mismatched), "mismatch_examples": mismatched[:10],
            "unused_provenance_entries": len(set(provenance) - set(digests)),
            "duplicate_text_records": sum(count - 1 for count in digests.values()),
            "duplicate_ids": sum(count - 1 for count in ids.values()),
            "missing_ids": ids.get(None, 0) + ids.get("", 0),
            "invalid_records": invalid, "era_documents": dict(sorted(eras.items())),
            "metadata_examples": metadata_examples}


def audit_corpus(root: Path) -> dict[str, Any]:
    """Check all four stored source layers, preserving the underlying bytes.

    Example::

        audit = audit_corpus(Path.cwd())
        missing = audit["layers"]["abstract"]["records_without_provenance"]
    """
    corpus = root / "data" / "corpus"
    sources = [
        ("abstract", [corpus / "abstracts.json"], corpus / "provenance.json", None, None),
        ("fulltext", sorted((root / "data" / "fulltexts").glob("fulltexts_*.json")),
         root / "data" / "fulltexts" / "provenance.json", "body_text", "pmcid"),
        ("bhl_historical", sorted((root / "data" / "bhl").glob("bhl_shard_*.json")),
         root / "data" / "bhl" / "provenance.json", "full_text", "ia_identifier"),
        ("arxiv", [corpus / "arxiv_records.json"], corpus / "arxiv_provenance.json",
         "abstract", "arxiv_id"),
    ]
    layers = {}
    for name, paths, sidecar, text_field, id_field in sources:
        if not paths or not all(path.exists() for path in paths):
            raise FileNotFoundError(f"Missing corpus layer: {name}")
        provenance = json.loads(sidecar.read_text())
        if name in {"abstract", "arxiv"}:
            provenance = provenance["records"]
        layers[name] = audit_layer(paths, provenance, text_field, id_field)
    return {"schema": 1, "layers": layers,
            "interpretation": "Local custody audit; does not establish relevance, licensing, annotation validity, or causal effects."}


def main() -> int:
    """Write the audit and return nonzero on malformed corpus records.

    Example CLI invocation::

        PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--require-analysis", action="store_true")
    args = parser.parse_args()
    audit = audit_corpus(args.root)
    target = args.root / "output" / "reports" / "corpus_audit.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    for name, result in audit["layers"].items():
        print(f"{name}: {result['records']} records; "
              f"{result['records_without_provenance']} without digest provenance; "
              f"{result['duplicate_text_records']} duplicate texts")
    if args.require_analysis:
        validate_analysis_manifest(args.root)
        print("Analysis receipt matches current corpus, implementation, and outputs")
    return int(any(layer["invalid_records"] for layer in audit["layers"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
