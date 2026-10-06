# Documentation maintenance

Use [README.md](README.md) to locate the reader's task. Keep procedures in guides/, computational definitions in reference/, and canonical paper source in manuscript/.

- Setup or execution changes: update [setup](guides/setup.md) and [workflow](guides/workflow.md), checking commands against the active entry points.
- Method or result changes: trace [data lineage](reference/data-lineage.md) to source and exports before editing the manuscript.
- Paper changes: follow [authoring](guides/authoring.md); keep computed quantities as supported template tokens and render changed paper source strictly.
- Verification claims: cite an actual receipt or log and identify its captured revision. Separate combined, statement, and branch coverage.
- Navigation changes: update every incoming link, including scripts/ and tests/ documentation. Keep numbered manuscript paths stable.
- Historical execution records belong with output evidence. User documentation should describe current procedures rather than accumulate dated review narratives.

Complete a documentation change when relative links resolve, documented commands match actual interfaces, and the source/analysis/PDF changes required by its scope have been checked. Documentation-only edits to guides or reference pages do not constitute a new corpus run.
