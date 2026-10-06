# Supplemental Analysis: Theoretical Extensions {#sec:supplemental_analysis}

These are proposed constructions, not additional experimental results. The repository does not fit a generative model of scientific language, measure variational free energy, estimate empirical Markov blankets, or test a causal terminology intervention.

## Individuality and Conditional Independence

A Markov blanket specifies a conditional-independence relation between internal variables $\mu$ and external variables $\eta$, conditional on variables $B$ \cite{friston2013life, kirchhoff2018markov}:

\begin{equation}\label{eq:markov_blanket}
P(\mu\mid\eta,B)=P(\mu\mid B).
\end{equation}

This relation is an assumption or a property to establish for a specified probability model, on the support where the conditional distributions are defined. A biological application requires named variables, dynamics, observations, and tests of the proposed conditional independence. A sensory/active decomposition requires further modeling assumptions.

An ant's sensory and motor variables, or colony-level interaction variables, could enter candidate models at different scales. Neither the cuticle, a nest entrance, nor a pheromone field automatically establishes a blanket. Likewise, calling a colony a superorganism is not equivalent to proving this factorization. The Active Inferants simulation provides related modeling context \cite{friedman2021active}, without validating a blanket inferred from terminology in this study.

## A Proposed Framing Score

A future annotated study could define a bounded score:

\begin{equation}\label{eq:discursive_framing}
F_{\mathrm{frame}}(D,T)=\sum_{t\in T}w_t f_t(D)c_t,
\quad w_t\geq0,\quad\sum_{t\in T}w_t=1.
\end{equation}

Here $f_t(D)$ and $c_t$ would be explicitly defined annotation-based quantities in $[0,1]$, giving a score in $[0,1]$ for nonempty $T$. Empty vocabularies would yield an undefined score, not an inferred absence of framing. The weights require a prespecified rationale and sensitivity analysis. This proposed quantity is distinct from variational free energy and is not an output of the current lexical-pattern pipeline.

## Ambiguity Annotation

Lexical, contextual, biological-scale, and temporal ambiguity are candidate annotation categories. The implemented entropy measure summarizes context-cluster occupancy; it does not independently assign or validate these four categories. An annotation protocol should specify meaning distinctions, uncertainty, annotator training, and agreement measurement. Changes in context counts or source composition need separate controls.

## Cross-Domain Mapping

Given an independently specified similarity score $s(t,D_i,D_j)$, an annotated cross-domain summary could be defined as:

\begin{equation}\label{eq:cross_domain_mapping}
M_{ij}=
\begin{cases}
|T_i\cap T_j|^{-1}\displaystyle\sum_{t\in T_i\cap T_j}s(t,D_i,D_j), & |T_i\cap T_j|>0,\\
\mathrm{undefined}, & |T_i\cap T_j|=0.
\end{cases}
\end{equation}

This is a proposed mean over shared terms. It is not the implemented domain overlap coefficient, and an empty intersection does not establish that two biological concepts are unrelated. Similarity and domain membership require explicit definitions before interpretation.

## Temporal Networks

A time-indexed analysis should first specify a common vertex registry, matching vocabulary, and sampling rules. Let $A(t)$ be weighted adjacency matrices over that registry, with zero entries for absent edges. Then an algebraically defined change is:

\begin{equation}\label{eq:temporal_network_evolution}
\Delta A(t)=A(t+1)-A(t).
\end{equation}

Changing matrix entries can reflect document availability, vocabulary selection, source genre, or retrieval as well as changes in use. Demonstrating a conceptual shift requires controls for these alternatives and dated meaning annotation. The current BHL literal-frequency analysis does not implement this longitudinal network model.

## Multiscale Interpretation

Term, domain, and cross-domain summaries can organize different observational scales. Claims about biological organization or scientific thought require additional measurements at the corresponding scale. Environment-Centric Active Inference and related interpretations remain hypotheses requiring specified models and empirical tests, rather than conclusions established by the present corpus.
