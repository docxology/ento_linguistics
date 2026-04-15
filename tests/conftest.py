"""Pytest configuration for project tests."""

import os
import sys

# Force headless backend for matplotlib in tests
os.environ.setdefault("MPLBACKEND", "Agg")

# Add template root to path so we can import infrastructure modules
# tests/ -> ento_linguistics/ -> projects/ -> template/
TEMPLATE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if TEMPLATE_ROOT not in sys.path:
    sys.path.insert(0, TEMPLATE_ROOT)

# Configure pytest-httpserver
try:
    import pytest
    from pytest_httpserver import HTTPServer

    @pytest.fixture
    def httpserver():
        """Provide HTTP server for testing."""
        server = HTTPServer()
        server.start()
        yield server
        server.clear()
        if server.is_running():
            server.stop()

except ImportError:
    # pytest-httpserver not available
    pass


# ── Shared fixtures for common test objects ──────────────────────────

@pytest.fixture
def sample_corpus():
    """Provide a small entomological corpus for testing."""
    return [
        "The queen ant lays eggs in the brood chamber of the colony. "
        "Workers tend to the brood and forage for food resources.",
        "Eusocial insect colonies exhibit a division of labor among castes. "
        "The reproductive caste includes queens and males.",
        "Foraging behavior in harvester ants is regulated by local interactions "
        "rather than centralized control from the queen.",
        "Haplodiploidy in Hymenoptera creates asymmetric relatedness among nestmates. "
        "Full sisters share 75% of their genes.",
        "Colony-level selection may operate as a superorganism when individual "
        "fitness is subordinated to collective outcomes.",
    ]


@pytest.fixture
def sample_terms():
    """Provide sample Term objects for testing."""
    from analysis.term_extraction import Term

    terms = [
        Term(text="queen", lemma="queen", frequency=244,
             domains=["power_and_labor", "sex_and_reproduction"]),
        Term(text="worker", lemma="worker", frequency=271,
             domains=["power_and_labor", "behavior_and_identity"]),
        Term(text="colony", lemma="colony", frequency=854,
             domains=["unit_of_individuality"]),
        Term(text="caste", lemma="caste", frequency=125,
             domains=["power_and_labor", "behavior_and_identity"]),
        Term(text="superorganism", lemma="superorganism", frequency=45,
             domains=["unit_of_individuality"]),
        Term(text="haplodiploidy", lemma="haplodiploidy", frequency=30,
             domains=["sex_and_reproduction"]),
        Term(text="foraging", lemma="forage", frequency=162,
             domains=["behavior_and_identity"]),
        Term(text="allocation", lemma="allocation", frequency=64,
             domains=["economics"]),
    ]
    # Add sample contexts
    for term in terms:
        term.add_context(f"The {term.text} plays a key role in colony organization.")
        term.add_context(f"Studies of {term.text} reveal complex social dynamics.")
    return terms


@pytest.fixture
def text_processor():
    """Provide a TextProcessor instance for testing."""
    from analysis.text_analysis import TextProcessor
    return TextProcessor()
