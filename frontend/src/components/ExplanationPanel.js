import React, { useState } from 'react';
import './ExplanationPanel.css';

const ExplanationPanel = ({ explanation }) => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="explanation-panel">
      <div className="tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📋 Overview
        </button>
        <button 
          className={activeTab === 'linebyline' ? 'active' : ''}
          onClick={() => setActiveTab('linebyline')}
        >
          🔍 Line by Line
        </button>
        <button 
          className={activeTab === 'concepts' ? 'active' : ''}
          onClick={() => setActiveTab('concepts')}
        >
          💡 Concepts
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="summary-card">
              <h3>Summary</h3>
              <p>{explanation.summary}</p>
            </div>

            {explanation.complexity && (
              <div className="complexity-section">
                <h3>⚡ Complexity Analysis</h3>
                <div className="complexity-grid">
                  <div className="complexity-card">
                    <span className="label">Time</span>
                    <span className="value">{explanation.complexity.time}</span>
                  </div>
                  <div className="complexity-card">
                    <span className="label">Space</span>
                    <span className="value">{explanation.complexity.space}</span>
                  </div>
                </div>
                <p className="complexity-explanation">
                  {explanation.complexity.explanation}
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'linebyline' && (
          <div className="linebyline-tab">
            {explanation.line_by_line?.map((line, idx) => (
              <div key={idx} className="line-explanation">
                <div className="line-header">
                  <span className="line-number">Line {line.line_number}</span>
                  <code className="line-code">{line.code}</code>
                </div>
                <p className="line-desc">{line.explanation}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'concepts' && (
          <div className="concepts-tab">
            {explanation.key_concepts?.map((concept, idx) => (
              <div key={idx} className="concept-card">
                <h4>{concept.concept}</h4>
                <p>{concept.explanation}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExplanationPanel;