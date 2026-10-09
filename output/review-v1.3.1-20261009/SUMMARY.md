# v1.3.1 candidate verification (2026-10-09)

Branch `release/v1.3.1` from `eaa2f91` (published v1.3.0). Not merged, tagged, pushed or published.

## Input and method changes

- **Abstract provenance.** A second exact-text reconciliation pass admitted 59 legacy abstracts. Each was re-fetched from NCBI and admitted only when the stored string equals one reconstruction of exactly one PubMed abstract. `abstracts.json` is byte-identical to v1.3.0, and no existing provenance record changed. Unreconciled strings fell from 69 to 10: 9 have no candidate, and 1 is a 0.999 near match that is not admitted. Evidence: `integrate_legacy_provenance.py`, `legacy-provenance-integration.json`, `legacy-abstract-candidates.json`.
- **PMC notices.** Records whose titles mark them as corrections, errata, retraction notices or retracted items are excluded from full-text analysis by `EDITORIAL_NOTICE_TITLE`. This removes 76 of 7,073 records, including two full-length retracted articles. Shards are unchanged, and the artifact lists every excluded PMCID.

## Execution (final code)

| Step | Start (UTC) | End (UTC) | Result |
| --- | --- | --- | --- |
| Generation | 2026-10-09T22:04:28Z | 2026-10-09T22:26:48Z | exit=0 |
| Network reading | 2026-10-09T22:26:48Z | 2026-10-09T22:27:27Z | exit=0 |
| Custody audit | 2026-10-09T22:27:27Z | 2026-10-09T22:27:53Z | exit=0 |
| Strict render | 2026-10-09T22:27:53Z | 2026-10-09T22:31:18Z | exit=0; both fixed-margin protocols re-executed |
| Full tests | 2026-10-09T22:31:18Z | 2026-10-09T22:43:29Z | 1,856 passed, 8 skipped, 91.99% coverage |

The PDF has 53 pages and no unresolved placeholders. SHA-256: `c420fc8966f0bd0e9f476761d0c6c419a830bd602e669465e5fd72c5a9c9de12`.

## Numerical effect

`variables-diff.json` lists all 733 changed template variables (v1.3.0 → candidate). Headline abstracts went from 7,540 to 7,599 and analyzed full texts from 7,073 to 6,997. Threshold-crossing conclusions keep their direction:
- ANOVA p goes from 0.0278 to 0.0319.
- Economics vs Unit of Individuality remains the only BH-significant pair (0.0352 → 0.0464).
- Observed fixed-margin edges (4,235) and clustering (0.8955) remain below both null envelopes.

High-entropy shares are threshold-sensitive (Economics 57.7 → 46.2%, Sex & Reproduction 53.1 → 43.8%), and no manuscript prose ranks them. An earlier run with a looser title regex produced identical variables (`run2-before-regex-tightening/`).

## Independent review

A read-only reviewer found no blockers. Four smaller points were addressed before the final run: a wording fix in S02, a tightened regex with new negative tests, CLI parity, and a full-suite run in a layout where the sibling template repo is found. `README.md` keeps the published v1.3.0 counts until release.

## Interruptions

The first generation was killed by a host restart (`generation.attempt1-interrupted-by-server-restart.log`). The first full-test attempt failed at collection because the worktree had no sibling `template/`; its log is retained in `run2-before-regex-tightening/`.
