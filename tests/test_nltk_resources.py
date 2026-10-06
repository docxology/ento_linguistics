"""Resource-custody controls with real NLTK files and fresh subprocesses."""
import shutil
import subprocess
import sys
from zipfile import ZipFile
from pathlib import Path

import nltk
import pytest


def _copy_resources(target: Path) -> None:
    """Copy the currently selected English inputs to an isolated data root."""
    for resource in ("tokenizers/punkt_tab/english/", "corpora/stopwords/english"):
        source = Path(str(nltk.data.find(resource)))
        destination = target / resource
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copyfile(source, destination)
    wordnet = nltk.data.find("corpora/wordnet/")
    destination = target / "corpora"
    if isinstance(wordnet, nltk.data.ZipFilePathPointer):
        shutil.copyfile(wordnet.zipfile.filename, destination / "wordnet.zip")
    else:
        shutil.copytree(str(wordnet), destination / "wordnet")


def _signature(data_root: Path) -> str:
    command = (
        "import nltk,sys; nltk.data.path[:]=[sys.argv[1]]; "
        "from core.provenance import analysis_signature; print(analysis_signature())"
    )
    return subprocess.check_output(
        [sys.executable, "-c", command, str(data_root)], text=True
    ).strip()


def test_analysis_signature_changes_when_active_tokenizer_changes(tmp_path: Path) -> None:
    # Given a real installed tokenizer, dictionary and stopword corpus.
    _copy_resources(tmp_path)
    before = _signature(tmp_path)
    # When one selected tokenizer input changes, without source or lock edits.
    source = tmp_path / "tokenizers/punkt_tab/english/abbrev_types.txt"
    source.write_bytes(source.read_bytes() + b"\nento_custody_control\n")
    # Then the cached-analysis identity must change.
    assert _signature(tmp_path) != before


def test_analysis_signature_rejects_missing_resources(tmp_path: Path) -> None:
    # Given no NLTK resource files in the explicitly selected data root.
    # When a receipt identity is requested, then missing inputs fail visibly.
    with pytest.raises(subprocess.CalledProcessError):
        _signature(tmp_path)


def test_analysis_signature_rejects_empty_tokenizer_directory(tmp_path: Path) -> None:
    # Given an installed-looking resource directory with no model files.
    (tmp_path / "tokenizers/punkt_tab/english").mkdir(parents=True)
    # When NLTK finds the directory, then receipt creation still fails.
    with pytest.raises(subprocess.CalledProcessError):
        _signature(tmp_path)


@pytest.mark.parametrize("contents", [b"", b" \n\t\n", "\u00a0\u2003".encode()])
def test_analysis_signature_rejects_zero_byte_stopwords(tmp_path: Path, contents: bytes) -> None:
    # Given actual tokenizer/dictionary files but an empty selected stopword file.
    _copy_resources(tmp_path)
    (tmp_path / "corpora/stopwords/english").write_bytes(contents)
    # When identifying the analysis inputs, then empty contents fail visibly.
    with pytest.raises(subprocess.CalledProcessError):
        _signature(tmp_path)


def test_analysis_signature_rejects_empty_wordnet_archive(tmp_path: Path) -> None:
    # Given real English tokenizer/stopwords and an archive with only a directory.
    _copy_resources(tmp_path)
    unpacked = tmp_path / "corpora/wordnet"
    if unpacked.exists():
        unpacked.rename(tmp_path / "corpora/wordnet-unused")
    with ZipFile(tmp_path / "corpora/wordnet.zip", "w") as archive:
        archive.writestr("wordnet/", b"")
    # When NLTK can find the archive directory, then absent model bytes still fail.
    with pytest.raises(subprocess.CalledProcessError):
        _signature(tmp_path)


def test_analysis_signature_rejects_whitespace_stopwords_in_zip(tmp_path: Path) -> None:
    # Given a selected archive-backed English file with no actual words.
    _copy_resources(tmp_path)
    (tmp_path / "corpora/stopwords").rename(tmp_path / "corpora/stopwords-unused")
    with ZipFile(tmp_path / "corpora/stopwords.zip", "w") as archive:
        archive.writestr("stopwords/english", "\u00a0 \n\t")
    # When its container has bytes, then empty selected payload still fails.
    with pytest.raises(subprocess.CalledProcessError):
        _signature(tmp_path)
