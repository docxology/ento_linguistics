# Custody and historical reports

`corpus_audit.json` reports current stored record identity, gaps, duplicate text and optional analysis-receipt agreement. `test_results.md` (April 2026) and `validation_report.md` (September 2026) are archived generic reports, not current draft acceptance. Their original JSON companions and archived bytes retain historical scope.

Run `PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis` for current custody. Read the matching final test/render logs in the verification reference rather than inferring current success from historical report filenames.

See [output map](../README.md), [workflow](../../docs/guides/workflow.md), [validation](../../docs/guides/validation.md), and [captured verification](../../docs/reference/verification.md).
