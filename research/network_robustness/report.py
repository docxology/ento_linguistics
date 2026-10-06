"""Evidence figures and a readable report for the fixed-margin extension."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray


if TYPE_CHECKING:
    from .study import MetricSummary, Protocol

__all__ = ["write_report"]


def write_report(
    documents: int, protocol: Protocol, metrics: Mapping[str, MetricSummary], values: NDArray[np.float64], out: Path
) -> None:
    """Plot actual sampled distributions and distinguish null envelopes from intervals."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    for col, metric in enumerate(["edges", "clustering"]):
        summary = metrics[metric]
        for i, seed in enumerate(protocol.seeds):
            axes[0, col].plot(values[i, :, col], label=f"Seed {seed}", alpha=0.8)
        axes[0, col].set(
            xlabel="Retained chain draw",
            ylabel=metric.capitalize(),
            title=f"{metric.capitalize()}: retained-chain traces",
        )
        axes[0, col].legend()
        axes[1, col].hist(values[:, :, col].reshape(-1), bins=24, color="#1d6fb8", alpha=0.8)
        axes[1, col].axvline(summary.observed, color="#c1121f", linewidth=2, label="Observed")
        axes[1, col].set(
            xlabel=metric.capitalize(), ylabel="Retained draws", title="Fixed-margin conditional distribution"
        )
        axes[1, col].legend()
    fig.suptitle("Abstract terminology network: fixed-margin robustness extension", fontsize=18)
    fig.savefig(out / "network_robustness.png", dpi=220)
    plt.close(fig)
    rows = []
    for metric, value in metrics.items():
        rhat = f"{value.rhat:.4f}" if value.rhat is not None else "Undefined: zero within-chain variance"
        rows.append(
            f"| {metric} | {value.observed:.6g} | {value.null_mean:.6g} | {value.null_q025:.6g}–{value.null_q975:.6g} | {rhat} |"
        )
    text = (
        """# Fixed-margin network robustness extension

This new local extension supplements the published paper. It independently reconstructs the observed network from every source-identified abstract, then randomizes the binary document/term matrix using Curveball trades. Each document keeps its selected-term count, and each term keeps its document frequency. The total projected edge weight is an analytical invariant and is checked on every retained draw.

## Protocol and results

"""
        + f"{documents} identified abstracts; 100 frequency-ranked domain-assigned terms; three seeds; {protocol.samples_per_chain} retained draws per chain, after {protocol.burn_sweeps} attempted-trade sweeps of burn-in, with {protocol.spacing_sweeps} sweep(s) between draws. A sweep is one attempted trade per document, including no-ops.\n\n"
        + """| Statistic | Observed | Null mean | Central 95% null envelope | R-hat |
| --- | ---: | ---: | ---: | ---: |
"""
        + "\n".join(rows)
        + """

The envelope describes the sampled conditional null, not uncertainty about the observed estimate. R-hat compares retained-chain variances; it is a diagnostic and does not prove mixing. Empirical tail fractions are available in the JSON but are not reported as confirmatory p-values. The 25/50/100-term sensitivity summaries condition on the same frequency ranking.

## Interpretation

High density and clustering must be assessed against the frequencies and document sizes that can generate them. This extension supplies that comparison. A departure identifies structural organization in this retrieved vocabulary; it does not identify author intent, biological command, or a causal effect of language. The model conditions on the selected top-frequency terms and the convenience corpus, rather than correcting retrieval or proxy validity.

[Curveball primary method](https://doi.org/10.1038/ncomms5114) · [Randomization framework](https://doi.org/10.1016/j.mex.2018.06.018)

## Reproduce

From the repository root: `uv run --no-sync python -m research.network_robustness`. The extension validates the existing published-core receipt before reading input, fails if independent reconstruction differs, and writes its own input/output hashes to receipt.json. It does not relabel cached core results or overwrite the published PDF. The retained draw array supports independent numerical replay and alternative diagnostics.
"""
    )
    (out / "network_robustness.md").write_text(text)
