"""Rhetorical analysis for Ento-Linguistic research.

This module provides methods for analyzing rhetorical strategies, narrative
frameworks, and argumentative structure scoring in entomological literature.

HEURISTIC SCORING NOTICE: all index/rating outputs of this module are simple
lexical heuristics (fixed offsets such as /10, /20, base 0.5).  They are raw
indices intended for ranking and comparison, NOT validated measures of
effectiveness or confidence, and must not be reported as such.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from .discourse_patterns import find_citations

__all__ = [
    "analyze_rhetorical_strategies",
    "identify_narrative_frameworks",
    "quantify_rhetorical_patterns",
    "score_argumentative_structures",
    "analyze_narrative_frequency",
]


def analyze_rhetorical_strategies(texts: List[str]) -> Dict[str, Dict[str, Any]]:
    """Analyze rhetorical strategies used in texts.

    Args:
        texts: Texts to analyze

    Returns:
        Dictionary of rhetorical strategy analysis.  Each entry records
        ``frequency`` (total matches), ``examples`` (capped) and
        ``text_count`` (number of distinct texts containing the pattern).
    """
    strategies = {
        "authority": {"frequency": 0, "examples": [], "text_count": 0},
        "analogy": {"frequency": 0, "examples": [], "text_count": 0},
        "generalization": {"frequency": 0, "examples": [], "text_count": 0},
        "anecdotal": {"frequency": 0, "examples": [], "text_count": 0},
    }

    for text in texts:
        # Authority citations (shared citation matcher; see persuasive_analysis)
        citations = find_citations(text)
        strategies["authority"]["frequency"] += len(citations)
        if citations:
            strategies["authority"]["examples"].extend(citations[:2])
            strategies["authority"]["text_count"] += 1

        # Analogies
        analogies = re.findall(r"\blike\s+.*?\bant|ant.*?\blike\s+", text.lower())
        strategies["analogy"]["frequency"] += len(analogies)
        if analogies:
            strategies["analogy"]["examples"].extend(analogies[:2])
            strategies["analogy"]["text_count"] += 1

        # Generalizations
        generalizations = re.findall(
            r"\b(all|every|always|never)\s+.*?\bant", text.lower()
        )
        strategies["generalization"]["frequency"] += len(generalizations)
        if generalizations:
            strategies["generalization"]["examples"].extend(generalizations[:2])
            strategies["generalization"]["text_count"] += 1

        # Anecdotal evidence
        anecdotal = re.findall(
            r"\b(for\s+example|such\s+as|consider|imagine)\b", text.lower()
        )
        strategies["anecdotal"]["frequency"] += len(anecdotal)
        if anecdotal:
            strategies["anecdotal"]["examples"].extend(anecdotal[:2])
            strategies["anecdotal"]["text_count"] += 1

    return strategies


def identify_narrative_frameworks(texts: List[str]) -> Dict[str, List[str]]:
    """Identify narrative frameworks used in texts.

    Args:
        texts: Texts to analyze

    Returns:
        Dictionary of narrative frameworks and examples
    """
    frameworks = {
        "progress_narrative": [],
        "conflict_narrative": [],
        "discovery_narrative": [],
        "complexity_narrative": [],
    }

    for text in texts:
        text_lower = text.lower()

        # Progress narratives (advancement, improvement)
        if any(
            word in text_lower
            for word in ["advance", "improvement", "progress", "development"]
        ):
            frameworks["progress_narrative"].append(text[:100] + "...")

        # Conflict narratives (struggle, adaptation)
        if any(
            word in text_lower
            for word in ["struggle", "adaptation", "conflict", "competition"]
        ):
            frameworks["conflict_narrative"].append(text[:100] + "...")

        # Discovery narratives (finding, revealing)
        if any(
            word in text_lower for word in ["discover", "reveal", "find", "uncover"]
        ):
            frameworks["discovery_narrative"].append(text[:100] + "...")

        # Complexity narratives (complex, sophisticated)
        if any(
            word in text_lower
            for word in ["complex", "sophisticated", "intricate", "elaborate"]
        ):
            frameworks["complexity_narrative"].append(text[:100] + "...")

    return frameworks


def quantify_rhetorical_patterns(texts: List[str]) -> Dict[str, Dict[str, Any]]:
    """Quantify rhetorical patterns with frequency metrics.

    ``text_coverage`` is the fraction of input texts in which the pattern
    occurs at least once (distinct-text coverage, not example counts, which
    are capped per text and would saturate).  The ``heuristic_*`` outputs are
    simple lexical indices — see the module heuristic-scoring notice.

    Args:
        texts: Texts to analyze

    Returns:
        Dictionary of quantified rhetorical patterns
    """
    patterns = analyze_rhetorical_strategies(texts)
    quantified_patterns = {}

    for pattern_name, pattern_data in patterns.items():
        # Calculate frequency metrics
        freq_data = pattern_data.get("frequency", 0)
        if isinstance(freq_data, dict):
            total_occurrences = sum(freq_data.values())
        else:
            total_occurrences = freq_data
        text_coverage = (
            pattern_data.get("text_count", 0) / len(texts) if texts else 0
        )

        # Occurrences-per-text index (heuristic, capped at 1)
        heuristic_frequency_index = (
            min(total_occurrences / len(texts), 1.0) if texts else 0
        )

        quantified_patterns[pattern_name] = {
            "total_occurrences": total_occurrences,
            "text_coverage": text_coverage,
            "heuristic_frequency_index": heuristic_frequency_index,
            "frequency_distribution": pattern_data.get("frequency", {}),
            "context_examples": pattern_data.get("examples", [])[
                :5
            ],  # Limit examples
            "heuristic_persuasiveness_index": _calculate_persuasiveness(
                pattern_data
            ),
        }

    return quantified_patterns


def score_argumentative_structures(
    structures: list, texts: List[str]
) -> Dict[str, Dict[str, Any]]:
    """Score argumentative structures for strength and coherence.

    All returned indices are simple lexical heuristics (see the module
    heuristic-scoring notice), not validated strength or confidence measures.

    Args:
        structures: List of ArgumentativeStructure objects (claim/warrant/
            qualification are lists of sentences)
        texts: Source texts (for context)

    Returns:
        Dictionary of scored argumentative structures
    """
    scored_structures = {}

    for structure in structures:
        # Mean heuristic strength over all collected claims/warrants; a
        # structure with no claims/warrants scores 0 for that component
        claim_strength = (
            sum(_evaluate_claim_strength(c) for c in structure.claim)
            / len(structure.claim)
            if structure.claim
            else 0.0
        )
        evidence_quality = _evaluate_evidence_quality(structure.evidence)
        reasoning_coherence = (
            sum(_evaluate_reasoning_coherence(w) for w in structure.warrant)
            / len(structure.warrant)
            if structure.warrant
            else 0.0
        )

        overall_strength = (
            claim_strength + evidence_quality + reasoning_coherence
        ) / 3

        scored_structures[f"structure_{len(scored_structures)}"] = {
            "claim": structure.claim,
            "evidence": structure.evidence,
            "warrant": structure.warrant,
            "claim_strength": claim_strength,
            "evidence_quality": evidence_quality,
            "reasoning_coherence": reasoning_coherence,
            "overall_strength": overall_strength,
            "qualification": structure.qualification,
            "heuristic_confidence_index": _calculate_structure_confidence(
                structure
            ),
        }

    return scored_structures


def analyze_narrative_frequency(texts: List[str]) -> Dict[str, Dict[str, Any]]:
    """Analyze frequency and distribution of narrative frameworks.

    Args:
        texts: Texts to analyze

    Returns:
        Dictionary of narrative framework frequencies
    """
    frameworks = identify_narrative_frameworks(texts)
    framework_analysis = {}

    total_texts = len(texts)

    for framework_type, framework_texts in frameworks.items():
        frequency = len(framework_texts)
        coverage = frequency / total_texts if total_texts > 0 else 0

        # Analyze framework characteristics
        avg_length = (
            sum(len(text.split()) for text in framework_texts) / frequency
            if frequency > 0
            else 0
        )
        unique_phrases = set()
        for text in framework_texts:
            words = text.lower().split()
            for i in range(len(words) - 1):
                unique_phrases.add(f"{words[i]} {words[i+1]}")

        framework_analysis[framework_type] = {
            "frequency": frequency,
            "coverage_percentage": coverage * 100,
            "average_text_length": avg_length,
            "unique_phrase_count": len(unique_phrases),
            "examples": framework_texts[:3],  # Limit examples
            "heuristic_consistency_index": _calculate_framework_consistency(
                framework_texts
            ),
        }

    return framework_analysis


# --- Helper functions ---


def _calculate_persuasiveness(pattern_data: Dict[str, Any]) -> float:
    """Heuristic persuasiveness index: (frequency + capped examples) / 10.

    Simple lexical heuristic — see the module heuristic-scoring notice.
    """
    freq_data = pattern_data.get("frequency", 0)
    if isinstance(freq_data, dict):
        frequency = sum(freq_data.values())
    else:
        frequency = freq_data
    example_count = len(pattern_data.get("examples", []))
    return min((frequency + example_count) / 10, 1.0)


def _evaluate_claim_strength(claim: str) -> float:
    """Heuristic claim-strength index (base 0.5 plus lexical bonuses)."""
    score = 0.5  # Base score

    if len(claim.split()) > 5:  # Substantial claims
        score += 0.2
    if "?" not in claim:  # Declarative rather than interrogative
        score += 0.1
    if any(
        word in claim.lower() for word in ["therefore", "thus", "hence"]
    ):  # Logical connectors
        score += 0.2

    return min(score, 1.0)


def _evaluate_evidence_quality(evidence: List[str]) -> float:
    """Heuristic evidence-quality index (base 0.5 plus lexical bonuses)."""
    if not evidence:
        return 0.0

    total_quality = 0
    for ev in evidence:
        quality = 0.5  # Base quality
        if len(ev.split()) > 10:  # Substantial evidence
            quality += 0.2
        if any(
            word in ev.lower()
            for word in ["data", "study", "research", "observation"]
        ):
            quality += 0.3
        total_quality += quality

    return min(total_quality / len(evidence), 1.0)


def _evaluate_reasoning_coherence(reasoning: str) -> float:
    """Heuristic reasoning-coherence index (base 0.3 plus connector bonus)."""
    coherence_indicators = [
        "because",
        "therefore",
        "thus",
        "hence",
        "consequently",
        "accordingly",
    ]
    connector_count = sum(
        1 for indicator in coherence_indicators if indicator in reasoning.lower()
    )

    base_coherence = 0.3
    coherence_bonus = min(connector_count * 0.1, 0.7)

    return min(base_coherence + coherence_bonus, 1.0)


def _calculate_structure_confidence(structure) -> float:
    """Heuristic structure index (base 0.5 plus presence bonuses).

    NOT a statistical confidence.  ``claim``/``warrant`` are lists of
    sentences; the first sentence of each is measured.
    """
    confidence = 0.5

    if structure.claim and len(structure.claim[0].split()) > 3:
        confidence += 0.2
    if structure.evidence:
        confidence += 0.2
    if structure.warrant and len(structure.warrant[0].split()) > 5:
        confidence += 0.1

    return min(confidence, 1.0)


def _calculate_framework_consistency(framework_texts: List[str]) -> float:
    """Heuristic framework-consistency index from length variance."""
    if len(framework_texts) < 2:
        return 1.0

    # Simple consistency based on text similarity
    avg_length = sum(len(text.split()) for text in framework_texts) / len(
        framework_texts
    )
    length_variance = sum(
        (len(text.split()) - avg_length) ** 2 for text in framework_texts
    ) / len(framework_texts)

    # Lower variance = higher consistency
    consistency = max(0, 1.0 - (length_variance / (avg_length**2)))

    return consistency
