# Manuscript data lineage

Current data lineage is content-bound rather than a fixed historical row count. Run the custody audit and inspect generated artifacts for the actual snapshot.

| Layer | Stored source | Analysis | Boundary |
|-------|---------------|----------|----------|
| Abstracts | *data/corpus/abstracts.json*, digest-indexed provenance | *output/data/statistical_analysis.json* and headline exports | Only digest-identified PubMed strings enter headline analysis; originals remain archived |
| PMC | *data/fulltexts/fulltexts_*.json* and provenance | *output/data/fulltext_analysis.json* | All stored records by default; explicit discourse sampling and development limit |
| arXiv | *data/corpus/arxiv_records.json* and nested provenance records | *data/corpus/arxiv_analysis.json* | Separate preprint layer |
| BHL | *data/bhl/corpus_*.json* and provenance | *data/bhl/era_term_usage.json* | All documents for literal rates, extraction and framing by default; twenty-term entropy sample per era |

The custody audit records malformed input, missing digests, repeated body text, source-ID mismatch, and unused metadata. A digest-indexed mapping can collapse different IDs sharing identical text; record count alone does not establish custody. Source identity does not establish relevance, licensing, or annotation validity.

*src/core/manuscript_variables.py* and *src/pipeline/rendering.py* resolve manuscript placeholders from these artifacts. Missing values are not silently borrowed from another project root. Content fingerprints bind ordered records, source implementation, and *uv.lock*. Bounded development settings are included in their respective fingerprints.

*output/figures/figure_registry.json* records image hashes and descriptive captions. The generator checks valid finite JSON, registered image hashes, decodable images, figure inventory, manuscript figure availability, and unresolved numerical placeholders before writing *output/data/analysis_manifest.json*. Rendering validates the receipt before producing the PDF.

See [reproducibility definitions](reproducibility.md), [validation commands](validation_guide.md), and [dated review evidence](review_20261005.md).
