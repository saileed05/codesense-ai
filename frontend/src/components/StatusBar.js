import React from 'react';
import { X } from 'lucide-react';
import './OverlaysAndStatus.css';

// ==================== EXPLANATION OVERLAY ====================
export const ExplanationOverlay = ({ explanation, onClose }) => {
  return (
    <div className="overlay-backdrop" onClick={onClose}>
      <div className="explanation-overlay" onClick={(e) => e.stopPropagation()}>
        <div className="overlay-header">
          <h2>💡 Code Explanation</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        
        <div className="overlay-content">
          {/* Summary */}
          {explanation.summary && (
            <div className="explanation-section">
              <h3>📋 Summary</h3>
              <p className="summary-text">{explanation.summary}</p>
            </div>
          )}
          
          {/* Line by Line */}
          {explanation.line_by_line && explanation.line_by_line.length > 0 && (
            <div className="explanation-section">
              <h3>📝 Line by Line Breakdown</h3>
              <div className="line-breakdown">
                {explanation.line_by_line.map((line, idx) => (
                  <div key={idx} className="line-item">
                    <div className="line-number">Line {line.line_number}</div>
                    <div className="line-code">
                      <code>{line.code}</code>
                    </div>
                    <div className="line-explanation">{line.explanation}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Key Concepts */}
          {explanation.key_concepts && explanation.key_concepts.length > 0 && (
            <div className="explanation-section">
              <h3>🔑 Key Concepts</h3>
              <div className="concepts-grid">
                {explanation.key_concepts.map((concept, idx) => (
                  <div key={idx} className="concept-card">
                    <div className="concept-title">{concept.concept}</div>
                    <div className="concept-explanation">{concept.explanation}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Complexity */}
          {explanation.complexity && (
            <div className="explanation-section">
              <h3>⚡ Complexity Analysis</h3>
              <div className="complexity-grid">
                <div className="complexity-item">
                  <span className="complexity-label">Time:</span>
                  <span className="complexity-value">{explanation.complexity.time}</span>
                </div>
                <div className="complexity-item">
                  <span className="complexity-label">Space:</span>
                  <span className="complexity-value">{explanation.complexity.space}</span>
                </div>
              </div>
              {explanation.complexity.explanation && (
                <p className="complexity-explanation">{explanation.complexity.explanation}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ==================== STATUS BAR ====================
export const StatusBar = ({ status }) => {
  if (!status.message) return null;
  
  const getStatusClass = () => {
    switch (status.type) {
      case 'success': return 'status-success';
      case 'error': return 'status-error';
      case 'info': return 'status-info';
      case 'processing': return 'status-processing';
      default: return '';
    }
  };
  
  const getStatusIcon = () => {
    switch (status.type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'info': return 'ℹ️';
      case 'processing': return '⏳';
      default: return '';
    }
  };
  
  return (
    <div className={`status-bar ${getStatusClass()}`}>
      <span className="status-icon">{getStatusIcon()}</span>
      <span className="status-message">{status.message}</span>
    </div>
  );
};

export default { ExplanationOverlay, StatusBar };