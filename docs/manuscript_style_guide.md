# Manuscript conventions

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
PYTHONPATH=src uv run python -m pipeline.corpus_audit --require-analysis
uv run python scripts/_render_pdf_override.py --strict-templates
~~~

The final receipt must match the current sources, corpus, selected NLTK resources and registered artifacts. A successful render establishes artifact coherence, not scientific validity. See reproducibility.md for unresolved custody, relevance, license and annotation limits.
