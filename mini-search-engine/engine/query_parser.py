"""
Query Parser module — handles advanced query syntax.

Supported syntax:
    - Simple:   python tutorial
    - AND:      python AND django
    - OR:       flask OR django
    - NOT:      python NOT javascript
    - Phrase:   "machine learning"
"""

import re
from engine.tokenizer import Tokenizer


class QueryParser:
    """
    Parses raw query strings into structured query objects.

    Handles boolean operators and phrase queries,
    returning a normalized form the ranker can process.
    """

    def __init__(self):
        self.tokenizer = Tokenizer()

    def parse(self, raw_query: str) -> dict:
        """
        Parse a raw query string into a structured query dict.

        Args:
            raw_query: User's input query string.

        Returns:
            Dict with keys:
                - type: "simple" | "boolean" | "phrase"
                - tokens: list of processed tokens
                - must:  terms that MUST appear (AND)
                - must_not: terms that must NOT appear (NOT)
                - should: terms that SHOULD appear (OR)
                - phrases: exact phrases to match
        """
        raw_query = raw_query.strip()

        # Detect phrase queries: "exact phrase"
        phrases = re.findall(r'"([^"]+)"', raw_query)
        raw_query_no_phrases = re.sub(r'"[^"]+"', "", raw_query)

        # Detect boolean operators
        has_boolean = any(op in raw_query.upper() for op in [" AND ", " OR ", " NOT "])

        if phrases and not has_boolean:
            return {
                "type": "phrase",
                "tokens": self.tokenizer.tokenize(raw_query_no_phrases),
                "phrases": phrases,
                "must": [],
                "must_not": [],
                "should": [],
            }

        if has_boolean:
            return self._parse_boolean(raw_query)

        # Simple query — just tokenize
        return {
            "type": "simple",
            "tokens": self.tokenizer.tokenize(raw_query),
            "phrases": [],
            "must": [],
            "must_not": [],
            "should": [],
        }

    def _parse_boolean(self, query: str) -> dict:
        """
        Parse boolean query into must / must_not / should buckets.

        Args:
            query: Raw query with AND/OR/NOT operators.

        Returns:
            Structured boolean query dict.
        """
        must = []
        must_not = []
        should = []

        # Split on boolean operators (case-insensitive)
        parts = re.split(r'\s+(AND|OR|NOT)\s+', query, flags=re.IGNORECASE)

        # First term is always a MUST
        if parts:
            tokens = self.tokenizer.tokenize(parts[0])
            must.extend(tokens)

        # Process operator + term pairs
        i = 1
        while i < len(parts) - 1:
            operator = parts[i].upper()
            term_tokens = self.tokenizer.tokenize(parts[i + 1])

            if operator == "AND":
                must.extend(term_tokens)
            elif operator == "OR":
                should.extend(term_tokens)
            elif operator == "NOT":
                must_not.extend(term_tokens)

            i += 2

        return {
            "type": "boolean",
            "tokens": must + should,
            "phrases": [],
            "must": must,
            "must_not": must_not,
            "should": should,
        }