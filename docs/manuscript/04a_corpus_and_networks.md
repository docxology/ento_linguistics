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

The processed vocabulary has type-token ratio {{CORPUS_TTR}}. Its most frequent recorded tokens are {{CORPUS_TOP_TERM_1}} ({{CORPUS_TOP_FREQ_1}}), {{CORPUS_TOP_TERM_2}} ({{CORPUS_TOP_FREQ_2}}), and {{CORPUS_TOP_TERM_3}} ({{CORPUS_TOP_FREQ_3}}). Frequency identifies recurring lexical material; it does not establish its conceptual importance or the intentions of authors.

## Terminology Network Structure

The observed terminology graph uses the hundred most frequent domain-assigned terms. Its edge weight counts documents containing both terms:

\begin{equation}\label{eq:network_edge_weight}
w(u,v)=\sum_{d=1}^{N}\mathbf{1}[u\in d]\mathbf{1}[v\in d].
\end{equation}

Whole-word matches are case-insensitive, and repeated mentions within a document do not add weight. No edge is inferred from shared labels or extraction order. The graph has clustering coefficient {{NETWORK_CLUSTERING}} under the generated network-summary definition; this statistic does not measure conceptual coherence, communication quality, or resistance to reform.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/terminology_network.png}
\caption{Observed document co-occurrence among the hundred highest-frequency domain-assigned terms in the {{CORPUS_PUBLICATIONS}}-abstract layer. Nodes represent terms, node area uses a square-root frequency scale, color identifies the primary domain, and edge width scales shared-document counts to a bounded display range (Eq.~\ref{eq:network_edge_weight}). Isolated nodes are omitted from the display and up to twenty frequent terms are considered for collision-filtered labels. Layout and dense regions have no causal or hierarchical interpretation.}
\label{fig:terminology_network}
\end{figure}

Domain-assignment overlap is a different quantity, displayed separately in Figure \ref{fig:domain_overlap}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/domain_overlap_heatmap.png}
\caption{Szymkiewicz--Simpson overlap coefficients between domain-assigned vocabularies (Eq.~\ref{eq:overlap_coefficient}). Each cell counts shared terms divided by the smaller vocabulary size. Values reflect the current lexical classifier; observed zeros do not establish conceptual isolation.}
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
\caption{Observed framing-marked terminology by canonical domain. Left: distinct extracted terms with at least one occurrence context matching an anthropomorphic pattern. Right: up to five terms per domain, selected by decreasing matched-context proportion, context count, and lexical ordering. Counts are neither curated vocabulary sizes nor occurrence frequencies. Occurrence-context framing proportions are exported separately.}
\label{fig:anthropomorphic}
\end{figure}

Among assigned terms, {{CORPUS_MULTIDOMAIN_PERCENTAGE}}\% have multiple domain labels. This is a property of the classifier and corpus. Temporal semantic drift would require explicit time-indexed meaning comparison, while lexical, contextual, and scale ambiguity require independent sense annotation or validated proxies. Those measurements are not established by label overlap.
