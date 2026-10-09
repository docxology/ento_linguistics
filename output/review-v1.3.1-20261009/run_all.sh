#!/bin/bash
# Full v1.3.1 candidate chain: regenerate, diagnostics, audit, strict render, full tests.
cd "$(dirname "$0")/../.."
EV=output/review-v1.3.1-20261009; export TMPDIR=$PWD/$EV/tmp
step() { name=$1; shift; date -u +%FT%TZ > $EV/$name.start; "$@" > $EV/$name.log 2>&1; echo "exit=$?" >> $EV/$name.log; date -u +%FT%TZ > $EV/$name.end; }
step generation uv run --no-sync python scripts/02_generate_figures.py
PYTHONPATH=src step network-reading uv run --no-sync python -m research.network_reading.study --root .
PYTHONPATH=src step custody uv run --no-sync python -m pipeline.corpus_audit --require-analysis
step render uv run --no-sync python scripts/_render_pdf_override.py --strict-templates
step full-tests uv run --no-sync python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=json:$EV/coverage.json -p no:cacheprovider -q
date -u +%FT%TZ > $EV/all.end
