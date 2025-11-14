import React from 'react';
import './StackVisualizer.css';

const StackVisualizer = ({ data }) => {
  const { name, data: elements, highlight, operation, removed_value } = data;
  const safeElements = elements || [];

  return (
    <div className="stack-visualizer">
      <div className="stack-header">
        <span className="stack-name">📚 {name}</span>
        {operation && (
          <span className="stack-operation">
            {operation === 'push' ? '➕ Push' : '➖ Pop'}
          </span>
        )}
      </div>

      {/* Stack Visual - Vertical Layout */}
      <div className="stack-container">
        <div className="stack-label top">TOP ↓</div>
        
        <div className="stack-elements">
          {safeElements.length === 0 ? (
            <div className="empty-stack">Empty Stack</div>
          ) : (
            <>
              {/* Reverse to show top at the top */}
              {[...safeElements].reverse().map((value, displayIndex) => {
                const actualIndex = safeElements.length - 1 - displayIndex;
                const isHighlighted = highlight?.includes(actualIndex);
                const isTop = actualIndex === safeElements.length - 1;
                
                return (
                  <div 
                    key={actualIndex} 
                    className={`stack-box ${isHighlighted ? 'highlighted' : ''} ${isTop ? 'top-item' : ''}`}
                  >
                    {isHighlighted && operation === 'push' && (
                      <div className="push-indicator">↓ NEW</div>
                    )}
                    
                    <div className="stack-value">{value}</div>
                    
                    {isTop && <div className="position-badge">TOP</div>}
                    
                    {isHighlighted && <div className="glow-effect"></div>}
                  </div>
                );
              })}
            </>
          )}
        </div>
        
        <div className="stack-label bottom">BOTTOM</div>
      </div>

      {/* Pop indicator */}
      {operation === 'pop' && removed_value && (
        <div className="pop-indicator">
          ⬆️ Popped: <strong>{removed_value}</strong>
        </div>
      )}

      {/* Metadata */}
      <div className="stack-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Size:</span>
          <span className="metadata-value">{safeElements.length}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Top:</span>
          <span className="metadata-value">{safeElements[safeElements.length - 1] || 'N/A'}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Bottom:</span>
          <span className="metadata-value">{safeElements[0] || 'N/A'}</span>
        </div>
      </div>
    </div>
  );
};

export default StackVisualizer;