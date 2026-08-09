import { Send, Trash2 } from 'lucide-react';
import Button from './common/Button';

/**
 * ChatInput - Large modern input at the bottom of the chat with send and clear buttons.
 * Supports Enter to send.
 */
const ChatInput = ({
  value,
  onChange,
  onSend,
  onClear,
  loading,
  messageCount,
}) => {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="chat-input-area">
      <div className="chat-input-row">
        <div className="chat-input-field">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about this repository…"
            className="textarea-field"
            rows={1}
            minRows={1}
            maxRows={5}
            disabled={loading}
            aria-label="Ask a question about the repository"
          />
        </div>
        {messageCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            icon={Trash2}
            onClick={onClear}
            disabled={loading}
            aria-label="Clear conversation"
          />
        )}
        <Button
          variant="primary"
          size="sm"
          icon={Send}
          loading={loading}
          disabled={loading || !value.trim()}
          onClick={onSend}
          aria-label="Send message"
          className="btn-enhanced"
        />
      </div>
      <div className="chat-input-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
};

export default ChatInput;