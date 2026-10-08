# Reproducibility and interpretation

[Documentation](../README.md) → Reproducibility and interpretation

The source of truth is the stored corpus plus executable analysis definitions. Generated numbers are bound to input bytes; manuscript placeholders are resolved only when rendering.

## Data lineage

Abstract strings map to digest-indexed PubMed provenance where available. The headline analysis requires a mapped PMID; unreconciled strings remain in the archived input but are excluded. PMC and BHL sidecars key on body/OCR digests; arXiv keys on abstract digests. Identical text under distinct identifiers can collapse metadata in those mappings. In this snapshot, duplicate PMC body groups are standardized retraction-notice text; notices and corrections are included alongside other records. The audit checks both digest coverage and record-ID agreement rather than assuming equal row counts prove custody.

The corpus layers are separate convenience samples. They differ in retrieval, language, date, source genre, document length and extraction threshold. Broad keyword relevance and open-access filtering are not record-level relevance or license certification. [PMC's reuse documentation](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/) explains why availability and license terms must be distinguished. [BHL documents its uncorrected OCR limitations](https://about.biodiversitylibrary.org/ufaqs/why-is-full-text-search-not-finding-all-instances-of-my-search-term-in-a-book-or-in-the-collection/).

## Analysis definitions

Domain labels come from seeds, compound-token overlap and fallback lexical patterns. Short windows provide heuristic contexts, not seed expansion. Candidate inclusion can also follow substring and compound-token filters; unrelated words and OCR artifacts can remain unassigned candidates. Headline extraction does not invoke the n-gram utility.

The conceptual graph uses predefined categories and vocabulary overlap. The terminology graph uses actual shared-document counts among a stated high-frequency vocabulary subset. Its layout cannot be interpreted as a biological hierarchy.

Domain entropy uses sentence contexts, TF-IDF and seeded KMeans. Excluded estimates do not enter means. Occupancy entropy is not a validated count of word senses. Entropy table totals sum valid domain memberships, so a multi-domain term can appear more than once.

Occurrence-context framing proportions share the same definition across abstract and full-text layers. A marker match is a lexical proxy, not a judgment about an author's assumptions. CACE vocabulary penalties encode design choices. Defaults for missing estimates cannot independently demonstrate clarity or consistency.

Welch and ANOVA calculations remain exploratory because terms and groups share observations. BH corrections address their numerical comparison family, without repairing dependence or source selection. Confirmation requires a document-level sampling model and independent annotation.

BHL literal rates, extraction, and framing cover all stored documents by default. Records and cleaned era text are held in memory; counting and framing work per document without a corpus-wide token-position map. Memory is still proportional to stored text, not constant in corpus size. Entropy evaluates the twenty most frequent candidates per era using sentence contexts from the full era corpus. An explicit development character budget can select whole documents; its fingerprint and coverage prevent treating that run as complete. PMC discourse uses a deterministic text sample. These bounded components must remain distinct from full-document extraction and framing.

## Content receipts

Caches include corpus content, implementation signatures, the dependency lock, and the selected English NLTK tokenizer, stopword and WordNet contents. The schema-2 manifest explicitly records their hashes. NLTK search order determines the selected resources, so a user-level installation that shadows the project environment is accounted for. The final manifest hashes input/output inventory entries. Rendering validates that receipt before using template values. A source, corpus, figure or analysis edit requires regeneration. Manuscript prose edits require rendering again; receipts do not certify the correctness of prose.

The pipeline propagates required-stage exceptions and renderer failures. Negative tests exercise changed text with unchanged metadata, corrupted corpus records, invalid limits, missing receipts, changed inventories and real subprocess failure.

Completed BHL eras are saved atomically in local recovery checkpoints. Each checkpoint binds the ordered era records, implementation/dependency/resource signature and any development bound, plus a digest of the completed result. A matching checkpoint can resume a disrupted run; changed inputs or bounds require recomputation, and corrupted matching results fail. The final four-layer receipt is still written only after all required stages complete.

## Reproduction limits

The dependency lock pins Python package versions. Separately installed NLTK resources are content-bound in the receipt, but are not vendored or automatically restored from those hashes. Archive-backed resources bind the whole selected archive; unpacked resources bind ordered relative file names and bytes. Open Multilingual WordNet is not consumed by this English pipeline and is outside this resource receipt. Numerical libraries, platform and fonts can affect exact PDF/image bytes. Semantic algorithms use fixed seeds and stable term ordering; this does not guarantee cross-platform bitwise output identity.

Logs, source custody records, registered figures and a successful PDF build must be reviewed together. Passing tests and content signatures provide software evidence, not a complete source reconciliation, relevance annotation, license audit, human-validation study or scientific release certificate.


## Separately receipted methodological extensions

[The fixed-margin network extension](../../research/network_robustness/README.md) consumes the verified published-core abstract and vocabulary exports. Its implementation lives outside the core generator so the existing four-layer receipt retains its original meaning. The extension has its own input, code, lock and output hashes and retains complete chain traces. A primary protocol and a longer-burn/wider-spacing protocol are preserved separately. This is an additional executed analysis, not a claim that unrelated OCR or full-text computations were rerun.

The current analysis includes the conditional comparison and its independently receipted companion artifacts. The published top-level PDF and Zenodo version are release artifacts; subsequent local manuscript renders do not automatically replace them.

The v1.2.1 extension guard checks decoded numerical artifacts in addition to byte identity. It verifies full chain dimensions, finite statistics and graph bounds, reconstructs the observed graph from the identified abstracts, replays all summary statistics, checks the Markdown result table, and decodes the PNG. Self-hashed corrupt artifacts and inconsistent reports fail. These checks establish internal agreement; they do not certify mixing, causal interpretation, or the scientific validity of lexical proxies.


## Representation sensitivity and complexity

[The network-reading diagnostic](../../research/network_reading/README.md) changes vocabulary size and inclusive shared-document threshold on the verified incidence representation. It keeps isolates and exposes each density denominator; the complete declared grid is reported. Its receipt binds inputs, implementation and plots, and the renderer recomputes the report rather than accepting self-hashed values. It adds no null draws or population uncertainty intervals.

Complex systems provides questions about units, coupling, information, feedback and scale. Density, connectedness and sentence-cluster occupancy do not constitute a universal complexity index. The [source-checked scholarship](../research/complexity-scholarship.md) distinguishes conditional near-decomposability, affiliation projection and biological mechanisms. Transfer across source layers or reader groups requires independent validation.
