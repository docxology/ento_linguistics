# Results: Corpus Analysis and Terminology Networks {#sec:experimental_results}

## Terminology Extraction Across Domains

Our analysis applies the mixed-methodology framework described in Section \ref{sec:methodology} to a corpus of entomological literature. The dataset includes abstracts from foundational works by Hölldobler, Wilson, and Gordon, incorporating terminology patterns characteristic of journals including *Behavioral Ecology*, *Journal of Insect Behavior*, and *Insectes Sociaux*.

Domain-specific extraction from **{{CORPUS_PUBLICATIONS}} publications** ({{CORPUS_TOTAL_TOKENS}} tokens) identified **{{CORPUS_CANDIDATE_TERMS}} candidate terms** total, of which **{{CORPUS_DOMAIN_TERMS}} receive domain assignments** spanning all six domains, with substantial variation in usage patterns:

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Domain} & \textbf{Term Count} & \textbf{Total Frequency} & \textbf{Bridging Terms} \\
\hline
Unit of Individuality & {{DOMAIN_UNIT_OF_INDIVIDUALITY_TERMS}} & {{DOMAIN_UNIT_OF_INDIVIDUALITY_FREQ}} & {{DOMAIN_UNIT_OF_INDIVIDUALITY_BRIDGING}} \\
Behavior \& Identity & {{DOMAIN_BEHAVIOR_AND_IDENTITY_TERMS}} & {{DOMAIN_BEHAVIOR_AND_IDENTITY_FREQ}} & {{DOMAIN_BEHAVIOR_AND_IDENTITY_BRIDGING}} \\
Power \& Labor & {{DOMAIN_POWER_AND_LABOR_TERMS}} & {{DOMAIN_POWER_AND_LABOR_FREQ}} & {{DOMAIN_POWER_AND_LABOR_BRIDGING}} \\
Sex \& Reproduction & {{DOMAIN_SEX_AND_REPRODUCTION_TERMS}} & {{DOMAIN_SEX_AND_REPRODUCTION_FREQ}} & {{DOMAIN_SEX_AND_REPRODUCTION_BRIDGING}} \\
Kin \& Relatedness & {{DOMAIN_KIN_AND_RELATEDNESS_TERMS}} & {{DOMAIN_KIN_AND_RELATEDNESS_FREQ}} & {{DOMAIN_KIN_AND_RELATEDNESS_BRIDGING}} \\
Economics & {{DOMAIN_ECONOMICS_TERMS}} & {{DOMAIN_ECONOMICS_FREQ}} & {{DOMAIN_ECONOMICS_BRIDGING}} \\
\hline
\end{tabular}
\caption{Domain-assigned terminology extracted from the {{CORPUS_PUBLICATIONS}}-publication corpus. Terms are assigned by seed-expansion matching against domain-specific seed vocabularies; a single term may appear in multiple domains, so per-domain Term Counts sum to more than the {{CORPUS_DOMAIN_TERMS}} distinct domain-assigned terms. Total Freq counts all occurrences across the corpus for domain-assigned terms. Bridging Terms indicate terms that co-occur across multiple domain vocabularies. Full per-domain breakdowns are in \texttt{output/data/domain\_statistics.json}.}
\label{tab:terminology_extraction}
\end{table}

Of {{CORPUS_CANDIDATE_TERMS}} total extracted candidate terms, {{CORPUS_DOMAIN_TERMS}} receive domain assignments. The global corpus vocabulary possesses a Type-Token Ratio (TTR) of **{{CORPUS_TTR}}**, reflecting the dense, highly specialized nature of the discourse. The absolute highest frequency terms across all contexts empirically anchor the investigation: **{{CORPUS_TOP_TERM_1}}** ({{CORPUS_TOP_FREQ_1}} occurrences), **{{CORPUS_TOP_TERM_2}}** ({{CORPUS_TOP_FREQ_2}} occurrences), and **{{CORPUS_TOP_TERM_3}}** ({{CORPUS_TOP_FREQ_3}} occurrences) dominate the conceptual landscape.

Among domains, Behavior \& Identity possesses the highest absolute occurrence frequency ({{DOMAIN_BEHAVIOR_AND_IDENTITY_FREQ}} total occurrences), while Power \& Labor exhibits the most extensive bridging capacity ({{DOMAIN_POWER_AND_LABOR_BRIDGING}} bridging terms). Conversely, Economics maintains the most tightly constrained vocabulary ({{DOMAIN_ECONOMICS_TERMS}} terms) with zero bridging bleed-over ({{DOMAIN_ECONOMICS_BRIDGING}} bridging terms), reflecting strict, insular deployment of economic metaphors.

## Terminology Network Structure

Terminology networks were constructed from the term--domain assignments produced by extraction: two terms are linked when they share at least one Ento-Linguistic domain, and edge weights are normalized by domain-set size to emphasize meaningful relationships. Writing $D(t)$ for the set of domains term $t$ is assigned to, an edge is retained only when its weight exceeds $0.1$:

\begin{equation}\label{eq:network_edge_weight}
w(u,v) = \frac{|D(u) \cap D(v)|}{\max(|D(u)|, |D(v)|)}
\end{equation}

Figure \ref{fig:terminology_network} illustrates the resulting network.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../output/figures/terminology_network.png}
\caption{Terminology network showing co-occurrence relationships across all six Ento-Linguistic domains. Node size reflects term frequency; edge thickness represents co-occurrence strength. Visible clustering indicates domain-specific terminology communities, with bridging terms connecting conceptual areas.}
\label{fig:terminology_network}
\end{figure}

The network exhibits strong modularity: {{NETWORK_NODES}} nodes ({{CORPUS_CANDIDATE_TERMS}} extracted terms plus the {{CORPUS_CONCEPT_COUNT}} conceptual cluster nodes) connected by {{NETWORK_EDGES}} edges, with a clustering coefficient of {{NETWORK_CLUSTERING}} and average degree of {{NETWORK_AVG_DEGREE}}. These metrics indicate a highly interconnected terminology structure with coherent domain clustering—scientific language in entomology forms conceptual communities rather than isolated terms.

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
