import React from 'react';
import './BugDetector.css';

const BugDetector = ({ bugs }) => {
  const getSeverityColor = (severity) => {
    const colors = {
      high: '#e74c3c',
      medium: '#f39c12',
      low: '#3498db'
    };
    return colors[severity] || '#95a5a6';
  };

  return (
    <div className="bug-detector">
      <h3>🐛 Code Analysis Results</h3>

      {bugs.bugs_found && bugs.bugs_found.length > 0 ? (
        <>
          <div className="bugs-section">
            <h4>⚠️ Bugs & Issues</h4>
            {bugs.bugs_found.map((bug, idx) => (
              <div 
                className="bug-card" 
                key={idx}
                style={{ borderLeftColor: getSeverityColor(bug.severity) }}
              >
                <div className="bug-header">
                  <span className={`severity-badge ${bug.severity}`}>
                    {bug.severity.toUpperCase()}
                  </span>
                  <span className="line-number">Line {bug.line}</span>
                </div>
                <h5>{bug.issue}</h5>
                <p className="explanation">{bug.explanation}</p>
                <div className="fix-suggestion">
                  <strong>💡 Fix:</strong>
                  <code>{bug.fix}</code>
                </div>
              </div>
            ))}
          </div>

          {bugs.code_smells && bugs.code_smells.length > 0 && (
            <div className="smells-section">
              <h4>👃 Code Smells</h4>
              {bugs.code_smells.map((smell, idx) => (
                <div className="smell-card" key={idx}>
                  <div className="smell-header">
                    <span className="smell-type">{smell.type}</span>
                    <span className="line-number">Line {smell.line}</span>
                  </div>
                  <p>{smell.issue}</p>
                  <p className="suggestion">
                    <strong>Suggestion:</strong> {smell.suggestion}
                  </p>
                </div>
              ))}
            </div>
          )}

          {bugs.improvements && bugs.improvements.length > 0 && (
            <div className="improvements-section">
              <h4>✨ Improvements</h4>
              {bugs.improvements.map((improvement, idx) => (
                <div className="improvement-card" key={idx}>
                  <span className="category">{improvement.category}</span>
                  <p>{improvement.suggestion}</p>
                  {improvement.example && (
                    <pre className="example-code">{improvement.example}</pre>
                  )}
                </div>
              ))}
            </div>
          )}

          {bugs.refactored_code && (
            <div className="refactored-section">
              <h4>🔧 Refactored Code</h4>
              <pre className="refactored-code">{bugs.refactored_code}</pre>
              <button className="copy-btn" onClick={() => {
                navigator.clipboard.writeText(bugs.refactored_code);
                alert('Copied to clipboard!');
              }}>
                📋 Copy Refactored Code
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="no-bugs">
          <span className="checkmark">✅</span>
          <h4>Great job! No major issues found.</h4>
          <p>Your code looks clean and follows best practices.</p>
        </div>
      )}
    </div>
  );
};

export default BugDetector;