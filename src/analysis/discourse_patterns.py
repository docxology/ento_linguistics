"""Core discourse pattern data structures and detection for Ento-Linguistic research.

This module provides the foundational data classes and core pattern detection
methods for analyzing how language structures scientific discourse in entomology.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "CITATION_PATTERN",
    "DISCOURSE_MARKERS",
    "ArgumentativeStructure",
    "DiscoursePattern",
    "extract_argumentative_structure",
    "find_citations",
    "identify_patterns_in_text",
]

CITATION_PATTERN = re.compile(r"\(.*?20\d{2}.*?\)")


def find_citations(text: str) -> list[str]:
    """Find parenthetical citations containing a 20xx year.

    Single source of truth for citation matching, shared by
    ``rhetorical_analysis`` (authority strategy) and ``persuasive_analysis``
    (authoritative citations technique).

    Args:
        text: Text to scan

    Returns:
        List of matched citation strings
    """
    return CITATION_PATTERN.findall(text)


@dataclass
class DiscoursePattern:
    """Represents a pattern in scientific discourse.

    Attributes:
        pattern_type: Type of discourse pattern
        examples: Example text instances
        frequency: How often this pattern appears
        domains: Ento-Linguistic domains where this appears
        rhetorical_function: What this pattern accomplishes rhetorically
    """

    pattern_type: str
    examples: list[str] = field(default_factory=list)
    frequency: int = 0
    domains: set[str] = field(default_factory=set)
    rhetorical_function: str = ""

    def add_example(self, example: str) -> None:
        """Add an example of this pattern.

        Args:
            example: Example text
        """
        self.examples.append(example)
        self.frequency = len(self.examples)


@dataclass
class ArgumentativeStructure:
    """Represents argumentative structures in scientific texts.

    Attributes:
        claim: Sentences making the main claim
        evidence: Supporting evidence
        warrant: Sentences connecting claim and evidence
        qualification: Sentences limiting or conditioning the claim
        discourse_markers: Linguistic markers used (deduplicated, first-seen order)
    """

    claim: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    warrant: list[str] = field(default_factory=list)
    qualification: list[str] = field(default_factory=list)
    discourse_markers: list[str] = field(default_factory=list)


# Discourse markers for different rhetorical functions
DISCOURSE_MARKERS = {
    "causation": [
        "because",
        "since",
        "due to",
        "as a result",
        "therefore",
        "thus",
        "consequently",
    ],
    "contrast": [
        "however",
        "although",
        "but",
        "yet",
        "nevertheless",
        "whereas",
        "despite",
    ],
    "evidence": [
        "according to",
        "as shown in",
        "the data indicate",
        "research shows",
        "studies demonstrate",
    ],
    "generalization": [
        "typically",
        "generally",
        "usually",
        "in general",
        "often",
        "frequently",
    ],
    "hedging": [
        "may",
        "might",
        "could",
        "possibly",
        "perhaps",
        "likely",
        "probably",
    ],
    "certainty": [
        "clearly",
        "obviously",
        "definitely",
        "certainly",
        "undoubtedly",
        "evidently",
    ],
}


def identify_patterns_in_text(text: str) -> dict[str, dict[str, Any]]:
    """Identify discourse patterns in a single text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary of patterns found
    """
    patterns = {}

    # Anthropomorphic framing patterns
    anthropomorphic_matches = re.findall(
        r"\b(ants?|colony|queen|workers?)\s+(choose|decide|prefer|select|communicate|cooperate|compete)\b",
        text.lower(),
    )

    if anthropomorphic_matches:
        patterns["anthropomorphic_framing"] = {
            "example": f"Found {len(anthropomorphic_matches)} anthropomorphic constructions",
            "function": "Imposes human-like agency on insect societies",
            "domain": "behavior_and_identity",
        }

    # Hierarchical language patterns
    hierarchy_matches = re.findall(
        r"\b(dominant|subordinate|superior|inferior|control|authority|command)\b",
        text.lower(),
    )

    if hierarchy_matches:
        patterns["hierarchical_framing"] = {
            "example": f"Found {len(hierarchy_matches)} hierarchical terms",
            "function": "Structures social relationships as human-like hierarchies",
            "domain": "power_and_labor",
        }

    # Economic metaphor patterns
    economic_matches = re.findall(r"\b(cost|benefit|trade|exchange|investment|profit|value)\b", text.lower())

    if economic_matches:
        patterns["economic_metaphors"] = {
            "example": f"Found {len(economic_matches)} economic metaphors",
            "function": "Applies market logic to biological processes",
            "domain": "economics",
        }

    # Scale ambiguity patterns
    scale_patterns = re.findall(
        r"\b(individual|colony|population|society|group)\s+(behavior|trait|characteristic|property)\b",
        text.lower(),
    )

    if scale_patterns:
        patterns["scale_ambiguity"] = {
            "example": f"Found {len(scale_patterns)} scale-ambiguous constructions",
            "function": "Creates confusion about biological levels of analysis",
            "domain": "unit_of_individuality",
        }

    return patterns


def extract_argumentative_structure(
    sentences: list[str],
) -> ArgumentativeStructure:
    """Extract argumentative structure from sentences.

    Args:
        sentences: List of sentences

    Returns:
        Argumentative structure
    """
    structure = ArgumentativeStructure()

    # \b-anchored phrase patterns: substring matching would spuriously fire
    # on words like "maybe" (may), "butter" (but) or "sputter" (utter).
    def _contains(sentence_lower: str, phrases: list[str]) -> bool:
        return any(re.search(r"\b" + re.escape(phrase) + r"\b", sentence_lower) for phrase in phrases)

    claim_phrases = ["therefore", "thus", "consequently", "we conclude"]
    evidence_phrases = ["research shows", "studies demonstrate", "data indicate"]
    warrant_phrases = ["because", "since", "due to"]
    qualification_phrases = ["however", "although", "but", "yet"]

    seen_markers = set()

    for sentence in sentences:
        sentence_lower = sentence.lower()

        # Collect each category independently; a sentence may serve several
        # roles, and no role is overwritten by later matches.
        if _contains(sentence_lower, claim_phrases):
            structure.claim.append(sentence.strip())

        if _contains(sentence_lower, evidence_phrases):
            structure.evidence.append(sentence.strip())

        if _contains(sentence_lower, warrant_phrases):
            structure.warrant.append(sentence.strip())

        if _contains(sentence_lower, qualification_phrases):
            structure.qualification.append(sentence.strip())

        # Collect discourse markers, deduplicated in first-seen order
        for markers in DISCOURSE_MARKERS.values():
            for marker in markers:
                if marker in seen_markers:
                    continue
                if _contains(sentence_lower, [marker]):
                    structure.discourse_markers.append(marker)
                    seen_markers.add(marker)

    return structure
