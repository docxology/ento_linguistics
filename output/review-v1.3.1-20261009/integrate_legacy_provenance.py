"""Second legacy reconciliation pass: admit exact-text PubMed matches to abstract provenance.

Inputs: the read-only candidate report (legacy-abstract-candidates.json).
Every candidate is re-fetched from NCBI eFetch/eSummary; a record is admitted only
when the stored abstract string equals exactly one reconstruction of exactly one
PubMed abstract. Corpus text (abstracts.json) is never modified.
"""
import hashlib
import json
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from data.literature_mining import PubMedMiner  # noqa: E402

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HERE = Path(__file__).parent


def fetch(endpoint, query):
    for attempt in range(4):
        try:
            time.sleep(0.4)
            with urlopen(Request(BASE + endpoint + "?" + query,
                                 headers={"User-Agent": "EntoLinguistics-custody-review/1.0"}), timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 + 2 * attempt)


def reconstructions(article):
    """Named reconstructions of a PubMed abstract from its AbstractText sections."""
    sections = [(s.get("Label", ""), "".join(s.itertext())) for s in article.iter("AbstractText")]
    plain = [text for _, text in sections]
    labelled = [f"{label}: {text}" if label else text for label, text in sections]
    stripped = [f"{label}: {text.strip()}" if label else text.strip() for label, text in sections if text.strip()]
    return {
        "sections joined with spaces": " ".join(plain),
        "sections joined with newlines": "\n".join(plain),
        "labelled sections joined with spaces": " ".join(labelled),
        "labelled sections joined with newlines": "\n".join(labelled),
        "pipeline eFetch join (labelled, stripped, spaces)": " ".join(stripped),
    }


def main():
    corpus = json.loads((ROOT / "data/corpus/abstracts.json").read_text())
    by_digest = {hashlib.sha256(t.encode()).hexdigest(): t for t in corpus}
    path = ROOT / "data/corpus/provenance.json"
    prov = json.loads(path.read_text())
    records = prov["records"]
    mapped_pmids = {str(v.get("pmid")) for v in records.values()}
    candidates = json.loads((HERE / "legacy-abstract-candidates.json").read_text())["items"]
    results = []
    for item in candidates:
        digest, found = item["sha256"], item["identified"]
        result = {"index": item["index"], "sha256": digest}
        if digest in records:
            result["status"] = "already_mapped"
        elif not found or found["match"] != "exact":
            result["status"] = "not_admitted_no_exact_candidate"
        elif found["pmid"] in mapped_pmids:
            result.update(status="not_admitted_pmid_already_mapped", pmid=found["pmid"])
        else:
            text = by_digest[digest]
            pmid = found["pmid"]
            root = ET.fromstring(fetch("efetch.fcgi", f"db=pubmed&retmode=xml&id={pmid}"))
            articles = [a for a in root.iter("PubmedArticle") if a.findtext(".//PMID") == pmid]
            forms = [name for a in articles for name, value in reconstructions(a).items() if value == text]
            if len(articles) != 1 or not forms:
                result.update(status="not_admitted_refetch_mismatch", pmid=pmid)
            else:
                summary = json.loads(fetch("esummary.fcgi", f"db=pubmed&retmode=json&id={pmid}"))["result"][pmid]
                pub = PubMedMiner()._parse_pubmed_summary(summary)
                records[digest] = {
                    "pmid": pmid, "doi": pub.doi, "title": pub.title, "year": pub.year,
                    "journal": pub.journal, "query": "legacy_exact_text_reconciliation",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "match": f"exact stored text equals NCBI eFetch abstract ({forms[0]})",
                }
                mapped_pmids.add(pmid)
                result.update(status="admitted", pmid=pmid, form=forms[0])
        results.append(result)
        print(result["index"], result["status"], result.get("form", ""), flush=True)
    admitted = [r for r in results if r["status"] == "admitted"]
    prov["seen_pmids"] = sorted(set(prov["seen_pmids"]) | {r["pmid"] for r in admitted})
    prov["_note"] = ("Keys are sha256 of the exact abstract string in abstracts.json. Records appended after the "
                     "original 369 carry harvest provenance; original records are mapped only where a later "
                     "reconciliation found an exact NCBI text match (see _reconciliation). Unmapped strings remain "
                     "in abstracts.json but are excluded from the headline analysis.")
    prov["_reconciliation"] = {
        "source": "NCBI ESearch/eSummary/eFetch",
        "method": "Unambiguous exact stored-abstract text equality; no corpus text edits",
        "legacy_records_checked": 369,
        "exact_matches_added": 300 + len(admitted),
        "passes": [
            {"exact_matches_added": 300, "evidence": "output/review-20261005/legacy_reconciliation_merged.json"},
            {"exact_matches_added": len(admitted),
             "evidence": "output/review-v1.3.1-20261009/legacy-provenance-integration.json"},
        ],
        "unmapped_legacy_records": sum(r["status"] != "admitted" for r in results),
    }
    path.write_text(json.dumps(prov, indent=2) + "\n")
    summary = {"admitted": len(admitted), "not_admitted": len(results) - len(admitted), "items": results}
    (HERE / "legacy-provenance-integration.json").write_text(json.dumps(summary, indent=2) + "\n")
    print({k: summary[k] for k in ("admitted", "not_admitted")})


if __name__ == "__main__":
    main()
