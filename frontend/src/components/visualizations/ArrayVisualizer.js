import React from 'react';
import './ArrayVisualizer.css';

const ArrayVisualizer = ({ data }) => {
  const { name, data: elements, capacity, highlight, operation } = data;

  // Ensure we have valid data
  const safeElements = elements || [];
  const safeCapacity = Math.max(capacity || 0, safeElements.length);
  const highlightIndices = highlight || [];

  // Calculate empty slots to show
  const emptySlots = Math.max(0, safeCapacity - safeElements.length);

  return (
    <div className="array-visualizer">
      {/* Variable Name */}
      <div className="array-header">
        <span className="array-name">{name}</span>
        {operation && (
          <span className="array-operation">
            ⚡ Operation: {operation}
          </span>
        )}
      </div>

      {/* Array Boxes */}
      <div className="array-container">
        {/* Filled elements */}
        {safeElements.map((value, index) => {
          const isHighlighted = highlightIndices.includes(index);
          
          return (
            <div 
              key={`elem-${index}`} 
              className={`array-box ${isHighlighted ? 'highlighted' : 'filled'}`}
            >
              {/* Insertion arrow for push operations */}
              {isHighlighted && operation === 'push_back' && (
                <div className="insertion-arrow">↓</div>
              )}
              
              {/* Value */}
              <div className="array-value">{value}</div>
              
              {/* Index */}
              <div className="array-index">[{index}]</div>
              
              {/* Glow effect for highlighted */}
              {isHighlighted && <div className="glow-effect"></div>}
            </div>
          );
        })}

        {/* Empty capacity slots */}
        {Array.from({ length: emptySlots }).map((_, i) => (
          <div 
            key={`empty-${i}`} 
            className="array-box empty"
          >
            <div className="array-value">-</div>
            <div className="array-index">[{safeElements.length + i}]</div>
          </div>
        ))}
      </div>

      {/* Metadata */}
      <div className="array-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Size:</span>
          <span className="metadata-value size">{safeElements.length}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Capacity:</span>
          <span className="metadata-value capacity">{safeCapacity}</span>
        </div>
        {safeCapacity > safeElements.length && (
          <div className="metadata-item">
            <span className="metadata-label">Free:</span>
            <span className="metadata-value free">{emptySlots}</span>
          </div>
        )}
      </div>

      {/* Resize indicator */}
      {operation === 'resize' && (
        <div className="resize-indicator">
          📦 Capacity increased! (Reallocation occurred)
        </div>
      )}
    </div>
  );
};

export default ArrayVisualizer;