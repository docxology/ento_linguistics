# Conclusion {#sec:conclusion}

This work provides a six-domain framework and a reproducible descriptive pipeline for examining terminology in scientific text. Across {{CORPUS_PUBLICATIONS}} stored abstracts, the pipeline processes {{CORPUS_TOTAL_TOKENS}} tokens and extracts {{CORPUS_CANDIDATE_TERMS}} candidate terms, with {{CORPUS_DOMAIN_TERMS}} receiving domain assignments. Observed document co-occurrence, predefined conceptual-category overlap, sentence-context entropy, and heuristic framing and CACE scores are reported as distinct quantities.

The {{CORPUS_MULTIDOMAIN_PERCENTAGE}}\% of assigned terms with multiple labels measures classification overlap, not semantic drift. The {{CORPUS_CONCEPT_COUNT}} concept categories are predefined rather than discovered. Complementary source layers extend the descriptive scope without establishing that language causes bias, that a terminology reform improves scientific modeling, or that numerical CACE rankings are independently validated.

## Future Directions

The immediate research priorities are source reconciliation, document-level relevance and license review, and independent annotation of senses and framing. A frozen annotated corpus would support tests of extraction accuracy, agreement between annotators, context-count sensitivity, and statistical models accounting for shared documents and overlapping domain labels.

Longitudinal analysis should distinguish changes in source composition and OCR quality from changes in terminology. Multilingual comparisons require language-specific normalization and definitions. Reader or author experiments could then evaluate whether operational definitions and alternative terms improve comprehension or mechanistic explanation.

CACE offers explicit evaluation questions for such studies. Its current scores provide an inspectable starting point, with design choices and missing-data conventions disclosed. Active Inference and multiscale interpretations remain theoretical proposals until connected to specified models and empirical measurements. The repository contributes tools and auditable descriptive results for that work.
