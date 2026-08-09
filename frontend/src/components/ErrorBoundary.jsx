import { Component } from 'react';

/**
 * ErrorBoundary - Catches React rendering errors and displays a fallback UI
 * Prevents blank blue screens when components crash
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React Error Boundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-screen">
          <div className="surface-card shadow-soft-lg error-card">
            <div className="error-header">
              <div className="error-icon">
                <span>⚠️</span>
              </div>
              <div>
                <h1 className="error-title">Something went wrong</h1>
                <p className="error-subtitle">The application encountered an unexpected error</p>
              </div>
            </div>

            <div className="error-details">
              <p className="error-details-label">Error Details</p>
              <p className="error-message">
                {this.state.error?.message || 'Unknown error'}
              </p>
            </div>

            <div className="error-actions">
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null, errorInfo: null });
                  window.location.reload();
                }}
                className="error-action-btn primary"
              >
                Reload Application
              </button>
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null, errorInfo: null });
                }}
                className="error-action-btn secondary"
              >
                Try to Continue
              </button>
            </div>

            <p className="error-footer">
              If this error persists, please check the browser console for details or restart the application.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;