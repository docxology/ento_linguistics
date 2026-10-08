# Reading a terminology network across representations

This v1.3.0 extension asks how vocabulary size and minimum shared-document counts affect an observed lexical projection. It is a deterministic representation diagnostic, separate from the fixed-margin randomized reference and from biological interaction measurements.

```bash
PYTHONPATH=src uv run python -m research.network_reading.study --root .
uv run pytest tests/test_network_reading.py --no-cov
```

The verified core receipt and identified abstracts are required first. The implementation reuses the independently reconstructed 100-term incidence and stable frequency ranking. Its declared grid has vocabulary sizes 25, 50, 75 and 100 and inclusive shared-document thresholds 1, 2, 5, 10 and 20. Every selected term remains a node, including isolates. Density uses all selected pairs; mean local clustering assigns degree-zero/one nodes zero. Components, largest-component size, isolates and document coverage are exported alongside the curves.

`output/extensions/network_reading/` holds the numerical report, sensitivity curves, graphical abstract and separate content receipt. The strict paper renderer injects `NETREAD_*` values only after input/code/lock checks, complete output-inventory checks, figure decoding and numerical replay. Missing, changed or self-hashed inconsistent artifacts fail. The graphical abstract illustrates separate biological and textual observational units; its biological arrows are schematic.

Thresholds do not discover true semantic edges. This is not a document bootstrap, uncertainty interval, additional null model, optimized community partition or scalar complexity index. Frequency selection still limits the represented vocabulary. See [complexity scholarship](../../docs/research/complexity-scholarship.md) and [methods](../../docs/manuscript/03_methods.md).
