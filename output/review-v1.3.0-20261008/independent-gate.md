# Independent v1.3.0 final gate — 2026-10-08

recommendation: APPROVE

blockers: []

originalIntent: Improve the public Ento-Linguistics paper, methods, scholarship and documentation, and deliver its matched twenty-minute DAF lecture with an effective opening graphical abstract. Complexity/Complex Systems is the organizing subject; Architecture/Fertilization/Expansion supports it. Preserve scientific history and archived DOI identities.

desiredOutcome: A coherent v1.3.0 research edition and matched fifth-edition 4K lecture, slides, audio and methodological companions, eligible for the separately authorized publication step.

userOutcomeReview: The frozen candidates and exact prepared release assets satisfy this bounded software/content/media outcome. The opening abstract visibly distinguishes biological processes from observed discourse, all six domains are represented, and the new methods expose the complete finite representation grid without claiming biological complexity or causal validation. No specific stated success criterion is demonstrably violated.

## Scope and identities

- Public review tree P: `/Volumes/GitVault/Local/worktrees/ento-v130-gate-20261008`; HEAD `d18bb1812c37cb7bf802e690d1b8d1bed2738a26`; baseline `470b4ed59d5a2c903feb73b37dfda3f27eb3683f`.
- Private review tree L: `/Volumes/GitVault/Local/worktrees/lecture-v5-gate-20261008`; HEAD `a3669c1eea841e9689202f7cd080bd60f07c1310`; baseline `e01a9e3ed732bd7eadd2c00b69564d063b92a232`.
- Both trees were clean on inspection and remain clean. Source and diffs were read from these trees. No candidate changes, credential reads, publication, push, or full regeneration occurred.
- Lecture scientific source commit `5b75355f79100cc2485c95854146c362310a9f60` differs from public candidate only by two scholarship receipt files, independently confirmed with Git.
- Paper SHA-256 `c6588539b0ca5e11aaf5fd9ca32037a599bc0a5d171da69c31dd9c6abdba48d3`; independently verified for public top-level/current render and bundle identity.
- Analysis signature `266f1e4c7c2e506270d371b8fd1811d8e24129e09c5ccb7607cb77629c4e579d`.
- Lecture bundle SHA-256 `a8eaa8796bf557a1292ad78134ab94efa189d1d83803a718414cb45752f89eaf`; all nine authored hashes and 103 finite copied-source hashes independently replayed.
- Actual final video SHA-256 `285d30fb4fe0a5c652904114ca4a8ea6bc907c00794c68e0e522978ea12b6ee7` independently replayed.
- `omo-agent-toolkit ulw-loop status --json` returned `ULW_LOOP_PLAN_MISSING`. The explicit assignment's sole permitted report destination overrides the generic fallback location.

## Criteria and reproduced evidence

| Criterion | Result and evidence |
|---|---|
| C1 — Accurate, complete declared 4 by 5 diagnostic on identified abstracts | PASS. Imported `P/research/network_reading/study.py` explicitly and ran `ensure(P)` successfully: 7,540 documents, 20 cells. A separate set-based oracle, without NetworkX or matrix projection, independently recomputed every cell's edge count, local clustering and document coverage. All matched. Last cell has 1,191/4,950 edges, density 0.2406060606, clustering 0.8619685933 and 7,314 covered documents. |
| C2 — Real invalid-input/custody controls and stated coverage floors | PASS within declared measured scope. Re-ran `tests/test_network_reading.py` with `--no-cov -p no:cacheprovider` and bytecode disabled: 11 passed, including invalid protocol/incidence inputs. Read self-hashed number, incomplete inventory and tiny-PNG receipts and traced their rejection paths in `ensure`. Read actual compressed private renderer traceback logs: image tamper and self-hashed version mismatch reject before voice selection. Read final-cue-removal and bundle-drift test. Exact full-suite logs and coverage totals support public 1,833 passed/8 skipped/91.9757% combined and private 1,457 passed/8 skipped/93.9553% combined core. These full suites were not redundantly rerun. |
| C3 — Preserve earlier numerical evidence and distinguish interpretation | PASS. Inspected changed numerical exports: differences are timestamps/signatures, not scientific numbers; unchanged core exports remain unchanged in Git. Independently byte-compared both retained chain arrays against baseline Git objects. Manuscript, source note and narration distinguish lexical projection, occupancy entropy, heuristic CACE, finite conditional references and proposed validation. |
| C4 — Matched research identity and historical DOI custody | PASS. Current publication config leaves DOI fields empty; prose identifies v1.2.1 DOI as archival. Public source delta after the lecture pin is receipt-only. New lecture metadata agrees with frozen provenance. Software package version versus research edition is intentionally separate. |
| C5 — Twenty-minute DAF production, actual 4K media, captions and graphical abstract | PASS for bounded media gate. Actual MP4 independently probed: 3840×2160, 25 fps, 1,200.000000 seconds, 48 kHz audio. Read 29-slide/319-cue/1,148.228-second speech receipt and complete decode receipt/progress. Independently inspected opening-final-video image, handout contact 1, final-motion contact 5, and public physical pages 10 and 13. Opening is clear and above the caption strip; the new diagnostic animation has distinct start/mid/end states and readable scientific bounds. Root's full layout/sample matrix is explicit about its bounded scope. |
| C6 — Prepared release assets preserve exact reviewed bytes | PASS. Independently hashed and size-checked all six assets against release_manifest.json, and ran ZIP testzip on both archives (12 and 27 entries). The packaged MP4 hash equals the actual production MP4. The initial packaging failure remains separately recorded; approval applies to the corrected manifested archive only. |

## Direct programming and remove-ai-slops pass

Loaded both named skills and the Python reference. Applied their review criteria without performing their modification workflow, as required by this read-only assignment.

Directly reviewed all new diagnostic production code and tests; synchronization code; render/encoder, caption typing and production changes; authored animation/slide changes; manuscript and documentation diff. The finite diagnostic, complete receipt, and source synchronization have concrete release purposes. Existing numerical loading and NetworkX/Pillow facilities are reused rather than inventing a graph or image parser. Boundary validation is necessary for the named corruption scenarios. No deletion-only tests, removal-verification tests, tautological expected values, implementation-mirroring oracle tests, pointless production extraction, or speculative normalization were identified in the changed code. The numerical test's small triangle-plus-isolate example independently distinguishes inclusive thresholds and clustering denominators. Real Git/PDF tests distinguish dirty source and mismatched committed paper bytes. The bundle-drift test observes early rejection rather than asserting an implementation call.

Maintenance NOTES, not criterion failures:

- `dict[str, Any]` report/provenance shapes offer weaker static guarantees than explicit TypedDict/data models. This is a programming-skill concern, not evidence of a wrong current artifact.
- `slides.py` retains a literal 1.3.0 source footer despite reading the version elsewhere. It matches this release but will require attention at a future version change.
- The source-identity test groups several transitions in one test; splitting would localize failures, but the scenarios are real and non-tautological.
- `study.py` combines numerical projection, custody and plotting; `_figures` has an unused root parameter. These are limited maintenance issues, not grounds to demand an unrequested refactor.
- The measured public `src` coverage excludes the separately located research extension; the private pure-core coverage similarly does not claim coverage of every example/backend. Focused tests, reconstruction, controls and rendered evidence must remain separate from headline coverage.

No standalone code-review report explicitly documenting the same skill/overfit pass was supplied or found in either scoped evidence directory. I read the directories and performed that pass directly. Thus prior-report coverage is a NOTE, not an unsupported claim of prior approval and not a blocker under the prescribed rule.

## Checked artifact paths

In P: applicable root/research/src/core/src/pipeline/tests/docs/manuscript AGENTS files; `docs/guides/authoring.md`; `docs/reference/data-lineage.md` and `reproducibility.md`; `research/network_reading/study.py`; `tests/test_network_reading.py`; changed manuscript, config, bibliography, scholarship note and renderer diff; `output/extensions/network_reading/{network_reading.json,receipt.json,network_reading.png,graphical_abstract.png}` via ensure; both retained trace arrays; top-level and rendered PDF; `output/review-v1.3.0-20261008/{SUMMARY.md,tests-receipt.json,coverage.json,full-tests.log.gz,generation-receipt.json,generation.log.gz,artifact-checks.json,network-reading-negative-controls.json,final-render-receipt.json,render-final-layout.log.gz,custody.log.gz,manual-paper-qa.json,scholarship.json,scholarship-negative-control.json}`.

In L: applicable root/examples/project/tests AGENTS files; `examples/ento_linguistics/{sync_sources.py,render.py,production.py,bottom_transcript.py,slides.py,animations.py,narration.md}` and changed tests; frozen `sources/provenance.json` plus its complete 112-entry file inventory; `verification/20261008-v5/{README.md,qa-matrix.md,tests-final-receipt.json,coverage-final.json,full-tests-final.log.gz,mypy-final.log.gz,lecture_receipt.json,production-negative-controls.json,source-png-tamper.log.gz,self-hashed-version-mismatch.log.gz,cue-negative-control.json,source-binding-checks.json,decode-receipt.json,manual-media-qa.json,opening-final-video.png}`.

Supplemental public main artifacts: `output/releases/v1.3.0/release_manifest.json` and all six manifested assets; `output/review-v1.3.0-20261008/page-10.png`, `page-13.png`; `.omo/evidence/complexity-scholarship-20261008/{README.md,final-verification.json,newman2003.txt}` (the actual projected-clustering paragraph and equation 42 support the bounded claim). Supplemental private main artifacts: `output/ento_linguistics_v5/video/lecture.mp4`; `output/review-v1.3.0-20261008/handout-contact-1.png` and `final-motion-contact-5.png`.

## Exact gaps and approval boundaries

No independent continuous auditory review, continuous viewing, or fresh full 30,000-frame decode was performed in this gate. DAF identity and full cue completeness are supported by the recorded synthesis/custody artifacts, not personal voice recognition. My visual pass sampled the named actual captures; it does not replace the root's complete layout sampling with a claim that I personally viewed all pages/slides. The source-note retrieval limitations for Ladyman and Simon remain explicit; no inaccessible full-text argument is newly certified here. No general causal, proxy-validity, convergence or external scientific approval is granted.

No standalone notepad path was supplied. No standalone prior code-review report was found; direct review supplied the required coverage. Hosted private Actions budget refusal remains a refusal, not a successful hosted run. Release upload/readback has not happened in this review and remains a subsequent publication operation. No new DOI is granted or inferred.

The first diagnostic replay accidentally imported the main-checkout module because Python placed the current directory first; it failed with a path-relative error. I corrected sys.path explicitly, printed the frozen module path, and reproduced successful ensure and independent oracle checks. A scholarship-artifact lookup in the worktree failed because those supplementary raw files live only in the main evidence directory; the corrected evidence read is identified above. Neither failed inspection is counted as a product failure or silently treated as a pass.
