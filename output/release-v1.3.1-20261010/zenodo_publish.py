"""Replace inherited files in the reserved v1.3.1 draft, set metadata, publish, and verify."""
from pathlib import Path
import json
import requests

root = Path.cwd()
work = root / "output/release-v1.3.1-20261010"
entries = dict(line.split("=", 1) for line in (root.parent / "template" / ".env").read_text().splitlines()
               if line.startswith("ZENODO_PROD_TOKEN="))
s = requests.Session()
s.headers["Authorization"] = "Bearer " + entries["ZENODO_PROD_TOKEN"].strip().strip(chr(34)).strip(chr(39))
url = "https://zenodo.org/api/deposit/depositions/23287623"
manifest = json.loads((work / "assets/release_manifest.json").read_text())
upload = {**manifest["assets"]}
r = s.get(url, timeout=60); r.raise_for_status(); draft = r.json()
assert not draft["submitted"] and draft["metadata"]["prereserve_doi"]["doi"] == "10.5281/zenodo.23287623"
for f in draft["files"]:
    s.delete(f["links"]["self"], timeout=60).raise_for_status()
bucket = draft["links"]["bucket"]
for name in [*upload, "release_manifest.json"]:
    with open(work / "assets" / name, "rb") as fh:
        s.put(f"{bucket}/{name}", data=fh, timeout=600).raise_for_status()
meta = dict(draft["metadata"])
z = json.loads((root / ".zenodo.json").read_text())
meta.update({k: z[k] for k in ("title", "version", "description", "keywords", "creators", "license", "access_right", "upload_type", "publication_type")})
meta["publication_date"] = "2026-10-10"
meta["related_identifiers"] = [
    {"identifier": "https://github.com/docxology/ento_linguistics/tree/v1.3.1", "relation": "isSupplementTo", "resource_type": "software"},
    {"identifier": "10.5281/zenodo.23215452", "relation": "isNewVersionOf", "resource_type": "publication-preprint"},
]
r = s.put(url, json={"metadata": meta}, timeout=60)
if not r.ok:
    print(r.text); r.raise_for_status()
r = s.get(url, timeout=60); r.raise_for_status(); ready = r.json()
want = {n: "md5:" + manifest["assets"][n]["md5"] for n in upload}
got = {f["filename"]: f["checksum"] if f["checksum"].startswith("md5:") else "md5:" + f["checksum"] for f in ready["files"]}
assert set(got) == set(want) | {"release_manifest.json"}, got
assert all(got[n] == want[n] for n in want), (got, want)
(work / "zenodo-ready-draft.json").write_text(json.dumps(ready, indent=2))
r = s.post(url + "/actions/publish", timeout=120)
if not r.ok:
    print(r.text); r.raise_for_status()
published = r.json()
assert published["submitted"] and published["doi"] == "10.5281/zenodo.23287623"
(work / "zenodo-published-deposition.json").write_text(json.dumps(published, indent=2))
print(json.dumps({"doi": published["doi"], "record": published["links"].get("record_html") or published["links"].get("html"),
                  "files": sorted(got)}))
