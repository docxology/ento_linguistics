"""Read-only: try to identify the 69 legacy abstracts lacking digest provenance via PubMed E-utilities.
Writes only a candidate report; never modifies data/."""
import json,hashlib,re,sys,time,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
E="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
def get(u):
    for k in range(4):
        try: return urllib.request.urlopen(u,timeout=30).read()
        except Exception as e: err=e; time.sleep(2+2*k)
    raise err
H=lambda t:hashlib.sha256(t.encode()).hexdigest()
norm=lambda t:re.sub(r"\s+"," ",t).strip()
a=json.loads(Path("data/corpus/abstracts.json").read_text()); p=json.loads(Path("data/corpus/provenance.json").read_text())["records"]
out=[]
for i,t in enumerate(a):
    if H(t) in p: continue
    uniq=list(dict.fromkeys(w.lower() for w in re.findall(r"[A-Za-z]{4,}",t)))
    ids=[]
    first=re.findall(r"[A-Za-z]{4,}",re.sub(r"^[A-Z ]+:\s*","",t))[:5]
    for q in [" AND ".join(f"{w}[tiab]" for w in sorted(uniq,key=len,reverse=True)[:n]) for n in (7,4,3)]+[" AND ".join(f"{w}[tiab]" for w in first)]:
        ids=json.loads(get(E+"esearch.fcgi?db=pubmed&retmode=json&retmax=5&term="+urllib.parse.quote(q)))["esearchresult"]["idlist"]; time.sleep(0.4)
        if ids: break
    best=None
    if ids:
        root=ET.fromstring(get(E+"efetch.fcgi?db=pubmed&retmode=xml&id="+",".join(ids))); time.sleep(0.4)
        for art in root.iter("PubmedArticle"):
            pm=art.findtext(".//PMID"); ab=" ".join("".join(x.itertext()) for x in art.iter("AbstractText"))
            ab2="\n".join("".join(x.itertext()) for x in art.iter("AbstractText"))
            parts=[(x.get("Label"),"".join(x.itertext())) for x in art.iter("AbstractText")]
            lab=[(f"{l}: {b}" if l else b) for l,b in parts]
            forms={ab,ab2," ".join(lab),"\n".join(lab)}
            exact=t in forms; nm=any(norm(f)==norm(t) for f in forms)
            if exact or nm:
                doi=next((x.text for x in art.iter("ArticleId") if x.get("IdType")=="doi"),None)
                best={"pmid":pm,"doi":doi,"title":art.findtext(".//ArticleTitle"),"year":art.findtext(".//PubDate/Year"),"journal":art.findtext(".//Journal/Title"),"match":"exact" if exact else "whitespace-normalized"}; break
    out.append({"index":i,"sha256":H(t),"candidates_searched":ids,"identified":best})
    print(i,best["match"] if best else "unidentified",file=sys.stderr)
r={"scope":"read-only candidate identification; data/ unmodified","records":len(out),"exact":sum(1 for o in out if o["identified"] and o["identified"]["match"]=="exact"),"normalized_only":sum(1 for o in out if o["identified"] and o["identified"]["match"]!="exact"),"unidentified":sum(1 for o in out if not o["identified"]),"items":out}
Path(sys.argv[1]).write_text(json.dumps(r,indent=2)+"\n"); print({k:r[k] for k in ("records","exact","normalized_only","unidentified")})
