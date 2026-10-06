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


## Fixed-Margin Network Robustness Extension

A separately receipted companion workflow reconstructs the abstract terminology network from the frozen identified records and the same frequency-ranked vocabulary. It randomizes the binary document--term incidence matrix with Curveball trades \cite{strona2014curveball, carstens2018curveball}. A trade retains common terms in both selected documents and uniformly repartitions their exclusive terms while preserving both row sizes. Consequently, each term retains its document frequency and each document retains its number of selected terms. Self-loop and other no-op transitions remain part of the chain. The total weight of the projected graph equals the sum of the number of term pairs in each document; this quantity is an invariant of the conditioning margins.

Every retained draw checks the two margins and the weight invariant. The workflow reports projected edge count, mean local unweighted clustering, retained-chain traces, between-chain diagnostics and empirical conditional distributions. It also evaluates observed projections under smaller vocabulary subsets of the same ranking. A second protocol uses longer burn-in and spacing with different seeds. These checks assess structural interpretation and sampling sensitivity. Finite correlated draws and between-chain agreement do not prove convergence to the stationary distribution. Conditional null envelopes describe the sampled reference and are distinct from population confidence intervals.

The companion implementation is in research/network\_robustness/. Its receipt binds the published-core input receipt, exact source inputs, extension implementation, dependency lock and generated outputs. It does not relabel cached core results as newly recomputed analyses. The executed report and trace array are provided as companion artifacts to version 1.2.0.
