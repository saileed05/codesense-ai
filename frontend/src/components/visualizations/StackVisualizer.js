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
            {operation === 'push' ? '⬇️ Push (Add to Top)' : '⬆️ Pop (Remove from Top)'}
          </span>
        )}
      </div>

      {/* Pop indicator at TOP */}
      {operation === 'pop' && removed_value !== undefined && (
        <div className="pop-indicator">
          ⬆️ Popped from TOP: <strong>{removed_value}</strong>
        </div>
      )}

      {/* Stack Visual - Vertical Layout (Top-Down) */}
      <div className="stack-container">
        <div className="stack-label top">📍 TOP (Last In, First Out) ⬇️</div>
        
        <div className="stack-elements">
          {safeElements.length === 0 ? (
            <div className="empty-stack">Empty Stack</div>
          ) : (
            <>
              {/* FIXED: Proper LIFO display - top element shown first */}
              {safeElements.slice().reverse().map((value, reverseIdx) => {
                const actualIndex = safeElements.length - 1 - reverseIdx;
                const isHighlighted = highlight?.includes(actualIndex);
                const isTop = actualIndex === safeElements.length - 1;
                
                return (
                  <div 
                    key={`stack-${actualIndex}-${value}-${reverseIdx}`}
                    className={`stack-box ${isHighlighted ? 'highlighted' : ''} ${isTop ? 'top-item' : ''}`}
                  >
                    {isHighlighted && operation === 'push' && (
                      <div className="push-indicator">⬇️ PUSHED</div>
                    )}
                    
                    <div className="stack-value">{value}</div>
                    
                    {/* Show index from top (0 = top element) */}
                    <div className="stack-index">[{reverseIdx}]</div>
                    
                    {isTop && <div className="position-badge">📍 TOP</div>}
                    
                    {isHighlighted && <div className="glow-effect"></div>}
                  </div>
                );
              })}
            </>
          )}
        </div>
        
        <div className="stack-label bottom">⬇️ BOTTOM (Base)</div>
      </div>

      {/* Metadata */}
      <div className="stack-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Size:</span>
          <span className="metadata-value">{safeElements.length}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Top (peek):</span>
          <span className="metadata-value">{safeElements[safeElements.length - 1] || 'N/A'}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Bottom:</span>
          <span className="metadata-value">{safeElements[0] || 'N/A'}</span>
        </div>
      </div>

      {/* LIFO Explanation */}
      <div className="stack-explanation">
        <strong>Stack = LIFO (Last In, First Out)</strong>
        <div>Operations happen at the TOP only</div>
      </div>
    </div>
  );
};

export default StackVisualizer;