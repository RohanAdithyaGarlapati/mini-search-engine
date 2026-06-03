"""
Pydantic models — defines request and response shapes for all API endpoints.
These act as automatic validation + documentation for FastAPI.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Request Models ──────────────────────────────────────────────

class IndexRequest(BaseModel):
    """Request body for POST /index — add a document."""
    id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full document text")
    url: Optional[str] = Field("", description="Source URL (optional)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "doc_10",
                "title": "Introduction to FastAPI",
                "content": "FastAPI is a modern Python web framework for building APIs.",
                "url": "https://fastapi.tiangolo.com"
            }
        }
    }


# ── Response Models ─────────────────────────────────────────────

class SearchResult(BaseModel):
    """A single search result."""
    doc_id: str
    title: str
    snippet: str
    url: str
    score: float


class SearchResponse(BaseModel):
    """Response for GET /search."""
    query: str
    total_results: int
    results: list[SearchResult]


class IndexResponse(BaseModel):
    """Response for POST /index."""
    success: bool
    doc_id: str
    message: str


class DeleteResponse(BaseModel):
    """Response for DELETE /document/{doc_id}."""
    success: bool
    doc_id: str
    message: str


class StatsResponse(BaseModel):
    """Response for GET /stats."""
    total_documents: int
    vocabulary_size: int
    average_doc_length: float
    index_file_exists: bool
