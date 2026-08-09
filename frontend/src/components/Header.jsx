import { Code, Github, Menu, Moon, Sun, Settings } from 'lucide-react';

/**
 * Header component - Top navigation bar with logo, theme toggle, and mobile menu.
 */
const Header = ({
  darkMode,
  onToggleTheme,
  onMenuClick,
  showMenuButton = false,
  repository = null,
}) => {
  return (
    <header className="app-header">
      <div className="header-left">
        {showMenuButton && (
          <button
            onClick={onMenuClick}
            className="icon-btn md-hidden"
            aria-label="Toggle navigation"
          >
            <Menu size={18} />
          </button>
        )}
        <div className="header-brand">
          <div className="header-logo">
            <Code size={18} />
          </div>
          <div className="header-brand-text">
            <h1 className="header-title">ANUBIS CODEX</h1>
            <p className="header-subtitle">GitHub Intelligence AI</p>
          </div>
        </div>
        {repository && (
          <div className="header-repo">
            <Github size={13} />
            <span className="header-repo-name">
              {repository.owner}/{repository.name}
            </span>
          </div>
        )}
      </div>

      <div className="header-actions">
        <button
          onClick={onToggleTheme}
          className="icon-btn"
          aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>
        <button
          className="icon-btn"
          aria-label="Settings"
        >
          <Settings size={16} />
        </button>
      </div>
    </header>
  );
};

export default Header;