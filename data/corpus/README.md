# corpus

Directory `corpus` inside the `ento_linguistics/data` tree of EntoTech.

Part of `ento_linguistics/data` (EntoTech lane, local-only under `projects/ongoing/`).

## Contents
Files: `AGENTS.md`, `README.md`, `abstracts.json`, `abstracts_backup.json`, `provenance.json`

## Usage
- See `ento_linguistics/data/README.md` for how this directory is produced and used.
- See `ento_linguistics/scripts/01_build_corpus.py` (thin orchestrator over
  `src/pipeline/corpus_build.py`) for the original stage-01 corpus build.

## Corpus growth (2026-09-15)

`abstracts.json` was broadened from 369 to **907 abstracts** by appending 538
new, deduplicated PubMed records. Growth is **append-only**: the original 369
records are untouched and identical to `abstracts_backup.json` (the pre-growth
snapshot, refreshed 2026-09-15).

### Provenance
- Source: PubMed via NCBI E-utilities (`esearch` / `esummary` / `efetch`),
  retrieved 2026-09-15 through `PubMedMiner` in `src/data/literature_mining.py`
  (`search` + `fetch_publications`, batched, with the miner's built-in
  sleep-based rate limiting).
- Every appended record is mapped to its PubMed identifiers in
  `provenance.json`: keys are the SHA-256 of the exact abstract string in
  `abstracts.json`; values carry `pmid`, `doi`, `title`, `year`, `journal`,
  and the originating query name (538 PMIDs, 536 DOIs; 2 records have no DOI
  in PubMed). The original 369 records predate PMID-level provenance tracking
  and have no entries there.
- The corpus is versioned in git: `data/corpus/abstracts.json`,
  `abstracts_backup.json`, and `provenance.json` are tracked; the growth
  commit records the exact retrieval state.

### Queries used (verbatim, in execution order)
Each query restricts to English journal articles/reviews
(`AND English[Language] AND (journal article[pt] OR review[pt])` appended
verbatim to every query below).

| # | Query name | Verbatim term (before the common suffix) | Hits (retmax=150) | Kept |
|---|-----------|------------------------------------------|-------------------|------|
| 1 | `reproductive_skew` | `"reproductive skew" AND (insect OR ant OR bee OR wasp OR termite)` | 68 | 62 |
| 2 | `kin_recognition` | `"kin recognition" AND (insect OR ant OR colony OR bee)` | 93 | 86 |
| 3 | `superorganism` | `superorganism AND (ant OR insect OR colony)` | 150 (capped) | 125 |
| 4 | `nestmate_recognition` | `("nestmate recognition" OR "nest odour" OR "nest odor")` | 150 (capped) | 137 |
| 5 | `colony_organization` | `("colony organization" OR "social organization") AND (insect OR ant OR bee OR wasp OR termite)` | 150 (capped) | 128 |
| 6-12 | `eusocial_communication`, `sociobiology`, `kin_selection`, `division_of_labor`, `foraging_economics`, `caste_queen_worker`, `myrmecology_core` | defined in `CORPUS_GROWTH_QUERIES` in `src/data/literature_mining.py` | not fetched (target reached after query 5) | — |

Queries 1–12 are the queries covering the six analysis domains; 6–12 remain
defined in `CORPUS_GROWTH_QUERIES` for future growth (running them would push
the corpus past its 1000-record ceiling).

### Filters and dedupe rule
- Query-level: English language, journal article / review publication types
  (enforced inside each query term).
- Record-level: non-empty abstract; word-boundary match against the
  social-insect relevance tokens (`_RELEVANCE_TOKENS` in
  `src/data/literature_mining.py`) — keeps the corpus on-topic and avoids
  pesticide/morphology-only pull-in.
- Dedupe: internal dedupe by PMID and by the first 100 lowercased,
  whitespace-collapsed characters of the abstract; then dedupe against the
  existing 369 records with the same text key (47 overlapping records
  discarded). Result: zero duplicate PMIDs, zero duplicate DOIs, zero
  duplicate abstract text keys in the merged corpus (907 records).

### How to reproduce
The queries live in `CORPUS_GROWTH_QUERIES` in `src/data/literature_mining.py`.
From the `ento_linguistics` project root:

```bash
.venv/bin/python -c "import sys; sys.path.insert(0, 'src'); \
from data.literature_mining import mine_corpus_growth; \
pubs, hits, pmid_to_query = mine_corpus_growth(max_per_query=150, target_new=500); \
print(hits, len(pubs))"
```

Then append the returned publications to `data/corpus/abstracts.json`
(dedupe by PMID and by first-100-lowercased-abstract-chars against both the
existing file and the new batch), and record PMIDs/DOIs/titles in
`provenance.json` keyed by the SHA-256 of each appended abstract. Validation
after any growth: `.venv/bin/python -m pytest tests/test_loader.py` plus a
`DataLoader().load_corpus("corpus/abstracts.json")` smoke load.

Note: `scripts/01_build_corpus.py --force` **overwrites** `abstracts.json`
with a fresh fetch rather than appending; it must not be used for growth.
