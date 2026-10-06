---
author:
- Daniel Ari Friedman
- Tucker Cahill Chambers
date: '2026-10-06'
subtitle: Descriptive Corpus Analysis and a Six-Domain Framework
title: 'Ento-Linguistics: Language, Ambiguity, and Scientific Communication in Entomology'
---
# Abstract {#sec:abstract}

Terms such as *queen*, *worker*, and *colony* connect biological descriptions to familiar social concepts. This study introduces a six-domain Ento-Linguistic framework and an open-source descriptive text-analysis pipeline. The headline layer contains 7540 source-identified abstracts from 7609 stored strings; 69 unreconciled strings are retained but excluded. This headline layer contains 991026 processed tokens and 11644 candidate terms, of which 1323 receive rule-based domain assignments. The pipeline separates observed document-level term co-occurrence from a map of 6 predefined concept categories with 15 vocabulary-overlap relationships. Among assigned terms, 11.9% receive multiple labels; this measures classification overlap rather than semantic drift. Complementary analyses use 7073 PMC full-text records, 2430 historical OCR documents, and a separate arXiv layer. TF-IDF clustering and Shannon entropy summarize sentence-context distributions, while lexical patterns identify candidate framing contexts. Clarity, Appropriateness, Consistency, and Evolvability (CACE) are proposed as heuristic evaluation dimensions. Neither cluster entropy nor marker occurrence establishes distortion of biological understanding, and CACE scores have not been validated against independent human judgments. Provenance gaps, mixed-topic retrieval, OCR errors, overlapping groups, and explicitly bounded analyses limit interpretation. The contribution is a reproducible descriptive workflow and a framework for subsequent annotated, hypothesis-driven research, rather than a causal test of language shaping scientific thought. Code and data lineage: https://github.com/docxology/ento_linguistics.


\clearpage

# Introduction {#sec:introduction}

## Terminology as a Research Question

Scientific terminology connects observations, categories, and explanatory models. In social-insect research, familiar labels such as queen, worker, caste, kin, and colony can serve technical functions while retaining ordinary-language connotations. The relevant question is when those connotations help communication, when explicit definitions are needed, and how either possibility can be studied without inferring beliefs from word counts alone.

Philosophical and linguistic work supplies motivation for examining terminology within scientific practice \cite{latour1987, longino1990, lakoff1980metaphors}. Entomological discussions of categories and loaded metaphors provide field-specific context \cite{gordon1992wittgenstein, herbers2006, herbers2007}. These perspectives motivate empirical questions; they do not make every conventional term misleading or demonstrate that a replacement improves scientific understanding.

## The Challenge of Terminological Reform

Established terms support literature discovery and can carry precise operational meanings. Proposed alternatives therefore require context-specific comparison rather than automatic replacement. A task-based description may be useful for a behavioral observation without replacing a developmentally defined caste category. Molecular and developmental research makes that distinction especially important \cite{sumner2018molecular, qiu2022canalized}.

CACE---Clarity, Appropriateness, Consistency, and Evolvability---is introduced as an explicit set of evaluation questions. Its numerical scoring rules are one inspectable implementation, rather than an independently validated measure of understanding. The biological mechanism, intended referent, reader population, and definition supplied by an author remain central to evaluating terminology.

## Six Analytical Domains

The framework defines six overlapping domains:

1. **Unit of Individuality:** terms identifying ants, nestmates, colonies, collectives, and superorganisms; how an author specifies the unit being observed or modeled.
2. **Behavior and Identity:** distinctions between a task, an observed behavior, a persistent propensity, and a developmental category.
3. **Power and Labor:** queen, worker, caste, and related labels; whether descriptions imply control mechanisms or simply name biological roles.
4. **Sex and Reproduction:** reproductive and developmental categories; how definitions accommodate variation across taxa and mating systems.
5. **Kin and Relatedness:** pedigrees, demographic assumptions, and relatedness terminology. For example, expected sister relatedness of $r=0.75$ requires an outbred haplodiploid pedigree with one mother and one haploid father; it is not a universal property of colonies.
6. **Economics:** resource, allocation, investment, and related expressions; distinctions between measured energetic expenditure, fitness consequences, and metaphorical usage.

These are predefined organizational categories. A term receiving several labels does not establish that its meaning changed over time. Each domain also requires qualitative annotation before lexical patterns can be interpreted as ambiguity or framing.

## Research Approach

The headline computation analyzes 7540 stored abstracts, yielding 991026 processed tokens and 11644 candidates, of which 1323 receive domain assignments. Complementary PMC, BHL, and arXiv layers retain separate source identities. The workflow distinguishes corpus frequencies, observed document co-occurrence, vocabulary overlap, context-cluster entropy, and heuristic scores.

Active Inference and multiscale modeling provide a theoretical perspective \cite{friston2010free, friedman2021active}, but the present pipeline does not fit a generative model of scientific language or measure variational free energy. A Markov blanket specifies conditional-independence relationships in a model; it is not a lexical security filter or a biological boundary established by terminology alone.

The contribution is a descriptive workflow, a proposed taxonomy, and explicit questions for subsequent validation. Historical OCR frequencies provide dated source-layer observations rather than proof of conceptual origins or causal reform. Methods and limitations state source custody gaps, convenience-sample retrieval, statistical dependence, and bounded analyses so that interpretation remains tied to the evidence actually produced.


\clearpage

# Methods {#sec:methodology}

The workflow separates acquisition, descriptive analysis, and theoretical interpretation. Supplemental Methods \ref{sec:supplemental_methods} and \ref{sec:supplemental_infrastructure} describe the implementation. Section \ref{sec:supplemental_analysis} develops conceptual proposals rather than fitted generative models.

## Data Acquisition {#sec:data_acquisition}

### Search Strategy and Source Selection

The archived input is the ordered abstract list in *data/corpus/abstracts.json*. The headline analysis selects strings whose digest maps to an identified PubMed record. Unreconciled strings remain archived but are excluded, without altering their bytes. The acquisition script delegates to *src/pipeline/corpus_build.py*; its base queries and the named growth queries in *src/data/literature_mining.py* are the executable query definitions. Digest-indexed provenance records PMIDs, DOIs, titles, years, journals, and query names where available. This corpus accumulated across retrieval runs; a single illustrative query does not reconstruct its history.

Three complementary layers remain separate: PMC title, abstract, and body text in *data/fulltexts/* shards; BHL mirror OCR in *data/bhl/* shards; and arXiv title/abstract records in *data/corpus/arxiv_records.json*. The arXiv harvester uses category-restricted queries over q-bio.PE and nlin.AO. Neither full texts nor preprints are merged into the headline abstract list. Query and retrieval metadata are retained in source sidecars.

### Corpus Composition and Cleaning

| Headline metric | Value |
|-----------------|-------|
| Stored abstract strings | 7609 |
| Source-identified analyzed abstracts | 7540 |
| Unreconciled strings excluded | 69 |
| Processed tokens | 991026 |
| Unique token types | 47064 |
| Candidate terms | 11644 |
| Domain-assigned terms | 1323 |

These are archived-input and selected-corpus counts, not estimates of all entomological literature. Broad searches retrieve adjacent biological topics and algorithmic uses of ant terminology; a keyword match does not establish relevance to ant biology. Historical volumes can contain substantial non-entomological material. The PMC input also includes correction and retraction notices, including standardized repeated notice text. Article-type, retraction-status and relevance screening are not complete. The custody audit in *output/reports/corpus_audit.json* records missing digest provenance, repeated text, identifier mismatches, and unused sidecar entries. Gaps are retained and disclosed; undocumented source identities are not inferred. Exact text-digest matches to retrieved PubMed abstracts can recover metadata without rewriting text. This establishes source identity rather than ant-topic relevance. Digest-keyed sidecars retain only one metadata entry when several records contain identical text. Relevance annotation and complete source reconciliation are needed before treating a layer as a curated field-wide sample.

TextProcessor normalizes text, tokenizes with NLTK, filters punctuation and stop words, and optionally lemmatizes with WordNet. Extraction disables lemmatization when counting surface-form terms. NLTK datasets are installed separately from Python dependencies; selected English tokenizer, stopword and WordNet contents are bound into analysis signatures and receipts. Article-level licenses require individual checking; indexing in PubMed/PMC does not establish reuse permission.

### Domain Coverage Verification

The six vocabularies are defined by TerminologyExtractor.DOMAIN_SEEDS: Unit of Individuality, Behavior and Identity, Power and Labor, Sex and Reproduction, Kin and Relatedness, and Economics. Coverage means that extraction assigned terms to these labels; it does not measure retrieval recall or validate the taxonomy against independent annotation.

## Statistical Analysis {#sec:statistical_analysis}

### Term Extraction and Classification

Extraction counts candidate tokens, retains configured seed words subject to length/frequency and preprocessing rules, applies remaining lexical-pattern filters, and assigns domains through direct seed matching, compound-word overlap, and fallback patterns. Three-token windows provide up to thirty deduplicated short contexts for heuristic scoring. They do not expand assignments by co-occurrence. Candidate filtering also admits scientific substrings and compound tokens, so candidates can include unrelated words and OCR artifacts. Candidate inclusion does not itself assign a domain or establish biological relevance. An n-gram utility is available but the headline extractor does not invoke it to extract multi-word phrases. The BHL literal-frequency pass separately matches multi-word seed phrases as consecutive tokens.

Minimum frequencies differ: one occurrence for headline abstracts, twenty for PMC, and two for arXiv and the BHL stack. These choices affect vocabulary size and prevent interpreting raw term counts as directly comparable measures across layers.

### Semantic Entropy

Terms with at least five usable sentence contexts undergo TF-IDF vectorization and seeded KMeans clustering (random state 42, ten initializations). Shannon entropy measures occupancy:

\begin{equation}\label{eq:semantic_entropy}
H(t)=-\sum_{i=1}^{k}p_i\log_2p_i.
\end{equation}

The requested cluster count is $k=\max(2,\min(5,n-1,\max(2,\lfloor\sqrt{n}\rfloor)))$; occupied clusters may be fewer. Normalized entropy divides by $\log_2 k_{\mathrm{occupied}}$, with zero for a single occupied cluster. Only successfully computed estimates enter domain means; insufficient-context and computation failures are recorded as exclusions. Domain figures and statistical descriptives share this sentence-context calculation. The $H>2$ bits flag is exploratory, without independent calibration. Clusters are computational partitions, not annotated word senses; high entropy does not by itself demonstrate ambiguity or temporal semantic drift.

### Domain-Level Statistical Tests

Welch tests, Benjamini--Hochberg adjustments, small-sample corrected standardized differences, and one-way ANOVA summarize valid per-term entropies. Groups with fewer than two usable values are omitted. These are exploratory comparisons. Terms can belong to multiple groups and derive contexts from shared documents, violating the simple independence interpretation. Multiplicity correction does not repair dependence, retrieval bias, or unequal context counts. Threshold crossings do not establish calibrated population significance or causal effects. Confirmatory inference requires independent annotation and a document-level sampling model accounting for shared terms and overlapping domains.

### Conceptual Network Analysis

The conceptual map assigns terms to six predefined categories. Its 15 links summarize vocabulary overlap:

\begin{equation}\label{eq:overlap_coefficient}
w_{AB}=\frac{|A\cap B|}{\min(|A|,|B|)}.
\end{equation}

The terminology graph counts actual documents containing each pair among the hundred most frequent domain-assigned terms, breaking frequency ties lexically. Whole-word matching is case-insensitive; repeated mentions within a document count once. Shared labels never create an observed edge. Document co-occurrence does not establish a semantic or causal relationship. The separate overlap heatmap summarizes classifier assignments.

### Rhetorical and Discourse Analysis

Regex and keyword analyzers identify candidate rhetorical, argumentative, and framing expressions. Framing is evaluated in three-token windows around extracted terms. Domain framing proportions measure occurrence contexts containing an anthropomorphic marker; multi-domain occurrences contribute to each domain but once to the overall tally. These are lexical proxies without gold-standard annotation validation. Discourse counts are accompanied by analyzed-document counts and sampling fractions. PMC discourse uses a deterministic approximately one-fifth sample of eligible texts rather than a full-text census.

### CACE Evaluation

Four heuristic dimensions define CACE:

\begin{equation}\label{eq:cace_clarity}
\mathrm{Clarity}(t)=\min(1,\max(0,1-H(t)/3.32)),
\end{equation}

\begin{equation}\label{eq:cace_appropriateness}
\mathrm{Appropriateness}(t)=\max(0,1-[0.4\,\mathbf{1}_{t\in\mathcal A}+0.1|\mathrm{overlap}(t,\mathcal A)|+0.05\max(|D(t)|-1,0)]),
\end{equation}

\begin{equation}\label{eq:cace_consistency}
\mathrm{Consistency}(t)=\frac{2}{n(n-1)}\sum_{i<j}\frac{\mathbf x_i\cdot\mathbf x_j}{\|\mathbf x_i\|\|\mathbf x_j\|},
\end{equation}

\begin{equation}\label{eq:cace_evolvability}
\mathrm{Evolvability}(t)=\tfrac12\min(1,|D(t)|/3)+\tfrac12\min(1,|S_t|/3).
\end{equation}

The implemented Clarity normalization constant is 3.32, approximately $\log_2 10$; it is a design choice rather than the five-cluster ceiling. Here $\mathcal A$ is the configured anthropomorphic vocabulary, $D(t)$ the domain assignments, and $S_t$ scale-marker categories found in contexts. The aggregate is their arithmetic mean. Domain CACE aggregates and their figure use the same up-to-fifty-term sample, ordered by decreasing frequency and lexical tie-break, and at most ten short extraction contexts per term. Computed entropy enters Clarity where available. Default zero entropy for unavailable estimates and Consistency of 0.5 for fewer than two contexts are conventions, not evidence of clarity or consistency. Weights and thresholds are design choices; no completed coefficient sensitivity study, inter-rater reliability measurement, or independent predictive validation is claimed.

### Historical Analysis and Coverage

All 2430 stored BHL documents enter literal seed-term frequencies per 10,000 OCR tokens by era. Literal spellings, hyphens, and OCR errors affect rates. The computational stack streams extraction and framing over all stored documents by default. Coverage metadata record available and analyzed documents and characters. Entropy is restricted to twenty frequent candidates per era, drawing contexts from all era documents. An optional positive development character budget selects complete documents by deterministic dyadic traversal across shard order; its fingerprint and coverage metadata distinguish it from a complete run. Neither the full stored corpus nor a bounded development selection is presumed representative of historical entomology.

### Validation and Reproducibility

Tests exercise numerical examples, real files, corpus slices, and local HTTP servers. Negative controls reject malformed text, stale content, missing receipts, and failed renderer commands. They establish software behavior, not scientific validity of the proxy measures. Python dependencies are resolved by uv.lock; NLTK resources are separate prerequisites. Corpus values remain manuscript placeholders. Content fingerprints bind analyses to ordered records, project source, and locked dependencies. A completed manifest binds input and output files; rendering rejects changed artifacts and nonzero toolchain exits.


\clearpage

# Results: Corpus Analysis and Terminology Networks {#sec:experimental_results}

## Terminology Extraction Across Domains

Analysis of the source-identified headline layer yields 11644 candidate terms from 7540 abstracts and 991026 processed tokens. Of these candidates, 1323 receive domain assignments. These counts exclude 69 unreconciled archived strings; broad retrieval still limits relevance and representativeness.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Domain} & \textbf{Terms} & \textbf{Frequency} & \textbf{Bridging terms} \\
\hline
Unit of Individuality & 526 & 27813 & 24 \\
Behavior \& Identity & 262 & 16896 & 91 \\
Power \& Labor & 294 & 12306 & 138 \\
Sex \& Reproduction & 244 & 9165 & 61 \\
Kin \& Relatedness & 83 & 3957 & 4 \\
Economics & 78 & 4458 & 3 \\
\hline
\end{tabular}
\caption{Rule-based domain assignments and corpus frequencies. A term can receive several labels, so domain counts and frequencies are not mutually exclusive. Bridging means multiple labels, not an observed transfer of meaning.}
\label{tab:terminology_extraction}
\end{table}

The processed vocabulary has type-token ratio 0.0475. Its most frequent recorded tokens are ant (20328), specie (10552), and colony (7319). Frequency identifies recurring lexical material; it does not establish its conceptual importance or the intentions of authors.

## Terminology Network Structure

The observed terminology graph uses the hundred most frequent domain-assigned terms. Its edge weight counts documents containing both terms:

\begin{equation}\label{eq:network_edge_weight}
w(u,v)=\sum_{d=1}^{N}\mathbf{1}[u\in d]\mathbf{1}[v\in d].
\end{equation}

Whole-word matches are case-insensitive, and repeated mentions within a document do not add weight. No edge is inferred from shared labels or extraction order. The graph has clustering coefficient 0.8948 under the generated network-summary definition; this statistic does not measure conceptual coherence, communication quality, or resistance to reform.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/terminology_network.png}
\caption{Observed document co-occurrence among the hundred highest-frequency domain-assigned terms in the 7540-abstract layer. Nodes represent terms, node area uses a square-root frequency scale, color identifies the primary domain, and edge width scales shared-document counts to a bounded display range (Eq.~\ref{eq:network_edge_weight}). Isolated nodes are omitted from the display and up to twenty frequent terms are considered for collision-filtered labels. Layout and dense regions have no causal or hierarchical interpretation.}
\label{fig:terminology_network}
\end{figure}

Domain-assignment overlap is a different quantity, displayed separately in Figure \ref{fig:domain_overlap}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/domain_overlap_heatmap.png}
\caption{Szymkiewicz--Simpson overlap coefficients between domain-assigned vocabularies (Eq.~\ref{eq:overlap_coefficient}). Each cell counts shared terms divided by the smaller vocabulary size. Values reflect the current lexical classifier; observed zeros do not establish conceptual isolation.}
\label{fig:domain_overlap}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/domain_comparison.png}
\caption{Six descriptive panels show distinct term counts, mean extraction confidence, total frequency, mean successfully computed sentence-context entropy, bridging counts, and heuristic CACE means over up to fifty selected terms per domain. Extraction confidence is a configured score rather than calibrated classification accuracy. Entropy and CACE sample definitions are specified in Methods; missing entropy does not establish zero ambiguity.}
\label{fig:domain_comparison}
\end{figure}


\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/concept_map.png}
\caption{Six predefined concept categories connected by vocabulary overlap. Node size summarizes associated terms, which can appear in several categories; the subtitle totals term associations rather than unique terms. Edge weights are classifier-defined overlaps, not observed causal connections or a discovered biological ontology.}
\label{fig:concept_map}
\end{figure}

## Framing Analysis

Lexical markers identify contexts for further qualitative examination. They do not distinguish metaphor from technical usage, demonstrate author bias, or establish a language-induced change in biological models. The same distinction applies to the domain-specific interpretations in Section \ref{sec:domain_findings}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/anthropomorphic_framing.png}
\caption{Observed framing-marked terminology by canonical domain. Left: distinct extracted terms with at least one occurrence context matching an anthropomorphic pattern. Right: up to five terms per domain, selected by decreasing matched-context proportion, context count, and lexical ordering. Counts are neither curated vocabulary sizes nor occurrence frequencies. Occurrence-context framing proportions are exported separately.}
\label{fig:anthropomorphic}
\end{figure}

Among assigned terms, 11.9\% have multiple domain labels. This is a property of the classifier and corpus. Temporal semantic drift would require explicit time-indexed meaning comparison, while lexical, contextual, and scale ambiguity require independent sense annotation or validated proxies. Those measurements are not established by label overlap.


\clearpage

# Results: Domain-Specific Findings {#sec:domain_findings}

The six domains organize descriptive outputs and questions for qualitative interpretation. Their assignments follow the configured vocabulary and lexical rules. Domain-specific statements below do not infer cognitive bias, biological mechanisms, or author intent from term counts.

## Unit of Individuality

This vocabulary includes references to individuals, colonies, and collective organization. Its mean computed sentence-context entropy is 1.55 bits. Frequency and word-formation panels describe extracted surface forms, while the scale panel counts keyword matches in term names. These counts do not estimate biological boundaries or conditional independence. Figures \ref{fig:domain_overview_grid}, \ref{fig:domain_patterns_grid}, and \ref{fig:unit_individuality_patterns} support inspection of the extraction.

## Power \& Labor

Power and Labor contains 294 assigned terms and 138 terms with multiple labels. Its occurrence-context anthropomorphic-marker proportion is 1.2\%, rather than a percentage of authors or publications using misleading language. Discussions of loaded terminology motivate contextual examination \cite{herbers2006, herbers2007}. Molecular work on caste \cite{sumner2018molecular} and developmental canalization \cite{qiu2022canalized} also make it important to distinguish developmental phenotypes from temporary task categories; canalization is not evidence that every caste identity is labile.

Figures \ref{fig:power_labor_frequencies} and \ref{fig:power_labor_ambiguities} show observed term frequency and context-cluster entropy. Figure \ref{fig:concept_hierarchy} ranks predefined concept categories by their direct graph connections; it does not show a biological hierarchy or term-level betweenness.

## Behavior \& Identity

The mean computed sentence-context entropy is 1.74 bits. Task labels provide useful candidates for context annotation. Evidence of behavioral flexibility in ants \cite{ravary2007, gordon2010} motivates asking when a label denotes an observation, a persistent propensity, or a morphological category. The corpus statistics alone do not establish that categorical labels obscure that flexibility.

## Sex \& Reproduction

This domain groups reproductive and developmental terminology. Its mean computed entropy is 1.74 bits. The presence of paired labels does not demonstrate a binary-opposition graph or the importation of mammalian sex determination. Reproductive systems and caste development vary across taxa, and the epigenetic review \cite{oldroyd2021epigenetics} provides background rather than validation of a lexical classifier.

## Kin \& Relatedness

The mean computed entropy is 1.75 bits. Relatedness terms require biological and demographic context: numerical coefficients depend on pedigrees, mating systems, and population structure. The present outputs do not estimate those quantities, measure competition between evolutionary explanations, or demonstrate that conflict terminology is underrepresented.

## Economics

The classifier assigns 78 terms to Economics, with 3 receiving multiple labels. Its mean computed entropy is 1.86 bits. Low overlap can follow directly from lexicon design; a zero overlap does not establish a closed conceptual subsystem. Terms such as allocation (210 occurrences), investment (271), resource (579), and resources (711) warrant examination of their operational definitions. Statistical or ecological compounds matching a seed word can be classification errors rather than evidence of economic framing.

## Historical Interpretation

Historical readings of caste and superorganism terminology provide context \cite{wheeler1911, gordon1992wittgenstein, boomsma2018superorganismality}. The BHL era analysis in Section \ref{sec:bhl_grounding} reports literal OCR frequencies and explicitly sampled stack outputs. Changes in those rates do not independently establish changes in conceptual commitments, the origin of a concept, or progress toward more accurate biological explanation.

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/domain_overview_grid.png}
\caption{Ten highest-frequency extracted terms per domain. Bar length is corpus frequency and color is the attached sentence-context entropy estimate. Zero-valued defaults for insufficient contexts must not be interpreted as evidence of unambiguous meaning. These are descriptive extraction outputs from the stored abstract layer.}
\label{fig:domain_overview_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/domain_patterns_grid.png}
\caption{Surface word-formation composition of assigned vocabularies. Donut areas summarize word, hyphenated-compound, and multi-word categories where present. The headline extractor does not independently add n-grams, so availability of a category in the plotting utility does not establish its extraction.}
\label{fig:domain_patterns_grid}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/unit_of_individuality_patterns.png}
\caption{Unit of Individuality term-formation counts (left) and counts of term names matching scale keyword groups (right). Scale groups can overlap; true zeros are retained. Neither panel estimates actual biological scale boundaries.}
\label{fig:unit_individuality_patterns}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/concept_hierarchy.png}
\caption{Direct-link centrality of predefined concept categories (left) and centrality against associated-term counts (right). Colors separate categories above versus at or below mean centrality. The display does not represent a biological command hierarchy.}
\label{fig:concept_hierarchy}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/power_and_labor_term_frequencies.png}
\caption{The fifteen highest-frequency assigned Power and Labor terms in the stored abstract layer. Frequency is annotated; color tracks rank. These observations do not quantify hierarchical control or bias.}
\label{fig:power_labor_frequencies}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/power_and_labor_ambiguities.png}
\caption{Power and Labor terms ranked by attached context-cluster entropy, with corpus frequency and short extraction-context counts. Sentence-context entropy and the plotted extraction-window counts use different context definitions. Cluster entropy is not an independently validated ambiguity measure.}
\label{fig:power_labor_ambiguities}
\end{figure}


\clearpage

# Discussion {#sec:discussion}

## Language and Scientific Practice

The descriptive outputs organize terminology into a framework for examining the relationship between language and biological explanation. They are compatible with asking whether scientific metaphors influence inquiry \cite{latour1987, longino1990, lakoff1980metaphors}, but do not test that causal hypothesis. Keyword frequency, sentence-cluster entropy, and co-occurrence identify lexical patterns rather than researchers' beliefs, decisions, or errors.

Terms such as *queen*, *worker*, and *caste* deserve contextual scrutiny because biological roles and ordinary-language connotations can differ. Existing discussions of terminology reform provide a substantive motivation \cite{herbers2006, herbers2007}. The present corpus analysis neither establishes that terminology delayed particular discoveries nor measures the adoption of alternatives across the field. Such claims would require dated source analysis and evidence about research decisions.

The observed graph has clustering coefficient 0.8948, while 11.9\% of assigned terms receive multiple labels. Neither quantity demonstrates self-reinforcing conceptual bias. Co-occurrence can arise because papers discuss several biological processes together; label overlap also follows from the predefined lexicons. A visualization's arrangement must not be read as a human-style command hierarchy.

## Active Inference as a Theoretical Perspective

Active Inference offers a vocabulary for discussing generative models, inference, and action \cite{friston2010free, clark2013whatever}. In the Active Inferants study, a simulated ant-foraging model reproduces selected colony phenomena in a laboratory-inspired setting \cite{friedman2021active}. This provides an example of mechanistic modeling without a centralized controller; it does not experimentally compare terminology choices or establish the empirical adequacy of every biological assumption.

Interpreting terminology as a prior is an analogy here. This repository does not fit an Active Inference model of scientific language, estimate variational free energy from the corpus, or infer Markov blankets from ant behavioral data. Whether an ant or colony admits a useful blanket description depends on specified state variables, dynamics, and conditional-independence assumptions \cite{friston2013life, kirchhoff2018markov}; it cannot be settled by changing a noun.

The Environment-Centric Active Inference and related multiscale proposals in Section \ref{sec:supplemental_analysis} should be read as theoretical extensions. They require explicit models and empirical tests before supporting biological or linguistic conclusions.

## Practical Use of CACE

CACE makes evaluation criteria inspectable: clarity of operational definitions, suitability of metaphors, consistency of use, and adaptability to new findings. Its numerical implementation is a heuristic instantiation. Penalizing membership in a predefined anthropomorphic vocabulary partly encodes the desired ranking; a favorable score is not independent validation of a replacement term.

The representative-term table includes terms absent from the extraction. Their scores are derived from text features and fallback conventions, as recorded by the in-corpus flag. In particular, a zero default entropy for an unattested term must not be interpreted as demonstrated specificity. Comparisons between *slave* and *host worker* illustrate these rules, rather than measuring a change in readers' comprehension or research outcomes.

The computed aggregate values are 0.30 and 0.47, respectively, with Appropriateness 0.50 and 0.40. These values remain useful for inspecting the scoring implementation. Independent assessment should compare definitions and context-specific biological accuracy, collect blinded judgments, measure agreement, and test sensitivity to the chosen weights before treating the scores as a prescriptive standard.

## Cross-Domain Communication

Domain overlap can help select terms for shared glossaries and explicit operational definitions. The six-domain framework is one proposed partition; alternative lexicons and annotation schemes may produce different assignments. Maintaining links to established terminology can support discoverability while clarifying which mechanism or observational category is meant. Benefits to communication remain hypotheses for reader and author studies.

## Limitations

1. **Source custody and relevance.** Some archived abstract strings lack digest-indexed source metadata and are excluded from headline analysis; broad queries include adjacent biology and computational uses. Historical volumes contain mixed topics; PMC retrieval includes correction/retraction notices and repeated boilerplate. Source reconciliation and relevance annotation remain incomplete.
2. **Sampling and accessibility.** Search and availability filters select a convenience corpus. Layers are not matched document samples and differ in extraction threshold, length, genre, and publication history.
3. **OCR and language.** Literal historical matching is sensitive to OCR errors, language, hyphenation, and spelling. Rare or absent matches do not date a concept's origin.
4. **Proxy validity.** Computational clusters are not annotated senses; marker patterns are not validated discourse labels. The pipeline does not measure author intent, cognitive distortion, or causal framing.
5. **Statistical dependence.** Domain groups overlap and share document-derived contexts. Reported test outputs are exploratory; no calibrated confirmatory inference is claimed.
6. **Explicitly bounded components.** PMC discourse uses an approximately one-fifth deterministic text sample; domain CACE uses at most fifty terms; BHL entropy uses twenty frequent terms per era with full-corpus contexts. Default BHL extraction, framing, and literal-frequency calculations include all stored documents; an optional development character cap produces a separately fingerprinted subset.
7. **Unmeasured theory.** No fitted generative model, empirical Markov-blanket estimation, term-reform intervention, or independent human validation is reported.

These boundaries support a focused next study: a frozen, fully reconciled corpus with independent annotations and prespecified document-level analysis, followed by a controlled evaluation of operational terminology.


\clearpage

# Conclusion {#sec:conclusion}

This work provides a six-domain framework and a reproducible descriptive pipeline for examining terminology in scientific text. Across 7540 stored abstracts, the pipeline processes 991026 tokens and extracts 11644 candidate terms, with 1323 receiving domain assignments. Observed document co-occurrence, predefined conceptual-category overlap, sentence-context entropy, and heuristic framing and CACE scores are reported as distinct quantities.

The 11.9\% of assigned terms with multiple labels measures classification overlap, not semantic drift. The 6 concept categories are predefined rather than discovered. Complementary source layers extend the descriptive scope without establishing that language causes bias, that a terminology reform improves scientific modeling, or that numerical CACE rankings are independently validated.

## Future Directions

The immediate research priorities are source reconciliation, document-level relevance and license review, and independent annotation of senses and framing. A frozen annotated corpus would support tests of extraction accuracy, agreement between annotators, context-count sensitivity, and statistical models accounting for shared documents and overlapping domain labels.

Longitudinal analysis should distinguish changes in source composition and OCR quality from changes in terminology. Multilingual comparisons require language-specific normalization and definitions. Reader or author experiments could then evaluate whether operational definitions and alternative terms improve comprehension or mechanistic explanation.

CACE offers explicit evaluation questions for such studies. Its current scores provide an inspectable starting point, with design choices and missing-data conventions disclosed. Active Inference and multiscale interpretations remain theoretical proposals until connected to specified models and empirical measurements. The repository contributes tools and auditable descriptive results for that work.


\clearpage

# Related Work {#sec:related_work}

## Scientific Language and Categories

Philosophy of science and discourse research provide context for studying terminology as part of research practice \cite{kuhn1996, latour1987, longino1990, fairclough1992, wodak2009methods}. Conceptual and deliberate-metaphor frameworks supply complementary questions about ordinary connotations and communicative intention \cite{lakoff1980metaphors, steen2017deliberate}. This study draws motivation from those traditions, while keeping computational lexical proxies separate from claims about thought, intention, or causal influence.

Work on scientific classification and cultural histories offers additional context \cite{berlin1992, hacking1999social, sleigh2007ants}. The present six-domain taxonomy is a proposed analytic organization; it is not independently established as exhaustive or uniquely appropriate.

## Terminology in Social-Insect Research

Debates over caste categories and descriptions of ant behavior motivate explicit definitions \cite{gordon1992wittgenstein, boomsma2018superorganismality}. Research on collective behavior provides biological context for distinguishing task allocation from an assumed centralized controller \cite{gordon2010, gordon2019ecology, gordon2023ecology}. The descriptive corpus pipeline does not itself test those mechanisms.

Discussions of racially loaded language in social-insect research provide a substantive case for examining terminology choices \cite{herbers2006, herbers2007}. The ESA Better Common Names Project is a related institutional initiative \cite{betternamesproject2024}. Neither the current frequency analysis nor CACE scoring measures the adoption or effects of these reforms.

Molecular accounts of caste and epigenetic mechanisms \cite{sumner2018molecular, oldroyd2021epigenetics} and developmental canalization research \cite{qiu2022canalized} reinforce the need to distinguish developmental processes from temporary behavioral labels. Canalization must not be interpreted as proof that every caste category is labile. The historical superorganism literature \cite{wheeler1911} and later conceptual analysis \cite{boomsma2018superorganismality} also caution against dating a concept's origin from an absent OCR match.

## Computational Mapping and Source-Layer Analysis

Computational literature mapping supplies methods for examining connections among terms and publications \cite{chen2006citespace}. Here, document co-occurrence is kept separate from vocabulary-overlap relationships between predefined concepts. TF-IDF/KMeans occupancy entropy is used as a descriptive measure of context distributions, without claiming independent sense annotation or validated linguistic ambiguity.

Source-layer comparisons are also descriptive. Abstracts, full texts, historical volumes and preprints differ in access, genre, length, topic and extraction threshold. An observed difference between layers is not automatically a robustness result or a historical change in meaning.

## Active Inference and Colony Modeling

The Free Energy Principle and Active Inference supply theoretical vocabulary for generative modeling \cite{friston2010free, friston2013life, clark2013whatever, kirchhoff2018markov}. The Active Inferants framework supplies a simulated ant-foraging example \cite{friedman2021active}; it does not experimentally compare terminology choices. Model behavior therefore cannot independently establish that hierarchical vocabulary caused modeling errors.

Theoretical perspectives on eusociality and biological individuality \cite{nowak2010evolution, boomsma2018superorganismality} motivate careful definition of units and mechanisms. The Environment-Centric Active Inference extensions in the supplement remain proposed constructions requiring explicit models and empirical testing.

## Positioning This Work

This repository contributes a six-domain descriptive workflow with auditable source layers, inspectable computational definitions, registered figures, and content-bound manuscript values. CACE is a proposed evaluation framework, not a historically validated intervention. Its independent validation would require annotated meanings, blinded judgments, measured agreement, and tests of sensitivity and communication outcomes. The distinction between implemented measurement, theoretical motivation, and unperformed validation is part of the contribution.


\clearpage

# Acknowledgments {#sec:acknowledgments}

We gratefully acknowledge the contributions of individuals and institutions that made this research possible.

## Institutional Support

This work was conducted at the Active Inference Institute. We thank the Institute for providing the research environment and collaborative infrastructure that supported the development of the Ento-Linguistic framework.

## Collaborations

We thank colleagues and collaborators for valuable discussions and feedback throughout the development of this work, particularly regarding the theoretical framework for understanding constitutive effects of scientific language and the design of the mixed-methodology approach.

## Data and Software

This research builds upon open-source software tools and publicly available datasets. We acknowledge:

- Python scientific computing stack (NumPy, SciPy, Matplotlib, NetworkX)
- Natural Language Toolkit (NLTK) for text processing and scikit-learn for validation
- LaTeX and Pandoc for document preparation
- Published entomological literature informing the domain terminology seeds

---

*All errors and omissions remain the sole responsibility of the authors.*


\clearpage

# Supplemental Methods: Text Processing and Term Extraction {#sec:supplemental_methods}

This section specifies the input and extraction stages used by the study. The numerical definitions and bounded components are detailed in Section \ref{sec:supplemental_infrastructure}. Developer APIs remain documented in source; template utilities are not additional research measurements.

## Source Layers and Custody

The archived abstract input contains 7609 strings. The headline analysis includes 7540 strings whose SHA-256 digest maps to an identified PubMed record and excludes 69 unreconciled strings. Exact digest matches to retrieved PubMed abstracts can recover metadata without changing archived text. Identification establishes a source association, not relevance to ant biology, a complete retrieval history, or independent text annotation.

PMC records retain title, abstract, and body text in their own shard directory. BHL records retain historical OCR and era assignments. arXiv title/abstract records form a separate preprint layer. Those documents are not concatenated into the headline abstract input. The custody audit inspects every stored record and reports missing metadata, duplicate text, identifier disagreement, unused sidecar entries, and invalid text.

Digest-indexed sidecars can retain only one source identity when several records share identical text. These collisions are reported rather than resolved by inventing metadata. Broad searches include adjacent biology, computational terminology and mixed-topic historical volumes. The PMC layer includes correction and retraction notices; repeated notice boilerplate contributes to shared body text. Individual relevance, article-type screening and license review remain incomplete.

## Normalization and Token Streams

TextProcessor applies Unicode normalization, lowercase conversion, word tokenization, punctuation filtering, and stop-word removal. Hyphenated and underscored tokens can remain intact. The stop vocabulary combines NLTK English stop words with configured scientific meta-language words. WordNet lemmatization is available and is used for corpus vocabulary summaries; terminology extraction disables lemmatization for its occurrence counts. Consequently a summary's most-common lemma and an extracted surface-form frequency need not have the same spelling.

NLTK sentence tokenization supplies the contexts used for semantic entropy. These sentence contexts differ from the short, processed-token windows retained on extracted Term objects. English-language resources are applied to a heterogeneous stored corpus; this is not a validated multilingual processing pipeline.

NLTK resources are separate downloaded prerequisites. The schema-2 analysis receipt binds the selected English stopword file, English punkt_tab files and WordNet dictionary bytes (the complete archive when archive-backed). The same hashes enter cache signatures; changing a selected resource requires reanalysis. These hashes identify the installed inputs without vendoring them or guaranteeing automatic restoration. Open Multilingual WordNet is outside this receipt because English lemmatization does not consume it. The source implementation and uv.lock specify Python package dependencies.

## Candidate Extraction and Domain Assignment

TerminologyExtractor counts tokens, applies a minimum frequency, and evaluates candidate filters. The headline threshold is one occurrence; the PMC threshold is twenty; arXiv and the BHL computational stack use two. Different thresholds, document lengths and source genres affect vocabulary size and prevent treating raw counts as matched layer comparisons.

Candidate filters retain configured seed words of three to fifty characters before evaluating generic filters. Other candidates enter through scientific patterns, compound separators, or configured scientific substrings. They reject pure numbers but can admit unrelated substring matches and OCR artifacts. Candidate inclusion is therefore broader than biological terminology. For example, skin, making and queensland can remain candidates without receiving a domain label.

The six DOMAIN_SEEDS vocabularies define direct assignments. Compound tokens can inherit labels from seed-word overlap; fallback lexical patterns use word boundaries. An extracted term can receive several labels. Label overlap follows from these rules and does not demonstrate temporal semantic drift or independently annotated meanings.

Candidate iteration is sorted for deterministic output. The extractor stores surface text, lemma, frequency, domain labels, confidence, and deduplicated short contexts. Three-token windows around occurrences supply at most thirty stored contexts. These windows support heuristic scoring; they do not expand domain labels by co-occurrence. The available n-gram utility is not invoked by the headline extractor.

Extraction confidence combines configured frequency, context and classification features. It is not calibrated against human correctness labels. The pipeline does not report precision, recall, multilingual accuracy, or inter-rater reliability.

## Document Co-occurrence and Concept Categories

The observed terminology graph uses the hundred highest-frequency domain-assigned terms, with lexical tie-breaking. Case-insensitive whole-word searches identify presence in each document. A pair's edge weight counts documents containing both terms, regardless of repeated mentions. Shared labels do not create observed edges. The saved graph statistics describe this selected vocabulary rather than the entire field.

The separate concept map uses six predefined categories and vocabulary-association rules. Terms can belong to several categories, so a total of term associations is not a count of unique terms. Category links summarize vocabulary overlap. Node positions, direct-link centrality, colors, and label selection are display conventions and do not establish biological hierarchy or causal dependence.

The overlap heatmap uses the Szymkiewicz--Simpson coefficient in Equation \ref{eq:overlap_coefficient}. Its diagonal is one by construction. A zero observed overlap does not establish conceptual separation.

## Reproducible Inputs and Failure Behavior

DataLoader rejects malformed or empty corpus input, including non-string and blank records. Required pipeline stages propagate failures. Process workers merge results in input order; ENTO_ANALYSIS_WORKERS=1 selects serial execution. Resource-related pool unavailability is logged before a serial retry, while other worker failures propagate.

Caches bind ordered record contents, project Python source, locked dependencies, and explicit development limits. Changed body text invalidates an artifact even if its metadata, record count and file modification time remain unchanged. The completed receipt binds the input/output inventory and image hashes. A receipt establishes which bytes were used, not the scientific validity of the taxonomy or proxies.


\clearpage

# Supplemental Methods: Statistical and Scoring Infrastructure {#sec:supplemental_infrastructure}

The canonical implementations are semantic_entropy, DomainAnalyzer, statistics_pipeline, fulltext_pipeline, arxiv_analysis, and bhl_analysis. Their generated artifacts preserve exclusions, coverage, and exploratory numerical outputs.

## Sentence-context Entropy

Each source text is sentence-tokenized once for a term set. An inverted index over alphanumeric parts prunes impossible matches; a case-insensitive whole-word regular expression makes the final decision. This preserves matching sentence order. Contexts must contain more than three words, and at least five usable contexts are required for computation.

TF-IDF uses English stop words, minimum document frequency one, and at most one thousand features. KMeans uses random state 42 and ten initializations. The requested cluster count follows the bounded square-root rule in Methods, remaining below the number of contexts. Occupied clusters may be fewer than requested.

Shannon entropy is computed from occupied-cluster probabilities in bits (Equation \ref{eq:semantic_entropy}). The normalized value divides by the occupied-cluster ceiling; a single occupied cluster has zero normalized entropy. The exploratory high-entropy flag uses a threshold above two bits. Computational partitions are not independently annotated word senses.

Results record ok, insufficient_contexts, or error status. Only ok values enter domain means and statistical groups. Excluded estimates are counted separately; their placeholder zero is not included as a measured value. A term assigned to several domains contributes to each domain group. Entropy-table sample sizes and weighted totals count valid domain memberships, not unique terms or documents.

## Exploratory Comparisons and Intervals

The statistical artifact reports per-domain valid-entropy means, standard deviations where at least two values exist, and exclusions. Welch tests compare groups with at least two values. Benjamini--Hochberg adjustments apply to the emitted comparison family at a nominal threshold of 0.05. Standardized differences use a small-sample bias correction; they should not be described as uncorrected Cohen's d.

One-way ANOVA and its effect-size summary use the valid groups. Figure intervals use nominal Student-t quantiles and are omitted for groups with only one valid estimate. These numerical calculations have software tests and independent numerical comparators, but their simple population interpretation is not justified by this corpus design.

Terms can share documents, contexts and domain labels. Multiplicity adjustment does not repair that dependence, convenience retrieval, unequal context counts, or differing extraction thresholds. Threshold flags are exploratory. Confirmatory inference requires a prespecified document-level model and independently annotated evaluation data.

## Shared CACE Sample and Scores

Domain figures and statistical exports use the same scoring function and sample: up to fifty terms per domain, ordered by decreasing frequency with lexical tie-breaking. Each term supplies at most ten of its stored short extraction contexts. The representative-term table is a separate named-term evaluation whose artifact records whether a term was extracted.

Clarity uses attached sentence-context entropy when available. Appropriateness uses configured vocabulary and domain-overlap penalties. Consistency uses TF-IDF context-vector cosine similarities. Evolvability uses assigned domains and scale-marker categories. Their equally weighted mean is the aggregate; Equations \ref{eq:cace_clarity}--\ref{eq:cace_evolvability} specify the proposed rules.

Unavailable entropy still defaults to zero inside the heuristic, and fewer than two contexts yield a Consistency convention of 0.5. These conventions do not establish clarity or consistency. Missing figure input is labeled unavailable instead of substituting confidence as a CACE score. No completed coefficient-sensitivity study, human-rating validation, intervention benefit, or calibrated scientific-accuracy prediction is claimed.

## Framing and Discourse Proxies

Occurrence-context framing uses three-token windows around domain-assigned terms. The feature extractor has four anthropomorphic, four hierarchical, and four economic regex patterns. Marker matches are lexical events, not validated author intent or judgments that a biological description is misleading.

Domain framing proportions count occurrence contexts matching an anthropomorphic pattern. Multi-domain occurrences contribute to each domain but once to the overall tally. Distinct framing-marked term counts in the figure are a different summary from those occurrence proportions.

Discourse, rhetorical, and persuasive analyzers use configured patterns and keywords. Their artifacts record eligible/analyzed texts and exclusions. PMC discourse uses a deterministic stride sample when corpus size exceeds the configured text/character targets, with an approximately one-fifth sample in this snapshot. Raw counts depend on text length and sample size; the cross-layer figure is not a normalized prevalence comparison or an annotated discourse study.

## Historical OCR and Layer Coverage

BHL literal frequencies normalize NFC text, lowercase it, join hyphenated line breaks, and tokenize Latin-letter words while retaining internal hyphens. Seed phrases match exact consecutive tokens; counts are non-overlapping per phrase. Rates divide by era token counts and multiply by ten thousand. Alternative spellings, OCR errors and language affect those rates. An observed zero does not date a concept's origin.

The BHL computational stack uses cleaned OCR with the canonical extraction and classification rules. Default extraction and framing process all stored era documents using per-document counters, avoiding a corpus-wide token-position map. Stored and cleaned text are still held in memory; memory use is not constant in corpus size. Entropy evaluates twenty frequent candidates per era with sentence contexts drawn from all era documents. Unassigned candidates can enter the overall sampled entropy mean, while domain means only use assigned valid candidates.

Coverage records available and analyzed documents and characters. An explicit positive `BHL_STACK_CHARACTER_BUDGET` selects a deterministic whole-document development subset. `FULLTEXT_ANALYSIS_LIMIT` similarly bounds a development PMC run. Both limits enter fingerprints; bounded caches cannot satisfy an unbounded default run.

## Execution and Artifact Verification

The standalone sequence installs locked dependencies and NLTK resources, runs tests, generates figures, checks custody, and renders the manuscript. Testing and generation run sequentially because some legacy tests consume exports.

The analysis signature also hashes the selected English NLTK tokenizer, stopwords and WordNet contents. The receipt records these resource hashes without machine-specific installation paths. Missing resources fail, and changed resources invalidate caches. These content hashes do not vendor or automatically restore external resource downloads.

Numerical values remain placeholders in canonical Markdown. The generator checks finite/nonempty JSON, decodable PNGs, registry hashes, figure inventory and manuscript figure availability before writing its receipt. Rendering validates the receipt, rejects unresolved placeholders, and requires successful Pandoc, XeLaTeX and BibTeX execution. Undefined citations/references and missing glyphs fail the final build.

Software tests use actual corpus slices, numerical examples, real files, local HTTP and real subprocesses. Negative controls establish that malformed input, stale artifacts and failing commands are rejected. Those checks establish software behavior and provenance, not source relevance, individual reuse rights, human-validation outcomes or causal scientific conclusions.


Completed BHL eras are saved atomically in local recovery checkpoints. Each checkpoint binds the ordered era records, implementation/dependency/resource signature and any development bound, plus a digest of the completed result. A matching checkpoint can resume a disrupted run; changed inputs or bounds require recomputation, and corrupted matching results fail. The final four-layer receipt is still written only after all required stages complete.


\clearpage

# Supplemental Results {#sec:supplemental_results}

## Exploratory Pairwise Domain Comparisons

Domain groups share terms and document-derived contexts. Independence is therefore not established; BH threshold flags are numerical outputs rather than calibrated population evidence.

Table \ref{tab:pairwise_domain} presents pairwise comparisons of per-term semantic entropy between all Ento-Linguistic domains using Welch's two-sample $t$-tests. Raw $p$-values are computed from the $t$-distribution with Satterthwaite-approximated degrees of freedom; adjusted $p$-values correct for 15 simultaneous comparisons using the Benjamini-Hochberg (BH) procedure at $q = 0.05$. Cohen's $d$ quantifies effect size, interpreted as small ($d \approx 0.2$), medium ($d \approx 0.5$), or large ($d \geq 0.8$). Domain descriptives entering these tests are per-term valid-entropy means with exclusions counted.

\begin{table}[h]
\centering
\small
\begin{tabular}{|l|l|c|c|c|c|c|}
\hline
\textbf{Domain A} & \textbf{Domain B} & \textbf{$t$} & \textbf{$p$ (raw)} & \textbf{$p$ (BH)} & \textbf{Cohen's $d$} & \textbf{Sig.\ (BH)} \\
\hline
Behavior \& Identity & Economics & -1.1741 & 0.2453 & 0.3984 & -0.2613 & no \\
Behavior \& Identity & Kin \& Relatedness & -0.1247 & 0.9014 & 0.9798 & -0.0316 & no \\
Behavior \& Identity & Power \& Labor & 1.1183 & 0.2656 & 0.3984 & 0.1943 & no \\
Behavior \& Identity & Sex \& Reproduction & -0.0254 & 0.9798 & 0.9798 & -0.0046 & no \\
Behavior \& Identity & Unit of Individuality & 2.2826 & 0.0243 & 0.1244 & 0.3655 & no \\
Economics & Kin \& Relatedness & 0.7908 & 0.4336 & 0.5420 & 0.2290 & no \\
Economics & Power \& Labor & 2.1875 & 0.0332 & 0.1244 & 0.4471 & no \\
Economics & Sex \& Reproduction & 1.1323 & 0.2621 & 0.3984 & 0.2343 & no \\
Economics & Unit of Individuality & 3.2290 & 0.0023 & 0.0352 & 0.6170 & yes \\
Kin \& Relatedness & Power \& Labor & 0.9250 & 0.3614 & 0.4929 & 0.2208 & no \\
Kin \& Relatedness & Sex \& Reproduction & 0.1046 & 0.9173 & 0.9798 & 0.0248 & no \\
Kin \& Relatedness & Unit of Individuality & 1.6961 & 0.1002 & 0.3006 & 0.3903 & no \\
Power \& Labor & Sex \& Reproduction & -1.1186 & 0.2654 & 0.3984 & -0.1897 & no \\
Power \& Labor & Unit of Individuality & 1.1426 & 0.2549 & 0.3984 & 0.1691 & no \\
Sex \& Reproduction & Unit of Individuality & 2.2489 & 0.0263 & 0.1244 & 0.3564 & no \\
\hline
\end{tabular}
\caption{Exploratory pairwise Welch tests on valid per-term sentence-context entropy, with Benjamini--Hochberg adjusted $p$-values over 15 comparisons and standardized effect sizes. Threshold flags use $q=0.05$ without establishing calibrated population significance: domain groups overlap and share document-derived contexts. The omnibus ANOVA yields $F(5.0000,350.0000)=2.5470$, $p$-value 0.0278, and $\eta^2=0.0351$.}
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
queen & 0.41 & 0.45 & 0.04 & 0.33 & 0.31 & yes \\
\textit{primary reproductive} & 1.00 & 1.00 & 0.50 & 0.00 & 0.62 & no \\
\hline
worker & 0.46 & 0.45 & 0.05 & 0.33 & 0.32 & yes \\
\textit{non-reproductive helper} & 1.00 & 1.00 & 0.50 & 0.00 & 0.62 & no \\
\hline
slave & 0.31 & 0.50 & 0.05 & 0.33 & 0.30 & yes \\
\textit{host worker} & 1.00 & 0.40 & 0.50 & 0.00 & 0.47 & no \\
\hline
caste & 0.44 & 1.00 & 0.07 & 0.33 & 0.46 & yes \\
\textit{task group} & 1.00 & 1.00 & 0.50 & 0.00 & 0.62 & no \\
\hline
soldier & 0.38 & 0.50 & 0.11 & 0.17 & 0.29 & yes \\
\textit{major worker} & 1.00 & 0.50 & 0.50 & 0.00 & 0.50 & no \\
\hline
colony & 0.44 & 1.00 & 0.03 & 0.33 & 0.45 & yes \\
haplodiploidy & 0.31 & 1.00 & 0.05 & 0.17 & 0.38 & yes \\
trophallaxis & 0.33 & 1.00 & 0.06 & 0.17 & 0.39 & yes \\
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
Economics & 1.86 & 57.7 & 26 \\
Power \& Labor & 1.64 & 34.2 & 76 \\
Behavior \& Identity & 1.74 & 41.1 & 56 \\
Sex \& Reproduction & 1.74 & 53.1 & 64 \\
Unit of Individuality & 1.55 & 26.8 & 112 \\
Kin \& Relatedness & 1.75 & 45.5 & 22 \\
\hline
\textbf{Overall} & 1.67 & 38.8 & \textbf{ 356 } \\
\hline
\end{tabular}
\caption{Distribution of semantic entropy $H(t)$ across Ento-Linguistic domains, computed from pipeline output in \texttt{output/data/domain\_statistics.json}. High-entropy terms are those exceeding the $H > 2.0$ bits threshold (per \texttt{src/analysis/semantic\_entropy.py}), summarizing occupancy of computational clusters without annotated senses. Entropy is calculated via TF-IDF vectorization of each term's corpus contexts followed by KMeans clustering (with $k < n$ contexts; see Eq.~\ref{eq:semantic_entropy}). The number of clusters is set to $k = \max(2,\, \min(k_{\max},\, n{-}1,\, \max(2, \lfloor\!\sqrt{n}\rfloor)))$ with $k_{\max}=5$ to prevent degenerate one-point-per-cluster assignments; each result also reports $H_{\max} = \log_2 k$ and the normalized entropy $H/H_{\max} \in [0,1]$. The $N$ column counts terms with usable entropy estimates; Overall sums valid domain memberships and can count a multi-domain term more than once. Its mean and high-entropy percentage use that same denominator; every table value resolves at render time from the artifact.}
\label{tab:entropy_distribution}
\end{table}

## Confidence Intervals for Domain Metrics

The frozen statistics artifact (\texttt{output/data/statistical\_analysis.json}) reports per-term valid-entropy descriptives (means and standard deviations, with exclusions counted) and the inferential results in Table \ref{tab:pairwise_domain}; it does not compute domain-level confidence intervals, so per-domain ambiguity-score and context-variability intervals are not tabulated here. Exploratory numerical differences are summarized by the Welch $t$-tests and the omnibus ANOVA reported in Table \ref{tab:pairwise_domain}, with per-domain entropy descriptives in Table \ref{tab:entropy_distribution} and the accompanying summary figure \texttt{statistical\_analysis.png}.

## Full-Text Parallel Layer

A complementary descriptive analysis was run over 7073 open
access full texts harvested from PubMed Central (PMC). The abstract corpus
remains the headline corpus of this study; the full-text layer is reported
here as a separate convenience sample with a higher extraction threshold. The analysis machinery is shared: the same
terminology extraction, domain assignment, semantic-entropy, and CACE
scoring implementations are applied to full texts, with the frozen artifact
written to \texttt{output/data/fulltext\_analysis.json} and rendered in
figure \texttt{fulltext\_analysis.png}.

The layer comprises 44507505 tokens of running text, with a
per-document median of 5624.0000 tokens. Table
\ref{tab:fulltext_domain} reports per-domain term counts and mean semantic
entropy over the full texts; 15 pairwise Welch
$t$-tests (Benjamini-Hochberg corrected, as in Table
\ref{tab:pairwise_domain}) accompany the omnibus one-way ANOVA on per-term
semantic entropy, $F = 8.6337$, <0.0001.

Anthropomorphic framing over the same full texts is scored as the
proportion of domain-term occurrence contexts containing an anthropomorphic
framing marker (\texttt{add\_framing\_analysis} in
\texttt{src/pipeline/fulltext\_pipeline.py}): 0.0107
overall, with Economics at
0.0359 against
0.0074 for Unit of
Individuality and 0.0078
for Behavior \& Identity.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|}
\hline
\textbf{Domain} & \textbf{Terms extracted} & \textbf{Mean $H$ (bits)} \\
\hline
Behavior \& Identity & 96 & 1.9654 \\
Economics & 35 & 1.7796 \\
Kin \& Relatedness & 24 & 1.9768 \\
Power \& Labor & 118 & 2.0165 \\
Sex \& Reproduction & 86 & 2.0407 \\
Unit of Individuality & 241 & 2.0240 \\
\hline
\end{tabular}
\caption{Per-domain terminology in the PMC full-text parallel layer: extracted-term counts and mean semantic entropy $H(t)$, computed over valid estimates with the same pipeline as the abstract layer; valid-estimate counts appear in the statistical figure (\texttt{output/data/fulltext\_analysis.json}, \texttt{descriptives} section). Term extraction uses a higher minimum token frequency than the abstract layer because full texts are substantially longer.}
\label{tab:fulltext_domain}
\end{table}

## Discourse and Rhetorical Layer

Both statistical artifacts additionally carry a corpus-level
``discourse`` section --- discourse patterns, rhetorical strategies,
argumentative structures, and persuasive techniques --- computed by the
shared discourse stage (\texttt{add\_discourse\_analysis} in
\texttt{src/pipeline/statistics\_pipeline.py}) after the statistics
stages. The abstract layer's discourse pass covers
7524 texts (sample fraction
1.0000). The full-text layer's
discourse pass covers 1415 of its
7073 texts --- a deterministic
0.2001 sample disclosed here because
full texts exceed the discourse pass's minimum-length bound far less
often than abstracts but are subsampled to keep the pass bounded.
Both layers' discourse dimensions are compared in figure
\texttt{discourse\_comparison.png} (registered as
\texttt{fig:discourse\_comparison}); panels spanning orders of
magnitude use a symlog frequency axis.

Discourse patterns occur 1271
times as hierarchical framing in the abstract layer against
1108 occurrences in the
full-text layer, with 1038 versus
1090 economic metaphors,
30 versus
47 anthropomorphic framings,
and 27 versus
33 scale-ambiguous constructions.

Rhetorical strategies show the same abstract-to-full-text expansion:
1563 anecdotal markers in the abstract
layer versus 9229 in full texts,
244 versus
29224 authority markers,
446 versus
1793 analogies, and
1141 versus
4228 generalizations.

The argumentative-structure pass identifies
1786 argumentative structures in the abstract
layer versus 1300 in the full-text sample.
Metaphorical language, the dominant persuasive technique, occurs
3800 times in the abstract layer
against 20772 occurrences in full
texts. All frequencies are raw corpus counts from the artifacts'
\texttt{discourse} sections (\texttt{output/data/statistical\_analysis.json}
and \texttt{output/data/fulltext\_analysis.json}); no values in this
subsection are literals.

## Statistical and Source-Layer Figures

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/statistical_analysis.png}
\caption{Headline valid-entropy descriptives with nominal intervals, bias-corrected standardized differences, and exploratory ANOVA. Bar annotations report valid term counts; overlapping domain memberships and shared document contexts limit population inference.}
\label{fig:statistical_analysis}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/fulltext_analysis.png}
\caption{Separate PMC full-text statistics over all stored records by default. Extraction thresholds and context distributions differ from the abstract layer. Nominal intervals and multiplicity-adjusted threshold flags remain exploratory.}
\label{fig:fulltext_analysis}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/layer_comparison.png}
\caption{Mean valid context-cluster entropy in the abstract and PMC layers, with valid-term counts. This compares distinct convenience samples and extraction thresholds; it is not a matched robustness experiment or evidence of causal language effects.}
\label{fig:layer_comparison}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/discourse_comparison.png}
\caption{Lexical discourse, rhetorical and persuasive-pattern counts, with analyzed-text counts shown in the legend. PMC uses an explicitly bounded text sample. Raw frequencies depend on sample size and text length and must not be read as normalized prevalence or human-validated author intent.}
\label{fig:discourse_comparison}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/arxiv_analysis.png}
\caption{Separate arXiv preprint-layer descriptives and exploratory comparisons. Some groups have only one valid entropy estimate, for which intervals are omitted; very small groups and nearly zero within-group variance can yield large standardized differences without establishing generalizable effects.}
\label{fig:arxiv_analysis}
\end{figure}


\clearpage

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


\clearpage

# Supplemental Analysis: Case Studies and Validation {#sec:supplemental_case_studies}

## Validation Agenda

Expert classification review, interdisciplinary assessment, historical interpretation, and cross-cultural comparison are proposed validation activities. This repository does not report completed human-annotation agreement, inter-rater reliability, multilingual validation, or a prespecified subsampling and coefficient-sensitivity study. Software tests and descriptive source-layer comparisons do not substitute for those measurements.

## Historical Terminology Analysis {#sec:bhl_grounding}

The historical layer contains 2430 stored BHL mirror OCR documents dated into three era buckets: 996 in 1850--1899, 1237 in 1900--1949, and 197 in 1950--1970. Retrieval selects volumes containing search expressions, not a manually curated collection of ant-only works. Document titles, dates, source identifiers, queries, and retrieval information are recorded in the source sidecar.

\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Term} & \textbf{1850--1899} & \textbf{1900--1949} & \textbf{1950--1970} \\
\hline
caste & 0.0735 & 0.1140 & 0.2253 \\
worker & 0.6394 & 0.7935 & 1.4169 \\
queen & 0.8861 & 1.0770 & 1.0064 \\
colony & 0.9283 & 1.1689 & 1.1047 \\
superorganism & 0.0003 & 0.0007 & 0.0051 \\
\hline
\end{tabular}
\caption{Complete-corpus literal OCR matches per 10,000 era tokens. Differences are descriptive of the selected volumes. OCR quality, topic, language, and spelling differences limit historical interpretation.}
\label{tab:superorganism_concept_evolution}
\end{table}

\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth,height=0.78\textheight,keepaspectratio]{/Volumes/GitVault/Username/docxology/Public/ento_linguistics/output/figures/bhl_term_usage.png}
\caption{Full-corpus historical literal frequencies for six seed terms. Each panel uses its own rate axis. Neither zeros nor changing rates establish conceptual origin, prevalence in all entomological literature, or causal influence on research.}
\label{fig:bhl_term_usage}
\end{figure}

Rare matches for superorganism cannot establish that the concept originated after 1970. Alternative spellings such as super-organism are counted differently, and earlier theoretical discussion can exist outside the sampled sources. Interpretation should be anchored in dated sources such as \citet{wheeler1911}, rather than treating an OCR absence as historical proof.

## Complete Document Coverage and Bounded Entropy

The BHL extraction/entropy/framing stack uses 996, 1237, and 197 complete documents, respectively. Default extraction and framing use all era documents. Available and analyzed characters are recorded in the artifact's coverage metadata. Entropy considers twenty frequent extracted candidates per era using contexts across all documents; it is a candidate-term sample rather than an exhaustive entropy census. Candidate filtering can retain unrelated substring matches such as skin, making, or queensland; unassigned candidates enter the overall sampled entropy mean but not domain means. These are computational filter outputs, not a curated historical vocabulary. An optional development character budget produces a disclosed, separately fingerprinted document subset. Neither default storage nor that subset establishes historical representativeness.

Developmental evidence for canalized caste differentiation \cite{qiu2022canalized} concerns biological mechanisms and does not establish a historical linguistic trend. Evaluating that connection would require a dated, annotated corpus with source-composition controls.

## A Reproducible Case-Study Protocol

A subsequent study can select a specific term, reconcile each text to its source, annotate meaning and biological referent in dated contexts, and preregister comparisons between research traditions or eras. Controls should distinguish genuine changes in use from retrieval, OCR, spelling, and genre changes. CACE judgments should be gathered independently of the automatic scoring vocabulary, with agreement and uncertainty reported.


\clearpage

# Symbols and Notation Glossary {#sec:glossary}

This glossary defines the mathematical notation and domain-specific terminology used throughout the manuscript.

## Mathematical Notation

| Symbol | Description | First Use |
|--------|-------------|-----------|
| $G = (V, E)$ | Terminology network (graph with vertices and edges) | Eq. \ref{eq:network_edge_weight} |
| $D(t)$ | Set of Ento-Linguistic domains term $t$ is assigned to | Eq. \ref{eq:cace_appropriateness} |
| $w(u,v)$ | Observed number of documents containing both terms $u$ and $v$ | Eq. \ref{eq:network_edge_weight} |
| $H(t)$ | Semantic entropy of term $t$ in bits (Shannon entropy over usage-context clusters) | Eq. \ref{eq:semantic_entropy} |
| $H^*$ | Configured threshold (2.0 bits); not an independently calibrated sense threshold | Eq. \ref{eq:semantic_entropy} |
| $H_{\max}$ | Maximum attainable entropy for $k$ clusters, $\log_2 k$ | Eq. \ref{eq:semantic_entropy} |
| $\hat{H}(t)$ | Normalized semantic entropy $H(t) / H_{\max} \in [0,1]$ | Eq. \ref{eq:semantic_entropy} |
| $p_i$ | Empirical proportion of contexts assigned to semantic cluster $i$ | Eq. \ref{eq:semantic_entropy} |
| $k$ | Requested number of computational clusters ($k$-means, $k = \max(2,\ \min(k_{\max},\ n{-}1,\ \max(2, \lfloor\!\sqrt{n}\rfloor)))$; $k_{\max}=5$, $n=|C_t|$; $k < n$) | Eq. \ref{eq:semantic_entropy} |
| $C_t$ | Set of valid usage contexts of term $t$ (sentences with $\geq 3$ words) | Eq. \ref{eq:semantic_entropy} |
| $S_t$ | Set of biological scale levels expressed in term $t$'s contexts | Eq. \ref{eq:cace_evolvability} |
| $w_{AB}$ | Overlap coefficient (Szymkiewicz--Simpson) between concept sets $A$ and $B$ | Eq. \ref{eq:overlap_coefficient} |
| $w_\text{base}$ | Base overlap-coefficient weight in composite relationship strength | Sec. \ref{sec:methodology} |
| $r_\text{term}$ | Term-overlap ratio component of composite relationship strength | Sec. \ref{sec:methodology} |
| $r_\text{domain}$ | Domain-overlap ratio component of composite relationship strength | Sec. \ref{sec:methodology} |
| $\text{Clarity}(t)$ | CACE Clarity score: $\min(1,\max(0,1-H(t)/3.32))$ | Eq. \ref{eq:cace_clarity} |
| $\text{Appropriateness}(t)$ | CACE Appropriateness score (penalizes anthropomorphic terms) | Eq. \ref{eq:cace_appropriateness} |
| $\text{Consistency}(t)$ | CACE Consistency score: mean pairwise cosine similarity of context vectors | Eq. \ref{eq:cace_consistency} |
| $\text{Evolvability}(t)$ | CACE Evolvability score: mean of calibrated domain-breadth and scale-marker components | Eq. \ref{eq:cace_evolvability} |
| $\mathcal{A}$ | Set of anthropomorphic terms (queen, king, slave, worker, soldier, nurse, ...) | Eq. \ref{eq:cace_appropriateness} |
| $F_{\mathrm{frame}}(D, T)$ | Proposed bounded annotated framing score for domain $D$ and term set $T$ | Supplemental Eq. \ref{eq:discursive_framing} |
| $M_{ij}$ | Cross-domain mapping strength between domains $D_i$ and $D_j$ | Supplemental Eq. \ref{eq:cross_domain_mapping} |
| $\Delta A(t)$ | Change in adjacency matrices on a common vertex registry | Supplemental Eq. \ref{eq:temporal_network_evolution} |
| $B$ | Markov Blanket boundary of a system | Supplemental Eq. \ref{eq:markov_blanket} |
| $\mu$ | Internal states (conditionally independent of external given blanket) | Supplemental Eq. \ref{eq:markov_blanket} |
| $\eta$ | External states | Supplemental Eq. \ref{eq:markov_blanket} |

## Theoretical Terms

| Term | Definition | Context |
|------|------------|---------|
| **Active Inference** | A corollary of the Free Energy Principle stating that agents act to fulfill the predictions of their generative models. | Sec. \ref{sec:introduction} |
| **CACE** | Clarity, Appropriateness, Consistency, Evolvability — four-dimensional meta-standard for evaluating scientific terminology. | Sec. \ref{sec:methodology} |
| **Generative Model** | A probabilistic model of how sensory data is generated from latent causes. | Sec. \ref{sec:discussion} |
| **Markov Blanket** | Variables rendering specified internal and external variables conditionally independent in a probability model. | Sec. \ref{sec:supplemental_analysis} |
| **Semantic Entropy** | Shannon entropy $H(t)$ over the cluster distribution of a term's usage contexts; describes computational cluster occupancy without independently validated senses. | Sec. \ref{sec:methodology} |
| **Stigmergy** | A mechanism of indirect coordination where agents modify the environment to stimulate the actions of others. | Sec. \ref{sec:introduction} |
| **Superorganism** | A colony-level organismic concept; its biological interpretation is not established by a term's frequency or by an assumed blanket. | Sec. \ref{sec:introduction}; Sec. \ref{sec:experimental_results} |
| **Variational Free Energy** | A variational bound on negative log model evidence under a specified probabilistic model; not measured by this corpus pipeline. | Sec. \ref{sec:discussion} |

## Pipeline Modules
<!-- BEGIN: AUTO-API-GLOSSARY -->

| Module | File | Function |
|---|---|---|
| Text Processing | `text_analysis.py` | Tokenization, normalization, feature extraction |
| Term Extraction | `term_extraction.py` | Domain-aware terminology identification |
| Semantic Entropy | `semantic_entropy.py` | Per-term $H(t)$ computation via TF-IDF + $k$-means |
| CACE Scoring | `cace_scoring.py` | Four-dimensional terminology evaluation |
| Domain Analysis | `domain_analysis.py` | Per-domain framing and ambiguity analysis |
| Conceptual Mapping | `conceptual_mapping.py` | Cross-domain concept graph construction |
| Rhetorical Analysis | `rhetorical_analysis.py` | Framing detection and argumentative scoring |
| Discourse Analysis | `discourse_analysis.py` | Discourse pattern classification |
| Statistics | `statistics.py` | Statistical validation utilities |
| Visualization | `concept_visualization.py` | Network and domain-specific figure generation |
<!-- END: AUTO-API-GLOSSARY -->




\clearpage

# References {#sec:references}


\bibliography{references}


\clearpage

