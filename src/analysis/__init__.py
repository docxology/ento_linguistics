"""Analysis sub-package for Ento-Linguistic research.

Provides modules for discourse analysis, domain analysis, conceptual mapping,
term extraction, text analysis, statistics, semantic entropy, CACE scoring,
and performance metrics.
"""

from .cace_scoring import (
    ANTHROPOMORPHIC_TERMS,
    CACEScore,
    compare_terms_cace,
    evaluate_term_cace,
    mean_context_similarity,
    score_appropriateness,
    score_clarity,
    score_evolvability,
)
from .conceptual_mapping import Concept, ConceptMap, ConceptualMapper
from .discourse_analysis import (
    ArgumentativeStructure,
    DiscourseAnalyzer,
    DiscoursePattern,
)
from .discourse_patterns import (
    DISCOURSE_MARKERS,
    extract_argumentative_structure,
    identify_patterns_in_text,
)
from .domain_analysis import DomainAnalysis, DomainAnalyzer
from .performance import ConvergenceMetrics, ScalabilityMetrics
from .persuasive_analysis import (
    analyze_persuasive_techniques,
    analyze_term_usage_context,
    measure_persuasive_effectiveness,
    quantify_framing_effects,
    track_conceptual_shifts,
)
from .rhetorical_analysis import (
    analyze_narrative_frequency,
    analyze_rhetorical_strategies,
    identify_narrative_frameworks,
    quantify_rhetorical_patterns,
    score_argumentative_structures,
)
from .semantic_entropy import (
    HIGH_ENTROPY_THRESHOLD,
    SemanticEntropyResult,
    calculate_corpus_entropy,
    calculate_semantic_entropy,
    get_high_entropy_terms,
)
from .statistics import DescriptiveStats
from .term_extraction import Term, TerminologyExtractor
from .text_analysis import LinguisticFeatureExtractor, TextProcessor

__all__ = [
    "ANTHROPOMORPHIC_TERMS",
    # discourse_patterns
    "DISCOURSE_MARKERS",
    "HIGH_ENTROPY_THRESHOLD",
    # discourse_analysis
    "ArgumentativeStructure",
    # cace_scoring
    "CACEScore",
    # conceptual_mapping
    "Concept",
    "ConceptMap",
    "ConceptualMapper",
    # performance
    "ConvergenceMetrics",
    # statistics
    "DescriptiveStats",
    "DiscourseAnalyzer",
    "DiscoursePattern",
    # domain_analysis
    "DomainAnalysis",
    "DomainAnalyzer",
    # text_analysis
    "LinguisticFeatureExtractor",
    "ScalabilityMetrics",
    # semantic_entropy
    "SemanticEntropyResult",
    # term_extraction
    "Term",
    "TerminologyExtractor",
    "TextProcessor",
    "analyze_narrative_frequency",
    # persuasive_analysis
    "analyze_persuasive_techniques",
    # rhetorical_analysis
    "analyze_rhetorical_strategies",
    "analyze_term_usage_context",
    "calculate_corpus_entropy",
    "calculate_semantic_entropy",
    "compare_terms_cace",
    "evaluate_term_cace",
    "extract_argumentative_structure",
    "get_high_entropy_terms",
    "identify_narrative_frameworks",
    "identify_patterns_in_text",
    "mean_context_similarity",
    "measure_persuasive_effectiveness",
    "quantify_framing_effects",
    "quantify_rhetorical_patterns",
    "score_appropriateness",
    "score_argumentative_structures",
    "score_clarity",
    "score_evolvability",
    "track_conceptual_shifts",
]
