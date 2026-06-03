"""
FastAPI application entry point.

Startup sequence:
    1. Load sample documents
    2. Build inverted index
    3. Initialize BM25 ranker
    4. Register API routes
    5. Serve on http://localhost:8000
"""

import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine.index import InvertedIndex
from engine.ranker import BM25Ranker
from api.routes import router, init_engine


def load_and_index_documents(filepath: str) -> InvertedIndex:
    """Load documents from JSON and build the inverted index."""
    index = InvertedIndex()

    with open(filepath, "r") as f:
        documents = json.load(f)

    for doc in documents:
        index.add_document(
            doc_id=doc["id"],
            title=doc["title"],
            content=doc["content"],
            url=doc.get("url", ""),
        )

    print(f"[startup] Indexed {index.num_docs} documents")
    print(f"[startup] Vocabulary: {len(index.index)} terms")
    return index


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build index and initialize engine on startup."""
    index = load_and_index_documents("data/sample_docs.json")
    ranker = BM25Ranker(index)
    init_engine(index, ranker)
    print("[startup] Search engine ready")
    yield
    print("[shutdown] Search engine stopped")


# ── App setup ───────────────────────────────────────────────────

app = FastAPI(
    title="Mini Search Engine",
    description="A BM25-powered search engine built from scratch",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "Mini Search Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/search", "/index", "/stats", "/document/{id}"]
    }
