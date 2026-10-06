"""Era orchestration and atomic recovery for the complete BHL analysis."""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeAlias
from core.provenance import analysis_signature, records_sha256

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
logger = logging.getLogger(__name__)


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"Nonfinite checkpoint value: {value}")


def _load_checkpoint(path: Path, fingerprint: str) -> JsonObject | None:
    """Read a completed matching era; fail on corrupt matching evidence."""
    if not path.exists():
        return None
    payload = json.loads(path.read_text(), parse_constant=_reject_nonfinite)
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid checkpoint object: {path.name}")
    if payload.get('schema') != 1 or payload.get('fingerprint') != fingerprint:
        return None
    result = payload.get('result')
    if (not isinstance(result, dict) or set(result) != {'era', 'terms', 'skipped'}
            or payload.get('result_sha256') != records_sha256([result])):
        raise ValueError(f"BHL checkpoint content changed: {path.name}")
    return result


def _save_checkpoint(path: Path, fingerprint: str, result: JsonObject) -> None:
    """Publish a completed era atomically; partial computations are never saved."""
    payload = {'schema': 1, 'fingerprint': fingerprint, 'result': result,
               'result_sha256': records_sha256([result])}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                   allow_nan=False) + '\n')
    temporary.replace(path)


def build_artifact(
    data_dir: Path,
    records: list[JsonObject] | None = None,
    checkpoint_dir: Path | None = None,
) -> JsonObject:
    """Build the era-stratified artifact dict for the BHL corpus.

    Per era, ``analyze_era_stack`` adds the ``extraction`` /
    ``entropy`` / ``framing`` sections; degenerate eras omit those
    sections and record the omission in the artifact-level
    ``skipped`` list.  The ``terms_per_10k``/``domains_per_10k``/
    ``terms`` sections are unchanged (backward compatible).

    Args:
        data_dir: Corpus directory with ``bhl_shard_*.json`` files.
        records: Pre-loaded records (loaded from ``data_dir`` when
            ``None``).
        checkpoint_dir: Optional local recovery directory. Completed era results
            bind ordered inputs, implementation/resources and development bounds.

    Returns:
        Artifact dict: ``{"layer": "bhl_historical", "generated",
        "source", "eras", "terms", "skipped"}``.
    """
    from .bhl_analysis import (ERA_KEYS, OCR_MIN_TERM_FREQUENCY, ENTROPY_TOP_TERMS,
                               analyze_eras, analyze_era_stack, load_corpus_records_for_analysis,
                               stack_character_budget, select_stack_records)
    signature = analysis_signature()
    if records is None:
        records = load_corpus_records_for_analysis(data_dir)
    vocabulary_source = "analysis.term_extraction.TerminologyExtractor.DOMAIN_SEEDS"
    eras_terms = analyze_eras([])
    eras = eras_terms["eras"]
    skipped: list[dict[str, str]] = []
    for era in ERA_KEYS:
        era_records = [r for r in records if r.get("era") == era]
        if not era_records:
            skipped.append(
                {
                    "kind": "era_stack",
                    "era": era,
                    "reason": (
                        "no documents in era; extraction/entropy/framing "
                        "sections omitted"
                    ),
                }
            )
            continue
        budget = stack_character_budget()
        fingerprint = records_sha256([era, era_records, signature, budget])
        checkpoint = checkpoint_dir / (era + '.json') if checkpoint_dir is not None else None
        result = _load_checkpoint(checkpoint, fingerprint) if checkpoint is not None else None
        if result is None:
            logger.info('Computing historical era %s (%d documents)', era, len(era_records))
            literal = analyze_eras(era_records)
            stack_records = select_stack_records(era_records, budget) if budget is not None else era_records
            stack = analyze_era_stack(stack_records)
            era_data = literal['eras'][era]
            era_data['stack_coverage'] = {
                'documents_available': len(era_records),
                'documents_analyzed': len(stack_records),
                'characters_available': sum(len(r.get('full_text') or '') for r in era_records),
                'characters_analyzed': sum(len(r.get('full_text') or '') for r in stack_records),
                'character_budget': budget,
                'selection': 'all stored era documents' if budget is None else 'deterministic dyadic traversal; whole documents; output in shard order',
            }
            for key in ('extraction', 'entropy', 'framing'):
                era_data[key] = stack[key]
            result = {'era': era_data, 'terms': literal['terms'], 'skipped': stack['skipped']}
            if checkpoint is not None:
                _save_checkpoint(checkpoint, fingerprint, result)
                logger.info('Saved completed historical era %s', era)
        else:
            logger.info('Resuming verified historical era %s', era)
        eras[era] = result['era']
        for term, values in result['terms'].items():
            eras_terms['terms'][term][era] = values[era]
            eras_terms['terms'][term]['total'] += values['total']
        skipped.extend({**entry, 'era': era} for entry in result['skipped'])
    return {
        "corpus_fingerprint": {"record_count": len(records),
                               "records_sha256": records_sha256(records),
                               "analysis_signature": signature,
                               "stack_character_budget": stack_character_budget()},
        "layer": "bhl_historical",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "data_dir": str(data_dir),
            "documents": len(records),
            "harvester": "src/data/bhl_corpus.py",
            "vocabulary_source": vocabulary_source,
            "matching": (
                "deterministic token-window matching over normalized "
                "(NFC, lowercased, hyphen-break-joined) OCR text; "
                "frequencies per 10k era tokens, 4 decimals"
            ),
            "ocr_cleaning": (
                "clean_ocr_text: normalize_text (NFC fold, hyphen-break "
                "join, whitespace collapse) plus removal of OCR speck "
                "tokens (standalone digit runs and single letters); "
                "domain seed terms are >=2 alphabetic characters, so "
                "these tokens carry no vocabulary signal"
            ),
            "stack": {
                "extraction": (
                    "TerminologyExtractor over clean_ocr_text output, "
                    f"min_frequency={OCR_MIN_TERM_FREQUENCY} per era"
                ),
                "entropy": (
                    "DomainAnalyzer.quantify_ambiguity_metrics over the "
                    f"top {ENTROPY_TOP_TERMS} most frequent extracted "
                    "terms per era (documented bounded fraction); only "
                    "status=ok terms report entropy"
                ),
                "framing": (
                    "occurrence-context anthropomorphic framing "
                    "proportions via the public "
                    "LinguisticFeatureExtractor API (+-3-token window); "
                    "vocabulary reconstructed from the extraction token "
                    "stream and cross-checked"
                ),
            },
        },
        **eras_terms,
        "skipped": skipped,
    }
