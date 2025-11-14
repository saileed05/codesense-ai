import React from 'react';
import './GraphWithDSVisualizer.css';

const GraphWithDSVisualizer = ({ data }) => {
  const { graph, data_structure } = data;

  // Generate text description for screen readers
  const generateGraphDescription = (graphData) => {
    const { nodes, current_node, visited = [], exploring = [] } = graphData;
    let desc = `Graph with ${nodes.length} nodes. `;
    
    if (current_node) {
      desc += `Currently processing node ${current_node}. `;
    }
    if (visited.length > 0) {
      desc += `Visited nodes: ${visited.join(', ')}. `;
    }
    if (exploring.length > 0) {
      desc += `Exploring: ${exploring.join(', ')}.`;
    }
    return desc;
  };

  // Pattern definitions for colorblind accessibility
  const PatternDefinitions = () => (
    <defs>
      {/* Diagonal stripes for exploring */}
      <pattern id="exploringPattern" width="8" height="8" patternUnits="userSpaceOnUse">
        <rect width="8" height="8" fill="#f59e0b" opacity="0.3"/>
        <path d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4" 
              stroke="#f59e0b" strokeWidth="2"/>
      </pattern>
      
      {/* Dots for visited */}
      <pattern id="visitedPattern" width="10" height="10" patternUnits="userSpaceOnUse">
        <circle cx="5" cy="5" r="2" fill="#10b981"/>
      </pattern>
      
      {/* Grid for current */}
      <pattern id="currentPattern" width="10" height="10" patternUnits="userSpaceOnUse">
        <rect width="10" height="10" fill="none" stroke="#3b82f6" strokeWidth="1"/>
      </pattern>
    </defs>
  );

  const renderGraph = (graphData) => {
    const { nodes, edges, positions, current_node, visited, exploring } = graphData;
    const description = generateGraphDescription(graphData);

    return (
      <div className="graph-section">
        <div className="graph-header">
          <span className="graph-title">📊 Graph: {graphData.name}</span>
          <span className="graph-stats">{nodes.length} nodes</span>
        </div>

        <svg 
          width="100%" 
          height="400" 
          viewBox="0 0 800 400" 
          className="graph-svg"
          preserveAspectRatio="xMidYMid meet"
          role="img"
          aria-label={`Graph visualization: ${graphData.name}`}
          aria-describedby="graph-desc graph-current-state"
        >
          <title id="graph-title">Graph Traversal Visualization</title>
          <desc id="graph-desc">{description}</desc>
          
          <PatternDefinitions />

          {/* Draw edges with better contrast */}
          {nodes.map(node => {
            const neighbors = edges[node] || [];
            const startPos = positions[node];
            
            return neighbors.map(neighbor => {
              const endPos = positions[neighbor];
              if (!startPos || !endPos) return null;

              const isActiveEdge = current_node === node && exploring?.includes(neighbor);
              const isVisitedEdge = visited?.includes(node) && visited?.includes(neighbor);

              const midX = (startPos.x + endPos.x) / 2;
              const midY = (startPos.y + endPos.y) / 2;
              const dx = endPos.x - startPos.x;
              const dy = endPos.y - startPos.y;
              const curve = 20;
              const controlX = midX - dy * curve / Math.sqrt(dx*dx + dy*dy);
              const controlY = midY + dx * curve / Math.sqrt(dx*dx + dy*dy);

              return (
                <g key={`${node}-${neighbor}`}>
                  <path
                    d={`M ${startPos.x} ${startPos.y} Q ${controlX} ${controlY} ${endPos.x} ${endPos.y}`}
                    stroke={isActiveEdge ? '#fbbf24' : isVisitedEdge ? '#34d399' : '#6b7280'}
                    strokeWidth={isActiveEdge ? 5 : 3}
                    fill="none"
                    className="graph-edge"
                    strokeDasharray={isActiveEdge ? "10,5" : "none"}
                    aria-label={`Edge from ${node} to ${neighbor}${isActiveEdge ? ', currently exploring' : ''}${isVisitedEdge ? ', already visited' : ''}`}
                  />
                  
                  <circle
                    cx={endPos.x}
                    cy={endPos.y}
                    r="6"
                    fill={isActiveEdge ? '#fbbf24' : isVisitedEdge ? '#34d399' : '#9ca3af'}
                    stroke="white"
                    strokeWidth="2"
                  />
                </g>
              );
            });
          })}

          {/* Draw nodes with patterns AND color */}
          {nodes.map(node => {
            const pos = positions[node];
            if (!pos) return null;

            const isCurrent = current_node === node;
            const isVisited = visited?.includes(node);
            const isExploring = exploring?.includes(node);

            let nodeColor = '#6b7280';
            let nodePattern = null;
            let nodeScale = 1;
            let statusIcon = '';
            let ariaLabel = `Node ${node}`;

            if (isCurrent) {
              nodeColor = '#3b82f6';
              nodePattern = 'url(#currentPattern)';
              nodeScale = 1.4;
              statusIcon = '▶';
              ariaLabel += ', currently processing';
            } else if (isExploring) {
              nodeColor = '#f59e0b';
              nodePattern = 'url(#exploringPattern)';
              nodeScale = 1.15;
              statusIcon = '?';
              ariaLabel += ', exploring';
            } else if (isVisited) {
              nodeColor = '#10b981';
              nodePattern = 'url(#visitedPattern)';
              statusIcon = '✓';
              ariaLabel += ', visited';
            } else {
              ariaLabel += ', unvisited';
            }

            return (
              <g 
                key={node} 
                className="graph-node"
                role="img"
                aria-label={ariaLabel}
                tabIndex="0"
              >
                {isCurrent && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={50 * nodeScale}
                    fill={nodeColor}
                    opacity="0.2"
                    className="node-glow"
                  />
                )}

                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={35 * nodeScale}
                  fill="white"
                  opacity="0.9"
                />

                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={30 * nodeScale}
                  fill={nodePattern || nodeColor}
                  stroke="white"
                  strokeWidth="4"
                  className="node-circle"
                />

                {statusIcon && (
                  <text
                    x={pos.x + 20}
                    y={pos.y - 20}
                    fontSize="20"
                    fontWeight="bold"
                  >
                    {statusIcon}
                  </text>
                )}

                <text
                  x={pos.x}
                  y={pos.y + 6}
                  textAnchor="middle"
                  fontSize={20 * nodeScale}
                  fontWeight="bold"
                  fill="#000"
                  stroke="white"
                  strokeWidth="3"
                  paintOrder="stroke"
                  className="node-label"
                >
                  {node}
                </text>

                {isCurrent && (
                  <text
                    x={pos.x}
                    y={pos.y - 50}
                    textAnchor="middle"
                    fontSize="14"
                    fontWeight="bold"
                    fill="#3b82f6"
                    stroke="white"
                    strokeWidth="2"
                    paintOrder="stroke"
                  >
                    CURRENT
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        <div 
          id="graph-current-state" 
          className="sr-only" 
          role="status" 
          aria-live="polite"
          aria-atomic="true"
        >
          {description}
        </div>
      </div>
    );
  };

  const renderDataStructure = (ds) => {
    if (!ds) return null;
    
    const elements = ds.data || [];
    const { name, type, highlight, operation, removed_value } = ds;

    if (type === 'queue') {
      return (
        <div 
          className="ds-section" 
          role="region" 
          aria-label={`Queue data structure: ${name}`}
        >
          <div className="ds-header">
            <span className="ds-title">🔄 {name}</span>
            {operation && (
              <span className="ds-operation">
                {operation === 'enqueue' ? '➕ Enqueue' : '➖ Dequeue'}
              </span>
            )}
          </div>

          <div className="ds-container">
            <div className="ds-label front">← FRONT</div>
            
            <div className="ds-elements">
              {elements.length === 0 ? (
                <div className="empty-ds">Empty Queue</div>
              ) : (
                elements.map((value, index) => {
                  const isHighlighted = highlight?.includes(index);
                  const isFront = index === 0;
                  const isBack = index === elements.length - 1;
                  
                  return (
                    <div 
                      key={index} 
                      className={`ds-box ${isHighlighted ? 'highlighted' : ''} ${isFront ? 'active' : ''}`}
                    >
                      {isHighlighted && operation === 'enqueue' && (
                        <div className="insert-indicator">↓ NEW</div>
                      )}
                      
                      <div className="ds-value">{value}</div>
                      
                      {isFront && <div className="position-badge">FRONT</div>}
                      {isBack && !isFront && <div className="position-badge">BACK</div>}
                    </div>
                  );
                })
              )}
            </div>
            
            <div className="ds-label back">BACK →</div>
          </div>

          {operation === 'dequeue' && removed_value && (
            <div className="removed-indicator">
              ⬅️ Dequeued: <strong>{removed_value}</strong>
            </div>
          )}
        </div>
      );
    }

    if (type === 'stack') {
      return (
        <div 
          className="ds-section" 
          role="region" 
          aria-label={`Stack data structure: ${name}`}
        >
          <div className="ds-header">
            <span className="ds-title">📚 {name}</span>
            {operation && (
              <span className="ds-operation">
                {operation === 'push' ? '➕ Push' : '➖ Pop'}
              </span>
            )}
          </div>

          <div className="ds-container stack-container">
            <div className="ds-label">TOP ↓</div>
            
            <div className="ds-elements stack">
              {elements.length === 0 ? (
                <div className="empty-ds">Empty Stack</div>
              ) : (
                [...elements].reverse().map((value, displayIndex) => {
                  const actualIndex = elements.length - 1 - displayIndex;
                  const isHighlighted = highlight?.includes(actualIndex);
                  const isTop = actualIndex === elements.length - 1;
                  
                  return (
                    <div 
                      key={actualIndex} 
                      className={`ds-box ${isHighlighted ? 'highlighted' : ''} ${isTop ? 'active' : ''}`}
                    >
                      {isHighlighted && operation === 'push' && (
                        <div className="insert-indicator">↓ NEW</div>
                      )}
                      
                      <div className="ds-value">{value}</div>
                      
                      {isTop && <div className="position-badge">TOP</div>}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {operation === 'pop' && removed_value && (
            <div className="removed-indicator">
              ⬆️ Popped: <strong>{removed_value}</strong>
            </div>
          )}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="graph-with-ds-visualizer">
      <div 
        className="step-description"
        role="status"
        aria-live="polite"
      >
         {graph.current_node ? (
           <div className="description-text">
            <strong>Processing:</strong> Node <span className="node-badge">{graph.current_node}</span>
             {graph.exploring?.length > 0 && (
               <span> → Checking neighbor <span className="node-badge exploring">{graph.exploring[0]}</span></span>
             )}
          </div>
         ) : (
           <div className="description-text">
             <strong>Ready to start traversal</strong>
           </div>
         )}
      </div>

      {/* FIXED: Side-by-side layout wrapper */}
      <div className="viz-grid">
        {graph && renderGraph(graph)}
        {data_structure && renderDataStructure(data_structure)}
      </div>
    </div>
  );
};

export default GraphWithDSVisualizer;