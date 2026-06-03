"""
Main entry point — demonstrates the full search engine pipeline.
Run this to verify the engine works before building the API layer.
"""

import json
from engine.index import InvertedIndex
from engine.ranker import BM25Ranker
from engine.query_parser import QueryParser


def load_documents(filepath: str) -> list[dict]:
    """Load sample documents from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def build_index(documents: list[dict]) -> InvertedIndex:
    """Ingest all documents into the inverted index."""
    index = InvertedIndex()
    for doc in documents:
        index.add_document(
            doc_id=doc["id"],
            title=doc["title"],
            content=doc["content"],
            url=doc["url"],
        )
    print(f"Indexed {index.num_docs} documents")
    print(f"Vocabulary size: {len(index.index)} unique terms")
    print(f"Average document length: {index.average_doc_length():.1f} tokens\n")
    return index


def main():
    # Step 1: Load documents
    documents = load_documents("data/sample_docs.json")

    # Step 2: Build inverted index
    index = build_index(documents)

    # Step 3: Initialize ranker and query parser
    ranker = BM25Ranker(index)
    parser = QueryParser()

    # Step 4: Run test queries
    test_queries = [
        "machine learning algorithms",
        "python web development",
        "neural networks deep learning",
        "python AND django",
        "machine learning NOT python",
    ]

    for query in test_queries:
        print(f"Query: '{query}'")
        parsed = parser.parse(query)
        print(f"  Type: {parsed['type']} | Tokens: {parsed['tokens']}")

        results = ranker.search(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['score']}] {result['title']}")
        print()

    # Step 5: Save index to disk
    index.save("data/index.json")


if __name__ == "__main__":
    main()