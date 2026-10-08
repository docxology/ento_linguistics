# Standalone paper build maintenance

Follow [output guidance](../AGENTS.md) and [directory reference](README.md). Run `uv run python scripts/_render_pdf_override.py --strict-templates` after matching receipt validation. Inspect the final TeX diagnostics and rasterized pages. The top-level published PDF and external DOI/release are distinct; a local render does not replace them.

Preserve unrelated files and historical evidence; check the tracked inventory before staging. Record command status and content identity, and distinguish current execution from an archived snapshot. See [verification](../../docs/reference/verification.md) for scope and completion evidence.
