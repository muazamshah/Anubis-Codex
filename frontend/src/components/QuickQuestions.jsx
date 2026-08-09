import { Layers } from 'lucide-react';

/**
 * QuickQuestions - Buttons for common questions that send to the chat system.
 */
const QuickQuestions = ({ onQuestionClick, disabled }) => {
  const questions = [
    'Explain this repository',
    'How does it work?',
    'Explain the architecture',
    'What are the main components?',
    'Which technologies are used?',
  ];

  return (
    <div>
      <div className="section-header">
        <Layers size={14} />
        Quick Questions
      </div>
      <div className="quick-questions-grid">
        {questions.map((q, i) => (
          <button
            key={i}
            onClick={() => onQuestionClick(q)}
            disabled={disabled}
            className="quick-question-btn"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickQuestions;