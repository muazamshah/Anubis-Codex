import { Code, Github } from 'lucide-react';
import Button from './common/Button';

/**
 * LandingScreen - Beautiful centered landing page shown when no repository is loaded.
 */
const LandingScreen = ({ url, onUrlChange, onAnalyze, loading, error }) => {
  return (
    <div className="landing-screen">
      <div className="landing-container animate-fadeIn">
        <div className="surface-card shadow-soft-lg landing-card">
          <div className="landing-body">
            {/* Logo */}
            <div className="landing-logo-wrap">
              <div className="landing-logo">
                <Code size={24} />
              </div>
            </div>

            {/* Brand */}
            <div className="landing-brand">
              <h1 className="landing-title">
                ANUBIS CODEX
              </h1>
              <p className="landing-subtitle">
                GitHub Intelligence AI
              </p>
            </div>

            {/* Tagline */}
            <p className="landing-tagline">
              AI that understands GitHub repositories. Ask questions, explore code, and get insights.
            </p>

            {/* Input */}
            <div className="landing-input-wrap">
              <label htmlFor="repo-url" className="sr-only">
                GitHub repository URL
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <Github size={16} />
                </span>
                <input
                  id="repo-url"
                  type="url"
                  value={url}
                  onChange={(e) => onUrlChange(e.target.value)}
                  placeholder="Paste GitHub repository URL…"
                  className="input-field"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Analyze Button */}
            <Button
              variant="primary"
              size="md"
              icon={Github}
              loading={loading}
              disabled={loading || !url.trim()}
              onClick={onAnalyze}
              className="btn-block btn-enhanced"
            >
              {loading ? 'Analyzing Repository...' : 'Analyze Repository'}
            </Button>

            {/* Error */}
            {error && (
              <div className="landing-error animate-fadeIn">
                <div className="landing-error-inner">
                  <span className="landing-error-label">Error:</span>
                  <span>{error}</span>
                </div>
              </div>
            )}

            {/* Features hint */}
            <div className="landing-features">
              <div className="landing-feature">
                <div className="landing-feature-dot" />
                <span>Semantic Search</span>
              </div>
              <div className="landing-feature">
                <div className="landing-feature-dot" />
                <span>Code Analysis</span>
              </div>
              <div className="landing-feature">
                <div className="landing-feature-dot" />
                <span>AI Chat</span>
              </div>
            </div>

            {/* Footer hint */}
            <p className="landing-footer-hint">
              Supports public GitHub repositories. No authentication required.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingScreen;