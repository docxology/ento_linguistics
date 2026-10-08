# Results: Corpus Analysis and Terminology Networks {#sec:experimental_results}

## Terminology Extraction Across Domains

Analysis of the source-identified headline layer yields {{CORPUS_CANDIDATE_TERMS}} candidate terms from {{CORPUS_PUBLICATIONS}} abstracts and {{CORPUS_TOTAL_TOKENS}} processed tokens. Of these candidates, {{CORPUS_DOMAIN_TERMS}} receive domain assignments. These counts exclude {{CORPUS_EXCLUDED_UNRECONCILED}} unreconciled archived strings; broad retrieval still limits relevance and representativeness.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Domain} & \textbf{Terms} & \textbf{Frequency} & \textbf{Bridging terms} \\
\hline
Unit of Individuality & {{DOMAIN_UNIT_OF_INDIVIDUALITY_TERMS}} & {{DOMAIN_UNIT_OF_INDIVIDUALITY_FREQ}} & {{DOMAIN_UNIT_OF_INDIVIDUALITY_BRIDGING}} \\
Behavior \& Identity & {{DOMAIN_BEHAVIOR_AND_IDENTITY_TERMS}} & {{DOMAIN_BEHAVIOR_AND_IDENTITY_FREQ}} & {{DOMAIN_BEHAVIOR_AND_IDENTITY_BRIDGING}} \\
Power \& Labor & {{DOMAIN_POWER_AND_LABOR_TERMS}} & {{DOMAIN_POWER_AND_LABOR_FREQ}} & {{DOMAIN_POWER_AND_LABOR_BRIDGING}} \\
Sex \& Reproduction & {{DOMAIN_SEX_AND_REPRODUCTION_TERMS}} & {{DOMAIN_SEX_AND_REPRODUCTION_FREQ}} & {{DOMAIN_SEX_AND_REPRODUCTION_BRIDGING}} \\
Kin \& Relatedness & {{DOMAIN_KIN_AND_RELATEDNESS_TERMS}} & {{DOMAIN_KIN_AND_RELATEDNESS_FREQ}} & {{DOMAIN_KIN_AND_RELATEDNESS_BRIDGING}} \\
Economics & {{DOMAIN_ECONOMICS_TERMS}} & {{DOMAIN_ECONOMICS_FREQ}} & {{DOMAIN_ECONOMICS_BRIDGING}} \\
\hline
\end{tabular}
\caption{Rule-based domain assignments and corpus frequencies. A term can receive several labels, so domain counts and frequencies are not mutually exclusive. Bridging means multiple labels, not an observed transfer of meaning.}
\label{tab:terminology_extraction}
\end{table}

Among assigned terms, {{CORPUS_MULTIDOMAIN_PERCENTAGE}}\% have multiple domain labels. This is a property of the classifier and corpus. Temporal semantic drift would require explicit time-indexed meaning comparison, while lexical, contextual, and scale ambiguity require independent sense annotation or validated proxies. Those measurements are not established by label overlap.

The processed vocabulary has type-token ratio {{CORPUS_TTR}}. Its most frequent WordNet lemmas are {{CORPUS_TOP_TERM_1}} ({{CORPUS_TOP_FREQ_1}}), {{CORPUS_TOP_TERM_2}} ({{CORPUS_TOP_FREQ_2}}), and {{CORPUS_TOP_TERM_3}} ({{CORPUS_TOP_FREQ_3}}). Lemmatization reduces inflected forms and can truncate words such as *species* to *specie*; extracted terms retain surface forms (Supplemental Section \ref{sec:supplemental_methods}). Frequency identifies recurring lexical material; it does not establish its conceptual importance or the intentions of authors.

## Terminology Network Structure

The observed terminology graph uses the hundred most frequent domain-assigned terms. Its edge weight counts documents containing both terms:

\begin{equation}\label{eq:network_edge_weight}
w(u,v)=\sum_{d=1}^{N}\mathbf{1}[u\in d]\mathbf{1}[v\in d].
\end{equation}

Whole-word matches are case-insensitive, and repeated mentions within a document do not add weight. No edge is inferred from shared labels or extraction order. The graph has mean local (unweighted) clustering coefficient {{NETWORK_CLUSTERING}}; this statistic does not measure conceptual coherence, communication quality, or resistance to reform.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/terminology_network.png}
\caption{Observed document co-occurrence among the hundred highest-frequency domain-assigned terms in the {{CORPUS_PUBLICATIONS}}-abstract layer. Nodes represent terms, node area uses a square-root frequency scale, color identifies the primary domain, and edge width scales shared-document counts to a bounded display range (Eq.~\ref{eq:network_edge_weight}). Isolated nodes are omitted from the display and up to twenty frequent terms are considered for collision-filtered labels. The right panel ranks the ten strongest observed pairs by shared-document count, with lexical tie-breaking. All observed edges remain in the left graph, whose unweighted layout reduces visual concentration around frequent pairs. Layout and dense regions have no causal or hierarchical interpretation.}
\label{fig:terminology_network}
\end{figure}

### Comparison with a Fixed-Margin Reference

Density and clustering depend on how many selected terms each abstract contains and how many abstracts contain each term. A Curveball randomization of the binary document--term incidence matrix preserves both margins (Supplemental Section \ref{sec:fixed_margin}). Over {{NULLNET_CHAINS}} chains and {{NULLNET_DRAWS}} retained draws for the {{NULLNET_DOCUMENTS}} source-identified abstracts and {{NULLNET_TERMS}} terms, the randomized reference averages {{NULLNET_EDGES_NULL_MEAN}} edges (central 95\% of draws {{NULLNET_EDGES_Q025}}--{{NULLNET_EDGES_Q975}}) and mean local clustering {{NULLNET_CLUSTERING_NULL_MEAN}} ({{NULLNET_CLUSTERING_Q025}}--{{NULLNET_CLUSTERING_Q975}}). The observed graph has {{NULLNET_EDGES_OBSERVED}} edges and clustering {{NULLNET_CLUSTERING_OBSERVED}}, below both envelopes (Figure \ref{fig:network_robustness}). A sensitivity protocol with longer burn-in, wider spacing and different seeds ({{NULLNET_SENS_DRAWS}} draws) gives reference means of {{NULLNET_SENS_EDGES_NULL_MEAN}} edges and {{NULLNET_SENS_CLUSTERING_NULL_MEAN}} clustering. Between-chain $\hat R$ is {{NULLNET_EDGES_RHAT}} for edges and {{NULLNET_CLUSTERING_RHAT}} for clustering; this diagnostic does not prove mixing.

Selected terms therefore co-occur in fewer distinct pairs, with less closed triadic structure, than their margins alone would produce: co-occurrence is concentrated among particular pairs. The envelopes describe the sampled conditional reference rather than uncertainty in the observed values, and the comparison does not identify a linguistic cause.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.7\textheight,keepaspectratio]{../output/extensions/network_robustness/network_robustness.png}
\caption{Fixed-margin comparison for the abstract terminology network. Top: retained-chain traces of projected edge count and mean local clustering for {{NULLNET_CHAINS}} seeds. Bottom: distributions of the {{NULLNET_DRAWS}} retained draws, with the observed value marked. Every draw preserves each abstract's selected-term count and each term's document frequency. The reference is conditional on the frequency-ranked vocabulary and the convenience corpus.}
\label{fig:network_robustness}
\end{figure}

### Vocabulary and Edge-Threshold Diagnostic

Across the declared {{NETREAD_CELLS}} vocabulary--threshold combinations on the same {{NETREAD_DOCUMENTS}} identified abstracts, the 100-term graph at a one-document threshold has density {{NETREAD_BASE_DENSITY}}. Requiring at least twenty shared documents retains {{NETREAD_THRESHOLD20_EDGES}} edges and gives density {{NETREAD_THRESHOLD20_DENSITY}}. Figure \ref{fig:network_reading} displays the full grid, including mean local clustering with isolates retained. These are deterministic descriptions of selected representations, not uncertainty intervals or evidence that one threshold recovers true semantic relations. Clustering need not decrease when edges are removed: changing neighborhoods also changes local triangle denominators. The curves separate these topological summaries rather than interpreting either as biological complexity.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.65\textheight,keepaspectratio]{../output/extensions/network_reading/network_reading.png}
\caption{Vocabulary and minimum-shared-document sensitivity. Curves use nested frequency-ranked vocabularies and inclusive thresholds. The denominator includes all selected pairs, and clustering includes isolates as zero. Each point is recomputed from the same identified abstract layer; no new randomization or biological-network inference is represented.}
\label{fig:network_reading}
\end{figure}

Domain-assignment overlap is a different quantity, displayed separately in Figure \ref{fig:domain_overlap}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/domain_overlap_heatmap.png}
\caption{Szymkiewicz--Simpson overlap coefficients between domain-assigned vocabularies (Eq.~\ref{eq:overlap_coefficient}). Each cell shows shared terms as a percentage of the smaller vocabulary; the diagonal is 100 by definition. Values reflect the current lexical classifier; observed zeros do not establish conceptual isolation.}
\label{fig:domain_overlap}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/domain_comparison.png}
\caption{Six descriptive panels show distinct term counts, mean extraction confidence, total frequency, mean successfully computed sentence-context entropy, bridging counts, and heuristic CACE means over up to fifty selected terms per domain. Extraction confidence is a configured score rather than calibrated classification accuracy. Entropy and CACE sample definitions are specified in Methods; missing entropy does not establish zero ambiguity.}
\label{fig:domain_comparison}
\end{figure}


\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/concept_map.png}
\caption{Six predefined concept categories connected by vocabulary overlap. Node size summarizes associated terms, which can appear in several categories; the subtitle totals term associations rather than unique terms. Edge weights are classifier-defined overlaps, not observed causal connections or a discovered biological ontology.}
\label{fig:concept_map}
\end{figure}

## Framing Analysis

Lexical markers identify contexts for further qualitative examination. They do not distinguish metaphor from technical usage, demonstrate author bias, or establish a language-induced change in biological models. The same distinction applies to the domain-specific interpretations in Section \ref{sec:domain_findings}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/anthropomorphic_framing.png}
\caption{Observed framing-marked terminology by canonical domain. Top: distinct extracted terms with at least one occurrence context matching an anthropomorphic pattern. Bottom: up to six terms per domain, selected by decreasing matched-context proportion, context count, and lexical ordering. Counts are neither curated vocabulary sizes nor occurrence frequencies. Occurrence-context framing proportions are exported separately.}
\label{fig:anthropomorphic}
\end{figure}
