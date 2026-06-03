"""
BM25 Ranking module — scores documents against a query.

BM25 Formula:
    score(D, Q) = Σ IDF(qi) * (freq(qi,D) * (k1+1)) / (freq(qi,D) + k1*(1 - b + b*|D|/avgdl))

    Parameters:
        k1 = 1.5  (term frequency saturation)
        b  = 0.75 (length normalization)
"""

from engine.index import InvertedIndex
from engine.tokenizer import Tokenizer


class BM25Ranker:
    """
    Scores and ranks documents using the BM25 algorithm.
    """

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.tokenizer = Tokenizer()
        self.k1 = k1
        self.b = b

    def score(self, doc_id: str, query_tokens: list) -> float:
        score = 0.0
        doc_len = self.index.doc_lengths.get(doc_id, 0)
        avg_dl = self.index.average_doc_length()

        for term in query_tokens:
            postings = self.index.get_postings(term)
            if doc_id not in postings:
                continue

            freq = postings[doc_id]["freq"]
            idf = self.index.idf(term)

            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * (doc_len / avg_dl))

            score += idf * (numerator / denominator)

        return score

    def search(self, query: str, top_k: int = 10) -> list:
        query_tokens = self.tokenizer.tokenize_query(query)

        if not query_tokens:
            return []

        candidate_docs = set()
        for term in query_tokens:
            postings = self.index.get_postings(term)
            candidate_docs.update(postings.keys())

        scored = []
        for doc_id in candidate_docs:
            bm25_score = self.score(doc_id, query_tokens)
            doc = self.index.documents[doc_id]

            scored.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "content": doc["content"],
                "url": doc["url"],
                "score": round(bm25_score, 4),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]