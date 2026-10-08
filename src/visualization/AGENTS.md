# Visualization maintenance

Follow [project standards](../../AGENTS.md) and [source guidance](../AGENTS.md). Read [authoring](../../docs/guides/authoring.md) before changing paper figures or captions. Plot actual exports and disclose vocabulary selection, units, sampling, exclusions, and missing-value conventions.

The core entry point is `manuscript_figures.py`, invoked by `scripts/02_generate_figures.py`. Derive figure inventory from `output/figures/figure_registry.json`. The fixed-margin extension has its own figure and receipt outside the core generator.

Verify numerical inputs and decoded image contents, then inspect figures at their final PDF size. Registry hashes and successful decoding alone do not establish that a chart portrays the intended quantities or remains readable. Source changes require affected regeneration and a strict paper render.
