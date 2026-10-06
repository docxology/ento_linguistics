# Independent terminal gate review — 2026-10-05

recommendation: APPROVE

blockers: []

originalIntent: Deeply review and improve the actual corpus analysis, visualizations, code, documentation, and manuscript, ensuring the local results work and claims match evidence.

desiredOutcome: An evidence-bounded local revision with reproducible descriptive results, functioning failure gates, regenerated figures/PDF, and candid scientific limitations. This is not publication approval or certification of relevance, licensing, causal validity, or human annotation.

userOutcomeReview: The frozen revision satisfies that outcome. Actual corpus inputs feed the outputs, shared-document counts replace constructed terminology edges, valid entropy estimates define statistical denominators, and figures share CACE samples with statistical exports. The manuscript describes limitations and sampling instead of presenting heuristic proxies as validated causal findings.

## Criteria and evidence

The assignment supplies narrative requirements rather than numbered acceptance criteria. These identifiers map directly to those requirements:

- C1 — Real corpus custody and cache coherence: live validate_analysis_manifest and validate_generated_artifacts calls passed against current files. All frozen source file hashes matched final-source-scope.json. Analysis signature is 1063433805bc48406589dd03a9e37b6d5f15c5379964949aaa8ebc9c9169ecfa. Abstract archive bytes and identified selection are receipt-bound; the retained custody audit explicitly reports 69 unmatched abstracts and eight repeated PMC bodies.
- C2 — Computations and claims agree: inspected term retention, document_cooccurrences, entropy propagation/status, denominator exports, shared _domain_cace_scores, BHL extraction/counting/framing, sampling fingerprints, methods, results, theory, glossary, and captions. Default BHL coverage records all 2,430 documents and 2,317,721,403 characters. Entropy remains explicitly limited to twenty candidates per era. PMC discourse sampling and overlapping exploratory groups are disclosed.
- C3 — Failure propagation and meaningful controls: independently ran tests/test_artifact_integrity.py, tests/test_provenance.py, and tests/test_review_controls.py with uv, no coverage or pytest cache writes: 34 passed in 29.74 seconds. These actually exercise malformed records, nonfinite/empty JSON, missing and extra inventory, file tampering, forged-hash invalid PNGs including valid CRC/broken pixels, real failed subprocesses, seed retention, extractor reuse, entropy reuse, invalid development limits, bounded network strokes, and missing CACE inputs. No mocking frameworks were added in these files.
- C4 — Required validation and coverage: read complete-final-tests.log and complete-final-coverage.json: 1,758 passed, eight explicitly skipped external-template tests; 91.936% combined statement/branch coverage, 93.333% statement coverage, 87.640% branch-only coverage. The configured overall 90% floor passes. Identified incorrect branch-only wording in the report and confirmed the coordinator corrected it. The complete suite was not redundantly rerun by this reviewer.
- C5 — User-visible artifacts: live PNG decoding, registry hash checks, and receipt validation passed. PDF hash matches 1cf3611197bb467f2a672d32a1732baaa608b476a3a2db47417fb67fcc738108. Final TeX log has no missing glyph, undefined reference/citation, overfull, or oversized-float diagnostics. Inspected all five figure contact sheets (17 figures), all four PDF contact sheets (46 pages), and the two final full-size methods/glossary page images. Figures and final bibliography are present; no blocking clipping/layout defect observed. Contact-sheet inspection does not imply every small label was independently read at full raster resolution.

## Direct programming and remove-ai-slops pass

Loaded both SKILL.md files and the programming Python reference. Applied review criteria directly; no cleanup or production edits were performed.

- Excessive/useless and deletion-only tests: no blocking instance in the additions. The tests exercise observable behavior and real invalid inputs, not just deleted symbols or desired source text.
- Tautological/implementation-mirroring tests: the CACE cross-surface test deliberately shares the scoring function, so it proves sample/figure agreement rather than scoring correctness; counted only for that contract. The BHL count test uses the prior independent phrase-count oracle. Extractor-reuse equivalence uses separate instances and distinct corpus slices. Seed tests are strengthened by real processed-literature frequency counts. These scopes avoid claiming numerical validity from mere equivalence.
- Unnecessary extraction/parsing/normalization: the provenance module is justified by actual input/output custody; the corpus audit is a separate read-only observable CLI. BHL per-document counters address observed memory requirements and reuse canonical classification. No speculative abstraction was necessary to reach this verdict.
- Maintenance NOTES: several large legacy modules and raw Dict/Any signatures remain; broad catches in the main pipeline wrap and rethrow rather than silently succeeding. The new visualization import of private _domain_cace_scores creates coupling, but prevents divergent scoring and does not violate the requested outcome. Generic helper typing could be strengthened in subsequent maintenance. These are not blockers under the stated criteria.
- Existing report coverage: docs/review_20261005.md contains correction and negative-control evidence but no explicit programming/remove-ai-slops coverage matrix. No separate code-review report or notepad was supplied; coordinator confirmed none exists. The evidence directory was inspected before judgment. This direct pass supplies the missing perspective, so absent prose coverage is not a blocker.

## Checked artifact paths

- docs/review_20261005.md; output/review-20261005/manual-qa.json
- output/review-20261005/final-source-scope.json
- output/review-20261005/complete-final-tests.log; complete-final-coverage.json
- output/review-20261005/frozen-final-generation.log; complete-final-artifacts.log; final-artifact-checks.json; check_artifacts.py
- output/review-20261005/complete-final-custody.log; complete-final-pdf-layout-fixed.log
- output/review-20261005/verified-figures-contact-1.png through verified-figures-contact-5.png
- output/review-20261005/verified-pdf-contact-1.png through verified-pdf-contact-4.png
- output/review-20261005/final-methods-page.png; final-glossary-page.png
- output/pdf/ento_linguistics_combined.pdf; ento_linguistics_combined.log
- output/data/analysis_manifest.json; corpus_statistics.json; domain_statistics.json; statistical_analysis.json; extracted_terms.json; concept_map_summary.json; fulltext_analysis.json
- output/figures/figure_registry.json and registered PNGs
- data/corpus/abstracts.json; provenance.json; arxiv_analysis.json; data/bhl/era_term_usage.json
- Changed source/test diffs against 7d49231b6b4ecb97b79f05aacb0cf5098be6cf08, new src/core/provenance.py and src/pipeline/corpus_audit.py, and the three new test modules named above
- docs/manuscript/01_abstract.md, 03_methods.md, 04a_corpus_and_networks.md, 04b_domain_findings.md, 06_conclusion.md, supplemental/theory/glossary rendering and captions

## Exact evidence gaps and limits

No separate original numbered criterion list, code-review report, or notepad path exists in the supplied assignment. No fresh full-suite, full BHL recomputation, external-parent integration run, or live bibliography retrieval was performed by this reviewer; those execution claims are bounded to retained logs and inspected artifacts. Static type/lint/security compliance was not a stated acceptance criterion and is not certified here. Human sense/framing validation, individual licenses, relevance annotation, full record-level PMC sidecar reconciliation, and causal inference remain unperformed and disclosed. NLTK resource archives remain unpinned. These are scientific or scope limits rather than failed local-revision criteria.

The local ulw-loop status command returned ULW_LOOP_PLAN_MISSING, so this report uses the required fallback evidence path. No reviewed source, tests, corpus, or manuscript was modified by this reviewer.

## Independent numerical cross-check

Recomputed the terminology graph using a separate document-index set per term and pairwise set intersections, directly from the 7,540 selected abstract strings and exported frequencies. It reproduced 100 nodes, 4,232 edges, and unweighted clustering 0.8948, matching concept_map_summary.json. Independently checked every domain's exported entropy mean, CACE mean, and valid-estimate denominator against statistical_analysis.json; all matched (means within 1e-12).
