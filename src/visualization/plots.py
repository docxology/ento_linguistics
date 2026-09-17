"""Plotting utilities for Ento-Linguistic visualization.

This module provides publication-quality plot implementations for visualizing
terminology distributions, ambiguity metrics, and discourse patterns.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

try:
    from ._style import (
        DOMAIN_PALETTE,
        FALLBACK_COLOR,
        MIN_FONT,
        primary_domain,
        publication_style,
    )
except (ImportError, ValueError):
    from visualization._style import (
        DOMAIN_PALETTE,
        FALLBACK_COLOR,
        MIN_FONT,
        primary_domain,
        publication_style,
    )


__all__ = [
    "plot_line",
    "plot_scatter",
    "plot_bar",
    "plot_heatmap",
    "plot_contour",
    "plot_3d_surface",
    "plot_convergence",
    "plot_comparison",
    "plot_term_frequency",
    "plot_domain_distribution",
    "plot_concept_network",
]


@publication_style
def plot_line(
    x: np.ndarray,
    y: np.ndarray,
    ax: Optional[plt.Axes] = None,
    label: Optional[str] = None,
    color: Optional[str] = None,
    linestyle: str = "-",
    marker: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> plt.Axes:
    """Create a line plot.

    Args:
        x: X values
        y: Y values
        ax: Axes to plot on (creates new if None)
        label: Line label
        color: Line color
        linestyle: Line style
        marker: Marker style
        **kwargs: Additional arguments for plot

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(
        x, y, label=label, color=color, linestyle=linestyle, marker=marker, **kwargs
    )

    if label:
        ax.legend()

    ax.set_xlabel(xlabel if xlabel is not None else "x", fontsize=MIN_FONT)
    ax.set_ylabel(ylabel if ylabel is not None else "y", fontsize=MIN_FONT)

    return ax


@publication_style
def plot_scatter(
    x: np.ndarray,
    y: np.ndarray,
    ax: Optional[plt.Axes] = None,
    color: Optional[str] = None,
    size: Optional[float] = None,
    alpha: float = 0.6,
    label: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> plt.Axes:
    """Create a scatter plot.

    Args:
        x: X values
        y: Y values
        xlabel: X-axis label (default "x")
        ylabel: Y-axis label (default "y")
        ax: Axes to plot on
        color: Point color
        size: Point size
        alpha: Transparency
        label: Plot label
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(x, y, c=color, s=size, alpha=alpha, label=label, **kwargs)

    if label:
        ax.legend()

    ax.set_xlabel(xlabel if xlabel is not None else "x", fontsize=MIN_FONT)
    ax.set_ylabel(ylabel if ylabel is not None else "y", fontsize=MIN_FONT)

    return ax


@publication_style
def plot_bar(
    categories: List[str],
    values: np.ndarray,
    ax: Optional[plt.Axes] = None,
    color: Optional[str] = None,
    width: float = 0.8,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> plt.Axes:
    """Create a bar chart.

    Args:
        categories: Category labels
        values: Bar values
        ax: Axes to plot on
        color: Bar color
        xlabel: X-axis label (default "Category")
        ylabel: Y-axis label (default "Value")
        width: Bar width
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    x_pos = np.arange(len(categories))
    ax.bar(x_pos, values, color=color, width=width, **kwargs)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_xlabel(
        xlabel if xlabel is not None else "Category", fontsize=MIN_FONT
    )
    ax.set_ylabel(ylabel if ylabel is not None else "Value", fontsize=MIN_FONT)

    return ax


@publication_style
def plot_heatmap(
    data: np.ndarray,
    ax: Optional[plt.Axes] = None,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    cmap: str = "viridis",
    colorbar: bool = True,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> plt.Axes:
    """Create a heatmap.

    Args:
        data: 2D data array
        ax: Axes to plot on
        row_labels: Row labels
        col_labels: Column labels
        cmap: Colormap name
        colorbar: Whether to show colorbar
        **kwargs: Additional arguments
        xlabel: X-axis label (default "Column index")
        ylabel: Y-axis label (default "Row index")

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    im = ax.imshow(data, cmap=cmap, aspect="auto", **kwargs)

    if row_labels:
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_yticklabels(row_labels)

    if col_labels:
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha="right")

    if colorbar:
        plt.colorbar(im, ax=ax)

    ax.set_xlabel(
        xlabel if xlabel is not None else "Column index", fontsize=MIN_FONT
    )
    ax.set_ylabel(
        ylabel if ylabel is not None else "Row index", fontsize=MIN_FONT
    )

    return ax


@publication_style
def plot_contour(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    ax: Optional[plt.Axes] = None,
    levels: int = 20,
    cmap: str = "viridis",
    filled: bool = True,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> plt.Axes:
    """Create a contour plot.

    Args:
        x: X coordinates (2D array)
        y: Y coordinates (2D array)
        z: Z values (2D array)
        xlabel: X-axis label (default "x")
        ylabel: Y-axis label (default "y")

        ax: Axes to plot on
        levels: Number of contour levels
        cmap: Colormap name
        filled: Whether to fill contours
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    if filled:
        contour = ax.contourf(x, y, z, levels=levels, cmap=cmap, **kwargs)
        plt.colorbar(contour, ax=ax)
    else:
        contour = ax.contour(x, y, z, levels=levels, cmap=cmap, **kwargs)
        ax.clabel(contour, inline=True, fontsize=MIN_FONT)

    ax.set_xlabel(xlabel if xlabel is not None else "x", fontsize=MIN_FONT)
    ax.set_ylabel(ylabel if ylabel is not None else "y", fontsize=MIN_FONT)

    return ax


@publication_style
def plot_3d_surface(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    ax: Optional[Any] = None,
    cmap: str = "viridis",
    **kwargs,
) -> Any:
    """Create a 3D surface plot.

    Args:
        x: X coordinates (2D array)
        y: Y coordinates (2D array)
        z: Z values (2D array)
        ax: 3D axes (creates new if None)
        cmap: Colormap name
        **kwargs: Additional arguments

    Returns:
        3D axes object
    """

    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(x, y, z, cmap=cmap, **kwargs)
    plt.colorbar(surf, ax=ax, shrink=0.5)
    ax.set_xlabel("x", fontsize=MIN_FONT)
    ax.set_ylabel("y", fontsize=MIN_FONT)
    ax.set_zlabel("z", fontsize=MIN_FONT)

    return ax


@publication_style
def plot_convergence(
    iterations: np.ndarray,
    values: np.ndarray,
    target: Optional[float] = None,
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """Plot convergence curve.

    Args:
        iterations: Iteration numbers
        values: Values at each iteration
        target: Target value (if known)
        ax: Axes to plot on
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(iterations, values, label="Convergence", **kwargs)

    if target is not None:
        ax.axhline(y=target, color="r", linestyle="--", label=f"Target: {target}")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Value")
    ax.set_title("Convergence Analysis")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return ax


@publication_style
def plot_comparison(
    methods: List[str],
    metrics: Dict[str, List[float]],
    metric_name: str,
    ax: Optional[plt.Axes] = None,
    plot_type: str = "bar",
    **kwargs,
) -> plt.Axes:
    """Plot comparison of methods.

    Args:
        methods: List of method names
        metrics: Dictionary of metric values
        metric_name: Metric to plot
        ax: Axes to plot on
        plot_type: Plot type (bar, line)
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    values = metrics.get(metric_name, [])

    if plot_type == "bar":
        plot_bar(methods, np.array(values), ax=ax, **kwargs)
    else:
        x_pos = np.arange(len(methods))
        ax.plot(x_pos, values, marker="o", **kwargs)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(methods, rotation=45, ha="right")

    ax.set_xlabel("Method", fontsize=MIN_FONT)
    ax.set_ylabel(metric_name, fontsize=MIN_FONT)
    ax.set_title(f"Comparison: {metric_name}")
    ax.grid(True, alpha=0.3)

    return ax

@publication_style
def plot_term_frequency(
    terms: Dict[str, Any],
    top_n: int = 20,
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """Plot term frequency distribution.

    Args:
        terms: Dictionary of terms
        top_n: Number of top terms to show
        ax: Axes to plot on
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    # Extract frequencies
    term_freqs = []
    for term_text, term_data in terms.items():
        freq = term_data.frequency if hasattr(term_data, "frequency") else term_data.get("frequency", 0)
        term_freqs.append((term_text, freq))

    # Sort and slice
    term_freqs.sort(key=lambda x: x[1], reverse=True)
    top_terms = term_freqs[:top_n]

    categories = [t[0] for t in top_terms]
    values = np.array([t[1] for t in top_terms])

    return plot_bar(
        categories,
        values,
        ax=ax,
        color=kwargs.get("color", "skyblue"),
        xlabel=kwargs.pop("xlabel", "Term"),
        ylabel=kwargs.pop("ylabel", "Frequency (count)"),
        **kwargs,
    )


@publication_style
def plot_domain_distribution(
    domain_counts: Dict[str, int],
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """Plot domain distribution.

    Args:
        domain_counts: Dictionary of domain counts
        ax: Axes to plot on
        **kwargs: Additional arguments

    Returns:
        Axes object
    """
    categories = list(domain_counts.keys())
    values = np.array(list(domain_counts.values()))

    return plot_bar(
        categories,
        values,
        ax=ax,
        color=kwargs.get("color", "lightgreen"),
        xlabel=kwargs.pop("xlabel", "Domain"),
        ylabel=kwargs.pop("ylabel", "Count"),
        **kwargs,
    )


@publication_style
def plot_concept_network(
    concept_map: Any,
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """Plot concept network using NetworkX spring layout.

    Creates a force-directed network graph from the concept map, colouring
    nodes by their primary domain and sizing them by degree centrality.

    Args:
        concept_map: Concept map object with ``concepts`` and
            ``concept_relationships`` attributes
        ax: Axes to plot on
        **kwargs: Additional arguments (``title`` overrides default title)

    Returns:
        Axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    try:
        import networkx as nx
    except ImportError:
        ax.text(
            0.5, 0.5,
            "Concept Network Visualization\n(Requires networkx)",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=MIN_FONT,
        )
        ax.axis("off")
        return ax

    # Build graph from concept_map
    G = nx.Graph()
    if hasattr(concept_map, "concepts"):
        for concept_name in concept_map.concepts:
            G.add_node(concept_name)
    if hasattr(concept_map, "concept_relationships"):
        for (c1, c2), weight in concept_map.concept_relationships.items():
            G.add_edge(c1, c2, weight=weight)

    if G.number_of_nodes() == 0:
        ax.text(
            0.5, 0.5, "No concepts available",
            ha="center", va="center", transform=ax.transAxes, fontsize=MIN_FONT,
        )
        ax.axis("off")
        return ax

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Colour by primary domain — shared canonical palette
    node_colors = []
    for node in G.nodes():
        color = FALLBACK_COLOR
        if hasattr(concept_map, "concepts") and node in concept_map.concepts:
            concept = concept_map.concepts[node]
            if hasattr(concept, "domains") and concept.domains:
                # Deterministic primary domain: lexicographically smallest,
                # independent of set iteration order and PYTHONHASHSEED.
                domain = primary_domain(concept.domains)
                color = DOMAIN_PALETTE.get(domain, FALLBACK_COLOR)
        node_colors.append(color)

    node_sizes = [max(300, G.degree(n) * 150) for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes, node_color=node_colors,
        alpha=0.85, edgecolors="white", linewidths=1.0, ax=ax,
    )
    edge_weights = [G.edges[e].get("weight", 0.5) for e in G.edges()]
    nx.draw_networkx_edges(
        G, pos, width=[w * 1.5 for w in edge_weights],
        edge_color="gray", alpha=0.5, ax=ax,
    )
    # Label top-degree nodes
    degrees = dict(G.degree())
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:15]
    labels = {n: n.replace("_", " ").title() for n in top_nodes}
    nx.draw_networkx_labels(
        G, pos, labels, font_size=MIN_FONT, font_weight="bold", ax=ax,
    )

    title = kwargs.get("title", "Concept Network")
    ax.set_title(title, fontsize=MIN_FONT + 2, fontweight="bold")
    ax.axis("off")

    return ax
