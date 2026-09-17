"""Build the entomological literature corpus for Ento-Linguistic analysis.

Business logic for stage 01: targeted PubMed retrieval, deduplication, corpus
validation statistics, and persistence to ``data/corpus/abstracts.json`` plus
``output/data/corpus_statistics.json``. Invoked via the thin orchestrator
``scripts/01_build_corpus.py``.
"""
import hashlib
import json
import logging
import re
import time
from pathlib import Path

from data.literature_mining import (
    Publication,
    PubMedMiner,
    mine_corpus_growth,
)

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


def _text_key(abstract: str) -> str:
    """Dedupe key for an abstract: first 100 chars, lowercased, collapsed.

    Args:
        abstract: Abstract text.

    Returns:
        Normalized 100-character prefix used as the corpus text key.
    """
    return re.sub(r"\s+", " ", abstract[:100].lower())


def fetch_publications_for_query(
    miner: PubMedMiner, query: str, max_per_query: int = 50
) -> list[Publication]:
    """Fetch full publication records for a single PubMed query.

    Args:
        miner: Initialized PubMedMiner instance.
        query: PubMed query string.
        max_per_query: Maximum number of results to fetch for this query.

    Returns:
        List of Publication objects (empty list on failure).
    """
    try:
        pmids = miner.search(query, max_results=max_per_query)
        results = miner.fetch_publications(pmids)
        logger.info(f"  Fetched {len(results)} publications for query: {query}")
        return results
    except Exception as e:
        logger.warning(f"  Query failed ({query}): {e}")
        return []


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
    pubs = fetch_publications_for_query(miner, query, max_per_query)
    abstracts = [p.abstract for p in pubs if p.abstract]
    logger.info(f"  {len(abstracts)} with abstracts for query: {query}")
    return abstracts


def _load_provenance(path: Path) -> dict:
    """Load the provenance sidecar file, returning a valid empty shell.

    Args:
        path: Path to ``provenance.json``.

    Returns:
        Dict with at least a ``records`` mapping (sha256 -> sidecar dict).
    """
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("records"), dict):
                return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Unreadable provenance file {path}: {e}")
    return {"records": {}}


def _provenance_sidecar(pub: Publication, query: str) -> dict:
    """Build a provenance sidecar entry for a publication.

    Args:
        pub: Publication record with metadata.
        query: Name of the query that produced the record.

    Returns:
        Dict with pmid, doi, title, year, journal, and query keys.
    """
    return {
        "pmid": pub.pmid,
        "doi": pub.doi,
        "title": pub.title,
        "year": pub.year,
        "journal": pub.journal,
        "query": query,
    }


def _serialize_stats(stats: dict) -> dict:
    """Convert in-memory statistics into the serializable on-disk schema.

    Args:
        stats: Statistics dict from :func:`validate_corpus`.

    Returns:
        Stats with tuple counters converted to JSON-friendly structures.
    """
    # Contract schema consumed by the manuscript variable producers
    # (core.manuscript_variables and the PDF renderer): type_token_ratio
    # and most_common_tokens are load-bearing template inputs. The
    # extra diagnostic fields below are additive.
    stats["top_tokens"] = [{"token": t, "count": c} for t, c in stats["top_tokens"]]
    stats["most_common_tokens"] = [
        [entry["token"], entry["count"]] for entry in stats["top_tokens"]
    ]
    for domain_info in stats["domain_coverage"].values():
        domain_info["coverage"] = round(domain_info["coverage"], 3)
    return stats


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
    # Contract schema consumed by the manuscript variable producers
    # (core.manuscript_variables and the PDF renderer): type_token_ratio
    # and most_common_tokens are load-bearing template inputs. The
    # extra diagnostic fields below are additive.
    stats = {
        "total_abstracts": len(abstracts),
        "total_tokens": len(words),
        "unique_tokens": len(word_counts),
        "total_characters": len(all_text),
        "avg_token_length": (len(all_text) / len(words)) if words else 0.0,
        "type_token_ratio": (len(word_counts) / len(words)) if words else 0.0,
        "avg_abstract_length_tokens": len(words) / len(abstracts) if abstracts else 0,
        "domain_coverage": domain_coverage,
        "most_common_tokens": word_counts.most_common(30),
        "top_tokens": word_counts.most_common(30),
    }

    return stats


def _known_corpus_state(
    output_path: Path, provenance_path: Path
) -> tuple[list[str], dict, set, set]:
    """Load the on-disk corpus and its dedupe state.

    Args:
        output_path: Path to ``abstracts.json``.
        provenance_path: Path to ``provenance.json``.

    Returns:
        Tuple of (existing abstracts, provenance dict, known PMIDs,
        known text keys).
    """
    existing: list[str] = []
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, list):
            existing = [a for a in loaded if isinstance(a, str) and a.strip()]
    prov = _load_provenance(provenance_path)
    known_pmids = {
        entry.get("pmid")
        for entry in prov["records"].values()
        if isinstance(entry, dict) and entry.get("pmid")
    }
    known_text_keys = {_text_key(a) for a in existing}
    return existing, prov, known_pmids, known_text_keys


def _run_grow(
    output_path: Path,
    stats_path: Path,
    max_per_query: int,
    target_new: int,
    since_pdat: str | None,
) -> int:
    """Append new unique growth-query records to the corpus.

    Args:
        output_path: Path to ``abstracts.json``.
        stats_path: Path to the statistics output file.
        max_per_query: Maximum PMIDs searched per growth query.
        target_new: Stop once this many new records were collected.
        since_pdat: Optional PubMed date window lower bound.

    Returns:
        Process exit code: 0 when the corpus holds at least 20 abstracts.
    """
    provenance_path = output_path.parent / "provenance.json"
    existing, prov, known_pmids, known_text_keys = _known_corpus_state(
        output_path, provenance_path
    )
    records = prov["records"]

    logger.info(
        f"Growing corpus at {output_path} "
        f"({len(existing)} abstracts, {len(records)} provenance records)"
    )
    logger.info(
        f"Max per query: {max_per_query}; target new: {target_new}; "
        f"since_pdat: {since_pdat}"
    )

    # Exclusion set: PMIDs in provenance sidecars plus the seen-PMID ledger
    # from previous growth runs (every PMID a search has ever surfaced).
    ledger_pmids = set(prov.get("seen_pmids", []))
    pubs, hit_counts, pmid_to_query = mine_corpus_growth(
        max_per_query=max_per_query,
        target_new=target_new,
        since_pdat=since_pdat,
        exclude_pmids=known_pmids | ledger_pmids,
        exclude_text_keys=known_text_keys,
    )
    for name, hits in hit_counts.items():
        logger.info(f"  {name}: {hits} hits")

    # Belt-and-braces dedupe against the on-disk corpus state; mine_corpus_growth
    # already excludes, this guards against races and provenance gaps.
    new_pubs: list[Publication] = []
    for pub in pubs:
        if not pub.abstract or not pub.abstract.strip():
            continue
        abstract = pub.abstract.strip()
        key = _text_key(abstract)
        if key in known_text_keys:
            continue
        if pub.pmid and pub.pmid in known_pmids:
            continue
        known_text_keys.add(key)
        if pub.pmid:
            known_pmids.add(pub.pmid)
        pub.abstract = abstract
        new_pubs.append(pub)

    merged = existing + [pub.abstract for pub in new_pubs]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    logger.info(
        f"Corpus saved to: {output_path} "
        f"({len(existing)} existing + {len(new_pubs)} new = {len(merged)})"
    )

    # Provenance sidecars for the appended records (same schema as the
    # 2026-09-15 growth): sha256(abstract) -> metadata dict. The seen-PMID
    # ledger records every PMID surfaced by this run's searches (collected
    # or not) so a repeated run with the same search surface appends nothing.
    for pub in new_pubs:
        if not pub.pmid:
            continue
        digest = hashlib.sha256(pub.abstract.encode("utf-8")).hexdigest()
        records.setdefault(
            digest, _provenance_sidecar(pub, pmid_to_query.get(pub.pmid, "unknown"))
        )
    prov["seen_pmids"] = sorted(set(prov.get("seen_pmids", [])) | set(pmid_to_query))
    with open(provenance_path, "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2, ensure_ascii=False)
    logger.info(
        f"Provenance saved to: {provenance_path} "
        f"({len(records)} records, {len(prov['seen_pmids'])} seen PMIDs)"
    )

    stats = _serialize_stats(validate_corpus(merged))
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"Statistics saved to: {stats_path}")

    return 0 if len(merged) >= 20 else 1


def main(project_root: Path | None = None, argv: list[str] | None = None) -> int:
    """Build, grow, or refresh statistics for the entomological corpus.

    Modes:
        * Cached (default): when the corpus already holds at least 20
          abstracts, only the statistics file is refreshed; nothing is
          fetched.
        * ``--force`` (and any fetch when the corpus is below 20 records):
          re-fetch the base ``ENTOMOLOGY_QUERIES`` and merge the results
          into the existing corpus with dedupe (PMID + 100-char text key);
          existing records are never dropped.
        * ``--grow``: run ``mine_corpus_growth`` over all
          ``CORPUS_GROWTH_QUERIES`` and append new unique records to the
          corpus, tracking provenance sidecars. Idempotent: a second run
          adds nothing.

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
        default=None,
        help="Maximum results per query (default: 50, or 1000 with --grow)",
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
        help="Re-fetch the base queries and merge into the existing corpus "
        "(dedupe by PMID + text key; existing records are never dropped)",
    )
    parser.add_argument(
        "--grow",
        action="store_true",
        help="Grow the corpus by running mine_corpus_growth over all "
        "CORPUS_GROWTH_QUERIES and appending new unique records",
    )
    parser.add_argument(
        "--target-new",
        type=int,
        default=1000,
        help="With --grow: stop once this many new records were collected "
        "(default: 1000)",
    )
    parser.add_argument(
        "--since-pdat",
        type=str,
        default=None,
        help="With --grow: PubMed date window lower bound, e.g. 2020/01/01",
    )
    args = parser.parse_args(argv)

    max_per_query = (
        args.max_per_query if args.max_per_query is not None else (1000 if args.grow else 50)
    )

    # Resolve output paths
    output_path = (
        Path(args.output) if args.output else root / "data" / "corpus" / "abstracts.json"
    )
    stats_path = (
        Path(args.stats_output)
        if args.stats_output
        else root / "output" / "data" / "corpus_statistics.json"
    )
    provenance_path = output_path.parent / "provenance.json"

    logger.info("=" * 60)
    logger.info("Ento-Linguistics Corpus Builder")
    logger.info("=" * 60)

    if args.grow:
        return _run_grow(
            output_path=output_path,
            stats_path=stats_path,
            max_per_query=max_per_query,
            target_new=args.target_new,
            since_pdat=args.since_pdat,
        )

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
            stats = _serialize_stats(validate_corpus(all_abstracts))
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Statistics saved to: {stats_path}")
            logger.info("Corpus build complete (cached)")
            return 0

    logger.info(f"Max per query: {max_per_query}")
    logger.info(f"Queries: {len(ENTOMOLOGY_QUERIES)}")
    logger.info(f"Output: {output_path}")

    # Load existing corpus state; fetched records are merged in, never
    # overwriting what is already on disk.
    existing, prov, known_pmids, known_text_keys = _known_corpus_state(
        output_path, provenance_path
    )
    records = prov["records"]
    before = len(existing)

    miner = PubMedMiner()
    for i, query in enumerate(ENTOMOLOGY_QUERIES, 1):
        logger.info(f"\n--- Query {i}/{len(ENTOMOLOGY_QUERIES)} ---")
        pubs = fetch_publications_for_query(miner, query, max_per_query)
        for pub in pubs:
            if not pub.abstract or not pub.abstract.strip():
                continue
            abstract = pub.abstract.strip()
            key = _text_key(abstract)
            if key in known_text_keys:
                continue
            if pub.pmid and pub.pmid in known_pmids:
                continue
            known_text_keys.add(key)
            if pub.pmid:
                known_pmids.add(pub.pmid)
                digest = hashlib.sha256(abstract.encode("utf-8")).hexdigest()
                records.setdefault(digest, _provenance_sidecar(pub, query))
            existing.append(abstract)

        # Rate limit between queries
        if i < len(ENTOMOLOGY_QUERIES):
            time.sleep(1.0)

    all_abstracts = existing
    logger.info(f"\n{'=' * 60}")
    logger.info(
        f"Corpus merge: {before} existing + {len(all_abstracts) - before} new "
        f"= {len(all_abstracts)} total"
    )

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

    # Save provenance sidecars for newly appended records
    with open(provenance_path, "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2, ensure_ascii=False)
    logger.info(f"Provenance saved to: {provenance_path}")

    # Save statistics
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(_serialize_stats(stats), f, indent=2, ensure_ascii=False)
    logger.info(f"Statistics saved to: {stats_path}")

    logger.info(f"\n{'=' * 60}")
    logger.info("Corpus build complete!")
    logger.info("=" * 60)

    return 0 if len(all_abstracts) >= 20 else 1
