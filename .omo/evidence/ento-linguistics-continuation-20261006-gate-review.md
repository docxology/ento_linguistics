# Independent continuation gate review — 2026-10-06

recommendation: REJECT

blockers:
- id: B1
  violatedCriterion: C1 — Missing/empty selected NLTK resources must fail rather than receive an analysis identity.
  observation: A zero-byte selected English stopword file receives a valid analysis signature with exit status 0. The implementation rejects an empty file inventory, not empty file contents.
  evidencePointer: src/core/nltk_resources.py:27-39; tests/test_nltk_resources.py:57-62; independent reproduction below.

originalIntent: Deeply improve accurate real-corpus analyses, visualizations, code, documentation and manuscript, then continue through complete reanalysis and rendering.

desiredOutcome: A working, evidence-bounded local paper with actual four-layer generation, truthful scientific limits, meaningful failure controls, reproducible content custody and readable rendered artifacts. No external publication or universal scientific certification is implied.

userOutcomeReview: The actual current numerical outputs and manuscript satisfy the descriptive local-paper outcome. However, one explicitly required resource failure boundary remains incomplete. The rejection is confined to that boundary; it is not a claim that the current installed resource contents or current numerical exports are empty or invalid.

## Criteria and direct evidence

Narrative requirements are assigned identifiers here, rather than inventing additional acceptance requirements.

- C1 — Selected NLTK inputs bind signatures/receipts; missing/empty resources and falsified resource receipts fail. Changed tokenizer bytes, absent roots, empty directories and forged receipt hashes are covered by real-file/fresh-process tests, which I reran successfully. **FAIL for zero-byte English stopwords**, reproduced below. Current resource hashes and schema-2 receipt otherwise validate live.
- C2 — BHL recovery binds ordered record contents, implementation/dependencies/resources and development bounds; corruption and nonfinite inputs fail; completed eras preserve default schema and combined counts. Inspected bhl_artifact.py, public wrapper/CLI and manuscript pipeline call site. Checkpoint creation follows successful era completion and uses atomic replacement; the final manifest remains after all required pipeline stages. Reran checkpoint tests including changed-body, bounded/full separation, malformed/nonfinite/tampered results and independent literal-count comparison. Three current checkpoint result digests recompute correctly, with 996/1,237/197 documents. No blocker found.
- C3 — Actual complete generation and numerical coherence. generation-status.json records exit 0 and complete default scope; checkpointed-generation.log reaches final integrity checks. Independently validated the live manifest, full PNG decoding, registry and finite/nonempty JSON. Recomputed all eight retained numerical-export comparisons excluding only generated/analysis_signature keys; all match. All 17 PNG hashes match the preceding receipt, and current receipt hashes match current files. Independent all-file frozen-hash comparison has no mismatches. The scope digest recomputes as db68a7cf03f94e3ecc9d40da14bf4197d6ad28c0b39d1a05d008e259c5f8b765; current analysis signature is 22c9157f0bae75d48a8c4896e4dff60ebe4ebbc955a105068d0415c7dc381f39.
- C4 — Required tests and coverage. Inspected complete-tests.log and final-coverage.json: 1,769 passed, 8 external-template skips, 83 warnings; 92.000606% combined coverage, 93.386854% statements, 87.731768% branches. Independently reran `PYTHONPATH=src UV_CACHE_DIR=output/review-20261006/uv-cache TMPDIR=output/review-20261006/tmp uv run --no-sync pytest tests/test_nltk_resources.py tests/test_bhl_checkpoints.py tests/test_provenance.py -q --no-cov -p no:cacheprovider`: **17 passed, 20 retained convergence warnings, 11.41 seconds**. Counts are not treated as proof of C1; the additional counterexample exposes the missing class.
- C5 — Rendered outcome and honest scientific limits. PDF SHA-256 independently matches ab2999504a1e884a2b56311fc32d41937c8d656595741476ce0376fe9361cfb7. Inspected all four page-contact sheets (46 pages), and current pages 27 and 31 at full raster size. Seventeen figures precede references on pages 45–46; no blocking clipping observed. Final TeX log search returned no missing glyph/undefined/overfull/oversized-float diagnostic. Strict build log reaches successful completion. Methods accurately distinguish resource hashes from vendoring/restoration, complete document extraction from bounded entropy, heuristics from validation and convenience samples from population inference. Native exit 138 remains explicitly unresolved and is not counted as success.

## B1 reproduction and requested correction

Used an isolated temporary directory under output/review-20261006/tmp, copied the actual installed resources with the existing real-file test helper, then emptied only the copied `corpora/stopwords/english` file. The production resources and reviewed source were not modified. A fresh subprocess selected that directory as its sole nltk.data.path and called core.provenance.analysis_signature.

Reproduction logic:

```python
import runpy
from pathlib import Path
ns = runpy.run_path("tests/test_nltk_resources.py")
ns["_copy_resources"](temporary_resource_root)
(temporary_resource_root / "corpora/stopwords/english").write_bytes(b"")
print(ns["_signature"](temporary_resource_root))
```

Observed subprocess output:

```text
EMPTY_STOPWORDS_RESOURCE_EXIT 0
118f099d01d643dc8466270fae6a10635c4ac323417b0de3684138f5c0db7ec8
```

Expected under C1: fail visibly, with no valid analysis identity. Add a narrow real-file regression for this case and reject an empty selected English stopword resource at the resource boundary. Do not indiscriminately reject every empty ancillary file: validate the actual required resource contract. Re-review the resulting frozen source/receipt state. The existing empty-directory test does not cover this case.

## Direct programming and remove-ai-slops pass

Loaded both skills and the programming Python reference and applied them directly in read-only mode. No cleanup workflow or delegation was performed.

- Excessive/useless tests: new resource tests cover distinct content mutation, absence and empty-directory behavior; checkpoint controls cover independent recovery/invalidation/corruption outcomes. No excessive or useless new suite identified.
- Deletion-only tests or tests merely verifying requested removal: none identified in continuation additions.
- Tautological tests: no new test was counted as numerical proof merely because an output exists. Resource key/length checks are supplemented by falsified-digest rejection; a length assertion alone would not suffice.
- Implementation-mirroring/overfit tests: checkpoint resumed equality is a cache contract, not an independent scientific oracle. Literal-count comparison plus changed-text count increments supply separate behavioral evidence. Preserved negative-before logs show genuine failures, although absent-API red tests alone do not prove recovery correctness. The missing empty-file class is the specific false-confidence gap B1.
- Production extraction/parsing/normalization: resource hashing supplies a real input-custody boundary; era orchestration extraction separates recovery from numerical analysis and preserves the public wrapper. No speculative normalization or generic framework added. JSON parsing and result hashes are justified at the cache boundary.
- Programming maintenance NOTES: generic Any signatures remain in provenance and recursive JSON dictionaries in bhl_artifact do not statically encode era-result shape. Large legacy modules remain. These are maintenance limits, not additional blockers under the stated criteria. No typecheck/security certification is asserted.
- Report coverage: inspected docs/review_20261005.md, docs/review_20261006.md, the earlier gate report, and evidence-directory inventory. The earlier gate explicitly covers programming/remove-ai-slops perspectives. The continuation executor report does not contain an explicit skill-perspective matrix; no separate continuation code-review report or notepad path was supplied/found in those directories. My direct pass supplies that coverage. Missing report prose itself is not a blocker.

## Checked artifact paths

- README.md; docs/AGENTS.md; docs/development_workflow.md; docs/reproducibility.md; docs/standards_compliance.md; docs/validation_guide.md; docs/manuscript_style_guide.md
- docs/review_20261005.md; docs/review_20261006.md; .omo/evidence/ento-linguistics-local-revision-gate-review.md
- src/AGENTS.md; src/core/AGENTS.md; src/pipeline/AGENTS.md
- src/core/nltk_resources.py; src/core/provenance.py; src/pipeline/bhl_artifact.py; src/pipeline/bhl_analysis.py; src/visualization/manuscript_figures.py; related analysis/statistics/parallel diffs
- tests/test_nltk_resources.py; tests/test_bhl_checkpoints.py; tests/test_provenance.py
- docs/manuscript/03_methods.md; S01a_text_and_extraction.md; S01b_analysis_infrastructure.md; 06_conclusion.md; rendered remaining manuscript sections
- output/review-20261006/final-source-scope.json; manual-qa.json; final-artifact-checks.json; final-execution-inputs.json; generation-status.json; generation-attempts.json
- output/review-20261006/checkpointed-generation.log; final-pdf-build.log; complete-tests.log; final-coverage.json; environment-dev-check.log; checkpoint-negative-before.log; nltk-negative-before.log
- output/review-20261006/compare_replay.py; check_artifacts.py; freeze_scope.py; numerical-replay.json; previous-artifacts/**/*.json
- output/review-20261006/pdf-contact-1.png through pdf-contact-4.png; final-pdf-pages/page-27.png; final-pdf-pages/page-31.png
- output/.checkpoints/bhl/*.json; output/data/analysis_manifest.json and its complete current inventory; output/figures/figure_registry.json and all registered PNGs
- output/pdf/ento_linguistics_combined.pdf; ento_linguistics_combined.log

## Exact evidence gaps and limits

No fresh complete suite, full BHL recomputation or independent full PDF rebuild was run by this reviewer; root owns heavy execution and retained logs were inspected. Live hashes/receipts, targeted tests and the additional negative control were independently executed. Contact sheets do not establish that every small figure label was read at full size. Earlier figure visual QA is reusable only because byte identity was independently verified. No separate numbered original criteria, continuation code-review report or notepad was supplied. Human sense/framing annotation, relevance/license review, full sidecar reconciliation and causal validation remain explicitly unperformed.

NOTE: generation-attempts.json still labels the earlier retry as running, while the dated continuation report identifies it as interrupted. The completed run has separate generation-status.json with exit 0; this stale historical status is a documentation note, not another blocker.

The status command returned ULW_LOOP_PLAN_MISSING, so the required fallback evidence path is used. No reviewed source, test, corpus or manuscript file was edited. Temporary real-file test fixtures were isolated. Memory search found no relevant project entry and supplied no facts to this verdict.
