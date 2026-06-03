export default function ResultCard({ result, rank }) {
  return (
    <div className="result-card">
      <div className="result-header">
        <span className="result-rank">#{rank}</span>
        <span className="result-title">{result.title}</span>
        <span className="result-score">{result.score}</span>
      </div>
      <div className="result-snippet" dangerouslySetInnerHTML={{ __html: result.snippet }} />
      <div className="result-footer">
        {result.url ? (
          <a href={result.url} className="result-url" target="_blank" rel="noopener noreferrer">
            {result.url}
          </a>
        ) : (
          <span className="result-url">-</span>
        )}
        <span className="result-id">{result.doc_id}</span>
      </div>
    </div>
  );
}