import React, { useEffect, useRef } from 'react';
import './GraphVisualizer.css';

const GraphVisualizer = ({ data }) => {
  const { name, nodes, edges, formatted, positions } = data;
  const canvasRef = useRef(null);

  // Draw graph on canvas
  useEffect(() => {
    if (!canvasRef.current || !nodes || !positions) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw edges first (behind nodes)
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 2;

    Object.keys(edges).forEach(node => {
      const neighbors = edges[node];
      if (!neighbors || !Array.isArray(neighbors)) return;

      const fromPos = positions[node];
      if (!fromPos) return;

      neighbors.forEach(neighbor => {
        // Handle weighted edges (tuples)
        const toNode = Array.isArray(neighbor) ? neighbor[0] : neighbor;
        const toPos = positions[toNode];

        if (toPos) {
          ctx.beginPath();
          ctx.moveTo(fromPos.x, fromPos.y);
          ctx.lineTo(toPos.x, toPos.y);
          ctx.stroke();

          // Draw arrow
          const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
          const arrowSize = 10;
          ctx.beginPath();
          ctx.moveTo(toPos.x, toPos.y);
          ctx.lineTo(
            toPos.x - arrowSize * Math.cos(angle - Math.PI / 6),
            toPos.y - arrowSize * Math.sin(angle - Math.PI / 6)
          );
          ctx.lineTo(
            toPos.x - arrowSize * Math.cos(angle + Math.PI / 6),
            toPos.y - arrowSize * Math.sin(angle + Math.PI / 6)
          );
          ctx.closePath();
          ctx.fillStyle = '#30363d';
          ctx.fill();
        }
      });
    });

    // Draw nodes
    nodes.forEach(node => {
      const pos = positions[node];
      if (!pos) return;

      // Node circle
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 30, 0, 2 * Math.PI);
      ctx.fillStyle = '#667eea';
      ctx.fill();
      ctx.strokeStyle = '#8b9aff';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Node label
      ctx.fillStyle = 'white';
      ctx.font = 'bold 18px Consolas';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(node), pos.x, pos.y);
    });

  }, [nodes, edges, positions]);

  return (
    <div className="graph-visualizer">
      <div className="graph-header">
        <span className="graph-name">🌐 {name}</span>
        <span className="node-count">{nodes?.length || 0} nodes</span>
      </div>

      {/* Canvas for visual graph */}
      {positions && (
        <div className="graph-canvas-container">
          <canvas 
            ref={canvasRef} 
            width={800} 
            height={500}
            className="graph-canvas"
          />
        </div>
      )}

      {/* Text representation */}
      <div className="graph-structure">
        <h4>Adjacency List:</h4>
        {formatted && formatted.map((line, idx) => (
          <div key={idx} className="graph-line">
            <code>{line}</code>
          </div>
        ))}
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
            {edges ? Object.values(edges).reduce((sum, arr) => {
              return sum + (Array.isArray(arr) ? arr.length : 0);
            }, 0) : 0}
          </span>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualizer;