# Ento-Linguistics fourth-edition gate review

recommendation: APPROVE

confidence: HIGH for the bounded artifact gate

blockers: []

## Scope and originalIntent

The user wanted substantially clearer paper visualizations and stronger scholarship, followed by an exact twenty-minute LectureCreate research lecture drawing broadly on the paper, with complex systems central and Architecture, Fertilization, Expansion supporting the presentation. Markdown must accurately describe current behavior and publication status. The existing DAF voice is required; no fallback voice is permitted. This review approves the frozen local artifacts for the subsequent authorized delivery step. It does not claim a new release, Zenodo publication, independent scientific validation, or continuous listening/watching.

desiredOutcome: a readable, source-bound unpublished paper and complete 4K narrated lecture with actual motion, complete provider-timed captions, preserved numerical results, and accurate reproducibility documentation.

Candidate paper: `55011f471b5c49953fd153e064fb8de96d0e7ed4`, baseline `f07b732f6fa11cf96c6a0c6d1bba7306188d0adc`, inspected in `/Volumes/GitVault/Local/worktrees/ento-lecture-v4-paper-review` (P).

Candidate lecture: `70b5b3d8dd29eedf95807d68ed0380acdb2a319c`, baseline `22c51cd90c61eae544773d54f76f6c3ee761375d`, inspected in `/Volumes/GitVault/Local/worktrees/ento-lecture-v4-lecture-review` (L).

Both candidates were independently checked as clean, detached, locked worktrees. No source, candidate, credential, or media file was modified. The only writes are this report and its external copy. `omo-agent-toolkit ulw-loop status --json` returned `ULW_LOOP_PLAN_MISSING`; the coordinator assigned this external fallback evidence root.

Artifact roots used below:

- E: `/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/review-lecture-v4-20261008`
- V: `/Volumes/GitVault/Username/docxology/Private/LectureCreate/output/ento_linguistics_v4`
- Q: `/Volumes/GitVault/Username/docxology/Private/LectureCreate/output/review-ento-v4-20261008`
- X: `L/examples/ento_linguistics`
- R: `X/verification/20261008-v4`

## userOutcomeReview and criteria

| Criterion | Result | Evidence and direct verification |
|---|---|---|
| C1: improve paper figures without changing numerical results | ACHIEVED | Reviewed plotting/style/caption diffs. Paper pages 11 and 14 show the topology plus ten ranked observed counts, and six aligned horizontal domain panels. Independently compared all eight named JSON exports with the baseline: changes are limited to `generated` and `corpus_fingerprint/analysis_signature`; four exports are entirely equal. Focused tests reproduce independent edge counts/tie order and domain counts/missing CACE. |
| C2: strengthen relevant scholarship and preserve scientific distinctions | ACHIEVED | Reviewed `docs/manuscript/05_discussion.md`, `07_related_work.md`, `references.bib`, lecture narration and authored plates. Three graph meanings, heuristic scores, conditional margins, theoretical analogies and proposed experiments remain distinguished. Checked the four primary bibliographic records and substantive context against accessible primary sources listed below. |
| C3: broad paper coverage, complex-systems focus, supporting theme | ACHIEVED | Read the complete narration and slide construction. All six domains, four layers, extraction, entropy, CACE, fixed-margin comparison, discourse, limits and future validation appear. All 28 encoded slide states were inspected via `V/encoded_qa/contact-1.png` through `contact-5.png`; the theme frames units, exchange and validation rather than displacing analyses. |
| C4: exact 20-minute 4K lecture with real DAF speech and actual motion | ACHIEVED | Independently hashed final MP4 and ran ffprobe: video/audio duration 1200.000000 s, 3840×2160, 25/1 fps. All 28 PCM clips are non-silent at 48000 Hz, match their alignment audio/text hashes, and total 1103273 ms. Renderer explicitly rejects non-ElevenLabs choice. Eight scene file hashes match receipts; three frames independently decoded from every scene differ. |
| C5: preserve every narrated sentence and readable timed captions | ACHIEVED | All 28 authored narration strings occur in narration.md. Normalized words match all 307 cues and each provider alignment. Loaded actual `PipelineResult.from_manifest`, ran `validate_coverage` successfully, then removed first cue and reproduced `CaptionError: Transcript does not contain the complete narration`. Encoded contact sheets show a separate readable two-line caption band. |
| C6: tests, coverage, strict render and custody | ACHIEVED | Raw public log ends 1822 passed/8 skipped; independently recalculated coverage from totals as 12402/13479 = 92.009793%. Private raw gzip log ends 1455 passed/8 skipped; totals 11813/12573 = 93.955301%. Receipts and logs establish successful full/default generation, custody and strict render; static-check receipts bind successful Ruff, format, mypy and MkDocs runs. Focused candidate tests passed as described below. |
| C7: preserve publication identities and current Markdown accuracy | ACHIEVED for candidate artifacts | Current paper/lecture are explicitly unpublished 1.2.2-dev; archived v1.2.1 is distinct. Top-level PDF is outside the baseline-to-candidate changed-file set. Both extension trace files are also unchanged in that diff. Reviewed changed README/workflow/verification/AGENTS guidance against renderer and recorded outputs. Source provenance binds the exact candidate paper commit and PDF. |
| C8: push authorized updates to main | PENDING DELIVERY, not a pre-delivery artifact blocker | Live `git ls-remote origin refs/heads/main` still returned public baseline f07b732f and private baseline 22c51cd during review. Coordinator must push approved candidates and read back remote heads before claiming this delivery step complete. No release publication is authorized by this gate. |

## Artifact authentication and QA matrix audit

Independently computed paper PDF SHA-256 `686f1775d4d92e5946e2bdd3c3fa354e9d6f0e904cf1872ef7512537503e16fc` and video SHA-256 `edcd3ea431a337ea535f5df72b1d103036e7b0c9fdfe757d25c666d1f59d903a`; both match receipts. All 68 frozen inputs plus eight authored source hashes in `X/sources/provenance.json` match actual bytes.

Audited every row of `E/qa-matrix.json`:

1. Regeneration/numerical regression: `generation-receipt.json`, `generation.log`, `artifact-comparison.json`; independently reproduced the eight baseline comparisons.
2. Public suite/coverage: `tests-receipt.json`, `full-tests.log`, `coverage.json`; terminal results and totals verified.
3. Custody/strict render: `render-receipt.json`, `custody.log`, `render.log`, `pdf-checks.json`; PDF identity verified.
4. Paper layout: `manual-paper-qa.json`; all 49 page capture hashes verified. Directly viewed full pages 11/14 and contact sheets 4/7. Other paper pages rely on the coordinator's bounded inspection, not a claim of a second all-page visual pass.
5. Private suite/static checks: `R/corrected-tests-receipt.json`, `R/tests.log.gz`, `R/coverage.json`, `R/static-final-receipt.json`; read real logs and receipts.
6. Real speech/timeline: `V/lecture_receipt.json`, `audio-source-checks.json`, actual WAV/alignment files and final MP4; independent hash, PCM and duration checks described above.
7. Negative controls: `Q/production-negative-controls.json`, `tampered-source-negative.log`; the latter shows rejection of changed terminology_network.png before voice selection. Missing-cue rejection independently rerun against actual persisted output.
8. Slides/handout/motion/decode: `V/manual-final-qa.json`, `full-decode-receipt.json`, `logs/decode-progress.txt`, encoded and motion capture receipts; raw decode ends frame=30000, dup_frames=0, drop_frames=0, progress=end. All 28 encoded PNG hashes and all 28 handout PNG hashes verified. Directly inspected handout contacts 1/5 and the new feedback/validation motion contacts. Independently decoded three times from every one of eight actual scene clips.

## Direct code and overfit/slop review

Loaded `omo:remove-ai-slops`, `omo:programming` and `omo:review-work` from the installed 5.1.8 skills. Read root/applicable AGENTS guidance. Independently inspected the changed production/test diffs, including public `_style.py`, `concept_visualization.py`, `manuscript_figures.py`, `test_concept_visualization.py`, `test_review_controls.py`, private `render.py`, `slides.py`, `animations.py`, and `test_ento_revision.py`, with neighboring caption/production contracts.

Explicit criterion coverage: no deletion-only tests, tests merely proving removal, tautological new tests, mock-produced green outputs, excessive duplicate tests, or new implementation-mirroring numerical expectations were found. Plot tests use fixed independent counts and missing-value outcomes. Font tests exercise actual measured fit and both horizontal/vertical rejection. Credential tests use real temporary files with distinct malformed cases, including absent/empty/duplicate assignments, and restoration of environment state. They were inspected without reading local credential values. Source authentication, minimal literal credential parsing, and measured text wrapping serve stated requirements; no unnecessary production extraction/normalization was found in the changed code. Existing caption normalization implements token-completeness checking and is supplemented by actual source/alignment hashes.

Representative paths traced: observed-pair ranking with ties; missing domain CACE; real persisted lecture/caption validation. Edge/failure classes checked: absent scoring inputs, rank ties, missing/empty/malformed/duplicate credential assignments, horizontal overflow, vertical overflow, missing cue, source tamper and non-ElevenLabs rejection. No error swallowing or dependency expansion was introduced. Public API signatures/documentation remain compatible.

Focused commands ran in review worktrees with main-checkout venv interpreters and candidate PYTHONPATH, `PYTHONDONTWRITEBYTECODE=1`, no pytest cache and no coverage writes:

- Public: `uv run --no-project --python <public-main>/.venv/bin/python python -m pytest tests/test_concept_visualization.py -k 'observed_pair_ranking or domain_horizontal' --no-cov -p no:cacheprovider -q`: 2 passed, 78 deselected.
- Private: same pattern with private venv, `tests/test_ento_revision.py -k measured`: 1 passed; real success, horizontal and vertical failure inputs.
- Real `PipelineResult.from_manifest` and `validate_coverage`: complete cue set accepted; removed first cue rejected.

Nonblocking maintenance note: `render.py` retains an unreachable Edge configuration branch after rejecting every backend other than ElevenLabs. It does not enable fallback or violate C4. The large `slides.py` is predominantly bounded authored content; its size is not a criterion-linked defect here.

## Exact evidence gaps and limits

- No separate code-review report or notepad path was supplied or located among top-level files in E, Q or curated R. Therefore prior report coverage of programming/slop checks cannot be confirmed. This report supplies the direct complete skill-perspective pass; the missing separate report is not a blocker under the gate rule.
- No independent listening/transcription or continuous-video inspection was performed. PCM/alignment identity and bounded decoded captures support the stated gate, not a perceptual voice-quality certification.
- Full generation/full suites were not rerun, as explicitly scoped. Their real terminal receipts, logs, coverage totals and frozen source bindings were inspected; focused candidate controls were rerun.
- Live remote main heads still require the authorized push/readback. This approval must not be described as completed remote delivery.

## Scholarship consulted

The manuscript's bounded mechanistic interpretations agree with these primary records, without implying that they validate lexical causation:

- [Couzin 2009](https://www.sciencedirect.com/science/article/pii/S1364661308002520)
- [Feinerman and Korman 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5226334/)
- [Gordon 2014](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1001805)
- [Greene, Pinter-Wollman and Gordon 2013](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0052219)

Initial direct PubMed/PMC opens returned sparse/challenge pages; publisher/search-indexed primary records supplied the bibliographic and interpretive checks. No credentials or production APIs were accessed.
