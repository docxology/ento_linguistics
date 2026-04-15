"""Logging utilities for the Ento-Linguistic Research Project.

This module provides structured logging functionality for pipeline execution,
stage tracking, progress reporting, and section signposting. All utilities use
Python's standard ``logging`` module and are controlled via the ``LOG_LEVEL``
environment variable.

Functions:
    get_logger: Create/retrieve a configured logger instance
    log_substep: Log an indented substep message
    log_progress_bar: Log a text-based progress bar
    log_stage: Log a numbered pipeline stage header
    log_section: Log a titled section divider for pipeline signposting
"""

import logging
import os
import time
from typing import Dict, Optional

__all__ = [
    "get_logger",
    "log_substep",
    "log_progress_bar",
    "log_stage",
    "log_section",
]


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with standard configuration.

    The log level is controlled by the ``LOG_LEVEL`` environment variable.
    Accepted values are:
    - Standard Python level names: ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``
      (case-insensitive).
    - Numeric shortcuts: ``0`` (DEBUG), ``1`` (INFO), ``2`` (WARNING),
      ``3`` (ERROR).
    Defaults to ``INFO`` if unset or unrecognised.

    Args:
        name: Logger name (usually ``__name__``)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Resolve level from environment variable
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()

        # Numeric-shorthand map (convenience aliases)
        numeric_map: Dict[str, int] = {
            "0": logging.DEBUG,
            "1": logging.INFO,
            "2": logging.WARNING,
            "3": logging.ERROR,
        }

        if level_str in numeric_map:
            level = numeric_map[level_str]
        else:
            # Standard Python level name (DEBUG, INFO, WARNING, ERROR)
            level = getattr(logging, level_str, logging.INFO)

        logger.setLevel(level)

        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


def log_substep(message: str, logger: Optional[logging.Logger] = None) -> None:
    """Log a substep with indentation.

    Args:
        message: Message to log
        logger: Logger instance (creates default if None)
    """
    if logger is None:
        logger = get_logger(__name__)
    logger.info(f"  {message}")


def log_progress_bar(
    current: int, total: int, task: str, logger: Optional[logging.Logger] = None
) -> None:
    """Log progress with a simple bar.

    Args:
        current: Current progress
        total: Total items
        task: Task description
        logger: Logger instance (creates default if None)
    """
    if logger is None:
        logger = get_logger(__name__)

    percentage = int(100 * current / total) if total > 0 else 0
    bar = "=" * (percentage // 5) + " " * (20 - percentage // 5)
    logger.info(f"[{bar}] {percentage}% - {task}")


def log_stage(
    stage_num: int,
    total_stages: int,
    stage_name: str,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Log a pipeline stage header.

    Args:
        stage_num: Current stage number (1-based)
        total_stages: Total number of stages
        stage_name: Name of the stage
        logger: Logger instance (creates default if None)
    """
    if logger is None:
        logger = get_logger(__name__)
    logger.info(f"Stage {stage_num}/{total_stages}: {stage_name}")


def log_section(
    title: str,
    *,
    elapsed: Optional[float] = None,
    width: int = 60,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Log a titled section divider for pipeline signposting.

    Produces a visually distinct separator that makes log output easier to
    scan.  Optionally appends elapsed wall-clock time for the preceding
    section.

    Example output::

        ═══════════════════════════════════════════════════════════════
        Term Extraction                                      [3.21 s]
        ═══════════════════════════════════════════════════════════════

    Args:
        title: Section title
        elapsed: Optional elapsed time in seconds for the *preceding* section
        width: Character width of the separator line (default 60)
        logger: Logger instance (creates default if None)
    """
    if logger is None:
        logger = get_logger(__name__)

    rule = "\u2550" * width
    if elapsed is not None:
        suffix = f"[{elapsed:.2f} s]"
        padded_title = f"{title:<{width - len(suffix) - 1}} {suffix}"
    else:
        padded_title = title

    logger.info(rule)
    logger.info(padded_title)
    logger.info(rule)
