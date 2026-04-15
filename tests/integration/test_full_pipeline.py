"""End-to-end integration test for the full analysis pipeline.

Tests the complete flow: corpus loading -> text processing -> term extraction ->
domain analysis -> concept mapping -> data output validation.
Uses the real corpus data if available, falls back to sample corpus.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def corpus_texts():
    """Load real corpus or provide sample texts."""
    corpus_path = PROJECT_DIR / "data" / "corpus" / "abstracts.json"
    if corpus_path.exists():
        with open(corpus_path) as f:
            data = json.load(f)
        abstracts = data if isinstance(data, list) else data.get("abstracts", [])
        # Use first 20 for speed
        return abstracts[:20]

    # Fallback sample corpus
    return [
        "The queen ant lays eggs in the brood chamber. Workers forage for food.",
        "Eusocial insect colonies exhibit division of labor among castes.",
        "Foraging behavior is regulated by local interactions, not centralized control.",
        "Haplodiploidy creates asymmetric relatedness among nestmates in Hymenoptera.",
        "Colony-level selection may operate when individual fitness is subordinated.",
    ]


@pytest.mark.integration
class TestFullPipeline:
    """End-to-end pipeline integration tests."""

    def test_text_processing_pipeline(self, corpus_texts):
        """TextProcessor handles real corpus texts without errors."""
        from analysis.text_analysis import TextProcessor

        processor = TextProcessor()
        for text in corpus_texts:
            tokens = processor.tokenize_words(text)
            assert isinstance(tokens, list)
            assert len(tokens) > 0

            sentences = processor.tokenize_sentences(text)
            assert isinstance(sentences, list)

        stats = processor.get_vocabulary_stats(corpus_texts)
        assert "type_token_ratio" in stats
        assert stats["total_tokens"] > 0
        assert 0.0 < stats["type_token_ratio"] <= 1.0

    def test_term_extraction_pipeline(self, corpus_texts):
        """TerminologyExtractor produces valid terms from corpus."""
        from analysis.term_extraction import TerminologyExtractor

        extractor = TerminologyExtractor()
        terms = extractor.extract_terms(corpus_texts)

        assert isinstance(terms, dict)
        assert len(terms) > 0

        # Validate term structure
        for name, term in terms.items():
            assert hasattr(term, "text")
            assert hasattr(term, "frequency")
            assert hasattr(term, "domains")
            assert term.frequency >= 1

    def test_domain_analysis_pipeline(self, corpus_texts):
        """DomainAnalyzer produces valid domain analyses."""
        from analysis.domain_analysis import DomainAnalyzer
        from analysis.term_extraction import TerminologyExtractor

        extractor = TerminologyExtractor()
        terms = extractor.extract_terms(corpus_texts)

        analyzer = DomainAnalyzer()
        results = analyzer.analyze_all_domains(terms, corpus_texts)

        assert isinstance(results, dict)
        # Should have domain analyses plus possible cross-domain metadata
        assert len(results) > 0

        # Check that at least some entries are DomainAnalysis objects
        from analysis.domain_analysis import DomainAnalysis
        domain_analyses = {
            k: v for k, v in results.items()
            if isinstance(v, DomainAnalysis)
        }
        for domain_name, analysis in domain_analyses.items():
            assert hasattr(analysis, "domain_name")
            assert hasattr(analysis, "key_terms")
            assert hasattr(analysis, "framing_assumptions")

    def test_concept_mapping_pipeline(self, corpus_texts):
        """ConceptualMapper builds valid concept maps."""
        from analysis.conceptual_mapping import ConceptualMapper
        from analysis.term_extraction import TerminologyExtractor

        extractor = TerminologyExtractor()
        terms = extractor.extract_terms(corpus_texts)

        mapper = ConceptualMapper()
        concept_map = mapper.build_concept_map(terms)

        assert concept_map is not None
        assert hasattr(concept_map, "concepts")
        assert isinstance(concept_map.concepts, dict)

    def test_cace_scoring_pipeline(self, corpus_texts):
        """CACE scoring produces bounded scores for extracted terms."""
        from analysis.cace_scoring import evaluate_term_cace
        from analysis.term_extraction import TerminologyExtractor

        extractor = TerminologyExtractor()
        terms = extractor.extract_terms(corpus_texts)

        # Score a sample of terms
        scored = 0
        for name, term in list(terms.items())[:10]:
            result = evaluate_term_cace(
                term=term.text,
                semantic_entropy=0.0,
                contexts=term.contexts,
                domains=term.domains,
            )
            assert 0.0 <= result.clarity <= 1.0
            assert 0.0 <= result.appropriateness <= 1.0
            assert 0.0 <= result.consistency <= 1.0
            assert 0.0 <= result.evolvability <= 1.0
            assert 0.0 <= result.aggregate <= 1.0
            scored += 1

        assert scored > 0

    def test_output_data_schema(self, tmp_path):
        """Validate that saved analysis data matches expected JSON schema."""
        # Check that real output data files have correct structure
        data_dir = PROJECT_DIR / "output" / "data"
        if not data_dir.exists():
            pytest.skip("No output data directory — run pipeline first")

        # corpus_statistics.json
        cs_path = data_dir / "corpus_statistics.json"
        if cs_path.exists():
            with open(cs_path) as f:
                cs = json.load(f)
            assert "total_tokens" in cs
            assert "unique_tokens" in cs
            assert "type_token_ratio" in cs
            assert isinstance(cs["total_tokens"], int)
            assert 0.0 < cs["type_token_ratio"] <= 1.0

        # domain_statistics.json
        ds_path = data_dir / "domain_statistics.json"
        if ds_path.exists():
            with open(ds_path) as f:
                ds = json.load(f)
            expected_domains = {
                "power_and_labor", "unit_of_individuality",
                "sex_and_reproduction", "behavior_and_identity",
                "kin_and_relatedness", "economics",
            }
            assert set(ds.keys()) == expected_domains
            for domain_name, domain_data in ds.items():
                assert "term_count" in domain_data
                assert "total_frequency" in domain_data
                assert "bridging_term_count" in domain_data
                assert isinstance(domain_data["term_count"], int)

        # concept_map_summary.json
        cm_path = data_dir / "concept_map_summary.json"
        if cm_path.exists():
            with open(cm_path) as f:
                cm = json.load(f)
            assert "n_concepts" in cm
            assert "n_relationships" in cm
            assert "network_nodes" in cm
            assert "concepts" in cm

        # extracted_terms.json
        et_path = data_dir / "extracted_terms.json"
        if et_path.exists():
            with open(et_path) as f:
                et = json.load(f)
            assert isinstance(et, dict)
            assert len(et) > 0
            # Spot check a term entry
            first_term = next(iter(et.values()))
            assert "lemma" in first_term
            assert "domains" in first_term
            assert "frequency" in first_term
