"""Data sub-package for Ento-Linguistic research.

Provides modules for synthetic data generation, data processing/cleaning,
and literature mining.
"""

from .data_generator import (
    generate_synthetic_data,
    generate_time_series,
)
from .data_processing import (
    clean_data,
    create_validation_pipeline,
    detect_outliers,
    extract_features,
    normalize_data,
    remove_outliers,
    standardize_data,
    transform_data,
)
from .literature_mining import (
    ArXivMiner,
    LiteratureCorpus,
    Publication,
    PubMedMiner,
    create_entomology_query,
    mine_entomology_literature,
)
from .loader import DataLoader

__all__ = [
    "ArXivMiner",
    "DataLoader",
    # literature_mining
    "LiteratureCorpus",
    "PubMedMiner",
    "Publication",
    # data_processing
    "clean_data",
    "create_entomology_query",
    "create_validation_pipeline",
    "detect_outliers",
    "extract_features",
    # data_generator
    "generate_synthetic_data",
    "generate_time_series",
    "mine_entomology_literature",
    "normalize_data",
    "remove_outliers",
    "standardize_data",
    "transform_data",
]
