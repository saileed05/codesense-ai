import React from 'react';
import './QueueVisualizer.css';

const QueueVisualizer = ({ data }) => {
  const { name, data: elements, highlight, operation, removed_value } = data;
  const safeElements = elements || [];

  return (
    <div className="queue-visualizer">
      <div className="queue-header">
        <span className="queue-name">{name}</span>
        {operation && (
          <span className="queue-operation">
            {operation === 'enqueue' ? '➕ Enqueue' : '➖ Dequeue'}
          </span>
        )}
      </div>

      {/* Queue Visual */}
      <div className="queue-container">
        <div className="queue-label front">← FRONT</div>
        
        <div className="queue-elements">
          {safeElements.length === 0 ? (
            <div className="empty-queue">Empty Queue</div>
          ) : (
            <>
              {safeElements.map((value, index) => {
                const isHighlighted = highlight?.includes(index);
                const isFront = index === 0;
                const isBack = index === safeElements.length - 1;
                
                return (
                  <div 
                    key={index} 
                    className={`queue-box ${isHighlighted ? 'highlighted' : ''} ${isFront ? 'front-item' : ''} ${isBack ? 'back-item' : ''}`}
                  >
                    {isHighlighted && operation === 'enqueue' && (
                      <div className="enqueue-arrow">↓ NEW</div>
                    )}
                    
                    <div className="queue-value">{value}</div>
                    
                    {isFront && <div className="position-label">Front</div>}
                    {isBack && <div className="position-label">Back</div>}
                    
                    {isHighlighted && <div className="glow-effect"></div>}
                  </div>
                );
              })}
            </>
          )}
        </div>
        
        <div className="queue-label back">BACK →</div>
      </div>

      {/* Dequeue indicator */}
      {operation === 'dequeue' && removed_value && (
        <div className="dequeue-indicator">
          ⬅️ Dequeued: <strong>{removed_value}</strong>
        </div>
      )}

      {/* Metadata */}
      <div className="queue-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Size:</span>
          <span className="metadata-value">{safeElements.length}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Front:</span>
          <span className="metadata-value">{safeElements[0] || 'N/A'}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Back:</span>
          <span className="metadata-value">{safeElements[safeElements.length - 1] || 'N/A'}</span>
        </div>
      </div>
    </div>
  );
};

export default QueueVisualizer;