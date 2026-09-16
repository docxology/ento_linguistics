# data

`data/` of the parent project.

Part of `ento_linguistics` (EntoTech lane, local-only under `projects/ongoing/`).

## Corpus abstracts
`corpus/abstracts.json` holds the literature corpus used by the analysis
pipeline: a plain JSON list of abstract text strings (907 records as of the
2026-09-15 growth; previously 369). Growth is append-only; the pre-growth
snapshot is `corpus/abstracts_backup.json`, and PubMed PMIDs/DOIs for every
appended record are recorded in `corpus/provenance.json` (source: PubMed
E-utilities, retrieved 2026-09-15). Queries, per-query counts, the dedupe
rule, and the reproduction command are documented in
`corpus/README.md`. All corpus files are versioned in git.

## Contents
Subfolders: `corpus/`
Files: `AGENTS.md`, `README.md`

## Usage
- See `ento_linguistics/README.md` for how this directory is produced and used.
