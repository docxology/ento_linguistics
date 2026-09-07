# Results: Domain-Specific Findings {#sec:domain_findings}

## Unit of Individuality

Frequency and ambiguity analyses confirm that the highest-frequency terms (``colony,'' ``individual'') are also the most ambiguous, consistent with the domain's elevated semantic entropy. Figure \ref{fig:unit_individuality_patterns} details the scale-dependent terminology patterns within this domain, while per-domain top-term frequency distributions and part-of-speech composition breakdowns for all six domains are visualized in Figure \ref{fig:domain_overview_grid} and Figure \ref{fig:domain_patterns_grid} respectively.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../output/figures/domain_overview_grid.png}
\caption{Domain Terminology Overview: top-10 terms by corpus frequency for each of the six Ento-Linguistic domains, displayed as a 3\,×\,2 grid of horizontal bar charts. Bar color encodes semantic entropy $H(t)$ (bits) on a shared \texttt{YlOrRd} scale; darker bars indicate higher polysemy. The overview highlights Economics' high entropy despite sparse vocabulary, with Power \& Labor and Behavior \& Identity also showing notable polysemy.}
\label{fig:domain_overview_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../output/figures/domain_patterns_grid.png}
\caption{Domain POS-Composition Patterns: donut charts showing the part-of-speech structure of each domain's vocabulary (3\,×\,2 grid, one panel per domain). Slices correspond to grammatical categories—noun compounds, adjective-noun, verb-noun, and other constructions—revealing how each domain's terminology is structurally organized. Domains with a dominant noun-compound slice (e.g., Unit of Individuality) tend toward reification of biological processes.}
\label{fig:domain_patterns_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/unit_of_individuality_patterns.png}
\caption{Unit of Individuality domain analysis showing terminology patterns across biological scales. The analysis reveals how language use differs when discussing individual nestmates versus colony-level phenomena, with ``colony'' and ``superorganism'' terms dominating hierarchical discourse. Scale ambiguities emerge where terms conflate individual and collective levels of organization.}
\label{fig:unit_individuality_patterns}
\end{figure}

## Power \& Labor

The most structurally rigid domain shows clear hierarchical patterns derived from human social systems \cite{herbers2007, boomsma2018superorganismality}. Recent molecular approaches to caste \cite{heinze2017molecular} and epigenetic evidence that caste determination is a labile developmental process \cite{warner2024caste} further underscore the need for reform. 69.8\% of Power \& Labor terms score above baseline on the pipeline's anthropomorphic-framing proportion for this domain (see \texttt{domain\_statistics.json}), consistent with pervasive hierarchical metaphor. "Caste" and "queen" form central hub terms with the highest betweenness centrality; "worker" and "slave" show parasitic terminology influence \cite{herbers2006}. The chain-like network structure reflects the linear hierarchies assumed by this vocabulary rather than the distributed organization documented in behavioral studies (Figures \ref{fig:concept_hierarchy}, \ref{fig:power_labor_frequencies}, \ref{fig:power_labor_ambiguities}).

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/concept_hierarchy.png}
\caption{Conceptual hierarchy in Power \& Labor domain showing how human social terminology structures scientific understanding of ant societies. The term "caste" creates direct parallels to human hierarchical systems \cite{crespi1992caste}, while terms like "queen" and "worker" impose role-based identities that may not reflect biological flexibility. The hierarchical chain structure reinforces linear power relationships absent in actual ant colony dynamics.}
\label{fig:concept_hierarchy}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/power_and_labor_term_frequencies.png}
\caption{Frequency analysis of Power \& Labor domain terminology. ``Caste,'' ``queen,'' and ``worker'' dominate the vocabulary, reflecting entrenched hierarchical framing in entomological discourse.}
\label{fig:power_labor_frequencies}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/power_and_labor_ambiguities.png}
\caption{Semantic entropy $H(t)$ for Power \& Labor domain terms (Eq.~\ref{eq:semantic_entropy}). \emph{Left}: per-term entropy sorted by descending $H(t)$, with context counts annotated; a dashed line marks the panel median. \emph{Right}: corpus frequency plotted against $H(t)$, with point size proportional to the number of extracted contexts per term. Terms such as ``caste'' and ``queen'' exhibit elevated entropy, consistent with their documented polysemy across hierarchical, reproductive, and behavioral research contexts.}
\label{fig:power_labor_ambiguities}
\end{figure}

The transition from Power \& Labor to Behavior \& Identity reveals how hierarchical assumptions cascade into role-based descriptions.

## Behavior & Identity

Behavioral descriptions create categorical identities that may obscure the biological fluidity documented in ant task-switching research \cite{ravary2007, gordon2010}. As \citet{gordon1992wittgenstein} argues—drawing on Wittgenstein's analysis of category boundaries—the act of classifying a nestmate as a "forager" or a "nurse" is not a neutral observation but an imposition of discrete categories onto continuous behavioral variation. Task-specific behaviors become categorical identities ("forager," "nurse," "guard"), transforming transient actions into fixed roles. Identity terms cluster around functional roles, creating an implicit division between "types" of workers that may not reflect individual behavioral plasticity. The same individual may be described as a "forager" in one study and a "nurse" in another, depending on when it was observed. \citeauthor{gordon2023ecology}'s \citeyearpar{gordon2023ecology} recent synthesis demonstrates that task allocation in harvester ant colonies operates entirely through local interaction networks—brief antennal contacts modulated by cuticular hydrocarbon profiles—without any centralized assignment. Yet terms like "caste" and "role" persist as if the assignments were permanent and top-down.

Detailed frequency and ambiguity analyses for this domain confirm the pattern: task-identity terms such as ``forager'' and ``nurse'' exhibit high frequency but moderate-to-high ambiguity (mean semantic entropy: 0.46 bits), reflecting the gap between categorical labels and fluid biological reality. Per-domain breakdowns are shown in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

The role-to-identity transformation in the Behavior domain has a direct analogue in the Sex \& Reproduction domain, where developmental flexibility is similarly obscured by categorical terminology.

## Sex \& Reproduction

Sex and reproduction terminology shows the lowest overall ambiguity but reveals a distinctive pattern of **binary opposition**—the dominant network structure in this domain (Figure \ref{fig:terminology_network}). Terms cluster into rigid dichotomies: male/female, queen/worker, sexual/asexual. These oppositions import mammalian sex-determination frameworks into a fundamentally different system: under haplodiploidy, males develop from unfertilized (haploid) eggs and females from fertilized (diploid) eggs, decoupling sex determination from the chromosomal mechanisms assumed by standard terminology \cite{chandra2021epigenetics}. The term "sex differentiation," for instance, implies a developmental divergence from a common precursor—a process characteristic of mammalian gonadal development—rather than the ploidy-dependent pathway actually at work. Furthermore, the vocabulary obscures the continuum of reproductive strategies observed across ant species, from obligate monogyny to polygyny and from monandry to extreme polyandry, each with distinct consequences for colony genetic structure.

Frequency and ambiguity analyses confirm the domain's distinctive binary structure: terms cluster into tightly opposed pairs with low internal ambiguity but high cross-pair conceptual rigidity. Full per-domain frequency and POS patterns are shown in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

## Kin \& Relatedness

Kin and Relatedness terminology exhibits moderate mean semantic entropy (0.25 bits) and a web-like network architecture reflecting the complex, non-intuitive relatedness structures of haplodiploid societies (Figure \ref{fig:domain_overview_grid}). The central tension is between human bilateral kinship models—where siblings share $r = 0.5$—and the haplodiploidy-specific asymmetry where full sisters share $r = 0.75$ but sisters relate to brothers at only $r = 0.25$. When researchers describe colony members as "sisters," the term imports an assumption of symmetry that masks the very asymmetry on which inclusive fitness theory depends.

Hub terms such as ``kin,'' ``relatedness,'' and ``inclusive fitness'' bridge multiple sub-domains. Network analysis reveals that Hamilton's-rule-adjacent vocabulary dominates the discourse, often at the expense of alternative frameworks such as multilevel selection. Analysis of kinship terminology shows that ``kin selection'' co-occurs with ``altruism'' and ``cooperation'' far more frequently than with ``conflict'' or ``policing,'' suggesting a framing bias toward cooperative explanations that may underrepresent intra-colony conflict dynamics. Per-domain frequency and pattern breakdowns are provided in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

## Economics

The Economics domain contains the smallest vocabulary (10 terms) and zero bridging terms (0)—the most insular domain by a substantial margin. For comparison, Power \& Labor contributes 43 bridging terms to adjacent domains, whereas Economics shares vocabulary with none. The complete term inventory reveals the character of this insularity: \textbf{allocation} ({{EXTRACTED_TERM_FREQ_ALLOCATION}} occurrences), \textbf{investment} ({{EXTRACTED_TERM_FREQ_INVESTMENT}}), \textbf{resources} ({{EXTRACTED_TERM_FREQ_RESOURCES}}), \textbf{resource} ({{EXTRACTED_TERM_FREQ_RESOURCE}}), and additional low-frequency terms including \textbf{trade-off}, \textbf{trade-offs}, \textbf{jack-of-all-trades}, and \textbf{gamma-distribution}. The final two are anomalies—terms pattern-matched to economics seed vocabulary that are, in practice, statistical and ecological constructs co-opted by economic framing, yet their presence reflects how pervasively the economic paradigm has colonized foraging ecology's conceptual substrate.

The semantically active core terms conflate two fundamentally different levels of explanation. "Cost" may refer to proximate energetic expenditure (measurable in joules) or to ultimate fitness reduction (requiring population-level inference); these distinct meanings are routinely treated as interchangeable. The same proximate–ultimate conflation operates across "investment," "resource allocation," and "trade-off." The resulting network architecture is self-contained: transaction-like term pairs ("cost–benefit," "allocation–resource") form tight clusters with 0 bridging edges to biological-mechanism clusters—indicating that economic terminology operates as a closed conceptual subsystem that resists integration with process-level descriptions.

Notably, Economics terms exhibit the highest mean semantic entropy (1.21 bits) of all domains despite zero bridging terms, confirming that economic metaphors form a self-contained but highly polysemous subsystem. The average extraction confidence is also the highest, indicating stable deployment within this insular vocabulary. This monoculture trades explanatory integration across domains for internal semantic precision. These patterns are shown across all domains in Figures \ref{fig:domain_overview_grid} and \ref{fig:domain_patterns_grid}.

## Longitudinal Case Studies

To understand how these linguistic paradigms evolve over time, we conducted longitudinal analysis on two critical terminology clusters: *Caste* and *Superorganism*.

### Caste Terminology Evolution

A clear historical trajectory emerges from rigid categories to plasticity-aware descriptions:

- **Foundational Era** (pre-1990): Rigid caste categories dominated descriptions of task allocation. Terms like "caste" and "subcaste" were used as if they denoted fixed, heritable phenotypes—analogous to social strata in human societies.
- **Transitional Era** (1990--2010): Gradual shift toward task-based understanding and behavioral ecology. \citeauthor{gordon1992wittgenstein}'s \citeyearpar{gordon1992wittgenstein} Wittgensteinian critique and accumulating behavioral data on task-switching challenged the categorical rigidity of caste vocabulary.
- **Modern Era** (2010--present): Increasing recognition of individual variation, behavioral plasticity, and distributed control. Epigenetic evidence \cite{chandra2021epigenetics, warner2024caste} reveals caste determination as a labile developmental process, further undermining the linguistic prior of fixed social categories.

### Superorganism Debate: Conceptual Evolution

The superorganism concept has undergone a parallel structural transformation. \citeauthor{wheeler1911}'s \citeyearpar{wheeler1911} early metaphor of the colony-as-organism organized a century of research while simultaneously constraining how individuality was conceptualized in social insect biology. More recent work has progressively replaced this metaphorical convenience with mathematically rigorous, multi-scale frameworks of biological individuality—particularly the Markov Blanket formalism \cite{friston2013life} and \citeauthor{boomsma2018superorganismality}'s \citeyearpar{boomsma2018superorganismality} analysis of how "superorganismality" was lost in translation between evolutionary and organismic biology. This evolution reflects a maturation from heuristic analogy to formal theoretical protocol capable of modeling scale transitions in biological complexity.
