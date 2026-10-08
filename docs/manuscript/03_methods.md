# Methods {#sec:methodology}

The workflow separates acquisition, descriptive analysis, and theoretical interpretation. Supplemental Methods \ref{sec:supplemental_methods} and \ref{sec:supplemental_infrastructure} describe the implementation. Section \ref{sec:supplemental_analysis} develops conceptual proposals rather than fitted generative models.

## Data Acquisition {#sec:data_acquisition}

### Search Strategy and Source Selection

The archived input is the ordered abstract list in *data/corpus/abstracts.json*. The headline analysis selects strings whose digest maps to an identified PubMed record. Unreconciled strings remain archived but are excluded, without altering their bytes. The acquisition script delegates to *src/pipeline/corpus_build.py*; its base queries and the named growth queries in *src/data/literature_mining.py* are the executable query definitions. Digest-indexed provenance records PMIDs, DOIs, titles, years, journals, and query names where available. This corpus accumulated across retrieval runs; a single illustrative query does not reconstruct its history.

Three complementary layers remain separate: PMC title, abstract, and body text in *data/fulltexts/* shards; BHL mirror OCR in *data/bhl/* shards; and arXiv title/abstract records in *data/corpus/arxiv_records.json*. The arXiv harvester uses category-restricted queries over q-bio.PE and nlin.AO. Neither full texts nor preprints are merged into the headline abstract list. Query and retrieval metadata are retained in source sidecars.

### Corpus Composition and Cleaning

| Headline metric | Value |
|-----------------|-------|
| Stored abstract strings | {{CORPUS_STORED_RECORDS}} |
| Source-identified analyzed abstracts | {{CORPUS_PUBLICATIONS}} |
| Unreconciled strings excluded | {{CORPUS_EXCLUDED_UNRECONCILED}} |
| Processed tokens | {{CORPUS_TOTAL_TOKENS}} |
| Unique token types | {{CORPUS_UNIQUE_TOKENS}} |
| Candidate terms | {{CORPUS_CANDIDATE_TERMS}} |
| Domain-assigned terms | {{CORPUS_DOMAIN_TERMS}} |

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

### Measurement Targets and Validation

Each computational quantity has a defined observational unit. Frequencies count processed occurrences; network edges count shared documents; domain overlap counts classifier memberships; entropy summarizes sentence-context cluster occupancy. Framing markers and CACE scores apply configured rules to selected contexts and terms. None directly measures an author's intention or a reader's understanding. Problem-specific validation is a central requirement of automated text analysis \cite{grimmer2013text}; reproducible calculation and valid interpretation address different questions.

A future evaluation should freeze annotation rules before inspecting score rankings and retain a held-out set of source contexts. Annotation should distinguish biological referent, task versus developmental category, technical definition, figurative use, and uncertainty. Sampling should include frequent and rare terms, assigned and unassigned candidates, and contexts without marker matches. These strata allow false positives and false negatives to be examined, rather than assessing only examples selected by the pipeline. Agreement, adjudication rules, and performance by source layer should be reported. This is a proposed validation design, not an executed component of the current analysis.

### Domain-Level Statistical Tests

Welch tests, Benjamini--Hochberg adjustments, small-sample corrected standardized differences, and one-way ANOVA summarize valid per-term entropies. Groups with fewer than two usable values are omitted. These are exploratory comparisons. Terms can belong to multiple groups and derive contexts from shared documents, violating the simple independence interpretation. Multiplicity correction does not repair dependence, retrieval bias, or unequal context counts. Threshold crossings do not establish calibrated population significance or causal effects. Confirmatory inference requires independent annotation and a document-level sampling model accounting for shared terms and overlapping domains.

### Conceptual Network Analysis

The conceptual map assigns terms to six predefined categories. Its {{CORPUS_RELATIONSHIP_COUNT}} links summarize vocabulary overlap:

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

All {{BHL_DOCUMENTS}} stored BHL documents enter literal seed-term frequencies per 10,000 OCR tokens by era. Literal spellings, hyphens, and OCR errors affect rates. The computational stack streams extraction and framing over all stored documents by default. Coverage metadata record available and analyzed documents and characters. Entropy is restricted to twenty frequent candidates per era, drawing contexts from all era documents. An optional positive development character budget selects complete documents by deterministic dyadic traversal across shard order; its fingerprint and coverage metadata distinguish it from a complete run. Neither the full stored corpus nor a bounded development selection is presumed representative of historical entomology.

### Validation and Reproducibility

Tests exercise numerical examples, real files, corpus slices, and local HTTP servers. Negative controls reject malformed text, stale content, missing receipts, and failed renderer commands. They establish software behavior, not scientific validity of the proxy measures. Python dependencies are resolved by uv.lock; NLTK resources are separate prerequisites. Corpus values remain manuscript placeholders. Content fingerprints bind analyses to ordered records, project source, and locked dependencies. A completed manifest binds input and output files; rendering rejects changed artifacts and nonzero toolchain exits.
