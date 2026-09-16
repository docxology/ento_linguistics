# Supplemental Results {#sec:supplemental_results}

## Pairwise Domain Comparisons

Table \ref{tab:pairwise_domain} presents pairwise comparisons of per-term semantic entropy between all Ento-Linguistic domains using Welch's two-sample $t$-tests. Raw $p$-values are computed from the $t$-distribution with Satterthwaite-approximated degrees of freedom; adjusted $p$-values correct for {{PAIRWISE_N_COMPARISONS}} simultaneous comparisons using the Benjamini-Hochberg (BH) procedure at $q = 0.05$. Cohen's $d$ quantifies effect size, interpreted as small ($d \approx 0.2$), medium ($d \approx 0.5$), or large ($d \geq 0.8$). Domain descriptives entering these tests are per-term valid-entropy means with exclusions counted.

\begin{table}[h]
\centering
\small
\begin{tabular}{|l|l|c|c|c|c|c|}
\hline
\textbf{Domain A} & \textbf{Domain B} & \textbf{$t$} & \textbf{$p$ (raw)} & \textbf{$p$ (BH)} & \textbf{Cohen's $d$} & \textbf{Sig.\ (BH)} \\
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
\caption{Pairwise Welch's $t$-tests on per-term semantic entropy between Ento-Linguistic domains, with Benjamini-Hochberg adjusted $p$-values ({{CORRECTION_METHOD}} correction over {{PAIRWISE_N_COMPARISONS}} comparisons) and Cohen's $d$ effect sizes. The Sig.\ (BH) column reports BH-adjusted significance at $q = 0.05$ for each comparison. Domain descriptives feeding these tests are per-term valid-entropy means with exclusions counted. The omnibus one-way ANOVA across the six domains on {{ANOVA_METRIC}} yields $F({{ANOVA_DF1}}, {{ANOVA_DF2}}) = {{ANOVA_F}}$, {{ANOVA_P}}, $\eta^2 = {{ANOVA_ETA_SQUARED}}$, where $df_1 = k - 1$ (between-group) and $df_2 = N - k$ (within-group).}
\label{tab:pairwise_domain}
\end{table}

## CACE Scoring for Key Terms

Table \ref{tab:cace_full} presents full CACE evaluations for a representative set of entomological terms, comparing anthropomorphic labels with proposed functional alternatives.

\begin{table}[h]
\centering
\small
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{Term} & \textbf{Clarity} & \textbf{Appropriateness} & \textbf{Consistency} & \textbf{Evolvability} & \textbf{Aggregate} \\
\hline
queen & {{CACE_TERM_QUEEN_CLARITY}} & {{CACE_TERM_QUEEN_APPROPRIATENESS}} & {{CACE_TERM_QUEEN_CONSISTENCY}} & {{CACE_TERM_QUEEN_EVOLVABILITY}} & {{CACE_TERM_QUEEN_AGGREGATE}} \\
\textit{primary reproductive} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_CLARITY}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_APPROPRIATENESS}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_CONSISTENCY}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_EVOLVABILITY}} & {{CACE_TERM_PRIMARY_REPRODUCTIVE_AGGREGATE}} \\
\hline
worker & {{CACE_TERM_WORKER_CLARITY}} & {{CACE_TERM_WORKER_APPROPRIATENESS}} & {{CACE_TERM_WORKER_CONSISTENCY}} & {{CACE_TERM_WORKER_EVOLVABILITY}} & {{CACE_TERM_WORKER_AGGREGATE}} \\
\textit{non-reproductive helper} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_CLARITY}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_APPROPRIATENESS}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_CONSISTENCY}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_EVOLVABILITY}} & {{CACE_TERM_NON_REPRODUCTIVE_HELPER_AGGREGATE}} \\
\hline
slave & {{CACE_TERM_SLAVE_CLARITY}} & {{CACE_TERM_SLAVE_APPROPRIATENESS}} & {{CACE_TERM_SLAVE_CONSISTENCY}} & {{CACE_TERM_SLAVE_EVOLVABILITY}} & {{CACE_TERM_SLAVE_AGGREGATE}} \\
\textit{host worker} & {{CACE_TERM_HOST_WORKER_CLARITY}} & {{CACE_TERM_HOST_WORKER_APPROPRIATENESS}} & {{CACE_TERM_HOST_WORKER_CONSISTENCY}} & {{CACE_TERM_HOST_WORKER_EVOLVABILITY}} & {{CACE_TERM_HOST_WORKER_AGGREGATE}} \\
\hline
caste & {{CACE_TERM_CASTE_CLARITY}} & {{CACE_TERM_CASTE_APPROPRIATENESS}} & {{CACE_TERM_CASTE_CONSISTENCY}} & {{CACE_TERM_CASTE_EVOLVABILITY}} & {{CACE_TERM_CASTE_AGGREGATE}} \\
\textit{task group} & {{CACE_TERM_TASK_GROUP_CLARITY}} & {{CACE_TERM_TASK_GROUP_APPROPRIATENESS}} & {{CACE_TERM_TASK_GROUP_CONSISTENCY}} & {{CACE_TERM_TASK_GROUP_EVOLVABILITY}} & {{CACE_TERM_TASK_GROUP_AGGREGATE}} \\
\hline
soldier & {{CACE_TERM_SOLDIER_CLARITY}} & {{CACE_TERM_SOLDIER_APPROPRIATENESS}} & {{CACE_TERM_SOLDIER_CONSISTENCY}} & {{CACE_TERM_SOLDIER_EVOLVABILITY}} & {{CACE_TERM_SOLDIER_AGGREGATE}} \\
\textit{major worker} & {{CACE_TERM_MAJOR_WORKER_CLARITY}} & {{CACE_TERM_MAJOR_WORKER_APPROPRIATENESS}} & {{CACE_TERM_MAJOR_WORKER_CONSISTENCY}} & {{CACE_TERM_MAJOR_WORKER_EVOLVABILITY}} & {{CACE_TERM_MAJOR_WORKER_AGGREGATE}} \\
\hline
colony & {{CACE_TERM_COLONY_CLARITY}} & {{CACE_TERM_COLONY_APPROPRIATENESS}} & {{CACE_TERM_COLONY_CONSISTENCY}} & {{CACE_TERM_COLONY_EVOLVABILITY}} & {{CACE_TERM_COLONY_AGGREGATE}} \\
haplodiploidy & {{CACE_TERM_HAPLODIPLOIDY_CLARITY}} & {{CACE_TERM_HAPLODIPLOIDY_APPROPRIATENESS}} & {{CACE_TERM_HAPLODIPLOIDY_CONSISTENCY}} & {{CACE_TERM_HAPLODIPLOIDY_EVOLVABILITY}} & {{CACE_TERM_HAPLODIPLOIDY_AGGREGATE}} \\
trophallaxis & {{CACE_TERM_TROPHALLAXIS_CLARITY}} & {{CACE_TERM_TROPHALLAXIS_APPROPRIATENESS}} & {{CACE_TERM_TROPHALLAXIS_CONSISTENCY}} & {{CACE_TERM_TROPHALLAXIS_EVOLVABILITY}} & {{CACE_TERM_TROPHALLAXIS_AGGREGATE}} \\
\hline
\end{tabular}
\caption{CACE dimension scores for representative entomological terms. Anthropomorphic terms (queen, worker, slave, caste, soldier) consistently score lower than functional alternatives (italicized). The largest improvements arise in Appropriateness (no anthropomorphic penalty) and Clarity (reduced semantic entropy). Non-anthropomorphic technical terms (haplodiploidy, trophallaxis) score highest on Clarity due to unambiguous, single-sense usage. Note: ``colony'' receives Appropriateness $= {{CACE_TERM_COLONY_APPROPRIATENESS}}$ because it falls outside the \texttt{ANTHROPOMORPHIC\_TERMS} set used for automated scoring; its colonial and settler-historical connotations are analyzed qualitatively in Section~\ref{sec:discussion}. All values resolve at render time from the frozen statistics artifact (\texttt{output/data/statistical\_analysis.json}).}
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
\caption{Distribution of semantic entropy $H(t)$ across Ento-Linguistic domains, computed from pipeline output in \texttt{output/data/domain\_statistics.json}. High-entropy terms are those exceeding the $H > 2.0$ bits threshold (per \texttt{src/analysis/semantic\_entropy.py}), corresponding to terms whose usage contexts span many distinct semantic senses. Entropy is calculated via TF-IDF vectorization of each term's corpus contexts followed by KMeans clustering (with $k < n$ contexts; see Eq.~\ref{eq:semantic_entropy}). The number of clusters is set to $k = \max(2,\, \min(k_{\max},\, n{-}1,\, \max(2, \lfloor\!\sqrt{n}\rfloor)))$ with $k_{\max}=5$ to prevent degenerate one-point-per-cluster assignments; each result also reports $H_{\max} = \log_2 k$ and the normalized entropy $H/H_{\max} \in [0,1]$. The $N$ column is each domain's term count in the same artifact, and the Overall row is their exact sum; every table value resolves at render time from the artifact.}
\label{tab:entropy_distribution}
\end{table}

## Confidence Intervals for Domain Metrics

The frozen statistics artifact (\texttt{output/data/statistical\_analysis.json}) reports per-term valid-entropy descriptives (means and standard deviations, with exclusions counted) and the inferential results in Table \ref{tab:pairwise_domain}; it does not compute domain-level confidence intervals, so per-domain ambiguity-score and context-variability intervals are not tabulated here. Separation between domains is established inferentially by the Welch $t$-tests and the omnibus ANOVA reported in Table \ref{tab:pairwise_domain}, with per-domain entropy descriptives in Table \ref{tab:entropy_distribution} and the accompanying summary figure \texttt{statistical\_analysis.png}.

## Full-Text Parallel Layer

To test whether the ento-linguistic patterns reported above survive beyond
abstracts, a parallel analysis layer was run over {{FULLTEXT_DOCUMENTS}} open
access full texts harvested from PubMed Central (PMC). The abstract corpus
remains the headline corpus of this study; the full-text layer is reported
here as a robustness check. The analysis machinery is shared: the same
terminology extraction, domain assignment, semantic-entropy, and CACE
scoring implementations are applied to full texts, with the frozen artifact
written to \texttt{output/data/fulltext\_analysis.json} and rendered in
figure \texttt{fulltext\_analysis.png}.

The layer comprises {{FULLTEXT_TOTAL_TOKENS}} tokens of running text, with a
per-document median of {{FULLTEXT_MEDIAN_TOKENS}} tokens. Table
\ref{tab:fulltext_domain} reports per-domain term counts and mean semantic
entropy over the full texts; {{FULLTEXT_PAIRWISE_N}} pairwise Welch
$t$-tests (Benjamini-Hochberg corrected, as in Table
\ref{tab:pairwise_domain}) accompany the omnibus one-way ANOVA on per-term
semantic entropy, $F = {{FULLTEXT_ANOVA_F}}$, {{FULLTEXT_ANOVA_P}}.

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
\caption{Per-domain terminology in the PMC full-text parallel layer: extracted-term counts and mean semantic entropy $H(t)$, computed with the same pipeline as the abstract layer (\texttt{output/data/fulltext\_analysis.json}, \texttt{descriptives} section). Term extraction uses a higher minimum token frequency than the abstract layer because full texts are substantially longer.}
\label{tab:fulltext_domain}
\end{table}
