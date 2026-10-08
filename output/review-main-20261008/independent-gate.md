# Independent candidate gate review

recommendation: APPROVE

candidate: c3b8574589775d52ecf917dd58c8dd759a129bc9

baseline: a5d8e27 (includes editorial commit fe9ba7e in reviewed delta)

blockers: []

originalIntent: Continue the earlier manuscript thread, tighten the unpublished draft with strict accuracy review, and prepare the accumulated changes for main. The separate private AWS campaign is outside this candidate audit.

desiredOutcome: A coherent, readable, explicitly unpublished 1.2.2-dev paper with corrected figures and labels, source-bound values, preserved scientific evidence and published release identity, and reproducible software verification.

userOutcomeReview: The candidate satisfies this bounded outcome. No demonstrated criterion failure was found. This approves the exact candidate for the requested repository integration; it is not a scientific-validity certificate, a new DOI/release approval, or verification that a push has occurred.

## Scope and criteria

Review was read-only in the locked detached worktree `../ento_linguistics-review-20261008`; HEAD was independently checked. The candidate remained clean after runtime checks. Only this report was written in the coordinator checkout. `omo-agent-toolkit ulw-loop status --json` returned ULW_LOOP_PLAN_MISSING, so the required fallback evidence location is used.

Criterion IDs below label the supplied brief and repository requirements; they are not invented additional product requirements.

- C1: Correct category composition, weighted overlap hierarchy, label placement and printed counts, consistent with captions and real exported data.
- C2: Regenerate affected artifacts, validate matching content receipts, and strictly render without unresolved values or toolchain failure.
- C3: Preserve numerical evidence and archived publication identity; distinguish unpublished draft, descriptive proxies, executed comparisons and proposed validation/theory.
- C4: Real tests and negative controls; combined statement/branch coverage at least 90%.
- C5: Inspect rendered figure/PDF readability and evidence rather than trusting success summaries.

## Directly reproduced evidence

Commands were run from the review worktree using the coordinator's existing interpreter with `uv run --no-project --python ../ento_linguistics/.venv/bin/python`, `PYTHONPATH=src`, and `PYTHONDONTWRITEBYTECODE=1`. No environment sync or heavy regeneration was performed.

1. `python -m pytest tests/test_concept_visualization.py tests/test_rendering.py tests/test_manuscript_variables.py --no-cov -p no:cacheprovider --basetemp=/Volumes/GitVault/Local/ento-gate-c3b857-tests`: **143 passed in 7.14s**, exit 0. This includes real Pandoc conversion, missing-extension strict failure, blocked-label handling, geometry, offset iterator, and rare-category cases.
2. Direct in-memory source mutations removed `ann.update_positions(renderer)` and separately removed offset-iterator materialization from `place_labels`. Real Matplotlib figures then failed the expected label-presence condition in both controls. No on-disk source was changed. A missing `NULLNET_MISSING` token raised SystemExit under strict substitution.
3. Recomputed all **35 source-scope hashes**, the analysis signature, and ran `validate_analysis_manifest` and `validate_generated_artifacts`: PASS. Signature is `d30c303d6764ead8cc322145f5b9e67ee754beba06ad5f61700e67c423284aac`.
4. Ran `research.network_robustness.receipt.validate_receipt` for both exact protocols. This includes reconstruction of the observed graph and replay of summaries from retained draws. Both PASS. Both `chain_statistics.npy` files also match baseline a5d8e27 bytes.
5. Compared the ten listed numerical JSON exports against a5d8e27, excluding only receipt signatures and generation timestamps: equal. For BHL and arXiv, direct diff confirms the only changes are `corpus_fingerprint.analysis_signature` and `generated`. All **17 PNG files** also equal the coordinator's retained `pre-contract-artifacts/output/figures/` bytes.
6. Reconstructed concept categories from `output/data/extracted_terms.json`: strengths rounded to two decimals are biological individuality 0.25, social organization 1.08, reproductive biology 0.29, kinship systems 0.09, resource economics 0.80, behavioral ecology 1.45. These match Figure 10. Independently counted individuality classes: 504 hyphenated compounds, 19 single words, 3 digit-containing terms; these match Figures 8 and 9.
7. Draft PDF hash independently equals `071a42aa8ee8a4c59363171325ddae74853e8152f0b8d762fd13d4957d6e0d12`. Published `Ento_Linguistics_manuscript.pdf` hash equals `098953e2594fffc94c347051b7b28cce631eba6820a52381d8cda968718da8c3`. `pdftotext -layout` produces 49 pages, unpublished 1.2.2-dev cover identity, and no unresolved template tokens, literal `{,}` or replacement glyphs. Final TeX log has no Overfull, undefined, or Missing character diagnostics.
8. Independently hashed all 49 retained `verified-page-XX.png` rasters against `pdf-checks.json`; all match. Direct visual review covered contact sheets 1–7 (all 49 layouts) and full-size page 21 (classification and hierarchy). The coordinator's broader full-size inspection is separately recorded in `manual-qa.json`; this reviewer does not claim to have repeated that entire full-size scope. No clipping/collision defect was observed in the inspected surfaces.
9. Read final generation/render/test logs and receipts, including superseded failure history. Full-suite log ends **1820 passed, 8 skipped, 83 warnings**; independently parsed coverage totals give **91.999405% combined**, **93.439070% statements**, **87.568223% branches**. Generation was full/default, not a claimed cold uncached scientific replication. Deferred NULLNET warnings at generation are resolved at strict rendering.

## Programming and remove-ai-slops direct pass

Loaded both installed SKILL.md files and the programming Python reference. Inspected the changed production code, tests, manuscript and relevant caller seams. Applied the existence/deletion ladder, unnecessary abstraction, defensive normalization, boundary, dead code, duplication, performance, module-size and test-quality checks. This was an audit, so no cleanup/refactor was made.

The shared label helper serves several real figure callers; geometry initialization and reusable offsets repair real failure cases. Shared word-formation classification fixes the previously incompatible denominators. The extension variable loader converts already validated report fields into print values; it does not invent scientific results or silently substitute missing results. Large-count formatting uses native integer formatting and is tested through Pandoc. No new dependency, speculative parser, broad swallowed exception, or unnecessary production extraction was found.

Nonblocking maintenance/false-confidence notes:

- `tests/test_concept_visualization.py:1262`: the generation-weight test only checks that a PNG exists; it would not detect replacing weighted sums with degree counts. The adjacent plotting test at line 1239 feeds scores directly and only checks distinct widths. Direct source review and the independent export-to-Figure-10 check above supply the missing outcome evidence for this candidate.
- `tests/test_concept_visualization.py:1212`: the pie/grid agreement test computes independent fixture counts and inspects grid text, but only checks saved pie existence. Its name overstates the asserted comparison. The shipped Figure 9 and exported counts were directly checked here.
- `tests/test_concept_visualization.py:1159,1239`: exact display-name/title/axis wording pins create editorial maintenance burden. Meaning-bearing labels matter, but all exact prose is not needed as a regression contract.
- `tests/test_rendering.py:452`: namespace-prefix assertions inspect the constant and loader keys, not execution of the generator's deferral branch. The full generator log, source seam and strict-render result supply current candidate evidence.
- `src/visualization/concept_visualization.py:940`: nonempty terms and the five-class classifier make the empty-counter fallback and greater-than-seven-category branch unreachable. Two class-color maps at concept_visualization.py:908 and manuscript_figures.py:675 duplicate the same palette. These are cleanup opportunities, not demonstrated wrong outputs.
- `src/visualization/_style.py:91,129`: `str(key)` and `(text or '')` normalize inputs beyond declared string contracts. This is unnecessary defensive behavior for current typed callers; no candidate output error was observed.
- Existing large visualization/rendering modules remain large; some new helpers retain raw dict/Any/Optional conventions rather than the skill's stricter typed structures. No required public signature was removed. A wholesale architecture/type migration was not a success criterion and would expand this task.

Explicit overfit coverage: no new deletion-only tests or tests whose sole purpose is verifying a requested removal were found. Real geometry/rare-label/Pandoc tests can fail and do fail in retained controls. No tautological numerical assertion was treated as proof. The weak existence-only and implementation/presentation-coupled tests are identified above rather than counted as substantive proof. Production parsing/normalization and extraction were checked separately from tests.

There is no separate current-candidate code-review report. The evidence directory was inspected and the coordinator confirmed this is the single independent lane. Thus no claim is made that another report explicitly covers the same skills; this direct pass supplies that coverage. The prior editorial gate concerns a different source epoch and was not treated as current approval.

## Checked artifacts and exact gaps

Checked paths include:

- `AGENTS.md`, `docs/AGENTS.md`, `src/AGENTS.md`, `tests/AGENTS.md`, `docs/manuscript/AGENTS.md`, `src/visualization/AGENTS.md`, `src/pipeline/AGENTS.md`.
- `docs/reference/data-lineage.md`, `docs/reference/reproducibility.md`, `docs/guides/authoring.md` and changed documentation delta.
- Changed code in `src/core/{manuscript_variables,validation_utils}.py`, `src/analysis/domain_analysis.py`, `src/data/loader.py`, `src/pipeline/{rendering,simulation}.py`, `src/visualization/{_style,concept_visualization,manuscript_figures,statistical_visualization}.py`, `research/network_robustness/report.py`; relevant provenance and extension-validation consumers.
- Changed tests in `tests/test_{concept_visualization,rendering,manuscript_variables,statistics_pipeline}.py`.
- Changed numbered manuscript, bibliography, config, preamble; final PDF, generated TeX/log, numerical exports, figure registry and both extension receipts/traces/reports.
- `output/review-main-20261008/{SUMMARY.md,artifact-checks.json,source-scope.json,manual-qa.json,pdf-checks.json,generation-receipt.json,tests-receipt.json,render-receipt.json,coverage.json,final-tests.log,generation.log,render.log,custody-final.log}` and all four `*-red.log` controls plus green/control logs.
- Coordinator-only preserved `output/review-main-20261008/pre-contract-artifacts/`, `verified-page-01.png` through `verified-page-49.png`, `verified-contact-1.png` through `verified-contact-7.png`. Notepad equivalent: `SUMMARY.md` plus QA/receipt records.

Two newly added scholarship references were checked against primary publisher pages: [Grimmer and Stewart](https://www.cambridge.org/core/journals/political-analysis/article/text-as-datathe-promise-and-pitfalls-of-automatic-content-analysis-methods-for-politicaltexts/F7AAC8B2909441603FEB25C156448F20) supports problem-specific validation; [Thibodeau and Boroditsky](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0016782) concerns crime-metaphor experiments, which the manuscript explicitly does not generalize into ant-terminology evidence. This is not a complete bibliography audit.

Exact evidence gaps: full heavy generation and full suite were not rerun by this reviewer; their raw logs, hashes and downstream validators were inspected instead. Full-size every-page scientific/visual audit, complete citation audit, human validation, license/relevance reconciliation, chain-mixing proof, external publication and AWS correctness were not established or claimed. Ruff invocation failed with `No module named ruff`; no lint PASS is claimed. No configured type-checker run or security scan was established. These gaps do not contradict a stated candidate success criterion; the configured coverage gate and affected runtime tests pass. No blocker is inferred from an unrequested hardening or style preference.

Final: APPROVE exact candidate c3b8574589775d52ecf917dd58c8dd759a129bc9, with the nonblocking notes and bounded evidence scope above.
