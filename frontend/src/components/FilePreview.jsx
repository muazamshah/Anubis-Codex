import { FileCode, X } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getHighlightLanguage, getLanguageDisplayName } from '../utils/languageUtils';

/**
 * FilePreview - Code preview panel with file name, language, path, line numbers,
 * and syntax highlighting.
 */
const FilePreview = ({ file, onClose, darkMode }) => {
  if (!file) return null;

  const language = file.language || 'text';
  const highlightLang = getHighlightLanguage(language);
  const displayName = getLanguageDisplayName(language);
  const content = file.content || '// No content available';

  return (
    <div className="file-preview">
      {/* Header */}
      <div className="file-preview-header">
        <div className="file-preview-info">
          <div className="file-preview-icon">
            <FileCode size={16} />
          </div>
          <div style={{ minWidth: 0 }}>
            <h3 className="file-preview-name">{file.name}</h3>
            <p className="file-preview-path">{file.path}</p>
          </div>
        </div>
        <div className="file-preview-actions">
          <span className="file-preview-lang">
            {displayName}
          </span>
          <button
            onClick={onClose}
            className="icon-btn"
            aria-label="Close file preview"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="file-preview-content">
        <SyntaxHighlighter
          language={highlightLang}
          style={oneDark}
          showLineNumbers
          wrapLines
          PreTag="div"
          className="code-block-enhanced"
          customStyle={{
            backgroundColor: 'transparent',
            fontSize: '0.75rem',
            lineHeight: '1.6',
            padding: '1rem',
            margin: 0,
            borderRadius: 0,
            border: 'none',
            height: '100%',
          }}
        >
          {content}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

export default FilePreview;