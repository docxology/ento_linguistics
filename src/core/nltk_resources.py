"""Content custody for the English NLTK inputs used by the paper pipeline."""
from __future__ import annotations

import hashlib
import codecs
from pathlib import Path
from typing import BinaryIO, TypedDict
from zipfile import ZipFile

from nltk.data import ZipFilePathPointer, find


class NltkResourceFingerprints(TypedDict):
    """Selected input hashes; machine-specific installation paths are omitted."""

    punkt_tab_english: str
    stopwords_english: str
    wordnet: str


def _resource_sha256(resource: str) -> str:
    """Hash a selected file/directory or the archive NLTK actually opens."""
    pointer = find(resource)
    match pointer:
        case ZipFilePathPointer():
            members = [entry for entry in pointer.zipfile.infolist()
                       if not entry.is_dir() and
                       (entry.filename == pointer.entry or
                        (pointer.entry.endswith("/") and entry.filename.startswith(pointer.entry)))]
            if not any(entry.file_size for entry in members):
                raise FileNotFoundError(f"Empty NLTK resource: {resource}")
            has_content = False
            with ZipFile(pointer.zipfile.filename) as archive:
                for entry in members:
                    with archive.open(entry.filename) as stream:
                        if _has_content(stream):
                            has_content = True
                            break
            if not has_content:
                raise FileNotFoundError(f"Empty NLTK resource: {resource}")
            path = Path(pointer.zipfile.filename)
            archive_backed = True
        case _:
            path = Path(str(pointer))
            archive_backed = False
    paths = sorted(path.rglob("*")) if path.is_dir() else [path]
    files = [entry for entry in paths if entry.is_file()]
    if not files:
        raise FileNotFoundError(f"Empty NLTK resource: {resource}")
    if not archive_backed:
        has_content = False
        for entry in files:
            with entry.open("rb") as stream:
                if _has_content(stream):
                    has_content = True
                    break
        if not has_content:
            raise FileNotFoundError(f"Empty NLTK resource: {resource}")
    digest = hashlib.sha256()
    for entry in files:
        name = str(entry.relative_to(path)) if path.is_dir() else path.name
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(entry.stat().st_size.to_bytes(8, "big"))
        with entry.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def _has_content(stream: BinaryIO) -> bool:
    """Detect meaningful UTF-8 text in extracted files or archive members."""
    decoder = codecs.getincrementaldecoder("utf-8")()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        if decoder.decode(chunk).strip():
            return True
    return bool(decoder.decode(b"", final=True).strip())


def nltk_resource_fingerprints() -> NltkResourceFingerprints:
    """Bind the selected English tokenizer, stopwords and WordNet bytes.

    Uses NLTK's actual data search order. Missing/empty resources raise;
    no downloads or fallback replacements occur here. ZIP inputs bind the
    entire selected archive; unpacked inputs bind ordered relative files.
    Open Multilingual WordNet is not used by English lemmatization.

    Example:
        >>> len(nltk_resource_fingerprints()["wordnet"])
        64
    """
    return {
        "punkt_tab_english": _resource_sha256("tokenizers/punkt_tab/english/"),
        "stopwords_english": _resource_sha256("corpora/stopwords/english"),
        "wordnet": _resource_sha256("corpora/wordnet/"),
    }
