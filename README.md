# MiniSearch

A full-text search engine I built from scratch. No Elasticsearch, no Solr, no search libraries doing the heavy lifting. Just an inverted index, BM25 ranking, a FastAPI backend, and a React frontend talking to each other.

Live demo: https://mini-search-engine-eta.vercel.app  
API docs: https://mini-search-engine-api.onrender.com/docs

---

## Why I built this

I got tired of using search as a black box. You drop Elasticsearch into a project, configure a few settings, and it just works. But I never really understood what was happening underneath.

So I decided to build one from the ground up. Every piece of it. The tokenizer, the inverted index, the ranking function, the query parser, and the API layer. No shortcuts in the core engine.

It turns out there is a lot going on inside a search engine that looks simple from the outside.

---

## What it does

- Takes documents and builds an inverted index that maps every term to the documents it appears in, along with how often and where
- Ranks results using BM25, which is the same ranking algorithm Elasticsearch uses under the hood
- Handles boolean queries like `python AND django` or `machine learning NOT java`
- Handles phrase queries like `"neural networks"` where word order matters
- Pulls out a relevant snippet from each matching document and highlights the query terms in it
- Wraps everything in a REST API built with FastAPI
- Displays results in a React frontend that shows scores, snippets, and source links

---

## Tech stack

| Layer | Tech |
|---|---|
| Core engine | Python, no search library dependencies |
| Tokenization | NLTK for stemming and stopword removal |
| Web framework | FastAPI with Uvicorn |
| Data validation | Pydantic v2 |
| Frontend | React with Vite |
| HTTP client | Axios |
| Containerization | Docker and Docker Compose |
| Backend hosting | Render |
| Frontend hosting | Vercel |

---

## How the ranking works

BM25 (Best Match 25) is an improvement over classical TF-IDF. It fixes two problems that TF-IDF has.

The first problem is term frequency saturation. In TF-IDF, a document where a keyword appears 100 times scores 10x higher than one where it appears 10 times. That is not always meaningful. BM25 puts a ceiling on how much repeated occurrences can boost a score. Past a certain point, seeing a word more times stops mattering as much.

The second problem is document length. A 200-word document that mentions "machine learning" three times is probably more focused on that topic than a 5000-word document that also mentions it three times. BM25 normalizes term frequency against the average document length across the corpus.

The formula looks like this:

```
score(D, Q) = sum of [ IDF(qi) x (freq(qi,D) x (k1+1)) / (freq(qi,D) + k1 x (1 - b + b x |D|/avgdl)) ]

k1 = 1.5   controls term frequency saturation
b  = 0.75  controls how much document length affects the score
```

---

## Project structure

```
search-engine/
├── mini-search-engine/
│   ├── engine/
│   │   ├── tokenizer.py         text preprocessing pipeline
│   │   ├── index.py             inverted index with term frequency and positions
│   │   ├── ranker.py            BM25 scoring and candidate retrieval
│   │   ├── query_parser.py      simple, boolean, and phrase query parsing
│   │   └── snippets.py          snippet extraction with keyword highlighting
│   ├── api/
│   │   ├── models.py            Pydantic request and response schemas
│   │   └── routes.py            FastAPI endpoint definitions
│   ├── data/
│   │   └── sample_docs.json     50 seeded documents with real URLs
│   ├── tests/
│   │   └── test_engine.py       unit tests for the core engine
│   ├── app.py                   FastAPI entry point
│   └── requirements.txt
├── search-ui/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── StatsBar.jsx
│   │   ├── App.jsx
│   │   └── App.css
│   └── vite.config.js
└── docker-compose.yml
```

---

## Running it locally

You need Python 3.10+ and Node.js 22.12+ installed. Docker is optional but makes it much easier.

### With Docker

```bash
git clone https://github.com/RohanAdithyaGarlapati/mini-search-engine.git
cd mini-search-engine
docker-compose up --build
```

Frontend runs at http://localhost:5173  
API docs at http://localhost:8000/docs

### Without Docker

```bash
# Start the backend
cd mini-search-engine
python -m venv venv
venv\Scripts\activate        # on Windows
source venv/bin/activate     # on Mac or Linux
pip install -r requirements.txt
uvicorn app:app --reload

# Start the frontend in a second terminal
cd search-ui
npm install
npm run dev
```

---

## API reference

| Method | Endpoint | What it does |
|---|---|---|
| GET | /search?q=...&top_k=10 | Search and return ranked results |
| POST | /index | Add a new document to the index |
| DELETE | /document/{id} | Remove a document from the index |
| GET | /stats | Returns index size and vocabulary stats |

Example response from /search:

```json
{
  "query": "machine learning",
  "total_results": 3,
  "results": [
    {
      "doc_id": "doc_1",
      "title": "Machine Learning - Google Developers",
      "snippet": "<mark>Machine</mark> <mark>learning</mark> is a subfield of AI...",
      "url": "https://developers.google.com/machine-learning/crash-course",
      "score": 5.6028
    }
  ]
}
```

Supported query syntax:

```
machine learning              simple query
python AND django             boolean AND
machine learning NOT java     boolean NOT
flask OR django               boolean OR
"neural networks"             exact phrase match
```

---

## Tests

```bash
cd mini-search-engine
pytest tests/ -v
```

The test suite covers tokenizer behavior, index correctness, BM25 ranking order, and query parser output for all supported query types.

---

## What I learned

Building the inverted index itself was not the hard part. The interesting problems came later.

Getting BM25 tuning to feel right took some reading. The default k1=1.5 and b=0.75 parameters come from decades of information retrieval research and they do hold up well in practice, but understanding why those values were chosen made the whole thing click.

The query parser had more edge cases than I expected. Operator precedence in boolean queries, making sure stemming is consistent between indexing and querying, and getting phrase search to actually use positional data from the index all had bugs that only showed up in the unit tests.

If I were to take this further, I would add persistent index storage with SQLite so the index survives restarts, build a simple web crawler to ingest real documents, and experiment with semantic reranking using sentence embeddings on top of the BM25 first pass.

---