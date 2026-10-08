# Fixed-margin terminology-network robustness

This separately receipted extension tests the observed abstract network against a binary document/term reference with both incidence margins fixed. It consumes the frozen published-core artifacts and validates their receipt before analysis. Its own implementation and outputs have an independent receipt; it does not overwrite or re-certify the existing four-layer analyses.

~~~bash
uv run --no-sync python -m research.network_robustness
uv run --no-sync pytest tests/test_network_robustness_extension.py -q
~~~

The workflow independently reconstructs the top-100 network from all source-identified abstracts. It rejects disagreement with the published edge count or clustering. Curveball trades retain each document's selected-term count and each term's document frequency, including legitimate no-op transitions. Every retained draw verifies both margins and the analytical total edge-weight invariant.

The default protocol uses three fixed seeds, ten attempted-trade sweeps of burn-in, one sweep between retained draws, and 200 draws per chain. Outputs include full traces, descriptive summaries, a conditional-null figure, vocabulary-size sensitivity at 25/50/100 terms, and source/output hashes under `output/extensions/network_robustness/`.

A second run doubles burn-in and spacing, with three additional seeds and 100 draws per chain. Its artifacts and independent receipt are in `output/extensions/network_robustness/sensitivity/`. This is a protocol sensitivity check, not an attempt to select a favorable conclusion.

Read [the executed report](../../output/extensions/network_robustness/network_robustness.md). Null envelopes describe sampled conditional distributions; they are not confidence intervals for population parameters. Retained draws are finite and correlated. Between-chain agreement is diagnostic, not proof of convergence. The method does not repair retrieval selection or identify a causal framing mechanism.

Primary methods: [Strona et al., 2014](https://doi.org/10.1038/ncomms5114) and [Carstens et al., 2018](https://doi.org/10.1016/j.mex.2018.06.018).

## Publication

The extension is included in [the published paper](https://doi.org/10.5281/zenodo.23215452). The current validator decodes the NPY and PNG files, verifies shape, finite values and graph bounds, independently reconstructs the observed graph, and recomputes all JSON summary statistics from retained traces. It checks the numerical Markdown table against those summaries. Byte receipts alone do not certify numerical or scientific validity. The guard does not prove that a decoded figure portrays every value correctly or that chains have mixed.
