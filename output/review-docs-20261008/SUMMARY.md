# Repository Markdown reconciliation — 8 October 2026

The baseline was main `aacf9efdd420576238ab544b33dad3d879ae506c`, containing 90 tracked Markdown files. Every tracked file was inventoried and parsed with Pandoc; maintained guidance was checked against the checkout, canonical manuscript values against valid exports, and historical evidence against its recorded scope. This summary is the additional Markdown file in the documentation candidate.

## Corrections

- Replace obsolete parent-template/local-only rules in all output directory guides with standalone ownership, managed artifacts and evidence-preservation guidance.
- Reconcile BHL counts with every stored shard: 2,430 documents and 2,317,721,403 characters, distributed 996/1,237/197 by era. Independently check PMC totals, year range, journals and every raw license-string count. Clarify historical harvest summaries and limits of license metadata.
- Correct the agent API example: real reproduction rejects a list of term pairs, while the dictionary-based example succeeds. Complete its inputs and flat package imports.
- Replace stale test guidance, fake examples and sub-30-second timing promises with real suite commands, combined coverage meaning, current test navigation and explicit external-tool/template requirements.
- Complete the pipeline module map and explain helper limitations, direct module paths, strict renderer and extension dependencies.
- Distinguish the 49-page unpublished 1.2.2-dev draft from the 47-page published v1.2.1 PDF throughout current navigation; update the missing changelog entries and retain historical release dates/results.
- Replace superseded September combined-manuscript and generic-report reading surfaces with archival navigation. Preserve all four original files byte-for-byte as `.txt` records in [legacy Markdown archive](../archive/legacy-markdown/identities.json). Historical independent reviews and their rejected/approved verdicts remain untouched.

## Verification

[Final inventory](inventory-final.json) records every tracked Markdown path/hash, parsed link count, missing/local-only link checks and real negative controls. The link validator exits nonzero for issues; a file merely existing locally does not qualify as a public tracked target. All parsed local links resolve to tracked files/directories, and no local fragment links require anchor checks. [Initial inventory](inventory-initial.json) retains the pre-edit path/parse receipt.

[Command receipts](command-receipts.json) and [log](command-checks.log) capture actual acquisition/render/helper help, stage listing, a dry run and collection: 1,828 tests collected, without executing acquisition or generation. [API control](api-example.log) records failure of the old input and success of the corrected example. [Corpus checks](corpus-readme-checks.json) record shard-derived counts. [Artifact checks](artifact-checks.json) validate the existing manifest, registered figures, both exact extension protocols, all 16 canonical manuscript sections and rejection of an unknown template variable.

No Python production source, executable tests, dependency lock, scientific corpus JSON, numerical exports, figure PNGs, fixed-margin traces or PDF bytes changed. Original archive bytes match the pushed baseline. The unchanged draft SHA-256 is `071a42aa8ee8a4c59363171325ddae74853e8152f0b8d762fd13d4957d6e0d12`; published SHA-256 is `098953e2594fffc94c347051b7b28cce631eba6820a52381d8cda968718da8c3`. The prior full-suite/render evidence retains its source scope; documentation-only checks are not relabeled as a fresh heavy suite or scientific computation.

This audit reconciles maintained documentation and computational bindings. It is not a fresh complete bibliography, external-link availability, relevance, individual-license, human-validation or causal-scientific audit. API service behavior in acquisition notes is explicitly historical. Historical review paths may refer to retained local or earlier Git-history evidence and do not imply those files are current public procedures. The separately recorded documentation gate binds the documentation candidate.
