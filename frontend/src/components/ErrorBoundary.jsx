import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Visualization Error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary" style={{
          padding: '2rem',
          background: '#0d1117',
          border: '1px solid #f85149',
          borderRadius: '8px',
          textAlign: 'center',
          margin: '1rem'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
          <h3 style={{ color: '#f85149', marginBottom: '0.5rem' }}>
            Visualization Error
          </h3>
          <p style={{ color: '#8b949e', marginBottom: '1rem' }}>
            {this.state.error?.message || 'Something went wrong rendering this visualization'}
          </p>
          <details style={{ textAlign: 'left', marginTop: '1rem' }}>
            <summary style={{ color: '#58a6ff', cursor: 'pointer' }}>
              Technical Details
            </summary>
            <pre style={{
              background: '#161b22',
              padding: '1rem',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '0.8rem',
              marginTop: '0.5rem'
            }}>
              {this.state.error?.stack}
              {this.state.errorInfo?.componentStack}
            </pre>
          </details>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              background: '#238636',
              border: 'none',
              borderRadius: '6px',
              color: 'white',
              cursor: 'pointer'
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;