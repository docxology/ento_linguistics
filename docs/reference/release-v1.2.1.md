# Version 1.2.1 validation patch

[Documentation](../README.md) → Release verification

Version 1.2.1 strengthens validation of the fixed-margin network companions and updates the paper's reproducibility methods. [Paper and media archive](https://doi.org/10.5281/zenodo.23215452) · [GitHub release](https://github.com/docxology/ento_linguistics/releases/tag/v1.2.1).

The previous byte-inventory guard accepted nonempty corrupt NPY/PNG files and an altered numerical summary when their receipt hashes were updated. Real-file negative controls reproduced all three failures. The guard now decodes the artifacts, checks retained-chain dimensions, finite values and graph bounds, reconstructs the observed graph from identified abstracts, replays the JSON summaries, and checks the readable result table.

Both protocols were re-executed on all 7,540 identified abstracts: 600 primary draws and 300 sensitivity draws. Both retained arrays are byte-for-byte identical to v1.2.0. The sampling model, seeds, scientific results and conclusions are unchanged. Existing four-layer core results were validated, not recomputed. PNG decoding establishes readability, not complete visual or scientific correctness; internal agreement does not establish chain mixing or causal effects.

The verified 20-minute DAF lecture, audio and slides are retained unchanged. The companion publication note identifies the validation patch. The lecture cites the v1.1.1 baseline and discusses the extension introduced in v1.2.0.

## Executed verification

| Check | Result |
| --- | --- |
| Full suite | 1,802 passed; eight external-template skips; 83 warnings; 91.45% combined coverage |
| Final focused controls | 30 passed, including the analytical summary oracle and invalid PNG pixel stream |
| New artifact validator | 95.92% combined coverage; numerical projection model 100% |
| Final extension execution | All 900 draws re-executed; both arrays match v1.2.0 exactly |
| Manuscript | Strict Pandoc/XeLaTeX/BibTeX render; 47 pages; updated methods page visually inspected |
| Lecture companion | All 22 frozen source hashes verified; five production controls passed; video/audio/slides unchanged |
| Static checks | Ruff check and formatting passed; changed documentation links resolve |

The source-change guard rejected an intermediate sensitivity run after the PNG decoder was tightened. That failed attempt was retained separately; the final frozen-source execution and strict render completed successfully. The full suite was collected before the two final analytical/pixel-stream controls were added; the final 30-control run covers both additions and the final validator.

[Release file identities](../../output/releases/v1.2.1.json) bind the paper and six downloadable companions.

## Publication readback

All six public Zenodo downloads were rehashed successfully; all six GitHub asset digests and the PDF downloaded from GitHub main matched the release manifest. Zenodo’s latest-version endpoint identifies v1.2.1. The [publication receipt](../../output/releases/v1.2.1-publication.json) records exact file identities and source commits. A fresh post-publication LectureCreate local suite passed 1,452 tests with eight skips and 93.96% combined coverage; no lecture engine or media bytes changed.
