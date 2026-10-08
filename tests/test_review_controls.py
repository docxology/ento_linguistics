"""Independent failure controls for corpus custody, counting and rendering."""
import hashlib
import json
import sys

import pytest

from pipeline.bhl_analysis import _count_term, _count_terms, select_stack_records
from pipeline.corpus_audit import audit_layer
from pipeline.rendering import run_latex_command


def test_bhl_fast_counts_match_nonoverlapping_oracle():
    vocabulary = {"ant": ("ant",), "ant ant": ("ant", "ant"),
                  "division of labor": ("division", "of", "labor"), "absent": ("absent",)}
    tokens = "ant ant ant ant ant division of labor ant".split()
    assert _count_terms(tokens, vocabulary) == {
        name: _count_term(tokens, phrase) for name, phrase in vocabulary.items()}
    assert _count_terms([], vocabulary) == dict.fromkeys(vocabulary, 0)


def test_bhl_sampling_is_explicit_whole_documents_and_deterministic():
    records = [{"full_text": "ant" * 10, "id": i} for i in range(10)]
    chosen = select_stack_records(records, 90)
    assert chosen == select_stack_records(records, 90)
    assert len(chosen) == 3
    assert chosen == sorted(chosen, key=lambda item: item["id"])
    assert select_stack_records(records, 1000) == records
    with pytest.raises(ValueError):
        select_stack_records(records, 0)
    with pytest.raises(ValueError):
        select_stack_records(records, 2)


def test_custody_audit_detects_missing_mismatched_and_duplicate_records(tmp_path):
    path = tmp_path / "texts.json"
    path.write_text(json.dumps([{"id": "A", "text": "ant"},
                                {"id": "B", "text": "ant"},
                                {"id": "B", "text": "bee"},
                                {"text": ""}]))
    digest = hashlib.sha256(b"ant").hexdigest()
    result = audit_layer([path], {digest: {"id": "A"}, "unused": {}}, "text", "id")
    assert result["records"] == 4
    assert result["records_without_provenance"] == 1
    assert result["provenance_id_mismatches"] == 1
    assert result["duplicate_text_records"] == 1
    assert result["duplicate_ids"] == 1
    assert result["unused_provenance_entries"] == 1
    assert len(result["invalid_records"]) == 1


def test_render_failure_cannot_be_masked_by_existing_output(tmp_path):
    (tmp_path / "stale.pdf").write_bytes(b"old artifact")
    with pytest.raises(RuntimeError, match="failure-control"):
        run_latex_command([sys.executable, "-c", "print('failure-control'); raise SystemExit(4)"], tmp_path)
    run_latex_command([sys.executable, "-c", "print('real subprocess success')"], tmp_path)


def test_network_count_weights_do_not_create_off_canvas_strokes():
    import matplotlib.pyplot as plt
    from visualization.concept_visualization import ConceptVisualizer
    terms = {"queen": {"frequency": 2000, "domains": ["power_and_labor"]},
             "worker": {"frequency": 1500, "domains": ["power_and_labor"]}}
    figure = ConceptVisualizer().visualize_terminology_network(terms, {("queen", "worker"): 1000})
    widths = [width for collection in figure.axes[0].collections for width in collection.get_linewidths()]
    assert max(widths) <= 4
    plt.close(figure)


def test_reusing_extractor_does_not_retain_another_corpus():
    from analysis.term_extraction import TerminologyExtractor
    from data.loader import DataLoader
    texts = DataLoader().load_corpus()[:2]
    extractor = TerminologyExtractor()
    extractor.extract_terms(texts[:1])
    actual = extractor.extract_terms(texts[1:])
    expected = TerminologyExtractor().extract_terms(texts[1:])
    assert set(actual) == set(expected)
    extractor.extract_terms([])
    assert extractor.extracted_terms == {}


def test_pubmed_doi_from_modern_identifier_metadata():
    """NCBI PMID 41904221 identifies its DOI in articleids metadata."""
    from data.literature_mining import PubMedMiner
    record = {
        "uid": "41904221",
        "title": "Vapor-phase (S)-methoprene alters cuticular hydrocarbons in the Argentine ant (Hymenoptera: Formicidae).",
        "elocationid": "doi: 10.1038/s41598-026-44089-0",
        "articleids": [{"idtype": "doi", "value": "10.1038/s41598-026-44089-0"}],
    }
    publication = PubMedMiner()._parse_pubmed_summary(record)
    assert publication.doi == "10.1038/s41598-026-44089-0"
    record["articleids"] = []
    assert PubMedMiner()._parse_pubmed_summary(record).doi == publication.doi


@pytest.mark.parametrize("record", ["not a record", {"body_text": 12}, {"title": []}])
def test_document_text_rejects_fabricated_string_coercion(record):
    from pipeline.fulltext_pipeline import _document_text
    with pytest.raises(ValueError):
        _document_text(record)


def test_bhl_streamed_vocabulary_matches_canonical_extraction():
    from analysis.term_extraction import TerminologyExtractor
    from pipeline.bhl_analysis import analyze_era_stack, clean_ocr_text
    from pipeline.fulltext_pipeline import _domain_term_counts
    from data.loader import DataLoader
    texts = DataLoader().load_corpus()[:8]
    records = [{"full_text": text} for text in texts]
    canonical = TerminologyExtractor().extract_terms([clean_ocr_text(text) for text in texts], min_frequency=2)
    streamed = analyze_era_stack(records)
    assert streamed["extraction"]["n_terms"] == len(canonical)
    assert streamed["extraction"]["domains"] == _domain_term_counts(canonical)


def test_bhl_default_is_unbounded_and_invalid_caps_fail(monkeypatch):
    from pipeline.bhl_analysis import stack_character_budget
    monkeypatch.delenv("BHL_STACK_CHARACTER_BUDGET", raising=False)
    assert stack_character_budget() is None
    monkeypatch.setenv("BHL_STACK_CHARACTER_BUDGET", "100")
    assert stack_character_budget() == 100
    for value in ("0", "-1", "invalid"):
        monkeypatch.setenv("BHL_STACK_CHARACTER_BUDGET", value)
        with pytest.raises(ValueError):
            stack_character_budget()


def test_registry_failure_report_cannot_be_mislabeled_as_valid(tmp_path):
    from core.validation import ValidationFramework
    result = ValidationFramework().validate_figure_registry(str(tmp_path / "missing.json"), str(tmp_path))
    assert not result.is_valid


def test_output_failure_report_cannot_be_mislabeled_as_valid(tmp_path):
    from core.validation import ValidationFramework
    assert not ValidationFramework().validate_outputs(str(tmp_path / "missing")).is_valid


def test_cace_figure_uses_the_statistical_sample():
    import matplotlib.pyplot as plt
    import numpy as np
    from analysis.term_extraction import TerminologyExtractor
    from pipeline.statistics_pipeline import _domain_cace_scores
    from visualization.manuscript_figures import load_real_corpus
    from visualization.concept_visualization import ConceptVisualizer
    texts = load_real_corpus(require_provenance=True)[:400]
    terms = TerminologyExtractor().extract_terms(texts, min_frequency=1)
    domain = 'unit_of_individuality'
    selected = [term for term in terms.values() if domain in term.domains]
    assert len(selected) > 50
    expected = float(np.mean([score.aggregate for score in _domain_cace_scores(selected)]))
    fig = ConceptVisualizer().create_domain_comparison_plot({domain: {'term_count':len(selected)}}, terms=terms)
    actual = fig.axes[5].patches[0].get_width()
    plt.close(fig)
    assert actual == pytest.approx(expected)


def test_missing_cace_data_is_not_a_confidence_score():
    import matplotlib.pyplot as plt
    from visualization.concept_visualization import ConceptVisualizer
    fig = ConceptVisualizer().create_domain_comparison_plot({'economics': {'avg_confidence':0.9}})
    values = [patch.get_width() for patch in fig.axes[5].patches]
    labels = [text.get_text() for text in fig.axes[5].texts]
    plt.close(fig)
    assert 'n/a' in labels
    import numpy as np
    assert all(np.isnan(value) for value in values)


def test_entropy_reuse_does_not_keep_an_old_value_for_an_excluded_term():
    from analysis.domain_analysis import DomainAnalyzer
    from analysis.term_extraction import Term
    from visualization.manuscript_figures import load_real_corpus
    analyzer = DomainAnalyzer()
    term = Term(text='queen', lemma='queen', domains=['power_and_labor'])
    analyzer.iter_domain_term_entropies([term], load_real_corpus(require_provenance=True)[:400])
    assert term.entropy_status == 'ok' and term.semantic_entropy > 0
    assert analyzer.iter_domain_term_entropies([term], []) == {}
    assert term.entropy_status == 'insufficient_contexts'
    assert term.semantic_entropy == 0


def test_every_single_word_domain_seed_is_a_candidate():
    from analysis.term_extraction import TerminologyExtractor
    extractor = TerminologyExtractor()
    seeds = {word for words in extractor.DOMAIN_SEEDS.values() for word in words
             if 3 <= len(word) <= 50 and not word.isdigit() and ' ' not in word}
    assert not {word for word in seeds if not extractor._is_candidate_term(word)}


def test_core_seed_frequencies_match_real_processed_literature():
    from collections import Counter
    from analysis.term_extraction import TerminologyExtractor
    from analysis.text_analysis import TextProcessor
    from visualization.manuscript_figures import load_real_corpus
    texts = load_real_corpus(require_provenance=True)[:400]
    processor = TextProcessor()
    counts = Counter(token for text in texts for token in processor.process_text(text, lemmatize=False))
    terms = TerminologyExtractor().extract_terms(texts, min_frequency=1)
    for word in ['ant','nest','brood']:
        assert counts[word] > 0
        assert terms[word].frequency == counts[word]


def test_named_cace_tokens_expose_extraction_status():
    from core.manuscript_variables import build_statistical_tokens
    terms = {
        'queen': {'in_corpus': True},
        'primary reproductive': {'in_corpus': False},
        'unreported': {},
    }
    values = build_statistical_tokens({'cace_terms': terms})
    assert values['CACE_TERM_QUEEN_IN_CORPUS'] == 'yes'
    assert values['CACE_TERM_PRIMARY_REPRODUCTIVE_IN_CORPUS'] == 'no'
    assert values['CACE_TERM_UNREPORTED_IN_CORPUS'] == 'unknown'
