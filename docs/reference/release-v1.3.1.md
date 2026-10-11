# Version 1.3.1 release verification

[GitHub release v1.3.1](https://github.com/docxology/ento_linguistics/releases/tag/v1.3.1) and [Zenodo version DOI 10.5281/zenodo.23287623](https://doi.org/10.5281/zenodo.23287623) publish the 53-page paper and the network-methods bundle. This is a corpus-custody patch: a second exact-text PubMed reconciliation links 59 more archived abstracts to their source records, and PMC records titled as corrections, errata, retraction notices or retracted items are excluded from full-text analysis. Stored abstract text and PMC shards are unchanged; the full-text artifact lists every excluded PMCID.

## Executed checks

| Surface | Verified result |
| --- | --- |
| Inputs | 7,599 of 7,609 archived abstracts identified (10 unreconciled, excluded from headline results); 6,997 of 7,073 stored PMC records analyzed (76 notices excluded) |
| Analysis | Full/default generation, network-reading diagnostic, custody audit and strict rendering passed; both fixed-margin protocols re-executed against the changed inputs |
| Numerical effect | All 733 changed template variables listed; threshold-crossing conclusions keep their direction (see candidate record) |
| Release render | 53 pages, no unresolved placeholders, version 1.3.1 and concept DOI on the title page |
| Public software | 1,856 passed, eight external-template skips, 91.99% combined coverage |
| Public readback | All three GitHub and Zenodo files downloaded and SHA-256 matched to the local bundle; the DOI resolves to the Zenodo record |
| Independent review | Candidate review found no blockers; a separate read-only release review of the metadata and documentation diff found citation, DOI and link defects that were fixed before tagging |

The [candidate verification record](../../output/review-v1.3.1-20261009/SUMMARY.md) retains the execution log, variable diff and reconciliation evidence. The [release folder](../../output/release-v1.3.1-20261010/) retains the release render, test log and Zenodo scripts; the [publication receipt](../../output/releases/v1.3.1-publication.json) records the exact public file identities.

A matched sixth-edition lecture was added to the GitHub release on 2026-10-11, after tagging and after the Zenodo version was published, so the v1.3.1 DOI identifies the paper and methods bundle only. The 1,200-second 4K video, slides, audio, transcript, captions, chapters and production receipt are listed with SHA-256 digests in the release's `lecture_manifest.json`; every uploaded file was downloaded back and matched ([lecture publication receipt](../../output/releases/v1.3.1-lecture-publication.json)). The LectureCreate verification record is `examples/ento_linguistics/verification/20261011-v6/` at LectureCreate commit `dbfd1cf`. The fifth-edition lecture remains with the [v1.3.0 release](https://github.com/docxology/ento_linguistics/releases/tag/v1.3.0), which has no DOI; earlier version DOIs keep their archived identities.

These checks establish software behavior, content custody and regenerated outputs. They do not validate the proposed proxies, causal interpretations or reader-study designs.
