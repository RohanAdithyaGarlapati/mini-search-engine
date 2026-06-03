import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import SearchBar from "./components/SearchBar";
import ResultCard from "./components/ResultCard";
import StatsBar from "./components/StatsBar";

const API = "https://mini-search-engine-api.onrender.com";

export default function App() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searched, setSearched] = useState(false);

    useEffect(() => {
        axios.get(`${API}/stats`)
            .then((res) => setStats(res.data))
            .catch(() => { });
    }, []);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setError(null);
        setSearched(true);

        try {
            const res = await axios.get(`${API}/search`, {
                params: { q: query, top_k: 10 },
            });
            setResults(res.data);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Could not reach the search engine. Is the FastAPI server running?"
            );
            setResults(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app">
            <header className="header">
                <h1 className="header-title">
                    Mini<span>Search</span>
                </h1>
                <p className="header-sub">
                    BM25-powered full-text search · inverted index · boolean queries
                </p>
            </header>

            <SearchBar
                query={query}
                setQuery={setQuery}
                onSearch={handleSearch}
                loading={loading}
            />

            <StatsBar stats={stats} />

            {error && <div className="state-error">⚠ {error}</div>}

            {loading && (
                <div className="state-loading">
                    <div className="spinner" />
                    <div>Searching index...</div>
                </div>
            )}

            {!loading && results && (
                <>
                    <div className="results-meta">
                        <span className="results-count">
                            <strong>{results.total_results}</strong> results for "{results.query}"
                        </span>
                    </div>

                    {results.results.length === 0 ? (
                        <div className="no-results">
                            No documents matched your query. Try different terms.
                        </div>
                    ) : (
                        results.results.map((r, i) => (
                            <ResultCard key={r.doc_id} result={r} rank={i + 1} />
                        ))
                    )}
                </>
            )}

            {!loading && !searched && (
                <div className="state-empty">
                    <span className="big">_</span>
                    type a query above to search
                    <br />
                    supports AND · OR · NOT · "phrase search"
                </div>
            )}
        </div>
    );
}