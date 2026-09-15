"""Build the entomological literature corpus for Ento-Linguistic analysis.

Business logic for stage 01: targeted PubMed retrieval, deduplication, corpus
validation statistics, and persistence to ``data/corpus/abstracts.json`` plus
``output/data/corpus_statistics.json``. Invoked via the thin orchestrator
``scripts/01_build_corpus.py``.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from data.literature_mining import PubMedMiner

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("build_ento_corpus")

# Domain-specific PubMed queries for targeted retrieval
# Using simple keyword queries (MeSH tags with brackets get double-encoded by urlencode)
ENTOMOLOGY_QUERIES = [
    "entomology+AND+social+behavior",
    "insect+eusociality",
    "ant+colony+algorithm",
    "honey+bee+communication",
    "termite+caste+differentiation",
    "insect+sociobiology",
    "swarm+behavior+insects",
    "insect+division+of+labor",
]


def fetch_abstracts_for_query(
    miner: PubMedMiner, query: str, max_per_query: int = 50
) -> list[str]:
    """Fetch abstracts for a single PubMed query.

    Args:
        miner: Initialized PubMedMiner instance.
        query: PubMed query string.
        max_per_query: Maximum number of results to fetch for this query.

    Returns:
        List of abstract texts (empty list on failure).
    """
    try:
        pmids = miner.search(query, max_results=max_per_query)
        results = miner.fetch_publications(pmids)
        abstracts = [r.abstract for r in results if r.abstract]
        logger.info(f"  Fetched {len(abstracts)} abstracts for query: {query}")
        return abstracts
    except Exception as e:
        logger.warning(f"  Query failed ({query}): {e}")
        return []


def validate_corpus(abstracts: list[str]) -> dict:
    """Validate and report corpus quality metrics.

    Args:
        abstracts: List of abstract texts.

    Returns:
        Dictionary with total_tokens, unique_tokens,
        avg_abstract_length_tokens, domain_coverage, and top_tokens.
    """
    from collections import Counter

    # Domain seed terms to check for coverage
    domain_seeds = {
        "unit_of_individuality": ["colony", "superorganism", "individual", "nestmate", "organism"],
        "behavior_and_identity": ["foraging", "worker", "behavior", "task", "role", "caste"],
        "power_and_labor": ["caste", "queen", "worker", "hierarchy", "dominant", "subordinate"],
        "sex_and_reproduction": ["haplodiploidy", "reproduction", "mating", "sex", "queen"],
        "kin_and_relatedness": ["kin", "relatedness", "altruism", "inclusive fitness", "cooperation"],
        "economics": ["resource", "allocation", "cost", "benefit", "foraging efficiency"],
    }

    all_text = " ".join(abstracts).lower()
    words = all_text.split()

    domain_coverage = {}
    for domain, seeds in domain_seeds.items():
        found = [term for term in seeds if term in all_text]
        domain_coverage[domain] = {
            "terms_found": found,
            "coverage": len(found) / len(seeds) if seeds else 0,
        }

    word_counts = Counter(words)
    stats = {
        "total_abstracts": len(abstracts),
        "total_tokens": len(words),
        "unique_tokens": len(word_counts),
        "avg_abstract_length_tokens": len(words) / len(abstracts) if abstracts else 0,
        "domain_coverage": domain_coverage,
        "top_tokens": word_counts.most_common(30),
    }

    return stats


def main(project_root: Path | None = None, argv: list[str] | None = None) -> int:
    """Build (or refresh statistics for) the entomological corpus.

    Args:
        project_root: Project root directory. Defaults to the repository root
            that contains this module.
        argv: CLI arguments (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code: 0 when the corpus holds at least 20 abstracts,
        1 otherwise.
    """
    import argparse

    root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description="Build entomological corpus from PubMed abstracts"
    )
    parser.add_argument(
        "--max-per-query",
        type=int,
        default=50,
        help="Maximum results per query (default: 50)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: data/corpus/abstracts.json)",
    )
    parser.add_argument(
        "--stats-output",
        type=str,
        default=None,
        help="Stats output file path (default: output/data/corpus_statistics.json)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch even if corpus already exists",
    )
    args = parser.parse_args(argv)

    # Resolve output paths
    output_path = (
        Path(args.output) if args.output else root / "data" / "corpus" / "abstracts.json"
    )
    stats_path = (
        Path(args.stats_output)
        if args.stats_output
        else root / "output" / "data" / "corpus_statistics.json"
    )

    logger.info("=" * 60)
    logger.info("Ento-Linguistics Corpus Builder")
    logger.info("=" * 60)

    # Skip fetching if corpus already exists with sufficient data
    if output_path.exists() and not args.force:
        with open(output_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if isinstance(existing, list) and len(existing) >= 20:
            logger.info(
                f"Corpus already exists with {len(existing)} abstracts: {output_path}"
            )
            logger.info("Skipping PubMed fetch (use --force to re-fetch)")
            all_abstracts = existing
            stats = validate_corpus(all_abstracts)
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            stats["top_tokens"] = [
                {"token": t, "count": c} for t, c in stats["top_tokens"]
            ]
            for domain_info in stats["domain_coverage"].values():
                domain_info["coverage"] = round(domain_info["coverage"], 3)
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Statistics saved to: {stats_path}")
            logger.info("Corpus build complete (cached)")
            return 0

    logger.info(f"Max per query: {args.max_per_query}")
    logger.info(f"Queries: {len(ENTOMOLOGY_QUERIES)}")
    logger.info(f"Output: {output_path}")

    miner = PubMedMiner()
    all_abstracts = []
    seen = set()  # Deduplicate

    for i, query in enumerate(ENTOMOLOGY_QUERIES, 1):
        logger.info(f"\n--- Query {i}/{len(ENTOMOLOGY_QUERIES)} ---")
        abstracts = fetch_abstracts_for_query(miner, query, args.max_per_query)

        for abstract in abstracts:
            # Deduplicate by first 100 chars
            key = abstract[:100].lower()
            if key not in seen:
                seen.add(key)
                all_abstracts.append(abstract)

        # Rate limit between queries
        if i < len(ENTOMOLOGY_QUERIES):
            time.sleep(1.0)

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Total unique abstracts collected: {len(all_abstracts)}")

    if len(all_abstracts) < 20:
        logger.warning(
            "Very few abstracts collected. The PubMed API may be rate-limiting. "
            "Try again in a few minutes or reduce --max-per-query."
        )

    # Validate corpus quality
    stats = validate_corpus(all_abstracts)
    logger.info(f"Total tokens: {stats['total_tokens']}")
    logger.info(f"Unique tokens: {stats['unique_tokens']}")
    logger.info(
        f"Avg abstract length: {stats['avg_abstract_length_tokens']:.0f} tokens"
    )

    logger.info("\nDomain coverage:")
    for domain, info in stats["domain_coverage"].items():
        coverage_pct = info["coverage"] * 100
        found = ", ".join(info["terms_found"][:5])
        logger.info(f"  {domain}: {coverage_pct:.0f}% ({found})")

    # Save corpus
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_abstracts, f, indent=2, ensure_ascii=False)
    logger.info(f"\nCorpus saved to: {output_path}")

    # Save statistics
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    # Convert Counter most_common tuples to serializable format
    stats["top_tokens"] = [{"token": t, "count": c} for t, c in stats["top_tokens"]]
    for domain_info in stats["domain_coverage"].values():
        domain_info["coverage"] = round(domain_info["coverage"], 3)

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"Statistics saved to: {stats_path}")

    logger.info(f"\n{'=' * 60}")
    logger.info("Corpus build complete!")
    logger.info("=" * 60)

    return 0 if len(all_abstracts) >= 20 else 1
