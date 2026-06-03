"""
Tokenizer module — handles text preprocessing pipeline.
Responsibilities: lowercasing, punctuation removal, stopword filtering, stemming.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data on first run
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)


class Tokenizer:
    """
    Preprocesses raw text into clean, stemmed tokens.

    Pipeline:
        raw text → lowercase → remove punctuation → tokenize
                 → remove stopwords → stem
    """

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))

    def tokenize(self, text: str) -> list[str]:
        """
        Convert raw text into a list of clean, stemmed tokens.

        Args:
            text: Raw input string.

        Returns:
            List of stemmed, filtered tokens.
        """
        # Lowercase
        text = text.lower()

        # Remove punctuation and special characters, keep letters/numbers/spaces
        text = re.sub(r"[^a-z0-9\s]", "", text)

        # Split into tokens
        tokens = text.split()

        # Remove stopwords and stem
        tokens = [
            self.stemmer.stem(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]

        return tokens

    def tokenize_query(self, query: str) -> list[str]:
        """
        Tokenize a search query — same pipeline as document tokenization
        so query terms match index terms correctly.

        Args:
            query: Raw search query string.

        Returns:
            List of processed query tokens.
        """
        return self.tokenize(query)