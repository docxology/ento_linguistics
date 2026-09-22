"""Statistical visualization module for Ento-Linguistic analysis.

This module provides specialized visualizations for statistical analysis results,
including significance testing, correlation matrices, distribution comparisons,
effect sizes, and confidence intervals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

try:
    from .concept_visualization import ConceptVisualizer
except ImportError:
    from concept_visualization import ConceptVisualizer

try:
    from ._style import (
        CANONICAL_DOMAINS,
        DOMAIN_PALETTE,
        FALLBACK_COLOR,
        MIN_FONT,
        publication_style,
        save_and_verify,
    )
except (ImportError, ValueError):
    from visualization._style import (
        CANONICAL_DOMAINS,
        DOMAIN_PALETTE,
        FALLBACK_COLOR,
        MIN_FONT,
        publication_style,
        save_and_verify,
    )

__all__ = [
    "StatisticalVisualizer",
    "plot_statistical_analysis",
    "plot_layer_comparison",
    "plot_discourse_comparison",
]


class StatisticalVisualizer(ConceptVisualizer):
    """Visualizer for statistical analysis results.

    This class provides methods for visualizing statistical test results,
    correlations, distributions, and other quantitative analyses.
    """

    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """Initialize statistical visualizer.

        Args:
            figsize: Default figure size for plots
        """
        super().__init__(figsize)
        # Colorblind-safe significance palette (Okabe-Ito): vermillion for
        # significant, orange for marginal, blue for not significant.
        self.significance_colors = {
            "significant": "#D55E00",  # Vermillion
            "marginally_significant": "#E69F00",  # Orange
            "not_significant": "#0072B2",  # Blue
        }

    @publication_style
    def visualize_statistical_significance(
        self,
        significance_results: Dict[str, Any],
        filepath: Optional[Path] = None,
        title: str = "Statistical Significance Analysis",
    ) -> plt.Figure:
        """Visualize statistical significance test results.

        Args:
            significance_results: Results from statistical significance testing
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # P-value visualization
        if "p_value" in significance_results:
            p_val = significance_results["p_value"]
            threshold = significance_results.get("significance_threshold", 0.05)

            # P-value bar chart
            ax1.bar(
                ["P-Value", "Threshold"],
                [p_val, threshold],
                color=["skyblue", "red"],
                alpha=0.7,
                edgecolor="black",
            )
            ax1.axhline(
                y=threshold,
                color="red",
                linestyle="--",
                alpha=0.7,
                label=f"α = {threshold}",
            )
            ax1.set_ylabel("Value", fontsize=MIN_FONT)
            ax1.set_title("P-Value vs Significance Threshold", fontsize=MIN_FONT + 2, fontweight="bold")
            ax1.legend(fontsize=MIN_FONT)
            ax1.grid(True, alpha=0.3)

            # Significance status
            is_significant = p_val < threshold
            status_color = (
                self.significance_colors["significant"]
                if is_significant
                else self.significance_colors["not_significant"]
            )
            status_text = "SIGNIFICANT" if is_significant else "NOT SIGNIFICANT"

            ax1.text(
                0.5,
                max(p_val, threshold) * 0.8,
                status_text,
                ha="center",
                va="center",
                fontsize=MIN_FONT,
                fontweight="bold",
                color=status_color,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

        # Chi-square statistic
        if "chi_square_statistic" in significance_results:
            chi_sq = significance_results["chi_square_statistic"]
            effect_size = significance_results.get("effect_size", 0)

            ax2.bar(
                ["Chi-Square", "Effect Size"],
                [chi_sq, effect_size],
                color=["orange", "purple"],
                alpha=0.7,
                edgecolor="black",
            )
            ax2.set_ylabel("Value", fontsize=MIN_FONT)
            ax2.set_title("Test Statistics", fontsize=MIN_FONT + 2, fontweight="bold")
            ax2.grid(True, alpha=0.3)

        # Significant patterns
        if "significant_patterns" in significance_results:
            patterns = significance_results["significant_patterns"]
            if patterns:
                ax3.bar(range(len(patterns)), [1] * len(patterns))
                ax3.set_xticks(range(len(patterns)))
                ax3.set_xticklabels(patterns, rotation=45, ha="right")
                ax3.set_ylabel("Significance", fontsize=MIN_FONT)
                ax3.set_title("Significant Patterns", fontsize=MIN_FONT + 2, fontweight="bold")
                ax3.grid(True, alpha=0.3)
            else:
                ax3.text(
                    0.5,
                    0.5,
                    "No Significant Patterns Found",
                    transform=ax3.transAxes,
                    ha="center",
                    va="center",
                    fontsize=MIN_FONT,
                    style="italic",
                )
                ax3.set_title("Significant Patterns", fontsize=MIN_FONT + 2, fontweight="bold")
                ax3.axis("off")

        # Effect size interpretation
        if "effect_size" in significance_results:
            effect_size = significance_results["effect_size"]

            # Effect size categories
            categories = ["Negligible", "Small", "Medium", "Large"]
            thresholds = [0.1, 0.3, 0.5, float("inf")]
            category_colors = ["#BBBBBB", "#56B4E9", "#E69F00", "#D55E00"]

            # Determine category
            category_idx = 0
            for i, threshold in enumerate(thresholds):
                if effect_size <= threshold:
                    category_idx = i
                    break

            ax4.bar(
                ["Effect Size"],
                [effect_size],
                color=category_colors[category_idx],
                alpha=0.7,
                edgecolor="black",
                width=0.5,
            )
            ax4.axhline(
                y=thresholds[category_idx],
                color=category_colors[category_idx],
                linestyle="--",
                alpha=0.7,
                label=categories[category_idx],
            )
            ax4.set_ylabel("Effect Size", fontsize=MIN_FONT)
            ax4.set_title("Effect Size Magnitude", fontsize=MIN_FONT + 2, fontweight="bold")
            ax4.legend(fontsize=MIN_FONT)
            ax4.grid(True, alpha=0.3)

            # Add interpretation text
            ax4.text(
                0,
                effect_size * 0.5,
                f"{categories[category_idx]}\n({effect_size:.3f})",
                ha="center",
                va="center",
                fontsize=MIN_FONT,
                fontweight="bold",
            )

        plt.suptitle(title, fontsize=MIN_FONT + 4, fontweight="bold")
        plt.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @publication_style
    def create_correlation_matrix_plot(
        self,
        correlation_data: Dict[str, Dict[str, float]],
        filepath: Optional[Path] = None,
        title: str = "Correlation Matrix",
    ) -> plt.Figure:
        """Create a correlation matrix heatmap visualization.

        Args:
            correlation_data: Dictionary of correlation coefficients
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Extract variable names and correlation matrix
        variables = list(correlation_data.keys())
        n_vars = len(variables)

        # Create correlation matrix
        corr_matrix = np.zeros((n_vars, n_vars))

        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i == j:
                    corr_matrix[i, j] = 1.0  # Perfect correlation with self
                else:
                    corr_matrix[i, j] = correlation_data[var1].get(var2, 0)

        # Create heatmap
        im = ax.imshow(corr_matrix, cmap="RdYlBu_r", aspect="equal", vmin=-1, vmax=1)

        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Correlation Coefficient", rotation=-90, va="bottom")

        # Add labels
        ax.set_xticks(range(n_vars))
        ax.set_yticks(range(n_vars))
        ax.set_xticklabels(variables, rotation=45, ha="right")
        ax.set_yticklabels(variables)

        # Add correlation values as text
        for i in range(n_vars):
            for j in range(n_vars):
                ax.text(
                    j,
                    i,
                    f"{corr_matrix[i, j]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=MIN_FONT,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
                )

        ax.set_title(title, fontsize=MIN_FONT + 4, fontweight="bold")
        plt.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @publication_style
    def visualize_distribution_comparison(
        self,
        distribution_data: Dict[str, List[float]],
        filepath: Optional[Path] = None,
        title: str = "Distribution Comparison",
    ) -> plt.Figure:
        """Visualize and compare multiple data distributions.

        Args:
            distribution_data: Dictionary mapping distribution names to data arrays
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        distributions = list(distribution_data.keys())
        colors = plt.cm.tab10(np.linspace(0, 1, len(distributions)))

        # Box plots
        data_lists = [distribution_data[dist] for dist in distributions]
        bp = ax1.boxplot(data_lists, tick_labels=distributions, patch_artist=True)
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
        ax1.set_ylabel("Value", fontsize=MIN_FONT)
        ax1.set_title("Box Plot Comparison", fontsize=MIN_FONT + 2, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # Violin plots
        parts = ax2.violinplot(data_lists, showmeans=True, showextrema=True)
        for i, (pc, color) in enumerate(zip(parts["bodies"], colors)):
            pc.set_facecolor(color)
            pc.set_edgecolor("black")
            pc.set_alpha(0.7)
        ax2.set_xticks(range(1, len(distributions) + 1))
        ax2.set_ylabel("Value", fontsize=MIN_FONT)
        ax2.set_title("Violin Plot Comparison", fontsize=MIN_FONT + 2, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        # Histograms
        for i, (name, data) in enumerate(distribution_data.items()):
            ax3.hist(
                data, bins=20, alpha=0.7, label=name, color=colors[i], edgecolor="black"
            )
        ax3.set_xlabel("Value", fontsize=MIN_FONT)
        ax3.set_ylabel("Frequency", fontsize=MIN_FONT)
        ax3.set_title("Histogram Comparison", fontsize=MIN_FONT + 2, fontweight="bold")
        ax3.legend(fontsize=MIN_FONT)
        ax3.grid(True, alpha=0.3)

        # Cumulative distribution functions
        for i, (name, data) in enumerate(distribution_data.items()):
            sorted_data = np.sort(data)
            yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
            ax4.plot(sorted_data, yvals, label=name, color=colors[i], linewidth=2)
        ax4.set_xlabel("Value", fontsize=MIN_FONT)
        ax4.set_ylabel("Cumulative Probability", fontsize=MIN_FONT)
        ax4.set_title("CDF Comparison", fontsize=MIN_FONT + 2, fontweight="bold")
        ax4.legend(fontsize=MIN_FONT)
        ax4.grid(True, alpha=0.3)
        plt.suptitle(title, fontsize=MIN_FONT + 4, fontweight="bold")
        plt.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @publication_style
    def visualize_effect_sizes(
        self,
        effect_size_data: Dict[str, Dict[str, float]],
        filepath: Optional[Path] = None,
        title: str = "Effect Size Analysis",
    ) -> plt.Figure:
        """Visualize effect sizes with interpretation guidelines.

        Args:
            effect_size_data: Dictionary of effect size results
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Extract effect sizes and labels
        labels = []
        effect_sizes = []
        categories = []

        for comparison, data in effect_size_data.items():
            es = data.get("effect_size", 0)
            effect_sizes.append(es)
            labels.append(comparison)

            # Categorize effect size
            if abs(es) < 0.2:
                categories.append("Negligible")
            elif abs(es) < 0.5:
                categories.append("Small")
            elif abs(es) < 0.8:
                categories.append("Medium")
            else:
                categories.append("Large")

        # Colorblind-safe magnitude palette (Okabe-Ito)
        category_colors = {
            "Negligible": "#BBBBBB",
            "Small": "#56B4E9",
            "Medium": "#E69F00",
            "Large": "#D55E00",
        }

        colors = [category_colors[cat] for cat in categories]

        # Create horizontal bar chart
        bars = ax.barh(
            range(len(effect_sizes)),
            effect_sizes,
            color=colors,
            alpha=0.7,
            edgecolor="black",
        )

        # Add value labels
        for i, (bar, es) in enumerate(zip(bars, effect_sizes)):
            width = bar.get_width()
            label_x = width + 0.01 if width >= 0 else width - 0.01
            ax.text(
                label_x,
                bar.get_y() + bar.get_height() / 2,
                f"{es:.2f}",
                ha="left" if width >= 0 else "right",
                va="center",
                fontsize=MIN_FONT,
                fontweight="bold",
            )

        # Add interpretation zones
        ax.axvline(x=-0.2, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(x=0.2, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(x=-0.5, color="orange", linestyle="--", alpha=0.5)
        ax.axvline(x=0.5, color="orange", linestyle="--", alpha=0.5)
        ax.axvline(x=-0.8, color="red", linestyle="--", alpha=0.5)
        ax.axvline(x=0.8, color="red", linestyle="--", alpha=0.5)

        # Add zone labels
        ax.text(
            -0.1,
            len(effect_sizes) * 0.9,
            "Negligible",
            ha="center",
            va="center",
            fontsize=MIN_FONT,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgray", alpha=0.7),
        )
        ax.text(
            -0.35,
            len(effect_sizes) * 0.9,
            "Small",
            ha="center",
            va="center",
            fontsize=MIN_FONT,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue", alpha=0.7),
        )
        ax.text(
            -0.65,
            len(effect_sizes) * 0.9,
            "Medium",
            ha="center",
            va="center",
            fontsize=MIN_FONT,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="orange", alpha=0.7),
        )
        ax.text(
            -0.9,
            len(effect_sizes) * 0.8,
            "Large",
            ha="center",
            va="center",
            fontsize=MIN_FONT,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="red", alpha=0.7),
        )

        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=MIN_FONT)
        ax.set_xlabel("Effect Size (Cohen's d)", fontsize=MIN_FONT)
        ax.set_title(title, fontsize=MIN_FONT + 4, fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Add legend
        legend_elements = [
            patches.Patch(facecolor=color, edgecolor="black", label=cat, alpha=0.7)
            for cat, color in category_colors.items()
        ]
        ax.legend(
            handles=legend_elements,
            title="Effect Size Magnitude",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )

        plt.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @publication_style
    def plot_confidence_intervals(
        self,
        ci_data: Dict[str, Dict[str, float]],
        filepath: Optional[Path] = None,
        title: str = "Confidence Intervals",
    ) -> plt.Figure:
        """Plot confidence intervals for multiple estimates.

        Args:
            ci_data: Dictionary with keys 'estimate', 'ci_lower', 'ci_upper' for each group
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        groups = list(ci_data.keys())
        estimates = [ci_data[group]["estimate"] for group in groups]
        ci_lowers = [ci_data[group]["ci_lower"] for group in groups]
        ci_uppers = [ci_data[group]["ci_upper"] for group in groups]

        # Calculate error bars
        yerr_lower = [est - lower for est, lower in zip(estimates, ci_lowers)]
        yerr_upper = [upper - est for est, upper in zip(estimates, ci_uppers)]
        yerr = [yerr_lower, yerr_upper]

        # Create plot
        x_positions = range(len(groups))
        ax.errorbar(
            x_positions,
            estimates,
            yerr=yerr,
            fmt="o",
            color="blue",
            ecolor="black",
            capsize=5,
            capthick=2,
            markersize=8,
            linewidth=2,
            alpha=0.8,
        )

        # Add reference line at zero if appropriate
        if min(ci_lowers) < 0 < max(ci_uppers):
            ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)

        # Add significance indicators
        for i, (group, estimate) in enumerate(zip(groups, estimates)):
            ci_lower = ci_lowers[i]
            ci_upper = ci_uppers[i]

            # Check if CI excludes zero (for difference measures)
            if ci_lower > 0 or ci_upper < 0:
                # Significant result
                ax.plot(
                    i,
                    estimate,
                    "o",
                    markersize=10,
                    markerfacecolor="red",
                    markeredgecolor="black",
                    markeredgewidth=2,
                )
                ax.text(
                    i,
                    estimate + (ci_upper - estimate) * 0.1,
                    "*",
                    ha="center",
                    va="bottom",
                    fontsize=MIN_FONT,
                    fontweight="bold",
                )

        ax.set_xticks(x_positions)
        ax.set_xticklabels(groups, rotation=45, ha="right", fontsize=MIN_FONT)
        ax.set_ylabel("Estimate", fontsize=MIN_FONT)
        ax.set_title(title, fontsize=MIN_FONT + 4, fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Add legend
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="blue",
                markersize=8,
                label="Estimate",
                linestyle="None",
            ),
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="red",
                markersize=10,
                markerfacecolor="red",
                markeredgecolor="black",
                label="Statistically Significant",
                linestyle="None",
            ),
        ]
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @publication_style
    def create_statistical_dashboard(
        self,
        dashboard_data: Dict[str, Any],
        filepath: Optional[Path] = None,
        title: str = "Statistical Analysis Dashboard",
    ) -> plt.Figure:
        """Create a comprehensive statistical dashboard.

        Args:
            dashboard_data: Dictionary containing various statistical results
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        axes = axes.flatten()

        plot_idx = 0
        rendered = set()
        panel_titles = {
            "significance_results": "Statistical Significance",
            "effect_sizes": "Effect Sizes",
            "distributions": "Distribution Comparison",
            "correlation_matrix": "Correlation Matrix",
            "confidence_intervals": "Confidence Intervals",
        }

        # Plot 1: Statistical significance (if available)
        if "significance_results" in dashboard_data and plot_idx < len(axes):
            sig_data = dashboard_data["significance_results"]
            if "p_value" in sig_data:
                p_val = sig_data["p_value"]
                threshold = sig_data.get("significance_threshold", 0.05)

                axes[plot_idx].bar(
                    ["P-Value", "Threshold"],
                    [p_val, threshold],
                    color=["skyblue", "red"],
                    alpha=0.7,
                )
                axes[plot_idx].set_title("Statistical Significance")
                axes[plot_idx].grid(True, alpha=0.3)
                axes[plot_idx].set_ylabel("Value", fontsize=MIN_FONT)
                plot_idx += 1
                rendered.add("significance_results")

        # Plot 2: Effect sizes (if available)
        if "effect_sizes" in dashboard_data and plot_idx < len(axes):
            es_data = dashboard_data["effect_sizes"]
            if es_data:
                labels = list(es_data.keys())[:5]  # Limit to 5
                values = [es_data[label] for label in labels]

                axes[plot_idx].barh(labels, values, color="lightgreen", alpha=0.7)
                axes[plot_idx].set_xlabel("Effect size", fontsize=MIN_FONT)
                axes[plot_idx].set_ylabel("Comparison", fontsize=MIN_FONT)
                axes[plot_idx].set_title("Effect Sizes")
                axes[plot_idx].grid(True, alpha=0.3)
                plot_idx += 1
                rendered.add("effect_sizes")

        # Plot 3: Distribution comparison (if available)
        if "distributions" in dashboard_data and plot_idx < len(axes):
            dist_data = dashboard_data["distributions"]
            if len(dist_data) >= 2:
                # Simple box plot for first two distributions
                dist_names = list(dist_data.keys())[:2]
                data_lists = [dist_data[name] for name in dist_names]

                axes[plot_idx].boxplot(data_lists, tick_labels=dist_names)
                axes[plot_idx].set_ylabel("Value", fontsize=MIN_FONT)
                axes[plot_idx].set_title("Distribution Comparison")
                axes[plot_idx].grid(True, alpha=0.3)
                plot_idx += 1
                rendered.add("distributions")

        # Plot 4: Correlation heatmap (if available)
        if "correlation_matrix" in dashboard_data and plot_idx < len(axes):
            corr_data = dashboard_data["correlation_matrix"]
            if corr_data:
                # Create simple correlation visualization
                variables = list(corr_data.keys())[:4]  # Limit to 4x4
                corr_matrix = np.eye(len(variables))

                for i, v1 in enumerate(variables):
                    for j, v2 in enumerate(variables):
                        corr_matrix[i, j] = corr_data[v1].get(v2, 0)

                im = axes[plot_idx].imshow(corr_matrix, cmap="RdYlBu_r", aspect="equal")
                axes[plot_idx].set_xticks(range(len(variables)))
                axes[plot_idx].set_yticks(range(len(variables)))
                axes[plot_idx].set_xticklabels(variables, rotation=45, ha="right")
                axes[plot_idx].set_yticklabels(variables)
                axes[plot_idx].set_title("Correlation Matrix")
                plt.colorbar(im, ax=axes[plot_idx])
                plot_idx += 1
                rendered.add("correlation_matrix")

        # Plot 5: Confidence intervals (if available)
        if "confidence_intervals" in dashboard_data and plot_idx < len(axes):
            ci_data = dashboard_data["confidence_intervals"]
            if ci_data:
                groups = list(ci_data.keys())[:4]  # Limit to 4
                estimates = [ci_data[g]["estimate"] for g in groups]
                lowers = [ci_data[g]["ci_lower"] for g in groups]
                uppers = [ci_data[g]["ci_upper"] for g in groups]

                x_pos = range(len(groups))
                yerr_lower = [est - low for est, low in zip(estimates, lowers)]
                yerr_upper = [up - est for est, up in zip(estimates, uppers)]

                axes[plot_idx].errorbar(
                    x_pos, estimates, yerr=[yerr_lower, yerr_upper], fmt="o", capsize=5
                )
                axes[plot_idx].set_xticks(x_pos)
                axes[plot_idx].set_xticklabels(groups, rotation=45, ha="right")
                axes[plot_idx].set_xlabel("Group", fontsize=MIN_FONT)
                axes[plot_idx].set_ylabel("Estimate", fontsize=MIN_FONT)
                axes[plot_idx].set_title("Confidence Intervals")
                axes[plot_idx].grid(True, alpha=0.3)
                plot_idx += 1
                rendered.add("confidence_intervals")

        # Hide unused subplots; label every skipped panel with its metric so
        # the dashboard never shows an anonymous empty panel.
        pending = [
            label for key, label in panel_titles.items() if key not in rendered
        ]
        for i in range(plot_idx, len(axes)):
            axes[i].axis("off")
            if i - plot_idx < len(pending):
                axes[i].set_title(f"{pending[i - plot_idx]} — no data")

        plt.suptitle(title, fontsize=MIN_FONT + 4, fontweight="bold")
        plt.tight_layout(rect=(0, 0, 1, 0.95))

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @publication_style
    def visualize_hypothesis_testing(
        self,
        hypothesis_results: List[Dict[str, Any]],
        filepath: Optional[Path] = None,
        title: str = "Hypothesis Testing Results",
    ) -> plt.Figure:
        """Visualize results from multiple hypothesis tests.

        Args:
            hypothesis_results: List of hypothesis test results
            filepath: Optional path to save figure
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Extract test results
        test_names = []
        p_values = []
        effect_sizes = []
        significances = []

        for result in hypothesis_results:
            test_names.append(result.get("test_name", f"Test {len(test_names) + 1}"))
            p_values.append(result.get("p_value", 1.0))
            effect_sizes.append(result.get("effect_size", 0))
            significances.append(result.get("p_value", 1.0) < 0.05)

        # Create scatter plot
        colors = ["red" if sig else "blue" for sig in significances]
        sizes = [abs(es) * 100 + 50 for es in effect_sizes]  # Size based on effect size

        ax.scatter(
            p_values, effect_sizes, c=colors, s=sizes, alpha=0.7, edgecolors="black"
        )

        # Add significance threshold line
        ax.axvline(x=0.05, color="red", linestyle="--", alpha=0.7, label="α = 0.05")

        # Add labels for significant results
        for i, (name, p_val, es, sig) in enumerate(
            zip(test_names, p_values, effect_sizes, significances)
        ):
            if sig:
                ax.annotate(
                    name,
                    (p_val, es),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=MIN_FONT,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="yellow", alpha=0.8),
                )

        ax.set_xlabel("P-Value", fontsize=MIN_FONT)
        ax.set_ylabel("Effect Size", fontsize=MIN_FONT)
        ax.set_title(title, fontsize=MIN_FONT + 4, fontweight="bold")
        ax.set_xscale("log")  # Log scale for p-values
        ax.grid(True, alpha=0.3)

        # Add legend
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="red",
                markersize=8,
                label="Significant (p < 0.05)",
                linestyle="None",
            ),
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="blue",
                markersize=8,
                label="Not Significant",
                linestyle="None",
            ),
            plt.Line2D(
                [0], [0], color="red", linestyle="--", label="Significance Threshold"
            ),
        ]
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig


# ── Frozen statistics-artifact figure (consumed by the pipeline wave) ──

# Colorblind-safe (Okabe-Ito) coding for BH significance on the effect
# panel — consistent with StatisticalVisualizer.significance_colors.
_SIGNIFICANT_COLOR = "#D55E00"  # Vermillion
_NOT_SIGNIFICANT_COLOR = "#0072B2"  # Blue
_DOMAIN_SHORT_NAMES = {
    "unit_of_individuality": "Unit",
    "behavior_and_identity": "Behavior",
    "power_and_labor": "Power",
    "sex_and_reproduction": "Sex",
    "kin_and_relatedness": "Kin",
    "economics": "Economics",
}


def _short_domain(name: str) -> str:
    """Compact display name for a domain (short canonical names, others title-cased).

    Examples:
        >>> _short_domain("behavior_and_identity")
        'Behavior'
        >>> _short_domain("noncanonical_extra_domain")
        'Noncanonical Extra Domain'
    """
    return _DOMAIN_SHORT_NAMES.get(name, name.replace("_", " ").title())


def _format_p(p: float) -> str:
    """Format a p-value for annotation, rendering tiny values as ``p < 0.001``.

    Args:
        p: P-value from the statistics artifact.

    Returns:
        Human-readable p-value string.
    """
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"


def _domain_order(descriptives: Dict[str, Any]) -> List[str]:
    """Order domains canonically first, then any extras lexicographically.

    Deterministic regardless of JSON key order or set iteration.

    Args:
        descriptives: Per-domain descriptive statistics mapping.

    Returns:
        Ordered list of domain names.
    """
    canonical = [d for d in CANONICAL_DOMAINS if d in descriptives]
    extras = sorted(d for d in descriptives if d not in CANONICAL_DOMAINS)
    return canonical + extras


def _fallback_text(ax: plt.Axes, message: str) -> None:
    """Render a centered fallback message on a panel.

    Args:
        ax: Axes to draw the message on.
        message: Explanation shown in place of the missing data.
    """
    ax.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=MIN_FONT,
        style="italic",
    )
    ax.axis("off")


@publication_style
def plot_statistical_analysis(
    stats: dict,
    output_dir: str,
    filename: str = "statistical_analysis.png",
) -> str:
    """Render the frozen statistics artifact as a multi-panel figure.

    Consumes the frozen ``statistical_analysis.json`` schema:

    - ``descriptives``: per-domain ``n_terms``, ``entropy_mean``, ``entropy_sd``
    - ``pairwise``: pairwise t-tests with ``cohens_d`` and BH significance
    - ``anova``: omnibus F-test with ``eta_squared``
    - ``corrections``: multiple-comparison metadata

    Panels: (a) per-domain entropy means with 95% CI whiskers and n
    annotations; (b) diverging Cohen's d bars, colourblind-safe coding
    for BH-significant vs non-significant comparisons; (c) compact
    ANOVA summary text panel.

    Missing/empty sections degrade to labelled fallback panels; ``p`` values
    below 0.001 (including exact 0.0) are annotated as ``p < 0.001``.

    Args:
        stats: Statistics artifact dict matching the frozen schema.
        output_dir: Directory the figure is written to (created if absent).
        filename: Output filename.

    Returns:
        Absolute path to the saved figure.

    Raises:
        RuntimeError: If the saved file is missing or empty.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    descriptives: Dict[str, Any] = stats.get("descriptives") or {}
    pairwise: List[Dict[str, Any]] = stats.get("pairwise") or []
    anova: Dict[str, Any] = stats.get("anova") or {}
    corrections: Dict[str, Any] = stats.get("corrections") or {}

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.45, wspace=0.55)
    ax_entropy = fig.add_subplot(gs[0, 0])
    ax_effects = fig.add_subplot(gs[0, 1])
    ax_summary = fig.add_subplot(gs[1, :])

    # ── Panel (a): per-domain entropy mean with 95% CI whiskers ──
    # Only domains whose descriptives entry actually carries
    # ``entropy_mean`` (tiny fixtures can omit it); plotting a missing
    # metric is a crash, not a zero.
    order = [
        d for d in _domain_order(descriptives)
        if "entropy_mean" in (descriptives.get(d) or {})
    ]
    if order:
        means = [float(descriptives[d]["entropy_mean"]) for d in order]
        # Whiskers drawn only when the artifact actually reports
        # per-domain ``entropy_sd`` (with ``n_terms``); otherwise omit
        # them honestly rather than drawing zero-length error bars
        # that read as measured zero variance.
        # 95% confidence intervals (the publication-standard
        # uncertainty display) computed from the artifact's per-domain
        # ``entropy_sd`` and ``n_terms``; SD whiskers overstate overlap
        # between domains and invite misreading.  Student-t quantiles
        # for honest small-n intervals, falling back to the normal
        # approximation when scipy is unavailable.
        has_sd = all("entropy_sd" in descriptives[d] for d in order)
        cis = None
        if has_sd:
            cis = []
            for d in order:
                n = int(descriptives[d].get("n_terms", 0))
                sd = float(descriptives[d]["entropy_sd"])
                if n > 1 and sd > 0:
                    try:
                        from scipy.stats import t as student_t
                        crit = float(student_t.ppf(0.975, n - 1))
                    except ImportError:
                        crit = 1.96
                    cis.append(crit * sd / (n ** 0.5))
                else:
                    cis.append(0.0)
            if not any(c > 0 for c in cis):
                cis = None
        colors = [DOMAIN_PALETTE.get(d, FALLBACK_COLOR) for d in order]
        bars = ax_entropy.bar(
            range(len(order)),
            means,
            yerr=cis,
            capsize=4 if cis else None,
            color=colors,
            edgecolor="black",
            alpha=0.85,
        )
        ax_entropy.set_xticks(range(len(order)))
        ax_entropy.set_xticklabels(
            [d.replace("_", " ").title() for d in order],
            rotation=30,
            ha="right",
        )
        if cis:
            top = max(m + c for m, c in zip(means, cis))
        else:
            top = max(means)
        ax_entropy.set_ylim(0, top * 1.25)
        for bar, domain in zip(bars, order):
            n_terms = descriptives[domain].get("n_terms", 0)
            ci = (
                cis[order.index(domain)]
                if cis
                else 0.0
            )
            ax_entropy.annotate(
                f"n={n_terms}",
                # Anchor above the CI whisker cap (bar top when no CI
                # is reported) so the text never crosses the error bar.
                xy=(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + ci,
                ),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                fontsize=MIN_FONT,
            )
        ax_entropy.set_ylabel(
            "Semantic Entropy (mean ± 95% CI)" if cis
            else "Semantic Entropy (mean)",
            fontsize=MIN_FONT,
        )
        ax_entropy.set_title("Domain Entropy", fontsize=MIN_FONT + 2, fontweight="bold")
        ax_entropy.grid(True, axis="y", alpha=0.3)
    else:
        _fallback_text(ax_entropy, "No domain descriptives available")

    # ── Panel (b): Cohen's d diverging bars, BH significance coding ──
    if pairwise:
        labels = [
            # Single-line compact labels: 15 two-line full-domain labels
            # overlap at the 16pt floor, so comparisons render as short
            # domain names on one row each.
            "{} vs {}".format(
                _short_domain(row.get("domain_a", "?")),
                _short_domain(row.get("domain_b", "?")),
            )
            for row in pairwise
        ]
        ds = [float(row.get("cohens_d", 0.0)) for row in pairwise]
        colors = [
            _SIGNIFICANT_COLOR if row.get("significant_bh") else _NOT_SIGNIFICANT_COLOR
            for row in pairwise
        ]
        ypos = np.arange(len(pairwise))
        ax_effects.barh(
            ypos,
            ds,
            color=colors,
            edgecolor="black",
            alpha=0.85,
        )
        ax_effects.axvline(0.0, color="black", linewidth=0.8)
        ax_effects.set_yticks(ypos)
        ax_effects.set_yticklabels(labels)
        ax_effects.invert_yaxis()
        span = max(0.1, max(abs(d) for d in ds))
        ax_effects.set_xlim(-span * 1.55, span * 1.55)
        for y, d, row in zip(ypos, ds, pairwise):
            ax_effects.text(
                d + (span * 0.04 if d >= 0 else -span * 0.04),
                y,
                f"{d:+.2f}",
                va="center",
                ha="left" if d >= 0 else "right",
                fontsize=MIN_FONT,
            )
            # BH-significance marker: colour already codes significance
            # (vermillion vs blue); the asterisk keeps it readable in
            # greyscale, directly above each significant bar's tip.
            if row.get("significant_bh"):
                ax_effects.annotate(
                    "*",
                    xy=(d, y),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=MIN_FONT,
                    fontweight="bold",
                    color=_SIGNIFICANT_COLOR,
                )
        ax_effects.set_xlabel(
            "Cohen's d (* = BH-significant)", fontsize=MIN_FONT
        )
        ax_effects.set_title(
            "Pairwise Effect Sizes", fontsize=MIN_FONT + 2, fontweight="bold"
        )
        ax_effects.grid(True, axis="x", alpha=0.3)
        legend_elements = [
            patches.Patch(
                facecolor=_SIGNIFICANT_COLOR, edgecolor="black",
                label="BH-significant", alpha=0.85,
            ),
            patches.Patch(
                facecolor=_NOT_SIGNIFICANT_COLOR, edgecolor="black",
                label="Not significant", alpha=0.85,
            ),
        ]
        # Outside the axes so the legend can never collide with bars or
        # their value labels; savefig(bbox_inches="tight") keeps it.
        ax_effects.legend(
            handles=legend_elements, loc="upper left", bbox_to_anchor=(1.02, 1)
        )
    else:
        _fallback_text(ax_effects, "No pairwise comparisons available")

    # ── Panel (c): compact ANOVA summary text ──
    if anova:
        # Readable two-line summary: a bolded header line and a single
        # statistics line carrying F, p, effect size and the correction
        # provenance, instead of the previous five-line block.
        metric = anova.get("metric", "")
        header = "ANOVA Summary"
        if metric:
            header += f" — {metric.replace('_', ' ').title()}"
        stat_line = "F({},{}) = {:.2f}, {}".format(
            "{:g}".format(float(anova.get("df1", float("nan")))),
            "{:g}".format(float(anova.get("df2", float("nan")))),
            float(anova.get("F", float("nan"))),
            _format_p(float(anova.get("p", 1.0))),
        )
        stat_line += f", η² = {float(anova.get('eta_squared', 0.0)):.3f}"
        if corrections:
            stat_line += " ({} over {} comparisons)".format(
                str(corrections.get("method", "unknown")).replace("_", " ").title(),
                corrections.get("n_comparisons", "?"),
            )
        ax_summary.text(
            0.5,
            0.60,
            header,
            ha="center",
            va="center",
            transform=ax_summary.transAxes,
            fontsize=MIN_FONT + 2,
            fontweight="bold",
        )
        ax_summary.text(
            0.5,
            0.35,
            stat_line,
            ha="center",
            va="center",
            transform=ax_summary.transAxes,
            fontsize=MIN_FONT,
        )
        ax_summary.axis("off")
    else:
        _fallback_text(ax_summary, "No ANOVA results available")

    filepath = out_path / filename
    save_and_verify(fig, filepath, dpi=300)
    plt.close(fig)
    return str(filepath)


@publication_style
def plot_layer_comparison(
    abstract_artifact: dict,
    fulltext_artifact: dict,
    output_dir: str,
    filename: str = "layer_comparison.png",
    metadata: Optional[Dict[str, Dict[str, Any]]] = None,
) -> str:
    """Render grouped per-domain entropy bars for the two corpus layers.

    Side-by-side bars per canonical Ento-Linguistic domain: the abstract
    layer (solid, domain palette colour) vs the full-text layer (same
    colour, hatched), both reading ``descriptives.<domain>.entropy_mean``
    from their artifacts.  Domains follow the canonical manuscript order
    first, then any extras lexicographically (shared
    :func:`_domain_order`); bars carry per-group value labels with
    per-layer ``n_terms`` annotations and every text element respects
    the 16pt floor.  The legend names each layer with its corpus size
    (``n_documents``) when the artifact — or the optional ``metadata``
    override — carries it.  Deterministic: fixed order, fixed colours,
    no randomness.

    Args:
        abstract_artifact: Parsed ``statistical_analysis.json`` (abstract
            layer).  An empty dict yields a labelled fallback panel.
        fulltext_artifact: Parsed ``fulltext_analysis.json`` (full-text
            layer).
        output_dir: Directory the figure is written to (created if absent).
        filename: Output filename.
        metadata: Optional per-layer overrides, e.g.
            ``{"abstract": {"n_documents": 120}}`` / ``{"fulltext": {...}}``.
            ``n_documents`` here takes precedence over the artifact's own
            value, so callers can supply corpus sizes for artifacts that
            do not record them.  Ignored when ``None`` (default).

    Returns:
        Absolute path to the saved figure.

    Raises:
        RuntimeError: If the saved file is missing or empty.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    abstract_desc: Dict[str, Any] = abstract_artifact.get("descriptives") or {}
    fulltext_desc: Dict[str, Any] = fulltext_artifact.get("descriptives") or {}
    order = _domain_order({**abstract_desc, **fulltext_desc})

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111)

    if order:
        abstract_means = [
            float((abstract_desc.get(d) or {}).get("entropy_mean", 0.0))
            for d in order
        ]
        fulltext_means = [
            float((fulltext_desc.get(d) or {}).get("entropy_mean", 0.0))
            for d in order
        ]
        abstract_ns = [
            int((abstract_desc.get(d) or {}).get("n_terms", 0)) for d in order
        ]
        fulltext_ns = [
            int((fulltext_desc.get(d) or {}).get("n_terms", 0)) for d in order
        ]
        xpos = np.arange(len(order))
        width = 0.38
        colors = [DOMAIN_PALETTE.get(d, FALLBACK_COLOR) for d in order]
        meta = metadata or {}

        def _layer_label(default: str, artifact: dict, layer_meta: dict) -> str:
            n_docs = layer_meta.get(
                "n_documents", artifact.get("n_documents")
            )
            if n_docs is None:
                return default
            return f"{default}\n(n={n_docs} documents)"

        ax.bar(
            xpos - width / 2,
            abstract_means,
            width=width,
            color=colors,
            edgecolor="black",
            alpha=0.9,
            label=_layer_label(
                "Abstract layer", abstract_artifact, meta.get("abstract") or {}
            ),
        )
        ax.bar(
            xpos + width / 2,
            fulltext_means,
            width=width,
            color=colors,
            edgecolor="black",
            alpha=0.55,
            hatch="//",
            label=_layer_label(
                "Full-text layer", fulltext_artifact, meta.get("fulltext") or {}
            ),
        )
        ax.set_xticks(xpos)
        ax.set_xticklabels(
            [d.replace("_", " ").title() for d in order],
            rotation=30,
            ha="right",
        )
        top = max(
            max(abstract_means, default=0.0), max(fulltext_means, default=0.0)
        )
        ax.set_ylim(0, top * 1.25 if top > 0 else 1.0)
        for x, value, n_terms in zip(
            xpos - width / 2, abstract_means, abstract_ns
        ):
            ax.annotate(
                f"{value:.2f}\nn={n_terms}",
                xy=(x, value),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=MIN_FONT,
            )
        for x, value, n_terms in zip(
            xpos + width / 2, fulltext_means, fulltext_ns
        ):
            ax.annotate(
                f"{value:.2f}\nn={n_terms}",
                xy=(x, value),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=MIN_FONT,
            )
        ax.set_ylabel("Semantic Entropy (mean)", fontsize=MIN_FONT)
        ax.set_title(
            "Domain Semantic Entropy: Abstract vs Full-Text Layer",
            fontsize=MIN_FONT + 2,
            fontweight="bold",
        )
        ax.grid(True, axis="y", alpha=0.3)
        # Outside the axes so the legend can never collide with bar
        # value labels; bbox_inches="tight" in save_and_verify keeps it.
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    else:
        _fallback_text(ax, "No domain descriptives available")

    filepath = out_path / filename
    save_and_verify(fig, filepath, dpi=300)
    plt.close(fig)
    return str(filepath)


#: Canonical key ordering per discourse dimension (canonical members
#: first, extras appended lexicographically) shared by
#: :func:`plot_discourse_comparison`.  Mirrors the token-family
#: ordering in ``core.manuscript_variables._DISCOURSE_CANONICAL_ORDER``.
_DISCOURSE_DIMENSIONS: List[Tuple[str, str, Tuple[str, ...]]] = [
    (
        "patterns",
        "Discourse Patterns",
        (
            "anthropomorphic_framing",
            "economic_metaphors",
            "hierarchical_framing",
            "scale_ambiguity",
        ),
    ),
    (
        "rhetorical",
        "Rhetorical Strategies",
        ("analogy", "anecdotal", "authority", "generalization"),
    ),
    (
        "persuasive",
        "Persuasive Techniques",
        (
            "authoritative_citations",
            "metaphorical_language",
            "quantitative_emphasis",
            "rhetorical_questions",
        ),
    ),
]

#: Grouped-bar scale threshold: when a panel's plotted maximum is at
#: least this multiple of its smallest positive value, the panel
#: switches to a symlog y-axis (linear below 1 occurrence) so bars
#: spanning orders of magnitude stay legible.  Chosen over a plain
#: log scale because discourse frequencies can legitimately be 0
#: (zero is drawable on symlog, invisible on log).
_LOG_SCALE_RATIO = 100.0


def _ordered_discourse_keys(section: str, members: dict) -> List[str]:
    """Order one discourse dimension's keys canonically, extras sorted."""
    canonical = next(
        (c for name, _, c in _DISCOURSE_DIMENSIONS if name == section), ()
    )
    return [k for k in canonical if k in members] + sorted(
        k for k in members if k not in canonical
    )


@publication_style
def plot_discourse_comparison(
    abstract_artifact: dict,
    fulltext_artifact: dict,
    output_dir: str,
    filename: str = "discourse_comparison.png",
) -> str:
    """Render per-dimension discourse-frequency bars for the two layers.

    One panel per shared ``discourse`` dimension — discourse patterns,
    rhetorical strategies, persuasive techniques — with grouped bars
    comparing the abstract layer (solid) against the full-text layer
    (hatched, same neutral palette) reading
    ``discourse.<dimension>.<key>.frequency`` (persuasive techniques
    read ``usage_frequency``) from both artifacts.  Keys follow the
    canonical ordering (:data:`_DISCOURSE_DIMENSIONS`, extras
    lexicographic); every text element respects the 16pt floor;
    per-layer legend labels carry the analyzed-text counts
    (``n_texts_analyzed``, which discloses the full-text layer's
    deterministic 20% sample).

    Scaling: when a panel's plotted maximum is at least 100x its
    smallest positive value, the panel uses a symlog y-axis (linear
    below 1) so abstract vs full-text ranges that differ by orders of
    magnitude stay legible; symlog rather than plain log because zero
    frequencies are drawable.  The choice is deterministic (fixed
    threshold, fixed order, no randomness).

    Missing ``discourse`` sections or empty dimensions degrade to
    labelled fallback panels; no fabricated zeros are drawn.

    Args:
        abstract_artifact: Parsed ``statistical_analysis.json``.
        fulltext_artifact: Parsed ``fulltext_analysis.json``.
        output_dir: Directory the figure is written to (created if
            absent).
        filename: Output filename.

    Returns:
        Absolute path to the saved figure.

    Raises:
        RuntimeError: If the saved file is missing or empty.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    abstract_discourse: Dict[str, Any] = (
        abstract_artifact.get("discourse") or {}
    )
    fulltext_discourse: Dict[str, Any] = (
        fulltext_artifact.get("discourse") or {}
    )

    fig = plt.figure(figsize=(18, 7.5))
    axes = fig.subplots(1, 3)
    # Headroom for the shared figure-level legend row above the
    # per-panel titles.
    fig.subplots_adjust(top=0.86)
    has_bars = False
    abstract_n = abstract_discourse.get("n_texts_analyzed")
    fulltext_n = fulltext_discourse.get("n_texts_analyzed")
    abstract_label = (
        f"Abstract layer (n={abstract_n} texts)"
        if abstract_n is not None
        else "Abstract layer"
    )
    fulltext_label = (
        f"Full-text layer (n={fulltext_n} texts)"
        if fulltext_n is not None
        else "Full-text layer"
    )

    for ax, (section, title, _canonical) in zip(axes, _DISCOURSE_DIMENSIONS):
        members: Dict[str, Any] = abstract_discourse.get(section) or {}
        extra_members: Dict[str, Any] = fulltext_discourse.get(section) or {}
        keys = _ordered_discourse_keys(section, {**members, **extra_members})
        if not keys:
            _fallback_text(ax, f"No {section.replace('_', ' ')} data available")
            continue
        value_key = "usage_frequency" if section == "persuasive" else "frequency"
        abstract_values = [
            float((members.get(k) or {}).get(value_key, 0.0)) for k in keys
        ]
        fulltext_values = [
            float((extra_members.get(k) or {}).get(value_key, 0.0)) for k in keys
        ]
        xpos = np.arange(len(keys))
        width = 0.38
        bars_a = ax.bar(
            xpos - width / 2,
            abstract_values,
            width=width,
            color="#0072B2",
            edgecolor="black",
            alpha=0.9,
            label=abstract_label,
        )
        bars_f = ax.bar(
            xpos + width / 2,
            fulltext_values,
            width=width,
            color="#0072B2",
            edgecolor="black",
            alpha=0.55,
            hatch="//",
            label=fulltext_label,
        )
        ax.set_xticks(xpos)
        ax.set_xticklabels(
            [k.replace("_", " ").title() for k in keys],
            rotation=30,
            ha="right",
        )
        plotted = [v for v in abstract_values + fulltext_values if v > 0]
        top = max(abstract_values + fulltext_values)
        if plotted and top >= _LOG_SCALE_RATIO * min(plotted):
            ax.set_yscale("symlog", linthresh=1)
            ax.set_ylabel("Frequency (symlog scale)", fontsize=MIN_FONT)
        else:
            ax.set_ylim(0, top * 1.25 if top > 0 else 1.0)
            ax.set_ylabel("Frequency", fontsize=MIN_FONT)
        for bars, values in ((bars_a, abstract_values), (bars_f, fulltext_values)):
            for bar, value in zip(bars, values):
                ax.annotate(
                    f"{value:.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, value),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=MIN_FONT,
                )
        # Symlog panels auto-scale without accounting for the value
        # annotations above the tallest bar; widen the top so the
        # labels are never clipped.  Linear panels already reserve
        # 25% headroom via set_ylim above.
        if plotted and top >= _LOG_SCALE_RATIO * min(plotted):
            lo, hi = ax.get_ylim()
            ax.set_ylim(lo, hi * 2.0)
        ax.set_title(title, fontsize=MIN_FONT + 2, fontweight="bold")
        ax.grid(True, axis="y", alpha=0.3)
        has_bars = True
    if has_bars:
        # One shared figure-level legend row above the panels: the
        # per-axes legend used to cover the bars of the first panel.
        handles = []
        labels_ = []
        for ax in axes:
            h, l = ax.get_legend_handles_labels()
            if h:
                handles, labels_ = h, l
                break
        if handles:
            fig.legend(
                handles, labels_, loc="upper center", ncol=2,
                bbox_to_anchor=(0.5, 1.02), frameon=False,
            )
    filepath = out_path / filename
    save_and_verify(fig, filepath, dpi=300)
    plt.close(fig)
    return str(filepath)
