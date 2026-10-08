# Results: Domain-Specific Findings {#sec:domain_findings}

The six domains organize descriptive outputs and questions for qualitative interpretation. Their assignments follow the configured vocabulary and lexical rules. Domain-specific statements below do not infer cognitive bias, biological mechanisms, or author intent from term counts.

## Unit of Individuality

This vocabulary includes references to individuals, colonies, and collective organization. Its mean computed sentence-context entropy is {{DOMAIN_UNIT_OF_INDIVIDUALITY_ENTROPY}} bits. Frequency and word-formation panels describe extracted surface forms, while the scale panel counts keyword matches in term names. These counts do not estimate biological boundaries. Figures \ref{fig:domain_overview_grid}, \ref{fig:domain_patterns_grid}, and \ref{fig:unit_individuality_patterns} support inspection of the extraction.

## Power \& Labor

Power and Labor contains {{DOMAIN_POWER_AND_LABOR_TERMS}} assigned terms and {{DOMAIN_POWER_AND_LABOR_BRIDGING}} terms with multiple labels. Its occurrence-context anthropomorphic-marker proportion is {{DOMAIN_POWER_AND_LABOR_ANTHROPOMORPHIC_PROPORTION_PCT}}\%, rather than a percentage of authors or publications using misleading language. Discussions of loaded terminology motivate contextual examination \citep{herbers2006, herbers2007}. Molecular work on caste \citep{sumner2018molecular} and developmental canalization \citep{qiu2022canalized} also make it important to distinguish developmental phenotypes from temporary task categories.

Figures \ref{fig:power_labor_frequencies} and \ref{fig:power_labor_ambiguities} show observed term frequency and context-cluster entropy. Figure \ref{fig:concept_hierarchy} ranks predefined concept categories by summed vocabulary overlap; it does not show a biological hierarchy or term-level betweenness.

## Behavior \& Identity

The mean computed sentence-context entropy is {{DOMAIN_BEHAVIOR_AND_IDENTITY_ENTROPY}} bits. Task labels provide useful candidates for context annotation. Evidence of behavioral flexibility in ants \citep{ravary2007, gordon2010} motivates asking when a label denotes an observation, a persistent propensity, or a morphological category. The corpus statistics alone do not establish that categorical labels obscure that flexibility.

## Sex \& Reproduction

This domain groups reproductive and developmental terminology. Its mean computed entropy is {{DOMAIN_SEX_AND_REPRODUCTION_ENTROPY}} bits. The presence of paired labels does not by itself demonstrate a conceptual opposition. Reproductive systems and caste development vary across taxa, and the epigenetic review \citep{oldroyd2021epigenetics} provides background rather than validation of a lexical classifier.

## Kin \& Relatedness

The mean computed entropy is {{DOMAIN_KIN_AND_RELATEDNESS_ENTROPY}} bits. Relatedness terms require biological and demographic context: numerical coefficients depend on pedigrees, mating systems, and population structure. The present outputs do not estimate those quantities.

## Economics

The classifier assigns {{DOMAIN_ECONOMICS_TERMS}} terms to Economics, with {{DOMAIN_ECONOMICS_BRIDGING}} receiving multiple labels. Its mean computed entropy is {{DOMAIN_ECONOMICS_ENTROPY}} bits. Low overlap can follow directly from lexicon design; a zero overlap does not establish a closed conceptual subsystem. Terms such as allocation ({{TERM_FREQ_ALLOCATION}} occurrences), investment ({{TERM_FREQ_INVESTMENT}}), resource ({{TERM_FREQ_RESOURCE}}), and resources ({{TERM_FREQ_RESOURCES}}) warrant examination of their operational definitions. Statistical or ecological compounds matching a seed word can be classification errors rather than evidence of economic framing.

## Historical Interpretation

Historical readings of caste and superorganism terminology provide context \citep{wheeler1911, gordon1992wittgenstein, boomsma2018superorganismality}. The BHL era analysis in Section \ref{sec:bhl_grounding} reports literal OCR frequencies and explicitly sampled stack outputs. Changes in those rates do not independently establish changes in conceptual commitments, the origin of a concept, or progress toward more accurate biological explanation.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/domain_overview_grid.png}
\caption{Ten highest-frequency extracted terms per domain. Bar length is corpus frequency and color is the attached sentence-context entropy estimate. Zero-valued defaults for insufficient contexts must not be interpreted as evidence of unambiguous meaning. These are descriptive extraction outputs from the source-identified abstract layer.}
\label{fig:domain_overview_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/domain_patterns_grid.png}
\caption{Surface word-formation composition of assigned vocabularies. Each term is assigned to exactly one surface category (single word, multi-word phrase, hyphenated or underscore compound, or containing digits), using the same classifier as Figure \ref{fig:unit_individuality_patterns}. The headline extractor does not independently add n-grams, so availability of a category in the plotting utility does not establish its extraction.}
\label{fig:domain_patterns_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/unit_of_individuality_patterns.png}
\caption{Unit of Individuality term-formation counts (left) and counts of term names matching scale keyword groups (right). Scale groups can overlap; true zeros are retained. Neither panel estimates actual biological scale boundaries.}
\label{fig:unit_individuality_patterns}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/concept_hierarchy.png}
\caption{Overlap strength of the six predefined concept categories: each category's weighted degree, the sum of its overlap coefficients with the other categories (Eq.~\ref{eq:overlap_coefficient}), ranked (left) and plotted against associated-term counts (right). Every category links to every other, so unweighted degree would not distinguish them. The display does not represent a biological command hierarchy.}
\label{fig:concept_hierarchy}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/power_and_labor_term_frequencies.png}
\caption{The fifteen highest-frequency assigned Power and Labor terms in the source-identified abstract layer. Frequency is annotated; color tracks rank. These observations do not quantify hierarchical control or bias.}
\label{fig:power_labor_frequencies}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/power_and_labor_ambiguities.png}
\caption{Power and Labor terms ranked by attached context-cluster entropy, with corpus frequency and short extraction-context counts. Sentence-context entropy and the plotted extraction-window counts use different context definitions. Cluster entropy is not an independently validated ambiguity measure.}
\label{fig:power_labor_ambiguities}
\end{figure}
