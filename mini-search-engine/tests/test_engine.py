"""Unit tests for the core search engine components."""

import pytest
from engine.tokenizer import Tokenizer
from engine.index import InvertedIndex
from engine.ranker import BM25Ranker
from engine.query_parser import QueryParser


@pytest.fixture
def sample_index():
    """Build a small index for testing."""
    index = InvertedIndex()
    index.add_document("d1", "Python Machine Learning", "Python is great for machine learning algorithms", "")
    index.add_document("d2", "Django Web Framework", "Django is a Python web framework for rapid development", "")
    index.add_document("d3", "Deep Learning Neural Networks", "Neural networks and deep learning transform AI", "")
    return index


def test_tokenizer_basic():
    t = Tokenizer()
    tokens = t.tokenize("Machine Learning is Amazing!")
    assert "machin" in tokens  # stemmed
    assert "is" not in tokens  # stopword removed


def test_tokenizer_removes_stopwords():
    t = Tokenizer()
    tokens = t.tokenize("the quick brown fox")
    assert "the" not in tokens


def test_index_adds_document(sample_index):
    assert sample_index.num_docs == 3
    assert "d1" in sample_index.documents


def test_index_postings(sample_index):
    t = Tokenizer()
    term = t.tokenize("python")[0]
    postings = sample_index.get_postings(term)
    assert "d1" in postings
    assert "d2" in postings


def test_bm25_ranks_correctly(sample_index):
    ranker = BM25Ranker(sample_index)
    results = ranker.search("python machine learning", top_k=3)
    assert results[0]["doc_id"] == "d1"  # most relevant doc should rank first
    assert results[0]["score"] > results[-1]["score"]


def test_query_parser_simple():
    parser = QueryParser()
    result = parser.parse("machine learning")
    assert result["type"] == "simple"
    assert len(result["tokens"]) > 0


def test_query_parser_boolean():
    parser = QueryParser()
    result = parser.parse("python AND django")
    assert result["type"] == "boolean"
    assert len(result["must"]) > 0


def test_query_parser_phrase():
    parser = QueryParser()
    result = parser.parse('"machine learning"')
    assert result["type"] == "phrase"
    assert "machine learning" in result["phrases"]