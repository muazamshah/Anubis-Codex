import { Bot, User, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

/**
 * ChatMessage - Renders a single chat message (user or assistant) with
 * markdown support, syntax highlighting, and clickable source references.
 */
const ChatMessage = ({ message, onSourceClick }) => {
  const isUser = message.role === 'user';

  // Markdown components for syntax highlighting
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
    <div
      className={`chat-row ${isUser ? 'user' : 'assistant'}`}
    >
      {!isUser && (
        <div className="chat-avatar bot">
          <Bot size={16} />
        </div>
      )}

      <div
        className={isUser ? 'chat-message-user' : 'chat-message-assistant'}
      >
        {isUser ? (
          <p style={{ lineHeight: '1.625' }}>{message.content}</p>
        ) : (
          <>
            <div style={{ lineHeight: '1.625' }}>
              <ReactMarkdown components={markdownComponents}>
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div className="chat-sources">
                <p className="chat-sources-title">
                  Sources
                </p>
                <div className="chat-sources-list">
                  {message.sources.slice(0, 5).map((source, idx) => (
                    <button
                      key={idx}
                      onClick={() =>
                        onSourceClick &&
                        onSourceClick(source.file, source.start_line, source.end_line)
                      }
                      className="source-chip"
                      title={source.file}
                    >
                      <FileText size={12} />
                      <span className="source-file">{source.file}</span>
                      {source.start_line && source.end_line && (
                        <span className="source-lines">
                          {source.start_line}–{source.end_line}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {isUser && (
        <div className="chat-avatar user">
          <User size={16} />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;