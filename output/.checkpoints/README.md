# Recovery checkpoints

`bhl/` stores completed-era results bound to ordered records, code/dependency/resource signatures, development bounds and result digests. The generator reuses matching completed eras and rejects corrupt matching checkpoints. `pipeline_checkpoint.json` is a retained generic earlier checkpoint, not the current four-layer completion receipt.

Preserve recovery state. A partial or completed-era checkpoint does not establish final generation success. For a deliberate cold recomputation, preserve the prior results and isolate reusable caches as described in workflow.

See [output map](../README.md), [workflow](../../docs/guides/workflow.md), [validation](../../docs/guides/validation.md), and [captured verification](../../docs/reference/verification.md).
