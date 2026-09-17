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
\caption{Co-occurrence network of the domain-assigned terminology extracted from the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; {{CORPUS_CANDIDATE_TERMS}} candidate terms, of which {{CORPUS_DOMAIN_TERMS}} are assigned to at least one Ento-Linguistic domain). Each node is an extracted term: node size is proportional to corpus frequency, and node color encodes the term's primary Ento-Linguistic domain (legend at right). Edge width is proportional to the pipeline relationship weight between terms (shared-domain overlap, Eq.~\ref{eq:network_edge_weight}); isolated terms are omitted, and only the twenty highest-frequency terms are labelled for legibility. Clustered regions are terminology communities dominated by particular domains; terms linking communities are the bridging terms discussed in the text. Network values resolve at build time from \texttt{output/data/domain\_statistics.json} and \texttt{output/data/concept\_map\_summary.json}.}
\label{fig:terminology_network}
\end{figure}

The network exhibits strong modularity: {{NETWORK_NODES}} nodes ({{CORPUS_CANDIDATE_TERMS}} extracted terms plus the {{CORPUS_CONCEPT_COUNT}} conceptual cluster nodes) connected by {{NETWORK_EDGES}} edges, with a clustering coefficient of {{NETWORK_CLUSTERING}} and average degree of {{NETWORK_AVG_DEGREE}}. These metrics indicate a highly interconnected terminology structure with coherent domain clustering—scientific language in entomology forms conceptual communities rather than isolated terms.

Domain-level network analysis reveals distinct architectures across the six core themes. As visualized in the aggregate network topology, dense identity clusters characterize Behavior & Identity terminology, while Power & Labor terminology forms hierarchical, chain-like structures. Conversely, Sex & Reproduction terms tend to organize into rigid binary oppositions, and Economics terms cluster tightly around transactional frameworks with few bridges to biological mechanism descriptions.

The conceptual bridges between these domains are quantified and visualized in Figure \ref{fig:domain_overlap}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/domain_overlap_heatmap.png}
\caption{Cross-domain terminology overlap among the six Ento-Linguistic domains, computed at build time from the term--domain assignments of the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; \texttt{output/data/domain\_statistics.json}). Each cell is the Szymkiewicz--Simpson overlap coefficient (Eq.~\ref{eq:overlap_coefficient}): the number of extracted terms assigned to both domains of the pair, divided by the smaller domain's term count. The heatmap is symmetric, so off-diagonal cells read the same in both directions; darker cells (\texttt{YlOrRd} colormap) indicate higher shared terminology, and the diagonal is 100\% by construction. The strongest observed connectivity joins Power \& Labor with Behavior \& Identity and with Sex \& Reproduction; zero cells (for example Economics with Behavior \& Identity) are observed zeros of the current corpus: no extracted term is assigned to both domains of those pairs.}
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
\caption{Comparison of terminology characteristics across the six Ento-Linguistic domains, computed at build time from the domain-assigned terminology of the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; \texttt{output/data/domain\_statistics.json}). The 3\,×\,2 grid of bar charts shows (top-left) the number of distinct terms extracted per domain, (top-right) the mean extraction confidence assigned by the term extractor, (center-left) the total corpus frequency of each domain's terms, (center-right) the mean semantic entropy $H(t)$ per domain (Eq.~\ref{eq:semantic_entropy}, averaged over the domain's terms), (bottom-left) the number of bridging terms (terms assigned to more than one domain), and (bottom-right) the mean CACE aggregate score (Clarity, Appropriateness, Consistency, Evolvability; computed per domain on a sample of up to fifty terms). Within each panel, bar height encodes the quantity named on the $y$-axis, with values annotated at the bar tips; bar colors distinguish domains, not magnitudes. Domains with higher mean semantic entropy have usage contexts spanning more sense clusters in this corpus---an observed association, not evidence of causal framing effects.}
\label{fig:domain_comparison}
\end{figure}

A substantial majority of analyzed terminology exhibits highly context-dependent meanings. Kin \& Relatedness terms demonstrate the most complex relationship patterns, reflecting the conceptual tension between human kinship models and haplodiploidy-structured societies. Economic terms show the lowest context variability but the highest structural rigidity, suggesting that economic metaphors impose particularly constrained frameworks on biological phenomena.

## Framing Analysis

Computational identification of framing assumptions reveals systematic biases embedded within the literature. Anthropomorphic framing profoundly affects all domains, while hierarchical framing concentrates heavily within the Power/Labor and Unit of Individuality discourse.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/anthropomorphic_framing.png}
\caption{Inventory of the curated anthropomorphic vocabulary used by the framing analysis over the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts). \emph{Left}: number of curated marker terms per category---Hierarchical Terms, Economic Metaphors, Kinship Language, Identity Labels, and Agency Attribution; bar height encodes the count, annotated at the bar tip, with the overall total shown bottom-right. \emph{Right}: up to five example terms per category. These categories define the marker vocabularies that the pipeline's framing analysis matches in term-occurrence contexts; the counts are the sizes of the curated vocabularies, not corpus frequencies. Per-domain anthropomorphic-framing proportions derived from these vocabularies resolve at build time from \texttt{output/data/domain\_statistics.json}.}
\label{fig:anthropomorphic}
\end{figure}

Our ambiguity detection algorithm classifies four distinct ambiguity types—lexical, contextual, scale-dependent, and temporal—and confirms that *scale ambiguity* (where meaning shifts across biological levels of organization) and *context-dependent semantic drift* are the most prevalent patterns across the corpus (see Section \ref{sec:supplemental_analysis} for the formal multi-level ambiguity classification).
