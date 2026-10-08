# Analysis maintenance

Follow [project standards](../../AGENTS.md) and [source guidance](../AGENTS.md). Before changing an algorithm, reproduce its behavior with real text or independent numerical examples and inspect callers. Keep public APIs typed and document definitions and error behavior.

Read [reproducibility definitions](../../docs/reference/reproducibility.md) and [data lineage](../../docs/reference/data-lineage.md) when changing extraction, domain assignment, entropy, network statistics, framing, or CACE. Preserve the distinction between document co-occurrence and predefined category overlap, context-cluster occupancy and annotated senses, heuristic scores and validated human judgments.

Algorithm changes require affected analysis regeneration, matching receipts, figure checks, and a strict paper render. Tests must exercise legitimate zeros, insufficient observations, overlapping labels, and invalid input without masking failures.
