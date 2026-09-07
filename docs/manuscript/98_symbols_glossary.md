# Symbols and Notation Glossary {#sec:glossary}

This glossary defines the mathematical notation and domain-specific terminology used throughout the manuscript.

## Mathematical Notation

| Symbol | Description | First Use |
|--------|-------------|-----------|
| $T$ | Raw text corpus (collection of scientific documents) | Sec. \ref{sec:methodology} |
| $T_{\text{normalized}}$ | Text after normalization preprocessing | Sec. \ref{sec:methodology} |
| $T_{\text{tokenized}}$ | Text after domain-aware tokenization | Sec. \ref{sec:methodology} |
| $T_{\text{lemmatized}}$ | Text after lemmatization | Sec. \ref{sec:methodology} |
| $\mathcal{T}_d$ | Set of terms classified in domain $d$ | Sec. \ref{sec:methodology} |
| $\theta$ | Relevance threshold for term inclusion | Sec. \ref{sec:methodology} |
| $G = (V, E)$ | Terminology network (graph with vertices and edges) | Eq. \ref{eq:network_edge_weight} |
| $\phi$ | Relationship threshold for edge inclusion | Sec. \ref{sec:methodology} |
| $w(u,v)$ | Edge weight between terms $u$ and $v$ (normalized co-occurrence) | Eq. \ref{eq:network_edge_weight} |
| $n$ | Corpus size (total words or documents) | Sec. \ref{sec:methodology} |
| $m$ | Number of identified terms after extraction | Sec. \ref{sec:methodology} |
| $d$ | Number of Ento-Linguistic domains (fixed at 6) | Sec. \ref{sec:methodology} |
| $S(t)$ | Term extraction score combining TF-IDF, domain relevance, and linguistic features | Sec. \ref{sec:methodology} |
| $H(t)$ | Semantic entropy of term $t$ in bits (Shannon entropy over usage-context clusters) | Eq. \ref{eq:semantic_entropy} |
| $H^*$ | High-entropy threshold (2.0 bits, $\geq 4$ equiprobable senses) | Eq. \ref{eq:semantic_entropy} |
| $p_i$ | Empirical proportion of contexts assigned to semantic cluster $i$ | Eq. \ref{eq:semantic_entropy} |
| $k$ | Number of semantic sense clusters ($k$-means, $k = \max(2,\min(k_{\max}, n{-}1, \lfloor\!\sqrt{n}\rfloor))$; $k_{\max}=5$, $n=|C_t|\geq 3$; $k < n$) | Eq. \ref{eq:semantic_entropy} |
| $A(t)$ | Ambiguity score based on contextual entropy and meaning dispersion | Eq. \ref{eq:semantic_entropy} |
| $w_{AB}$ | Overlap coefficient (Szymkiewicz--Simpson) between concept sets $A$ and $B$ | Eq. \ref{eq:overlap_coefficient} |
| $\text{Clarity}(t)$ | CACE Clarity score: $\max(0, 1 - H(t)/\log_2 10)$ | Eq. \ref{eq:cace_clarity} |
| $\text{Appropriateness}(t)$ | CACE Appropriateness score (penalizes anthropomorphic terms) | Eq. \ref{eq:cace_appropriateness} |
| $\text{Consistency}(t)$ | CACE Consistency score: mean pairwise cosine similarity of context vectors | Eq. \ref{eq:cace_consistency} |
| $\text{Evolvability}(t)$ | CACE Evolvability score: proportion of biological scale levels in contexts | Eq. \ref{eq:cace_evolvability} |
| $\mathcal{A}$ | Set of anthropomorphic terms (queen, king, slave, worker, soldier, nurse, ...) | Eq. \ref{eq:cace_appropriateness} |
| $F(D, T)$ | Discursive framing network function for domain $D$ and term set $T$ | Supplemental Eq. \ref{eq:discursive_framing} |
| $M_{ij}$ | Cross-domain mapping strength between domains $D_i$ and $D_j$ | Supplemental Eq. \ref{eq:cross_domain_mapping} |
| $\Delta G(t)$ | Temporal network evolution (graph change over time) | Supplemental Eq. \ref{eq:temporal_network_evolution} |
| $B$ | Markov Blanket boundary of a system | Supplemental Eq. \ref{eq:markov_blanket} |
| $\mu$ | Internal states (conditionally independent of external given blanket) | Supplemental Eq. \ref{eq:markov_blanket} |
| $\eta$ | External states | Supplemental Eq. \ref{eq:markov_blanket} |

## Theoretical Terms

| Term | Definition | Context |
|------|------------|---------|
| **Active Inference** | A corollary of the Free Energy Principle stating that agents act to fulfill the predictions of their generative models. | Sec. \ref{sec:introduction} |
| **CACE** | Clarity, Appropriateness, Consistency, Evolvability — four-dimensional meta-standard for evaluating scientific terminology. | Sec. \ref{sec:methodology} |
| **Generative Model** | A probabilistic model of how sensory data is generated from latent causes. | Sec. \ref{sec:discussion} |
| **Markov Blanket** | The statistical boundary that separates independent internal states from external states, formally defining the individual. | Sec. \ref{sec:supplemental_analysis} |
| **Semantic Entropy** | Shannon entropy $H(t)$ over the cluster distribution of a term's usage contexts; quantifies terminological ambiguity. | Sec. \ref{sec:methodology} |
| **Stigmergy** | A mechanism of indirect coordination where agents modify the environment to stimulate the actions of others. | Sec. \ref{sec:introduction} |
| **Superorganism** | A colony-level entity whose Markov Blanket encompasses multiple organisms; not merely metaphorical but a formal individuality claim. | Sec. \ref{sec:introduction}; Sec. \ref{sec:experimental_results} |
| **Variational Free Energy** | An information-theoretic quantity that bounds the surprise of a model; biological systems minimize this to maintain integrity. | Sec. \ref{sec:discussion} |

## Pipeline Modules

| Module | File | Function |
|---|---|---|
| Text Processing | `src/analysis/text_analysis.py` | Tokenization, normalization, feature extraction |
| Term Extraction | `src/analysis/term_extraction.py` | Domain-aware terminology identification |
| Semantic Entropy | `src/analysis/semantic_entropy.py` | Per-term $H(t)$ computation via TF-IDF + $k$-means |
| CACE Scoring | `src/analysis/cace_scoring.py` | Four-dimensional terminology evaluation |
| Domain Analysis | `src/analysis/domain_analysis.py` | Per-domain framing and ambiguity analysis |
| Conceptual Mapping | `src/analysis/conceptual_mapping.py` | Cross-domain concept graph construction |
| Rhetorical Analysis | `src/analysis/rhetorical_analysis.py` | Framing detection and argumentative scoring |
| Discourse Analysis | `src/analysis/discourse_analysis.py` | Discourse pattern classification |
| Statistics | `src/analysis/statistics.py` | Statistical validation utilities |
| Visualization | `src/visualization/concept_visualization.py` | Network and domain-specific figure generation |


