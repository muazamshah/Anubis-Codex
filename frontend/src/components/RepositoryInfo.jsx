import {
  BarChart3,
  Database,
  HardDrive,
  Layers,
  Search,
  Server,
  Zap,
} from 'lucide-react';
import Badge from './common/Badge';
import StatusIndicator from './common/StatusIndicator';
import { getLanguageColor, getLanguageDisplayName } from '../utils/languageUtils';

/**
 * RepositoryInfo - Right sidebar with repository overview, AI analysis stats,
 * quick questions, and search interface.
 */
const RepositoryInfo = ({
  repository,
  metadata,
  fileCount,
  languages,
  indexing,
  vectorStats,
  cacheStats,
  onQuickQuestion,
  onSearch,
  searchText,
  onSearchTextChange,
  searchResults,
  isSearching,
  isIndexed,
}) => {
  const quickQuestions = [
    'Explain this repository',
    'How does it work?',
    'Explain the architecture',
    'What are the main components?',
    'Which technologies are used?',
  ];

  const handleQuickQuestion = (question) => {
    if (onQuickQuestion) onQuickQuestion(question);
  };

  return (
    <div className="repo-info">
      {/* Repository Overview */}
      <div className="compact-card">
        <div className="section-header">
          <Database size={14} />
          Overview
        </div>
        <div className="repo-info-section">
          {metadata?.description && (
            <div>
              <p className="repo-description">{metadata.description}</p>
            </div>
          )}
          <div className="repo-languages">
            {languages?.map((lang) => (
              <span
                key={lang}
                className="repo-language"
              >
                <span
                  className="repo-language-dot"
                  style={{ backgroundColor: getLanguageColor(lang) }}
                />
                {getLanguageDisplayName(lang)}
              </span>
            ))}
            {(!languages || languages.length === 0) && (
              <span className="text-tertiary" style={{ fontSize: '0.6875rem' }}>Unknown</span>
            )}
          </div>
          <div className="repo-file-count">
            {fileCount} {fileCount === 1 ? 'file' : 'files'}
          </div>
        </div>
      </div>

      {/* AI Analysis */}
      <div className="compact-card">
        <div className="section-header">
          <Zap size={14} />
          AI Analysis
        </div>
        <div className="repo-info-section">
          <div className="stat-row">
            <span className="stat-label">Files</span>
            <span className="stat-value">{fileCount}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Chunks</span>
            <span className="stat-value">
              {indexing?.chunks_created || 0}
            </span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Embeddings</span>
            <span className="stat-value">
              {indexing?.embeddings_generated || 0}
            </span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Status</span>
            <StatusIndicator
              status={isIndexed ? 'completed' : 'idle'}
              label={isIndexed ? 'Ready' : 'Not ready'}
              showDot={true}
              size="sm"
            />
          </div>
        </div>
      </div>

      {/* Quick Questions */}
      <div className="compact-card">
        <div className="section-header">
          <Layers size={14} />
          Quick Questions
        </div>
        <div className="quick-question-list">
          {quickQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => handleQuickQuestion(q)}
              className="quick-question-item"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Search */}
      <div className="compact-card">
        <div className="section-header">
          <Search size={14} />
          Search
        </div>
        <div className="search-section">
          <div className="input-wrapper">
            <span className="input-icon">
              <Search size={14} />
            </span>
            <input
              type="text"
              value={searchText}
              onChange={(e) => onSearchTextChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && onSearch()}
              placeholder="Search repository..."
              className="input-field"
              disabled={!isIndexed}
            />
          </div>
          <button
            onClick={onSearch}
            disabled={isSearching || !searchText.trim() || !isIndexed}
            className="btn btn-primary btn-sm"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="search-results">
              <div className="search-results-count">
                {searchResults.length} results
              </div>
              {searchResults.map((result, index) => (
                <div
                  key={index}
                  className="search-result-item"
                >
                  <div className="search-result-header">
                    <span className="search-result-file">
                      {result.metadata?.file_path || 'Unknown file'}
                    </span>
                    <span className="search-result-score">
                      {result.score ? (result.score * 100).toFixed(0) : 0}%
                    </span>
                  </div>
                  <p className="search-result-content">
                    {result.content?.slice(0, 150) || 'No content available'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="compact-card">
        <div className="section-header">
          <Server size={14} />
          System
        </div>
        <div className="repo-info-section">
          <div className="stat-row">
            <span className="stat-label">Vector DB</span>
            <StatusIndicator
              status={vectorStats?.status === 'active' ? 'completed' : 'idle'}
              label={vectorStats?.status || 'Unknown'}
              showDot={true}
              size="sm"
            />
          </div>
          <div className="stat-row">
            <span className="stat-label">Cache</span>
            <span className="stat-value">
              {cacheStats?.total_keys || 0} keys
            </span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Vectors</span>
            <span className="stat-value">
              {vectorStats?.count || 0}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RepositoryInfo;