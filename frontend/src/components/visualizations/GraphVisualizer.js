import React from 'react';
import './GraphVisualizer.css';

const GraphVisualizer = ({ data }) => {
  const { name, nodes, edges, formatted } = data;

  return (
    <div className="graph-visualizer">
      <div className="graph-header">
        <span className="graph-name">{name}</span>
        <span className="node-count">{nodes?.length || 0} nodes</span>
      </div>

      {/* Graph Structure Display */}
      <div className="graph-structure">
        {formatted && formatted.map((line, idx) => (
          <div key={idx} className="graph-line">
            <code>{line}</code>
          </div>
        ))}
      </div>

      {/* Node List */}
      <div className="nodes-section">
        <h4>Nodes:</h4>
        <div className="node-list">
          {nodes && nodes.map((node, idx) => (
            <div key={idx} className="node-item">
              <div className="node-circle">{node}</div>
              <div className="node-connections">
                {edges[node] && edges[node].length > 0 ? (
                  <span>→ {edges[node].join(', ')}</span>
                ) : (
                  <span className="no-edges">No edges</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="graph-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Total Nodes:</span>
          <span className="metadata-value">{nodes?.length || 0}</span>
        </div>
        <div className="metadata-item">
          <span className="metadata-label">Total Edges:</span>
          <span className="metadata-value">
            {edges ? Object.values(edges).reduce((sum, arr) => sum + arr.length, 0) : 0}
          </span>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualizer;