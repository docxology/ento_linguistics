"""Semantic entropy calculation for Ento-Linguistic analysis.

This module implements the core semantic entropy metric H(t) = -sum(p(ci) log2 p(ci)),
which quantifies terminological ambiguity by measuring how a term's usage contexts
distribute across distinct semantic senses (clusters).

High entropy (H > 2.0 bits) indicates a term is used in many distinct senses,
signaling potential for miscommunication in scientific discourse.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields as dataclass_fields
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.stats import entropy as scipy_entropy
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

__all__ = [
    "HIGH_ENTROPY_THRESHOLD",
    "SemanticEntropyResult",
    "calculate_semantic_entropy",
    "calculate_corpus_entropy",
    "get_high_entropy_terms",
]


# Threshold for "high entropy" — corresponds to >4 equiprobable semantic senses
# Calibrated against known polysemous terms in entomological literature
HIGH_ENTROPY_THRESHOLD = 2.0


@dataclass
class SemanticEntropyResult:
    """Result of semantic entropy calculation for a single term.

    Entropy comparability contract
    ------------------------------
    ``entropy_bits`` is the raw Shannon entropy H = -sum(p * log2(p)) over the
    cluster distribution.  Because the number of semantic clusters ``k`` is
    chosen from the number of contexts (see ``calculate_semantic_entropy``),
    the ceiling of H is log2(k), which differs across terms.  Raw H is
    therefore NOT directly comparable across terms with different context
    counts.  Use ``entropy_normalized`` = H / h_max for cross-term comparison:
    it maps to [0, 1] where 1.0 means the contexts are uniformly spread over
    every available sense (maximum ambiguity given k) and 0.0 means a single
    dominant sense.

    Attributes:
        term: The term text
        entropy_bits: Raw Shannon entropy in bits (H = -sum(p * log2(p)))
        n_clusters: Number of distinct semantic clusters found
        cluster_distribution: Probability distribution across clusters
        is_high_entropy: Whether entropy exceeds the HIGH_ENTROPY_THRESHOLD
        n_contexts: Number of contexts used in the calculation
        entropy_normalized: H normalized by its ceiling h_max, in [0, 1].
            Comparable across terms. 0.0 when undefined (fewer than 2
            occupied clusters).
        h_max: Entropy ceiling log2(k_used) in bits for this term's cluster
            count. 0.0 when fewer than 2 clusters were used.
        status: ``"ok"`` when entropy was computed; ``"insufficient_contexts"``
            when fewer usable contexts than ``min_contexts`` (or too few to
            cluster); ``"error"`` when vectorization/clustering failed.
            Downstream consumers MUST exclude non-``"ok"`` results from
            aggregate statistics.
        error: Failure description when ``status == "error"``, else None.
    """

    term: str
    entropy_bits: float
    n_clusters: int
    cluster_distribution: List[float] = field(default_factory=list)
    is_high_entropy: bool = False
    n_contexts: int = 0
    entropy_normalized: float = 0.0
    h_max: float = 0.0
    status: str = "ok"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "term": self.term,
            "entropy_bits": self.entropy_bits,
            "n_clusters": self.n_clusters,
            "cluster_distribution": self.cluster_distribution,
            "is_high_entropy": self.is_high_entropy,
            "n_contexts": self.n_contexts,
            "entropy_normalized": self.entropy_normalized,
            "h_max": self.h_max,
            "status": self.status,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticEntropyResult":
        """Create from dictionary.

        Tolerates serialized payloads that predate the normalized-entropy
        fields; missing keys fall back to dataclass defaults.
        """
        known = {f.name for f in dataclass_fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


def calculate_semantic_entropy(
    term: str,
    contexts: List[str],
    max_clusters: int = 5,
    min_contexts: int = 5,
    random_state: int = 42,
    threshold: float = HIGH_ENTROPY_THRESHOLD,
) -> SemanticEntropyResult:
    """Calculate semantic entropy for a term given its usage contexts.

    The algorithm:
    1. Vectorizes contexts using TF-IDF
    2. Clusters context vectors using KMeans to identify distinct semantic senses
    3. Computes Shannon entropy of the cluster distribution

    Args:
        term: The term to analyze
        contexts: List of textual contexts where the term appears
        max_clusters: Maximum number of semantic sense clusters
        min_contexts: Minimum contexts required for meaningful analysis
        random_state: Random seed for deterministic clustering
        threshold: Entropy threshold for is_high_entropy flag

    Returns:
        SemanticEntropyResult with entropy and cluster information
    """
    # Filter to meaningful contexts (at least 3 words)
    valid_contexts = [c.strip() for c in contexts if len(c.strip().split()) >= 3]

    if len(valid_contexts) < min_contexts:
        return SemanticEntropyResult(
            term=term,
            entropy_bits=0.0,
            n_clusters=1 if valid_contexts else 0,
            cluster_distribution=[1.0] if valid_contexts else [],
            is_high_entropy=False,
            n_contexts=len(valid_contexts),
            status="insufficient_contexts",
        )

    try:
        # Step 1: Vectorize contexts using TF-IDF
        vectorizer = TfidfVectorizer(
            stop_words="english",
            min_df=1,
            max_features=1000,
        )
        X = vectorizer.fit_transform(valid_contexts)

        # Step 2: Cluster to find distinct semantic senses.
        # k must be strictly less than n to avoid the degenerate case
        # where every context lands in its own cluster (uniform p_i = 1/k,
        # H = log2(k) for all terms regardless of actual semantic spread).
        # Using sqrt(n) as a data-driven upper bound stabilizes small-n
        # cases while still allowing finer discrimination on large corpora.
        n = len(valid_contexts)
        k_upper = min(max_clusters, n - 1, max(2, int(np.sqrt(n))))
        n_clusters = max(2, k_upper)
        if n_clusters < 2 or n < 3:
            return SemanticEntropyResult(
                term=term,
                entropy_bits=0.0,
                n_clusters=1,
                cluster_distribution=[1.0],
                is_high_entropy=False,
                n_contexts=len(valid_contexts),
                status="insufficient_contexts",
            )

        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        )
        labels = kmeans.fit_predict(X)

        # Step 3: Calculate cluster distribution
        unique_labels, counts = np.unique(labels, return_counts=True)
        probabilities = counts / len(labels)

        # Step 4: Shannon entropy in bits (base 2), plus its ceiling so the
        # normalized value is comparable across terms with different k
        # (see SemanticEntropyResult docstring).
        H = float(scipy_entropy(probabilities, base=2))
        k_used = len(unique_labels)
        h_max = float(np.log2(k_used)) if k_used > 1 else 0.0
        entropy_normalized = H / h_max if h_max > 0 else 0.0

        return SemanticEntropyResult(
            term=term,
            entropy_bits=H,
            n_clusters=k_used,
            cluster_distribution=probabilities.tolist(),
            is_high_entropy=H > threshold,
            n_contexts=len(valid_contexts),
            entropy_normalized=entropy_normalized,
            h_max=h_max,
        )

    except (ValueError, RuntimeError) as e:
        # Specific exceptions for vectorization/clustering failures (e.g. empty vocabulary,
        # singular matrices in small context sets). KMeans instability on tiny datasets is
        # expected; fallback gracefully without masking other errors.
        # TODO: unify with core.logging.get_logger once logging is standardized
        import logging
        logging.getLogger(__name__).warning(
            "Semantic entropy calculation failed for term '%s' (%d contexts): %s. "
            "Returning zero entropy fallback.",
            term, len(valid_contexts), str(e)
        )
        return SemanticEntropyResult(
            term=term,
            entropy_bits=0.0,
            n_clusters=0,
            cluster_distribution=[],
            is_high_entropy=False,
            n_contexts=len(valid_contexts),
            status="error",
            error=str(e),
        )


def calculate_corpus_entropy(
    terms_contexts: Dict[str, List[str]],
    max_clusters: int = 5,
    min_contexts: int = 5,
    random_state: int = 42,
    threshold: float = HIGH_ENTROPY_THRESHOLD,
) -> Dict[str, SemanticEntropyResult]:
    """Calculate semantic entropy for all terms in a corpus.

    Args:
        terms_contexts: Dictionary mapping term text to list of contexts
        max_clusters: Maximum clusters per term
        min_contexts: Minimum contexts for analysis
        random_state: Random seed for determinism
        threshold: Entropy threshold

    Returns:
        Dictionary mapping term text to SemanticEntropyResult
    """
    results = {}
    for term, contexts in terms_contexts.items():
        results[term] = calculate_semantic_entropy(
            term=term,
            contexts=contexts,
            max_clusters=max_clusters,
            min_contexts=min_contexts,
            random_state=random_state,
            threshold=threshold,
        )
    return results


def get_high_entropy_terms(
    results: Dict[str, SemanticEntropyResult],
) -> List[SemanticEntropyResult]:
    """Filter to only high-entropy (ambiguous) terms.

    Args:
        results: Dictionary of entropy results

    Returns:
        List of high-entropy results, sorted by entropy descending
    """
    high = [r for r in results.values() if r.is_high_entropy]
    return sorted(high, key=lambda r: r.entropy_bits, reverse=True)
