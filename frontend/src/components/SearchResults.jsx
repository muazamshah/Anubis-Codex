import { BarChart3, FileText, Search } from 'lucide-react';

/**
 * SearchResults - Displays repository search results with file path, line number,
 * and content preview.
 */
const SearchResults = ({ results, query, isSearching, onResultClick }) => {
  if (!results || results.length === 0) {
    return (
      <div className="empty-state">
        {isSearching ? 'Searching...' : 'No search results. Enter a query to search.'}
      </div>
    );
  }

  return (
    <div style={{ padding: 'var(--space-4)' }}>
      <div style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <BarChart3 size={18} className="text-secondary" />
          <h3 className="text-secondary font-semibold" style={{ fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Search Results
          </h3>
        </div>
        <span className="text-tertiary" style={{ fontSize: '0.75rem' }}>
          {results.length} results for "{query}"
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {results.map((result, index) => {
          const metadata = result.metadata || {};
          const filePath = metadata.file_path || 'Unknown file';
          const startLine = metadata.start_line || 0;
          const endLine = metadata.end_line || 0;
          const score = result.score ? (result.score * 100).toFixed(1) : '0';
          const content = result.content || '';

          return (
            <div
              key={index}
              className="search-result-item"
              style={{ cursor: 'pointer' }}
              onClick={() => onResultClick && onResultClick(result)}
            >
              <div className="search-result-header" style={{ marginBottom: 'var(--space-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <FileText size={14} className="text-tertiary" />
                  <span className="search-result-file">
                    {filePath}
                  </span>
                </div>
                <span className="search-result-score">
                  {score}%
                </span>
              </div>
              {startLine && endLine && (
                <p className="text-tertiary" style={{ fontSize: '0.75rem', marginBottom: 'var(--space-1)' }}>
                  Lines {startLine}–{endLine}
                </p>
              )}
              <p className="search-result-content">
                {content.slice(0, 250)}
                {content.length > 250 && '...'}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SearchResults;