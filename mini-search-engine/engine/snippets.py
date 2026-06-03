"""
Snippet extractor — pulls relevant excerpt from document content
and highlights matching query terms.

Example output:
    "...Python is widely used in <mark>machine learning</mark> and
    <mark>data</mark> science workflows..."
"""

import re
from engine.tokenizer import Tokenizer


class SnippetExtractor:
    """
    Extracts a relevant text snippet from a document and highlights
    query terms within it.
    """

    def __init__(self, snippet_length: int = 200):
        """
        Args:
            snippet_length: Max number of characters in the snippet.
        """
        self.snippet_length = snippet_length
        self.tokenizer = Tokenizer()

    def extract(self, content: str, query: str) -> str:
        """
        Find the most relevant section of content for the query
        and return it with query terms highlighted.

        Args:
            content: Full document text.
            query:   Raw search query string.

        Returns:
            HTML snippet string with <mark> tags around matches.
        """
        if not content or not query:
            return content[:self.snippet_length] + "..."

        # Find best window in content that contains most query words
        best_start = self._find_best_window(content, query)

        # Extract snippet around best position
        start = max(0, best_start - 20)
        end = min(len(content), start + self.snippet_length)
        snippet = content[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        # Highlight query terms
        snippet = self._highlight(snippet, query)

        return snippet

    def _find_best_window(self, content: str, query: str) -> int:
        """
        Find the character position in content where the most
        query terms appear close together.

        Args:
            content: Document text.
            query:   Raw query string.

        Returns:
            Best starting character position.
        """
        query_words = [w.lower() for w in query.split() if len(w) > 2]
        content_lower = content.lower()

        best_pos = 0
        best_count = 0

        for word in query_words:
            pos = content_lower.find(word)
            if pos == -1:
                continue

            # Count how many query words appear near this position
            window = content_lower[max(0, pos - 100): pos + 200]
            count = sum(1 for w in query_words if w in window)

            if count > best_count:
                best_count = count
                best_pos = pos

        return best_pos

    def _highlight(self, text: str, query: str) -> str:
        """
        Wrap query terms in <mark> tags for frontend highlighting.

        Args:
            text:  Snippet text.
            query: Raw query string.

        Returns:
            Text with <mark>term</mark> wrapping matched words.
        """
        # Get unique query words (ignore short words and operators)
        skip = {"and", "or", "not"}
        query_words = [
            w for w in query.lower().split()
            if len(w) > 2 and w not in skip
        ]

        for word in query_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            text = pattern.sub(lambda m: f"<mark>{m.group()}</mark>", text)

        return text
