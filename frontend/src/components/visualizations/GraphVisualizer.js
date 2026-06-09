import React, { useEffect, useRef } from 'react';
import './GraphVisualizer.css';

const GraphVisualizer = ({ data }) => {
  const { name, nodes, edges, formatted, positions } = data;
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  // Draw graph on canvas with responsive sizing
  useEffect(() => {
    if (!canvasRef.current || !nodes || !positions) return;

    const canvas = canvasRef.current;
    const container = containerRef.current;
    const ctx = canvas.getContext('2d');
    
    // Get container dimensions for responsive canvas
    const containerWidth = container?.clientWidth || 800;
    const containerHeight = 500;
    
    // Set canvas dimensions to match container
    canvas.width = containerWidth;
    canvas.height = containerHeight;
    
    // Calculate scale to fit graph within canvas
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    Object.values(positions).forEach(pos => {
      minX = Math.min(minX, pos.x);
      minY = Math.min(minY, pos.y);
      maxX = Math.max(maxX, pos.x);
      maxY = Math.max(maxY, pos.y);
    });
    
    const padding = 50;
    const scaleX = (containerWidth - padding * 2) / (maxX - minX || 1);
    const scaleY = (containerHeight - padding * 2) / (maxY - minY || 1);
    const scale = Math.min(scaleX, scaleY);
    
    const offsetX = (containerWidth - (maxX - minX) * scale) / 2 - minX * scale;
    const offsetY = (containerHeight - (maxY - minY) * scale) / 2 - minY * scale;

    // Clear canvas
    ctx.clearRect(0, 0, containerWidth, containerHeight);

    // Draw edges first (behind nodes)
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 2;

    Object.keys(edges).forEach(node => {
      const neighbors = edges[node];
      if (!neighbors || !Array.isArray(neighbors)) return;

      const fromPos = positions[node];
      if (!fromPos) return;

      neighbors.forEach(neighbor => {
        const toNode = Array.isArray(neighbor) ? neighbor[0] : neighbor;
        const toPos = positions[toNode];

        if (toPos) {
          const fromX = fromPos.x * scale + offsetX;
          const fromY = fromPos.y * scale + offsetY;
          const toX = toPos.x * scale + offsetX;
          const toY = toPos.y * scale + offsetY;
          
          ctx.beginPath();
          ctx.moveTo(fromX, fromY);
          ctx.lineTo(toX, toY);
          ctx.stroke();

          // Draw arrow
          const angle = Math.atan2(toY - fromY, toX - fromX);
          const arrowSize = 10;
          ctx.beginPath();
          ctx.moveTo(toX, toY);
          ctx.lineTo(
            toX - arrowSize * Math.cos(angle - Math.PI / 6),
            toY - arrowSize * Math.sin(angle - Math.PI / 6)
          );
          ctx.lineTo(
            toX - arrowSize * Math.cos(angle + Math.PI / 6),
            toY - arrowSize * Math.sin(angle + Math.PI / 6)
          );
          ctx.closePath();
          ctx.fillStyle = '#30363d';
          ctx.fill();
        }
      });
    });

    // Draw nodes
    const nodeRadius = 25;
    nodes.forEach(node => {
      const pos = positions[node];
      if (!pos) return;

      const x = pos.x * scale + offsetX;
      const y = pos.y * scale + offsetY;

      // Node circle
      ctx.beginPath();
      ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI);
      ctx.fillStyle = '#667eea';
      ctx.fill();
      ctx.strokeStyle = '#8b9aff';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Node label
      ctx.fillStyle = 'white';
      ctx.font = `bold ${Math.min(18, nodeRadius * 0.7)}px Consolas`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(node), x, y);
    });

  }, [nodes, edges, positions]);

  return (
    <div className="graph-visualizer">
      <div className="graph-header">
        <span className="graph-name">🌐 {name}</span>
        <span className="node-count">{nodes?.length || 0} nodes</span>
      </div>

      {/* Responsive canvas container */}
      <div className="graph-canvas-container" ref={containerRef}>
        <canvas 
          ref={canvasRef} 
          className="graph-canvas"
          style={{ width: '100%', height: 'auto', minHeight: '400px' }}
        />
      </div>

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