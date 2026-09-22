# BHL Historical Full-Text Corpus (1850-1970) — data/bhl

Biodiversity Heritage Library historical layer grounding the
manuscript's S03b longitudinal claims (see
`docs/manuscript/S03b_case_studies.md` and
`src/pipeline/bhl_analysis.py`).

Last harvest run: 0 new documents from 133 candidates (3 texts fetched, 0 without text derivative, 0 out of window, 3 irrelevant, 0 failed items skipped).


## API reality check

- BHL API v3 (`https://www.biodiversitylibrary.org/api3`) requires an
  API key: keyless calls return `Status: unauthorized` ("'' is an
  invalid or unauthorized API key.").  Request a free key at
  `https://www.biodiversitylibrary.org/getapikey.aspx` and export it
  as `BHL_API_KEY` to upgrade the harvest to the official endpoints
  (`search`, `GetTitleMetadata`, `GetItemMetadata`,
  `GetPageMetadata`/`GetPageText`).
- Keyless per-page text (`https://www.biodiversitylibrary.org/page/N.txt`)
  is Cloudflare-gated (HTTP 403) for non-browser clients.
- The `/data/` OpenData exports (BibTeX/KBART/MODS/RIS/TSV) are
  metadata-only — no full text.
- When a key is available the harvest additionally runs BHL's
  keyed full-text search (`PublicationSearch`, `searchtype=F`) — the
  "Search Inside" capability; the literal `op=SearchInside` returns an
  empty 200 response and is not part of the API method table.
- This corpus therefore harvests the BHL mirror collection on the
  Internet Archive (`collection:"biodiversity"`) via IA's keyless
  Search / Metadata / Download endpoints; each record lists the BHL
  collections its item belongs to.

API check at harvest time: endpoint `https://www.biodiversitylibrary.org/api3`, keyed=False, status=`HTTP 401 (key required)`, ok=False.


## Files

- `bhl_shard_NNNNN.json` — shard files, at most 40 records
  (~19 MB) each (GitHub rejects blobs >100 MB), holding JSON lists of
  records with fields: `bhl_id`, `ia_identifier`, `title`,
  `publication_date`, `year`, `era`, `collections`, `url`,
  `full_text`.  Concatenation order is filename order:

- `bhl_shard_00001.json`
- `bhl_shard_00002.json`
- `bhl_shard_00003.json`
- `bhl_shard_00004.json`
- `bhl_shard_00005.json`
- `bhl_shard_00006.json`
- `bhl_shard_00007.json`
- `bhl_shard_00008.json`
- `bhl_shard_00009.json`
- `bhl_shard_00010.json`
- `bhl_shard_00011.json`
- `bhl_shard_00012.json`
- `bhl_shard_00013.json`
- `bhl_shard_00014.json`
- `bhl_shard_00015.json`
- `bhl_shard_00016.json`
- `bhl_shard_00017.json`
- `bhl_shard_00018.json`
- `bhl_shard_00019.json`
- `bhl_shard_00020.json`
- `bhl_shard_00021.json`
- `bhl_shard_00022.json`
- `bhl_shard_00023.json`
- `bhl_shard_00024.json`
- `bhl_shard_00025.json`
- `bhl_shard_00026.json`
- `bhl_shard_00027.json`
- `bhl_shard_00028.json`
- `bhl_shard_00029.json`
- `bhl_shard_00030.json`
- `bhl_shard_00031.json`
- `bhl_shard_00032.json`
- `bhl_shard_00033.json`
- `bhl_shard_00034.json`
- `bhl_shard_00035.json`
- `bhl_shard_00036.json`
- `bhl_shard_00037.json`
- `bhl_shard_00038.json`
- `bhl_shard_00039.json`
- `bhl_shard_00040.json`
- `bhl_shard_00041.json`
- `bhl_shard_00042.json`
- `bhl_shard_00043.json`
- `bhl_shard_00044.json`
- `bhl_shard_00045.json`
- `bhl_shard_00046.json`
- `bhl_shard_00047.json`
- `bhl_shard_00048.json`
- `bhl_shard_00049.json`
- `bhl_shard_00050.json`
- `bhl_shard_00051.json`
- `bhl_shard_00052.json`
- `bhl_shard_00053.json`
- `bhl_shard_00054.json`
- `bhl_shard_00055.json`
- `bhl_shard_00056.json`
- `bhl_shard_00057.json`
- `bhl_shard_00058.json`
- `bhl_shard_00059.json`
- `bhl_shard_00060.json`
- `bhl_shard_00061.json`
- `bhl_shard_00062.json`

- `provenance.json` — sidecar mapping `sha256(full_text)` to
  `{bhl_id, ia_identifier, title, publication_date, era, collections,
  url, query, retrieved_at}`.
- `searchinside_results.json` — keyed-search checkpoint: per-term
  in-window publication lists from `PublicationSearch` (resumable:
  terms already present are not re-queried).
- `searchinside_items.json` — keyed-search checkpoint: Part→Item
  resolution cache, the ranked capped candidate item list with the
  queries that matched each item, and the IA-backed harvest stubs.
- `README.md` — this document.

## Search query (verbatim)

```
collection:"biodiversity" AND mediatype:texts AND (title:(ants OR ant OR Formicidae OR myrmecology) OR subject:(Formicidae OR ants OR myrmecology OR "social insects" OR eusocial)) AND date:[1850-01-01 TO 1970-12-31]
```

Issued against `https://archive.org/advancedsearch.php` with
`fl[]=identifier,title,year,collection`, `rows=200`,
`output=json`, paging via `start`.

## Filters

1. `collection:"biodiversity"` — BHL-ingested scans only.
2. `mediatype:texts` — items with retrievable derivatives.
3. Title/subject clause binds hits to ant / Formicidae / myrmecology /
   social-insect / eusocial literature.
4. `date:[1850-01-01 TO 1970-12-31]` — publication-date window;
   item metadata `date`/`year` is authoritative, undatable items are
   dropped.
5. Era buckets: 1850-1899 -> `era_1850_1899`, 1900-1949 ->
   `era_1900_1949`, 1950-1970 -> `era_1950_1970`.
6. Word-boundary relevance guard over title+text: ant/ants,
   Formicidae, myrmecology/myrmecological, eusocial/eusociality,
   "social insects".

## Era coverage (2460 documents)

- Publication years: 1850-1970
- Body text: 2,350,509,858 characters
- Documents per era:

- `era_1850_1899`: 1013 documents
- `era_1900_1949`: 1247 documents
- `era_1950_1970`: 200 documents

## Reproduction

```bash
uv run python src/data/bhl_corpus.py
# keyed full-text upgrade (requires BHL_API_KEY; resumable):
BHL_API_KEY=<key> uv run python src/data/bhl_corpus.py --keyed
```

The harvester is resumable: stored `ia_identifier`s are skipped and
re-running continues an interrupted harvest.  Load the corpus with:

```python
from pathlib import Path
from data.bhl_corpus import load_corpus_records
records = load_corpus_records(Path("data/bhl"))
```

The era-stratified analysis is built separately:

```bash
uv run python src/pipeline/bhl_analysis.py
```
