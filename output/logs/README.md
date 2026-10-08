# Execution logs

Log filenames alone do not identify current execution. Associate each log with its command, exit status, source scope, inputs and matching output receipt. Dated review folders retain more specific build/test logs.

Retain stderr and nonzero failures. Preserve earlier logs before another run; never relabel them as fresh execution or suppress required-stage errors.

See [output map](../README.md), [workflow](../../docs/guides/workflow.md), [validation](../../docs/guides/validation.md), and [captured verification](../../docs/reference/verification.md).
