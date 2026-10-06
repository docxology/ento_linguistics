# Network robustness extension

This is an independent methodological extension of the published-core outputs, not a replacement for the four-layer generator. Keep its algorithm in model.py, corpus/sampling workflow in study.py, and plots/reporting in report.py. The entry point only selects the project and protocol.

Before computing, validate the published-core analysis receipt and independently reproduce the observed network. Every retained draw must preserve row totals, column totals and total projected edge weight. Preserve no-op trades. Never present finite correlated draws as exact independent uniform samples or their tail fractions as calibrated population p-values.

Run the numerical controls, including the independent NetworkX oracle and the exhaustive two-row state-space control. Re-execute the extension after implementation changes; bind input bytes, implementation, lock and output bytes in its receipt. Preserve the baseline and sensitivity runs separately. Preserve the distinction between the v1.1.1 baseline analyses and the extension introduced in v1.2.0.
