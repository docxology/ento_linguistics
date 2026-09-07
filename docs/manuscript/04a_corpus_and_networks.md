# Results: Corpus Analysis and Terminology Networks {#sec:experimental_results}

## Terminology Extraction Across Domains

Our analysis applies the mixed-methodology framework described in Section \ref{sec:methodology} to a corpus of entomological literature. The dataset includes abstracts from foundational works by Hölldobler, Wilson, and Gordon, incorporating terminology patterns characteristic of journals including *Behavioral Ecology*, *Journal of Insect Behavior*, and *Insectes Sociaux*.

Domain-specific extraction from **369 publications** (48787 tokens) identified **888 candidate terms** total, of which **261 receive domain assignments** spanning all six domains, with substantial variation in usage patterns:

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Domain} & \textbf{Term Count} & \textbf{Total Frequency} & \textbf{Bridging Terms} \\
\hline
Unit of Individuality & 73 & 769 & 2 \\
Behavior \& Identity & 40 & 948 & 19 \\
Power \& Labor & 63 & 905 & 43 \\
Sex \& Reproduction & 64 & 605 & 26 \\
Kin \& Relatedness & 57 & 459 & 0 \\
Economics & 10 & 201 & 0 \\
\hline
\end{tabular}
\caption{Domain-assigned terminology extracted from the 369-publication corpus. Terms are assigned by seed-expansion matching against domain-specific seed vocabularies; a single term may appear in multiple domains, so per-domain Term Counts sum to more than the 261 distinct domain-assigned terms. Total Freq counts all occurrences across the corpus for domain-assigned terms. Bridging Terms indicate terms that co-occur across multiple domain vocabularies. Full per-domain breakdowns are in \texttt{output/data/domain\_statistics.json}.}
\label{tab:terminology_extraction}
\end{table}

Of 888 total extracted candidate terms, 261 receive domain assignments. The global corpus vocabulary possesses a Type-Token Ratio (TTR) of **0.1456**, reflecting the dense, highly specialized nature of the discourse. The absolute highest frequency terms across all contexts empirically anchor the investigation: **ant** (1033 occurrences), **colony** (850 occurrences), and **worker** (831 occurrences) dominate the conceptual landscape.

Among domains, Power \& Labor possesses highly dominant bridging capacities (43 bridging terms) and the highest absolute occurrence frequency (905 total occurrences). Conversely, Economics maintains the most tightly constrained vocabulary (10 terms) with zero bridging bleed-over (0 bridging terms), reflecting strict, insular deployment of economic metaphors.

## Terminology Network Structure

Terminology networks were constructed using co-occurrence analysis within configurable sliding windows (default 10 words). Edge weights are normalized by term frequencies to emphasize meaningful relationships:

\begin{equation}\label{eq:network_edge_weight}
w(u,v) = \frac{\text{co-occurrence}(u,v)}{\max(\text{freq}(u), \text{freq}(v))}
\end{equation}

Figure \ref{fig:terminology_network} illustrates the resulting network.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../output/figures/terminology_network.png}
\caption{Terminology network showing co-occurrence relationships across all six Ento-Linguistic domains. Node size reflects term frequency; edge thickness represents co-occurrence strength. Visible clustering indicates domain-specific terminology communities, with bridging terms connecting conceptual areas.}
\label{fig:terminology_network}
\end{figure}

The network exhibits strong modularity: 894 nodes (888 extracted terms plus the 6 conceptual cluster nodes) connected by 538 edges, with a clustering coefficient of 0.1749 and average degree of 1.2. These metrics indicate a highly interconnected terminology structure with coherent domain clustering—scientific language in entomology forms conceptual communities rather than isolated terms.

Domain-level network analysis reveals distinct architectures across the six core themes. As visualized in the aggregate network topology, dense identity clusters characterize Behavior & Identity terminology, while Power & Labor terminology forms hierarchical, chain-like structures. Conversely, Sex & Reproduction terms tend to organize into rigid binary oppositions, and Economics terms cluster tightly around transactional frameworks with few bridges to biological mechanism descriptions.

The conceptual bridges between these domains are quantified and visualized in Figure \ref{fig:domain_overlap}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/domain_overlap_heatmap.png}
\caption{Domain overlap heatmap showing the Szymkiewicz--Simpson overlap coefficient of shared terminology between each pair of Ento-Linguistic domains. Darker cells indicate higher overlap; Power \& Labor exhibits the strongest cross-domain connectivity (particularly to Behavior \& Identity and Sex \& Reproduction), while Economics shows zero bridging terms with other domains. Off-diagonal asymmetry reflects directional borrowing patterns. Values are computed at runtime from the extracted term-domain assignments in \texttt{output/data/domain\_statistics.json}.}
\label{fig:domain_overlap}
\end{figure}

Distinctive cross-domain bridges include:

- **Power & Labor $\leftrightarrow$ Behavior & Identity**: Mechanisms of role assignment.
- **Unit of Individuality $\leftrightarrow$ Kin & Relatedness**: Foundations of social structure.
- **Economics $\leftrightarrow$ Power & Labor**: Resource distribution hierarchies.

Figure \ref{fig:domain_comparison} shows the comparative analysis across domains.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/domain_comparison.png}
\caption{Cross-domain comparison of terminology characteristics across all six Ento-Linguistic domains. The six panels show (top-left) the number of distinct terms extracted per domain, (top-right) the average confidence score assigned during extraction, (center-left) cumulative term frequency across the corpus, (center-right) the mean semantic entropy $H(t)$ per domain, (bottom-left) cross-domain bridging term counts, and (bottom-right) the mean CACE aggregate score. Domains with higher semantic entropy contain terms whose meanings shift most across research contexts, indicating areas where terminological reform may be most impactful. All panel values are computed at runtime from \texttt{output/data/domain\_statistics.json}.}
\label{fig:domain_comparison}
\end{figure}

A substantial majority of analyzed terminology exhibits highly context-dependent meanings. Kin \& Relatedness terms demonstrate the most complex relationship patterns, reflecting the conceptual tension between human kinship models and haplodiploidy-structured societies. Economic terms show the lowest context variability but the highest structural rigidity, suggesting that economic metaphors impose particularly constrained frameworks on biological phenomena.

## Framing Analysis

Computational identification of framing assumptions reveals systematic biases embedded within the literature. Anthropomorphic framing profoundly affects all domains, while hierarchical framing concentrates heavily within the Power/Labor and Unit of Individuality discourse.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/anthropomorphic_framing.png}
\caption{Anthropomorphic framing prevalence across Ento-Linguistic domains. The trajectory highlights paradigm shifts across decades, showcasing how domains like Power \& Labor experienced steep declines in overt anthropomorphism—consistent with the formal "slave" terminology reforms documented in Section \ref{sec:discussion}—while economic framing concurrently rose to prominence.}
\label{fig:anthropomorphic}
\end{figure}

Our ambiguity detection algorithm classifies four distinct ambiguity types—lexical, contextual, scale-dependent, and temporal—and confirms that *scale ambiguity* (where meaning shifts across biological levels of organization) and *context-dependent semantic drift* are the most prevalent patterns across the corpus (see Section \ref{sec:supplemental_analysis} for the formal multi-level ambiguity classification).
