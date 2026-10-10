"""Reserve the v1.3.1 Zenodo version draft (unpublished) without exposing credentials."""
from pathlib import Path
import json
import requests

root = Path.cwd()
work = root / "output/release-v1.3.1-20261010"
entries = dict(line.split("=", 1) for line in (root.parent / "template" / ".env").read_text().splitlines()
               if line.startswith("ZENODO_PROD_TOKEN="))
s = requests.Session()
s.headers["Authorization"] = "Bearer " + entries["ZENODO_PROD_TOKEN"].strip().strip(chr(34)).strip(chr(39))
base = "https://zenodo.org/api/deposit/depositions"
r = s.post(base + "/23215452/actions/newversion", timeout=60)
r.raise_for_status()
r = s.get(r.json()["links"]["latest_draft"], timeout=60)
r.raise_for_status()
draft = r.json()
(work / "zenodo-draft.json").write_text(json.dumps(draft, indent=2))
print(json.dumps({"id": draft["id"], "doi": draft["metadata"]["prereserve_doi"]["doi"],
                  "submitted": draft["submitted"], "files": [f["filename"] for f in draft["files"]]}))
