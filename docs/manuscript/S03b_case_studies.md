# Supplemental Analysis: Case Studies and Validation {#sec:supplemental_case_studies}

## Validation Agenda

Expert classification review, interdisciplinary assessment, historical interpretation, and cross-cultural comparison are proposed validation activities. This repository does not report completed human-annotation agreement, inter-rater reliability, multilingual validation, or a prespecified subsampling and coefficient-sensitivity study. Software tests and descriptive source-layer comparisons do not substitute for those measurements.

## Historical Terminology Analysis {#sec:bhl_grounding}

The historical layer contains {{BHL_DOCUMENTS}} stored BHL mirror OCR documents dated into three era buckets: {{BHL_ERA_1850_1899_DOCS}} in 1850--1899, {{BHL_ERA_1900_1949_DOCS}} in 1900--1949, and {{BHL_ERA_1950_1970_DOCS}} in 1950--1970. Retrieval selects volumes containing search expressions, not a manually curated collection of ant-only works. Document titles, dates, source identifiers, queries, and retrieval information are recorded in the source sidecar.

\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Term} & \textbf{1850--1899} & \textbf{1900--1949} & \textbf{1950--1970} \\
\hline
caste & {{BHL_ERA_1850_1899_CASTE_PER_10K}} & {{BHL_ERA_1900_1949_CASTE_PER_10K}} & {{BHL_ERA_1950_1970_CASTE_PER_10K}} \\
worker & {{BHL_ERA_1850_1899_WORKER_PER_10K}} & {{BHL_ERA_1900_1949_WORKER_PER_10K}} & {{BHL_ERA_1950_1970_WORKER_PER_10K}} \\
queen & {{BHL_ERA_1850_1899_QUEEN_PER_10K}} & {{BHL_ERA_1900_1949_QUEEN_PER_10K}} & {{BHL_ERA_1950_1970_QUEEN_PER_10K}} \\
colony & {{BHL_ERA_1850_1899_COLONY_PER_10K}} & {{BHL_ERA_1900_1949_COLONY_PER_10K}} & {{BHL_ERA_1950_1970_COLONY_PER_10K}} \\
superorganism & {{BHL_ERA_1850_1899_SUPERORGANISM_PER_10K}} & {{BHL_ERA_1900_1949_SUPERORGANISM_PER_10K}} & {{BHL_ERA_1950_1970_SUPERORGANISM_PER_10K}} \\
\hline
\end{tabular}
\caption{Complete-corpus literal OCR matches per 10,000 era tokens. Differences are descriptive of the selected volumes. OCR quality, topic, language, and spelling differences limit historical interpretation.}
\label{tab:superorganism_concept_evolution}
\end{table}

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{../output/figures/bhl_term_usage.png}
\caption{Full-corpus historical literal frequencies for six seed terms. Each panel uses its own rate axis. Neither zeros nor changing rates establish conceptual origin, prevalence in all entomological literature, or causal influence on research.}
\label{fig:bhl_term_usage}
\end{figure}

Rare matches for superorganism cannot establish that the concept originated after 1970. Alternative spellings such as super-organism are counted differently, and earlier theoretical discussion can exist outside the sampled sources. Interpretation should be anchored in dated sources such as \citet{wheeler1911}, rather than treating an OCR absence as historical proof.

## Complete Document Coverage and Bounded Entropy

The BHL extraction/entropy/framing stack uses {{BHL_ERA_1850_1899_STACK_DOCS}}, {{BHL_ERA_1900_1949_STACK_DOCS}}, and {{BHL_ERA_1950_1970_STACK_DOCS}} complete documents, respectively. Default extraction and framing use all era documents. Available and analyzed characters are recorded in the artifact's coverage metadata. Entropy considers twenty frequent extracted candidates per era using contexts across all documents; it is a candidate-term sample rather than an exhaustive entropy census. Candidate filtering can retain unrelated substring matches such as skin, making, or queensland; unassigned candidates enter the overall sampled entropy mean but not domain means. These are computational filter outputs, not a curated historical vocabulary. An optional development character budget produces a disclosed, separately fingerprinted document subset. Neither default storage nor that subset establishes historical representativeness.

Developmental evidence for canalized caste differentiation \citep{qiu2022canalized} concerns biological mechanisms and does not establish a historical linguistic trend. Evaluating that connection would require a dated, annotated corpus with source-composition controls.

## A Reproducible Case-Study Protocol

A subsequent study can select a specific term, reconcile each text to its source, annotate meaning and biological referent in dated contexts, and preregister comparisons between research traditions or eras. Controls should distinguish genuine changes in use from retrieval, OCR, spelling, and genre changes. CACE judgments should be gathered independently of the automatic scoring vocabulary, with agreement and uncertainty reported.
