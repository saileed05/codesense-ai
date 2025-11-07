import React from 'react';
import './GraphWithDSVisualizer.css';

const GraphWithDSVisualizer = ({ data }) => {
  const { graph, data_structure } = data;

  const renderDataStructure = (ds) => {
    const elements = ds.data || [];
    
    if (ds.type === 'queue' || ds.type === 'stack') {
      return (
        <div className="ds-panel">
          <div className="ds-header">
            <span className="ds-title">
              {ds.type === 'queue' ? '📋 Queue' : '📚 Stack'}: {ds.name}
            </span>
            {ds.operation && (
              <span className="ds-operation">{ds.operation}</span>
            )}
          </div>
          
          <div className="ds-container">
            {ds.type === 'queue' && <div className="ds-label front">← FRONT</div>}
            {ds.type === 'stack' && <div className="ds-label">TOP ↓</div>}
            
            <div className={`ds-elements ${ds.type}`}>
              {elements.length === 0 ? (
                <div className="empty-ds">Empty</div>
              ) : (
                elements.map((value, index) => {
                  const isHighlighted = ds.highlight?.includes(index);
                  const isFront = ds.type === 'queue' && index === 0;
                  const isTop = ds.type === 'stack' && index === elements.length - 1;
                  
                  return (
                    <div 
                      key={index}
                      className={`ds-box ${isHighlighted ? 'highlighted' : ''} ${isFront || isTop ? 'active' : ''}`}
                    >
                      {isHighlighted && ds.operation === 'enqueue' && (
                        <div className="insert-indicator">⬆️ NEW</div>
                      )}
                      <div className="ds-value">{value}</div>
                      {(isFront || isTop) && (
                        <div className="position-badge">{isFront ? 'FRONT' : 'TOP'}</div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
            
            {ds.type === 'queue' && <div className="ds-label back">BACK →</div>}
          </div>

          {ds.removed_value && (
            <div className="removed-indicator">
              ⬇️ Removed: <strong>{ds.removed_value}</strong>
            </div>
          )}
        </div>
      );
    }

    // Visited tracker
    if (ds.type === 'visited') {
      return (
        <div className="ds-panel">
          <div className="ds-header">
            <span className="ds-title">✅ Visited: {ds.name}</span>
          </div>
          <div className="visited-container">
            {elements.length === 0 ? (
              <div className="empty-visited">None yet</div>
            ) : (
              elements.map((node, idx) => (
                <div 
                  key={idx}
                  className={`visited-badge ${ds.highlight?.includes(idx) ? 'new' : ''}`}
                >
                  {node}
                </div>
              ))
            )}
          </div>
        </div>
      );
    }

    return null;
  };

  const renderGraph = (graphData) => {
    const { nodes, edges, positions, current_node, visited, exploring } = graphData;

    return (
      <div className="graph-panel">
        <div className="graph-header">
          <span className="graph-title">📊 Graph: {graphData.name}</span>
          <span className="graph-stats">{nodes.length} nodes</span>
        </div>

        <svg width="800" height="500" viewBox="0 0 800 500" className="graph-svg">
          {/* Draw edges */}
          {nodes.map(node => {
            const neighbors = edges[node] || [];
            const startPos = positions[node];
            
            return neighbors.map(neighbor => {
              const endPos = positions[neighbor];
              if (!startPos || !endPos) return null;

              const isActiveEdge = current_node === node && exploring?.includes(neighbor);
              const isVisitedEdge = visited?.includes(node) && visited?.includes(neighbor);

              // Calculate edge path with curve
              const midX = (startPos.x + endPos.x) / 2;
              const midY = (startPos.y + endPos.y) / 2;
              const dx = endPos.x - startPos.x;
              const dy = endPos.y - startPos.y;
              const curve = 20;
              const controlX = midX - dy * curve / Math.sqrt(dx*dx + dy*dy);
              const controlY = midY + dx * curve / Math.sqrt(dx*dx + dy*dy);

              return (
                <g key={`${node}-${neighbor}`}>
                  {/* Edge path */}
                  <path
                    d={`M ${startPos.x} ${startPos.y} Q ${controlX} ${controlY} ${endPos.x} ${endPos.y}`}
                    stroke={isActiveEdge ? '#f59e0b' : isVisitedEdge ? '#10b981' : '#4b5563'}
                    strokeWidth={isActiveEdge ? 4 : 2}
                    fill="none"
                    className="graph-edge"
                    style={{
                      animation: isActiveEdge ? 'edgePulse 1s infinite' : 'none'
                    }}
                  />
                  
                  {/* Arrow head */}
                  <circle
                    cx={endPos.x}
                    cy={endPos.y}
                    r="5"
                    fill={isActiveEdge ? '#f59e0b' : isVisitedEdge ? '#10b981' : '#4b5563'}
                  />
                </g>
              );
            });
          })}

          {/* Draw nodes */}
          {nodes.map(node => {
            const pos = positions[node];
            if (!pos) return null;

            const isCurrent = current_node === node;
            const isVisited = visited?.includes(node);
            const isExploring = exploring?.includes(node);

            let nodeColor = '#6b7280'; // default gray
            let nodeScale = 1;
            let hasGlow = false;
            let nodeStroke = 'white';
            let strokeWidth = 3;

            if (isCurrent) {
              nodeColor = '#3b82f6'; // purple
              nodeScale = 1.4;
              hasGlow = true;
              strokeWidth = 4;
            } else if (isExploring) {
              nodeColor = '#f59e0b'; // amber
              nodeScale = 1.15;
              strokeWidth = 4;
            } else if (isVisited) {
              nodeColor = '#10b981';
              nodeStroke = '#34d399'; // green
            }

            return (
              <g key={node} className="graph-node">
                {/* Glow effect */}
                {hasGlow && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={45 * nodeScale}
                    fill={nodeColor}
                    opacity="0.3"
                    className="node-glow"
                  />
                )}

                {/* Node circle */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={30 * nodeScale}
                  fill={nodeColor}
                  stroke="white"
                  strokeWidth="3"
                  className="node-circle"
                  style={{
                    transition: 'all 0.5s ease',
                    transformOrigin: `${pos.x}px ${pos.y}px`
                  }}
                />

                {/* Node label */}
                <text
                  x={pos.x}
                  y={pos.y + 6}
                  textAnchor="middle"
                  fontSize={18 * nodeScale}
                  fontWeight="bold"
                  fill="white"
                  className="node-label"
                >
                  {node}
                </text>

                {/* Status badge */}
                {isCurrent && (
                  <text
                    x={pos.x}
                    y={pos.y - 45}
                    textAnchor="middle"
                    fontSize="12"
                    fill="#a855f7"
                    fontWeight="bold"
                  >
                    CURRENT
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div className="graph-legend">
          <div className="legend-item">
            <div className="legend-circle gray"></div>
            <span>Unvisited</span>
          </div>
          <div className="legend-item">
            <div className="legend-circle blue"></div>
            <span>Current</span>
          </div>
          <div className="legend-item">
            <div className="legend-circle amber"></div>
            <span>Exploring</span>
          </div>
          <div className="legend-item">
            <div className="legend-circle green"></div>
            <span>Visited</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="graph-with-ds-visualizer">
      <div className="step-description">
         {graph.current_node ? (
           <div className="description-text">
            <strong>Processing:</strong> Node <span className="node-badge">{graph.current_node}</span>
             {graph.exploring?.length > 0 && (
               <span> → Checking neighbor <span className="node-badge exploring">{graph.exploring[0]}</span></span>
               )}
        </div>         ) : (
           <div className="description-text">
             <strong>Ready to start BFS traversal</strong>
           </div>
         )}
      </div>
      {/* Graph Visualization */}
      {graph && renderGraph(graph)}

      {/* Data Structure Visualization */}
      {data_structure && renderDataStructure(data_structure)}
    </div>
  );
};

export default GraphWithDSVisualizer;