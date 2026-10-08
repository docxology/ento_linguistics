# Discussion {#sec:discussion}

## Language and Scientific Practice

The descriptive outputs organize terminology into a framework for examining the relationship between language and biological explanation. They are compatible with asking whether scientific metaphors influence inquiry \citep{latour1987, longino1990, lakoff1980metaphors}, but do not test that causal hypothesis. Keyword frequency, sentence-cluster entropy, and co-occurrence identify lexical patterns rather than researchers' beliefs, decisions, or errors.

Terms such as *queen*, *worker*, and *caste* deserve contextual scrutiny because biological roles and ordinary-language connotations can differ. Existing discussions of terminology reform provide a substantive motivation \citep{herbers2006, herbers2007}. The present corpus analysis neither establishes that terminology delayed particular discoveries nor measures the adoption of alternatives across the field. Such claims would require dated source analysis and evidence about research decisions.

The observed graph has clustering coefficient {{NETWORK_CLUSTERING}}, while {{CORPUS_MULTIDOMAIN_PERCENTAGE}}\% of assigned terms receive multiple labels. Neither quantity demonstrates self-reinforcing conceptual bias. Co-occurrence can arise because papers discuss several biological processes together; label overlap also follows from the predefined lexicons. A visualization's arrangement must not be read as a human-style command hierarchy.

## Network Structure and Its Conditional Reference

A dense co-occurrence graph needs a reference that accounts for vocabulary selection and document-level opportunity. The companion fixed-margin extension preserves selected-term counts within documents and the document frequency of each term. In the executed finite-chain comparisons, the observed graph has fewer edges and lower clustering than the randomized reference. The same direction appears under the longer-burn, wider-spacing sensitivity protocol. The substantive interpretation is concentration of co-occurrence relative to those margins, rather than exceptional density attributable to terminology alone. Topic, genre and other sources of document organization remain possible explanations. A graph's visual density is therefore an observation to explain, not evidence of conceptual bias by itself.

The extension also makes vocabulary sensitivity explicit. Changing the frequency-ranked subset changes the projection and the amount of connectivity it can display. Interpretation should state the selected vocabulary, the incidence margins and the comparison model. The comparison is separately receipted, so its inputs and outputs can be inspected independently of the corpus analysis.

## Biological Precision and Terminological Continuity

A terminology decision has several possible costs: obscuring a biological distinction, inviting an unsupported analogy, or making relevant literature harder to retrieve. These costs need not move together. For example, replacing a developmental category with a task description may lose information even when the replacement sounds less anthropomorphic. The Introduction's distinction between a definitional question (what counts as a caste) and a mechanistic one (how experience shapes division of labor) is the distinction a useful glossary should preserve.

The practical unit of revision is therefore a defined use in a passage. Authors can specify the organism or collective being measured, the criteria for category membership, and the mechanism supported by their observations. Linking an alternative expression to established indexing vocabulary can retain discoverability. CACE can structure that review, but its aggregate should accompany the definition and evidential rationale rather than decide which expression is biologically correct.

## Active Inference as a Theoretical Perspective

Active Inference offers a vocabulary for discussing generative models, inference, and action \citep{friston2010free, clark2013whatever}. In the Active Inferants study, a simulated ant-foraging model reproduces selected colony phenomena in a laboratory-inspired setting \citep{friedman2021active}. This provides an example of mechanistic modeling without a centralized controller; it does not experimentally compare terminology choices or establish the empirical adequacy of every biological assumption.

Interpreting terminology as a prior is an analogy here; as the Introduction states, no Active Inference model is fitted to the corpus. Whether an ant or colony admits a useful blanket description depends on specified state variables, dynamics, and conditional-independence assumptions \citep{friston2013life, kirchhoff2018markov}; it cannot be settled by changing a noun.

The Environment-Centric Active Inference and related multiscale proposals in Section \ref{sec:supplemental_analysis} should be read as theoretical extensions. They require explicit models and empirical tests before supporting biological or linguistic conclusions.

## A Complex Systems Reading of Terminology

The framework can organize questions about scale, connectivity and feedback without treating a lexical graph as a biological system. For each passage, specify the units (individuals, tasks, interactions or colonies), the relevant state variables, the observation timescale and the coupling being measured. The paper's three networks must remain distinct: observed term co-occurrence, configured category overlap and the biological interactions discussed by the underlying literature. A dense term graph does not supply evidence that the ants have an equally dense communication graph.

This distinction supports productive comparison rather than automatic analogy. A mechanism-based account of task allocation can connect the Power and Labor vocabulary to questions about local information and regulation, while biological individuality asks whether the reported outcome is measured at individual or colony scale. The next empirical step is to annotate these mechanistic commitments in source passages and test agreement on held-out documents. Only then can the framework assess whether a terminology choice helps readers recover the actual units, coupling and conditions of a study. Expanding to other taxa, genres or languages requires a new measurement-validation assessment; reproducible software alone does not establish transportability.

## Practical Use of CACE

CACE makes evaluation criteria inspectable: clarity of operational definitions, suitability of metaphors, consistency of use, and adaptability to new findings. Its numerical implementation is a heuristic instantiation. Penalizing membership in a predefined anthropomorphic vocabulary partly encodes the desired ranking; a favorable score is not independent validation of a replacement term.

The representative-term table includes terms absent from the extraction. Their scores are derived from text features and fallback conventions, as recorded in the Extracted column. In particular, a zero default entropy for an unattested term must not be interpreted as demonstrated specificity. Comparisons between *slave* and *host worker* illustrate these rules, rather than measuring a change in readers' comprehension or research outcomes.

The computed aggregate values are {{CACE_TERM_SLAVE_AGGREGATE}} and {{CACE_TERM_HOST_WORKER_AGGREGATE}}, respectively, with Appropriateness {{CACE_TERM_SLAVE_APPROPRIATENESS}} and {{CACE_TERM_HOST_WORKER_APPROPRIATENESS}}. These values remain useful for inspecting the scoring implementation. Independent assessment should compare definitions and context-specific biological accuracy, collect blinded judgments, measure agreement, and test sensitivity to the chosen weights before treating the scores as a prescriptive standard.

## Cross-Domain Communication

Domain overlap can help select terms for shared glossaries and explicit operational definitions. The six-domain framework is one proposed partition; alternative lexicons and annotation schemes may produce different assignments. Maintaining links to established terminology can support discoverability while clarifying which mechanism or observational category is meant. Benefits to communication remain hypotheses for reader and author studies.

## Measurement Validation and Terminology Intervention

Two study designs separate measurement quality from communication effects. The first is the annotation design specified in Section \ref{sec:measurement_validation}: it tests whether occupancy entropy and lexical indicators track reader-labeled meanings and discourse functions after accounting for term frequency, document length and topic, with agreement and uncertainty reported at the level of the annotated observation.

The second borrows the manipulation logic of metaphor experiments (Section \ref{sec:related_work}). A randomized reader study can hold biological evidence constant while varying an established label, a proposed alternative and an explicit operational definition. Prespecified outcomes include inference accuracy, confidence calibration, recall and literature retrieval. This design tests a terminology effect directly. Comparing its outcomes with CACE rankings then evaluates the scoring proposal using evidence outside the scheme. Researchers and students can be included as prespecified groups rather than assumed to interpret a term identically.

## Limitations

1. **Source custody and relevance.** Some archived abstract strings lack digest-indexed source metadata and are excluded from headline analysis; broad queries include adjacent biology and computational uses. Historical volumes contain mixed topics; PMC retrieval includes correction/retraction notices and repeated boilerplate. Source reconciliation and relevance annotation remain incomplete.
2. **Sampling and accessibility.** Search and availability filters select a convenience corpus. Layers are not matched document samples and differ in extraction threshold, length, genre, and publication history.
3. **OCR and language.** Literal historical matching is sensitive to OCR errors, language, hyphenation, and spelling. Rare or absent matches do not date a concept's origin.
4. **Proxy validity.** Computational clusters are not annotated senses; marker patterns are not validated discourse labels. The pipeline does not measure author intent, cognitive distortion, or causal framing.
5. **Statistical dependence.** Domain groups overlap and share document-derived contexts. Reported test outputs are exploratory; no calibrated confirmatory inference is claimed.
6. **Explicitly bounded components.** PMC discourse uses an approximately one-fifth deterministic text sample; domain CACE uses at most fifty terms; BHL entropy uses twenty frequent terms per era with full-corpus contexts. Default BHL extraction, framing, and literal-frequency calculations include all stored documents; an optional development character cap produces a separately fingerprinted subset.
7. **Unmeasured theory.** No fitted generative model, empirical Markov-blanket estimation, term-reform intervention, or independent human validation is reported.

These boundaries support a focused next study: a frozen, fully reconciled corpus with independent annotations and prespecified document-level analysis, followed by a controlled evaluation of operational terminology.
