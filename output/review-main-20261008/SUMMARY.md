# Unpublished 1.2.2 draft continuation — 8 October 2026

Continues thread `417c0b35-40cc-4af3-a247-7de75b550c00`. The draft corrects figure geometry, exact-count category legends, weighted network hierarchy, exclusive word-formation classification, manuscript labels and rendering. Real negative controls reproduced the uninitialized label geometry, iterator exhaustion, overlapping tiny category labels, and Pandoc literal brace separators before correction.

- Full/default generation: exit 0, 17 figures; [receipt](generation-receipt.json), [log](generation.log).
- Complete suite: 1,820 passed, eight external-template skips, 83 warnings; 92.00% combined coverage (93.44% statements, 87.57% branches). [Receipt](tests-receipt.json), [log](final-tests.log), [coverage](coverage.json). The floor is 90% combined.
- Core implementation/resource/inventory coherence and full stored BHL character coverage pass. Ten numerical exports are unchanged after excluding only receipt/time identity fields; all 17 PNGs match the corrected pre-contract build. [Artifact checks](artifact-checks.json).
- Corpus custody audit: exit 0; 7,609 abstracts, 69 lacking source digest provenance excluded from the 7,540 headline corpus; 7,073 PMC bodies with eight duplicated texts, 2,430 BHL documents, 61 arXiv records. [Audit](custody-final.log).
- Strict render: exit 0, 49 physical pages; no unresolved tokens, literal `{,}` separators, overfull boxes, undefined references or missing-character diagnostics. Both fixed-margin companion trace arrays remain byte-identical to their preserved pre-change executions. [Render receipt](render-receipt.json), [log](render.log), [PDF checks](pdf-checks.json), [manual QA](manual-qa.json).
- Draft PDF SHA-256: `071a42aa8ee8a4c59363171325ddae74853e8152f0b8d762fd13d4957d6e0d12`. Analysis signature: `d30c303d6764ead8cc322145f5b9e67ee754beba06ad5f61700e67c423284aac`.

The PDF is 1.2.2-dev **unpublished**. The top-level published v1.2.1 PDF remains byte-identical (SHA-256 `098953e2594fffc94c347051b7b28cce631eba6820a52381d8cda968718da8c3`). No new release or DOI is asserted. Descriptive proxies, executed network comparisons, and proposed theory remain distinct; source-selection, licensing, human-validation, and incomplete provenance limitations remain disclosed. Visual QA is bounded layout/figure evidence, not proof of scientific validity.

A superseded generation was deliberately stopped after discovery of the Pandoc formatting defect (exit 143); [receipt](superseded-generation-receipt.json). It is not counted as a successful run. Historical checkpoints, scratch rasters and unrelated private AWS campaign observations are retained locally, outside this curated public evidence set.
