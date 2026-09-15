"""Tests for data loader module."""

import json
import pytest
from data.loader import DataLoader

@pytest.fixture
def loader():
    """Create DataLoader instance."""
    return DataLoader()

def test_loader_initialization():
    """Test DataLoader initialization."""
    loader = DataLoader()
    assert loader.data_root.exists()
    assert loader.data_root.name == "data"

def test_load_corpus_exists(loader):
    """Test loading existing corpus."""
    # We know corpus/abstracts.json should exist as we created it
    texts = loader.load_corpus("corpus/abstracts.json")
    assert isinstance(texts, list)
    assert len(texts) > 0
    assert all(isinstance(t, str) for t in texts)

def test_load_corpus_not_found(loader):
    """Test loading non-existent corpus."""
    with pytest.raises(FileNotFoundError):
        loader.load_corpus("non_existent.json")

def test_loader_custom_data_root(tmp_path):
    """Test DataLoader with custom data_root."""
    loader = DataLoader(data_root=tmp_path)
    assert loader.data_root == tmp_path


def test_save_and_load_custom_corpus(loader, tmp_path):
    """Test saving and loading custom corpus."""
    # Temporarily override data_root to tmp_path for this test
    loader.data_root = tmp_path

    texts = ["Abstract 1", "Abstract 2"]
    filename = "custom_corpus.json"

    # Save
    path = loader.save_corpus(texts, filename)
    assert path.exists()

    # Load
    loaded_texts = loader.load_corpus(filename)
    assert loaded_texts == texts


def test_load_corpus_dict_format(tmp_path):
    """Test loading corpus in dict format with 'abstracts' key."""
    loader = DataLoader(data_root=tmp_path)
    corpus_file = tmp_path / "dict_corpus.json"
    corpus_file.write_text(json.dumps({"abstracts": ["text1", "text2", "text3"]}))

    texts = loader.load_corpus("dict_corpus.json")
    assert texts == ["text1", "text2", "text3"]


def test_load_corpus_invalid_format(tmp_path):
    """Test loading corpus with invalid format raises ValueError."""
    loader = DataLoader(data_root=tmp_path)
    bad_file = tmp_path / "bad_corpus.json"
    bad_file.write_text(json.dumps({"wrong_key": "not a list"}))

    with pytest.raises(ValueError, match="Invalid corpus format"):
        loader.load_corpus("bad_corpus.json")


class TestConvertCorpus:
    """Tests for the convert_corpus fallback/external-source paths."""

    def test_convert_corpus_missing_input_returns_zero(self, tmp_path):
        """convert_corpus returns 0 when the input file does not exist."""
        from data.loader import convert_corpus

        missing_input = tmp_path / "does_not_exist.json"
        output = tmp_path / "out.json"

        count = convert_corpus(input_path=missing_input, output_path=output)

        assert count == 0
        assert not output.exists()

    def test_convert_corpus_writes_formatted_abstracts(self, tmp_path):
        """convert_corpus formats each publication as 'Title. Authors (Year). Abstract'."""
        from data.loader import convert_corpus

        corpus = {
            "publications": [
                {
                    "title": "Ant Colony Organization",
                    "authors": ["Wilson, E.O.", "Hölldobler, B."],
                    "year": 1990,
                    "abstract": "A study of ant colony structure.",
                },
                {
                    "title": "No Abstract Paper",
                    "authors": ["Doe, J."],
                    "year": 2001,
                    "abstract": "",
                },
                {
                    "title": "Whitespace Abstract Paper",
                    "authors": [],
                    "year": "",
                    "abstract": "   ",
                },
            ]
        }
        input_file = tmp_path / "literature_corpus.json"
        input_file.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
        output_file = tmp_path / "abstracts.json"

        count = convert_corpus(input_path=input_file, output_path=output_file)

        assert count == 1
        written = json.loads(output_file.read_text(encoding="utf-8"))
        assert written == [
            "Ant Colony Organization. Wilson, E.O., Hölldobler, B. (1990). "
            "A study of ant colony structure."
        ]

    def test_convert_corpus_without_publications_key(self, tmp_path):
        """convert_corpus writes an empty list when the input has no publications."""
        from data.loader import convert_corpus

        input_file = tmp_path / "empty_corpus.json"
        input_file.write_text(json.dumps({"metadata": "no publications here"}))
        output_file = tmp_path / "abstracts.json"

        count = convert_corpus(input_path=input_file, output_path=output_file)

        assert count == 0
        assert json.loads(output_file.read_text(encoding="utf-8")) == []

    def test_convert_corpus_abstract_fallback_when_none(self, tmp_path):
        """convert_corpus skips publications whose abstract is None."""
        from data.loader import convert_corpus

        corpus = {"publications": [{"title": "T", "authors": [], "abstract": None}]}
        input_file = tmp_path / "null_abstract.json"
        input_file.write_text(json.dumps(corpus))
        output_file = tmp_path / "abstracts.json"

        count = convert_corpus(input_path=input_file, output_path=output_file)

        assert count == 0
        assert json.loads(output_file.read_text(encoding="utf-8")) == []
