import { BookOpen, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

/**
 * ReadmeViewer - Beautiful Markdown viewer for README content.
 */
const ReadmeViewer = ({ readme, onClose }) => {
  if (!readme) return null;

  const markdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : 'text';
      return !inline && match ? (
        <SyntaxHighlighter
          style={oneDark}
          language={language}
          PreTag="div"
          className="code-block-enhanced"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  };

  return (
    <div className="readme-viewer">
      {/* Header */}
      <div className="readme-header">
        <div className="readme-header-left">
          <div className="readme-header-icon">
            <BookOpen size={18} />
          </div>
          <h3 className="readme-title">README</h3>
        </div>
        <button
          onClick={onClose}
          className="icon-btn"
          aria-label="Close README viewer"
        >
          <X size={16} />
        </button>
      </div>

      {/* Content */}
      <div className="readme-content">
        <div className="markdown-content">
          <ReactMarkdown components={markdownComponents}>
            {readme}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default ReadmeViewer;