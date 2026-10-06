# Verification and publication

[Documentation](../README.md) → Verification and publication

This page identifies the captured 6 October 2026 revision. It is a reference to actual execution records, not a live status dashboard or a new scientific validation claim.

## Recorded checks

| Check | Captured result | Evidence |
| --- | --- | --- |
| Full/default corpus generation | Exit 0; four source layers complete | [generation status](../../output/review-20261006/generation-status.json) |
| Corpus/output coherence | Matching implementation, resources, inventories, and shared statistics | [artifact checks](../../output/review-20261006/final-artifact-checks.json), [analysis manifest](../../output/data/analysis_manifest.json) |
| Complete test suite | 1,774 passed, eight external-template skips, 83 warnings | [test log](../../output/review-20261006/complete-tests.log) |
| Coverage | 91.93% combined; 93.37% statements; 87.53% branches | [coverage JSON](../../output/review-20261006/final-coverage.json) |
| Strict paper build | 46 pages, 17 figures; page and figure inspection passed | [build log](../../output/review-20261006/final-pdf-build.log), [manual QA](../../output/review-20261006/manual-qa.json) |
| Independent final correction review | APPROVE; no criterion-linked blockers | [gate record](../../output/review-20261006/final-gate.json) |
| Zenodo public download | Exact PDF SHA-256 match | [publication receipt](../../output/review-20261006/zenodo/publication-receipt.json) |

The configured test floor is 90% combined statement/branch coverage, not a separate 90% branch-only floor. Skipped external parent-template tests are not counted as exercised standalone functionality.

A prior resource-guard revision was rejected and corrected before the final run. An earlier native generation attempt exited 138 without an established cause; that failed attempt is not counted as successful execution. The final full/default checkpoint-enabled run completed. Historical detailed records remain in Git history and output evidence; user-facing review narratives have been retired.

## Published paper identity

- [Top-level paper](../../Ento_Linguistics_manuscript.pdf)
- [Zenodo version record](https://zenodo.org/records/23193499)
- Version DOI: [10.5281/zenodo.23193499](https://doi.org/10.5281/zenodo.23193499)
- Concept DOI: [10.5281/zenodo.19574117](https://doi.org/10.5281/zenodo.19574117)
- PDF SHA-256: **4c22688cde6980fe03174779dff27cb224e547b63509ea6a0f89f5904ddc8586**

The version label is *1.1.1 (2026-10-06 revision)*. The manuscript publication metadata and the Python package version serve different purposes; one is not inferred from the other.

## Reusing evidence after a change

Source Python, the dependency lock, corpus, or selected NLTK changes require regeneration and fresh receipt validation. Manuscript content, configuration, or preamble changes require a new strict render and page checks. Documentation navigation changes do not rerun the scientific pipeline.

The recorded gate binds the reviewed source scope and PDF. Later publication-link or documentation edits should identify their own scope rather than relabel the historical gate as a fresh audit.

For a fresh run, follow [validation](../guides/validation.md). For limits on source selection, licensing, clustering, heuristics, and inference, read [reproducibility](reproducibility.md).
