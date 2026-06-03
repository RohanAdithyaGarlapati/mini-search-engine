export default function StatsBar({ stats }) {
  if (!stats) return null;
  return (
    <div className="stats-bar">
      <div className="stat-item"><span className="stat-label">Documents</span><span className="stat-value accent">{stats.total_documents}</span></div>
      <div className="stat-item"><span className="stat-label">Vocabulary</span><span className="stat-value">{stats.vocabulary_size} terms</span></div>
      <div className="stat-item"><span className="stat-label">Avg length</span><span className="stat-value">{stats.average_doc_length} tokens</span></div>
      <div className="stat-item"><span className="stat-label">Index</span><span className="stat-value">{stats.index_file_exists ? "persisted" : "in-memory"}</span></div>
    </div>
  );
}