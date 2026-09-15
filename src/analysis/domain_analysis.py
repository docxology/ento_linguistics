"""Domain analysis for Ento-Linguistic research.

This module provides specialized analysis functions for each of the six
Ento-Linguistic domains, examining how terminology structures understanding
within specific conceptual areas.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from .term_extraction import Term, filter_matching_sentences
from .text_analysis import LinguisticFeatureExtractor, TextProcessor

__all__ = [
    "DomainAnalysis",
    "DomainAnalyzer",
]

# Function words excluded from lexical keyword-support computation so that
# stop-word overlap cannot inflate support ratios.
_CONTENT_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "were",
    "which", "with", "rather", "than", "into", "over", "not", "no",
}


@dataclass
class DomainAnalysis:
    """Results of domain-specific analysis.

    Attributes:
        domain_name: Name of the Ento-Linguistic domain
        key_terms: Most important terms in this domain
        term_patterns: Common linguistic patterns
        framing_assumptions: Identified framing assumptions
        conceptual_structure: How concepts are organized
        ambiguities: Identified ambiguities and their contexts
        recommendations: Suggestions for clearer communication
        frequency_stats: Statistical analysis of term frequencies
        cooccurrence_analysis: Term co-occurrence patterns
        ambiguity_metrics: Quantified ambiguity metrics
        confidence_scores: Lexical keyword-support ratios for framing
            assumptions (NOT statistical confidence)
        statistical_significance: Statistical significance of term patterns
    """

    domain_name: str
    key_terms: List[str] = field(default_factory=list)
    term_patterns: Dict[str, int] = field(default_factory=dict)
    framing_assumptions: List[str] = field(default_factory=list)
    conceptual_structure: Dict[str, Any] = field(default_factory=dict)
    ambiguities: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    frequency_stats: Dict[str, Any] = field(default_factory=dict)
    cooccurrence_analysis: Dict[str, Any] = field(default_factory=dict)
    ambiguity_metrics: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    conceptual_metrics: Dict[str, Any] = field(default_factory=dict)
    statistical_significance: Dict[str, Any] = field(default_factory=dict)


class DomainAnalyzer:
    """Analyze terminology within specific Ento-Linguistic domains.

    This class provides domain-specific analysis methods that examine
    how terminology structures understanding within each of the six domains.
    """

    def __init__(self):
        """Initialize domain analyzer."""
        self.text_processor = TextProcessor()
        self.feature_extractor = LinguisticFeatureExtractor()

    def analyze_all_domains(
        self, terms: Dict[str, Term], texts: List[str]
    ) -> Dict[str, DomainAnalysis]:
        """Analyze all six Ento-Linguistic domains.

        Args:
            terms: Dictionary of extracted terms
            texts: Source texts for context

        Returns:
            Dictionary mapping domain names to DomainAnalysis results.  The
            cross-domain overlap analysis is deliberately NOT mixed into this
            mapping (a plain dict under a magic key broke ``compare_domains``
            and every consumer expecting DomainAnalysis values); callers who
            need it invoke ``analyze_cross_domain_overlap(terms)`` separately.

        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if not isinstance(terms, dict):
            raise ValueError("terms must be a dictionary")
        if not isinstance(texts, list):
            raise ValueError("texts must be a list")
        if not terms:
            return {}  # Nothing to analyze

        domain_analyses = {}

        # Group terms by domain
        domain_terms = self._group_terms_by_domain(terms)

        # Analyze each domain
        domain_methods = {
            "unit_of_individuality": self._analyze_individuality_domain,
            "behavior_and_identity": self._analyze_behavior_domain,
            "power_and_labor": self._analyze_power_domain,
            "sex_and_reproduction": self._analyze_reproduction_domain,
            "kin_and_relatedness": self._analyze_kinship_domain,
            "economics": self._analyze_economics_domain,
        }

        for domain_name, terms_list in domain_terms.items():
            if domain_name in domain_methods:
                analysis = domain_methods[domain_name](terms_list, texts)

                # Add statistical analysis
                analysis.frequency_stats = self.analyze_term_frequency_distribution(
                    terms_list, texts
                )
                analysis.cooccurrence_analysis = self.analyze_term_cooccurrence(
                    terms_list, texts
                )
                analysis.ambiguity_metrics = self.quantify_ambiguity_metrics(
                    terms_list, texts
                )
                analysis.confidence_scores = self.generate_confidence_scores(
                    analysis.framing_assumptions, terms_list, texts
                )
                analysis.conceptual_metrics = self.quantify_conceptual_structure(
                    analysis.conceptual_structure, terms_list
                )
                analysis.statistical_significance = (
                    self.calculate_statistical_significance(analysis.term_patterns)
                )

                domain_analyses[domain_name] = analysis

        return domain_analyses

    def _group_terms_by_domain(self, terms: Dict[str, Term]) -> Dict[str, List[Term]]:
        """Group terms by their Ento-Linguistic domains.

        Args:
            terms: Dictionary of terms

        Returns:
            Dictionary mapping domain names to term lists
        """
        domain_groups = defaultdict(list)

        for term in terms.values():
            for domain in term.domains:
                domain_groups[domain].append(term)

        return dict(domain_groups)

    def _analyze_individuality_domain(
        self, terms: List[Term], texts: List[str]
    ) -> DomainAnalysis:
        """Analyze the Unit of Individuality domain.

        Args:
            terms: Terms in this domain
            texts: Source texts

        Returns:
            Domain analysis results
        """
        analysis = DomainAnalysis(domain_name="unit_of_individuality")

        # Key terms analysis
        term_texts = [term.text for term in terms]
        analysis.key_terms = self._extract_key_terms(term_texts, top_n=10)

        # Pattern analysis
        analysis.term_patterns = self._analyze_term_patterns(terms)

        # Framing assumptions
        analysis.framing_assumptions = [
            "Individuality exists on a single biological scale",
            "Colony-level traits are emergent rather than individual",
            "Superorganism concept implies loss of individual agency",
            "Nestmate recognition defines individual boundaries",
        ]

        # Conceptual structure
        analysis.conceptual_structure = {
            "scale_hierarchy": ["gene", "cell", "organism", "colony", "population"],
            "individuality_types": ["genetic", "physiological", "behavioral", "social"],
            "boundary_concepts": ["recognition", "kinship", "cooperation", "conflict"],
        }

        # Ambiguities
        analysis.ambiguities = [
            {
                "term": "colony",
                "contexts": [
                    "reproductive unit",
                    "behavioral entity",
                    "ecological unit",
                ],
                "issue": "Shifts meaning across biological scales",
            },
            {
                "term": "individual",
                "contexts": ["nestmate", "colony member", "genetic individual"],
                "issue": "Multiple biological scales of individuality",
            },
        ]

        # Recommendations
        analysis.recommendations = [
            "Specify biological scale when using individuality terms",
            "Distinguish between genetic, physiological, and social individuality",
            "Use 'colony-level' vs 'individual-level' traits explicitly",
            "Avoid assuming single scale of biological organization",
        ]

        return analysis

    def _analyze_behavior_domain(
        self, terms: List[Term], texts: List[str]
    ) -> DomainAnalysis:
        """Analyze the Behavior and Identity domain.

        Args:
            terms: Terms in this domain
            texts: Source texts

        Returns:
            Domain analysis results
        """
        analysis = DomainAnalysis(domain_name="behavior_and_identity")

        # Key terms
        term_texts = [term.text for term in terms]
        analysis.key_terms = self._extract_key_terms(term_texts, top_n=10)

        # Pattern analysis
        analysis.term_patterns = self._analyze_term_patterns(terms)

        # Framing assumptions
        analysis.framing_assumptions = [
            "Behavioral categories reflect discrete identities",
            "Task performance defines individual identity",
            "Behavioral specialization is fixed and heritable",
            "Foraging behavior indicates specialized role",
        ]

        # Conceptual structure
        analysis.conceptual_structure = {
            "identity_types": ["task-based", "age-based", "size-based", "genetic"],
            "behavior_categories": ["foraging", "nursing", "defense", "reproduction"],
            "plasticity_concepts": ["developmental", "environmental", "social"],
        }

        # Ambiguities
        analysis.ambiguities = [
            {
                "term": "forager",
                "contexts": [
                    "observed carrying food",
                    "genetically predisposed",
                    "temporarily assigned",
                ],
                "issue": "Identity vs behavior vs observation",
            },
            {
                "term": "worker",
                "contexts": [
                    "sterile female",
                    "non-reproductive adult",
                    "task-performing individual",
                ],
                "issue": "Reproductive status vs behavioral role",
            },
        ]

        # Recommendations
        analysis.recommendations = [
            "Distinguish between behavioral observations and identities",
            "Specify whether roles are fixed or plastic",
            "Use 'behavioral specialization' rather than 'caste identity'",
            "Avoid assuming heritability of behavioral roles",
        ]

        return analysis

    def _analyze_power_domain(
        self, terms: List[Term], texts: List[str]
    ) -> DomainAnalysis:
        """Analyze the Power & Labor domain.

        Args:
            terms: Terms in this domain
            texts: Source texts

        Returns:
            Domain analysis results
        """
        analysis = DomainAnalysis(domain_name="power_and_labor")

        # Key terms
        term_texts = [term.text for term in terms]
        analysis.key_terms = self._extract_key_terms(term_texts, top_n=10)

        # Pattern analysis
        analysis.term_patterns = self._analyze_term_patterns(terms)

        # Framing assumptions
        analysis.framing_assumptions = [
            "Social organization mirrors human hierarchical structures",
            "Power relationships are analogous to human societies",
            "Labor division reflects inherent inequalities",
            "Queen dominance implies worker subordination",
        ]

        # Conceptual structure
        analysis.conceptual_structure = {
            "power_types": ["reproductive", "behavioral", "resource", "spatial"],
            "hierarchy_levels": ["queen", "major workers", "minor workers", "soldiers"],
            "control_mechanisms": ["chemical", "behavioral", "physical", "genetic"],
        }

        # Ambiguities
        analysis.ambiguities = [
            {
                "term": "caste",
                "contexts": [
                    "morphological difference",
                    "behavioral role",
                    "social status",
                ],
                "issue": "Biological vs social category",
            },
            {
                "term": "slave",
                "contexts": [
                    "captured worker",
                    "social parasite",
                    "metaphorical usage",
                ],
                "issue": "Biological relationship vs human analogy",
            },
        ]

        # Recommendations
        analysis.recommendations = [
            "Use 'morphological caste' or 'behavioral caste' explicitly",
            "Avoid human social terms like 'slave' and 'parasite'",
            "Specify mechanisms of social control",
            "Use 'reproductive skew' rather than 'queen dominance'",
        ]

        return analysis

    def _analyze_reproduction_domain(
        self, terms: List[Term], texts: List[str]
    ) -> DomainAnalysis:
        """Analyze the Sex & Reproduction domain.

        Args:
            terms: Terms in this domain
            texts: Source texts

        Returns:
            Domain analysis results
        """
        analysis = DomainAnalysis(domain_name="sex_and_reproduction")

        # Key terms
        term_texts = [term.text for term in terms]
        analysis.key_terms = self._extract_key_terms(term_texts, top_n=10)

        # Pattern analysis
        analysis.term_patterns = self._analyze_term_patterns(terms)

        # Framing assumptions
        analysis.framing_assumptions = [
            "Sex determination follows binary human model",
            "Reproductive roles determine social status",
            "Mating systems analogous to human relationships",
            "Parental investment follows human patterns",
        ]

        # Conceptual structure
        analysis.conceptual_structure = {
            "sex_systems": [
                "haplodiploidy",
                "environmental sex determination",
                "genetic sex determination",
            ],
            "reproductive_strategies": [
                "monogamy",
                "polygyny",
                "polyandry",
                "clonal reproduction",
            ],
            "mating_systems": [
                "monogyny",
                "polygyny",
                "pleometrosis",
                "secondary monogyny",
            ],
        }

        # Ambiguities
        analysis.ambiguities = [
            {
                "term": "sex determination",
                "contexts": ["chromosomal", "environmental", "social"],
                "issue": "Multiple mechanisms conflated",
            },
            {
                "term": "female",
                "contexts": [
                    "reproductive queen",
                    "sterile worker",
                    "developmental stage",
                ],
                "issue": "Reproductive capacity vs morphological sex",
            },
        ]

        # Recommendations
        analysis.recommendations = [
            "Specify mechanism of sex determination",
            "Use 'reproductive female' vs 'morphological female'",
            "Avoid assuming binary sex determination",
            "Specify reproductive strategy explicitly",
        ]

        return analysis

    def _analyze_kinship_domain(
        self, terms: List[Term], texts: List[str]
    ) -> DomainAnalysis:
        """Analyze the Kin & Relatedness domain.

        Args:
            terms: Terms in this domain
            texts: Source texts

        Returns:
            Domain analysis results
        """
        analysis = DomainAnalysis(domain_name="kin_and_relatedness")

        # Key terms
        term_texts = [term.text for term in terms]
        analysis.key_terms = self._extract_key_terms(term_texts, top_n=10)

        # Pattern analysis
        analysis.term_patterns = self._analyze_term_patterns(terms)

        # Framing assumptions
        analysis.framing_assumptions = [
            "Kinship follows human family structures",
            "Relatedness is primarily genetic",
            "Kin recognition requires genetic similarity",
            "Family relationships mirror human patterns",
        ]

        # Conceptual structure
        analysis.conceptual_structure = {
            "relatedness_types": ["genetic", "phenotypic", "environmental", "social"],
            "kinship_mechanisms": [
                "recognition",
                "discrimination",
                "cooperation",
                "conflict",
            ],
            "relatedness_measures": [
                "coefficient",
                "distance",
                "similarity",
                "correlation",
            ],
        }

        # Ambiguities
        analysis.ambiguities = [
            {
                "term": "kin",
                "contexts": [
                    "genetic relatives",
                    "social affiliates",
                    "colony members",
                ],
                "issue": "Genetic vs social kinship",
            },
            {
                "term": "family",
                "contexts": ["nuclear family", "colony kin group", "mating pair"],
                "issue": "Human family structures vs insect groupings",
            },
        ]

        # Recommendations
        analysis.recommendations = [
            "Specify type of relatedness (genetic, social, environmental)",
            "Use 'relatedness coefficient' for genetic measures",
            "Avoid 'family' for insect groupings",
            "Specify mechanisms of kin recognition",
        ]

        return analysis

    def _analyze_economics_domain(
        self, terms: List[Term], texts: List[str]
    ) -> DomainAnalysis:
        """Analyze the Economics domain.

        Args:
            terms: Terms in this domain
            texts: Source texts

        Returns:
            Domain analysis results
        """
        analysis = DomainAnalysis(domain_name="economics")

        # Key terms
        term_texts = [term.text for term in terms]
        analysis.key_terms = self._extract_key_terms(term_texts, top_n=10)

        # Pattern analysis
        analysis.term_patterns = self._analyze_term_patterns(terms)

        # Framing assumptions
        analysis.framing_assumptions = [
            "Colony economics mirror human market systems",
            "Resource allocation follows market principles",
            "Costs and benefits analogous to human economics",
            "Optimization implies conscious decision-making",
        ]

        # Conceptual structure
        analysis.conceptual_structure = {
            "resource_types": ["food", "space", "information", "social capital"],
            "allocation_mechanisms": [
                "competition",
                "cooperation",
                "division of labor",
                "storage",
            ],
            "economic_measures": [
                "efficiency",
                "productivity",
                "cost-benefit",
                "optimization",
            ],
        }

        # Ambiguities
        analysis.ambiguities = [
            {
                "term": "trade",
                "contexts": ["resource exchange", "trophallaxis", "metaphorical usage"],
                "issue": "Biological exchange vs economic metaphor",
            },
            {
                "term": "cost",
                "contexts": ["energetic expenditure", "risk", "opportunity cost"],
                "issue": "Multiple types of costs conflated",
            },
        ]

        # Recommendations
        analysis.recommendations = [
            "Specify type of resource allocation mechanism",
            "Use 'resource exchange' rather than 'trade'",
            "Specify cost type (energetic, risk, opportunity)",
            "Avoid assuming conscious economic decision-making",
        ]

        return analysis

    def _extract_key_terms(self, term_texts: List[str], top_n: int = 10) -> List[str]:
        """Extract most important terms by frequency.

        Args:
            term_texts: List of term texts
            top_n: Number of top terms to return

        Returns:
            List of top terms
        """
        term_counts = Counter(term_texts)
        return [term for term, _ in term_counts.most_common(top_n)]

    def _analyze_term_patterns(self, terms: List[Term]) -> Dict[str, int]:
        """Analyze linguistic patterns in terms.

        Args:
            terms: List of terms to analyze

        Returns:
            Dictionary of pattern counts
        """
        patterns = Counter()

        for term in terms:
            # Compound words
            if "_" in term.text or "-" in term.text:
                patterns["compound"] += 1

            # Multi-word terms
            if " " in term.text:
                patterns["multi_word"] += 1

            # Capitalized terms
            if term.text[0].isupper():
                patterns["capitalized"] += 1

            # Scientific abbreviations
            if re.match(r"^[A-Z]{2,}$", term.text):
                patterns["abbreviation"] += 1

            # Number-containing terms
            if any(char.isdigit() for char in term.text):
                patterns["numeric"] += 1

        return dict(patterns)

    def generate_domain_report(self, analysis) -> str:
        """Generate a human-readable report for domain analysis.

        Args:
            analysis: Domain analysis results (DomainAnalysis object or dict)

        Returns:
            Formatted report string
        """
        # Handle both dict and DomainAnalysis object inputs
        if isinstance(analysis, dict):
            domain_name = analysis.get("domain_name", "unknown")
            key_terms = analysis.get("key_terms", [])
            term_patterns = analysis.get("term_patterns", {})
            framing_assumptions = analysis.get("framing_assumptions", [])
            ambiguities = analysis.get("ambiguities", [])
            recommendations = analysis.get("recommendations", [])
        else:
            # DomainAnalysis object
            domain_name = analysis.domain_name
            key_terms = analysis.key_terms
            term_patterns = analysis.term_patterns
            framing_assumptions = analysis.framing_assumptions
            ambiguities = analysis.ambiguities
            recommendations = analysis.recommendations

        report = f"""
# {domain_name.replace('_', ' ').title()} Domain Analysis

## Key Terms
{', '.join(key_terms)}

## Term Patterns
{chr(10).join(f"- {pattern}: {count}" for pattern, count in term_patterns.items())}

## Framing Assumptions
{chr(10).join(f"- {assumption}" for assumption in framing_assumptions)}

## Ambiguities Identified
{chr(10).join(f"- **{amb['term']}**: {amb['issue']} (contexts: {', '.join(amb['contexts'])})" for amb in ambiguities)}

## Recommendations
{chr(10).join(f"- {rec}" for rec in recommendations)}
"""
        return report

    def compare_domains(self, analyses: Dict[str, DomainAnalysis]) -> Dict[str, Any]:
        """Compare patterns across domains.

        Args:
            analyses: Dictionary of domain analyses

        Returns:
            Comparison results
        """
        comparison = {
            "domain_sizes": {
                name: len(analysis.key_terms) for name, analysis in analyses.items()
            },
            "shared_assumptions": self._find_shared_assumptions(analyses),
            "heuristic_cross_domain_notes": self._heuristic_cross_domain_notes(
                analyses
            ),
        }

        return comparison

    def _find_shared_assumptions(
        self, analyses: Dict[str, DomainAnalysis]
    ) -> List[str]:
        """Find assumptions shared across domains.

        Args:
            analyses: Domain analyses

        Returns:
            List of shared assumptions
        """
        all_assumptions = []
        for analysis in analyses.values():
            all_assumptions.extend(analysis.framing_assumptions)

        assumption_counts = Counter(all_assumptions)
        shared = [
            assumption for assumption, count in assumption_counts.items() if count > 1
        ]

        return shared

    def _heuristic_cross_domain_notes(
        self, analyses: Dict[str, DomainAnalysis]
    ) -> List[Dict[str, Any]]:
        """Return fixed editorial notes about cross-domain framing.

        IMPORTANT — NON-EMPIRICAL OUTPUT: the returned list is a hardcoded
        set of methodological commentary items.  It is NOT derived from the
        analyzed data in any way and must not be reported as an empirical
        finding.  Consumers should present it as background notes at most.

        Args:
            analyses: Domain analyses (ignored; accepted for API stability)

        Returns:
            List of non-empirical editorial note dictionaries
        """
        heuristic_notes = [
            {
                "note": "Anthropomorphic framing across domains",
                "affected_domains": [
                    "power_and_labor",
                    "behavior_and_identity",
                    "economics",
                ],
                "description": "Human social concepts applied to insect societies",
            }
        ]

        return heuristic_notes

    def analyze_term_frequency_distribution(
        self, terms: List[Term], texts: List[str]
    ) -> Dict[str, Any]:
        """Analyze term frequency distributions within domains.

        Args:
            terms: List of terms to analyze
            texts: Source texts for context

        Returns:
            Statistical analysis of term frequencies
        """

        import numpy as np

        # Extract term frequencies
        term_freqs = [term.frequency for term in terms]
        term_texts = [term.text for term in terms]

        # Basic statistics
        if term_freqs:
            stats = {
                "mean_frequency": np.mean(term_freqs),
                "median_frequency": np.median(term_freqs),
                "std_frequency": np.std(term_freqs, ddof=1) if len(term_freqs) > 1 else 0.0,
                "min_frequency": min(term_freqs),
                "max_frequency": max(term_freqs),
                "total_occurrences": sum(term_freqs),
                "unique_terms": len(term_freqs),
            }

            # Frequency distribution
            hist, bin_edges = np.histogram(term_freqs, bins="auto")
            stats["frequency_distribution"] = {
                "bins": bin_edges.tolist(),
                "counts": hist.tolist(),
            }

            # Most frequent terms
            sorted_terms = sorted(
                zip(term_texts, term_freqs), key=lambda x: x[1], reverse=True
            )
            stats["top_terms"] = [
                {"term": term, "frequency": freq} for term, freq in sorted_terms[:10]
            ]

        else:
            stats = {"error": "No terms provided for analysis"}

        return stats

    def analyze_term_cooccurrence(
        self, terms: List[Term], texts: List[str], window_size: int = 50
    ) -> Dict[str, Any]:
        """Analyze co-occurrence patterns between terms.

        Each unordered term pair co-occurring within ``window_size`` tokens is
        counted exactly once (canonical pair keys), so
        ``total_cooccurrences`` equals the number of co-occurring pairs, not
        double the number as in earlier implementations that recorded both
        (i, j) and (j, i).

        Args:
            terms: List of terms to analyze
            texts: Source texts for context
            window_size: Size of co-occurrence window

        Returns:
            Co-occurrence analysis results.  ``cooccurrence_matrix`` is a
            symmetric nested dict of per-pair counts.
        """
        from collections import defaultdict

        term_set = {term.text.lower() for term in terms}
        n_terms = len(term_set)
        pair_counts: Dict[tuple, int] = defaultdict(int)
        half_window = window_size // 2

        # Build canonical (unordered) pair counts with set membership lookups
        for text in texts:
            words = text.lower().split()
            for i, word1 in enumerate(words):
                if word1 not in term_set:
                    continue
                start = i + 1
                end = min(len(words), i + half_window + 1)
                for j in range(start, end):
                    word2 = words[j]
                    if word2 in term_set and word2 != word1:
                        pair = tuple(sorted((word1, word2)))
                        pair_counts[pair] += 1

        # Rebuild the symmetric matrix for JSON serialization
        cooccurrence_matrix: Dict[str, Dict[str, int]] = defaultdict(dict)
        for (term1, term2), count in pair_counts.items():
            cooccurrence_matrix[term1][term2] = count
            cooccurrence_matrix[term2][term1] = count

        total_cooccurrences = sum(pair_counts.values())

        return {
            "cooccurrence_matrix": dict(cooccurrence_matrix),
            "total_cooccurrences": total_cooccurrences,
            "unique_term_pairs": len(pair_counts),
            "average_cooccurrences_per_term": (
                total_cooccurrences / n_terms if n_terms else 0
            ),
        }

    def quantify_ambiguity_metrics(
        self, terms: List[Term], texts: List[str]
    ) -> Dict[str, Any]:
        """Quantify ambiguity metrics for terms using Shannon Entropy.

        Delegates to the canonical ``semantic_entropy`` module for the core
        TF-IDF → KMeans → Shannon-entropy pipeline.  Sentences are tokenized
        once for all terms and contexts are matched with the shared
        word-boundary helper ``filter_matching_sentences``.  Results whose
        entropy could not be computed (``status != "ok"``) are flagged and
        excluded from the aggregate domain statistics.

        Args:
            terms: List of terms to analyze
            texts: Source texts for context

        Returns:
            Ambiguity quantification metrics (raw entropy in bits plus the
            normalized entropy fields from ``semantic_entropy``)
        """
        from nltk.tokenize import sent_tokenize

        from .semantic_entropy import HIGH_ENTROPY_THRESHOLD, calculate_semantic_entropy

        ambiguity_scores: Dict[str, Any] = {}

        # Tokenize every text once; reuse the sentence lists for all terms
        tokenized_texts = [sent_tokenize(text) for text in texts]

        for term in terms:
            term_text = term.text.lower()
            contexts: List[str] = []

            # Extract contexts where the term appears (whole-word match)
            for sentences in tokenized_texts:
                for sentence in filter_matching_sentences(sentences, term_text):
                    clean_context = sentence.strip()
                    if len(clean_context.split()) > 3:
                        contexts.append(clean_context)

            # Delegate to canonical semantic entropy module
            result = calculate_semantic_entropy(term=term_text, contexts=contexts)

            ambiguity_scores[term_text] = {
                "total_occurrences": result.n_contexts,
                "entropy_bits": result.entropy_bits,
                "ambiguity_score": result.entropy_bits,
                "is_high_entropy": result.is_high_entropy,
                "entropy_normalized": result.entropy_normalized,
                "h_max": result.h_max,
                "status": result.status,
                "error": result.error,
            }

        # Overall domain ambiguity metrics, excluding failed/unusable results
        if ambiguity_scores:
            domain_scores = list(ambiguity_scores.values())
            valid_scores = [
                s["entropy_bits"] for s in domain_scores if s["status"] == "ok"
            ]

            if valid_scores:
                valid_normalized = [
                    s["entropy_normalized"] for s in domain_scores
                    if s["status"] == "ok"
                ]
                overall_metrics = {
                    "average_entropy": np.mean(valid_scores),
                    "max_entropy": np.max(valid_scores),
                    "average_entropy_normalized": float(np.mean(valid_normalized)),
                    "n_excluded_failures": sum(
                        1 for s in domain_scores if s["status"] != "ok"
                    ),
                    "total_information_loss_bits": np.sum(valid_scores),
                    "highly_ambiguous_terms": [
                        term for term, score in ambiguity_scores.items()
                        if score["status"] == "ok"
                        and score["entropy_bits"] > HIGH_ENTROPY_THRESHOLD
                    ],
                }
            else:
                overall_metrics = {"average_entropy": 0.0}
        else:
            overall_metrics = {"error": "No terms found for ambiguity analysis"}


        return {
            "term_ambiguity_scores": ambiguity_scores,
            "domain_metrics": overall_metrics,
        }

    def analyze_cross_domain_overlap(
        self, terms: Dict[str, Term]
    ) -> Dict[str, Any]:
        """Analyze overlap between terms across different domains.

        Args:
            terms: All terms with their domain classifications

        Returns:
            Cross-domain overlap analysis
        """
        domain_terms = self._group_terms_by_domain(terms)
        from collections import defaultdict

        # Build term-to-domains mapping
        term_domains = defaultdict(set)
        for term_text, term_obj in terms.items():
            if hasattr(term_obj, "domains") and term_obj.domains:
                term_domains[term_text] = set(term_obj.domains)

        # Calculate overlap statistics
        overlap_stats = defaultdict(dict)

        domain_names = list(domain_terms.keys())
        for i, domain1 in enumerate(domain_names):
            for j, domain2 in enumerate(domain_names):
                if i < j:  # Avoid duplicate pairs
                    pair_key = f"{domain1}_{domain2}"

                    # Find terms shared between domains
                    shared_terms = []
                    for term_text, domains in term_domains.items():
                        if domain1 in domains and domain2 in domains:
                            shared_terms.append(term_text)

                    overlap_stats[pair_key] = {
                        "shared_terms": shared_terms,
                        "shared_count": len(shared_terms),
                        "domain1_total": len(domain_terms[domain1]),
                        "domain2_total": len(domain_terms[domain2]),
                        "overlap_percentage": (
                            (
                                len(shared_terms)
                                / min(
                                    len(domain_terms[domain1]),
                                    len(domain_terms[domain2]),
                                )
                            )
                            * 100
                            if min(
                                len(domain_terms[domain1]), len(domain_terms[domain2])
                            )
                            > 0
                            else 0
                        ),
                    }

        # Overall statistics
        all_shared_terms = set()
        for stats in overlap_stats.values():
            all_shared_terms.update(stats["shared_terms"])

        return {
            "domain_pair_overlaps": dict(overlap_stats),
            "total_unique_shared_terms": len(all_shared_terms),
            "average_overlap_percentage": (
                np.mean(
                    [stats["overlap_percentage"] for stats in overlap_stats.values()]
                )
                if overlap_stats
                else 0
            ),
        }

    def calculate_statistical_significance(
        self,
        term_patterns: Dict[str, int],
        expected_patterns: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Calculate statistical significance for term patterns.

        Args:
            term_patterns: Observed term pattern frequencies
            expected_patterns: Expected pattern frequencies (optional)

        Returns:
            Statistical significance analysis
        """
        import numpy as np
        from scipy import stats

        if not term_patterns:
            return {"error": "No patterns provided"}

        # If no expected patterns, use uniform distribution
        if expected_patterns is None:
            total_patterns = sum(term_patterns.values())
            expected_patterns = {
                pattern: total_patterns / len(term_patterns)
                for pattern in term_patterns.keys()
            }

        # Chi-square test for pattern significance
        observed = list(term_patterns.values())
        expected = [
            expected_patterns.get(pattern, 0) for pattern in term_patterns.keys()
        ]

        n_total = sum(observed)
        k = len(observed)
        try:
            chi2_stat, p_value = stats.chisquare(observed, expected)
            significant_patterns = [
                pattern
                for pattern, freq in term_patterns.items()
                if freq > expected_patterns.get(pattern, 0)
            ]

            return {
                "chi_square_statistic": chi2_stat,
                "p_value": p_value,
                "significant_patterns": significant_patterns,
                "significance_threshold": 0.05,
                "is_significant": p_value < 0.05,
                # Cramer's V for the goodness-of-fit case:
                # V = sqrt(chi2 / (N * (k - 1))), k = number of categories
                "effect_size": float(
                    np.sqrt(chi2_stat / (n_total * (k - 1)))
                )
                if n_total > 0 and k > 1
                else 0.0,
            }
        except ValueError as e:
            # scipy raises ValueError for degenerate contingency input
            # (e.g. zero totals or non-positive expected frequencies)
            return {
                "error": f"Statistical analysis failed: {str(e)}",
                "observed_patterns": term_patterns,
            }

    def generate_confidence_scores(
        self, framing_assumptions: List[str], terms: List[Term], texts: List[str]
    ) -> Dict[str, float]:
        """Generate lexical keyword-support ratios for framing assumptions.

        IMPORTANT — NOT STATISTICAL CONFIDENCE: the returned values are the
        fraction of an assumption's content words (stop words excluded) that
        occur lexically in the domain's term vocabulary.  They quantify
        lexical overlap only and must not be reported as confidence levels.

        Args:
            framing_assumptions: List of framing assumptions
            terms: Terms in the domain
            texts: Source texts (unused; kept for API stability)

        Returns:
            Mapping from assumption to keyword-support ratio in [0, 1]
        """
        confidence_scores = {}

        for assumption in framing_assumptions:
            # Content words only: function words must not inflate support
            assumption_keywords = [
                word
                for word in assumption.lower().split()
                if word.isalpha() and word not in _CONTENT_STOP_WORDS
            ]
            if not assumption_keywords or not terms:
                confidence_scores[assumption] = 0.0
                continue

            term_vocab = set()
            for term in terms:
                term_vocab.update(term.text.lower().replace("_", " ").replace("-", " ").split())

            supported_keywords = sum(
                1 for keyword in assumption_keywords if keyword in term_vocab
            )
            confidence_scores[assumption] = supported_keywords / len(
                assumption_keywords
            )

        return confidence_scores

    def quantify_conceptual_structure(
        self, conceptual_structure: Dict[str, Any], terms: List[Term]
    ) -> Dict[str, Any]:
        """Quantify conceptual structure metrics.

        Args:
            conceptual_structure: Conceptual structure dictionary
            terms: Terms in the domain

        Returns:
            Quantitative metrics for conceptual structure
        """
        metrics = {}

        # Concept coverage - how many terms map to concepts
        total_concepts = 0
        for key, value in conceptual_structure.items():
            if isinstance(value, list):
                total_concepts += len(value)
            elif isinstance(value, dict):
                total_concepts += len(value)

        metrics["total_concepts"] = total_concepts
        metrics["terms_per_concept"] = (
            len(terms) / total_concepts if total_concepts > 0 else 0
        )

        # Concept diversity - number of different concept types
        concept_types = sum(
            1
            for value in conceptual_structure.values()
            if isinstance(value, (list, dict))
        )
        metrics["concept_types"] = concept_types

        # Structural complexity - nested levels
        def calculate_depth(obj, current_depth=0):
            if isinstance(obj, dict):
                return max(calculate_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                return current_depth + 1
            else:
                return current_depth

        metrics["structural_depth"] = calculate_depth(conceptual_structure)
        metrics["structural_complexity_score"] = (
            concept_types * metrics["structural_depth"]
        )

        return metrics
