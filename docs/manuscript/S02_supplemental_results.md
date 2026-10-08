# Supplemental Results {#sec:supplemental_results}

## Exploratory Pairwise Domain Comparisons

Table \ref{tab:pairwise_domain} presents pairwise comparisons of per-term semantic entropy between all Ento-Linguistic domains using Welch's two-sample $t$-tests. Raw $p$-values are computed from the $t$-distribution with Satterthwaite-approximated degrees of freedom; adjusted $p$-values correct for {{PAIRWISE_N_COMPARISONS}} simultaneous comparisons using the Benjamini-Hochberg (BH) procedure at $q = 0.05$. The effect size $d$ is a small-sample bias-corrected (Hedges-type) standardized difference. Conventional benchmarks of about 0.2, 0.5 and 0.8 \citep{cohen1988statistical} are rules of thumb that are not calibrated for these overlapping, dependent groups. Domain descriptives entering these tests are per-term valid-entropy means with exclusions counted.

\begin{table}[h]
\centering
\small
\begin{tabular}{|l|l|c|c|c|c|c|}
\hline
\textbf{Domain A} & \textbf{Domain B} & \textbf{$t$} & \textbf{$p$ (raw)} & \textbf{$p$ (BH)} & \textbf{Std.\ diff.\ $d$} & \textbf{Sig.\ (BH)} \\
\hline
Behavior \& Identity & Economics & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_ECONOMICS_T}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_ECONOMICS_P}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_ECONOMICS_P_BH}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_ECONOMICS_D}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_ECONOMICS_SIGNIFICANT}} \\
Behavior \& Identity & Kin \& Relatedness & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_KIN_AND_RELATEDNESS_T}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_KIN_AND_RELATEDNESS_P}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_KIN_AND_RELATEDNESS_P_BH}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_KIN_AND_RELATEDNESS_D}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_KIN_AND_RELATEDNESS_SIGNIFICANT}} \\
Behavior \& Identity & Power \& Labor & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_POWER_AND_LABOR_T}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_POWER_AND_LABOR_P}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_POWER_AND_LABOR_P_BH}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_POWER_AND_LABOR_D}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_POWER_AND_LABOR_SIGNIFICANT}} \\
Behavior \& Identity & Sex \& Reproduction & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_SEX_AND_REPRODUCTION_T}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_SEX_AND_REPRODUCTION_P}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_SEX_AND_REPRODUCTION_P_BH}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_SEX_AND_REPRODUCTION_D}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_SEX_AND_REPRODUCTION_SIGNIFICANT}} \\
Behavior \& Identity & Unit of Individuality & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_UNIT_OF_INDIVIDUALITY_T}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_UNIT_OF_INDIVIDUALITY_P}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_UNIT_OF_INDIVIDUALITY_P_BH}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_UNIT_OF_INDIVIDUALITY_D}} & {{PAIRWISE_BEHAVIOR_AND_IDENTITY_UNIT_OF_INDIVIDUALITY_SIGNIFICANT}} \\
Economics & Kin \& Relatedness & {{PAIRWISE_ECONOMICS_KIN_AND_RELATEDNESS_T}} & {{PAIRWISE_ECONOMICS_KIN_AND_RELATEDNESS_P}} & {{PAIRWISE_ECONOMICS_KIN_AND_RELATEDNESS_P_BH}} & {{PAIRWISE_ECONOMICS_KIN_AND_RELATEDNESS_D}} & {{PAIRWISE_ECONOMICS_KIN_AND_RELATEDNESS_SIGNIFICANT}} \\
Economics & Power \& Labor & {{PAIRWISE_ECONOMICS_POWER_AND_LABOR_T}} & {{PAIRWISE_ECONOMICS_POWER_AND_LABOR_P}} & {{PAIRWISE_ECONOMICS_POWER_AND_LABOR_P_BH}} & {{PAIRWISE_ECONOMICS_POWER_AND_LABOR_D}} & {{PAIRWISE_ECONOMICS_POWER_AND_LABOR_SIGNIFICANT}} \\
Economics & Sex \& Reproduction & {{PAIRWISE_ECONOMICS_SEX_AND_REPRODUCTION_T}} & {{PAIRWISE_ECONOMICS_SEX_AND_REPRODUCTION_P}} & {{PAIRWISE_ECONOMICS_SEX_AND_REPRODUCTION_P_BH}} & {{PAIRWISE_ECONOMICS_SEX_AND_REPRODUCTION_D}} & {{PAIRWISE_ECONOMICS_SEX_AND_REPRODUCTION_SIGNIFICANT}} \\
Economics & Unit of Individuality & {{PAIRWISE_ECONOMICS_UNIT_OF_INDIVIDUALITY_T}} & {{PAIRWISE_ECONOMICS_UNIT_OF_INDIVIDUALITY_P}} & {{PAIRWISE_ECONOMICS_UNIT_OF_INDIVIDUALITY_P_BH}} & {{PAIRWISE_ECONOMICS_UNIT_OF_INDIVIDUALITY_D}} & {{PAIRWISE_ECONOMICS_UNIT_OF_INDIVIDUALITY_SIGNIFICANT}} \\
Kin \& Relatedness & Power \& Labor & {{PAIRWISE_KIN_AND_RELATEDNESS_POWER_AND_LABOR_T}} & {{PAIRWISE_KIN_AND_RELATEDNESS_POWER_AND_LABOR_P}} & {{PAIRWISE_KIN_AND_RELATEDNESS_POWER_AND_LABOR_P_BH}} & {{PAIRWISE_KIN_AND_RELATEDNESS_POWER_AND_LABOR_D}} & {{PAIRWISE_KIN_AND_RELATEDNESS_POWER_AND_LABOR_SIGNIFICANT}} \\
Kin \& Relatedness & Sex \& Reproduction & {{PAIRWISE_KIN_AND_RELATEDNESS_SEX_AND_REPRODUCTION_T}} & {{PAIRWISE_KIN_AND_RELATEDNESS_SEX_AND_REPRODUCTION_P}} & {{PAIRWISE_KIN_AND_RELATEDNESS_SEX_AND_REPRODUCTION_P_BH}} & {{PAIRWISE_KIN_AND_RELATEDNESS_SEX_AND_REPRODUCTION_D}} & {{PAIRWISE_KIN_AND_RELATEDNESS_SEX_AND_REPRODUCTION_SIGNIFICANT}} \\
Kin \& Relatedness & Unit of Individuality & {{PAIRWISE_KIN_AND_RELATEDNESS_UNIT_OF_INDIVIDUALITY_T}} & {{PAIRWISE_KIN_AND_RELATEDNESS_UNIT_OF_INDIVIDUALITY_P}} & {{PAIRWISE_KIN_AND_RELATEDNESS_UNIT_OF_INDIVIDUALITY_P_BH}} & {{PAIRWISE_KIN_AND_RELATEDNESS_UNIT_OF_INDIVIDUALITY_D}} & {{PAIRWISE_KIN_AND_RELATEDNESS_UNIT_OF_INDIVIDUALITY_SIGNIFICANT}} \\
Power \& Labor & Sex \& Reproduction & {{PAIRWISE_POWER_AND_LABOR_SEX_AND_REPRODUCTION_T}} & {{PAIRWISE_POWER_AND_LABOR_SEX_AND_REPRODUCTION_P}} & {{PAIRWISE_POWER_AND_LABOR_SEX_AND_REPRODUCTION_P_BH}} & {{PAIRWISE_POWER_AND_LABOR_SEX_AND_REPRODUCTION_D}} & {{PAIRWISE_POWER_AND_LABOR_SEX_AND_REPRODUCTION_SIGNIFICANT}} \\
Power \& Labor & Unit of Individuality & {{PAIRWISE_POWER_AND_LABOR_UNIT_OF_INDIVIDUALITY_T}} & {{PAIRWISE_POWER_AND_LABOR_UNIT_OF_INDIVIDUALITY_P}} & {{PAIRWISE_POWER_AND_LABOR_UNIT_OF_INDIVIDUALITY_P_BH}} & {{PAIRWISE_POWER_AND_LABOR_UNIT_OF_INDIVIDUALITY_D}} & {{PAIRWISE_POWER_AND_LABOR_UNIT_OF_INDIVIDUALITY_SIGNIFICANT}} \\
Sex \& Reproduction & Unit of Individuality & {{PAIRWISE_SEX_AND_REPRODUCTION_UNIT_OF_INDIVIDUALITY_T}} & {{PAIRWISE_SEX_AND_REPRODUCTION_UNIT_OF_INDIVIDUALITY_P}} & {{PAIRWISE_SEX_AND_REPRODUCTION_UNIT_OF_INDIVIDUALITY_P_BH}} & {{PAIRWISE_SEX_AND_REPRODUCTION_UNIT_OF_INDIVIDUALITY_D}} & {{PAIRWISE_SEX_AND_REPRODUCTION_UNIT_OF_INDIVIDUALITY_SIGNIFICANT}} \\
\hline
\end{tabular}
\caption{Exploratory pairwise Welch tests on valid per-term sentence-context entropy, with Benjamini--Hochberg adjusted $p$-values over {{PAIRWISE_N_COMPARISONS}} comparisons and standardized effect sizes. Threshold flags use $q=0.05$; domain groups share terms and contexts, so the flags are exploratory (Supplemental Section \ref{sec:supplemental_infrastructure}). The omnibus ANOVA yields $F({{ANOVA_DF1}},{{ANOVA_DF2}})={{ANOVA_F}}$, $p$-value {{ANOVA_P}}, and $\eta^2={{ANOVA_ETA_SQUARED}}$.}
\label{tab:pairwise_domain}
\end{table}

## CACE Scoring for Key Terms

Table \ref{tab:cace_full} presents full CACE evaluations for a representative set of entomological terms, comparing anthropomorphic labels with proposed functional alternatives.

\begin{table}[h]
\centering
\small
\begin{tabular}{|l|c|c|c|c|c|c|}
\hline
\textbf{Term} & \textbf{C} & \textbf{A} & \textbf{Cs} & \textbf{E} & \textbf{Mean} & \textbf{Extracted} \\
\hline
queen & {{CACE_TERM_QUEEN_CLARITY}} & {{CACE_TERM_QUEEN_APPROPRIATENESS}} & {{CACE_TERM_QUEEN_CONSISTENCY}} & {{CACE_TERM_QUEEN_EVOLVABILITY}} & {{CACE_TERM_QUEEN_AGGREGATE}} & {{CACE_TERM_QUEEN_IN_CORPUS}} \\
\textit{primary reproductive} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_CLARITY}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_APPROPRIATENESS}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_CONSISTENCY}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_EVOLVABILITY}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_AGGREGATE}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_IN_CORPUS}} \\
\hline
worker & {{CACE_TERM_WORKER_CLARITY}} & {{CACE_TERM_WORKER_APPROPRIATENESS}} & {{CACE_TERM_WORKER_CONSISTENCY}} & {{CACE_TERM_WORKER_EVOLVABILITY}} & {{CACE_TERM_WORKER_AGGREGATE}} & {{CACE_TERM_WORKER_IN_CORPUS}} \\
\textit{non-reproductive helper} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_CLARITY}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_APPROPRIATENESS}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_CONSISTENCY}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_EVOLVABILITY}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_AGGREGATE}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_IN_CORPUS}} \\
\hline
slave & {{CACE_TERM_SLAVE_CLARITY}} & {{CACE_TERM_SLAVE_APPROPRIATENESS}} & {{CACE_TERM_SLAVE_CONSISTENCY}} & {{CACE_TERM_SLAVE_EVOLVABILITY}} & {{CACE_TERM_SLAVE_AGGREGATE}} & {{CACE_TERM_SLAVE_IN_CORPUS}} \\
\textit{host worker} & {{CACE_TERM_HOST_WORKER_CLARITY}} & {{CACE_TERM_HOST_WORKER_APPROPRIATENESS}} & {{CACE_TERM_HOST_WORKER_CONSISTENCY}} & {{CACE_TERM_HOST_WORKER_EVOLVABILITY}} & {{CACE_TERM_HOST_WORKER_AGGREGATE}} & {{CACE_TERM_HOST_WORKER_IN_CORPUS}} \\
\hline
caste & {{CACE_TERM_CASTE_CLARITY}} & {{CACE_TERM_CASTE_APPROPRIATENESS}} & {{CACE_TERM_CASTE_CONSISTENCY}} & {{CACE_TERM_CASTE_EVOLVABILITY}} & {{CACE_TERM_CASTE_AGGREGATE}} & {{CACE_TERM_CASTE_IN_CORPUS}} \\
\textit{task group} & {{CACE_TERM_TASK_GROUP_CLARITY}} & {{CACE_TERM_TASK_GROUP_APPROPRIATENESS}} & {{CACE_TERM_TASK_GROUP_CONSISTENCY}} & {{CACE_TERM_TASK_GROUP_EVOLVABILITY}} & {{CACE_TERM_TASK_GROUP_AGGREGATE}} & {{CACE_TERM_TASK_GROUP_IN_CORPUS}} \\
\hline
soldier & {{CACE_TERM_SOLDIER_CLARITY}} & {{CACE_TERM_SOLDIER_APPROPRIATENESS}} & {{CACE_TERM_SOLDIER_CONSISTENCY}} & {{CACE_TERM_SOLDIER_EVOLVABILITY}} & {{CACE_TERM_SOLDIER_AGGREGATE}} & {{CACE_TERM_SOLDIER_IN_CORPUS}} \\
\textit{major worker} & {{CACE_TERM_MAJOR_WORKER_CLARITY}} & {{CACE_TERM_MAJOR_WORKER_APPROPRIATENESS}} & {{CACE_TERM_MAJOR_WORKER_CONSISTENCY}} & {{CACE_TERM_MAJOR_WORKER_EVOLVABILITY}} & {{CACE_TERM_MAJOR_WORKER_AGGREGATE}} & {{CACE_TERM_MAJOR_WORKER_IN_CORPUS}} \\
\hline
colony & {{CACE_TERM_COLONY_CLARITY}} & {{CACE_TERM_COLONY_APPROPRIATENESS}} & {{CACE_TERM_COLONY_CONSISTENCY}} & {{CACE_TERM_COLONY_EVOLVABILITY}} & {{CACE_TERM_COLONY_AGGREGATE}} & {{CACE_TERM_COLONY_IN_CORPUS}} \\
haplodiploidy & {{CACE_TERM_HAPLODIPLOIDY_CLARITY}} & {{CACE_TERM_HAPLODIPLOIDY_APPROPRIATENESS}} & {{CACE_TERM_HAPLODIPLOIDY_CONSISTENCY}} & {{CACE_TERM_HAPLODIPLOIDY_EVOLVABILITY}} & {{CACE_TERM_HAPLODIPLOIDY_AGGREGATE}} & {{CACE_TERM_HAPLODIPLOIDY_IN_CORPUS}} \\
trophallaxis & {{CACE_TERM_TROPHALLAXIS_CLARITY}} & {{CACE_TERM_TROPHALLAXIS_APPROPRIATENESS}} & {{CACE_TERM_TROPHALLAXIS_CONSISTENCY}} & {{CACE_TERM_TROPHALLAXIS_EVOLVABILITY}} & {{CACE_TERM_TROPHALLAXIS_AGGREGATE}} & {{CACE_TERM_TROPHALLAXIS_IN_CORPUS}} \\
\hline
\end{tabular}
\caption{Heuristic representative-term CACE scores: C is Clarity, A Appropriateness, Cs Consistency, and E Evolvability; Mean weights them equally. Extracted indicates membership in the extracted vocabulary, not phrase presence anywhere in the source text. Unextracted alternatives use fallback conventions. Defaults and vocabulary penalties are not independently measured clarity, biological accuracy, or evidence of terminology-reform benefit.}
\label{tab:cace_full}
\end{table}

## Semantic Entropy Distribution

Table \ref{tab:entropy_distribution} summarizes the distribution of semantic entropy across domains.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Domain} & \textbf{Mean $H$ (bits)} & \textbf{High-entropy terms (\%)} & \textbf{$N$} \\
\hline
Economics & {{DOMAIN_ECONOMICS_ENTROPY}} & {{DOMAIN_ECONOMICS_HIGH_ENTROPY_PCT}} & {{DOMAIN_ECONOMICS_N_TERMS}} \\
Power \& Labor & {{DOMAIN_POWER_AND_LABOR_ENTROPY}} & {{DOMAIN_POWER_AND_LABOR_HIGH_ENTROPY_PCT}} & {{DOMAIN_POWER_AND_LABOR_N_TERMS}} \\
Behavior \& Identity & {{DOMAIN_BEHAVIOR_AND_IDENTITY_ENTROPY}} & {{DOMAIN_BEHAVIOR_AND_IDENTITY_HIGH_ENTROPY_PCT}} & {{DOMAIN_BEHAVIOR_AND_IDENTITY_N_TERMS}} \\
Sex \& Reproduction & {{DOMAIN_SEX_AND_REPRODUCTION_ENTROPY}} & {{DOMAIN_SEX_AND_REPRODUCTION_HIGH_ENTROPY_PCT}} & {{DOMAIN_SEX_AND_REPRODUCTION_N_TERMS}} \\
Unit of Individuality & {{DOMAIN_UNIT_OF_INDIVIDUALITY_ENTROPY}} & {{DOMAIN_UNIT_OF_INDIVIDUALITY_HIGH_ENTROPY_PCT}} & {{DOMAIN_UNIT_OF_INDIVIDUALITY_N_TERMS}} \\
Kin \& Relatedness & {{DOMAIN_KIN_AND_RELATEDNESS_ENTROPY}} & {{DOMAIN_KIN_AND_RELATEDNESS_HIGH_ENTROPY_PCT}} & {{DOMAIN_KIN_AND_RELATEDNESS_N_TERMS}} \\
\hline
\textbf{Overall} & {{CORPUS_OVERALL_ENTROPY}} & {{CORPUS_OVERALL_HIGH_ENTROPY_PCT}} & \textbf{ {{CORPUS_OVERALL_N_TERMS}} } \\
\hline
\end{tabular}
\caption{Distribution of sentence-context entropy $H(t)$ across Ento-Linguistic domains (Eq.~\ref{eq:semantic_entropy}; cluster-count rule in Methods). High-entropy terms exceed $H > 2.0$ bits; the statistic summarizes occupancy of computational clusters, not annotated senses. Normalized entropy divides by $\log_2 k_{\mathrm{occupied}}$ and is zero when one cluster is occupied. $N$ counts terms with usable estimates; Overall sums valid domain memberships, so a multi-domain term can count more than once, and its mean and high-entropy percentage use that same denominator.}
\label{tab:entropy_distribution}
\end{table}

## Interval Reporting

The statistics artifact reports per-term valid-entropy descriptives (means and standard deviations, with exclusions counted) and the inferential results in Table \ref{tab:pairwise_domain}; it does not compute domain-level confidence intervals, so per-domain ambiguity-score and context-variability intervals are not tabulated here. Exploratory numerical differences are summarized by the Welch $t$-tests and the omnibus ANOVA reported in Table \ref{tab:pairwise_domain}, with per-domain entropy descriptives in Table \ref{tab:entropy_distribution} and the summary in Figure \ref{fig:statistical_analysis}.

## Full-Text Parallel Layer

A complementary descriptive analysis was run over {{FULLTEXT_DOCUMENTS}} open
access full texts harvested from PubMed Central (PMC). The abstract corpus
remains the headline corpus of this study; the full-text layer is reported
here as a separate convenience sample with a higher extraction threshold. The analysis machinery is shared: the same
terminology extraction, domain assignment, semantic-entropy, and CACE
scoring implementations are applied to full texts (Figure
\ref{fig:fulltext_analysis}).

The layer comprises {{FULLTEXT_TOTAL_TOKENS}} tokens of running text, with a
per-document median of {{FULLTEXT_MEDIAN_TOKENS}} tokens. Table
\ref{tab:fulltext_domain} reports per-domain term counts and mean semantic
entropy over the full texts; {{FULLTEXT_PAIRWISE_N}} pairwise Welch
$t$-tests (Benjamini-Hochberg corrected, as in Table
\ref{tab:pairwise_domain}) accompany the omnibus one-way ANOVA on per-term
semantic entropy, $F = {{FULLTEXT_ANOVA_F}}$, $p$-value {{FULLTEXT_ANOVA_P}}.

Anthropomorphic framing over the same full texts is scored as the
proportion of domain-term occurrence contexts containing an anthropomorphic
framing marker, using the same patterns as the abstract layer: {{FULLTEXT_ANTHROPOMORPHIC_OVERALL}}
overall, with Economics at
{{FULLTEXT_DOMAIN_ECONOMICS_ANTHROPOMORPHIC}} against
{{FULLTEXT_DOMAIN_UNIT_OF_INDIVIDUALITY_ANTHROPOMORPHIC}} for Unit of
Individuality and {{FULLTEXT_DOMAIN_BEHAVIOR_AND_IDENTITY_ANTHROPOMORPHIC}}
for Behavior \& Identity.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|}
\hline
\textbf{Domain} & \textbf{Terms extracted} & \textbf{Mean $H$ (bits)} \\
\hline
Behavior \& Identity & {{FULLTEXT_DOMAIN_BEHAVIOR_AND_IDENTITY_TERMS}} & {{FULLTEXT_DOMAIN_BEHAVIOR_AND_IDENTITY_ENTROPY}} \\
Economics & {{FULLTEXT_DOMAIN_ECONOMICS_TERMS}} & {{FULLTEXT_DOMAIN_ECONOMICS_ENTROPY}} \\
Kin \& Relatedness & {{FULLTEXT_DOMAIN_KIN_AND_RELATEDNESS_TERMS}} & {{FULLTEXT_DOMAIN_KIN_AND_RELATEDNESS_ENTROPY}} \\
Power \& Labor & {{FULLTEXT_DOMAIN_POWER_AND_LABOR_TERMS}} & {{FULLTEXT_DOMAIN_POWER_AND_LABOR_ENTROPY}} \\
Sex \& Reproduction & {{FULLTEXT_DOMAIN_SEX_AND_REPRODUCTION_TERMS}} & {{FULLTEXT_DOMAIN_SEX_AND_REPRODUCTION_ENTROPY}} \\
Unit of Individuality & {{FULLTEXT_DOMAIN_UNIT_OF_INDIVIDUALITY_TERMS}} & {{FULLTEXT_DOMAIN_UNIT_OF_INDIVIDUALITY_ENTROPY}} \\
\hline
\end{tabular}
\caption{Per-domain terminology in the PMC full-text parallel layer: extracted-term counts and mean semantic entropy $H(t)$, computed over valid estimates with the same pipeline as the abstract layer; valid-estimate counts appear in Figure \ref{fig:fulltext_analysis}. Term extraction uses a higher minimum token frequency than the abstract layer because full texts are substantially longer.}
\label{tab:fulltext_domain}
\end{table}

## Discourse and Rhetorical Layer

A shared discourse stage counts rule-based markers of discourse patterns,
rhetorical strategies, argumentative structures, and persuasive techniques
in both layers. Texts shorter than {{ABSTRACT_DISCOURSE_MIN_TEXT_LENGTH}}
characters are excluded. The abstract pass therefore covers
{{ABSTRACT_DISCOURSE_N_ANALYZED}} texts ({{ABSTRACT_DISCOURSE_EXCLUDED_MIN_LENGTH}}
excluded as too short; {{ABSTRACT_DISCOURSE_SAMPLE_PERCENT}}\% of the
eligible texts). The full-text pass covers {{FULLTEXT_DISCOURSE_N_ANALYZED}}
of {{FULLTEXT_DOCUMENTS}} texts, a deterministic
{{FULLTEXT_DISCOURSE_SAMPLE_PERCENT}}\% sample of eligible texts drawn to keep
the pass computationally bounded. Figure \ref{fig:discourse_comparison}
compares the two layers; panels spanning orders of magnitude use a symlog
frequency axis.

Discourse patterns occur {{ABSTRACT_PATTERNS_HIERARCHICAL_FRAMING}}
times as hierarchical framing in the abstract layer against
{{FULLTEXT_PATTERNS_HIERARCHICAL_FRAMING}} occurrences in the
full-text layer, with {{ABSTRACT_PATTERNS_ECONOMIC_METAPHORS}} versus
{{FULLTEXT_PATTERNS_ECONOMIC_METAPHORS}} economic metaphors,
{{ABSTRACT_PATTERNS_ANTHROPOMORPHIC_FRAMING}} versus
{{FULLTEXT_PATTERNS_ANTHROPOMORPHIC_FRAMING}} anthropomorphic framings,
and {{ABSTRACT_PATTERNS_SCALE_AMBIGUITY}} versus
{{FULLTEXT_PATTERNS_SCALE_AMBIGUITY}} scale-ambiguous constructions.

Rhetorical-strategy marker counts in the two layers are:
{{ABSTRACT_RHETORICAL_ANECDOTAL}} anecdotal markers in the abstract
layer versus {{FULLTEXT_RHETORICAL_ANECDOTAL}} in full texts,
{{ABSTRACT_RHETORICAL_AUTHORITY}} versus
{{FULLTEXT_RHETORICAL_AUTHORITY}} authority markers,
{{ABSTRACT_RHETORICAL_ANALOGY}} versus
{{FULLTEXT_RHETORICAL_ANALOGY}} analogies, and
{{ABSTRACT_RHETORICAL_GENERALIZATION}} versus
{{FULLTEXT_RHETORICAL_GENERALIZATION}} generalizations.

The argumentative-structure pass identifies
{{ABSTRACT_ARG_STRUCTURES}} argumentative structures in the abstract
layer versus {{FULLTEXT_ARG_STRUCTURES}} in the full-text sample.
Metaphorical-language markers occur
{{ABSTRACT_PERSUASIVE_METAPHORICAL}} times in the abstract layer
against {{FULLTEXT_PERSUASIVE_METAPHORICAL}} occurrences in full
texts. All frequencies are raw marker counts. The layers differ in size
and sampling, so these counts are not prevalence comparisons.

\clearpage

## Statistical and Source-Layer Figures

Figures \ref{fig:statistical_analysis}--\ref{fig:arxiv_analysis} summarize the headline statistics, the PMC full-text layer, the cross-layer comparison, the discourse markers and the separate arXiv preprint layer.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/statistical_analysis.png}
\caption{Headline valid-entropy descriptives with nominal intervals, bias-corrected standardized differences, and exploratory ANOVA. Bar annotations report valid term counts; overlapping domain memberships and shared document contexts limit population inference.}
\label{fig:statistical_analysis}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/fulltext_analysis.png}
\caption{Separate PMC full-text statistics over all stored records by default. Extraction thresholds and context distributions differ from the abstract layer. Nominal intervals and multiplicity-adjusted threshold flags remain exploratory.}
\label{fig:fulltext_analysis}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/layer_comparison.png}
\caption{Mean valid context-cluster entropy in the abstract and PMC layers, with valid-term counts. This compares distinct convenience samples and extraction thresholds; it is not a matched robustness experiment or evidence of causal language effects.}
\label{fig:layer_comparison}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/discourse_comparison.png}
\caption{Lexical discourse, rhetorical and persuasive-pattern counts, with analyzed-text counts shown in the legend. PMC uses an explicitly bounded text sample. Raw frequencies depend on sample size and text length and must not be read as normalized prevalence or human-validated author intent.}
\label{fig:discourse_comparison}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/arxiv_analysis.png}
\caption{Separate arXiv preprint-layer descriptives and exploratory comparisons. Some groups have only one valid entropy estimate, for which intervals are omitted; very small groups and nearly zero within-group variance can yield large standardized differences without establishing generalizable effects.}
\label{fig:arxiv_analysis}
\end{figure}
