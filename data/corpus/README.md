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

## Corpus growth (2026-09-16, PubMed `--grow` harvest)

`abstracts.json` was grown from 907 to **1,907 abstracts** by appending 1,000
new, deduplicated PubMed records through the pipeline's `--grow` mode
(`scripts/01_build_corpus.py --grow --target-new 1000`). Growth is
**append-only**: the original 369 records are untouched and identical to
`abstracts_backup.json` (the v1 pre-growth snapshot, refreshed 2026-09-15),
and `provenance.json` tracks every record appended since (both the 538 added
on 2026-09-15 and the 1,000 added here).

### Provenance
- Source: PubMed via NCBI E-utilities (`esearch` / `esummary` / `efetch`),
  retrieved 2026-09-16 through `PubMedMiner` in
  `src/data/literature_mining.py` (`search` + `fetch_publications`, batched,
  with the miner's built-in sleep-based rate limiting).
- `provenance.json` now carries **1,538 sidecars** keyed by the SHA-256 of
  the exact abstract string in `abstracts.json`, with
  `{pmid, doi, title, year, journal, query}` values (538 from the 2026-09-15
  growth + 1,000 from this harvest; the original 369 predate PMID-level
  provenance tracking and have no entries there).
- `provenance.json` also carries a top-level **`seen_pmids` ledger**
  (5,016 PMIDs): every PMID surfaced by a growth-query search since
  2026-09-16, appended or not. This is what makes repeated `--grow` runs
  idempotent: a second run excludes everything the searches already
  surfaced, so it appends nothing.

### Harvest results (retmax 1000, target 1000 new)

| # | Query name | Hits (retmax 1000) | Appended |
|---|-----------|--------------------|----------|
| 1 | `reproductive_skew` | 68 | 0 (saturated 2026-09-15) |
| 2 | `kin_recognition` | 93 | 0 (saturated 2026-09-15) |
| 3 | `superorganism` | 155 | 4 |
| 4 | `nestmate_recognition` | 255 | 98 |
| 5 | `colony_organization` | 359 | 184 |
| 6 | `eusocial_communication` | 391 | 330 |
| 7 | `sociobiology` | 351 | 293 |
| 8 | `kin_selection` | 424 | 91 |
| 9 | `division_of_labor` | 725 | 0 (target reached mid-run) |
| 10 | `foraging_economics` | 1000 (capped) | 0 (target reached mid-run) |
| 11 | `caste_queen_worker` | 1000 (capped) | 0 (target reached mid-run) |
| 12 | `myrmecology_core` | 1000 (capped) | 0 (target reached mid-run) |

Total appended: 1,000 (target reached exactly, mid-batch inside query 8).
Dedupe: zero duplicate PMIDs, zero duplicate abstract text keys (first 100
lowercased whitespace-collapsed characters), zero duplicate sidecar keys in
the merged 1,907-record corpus. Record-level filters unchanged from
2026-09-15: non-empty abstract, English, journal article / review, and the
social-insect relevance-token check (`_RELEVANCE_TOKENS` in
`src/data/literature_mining.py`).

### `--grow` / `--force` semantics (`scripts/01_build_corpus.py`)

- **default (no flags)**: if the corpus already holds >= 20 abstracts,
  nothing is fetched; only `output/data/corpus_statistics.json` is refreshed.
- **`--force`**: re-fetches the 8 base `ENTOMOLOGY_QUERIES` and **merges**
  the results into the existing corpus with dedupe (PMID from provenance +
  100-char text key); it never drops or overwrites existing records, and
  newly appended records get provenance sidecars. (Before 2026-09-16
  `--force` overwrote `abstracts.json` from scratch, destroying grown
  records — fixed and regression-tested.)
- **`--grow [--target-new N] [--max-per-query N] [--since-pdat DATE]`**:
  searches all 12 `CORPUS_GROWTH_QUERIES` (default `--max-per-query` 1000),
  appends up to `--target-new` new unique records (default 1000), updates
  `provenance.json` sidecars plus the `seen_pmids` ledger, and rewrites the
  statistics file. **Idempotent**: a second run with the same search surface
  appends 0 (verified 2026-09-16: 1,907 existing + 0 new).
  `--since-pdat "2020/01/01"` appends `AND ("2020/01/01"[PDAT] : "3000")` to
  every query so future runs can catch newly published work.

### How to reproduce / grow further

```bash
# Idempotent growth pass (searches all 12 queries, appends only new records)
uv run python scripts/01_build_corpus.py --grow --target-new 1000

# Date-windowed growth pass (only newly published work)
uv run python scripts/01_build_corpus.py --grow --target-new 1000 \
    --since-pdat "2026/09/16"

# Saturation marker: record the current search surface without fetching
uv run python scripts/01_build_corpus.py --grow --target-new 0
```

## Corpus growth (2026-09-19 → 2026-09-20, full search-surface drain)

Two full-surface `--grow` passes grew the corpus from 1,907 to **7,609
abstracts** (+5,702). The 2026-09-19 pass appended 5,701 records
(sidecars 1,538 → 7,239; `seen_pmids` ledger 5,016 → 11,077; committed as
the 2026-09-20 baseline). The 2026-09-20 pass
(`--target-new 500000 --max-per-query 10000`, no date window) then fully
enumerated every remaining hit of all 12 `CORPUS_GROWTH_QUERIES` and
appended just **1** new record (from `foraging_economics`), bringing the
sidecar count to 7,240 and the ledger to 11,078.

### 2026-09-20 full-surface hit counts (retmax 10000, all queries enumerated)

| # | Query name | Hits | Appended |
|---|-----------|------|----------|
| 1 | `reproductive_skew` | 68 | 0 |
| 2 | `kin_recognition` | 93 | 0 |
| 3 | `superorganism` | 155 | 0 |
| 4 | `nestmate_recognition` | 255 | 0 |
| 5 | `colony_organization` | 359 | 0 |
| 6 | `eusocial_communication` | 391 | 0 |
| 7 | `sociobiology` | 351 | 0 |
| 8 | `kin_selection` | 424 | 0 |
| 9 | `division_of_labor` | 725 | 0 |
| 10 | `foraging_economics` | 1809 | 1 |
| 11 | `caste_queen_worker` | 1271 | 0 |
| 12 | `myrmecology_core` | 7177 | 0 |

Total appended: 1 (7,608 → 7,609). **The search surface is exhausted**: the
corpus now contains every record the 12 growth queries return that passes
the relevance filters and dedupe. Further `--grow` runs append 0 until
newly published matching work appears (use `--since-pdat "2026/09/20"` to
window future growth).

Validation after any growth:
`uv run pytest tests/test_corpus_build.py tests/test_literature_mining.py -q`
plus a `DataLoader().load_corpus("corpus/abstracts.json")` smoke load.
All 12 `CORPUS_GROWTH_QUERIES` were fully enumerated on 2026-09-20 (see the
2026-09-19 → 2026-09-20 growth section above); raising `--target-new` no
longer grows the corpus until new publications appear.

## arXiv preprint layer (2026-09-16)

`arxiv_records.json` holds arXiv preprints harvested as a **separate source
layer** — these records are deliberately **not merged** into `abstracts.json`,
which remains the PubMed-only corpus. The layer is produced by
`src/data/arxiv_corpus.py`, which queries the existing `ArXivMiner` machinery
(`EnrichedArXivMiner` subclass adding arXiv ID / primary category / raw
publication timestamp parsing).

### Schema
- `arxiv_records.json`: list of `{arxiv_id, doi, title, abstract,
  primary_category, published, authors}` (`doi` is `null` when the preprint
  has none).
- `arxiv_provenance.json`: sidecar keyed by the SHA-256 of each abstract
  string (same convention as `provenance.json`), with `arxiv_id`, `title`,
  `doi`, `primary_category`, `published`, the originating `query`, and the
  retrieval timestamp. The file also records the verbatim queries and
  per-query kept/duplicate counts.

### Queries used (verbatim, in execution order)
Each query is category-restricted to `q-bio.PE` (quantitative biology:
population & evolutionary biology) and `nlin.AO` (nonlinear sciences:
adaptation & organization); see `ARXIV_QUERIES` in `src/data/arxiv_corpus.py`:

| # | Query name | Verbatim query |
|---|-----------|----------------|
| 1 | `ant_colonies` | `(cat:q-bio.PE OR cat:nlin.AO) AND all:"ant colonies"` |
| 2 | `eusociality` | `(cat:q-bio.PE OR cat:nlin.AO) AND all:"eusociality"` |
| 3 | `superorganisms` | `(cat:q-bio.PE OR cat:nlin.AO) AND all:"superorganisms"` |
| 4 | `collective_behavior` | `(cat:q-bio.PE OR cat:nlin.AO) AND all:"collective behavior"` |
| 5 | `stigmergy` | `(cat:q-bio.PE OR cat:nlin.AO) AND all:"stigmergy"` |

### Filters and dedupe rule
- Record-level: non-empty arXiv ID/title/abstract; word-boundary match
  against the social-insect relevance tokens (`is_relevant_social_insect_text`
  in `src/data/literature_mining.py`).
- Internal dedupe: by arXiv ID (version-stripped), normalized title, and
  first-100-normalized-abstract-chars.
- Dedupe against the PubMed corpus (`abstracts.json` + `provenance.json`):
  by DOI, normalized title (from provenance records), and normalized abstract
  prefix (covers the whole corpus, including the 369 original records that
  predate provenance tracking).

### How to reproduce
From the `ento_linguistics` project root:

```bash
uv run python -m data.arxiv_corpus --target 100        # live harvest
uv run python -m data.arxiv_corpus --dry-run           # plan only, no writes
```

The harvest is **resumable**: arXiv IDs already present in
`arxiv_records.json` are skipped on re-run. Tests:
`uv run pytest tests/test_arxiv_corpus.py -q`.

## OpenAlex citation enrichment (2026-09-16)

`citation_metadata.json` holds OpenAlex citation metadata for every
DOI-bearing record of the PubMed corpus (DOIs read from `provenance.json`).
Produced by `src/data/openalex_enrichment.py`, which queries
`https://api.openalex.org/works/doi:<doi>` with a polite `mailto` parameter
and a sleep between calls.

### Schema
Keys are the SHA-256 of the record's abstract string (matching
`provenance.json`); each entry carries its `doi` plus either:
- `"status": "ok"` with `cited_by_count`, `publication_year`, `concepts`
  (top 3 concept display names by score), `open_access`
  (`{is_oa, oa_status}`), and `fetched_at`; or
- `"status": "not_found"` (OpenAlex 404 — DOI unknown to OpenAlex) with
  `checked_at`; or
- `"status": "error"` (network failure after 3 retries) with the error text.

`not_found` and `error` entries are explicit — no DOI is ever silently
skipped.

### How to reproduce
From the `ento_linguistics` project root:

```bash
uv run python -m data.openalex_enrichment                 # all pending DOIs
uv run python -m data.openalex_enrichment --limit 10      # first 10 only
uv run python -m data.openalex_enrichment --dry-run       # plan only
```

The enrichment is **resumable**: `ok`/`not_found` entries are skipped on
re-run (errors are retried), and the output file is rewritten after every
record, so an interrupted run can simply be restarted. Tests:
`uv run pytest tests/test_openalex_enrichment.py -q`.
