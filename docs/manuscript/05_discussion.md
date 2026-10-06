# Discussion {#sec:discussion}

## Language and Scientific Practice

The descriptive outputs organize terminology into a framework for examining the relationship between language and biological explanation. They are compatible with asking whether scientific metaphors influence inquiry \cite{latour1987, longino1990, lakoff1980metaphors}, but do not test that causal hypothesis. Keyword frequency, sentence-cluster entropy, and co-occurrence identify lexical patterns rather than researchers' beliefs, decisions, or errors.

Terms such as *queen*, *worker*, and *caste* deserve contextual scrutiny because biological roles and ordinary-language connotations can differ. Existing discussions of terminology reform provide a substantive motivation \cite{herbers2006, herbers2007}. The present corpus analysis neither establishes that terminology delayed particular discoveries nor measures the adoption of alternatives across the field. Such claims would require dated source analysis and evidence about research decisions.

The observed graph has clustering coefficient {{NETWORK_CLUSTERING}}, while {{CORPUS_MULTIDOMAIN_PERCENTAGE}}\% of assigned terms receive multiple labels. Neither quantity demonstrates self-reinforcing conceptual bias. Co-occurrence can arise because papers discuss several biological processes together; label overlap also follows from the predefined lexicons. A visualization's arrangement must not be read as a human-style command hierarchy.

## Active Inference as a Theoretical Perspective

Active Inference offers a vocabulary for discussing generative models, inference, and action \cite{friston2010free, clark2013whatever}. In the Active Inferants study, a simulated ant-foraging model reproduces selected colony phenomena in a laboratory-inspired setting \cite{friedman2021active}. This provides an example of mechanistic modeling without a centralized controller; it does not experimentally compare terminology choices or establish the empirical adequacy of every biological assumption.

Interpreting terminology as a prior is an analogy here. This repository does not fit an Active Inference model of scientific language, estimate variational free energy from the corpus, or infer Markov blankets from ant behavioral data. Whether an ant or colony admits a useful blanket description depends on specified state variables, dynamics, and conditional-independence assumptions \cite{friston2013life, kirchhoff2018markov}; it cannot be settled by changing a noun.

The Environment-Centric Active Inference and related multiscale proposals in Section \ref{sec:supplemental_analysis} should be read as theoretical extensions. They require explicit models and empirical tests before supporting biological or linguistic conclusions.

## Practical Use of CACE

CACE makes evaluation criteria inspectable: clarity of operational definitions, suitability of metaphors, consistency of use, and adaptability to new findings. Its numerical implementation is a heuristic instantiation. Penalizing membership in a predefined anthropomorphic vocabulary partly encodes the desired ranking; a favorable score is not independent validation of a replacement term.

The representative-term table includes terms absent from the extraction. Their scores are derived from text features and fallback conventions, as recorded by the in-corpus flag. In particular, a zero default entropy for an unattested term must not be interpreted as demonstrated specificity. Comparisons between *slave* and *host worker* illustrate these rules, rather than measuring a change in readers' comprehension or research outcomes.

The computed aggregate values are {{CACE_TERM_SLAVE_AGGREGATE}} and {{CACE_TERM_HOST_WORKER_AGGREGATE}}, respectively, with Appropriateness {{CACE_TERM_SLAVE_APPROPRIATENESS}} and {{CACE_TERM_HOST_WORKER_APPROPRIATENESS}}. These values remain useful for inspecting the scoring implementation. Independent assessment should compare definitions and context-specific biological accuracy, collect blinded judgments, measure agreement, and test sensitivity to the chosen weights before treating the scores as a prescriptive standard.

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
