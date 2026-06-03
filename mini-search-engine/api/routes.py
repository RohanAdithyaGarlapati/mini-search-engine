"""
API Routes — all endpoint definitions.
Each route validates input via Pydantic, calls the engine, returns structured response.
"""

import os
from fastapi import APIRouter, HTTPException, Query

from engine.index import InvertedIndex
from engine.ranker import BM25Ranker
from engine.snippets import SnippetExtractor
from engine.query_parser import QueryParser
from api.models import (
    IndexRequest,
    IndexResponse,
    SearchResponse,
    SearchResult,
    DeleteResponse,
    StatsResponse,
)

router = APIRouter()

# ── Shared engine state (injected from app.py) ──────────────────
_index: InvertedIndex = None
_ranker: BM25Ranker = None
_snippet_extractor: SnippetExtractor = SnippetExtractor()
_query_parser: QueryParser = QueryParser()


def init_engine(index: InvertedIndex, ranker: BM25Ranker):
    """Initialize shared engine instances from app.py startup."""
    global _index, _ranker
    _index = index
    _ranker = ranker


# ── Endpoints ───────────────────────────────────────────────────

@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results to return"),
):
    """
    Search the index and return ranked results with snippets.

    - Supports simple queries: `python tutorial`
    - Supports boolean: `python AND django`, `ML NOT java`
    - Supports phrases: `"machine learning"`
    """
    if _index is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")

    raw_results = _ranker.search(q, top_k=top_k)

    results = []
    for r in raw_results:
        snippet = _snippet_extractor.extract(r["content"], q)
        results.append(SearchResult(
            doc_id=r["doc_id"],
            title=r["title"],
            snippet=snippet,
            url=r["url"],
            score=r["score"],
        ))

    return SearchResponse(
        query=q,
        total_results=len(results),
        results=results,
    )


@router.post("/index", response_model=IndexResponse)
def index_document(request: IndexRequest):
    """
    Add a new document to the search index.
    If the document ID already exists it will be re-indexed.
    """
    if _index is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")

    # Check for duplicate
    if request.id in _index.documents:
        return IndexResponse(
            success=False,
            doc_id=request.id,
            message=f"Document '{request.id}' already exists. Use a unique ID.",
        )

    _index.add_document(
        doc_id=request.id,
        title=request.title,
        content=request.content,
        url=request.url or "",
    )

    return IndexResponse(
        success=True,
        doc_id=request.id,
        message=f"Document '{request.id}' indexed successfully.",
    )


@router.delete("/document/{doc_id}", response_model=DeleteResponse)
def delete_document(doc_id: str):
    """
    Remove a document from the index by its ID.
    Note: removes from document store and postings lists.
    """
    if _index is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")

    if doc_id not in _index.documents:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")

    # Remove from document store
    del _index.documents[doc_id]

    # Remove from doc_lengths
    if doc_id in _index.doc_lengths:
        del _index.doc_lengths[doc_id]

    # Remove from all postings lists
    terms_to_clean = []
    for term, postings in _index.index.items():
        if doc_id in postings:
            del postings[doc_id]
        if not postings:
            terms_to_clean.append(term)

    # Clean up empty terms
    for term in terms_to_clean:
        del _index.index[term]

    _index.num_docs = len(_index.documents)

    return DeleteResponse(
        success=True,
        doc_id=doc_id,
        message=f"Document '{doc_id}' removed from index.",
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats():
    """Return current index statistics."""
    if _index is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")

    return StatsResponse(
        total_documents=_index.num_docs,
        vocabulary_size=len(_index.index),
        average_doc_length=round(_index.average_doc_length(), 2),
        index_file_exists=os.path.exists("data/index.json"),
    )
