# Manuscript conventions

[Documentation](../README.md) → Manuscript conventions

Canonical sections live in docs/manuscript/. Corpus-derived numbers use supported double-brace template tokens; changes to prose require a fresh strict render. Match methods and captions to executable definitions rather than inferred scientific intent.

## Figures

The authoritative inventory is output/figures/figure_registry.json. Every generated PNG must have a registered label and a content hash, and every manuscript reference must resolve. Use actual figure captions and terminology from the corresponding export.

~~~latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/domain_comparison.png}
\caption{Describe the panels, computational sample and interpretation limits.}
\label{fig:domain_comparison}
\end{figure}
~~~

The renderer resolves project figure paths and flushes floats between sections. Check final pages for margin/footer collisions; pixel dimensions or a minimum plotting font do not establish readability after scaling.

Terminology edges count actual shared documents among the frequency-ranked vocabulary. Concept relationships encode configured vocabulary/category overlap. Domain entropy uses valid sentence-context estimates. CACE scores share the frequency-ranked term sample with statistics. Frame markers describe lexical matches, not independently annotated intent. BHL entropy and PMC discourse sampling must be identified separately from full-document extraction.

## Equations and citations

Describe every symbol and identify whether an equation is computed, heuristic or proposed. Entropy is Shannon occupancy entropy of TF-IDF/KMeans sentence contexts, not a validated number of senses. Explain overlapping domain memberships before presenting exploratory comparisons.

Use the shared references.bib database and existing BibTeX citation syntax. Verify new bibliographic metadata against primary records. Preserve accented names and inspect the rendered bibliography for missing glyphs. Put the bibliography last.

## Verification

~~~bash
uv run python scripts/02_generate_figures.py
PYTHONPATH=src uv run python -m research.network_reading.study --root .
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

Generation rejects any placeholder its variable map cannot resolve, except the `NULLNET_*` and `NETREAD_*` namespaces. Those values come from the separately receipted fixed-margin and network-reading extensions, which runs after the core receipt exists; the strict renderer resolves them from the extension's receipted reports and fails if any is missing.

The final receipt must match the current sources, corpus, selected NLTK resources and registered artifacts. A successful render establishes artifact coherence, not scientific validity. See [reproducibility](../reference/reproducibility.md) for unresolved custody, relevance, license and annotation limits.

## Scope of an edit

| Changed input | Required follow-through |
| --- | --- |
| Python analysis, corpus, lock, or selected NLTK resource | Regenerate affected analyses/figures, validate the final receipt, and rebuild the paper |
| Numbered manuscript, bibliography, publication config, or TeX preamble | Strict render and page checks against the existing valid analysis receipt |
| Documentation README, guide, or reference | Check links and commands; retain the existing scientific artifacts |

The published top-level PDF and Zenodo deposit are release artifacts. A local render changes neither automatically. Use the [verification reference](../reference/verification.md) to distinguish the last published file from a newly generated one.
