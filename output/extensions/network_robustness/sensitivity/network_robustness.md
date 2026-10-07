# Fixed-margin network robustness extension

This extension was introduced in the published v1.2.0 paper and supplements its original descriptive network analysis. It independently reconstructs the observed network from every source-identified abstract, then randomizes the binary document/term matrix using Curveball trades. Each document keeps its selected-term count, and each term keeps its document frequency. The total projected edge weight is an analytical invariant and is checked on every retained draw.

## Protocol and results

7540 identified abstracts; 100 frequency-ranked domain-assigned terms; three seeds; 100 retained draws per chain, after 20 attempted-trade sweeps of burn-in, with 2 sweep(s) between draws. A sweep is one attempted trade per document, including no-ops.

| Statistic | Observed | Null mean | Central 95% null envelope | R-hat |
| --- | ---: | ---: | ---: | ---: |
| edges | 4232 | 4518.48 | 4483.48–4550.05 | 0.9989 |
| clustering | 0.894841 | 0.932134 | 0.927812–0.936265 | 1.0005 |

The envelope describes the sampled conditional null, not uncertainty about the observed estimate. R-hat compares retained-chain variances; it is a diagnostic and does not prove mixing. Empirical tail fractions are available in the JSON but are not reported as confirmatory p-values. The 25/50/100-term sensitivity summaries condition on the same frequency ranking.

## Interpretation

High density and clustering must be assessed against the frequencies and document sizes that can generate them. This extension supplies that comparison. A departure identifies structural organization in this retrieved vocabulary; it does not identify author intent, biological command, or a causal effect of language. The model conditions on the selected top-frequency terms and the convenience corpus, rather than correcting retrieval or proxy validity.

[Curveball primary method](https://doi.org/10.1038/ncomms5114) · [Randomization framework](https://doi.org/10.1016/j.mex.2018.06.018)

## Reproduce

From the repository root: `uv run --no-sync python -m research.network_robustness`. The extension validates the existing published-core receipt before reading input, fails if independent reconstruction differs, and writes its own input/output hashes to receipt.json. It does not relabel cached core results or overwrite the published PDF. The retained draw array supports independent numerical replay and alternative diagnostics.
