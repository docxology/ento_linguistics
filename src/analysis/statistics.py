"""Statistical analysis for Ento-Linguistic research.

This module provides statistical tools for analyzing term frequencies,
ambiguity distributions, and cross-domain significance in scientific discourse.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy.stats import t as t_dist, f as f_dist

__all__ = [
    "DescriptiveStats",
    "calculate_descriptive_stats",
    "t_test",
    "calculate_correlation",
    "calculate_confidence_interval",
    "fit_distribution",
    "anova_test",
    "benjamini_hochberg_correction",
]


@dataclass
class DescriptiveStats:
    """Descriptive statistics for a dataset."""

    mean: float
    std: float
    median: float
    min: float
    max: float
    q25: float  # First quartile
    q75: float  # Third quartile
    count: int

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "mean": self.mean,
            "std": self.std,
            "median": self.median,
            "min": self.min,
            "max": self.max,
            "q25": self.q25,
            "q75": self.q75,
            "count": self.count,
        }


def calculate_descriptive_stats(data: np.ndarray) -> DescriptiveStats:
    """Calculate descriptive statistics.

    Args:
        data: Input data array (must contain at least one element)

    Returns:
        DescriptiveStats object

    Raises:
        ValueError: If data is empty after flattening
    """
    data_flat = data.flatten()
    if len(data_flat) == 0:
        raise ValueError("Cannot compute descriptive statistics on empty array")

    return DescriptiveStats(
        mean=float(np.mean(data_flat)),
        std=float(np.std(data_flat, ddof=1)) if len(data_flat) > 1 else 0.0,
        median=float(np.median(data_flat)),
        min=float(np.min(data_flat)),
        max=float(np.max(data_flat)),
        q25=float(np.percentile(data_flat, 25)),
        q75=float(np.percentile(data_flat, 75)),
        count=int(len(data_flat)),
    )


def t_test(
    sample1: np.ndarray,
    sample2: Optional[np.ndarray] = None,
    mu: Optional[float] = None,
    alternative: str = "two-sided",
) -> Dict[str, float]:
    """Perform t-test.

    Args:
        sample1: First sample
        sample2: Second sample (for two-sample test) or None (for one-sample)
        mu: Population mean (for one-sample test)
        alternative: Alternative hypothesis (two-sided, greater, less)

    Returns:
        Dictionary with t-statistic, p-value, and degrees of freedom
    """
    if sample2 is None:
        # One-sample t-test
        if mu is None:
            mu = 0.0

        n = len(sample1)
        mean = np.mean(sample1)
        std = np.std(sample1, ddof=1)
        # Guard: zero std means all values identical → t is 0 when mean==mu
        if std == 0:
            t_stat = 0.0 if np.isclose(mean, mu) else np.inf * np.sign(mean - mu)
        else:
            t_stat = (mean - mu) / (std / np.sqrt(n))
        df = n - 1
    else:
        # Two-sample t-test
        n1, n2 = len(sample1), len(sample2)
        mean1, mean2 = np.mean(sample1), np.mean(sample2)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            var1 = np.var(sample1, ddof=1) if n1 > 1 else 0.0
            var2 = np.var(sample2, ddof=1) if n2 > 1 else 0.0

        # Pooled standard error
        pooled_std = np.sqrt((var1 / n1) + (var2 / n2))
        # Guard: zero pooled_std means both groups have zero variance
        if pooled_std == 0:
            t_stat = 0.0 if np.isclose(mean1, mean2) else np.inf * np.sign(mean1 - mean2)
        else:
            t_stat = (mean1 - mean2) / pooled_std

        # Degrees of freedom (Welch's approximation)
        # Guard: n=1 causes division by zero in Welch-Satterthwaite df
        denom1 = (var1 / n1) ** 2 / (n1 - 1) if n1 > 1 else 0.0
        denom2 = (var2 / n2) ** 2 / (n2 - 1) if n2 > 1 else 0.0
        denom = denom1 + denom2
        if denom == 0:
            df = max(n1 - 1, 1) + max(n2 - 1, 1)
        else:
            df = ((var1 / n1 + var2 / n2) ** 2) / denom

    # Calculate p-value using scipy t-distribution
    if alternative == "two-sided":
        p_value = float(t_dist.sf(abs(t_stat), df) * 2)
    elif alternative == "greater":
        p_value = float(t_dist.sf(t_stat, df))
    elif alternative == "less":
        p_value = float(t_dist.cdf(t_stat, df))
    else:
        p_value = float(t_dist.sf(abs(t_stat), df) * 2)

    return {
        "t_statistic": float(t_stat),
        "p_value": p_value,
        "degrees_of_freedom": float(df),
        "alternative": alternative,
    }


def calculate_correlation(
    x: np.ndarray, y: np.ndarray, method: str = "pearson"
) -> Dict[str, float]:
    """Calculate correlation between two variables.

    Args:
        x: First variable
        y: Second variable
        method: Correlation method (pearson, spearman)

    Returns:
        Dictionary with correlation coefficient and p-value
    """
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    if method == "pearson":
        # Pearson correlation with guard for constant inputs (which produce NaN)
        if np.std(x) == 0 or np.std(y) == 0:
            correlation = 0.0  # No variation = no correlation
        else:
            correlation = np.corrcoef(x, y)[0, 1]
    elif method == "spearman":
        # Spearman rank correlation
        from scipy.stats import spearmanr

        correlation, p_value = spearmanr(x, y)
        return {
            "correlation": float(correlation),
            "p_value": float(p_value),
            "method": method,
        }
    else:
        raise ValueError(f"Unknown method: {method}")

    # Compute p-value for Pearson correlation via t-distribution
    n = len(x)
    if abs(correlation) >= 1.0:
        p_value = 0.0
    else:
        t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2))
        p_value = float(t_dist.sf(abs(t_stat), n - 2) * 2)

    return {"correlation": float(correlation), "p_value": p_value, "method": method}


def calculate_confidence_interval(
    data: np.ndarray, confidence: float = 0.95
) -> Tuple[float, float]:
    """Calculate confidence interval for mean.

    Args:
        data: Input data (must contain at least 2 elements)
        confidence: Confidence level (0.95 for 95%)

    Returns:
        Tuple of (lower_bound, upper_bound)

    Raises:
        ValueError: If data has fewer than 2 elements (t-distribution requires df >= 1)
    """
    n = len(data)
    if n < 2:
        raise ValueError(
            f"Confidence interval requires at least 2 data points, got {n}"
        )
    mean = np.mean(data)
    std = np.std(data, ddof=1)

    alpha = 1 - confidence
    t_value = float(t_dist.ppf(1 - alpha / 2, df=n - 1))

    margin = t_value * (std / np.sqrt(n))

    return (float(mean - margin), float(mean + margin))


def fit_distribution(data: np.ndarray, distribution: str = "normal") -> Dict[str, Any]:
    """Fit a distribution to data.

    Args:
        data: Input data
        distribution: Distribution type to fit

    Returns:
        Dictionary with fitted parameters
    """
    if distribution == "normal":
        return {
            "distribution": "normal",
            "mean": float(np.mean(data)),
            "std": float(np.std(data, ddof=1)),
        }
    elif distribution == "exponential":
        mean = float(np.mean(data))
        if mean <= 0:
            raise ValueError(
                "Exponential distribution requires strictly positive mean"
            )
        return {
            "distribution": "exponential",
            "scale": mean,
            "lambda": 1.0 / mean,
        }
    elif distribution == "uniform":
        return {
            "distribution": "uniform",
            "min": float(np.min(data)),
            "max": float(np.max(data)),
        }
    else:
        raise ValueError(f"Unknown distribution: {distribution}")


def benjamini_hochberg_correction(
    p_values: List[float],
    q: float = 0.05,
) -> Dict[str, Any]:
    """Apply Benjamini-Hochberg false discovery rate correction.

    Controls the expected proportion of false discoveries (FDR) at level q
    among the rejected hypotheses. Produces adjusted p-values and a Boolean
    rejection mask.

    Args:
        p_values: List of raw p-values (one per hypothesis test)
        q: FDR threshold (default 0.05)

    Returns:
        Dictionary with keys:
            - adjusted_p_values: BH-adjusted p-values (list, same order as input)
            - rejected: Boolean list — True where null hypothesis is rejected
            - n_rejected: Count of rejected hypotheses
            - alpha_threshold: The largest raw p-value that passed the BH criterion
    """
    m = len(p_values)
    if m == 0:
        return {
            "adjusted_p_values": [],
            "rejected": [],
            "n_rejected": 0,
            "alpha_threshold": 0.0,
        }

    # Rank p-values (1-indexed, ascending)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    rejected = [False] * m

    # Step-up BH procedure: adjusted p_i = min(1, p_i * m / i)
    # computed from largest rank downward to ensure monotonicity
    running_min = 1.0
    for rank in range(m, 0, -1):
        orig_idx, raw_p = indexed[rank - 1]
        adj = min(1.0, raw_p * m / rank)
        running_min = min(running_min, adj)
        adjusted[orig_idx] = running_min

    # Reject where adjusted p-value <= q
    alpha_threshold = 0.0
    for orig_idx, raw_p in indexed:
        if adjusted[orig_idx] <= q:
            rejected[orig_idx] = True
            alpha_threshold = max(alpha_threshold, raw_p)

    return {
        "adjusted_p_values": adjusted,
        "rejected": rejected,
        "n_rejected": sum(rejected),
        "alpha_threshold": float(alpha_threshold),
    }


def anova_test(groups: List[np.ndarray]) -> Dict[str, float]:
    """Perform one-way ANOVA test.

    Args:
        groups: List of arrays, one per group

    Returns:
        Dictionary with F-statistic and p-value
    """
    # Calculate group means and overall mean
    group_means = [np.mean(g) for g in groups]
    group_sizes = [len(g) for g in groups]
    overall_mean = np.mean(np.concatenate(groups))

    # Between-group sum of squares
    ss_between = sum(
        n * (mean - overall_mean) ** 2 for n, mean in zip(group_sizes, group_means)
    )
    df_between = len(groups) - 1

    # Within-group sum of squares
    ss_within = sum(np.sum((g - mean) ** 2) for g, mean in zip(groups, group_means))
    df_within = sum(group_sizes) - len(groups)

    # F-statistic
    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_within = ss_within / df_within if df_within > 0 else 0
    f_stat = ms_between / ms_within if ms_within > 0 else 0

    # Compute p-value using scipy F-distribution
    if f_stat > 0 and df_between > 0 and df_within > 0:
        p_value = float(f_dist.sf(f_stat, df_between, df_within))
    else:
        p_value = 1.0

    return {
        "f_statistic": float(f_stat),
        "p_value": p_value,
        "df_between": float(df_between),
        "df_within": float(df_within),
    }
