# Supplemental Methods: Text Processing and Term Extraction {#sec:supplemental_methods}

This section specifies the input and extraction stages used by the study. The numerical definitions and bounded components are detailed in Section \ref{sec:supplemental_infrastructure}. Developer APIs remain documented in source; support utilities are not additional research measurements.

## Source Layers and Custody

The archived abstract input contains {{CORPUS_STORED_RECORDS}} strings. The headline analysis includes {{CORPUS_PUBLICATIONS}} strings whose SHA-256 digest maps to an identified PubMed record and excludes {{CORPUS_EXCLUDED_UNRECONCILED}} unreconciled strings. Exact digest matches to retrieved PubMed abstracts can recover metadata without changing archived text. Identification establishes a source association, not relevance to ant biology, a complete retrieval history, or independent text annotation.

PMC records retain title, abstract, and body text in their own shard directory. BHL records retain historical OCR and era assignments. arXiv title/abstract records form a separate preprint layer. Those documents are not concatenated into the headline abstract input. The custody audit inspects every stored record and reports missing metadata, duplicate text, identifier disagreement, unused sidecar entries, and invalid text.

Digest-indexed sidecars can retain only one source identity when several records share identical text. These collisions are reported rather than resolved by inventing metadata. Broad searches include adjacent biology, computational terminology and mixed-topic historical volumes. The stored PMC layer includes correction and retraction notices whose repeated boilerplate produces shared body text. Records whose titles begin with a correction, erratum or retraction prefix, including retracted full articles, are retained in the shards but excluded from full-text analysis. Individual relevance, article-type screening and license review remain incomplete.

## Normalization and Token Streams

TextProcessor applies Unicode normalization, lowercase conversion, word tokenization, punctuation filtering, and stop-word removal. Hyphenated and underscored tokens can remain intact. The stop vocabulary combines NLTK English stop words with configured scientific meta-language words. WordNet lemmatization is available and is used for corpus vocabulary summaries; terminology extraction disables lemmatization for its occurrence counts. Consequently a summary's most-common lemma and an extracted surface-form frequency need not have the same spelling.

NLTK sentence tokenization supplies the contexts used for semantic entropy. These sentence contexts differ from the short, processed-token windows retained on extracted Term objects. English-language resources are applied to a heterogeneous stored corpus; this is not a validated multilingual processing pipeline.

NLTK resources are separate downloaded prerequisites. The analysis receipt binds the selected English stopword file, English punkt_tab files and WordNet dictionary bytes (the complete archive when archive-backed). The same hashes enter cache signatures; changing a selected resource requires reanalysis. These hashes identify the installed inputs without vendoring them or guaranteeing automatic restoration. Open Multilingual WordNet is outside this receipt because English lemmatization does not consume it. The source implementation and uv.lock specify Python package dependencies.

## Candidate Extraction and Domain Assignment

TerminologyExtractor counts tokens, applies the layer-specific minimum frequency listed in Methods, and evaluates candidate filters.

Candidate filters retain configured seed words of three to fifty characters before evaluating generic filters. Other candidates enter through scientific patterns, compound separators, or configured scientific substrings. They reject pure numbers but can admit unrelated substring matches and OCR artifacts. Candidate inclusion is therefore broader than biological terminology. For example, skin, making and queensland can remain candidates without receiving a domain label.

The six DOMAIN_SEEDS vocabularies define direct assignments. Compound tokens can inherit labels from seed-word overlap; fallback lexical patterns use word boundaries. An extracted term can receive several labels. Label overlap follows from these rules and does not demonstrate temporal semantic drift or independently annotated meanings.

Candidate iteration is sorted for deterministic output. The extractor stores surface text, lemma, frequency, domain labels, confidence, and deduplicated short contexts.

Extraction confidence combines configured frequency, context and classification features. It is not calibrated against human correctness labels. The pipeline does not report precision, recall, multilingual accuracy, or inter-rater reliability.

## Document Co-occurrence and Concept Categories

The observed terminology graph uses the hundred highest-frequency domain-assigned terms, with lexical tie-breaking. Case-insensitive whole-word searches identify presence in each document. A pair's edge weight counts documents containing both terms, regardless of repeated mentions. Shared labels do not create observed edges. The saved graph statistics describe this selected vocabulary rather than the entire field.

The separate concept map uses six predefined categories and vocabulary-association rules. Terms can belong to several categories, so a total of term associations is not a count of unique terms. Category links summarize vocabulary overlap. Node positions, direct-link centrality, colors, and label selection are display conventions and do not establish biological hierarchy or causal dependence.

The overlap heatmap uses the Szymkiewicz--Simpson coefficient in Equation \ref{eq:overlap_coefficient}. Its diagonal is one by construction. A zero observed overlap does not establish conceptual separation.

## Reproducible Inputs and Failure Behavior

DataLoader rejects malformed or empty corpus input, including non-string and blank records. Required pipeline stages propagate failures. Process workers merge results in input order; ENTO_ANALYSIS_WORKERS=1 selects serial execution. Resource-related pool unavailability is logged before a serial retry, while other worker failures propagate.

Caches bind ordered record contents, project Python source, locked dependencies, and explicit development limits. Changed body text invalidates an artifact even if its metadata, record count and file modification time remain unchanged. The completed receipt binds the input/output inventory and image hashes. A receipt establishes which bytes were used, not the scientific validity of the taxonomy or proxies.
