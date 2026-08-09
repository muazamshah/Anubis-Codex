import { Bot, MessageSquare, Trash2 } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import QuickQuestions from './QuickQuestions';
import Button from './common/Button';

/**
 * ChatInterface - The main chat container with messages, input, and quick questions.
 */
const ChatInterface = ({
  messages,
  isChatLoading,
  chatError,
  chatMessage,
  onChatMessageChange,
  onSendMessage,
  onClearChat,
  onQuickQuestion,
  onSourceClick,
  isIndexed,
}) => {
  const handleSend = () => {
    if (chatMessage.trim() && !isChatLoading) {
      onSendMessage(chatMessage);
    }
  };

  const handleClear = () => {
    if (onClearChat) onClearChat();
  };

  const handleQuickQuestion = (question) => {
    if (onQuickQuestion) onQuickQuestion(question);
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="chat-header-title">
            <MessageSquare size={16} />
            <h2>Repository Intelligence</h2>
          </div>
          {isIndexed && (
            <span className="status-badge success">
              <span className="status-badge-dot animate-pulse-subtle" />
              Ready
            </span>
          )}
        </div>
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            icon={Trash2}
            onClick={handleClear}
            aria-label="Clear conversation"
          />
        )}
      </div>

      {/* Messages */}
      <div className="chat-messages">
        <div className="chat-messages-inner">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="chat-empty-icon-wrap">
                <div className="chat-empty-glow">
                  <div className="chat-empty-glow-inner" />
                </div>
                <div className="chat-empty-icon">
                  <Bot size={24} />
                </div>
              </div>
              <h3 className="chat-empty-title">
                ANUBIS CODEX
              </h3>
              <p className="chat-empty-desc">
                Ask me anything about this repository.
              </p>
              <p className="chat-empty-hint">
                I can explain code, architecture, and answer technical questions.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className="animate-fadeIn"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                <ChatMessage message={message} onSourceClick={onSourceClick} />
              </div>
            ))
          )}

          {isChatLoading && (
            <div className="chat-loading animate-fadeIn">
              <div className="chat-avatar bot">
                <Bot size={14} />
              </div>
              <div className="chat-loading-bubble">
                <div className="chat-loading-dots">
                  <div className="chat-loading-dot" />
                  <div className="chat-loading-dot" />
                  <div className="chat-loading-dot" />
                </div>
              </div>
            </div>
          )}

          {chatError && (
            <div className="chat-error animate-fadeIn">
              <div className="chat-error-inner">
                <span className="chat-error-label">Error:</span>
                <span>{chatError}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Questions (only when no messages) */}
      {messages.length === 0 && isIndexed && (
        <div className="quick-questions">
          <QuickQuestions
            onQuestionClick={handleQuickQuestion}
            disabled={isChatLoading}
          />
        </div>
      )}

      {/* Chat Input */}
      <ChatInput
        value={chatMessage}
        onChange={onChatMessageChange}
        onSend={handleSend}
        onClear={handleClear}
        loading={isChatLoading}
        messageCount={messages.length}
      />
    </div>
  );
};

export default ChatInterface;