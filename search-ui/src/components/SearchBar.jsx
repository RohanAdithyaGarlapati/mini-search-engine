export default function SearchBar({ query, setQuery, onSearch, loading }) {
  const hints = ["machine learning", "python AND django", "neural networks", "machine learning NOT python"];
  const handleKey = (e) => { if (e.key === "Enter" && !loading) onSearch(); };
  return (
    <div>
      <div className="search-wrap">
        <input className="search-input" type="text" placeholder="Try: python AND django" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={handleKey} autoFocus />
        <button className="search-btn" onClick={onSearch} disabled={loading || !query.trim()}>{loading ? "..." : "Search"}</button>
      </div>
      <div className="hints">
        {hints.map((h) => (<button key={h} className="hint-chip" onClick={() => setQuery(h)}>{h}</button>))}
      </div>
    </div>
  );
}