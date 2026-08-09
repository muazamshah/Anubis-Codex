import { Github, ExternalLink } from 'lucide-react';
import Badge from './common/Badge';
import StatusIndicator from './common/StatusIndicator';
import { getLanguageColor, getLanguageDisplayName } from '../utils/languageUtils';

/**
 * RepositoryHeader - Compact professional repository header with metadata.
 */
const RepositoryHeader = ({ repository, metadata, fileCount, indexing }) => {
  const repoName = repository?.name || 'Unknown Repository';
  const owner = repository?.owner || 'unknown';
  const repoUrl = repository?.url || `https://github.com/${owner}/${repoName}`;
  const languages = metadata?.languages || [];
  const isIndexed = indexing?.chunks_created > 0 || indexing?.vector_db_updated;

  return (
    <div style={{ padding: 'var(--space-3) var(--space-4)', borderBottom: '1px solid var(--border)', background: 'rgba(var(--surface-rgb, 16, 19, 32), 0.3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
        {/* Left: Repo info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '2.25rem', height: '2.25rem', flexShrink: 0, borderRadius: 'var(--radius-lg)', background: 'var(--accent-soft)', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
            <Github size={18} className="text-accent" />
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <h2 className="text-primary font-semibold" style={{ fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{repoName}</h2>
              <a
                href={repoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-tertiary"
                style={{ flexShrink: 0, transition: 'color var(--transition)' }}
                aria-label="View on GitHub"
              >
                <ExternalLink size={14} />
              </a>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: '0.125rem' }}>
              <span className="text-secondary" style={{ fontSize: '0.75rem' }}>{owner}</span>
              {languages.length > 0 && (
                <>
                  <span className="text-tertiary">•</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    {languages.slice(0, 3).map((lang) => (
                      <div key={lang} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                        <span
                          style={{ width: '0.5rem', height: '0.5rem', borderRadius: '50%', backgroundColor: getLanguageColor(lang) }}
                        />
                        <span className="text-secondary" style={{ fontSize: '0.6875rem' }}>
                          {getLanguageDisplayName(lang)}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Right: Status and file count */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexShrink: 0 }}>
          <StatusIndicator
            status={isIndexed ? 'completed' : 'idle'}
            label={isIndexed ? 'Indexed' : 'Not Indexed'}
            showDot={true}
            size="sm"
          />
          <span className="text-tertiary" style={{ fontSize: '0.75rem' }}>
            {fileCount} {fileCount === 1 ? 'file' : 'files'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RepositoryHeader;