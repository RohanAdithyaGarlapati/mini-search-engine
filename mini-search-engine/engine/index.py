"""
Inverted Index module — core data structure of the search engine.

Structure:
    {
        "term": {
            "doc_id_1": {"freq": 3, "positions": [2, 7, 15]},
            "doc_id_2": {"freq": 1, "positions": [4]},
        }
    }
"""

import json
import math
from collections import defaultdict
from engine.tokenizer import Tokenizer


class InvertedIndex:
    """
    Builds and manages an inverted index over a document corpus.

    Supports:
        - Document ingestion
        - Term frequency + position tracking
        - TF-IDF weight computation
        - Index persistence (save/load JSON)
    """

    def __init__(self):
        self.tokenizer = Tokenizer()

        # Core index: term → {doc_id → {freq, positions}}
        self.index: dict[str, dict[str, dict]] = defaultdict(dict)

        # Document store: doc_id → {title, content, url}
        self.documents: dict[str, dict] = {}

        # Document lengths (number of tokens per doc) — needed for BM25
        self.doc_lengths: dict[str, int] = {}

        # Total number of documents in the corpus
        self.num_docs: int = 0

    def add_document(self, doc_id: str, title: str, content: str, url: str = "") -> None:
        """
        Ingest a document into the index.

        Args:
            doc_id:   Unique document identifier.
            title:    Document title.
            content:  Full document text.
            url:      Optional source URL.
        """
        # Store raw document
        self.documents[doc_id] = {
            "title": title,
            "content": content,
            "url": url,
        }

        # Tokenize full text (title weighted 2x for better relevance)
        full_text = f"{title} {title} {content}"
        tokens = self.tokenizer.tokenize(full_text)

        # Track document length
        self.doc_lengths[doc_id] = len(tokens)
        self.num_docs += 1

        # Build index entries with positions
        for position, term in enumerate(tokens):
            if doc_id not in self.index[term]:
                self.index[term][doc_id] = {"freq": 0, "positions": []}

            self.index[term][doc_id]["freq"] += 1
            self.index[term][doc_id]["positions"].append(position)

    def get_postings(self, term: str) -> dict[str, dict]:
        """
        Retrieve all documents containing a given term.

        Args:
            term: A single (already stemmed) query term.

        Returns:
            Dict of {doc_id: {freq, positions}} or empty dict.
        """
        return self.index.get(term, {})

    def document_frequency(self, term: str) -> int:
        """Number of documents containing the term."""
        return len(self.index.get(term, {}))

    def average_doc_length(self) -> float:
        """Average token count across all indexed documents."""
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)

    def idf(self, term: str) -> float:
        """
        Compute Inverse Document Frequency for a term.
        Uses smoothed IDF: log((N - df + 0.5) / (df + 0.5) + 1)

        Args:
            term: Query term.

        Returns:
            IDF score (float).
        """
        df = self.document_frequency(term)
        if df == 0:
            return 0.0
        return math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)

    def save(self, filepath: str) -> None:
        """
        Persist the index to a JSON file.

        Args:
            filepath: Output file path.
        """
        data = {
            "index": {term: postings for term, postings in self.index.items()},
            "documents": self.documents,
            "doc_lengths": self.doc_lengths,
            "num_docs": self.num_docs,
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Index saved to {filepath}")

    def load(self, filepath: str) -> None:
        """
        Load a previously saved index from JSON.

        Args:
            filepath: Path to saved index file.
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        self.index = defaultdict(dict, data["index"])
        self.documents = data["documents"]
        self.doc_lengths = data["doc_lengths"]
        self.num_docs = data["num_docs"]
        print(f"Index loaded from {filepath} — {self.num_docs} documents")