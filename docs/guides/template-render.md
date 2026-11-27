# Render the canonical paper with Template

The project renderer remains the research publication build. The pinned
[Template renderer](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2)
provides a separate PDF and HTML build from the 16 canonical sections,
v1.3.1 variable snapshot, network-reading report, and original figures.
The adapter verifies the retained figure hashes, resolves the manuscript
variables, and translates the existing LaTeX figures, tables and equations
into portable Pandoc Markdown. The generated edition is distinct from
the published PDF. Its title metadata retains the project concept DOI and
omits the release-specific DOI.

Install Git, uv, Python 3.14 or later, Pandoc with matching pandoc-crossref,
XeLaTeX, BibTeX, and Poppler. Run the following from a committed code
checkout. The sparse worktree limits data transfer to paper sources and
retained figures and values, and isolates Template outputs from archival
paths in the main checkout.

```bash
set -e
source_checkout="$(pwd -P)"
scratch="$(mktemp -d)"
renderer="$scratch/template"
project="$renderer/projects/working/ento_linguistics"

git clone https://github.com/docxology/template.git "$renderer"
git -C "$renderer" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$renderer/projects/working"
git -C "$source_checkout" worktree add --no-checkout --detach "$project" HEAD
git -C "$project" sparse-checkout set --no-cone \
  '/*' '!/*/' '!/Ento_Linguistics_manuscript.pdf' '/docs/' '/scripts/' '/src/' '/research/' \
  '/output/figures/*.png' '/output/extensions/network_reading/' \
  '/output/extensions/network_robustness/network_robustness.png' \
  '/output/extensions/network_robustness/receipt.json' \
  '/output/review-v1.3.1-20261009/variables-v1.3.1-candidate.json'
git -C "$project" read-tree -mu HEAD
cd "$renderer"
uv sync --locked
uv run --no-sync python "$project/scripts/_prepare_template_manuscript.py"
uv run --no-sync python scripts/pipeline/stage_03_render.py \
  --skip-manuscript-hydration --project working/ento_linguistics
uv run --no-sync python scripts/pipeline/stage_04_validate.py \
  --project working/ento_linguistics
printf '%s\n' "$project/output"
```

Read `output/pdf/ento_linguistics_combined.pdf`, `output/web/index.html`,
and the validation and provenance files under `output/reports/`.
The commands use retained analysis. They do not run acquisition or rerun
the full corpus and network calculations. To exercise only the local
terminology and text-analysis tests, use the locked Python environment
and the [English NLTK resources](setup.md) from the project checkout.

```bash
uv run --locked --extra dev pytest tests/test_text_analysis.py tests/test_term_extraction.py
```
