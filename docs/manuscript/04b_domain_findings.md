# Results: Domain-Specific Findings {#sec:domain_findings}

## Unit of Individuality

Frequency and ambiguity analyses show that the highest-frequency terms (``colony,'' ``individual'') anchor the domain. Its mean semantic entropy ({{DOMAIN_UNIT_OF_INDIVIDUALITY_ENTROPY}} bits) sits in the lower half of the six-domain range (Table \ref{tab:entropy_distribution}). Figure \ref{fig:unit_individuality_patterns} details the scale-dependent terminology patterns within this domain, while per-domain top-term frequency distributions and part-of-speech composition breakdowns for all six domains are visualized in Figure \ref{fig:domain_overview_grid} and Figure \ref{fig:domain_patterns_grid} respectively.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../output/figures/domain_overview_grid.png}
\caption{Top terms by corpus frequency for each of the six Ento-Linguistic domains, as a 3\,×\,2 grid of horizontal bar charts computed at build time from the terminology of the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; {{CORPUS_DOMAIN_TERMS}} domain-assigned terms; \texttt{output/data/domain\_statistics.json}). Within each panel, the ten highest-frequency terms of that domain are ranked by corpus frequency (bar length, annotated at the bar tip); panel titles give each domain's total term count. Bar color encodes per-term semantic entropy $H(t)$ in bits (Eq.~\ref{eq:semantic_entropy}) on a shared \texttt{YlOrRd} scale spanning zero to the corpus maximum, with the shared color bar at right; darker bars indicate terms whose usage contexts span more sense clusters. The grid shows Economics as the smallest domain while its terms carry the highest entropies (Table \ref{tab:entropy_distribution}), with Power \& Labor and Behavior \& Identity also containing high-entropy terms.}
\label{fig:domain_overview_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../output/figures/domain_patterns_grid.png}
\caption{Part-of-speech composition of each Ento-Linguistic domain's vocabulary, shown as donut charts in a 3\,×\,2 grid (one panel per domain), computed at build time from the part-of-speech tags of the domain-assigned terms extracted from the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; \texttt{output/data/domain\_statistics.json}). Each slice is a grammatical category (for example noun compounds, adjective--noun, or verb--noun constructions) with slice angle proportional to that category's share of part-of-speech tag counts within the domain; because a term can carry several tags, shares are of tag counts, not distinct terms. Categories beyond the six largest per domain are grouped as \emph{Other}, and the annotation at each donut's centre gives the domain's term count. Domains whose slices concentrate in noun-compound categories (for example Unit of Individuality) have vocabularies structurally biased toward reified noun phrases in this corpus.}
\label{fig:domain_patterns_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/unit_of_individuality_patterns.png}
\caption{Terminology patterns in the Unit of Individuality domain, computed at build time from the domain's terms in the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; \texttt{output/data/domain\_statistics.json}). \emph{Left}: term-formation patterns (the part-of-speech structure of the domain's terms) as a pie chart, with slice angles proportional to pattern counts and percentages annotated. \emph{Right}: number of domain terms whose names match keyword groups for five biological scales---Colony (Superorganism), Sub-colony (Caste), Individual (Worker), Genomic (Gene-level), and Emergent (Collective)---as a bar chart with counts annotated; counts are floored at one for display, so a near-zero scale is indistinguishable from a single match. Colony-level terms such as ``colony'' and ``superorganism'' populate the colony-scale group; the distribution across scales grounds the scale ambiguities discussed in the text.}
\label{fig:unit_individuality_patterns}
\end{figure}

## Power \& Labor

The most structurally rigid domain shows clear hierarchical patterns derived from human social systems \cite{herbers2007, boomsma2018superorganismality}. Recent molecular approaches to caste \cite{heinze2017molecular} and epigenetic evidence that caste determination is a labile developmental process \cite{warner2024caste} further underscore the need for reform. {{DOMAIN_POWER_AND_LABOR_ANTHROPOMORPHIC_PROPORTION_PCT}}\% of Power \& Labor terms score above baseline on the pipeline's anthropomorphic-framing proportion for this domain (see \texttt{domain\_statistics.json}), consistent with pervasive hierarchical metaphor. Figure \ref{fig:concept_hierarchy} visualizes the resulting conceptual hierarchy; Figures \ref{fig:power_labor_frequencies} and \ref{fig:power_labor_ambiguities} profile the domain's term frequencies and semantic-entropy distribution. "Caste" and "queen" form central hub terms with the highest betweenness centrality; "worker" and "slave" show parasitic terminology influence \cite{herbers2006}. The chain-like network structure reflects the linear hierarchies assumed by this vocabulary rather than the distributed organization documented in behavioral studies (Figures \ref{fig:concept_hierarchy}, \ref{fig:power_labor_frequencies}, \ref{fig:power_labor_ambiguities}).

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/concept_hierarchy.png}
\caption{Concept-centrality structure of the Ento-Linguistic concept map, computed at build time from the concept map built over the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; \texttt{output/data/concept\_map\_summary.json}). Concepts are clusters of domain-assigned terms; a concept's centrality is its number of direct links to other concepts in the map. \emph{Left}: all concepts ranked by centrality (bar length, score annotated at the bar tip), colored green for core concepts (centrality strictly above the map-wide mean) and red for peripheral concepts (at or below the mean). \emph{Right}: centrality against the number of associated terms, with point area proportional to centrality and the ten highest-centrality concepts labelled. The ranking spans all six Ento-Linguistic domains; it is not restricted to Power \& Labor.}
\label{fig:concept_hierarchy}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/power_and_labor_term_frequencies.png}
\caption{Corpus frequency of the fifteen most frequent Power \& Labor terms, computed at build time from the domain-assigned terminology of the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; \texttt{output/data/domain\_statistics.json}). Bar height encodes total corpus frequency, annotated at the bar tip; bars are ordered by descending frequency, and the \texttt{YlOrRd} shading tracks rank order only, encoding no additional quantity. In the current corpus ``queen,'' ``worker,'' and ``caste'' are the three most frequent terms of this domain, consistent with the entrenched hierarchical framing discussed in the text; the ranking is descriptive, and no significance testing is applied to it.}
\label{fig:power_labor_frequencies}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/power_and_labor_ambiguities.png}
\caption{Semantic entropy $H(t)$ of Power \& Labor terms (Eq.~\ref{eq:semantic_entropy}), computed at build time from the usage contexts of the domain's terms in the headline abstract layer ({{CORPUS_PUBLICATIONS}} open-access PubMed abstracts; TF-IDF vectorization of each term's contexts followed by $k$-means sense clustering; \texttt{output/data/domain\_statistics.json}). The fifteen highest-entropy terms of the domain are shown. \emph{Left}: per-term entropy as bars sorted by descending $H(t)$, each annotated with its entropy in bits and extracted-context count, with a dashed vertical line marking the panel median. \emph{Right}: corpus frequency (horizontal) against $H(t)$ (vertical), with point area proportional to the number of extracted contexts and point color repeating the entropy scale (\texttt{Purples}). ``Caste'' and ``queen'' exhibit elevated entropy in this corpus, consistent with their documented polysemy across hierarchical, reproductive, and behavioral research contexts; entropy values describe context diversity and imply no preferred reform direction.}
\label{fig:power_labor_ambiguities}
\end{figure}

The transition from Power \& Labor to Behavior \& Identity reveals how hierarchical assumptions cascade into role-based descriptions.

## Behavior & Identity

Behavioral descriptions create categorical identities that may obscure the biological fluidity documented in ant task-switching research \cite{ravary2007, gordon2010}. As \citet{gordon1992wittgenstein} argues—drawing on Wittgenstein's analysis of category boundaries—the act of classifying a nestmate as a "forager" or a "nurse" is not a neutral observation but an imposition of discrete categories onto continuous behavioral variation. Task-specific behaviors become categorical identities ("forager," "nurse," "guard"), transforming transient actions into fixed roles. Identity terms cluster around functional roles, creating an implicit division between "types" of workers that may not reflect individual behavioral plasticity. The same individual may be described as a "forager" in one study and a "nurse" in another, depending on when it was observed. \citeauthor{gordon2023ecology}'s \citeyearpar{gordon2023ecology} recent synthesis demonstrates that task allocation in harvester ant colonies operates entirely through local interaction networks—brief antennal contacts modulated by cuticular hydrocarbon profiles—without any centralized assignment. Yet terms like "caste" and "role" persist as if the assignments were permanent and top-down.

Detailed frequency and ambiguity analyses for this domain confirm the pattern: task-identity terms such as ``forager'' and ``nurse'' exhibit high frequency but moderate-to-high ambiguity (mean semantic entropy: {{DOMAIN_BEHAVIOR_AND_IDENTITY_ENTROPY}} bits), reflecting the gap between categorical labels and fluid biological reality. Per-domain breakdowns are shown in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

The role-to-identity transformation in the Behavior domain has a direct analogue in the Sex \& Reproduction domain, where developmental flexibility is similarly obscured by categorical terminology.

## Sex \& Reproduction

Sex and reproduction terminology shows the lowest overall ambiguity but reveals a distinctive pattern of **binary opposition**—the dominant network structure in this domain (Figure \ref{fig:terminology_network}). Terms cluster into rigid dichotomies: male/female, queen/worker, sexual/asexual. These oppositions import mammalian sex-determination frameworks into a fundamentally different system: under haplodiploidy, males develop from unfertilized (haploid) eggs and females from fertilized (diploid) eggs, decoupling sex determination from the chromosomal mechanisms assumed by standard terminology \cite{chandra2021epigenetics}. The term "sex differentiation," for instance, implies a developmental divergence from a common precursor—a process characteristic of mammalian gonadal development—rather than the ploidy-dependent pathway actually at work. Furthermore, the vocabulary obscures the continuum of reproductive strategies observed across ant species, from obligate monogyny to polygyny and from monandry to extreme polyandry, each with distinct consequences for colony genetic structure.

Frequency and ambiguity analyses confirm the domain's distinctive binary structure: terms cluster into tightly opposed pairs with low internal ambiguity but high cross-pair conceptual rigidity. Full per-domain frequency and POS patterns are shown in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

## Kin \& Relatedness

Kin and Relatedness terminology exhibits the lowest mean semantic entropy ({{DOMAIN_KIN_AND_RELATEDNESS_ENTROPY}} bits) and a web-like network architecture reflecting the complex, non-intuitive relatedness structures of haplodiploid societies (Figure \ref{fig:domain_overview_grid}). The central tension is between human bilateral kinship models—where siblings share $r = 0.5$—and the haplodiploidy-specific asymmetry where full sisters share $r = 0.75$ but sisters relate to brothers at only $r = 0.25$. When researchers describe colony members as "sisters," the term imports an assumption of symmetry that masks the very asymmetry on which inclusive fitness theory depends.

Hub terms such as ``kin,'' ``relatedness,'' and ``inclusive fitness'' bridge multiple sub-domains. Network analysis reveals that Hamilton's-rule-adjacent vocabulary dominates the discourse, often at the expense of alternative frameworks such as multilevel selection. Analysis of kinship terminology shows that ``kin selection'' co-occurs with ``altruism'' and ``cooperation'' far more frequently than with ``conflict'' or ``policing,'' suggesting a framing bias toward cooperative explanations that may underrepresent intra-colony conflict dynamics. Per-domain frequency and pattern breakdowns are provided in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

## Economics

The Economics domain contains the smallest vocabulary ({{DOMAIN_ECONOMICS_TERMS}} terms) and zero bridging terms ({{DOMAIN_ECONOMICS_BRIDGING}})—the most insular domain by a substantial margin. For comparison, Power \& Labor contributes {{DOMAIN_POWER_AND_LABOR_BRIDGING}} bridging terms to adjacent domains, whereas Economics shares vocabulary with none. The complete term inventory reveals the character of this insularity: \textbf{allocation} ({{TERM_FREQ_ALLOCATION}} occurrences), \textbf{investment} ({{TERM_FREQ_INVESTMENT}}), \textbf{resources} ({{TERM_FREQ_RESOURCES}}), \textbf{resource} ({{TERM_FREQ_RESOURCE}}), and additional low-frequency terms including \textbf{trade-off}, \textbf{trade-offs}, \textbf{jack-of-all-trades}, and \textbf{gamma-distribution}. The final two are anomalies—terms pattern-matched to economics seed vocabulary that are, in practice, statistical and ecological constructs co-opted by economic framing, yet their presence reflects how pervasively the economic paradigm has colonized foraging ecology's conceptual substrate.

The semantically active core terms conflate two fundamentally different levels of explanation. "Cost" may refer to proximate energetic expenditure (measurable in joules) or to ultimate fitness reduction (requiring population-level inference); these distinct meanings are routinely treated as interchangeable. The same proximate–ultimate conflation operates across "investment," "resource allocation," and "trade-off." The resulting network architecture is self-contained: transaction-like term pairs ("cost–benefit," "allocation–resource") form tight clusters with {{DOMAIN_ECONOMICS_BRIDGING}} bridging edges to biological-mechanism clusters—indicating that economic terminology operates as a closed conceptual subsystem that resists integration with process-level descriptions.

Notably, Economics terms exhibit the highest mean semantic entropy ({{DOMAIN_ECONOMICS_ENTROPY}} bits) of all domains despite zero bridging terms, confirming that economic metaphors form a self-contained but highly polysemous subsystem. The average extraction confidence is also the highest, indicating stable deployment within this insular vocabulary. This monoculture trades explanatory integration across domains for internal semantic precision. These patterns are shown across all domains in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

## Longitudinal Case Studies

To understand how these linguistic paradigms evolve over time, we conducted longitudinal analysis on two critical terminology clusters: *Caste* and *Superorganism*.

### Caste Terminology Evolution

A clear historical trajectory emerges from rigid categories to plasticity-aware descriptions:

- **Foundational Era** (pre-1990): Rigid caste categories dominated descriptions of task allocation. Terms like "caste" and "subcaste" were used as if they denoted fixed, heritable phenotypes—analogous to social strata in human societies.
- **Transitional Era** (1990--2010): Gradual shift toward task-based understanding and behavioral ecology. \citeauthor{gordon1992wittgenstein}'s \citeyearpar{gordon1992wittgenstein} Wittgensteinian critique and accumulating behavioral data on task-switching challenged the categorical rigidity of caste vocabulary.
- **Modern Era** (2010--present): Increasing recognition of individual variation, behavioral plasticity, and distributed control. Epigenetic evidence \cite{chandra2021epigenetics, warner2024caste} reveals caste determination as a labile developmental process, further undermining the linguistic prior of fixed social categories.

### Superorganism Debate: Conceptual Evolution

The superorganism concept has undergone a parallel structural transformation. \citeauthor{wheeler1911}'s \citeyearpar{wheeler1911} early metaphor of the colony-as-organism organized a century of research while simultaneously constraining how individuality was conceptualized in social insect biology. More recent work has progressively replaced this metaphorical convenience with mathematically rigorous, multi-scale frameworks of biological individuality—particularly the Markov Blanket formalism \cite{friston2013life} and \citeauthor{boomsma2018superorganismality}'s \citeyearpar{boomsma2018superorganismality} analysis of how "superorganismality" was lost in translation between evolutionary and organismic biology. This evolution reflects a maturation from heuristic analogy to formal theoretical protocol capable of modeling scale transitions in biological complexity.
