import React, { useEffect, useState, useRef } from 'react';
import ArrayVisualizer from './visualizations/ArrayVisualizer';
import GraphVisualizer from './visualizations/GraphVisualizer';
import QueueVisualizer from './visualizations/QueueVisualizer';
import GraphWithDSVisualizer from './visualizations/GraphWithDSVisualizer';
import StackVisualizer from './visualizations/StackVisualizer';
import './VisualExplainer.css';

const VisualExplainer = ({ code, language, apiUrl, preloadedSteps, currentStep }) => {
  const [steps, setSteps] = useState([]);
  const [renderKey, setRenderKey] = useState(0);
  const containerRef = useRef(null);

  // FIX 1: Update steps when preloadedSteps changes
  useEffect(() => {
    if (preloadedSteps && preloadedSteps.length > 0) {
      console.log('📊 Loading steps:', preloadedSteps.length);
      setSteps(preloadedSteps);
      setRenderKey(prev => prev + 1);
    }
  }, [preloadedSteps]);

  // FIX 2: Force re-render when currentStep changes AND auto-scroll
  useEffect(() => {
    console.log('🔄 Current step changed to:', currentStep);
    setRenderKey(prev => prev + 1);
    
    // Auto-scroll to top of visualization
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  }, [currentStep]);

  // FIX 3: Debug current step data
  useEffect(() => {
    if (steps.length > 0 && currentStep < steps.length) {
      const stepData = steps[currentStep];
      console.log('📍 Step', currentStep, 'data:', stepData);
    }
  }, [steps, currentStep]);

  const renderVisualization = (viz) => {
    if (!viz) {
      return (
        <div className="no-visualization">
          <p>ℹ️ No visualization data for this step</p>
        </div>
      );
    }

    // FIX 4: Add key prop to force re-mount on step change
    const vizKey = `${viz.type}-${currentStep}-${renderKey}`;

    switch (viz.type) {
      case 'graph_with_ds':
        return <GraphWithDSVisualizer key={vizKey} data={viz} />;
      
      case 'array':
        return <ArrayVisualizer key={vizKey} data={viz} />;
      
      case 'queue':
        return <QueueVisualizer key={vizKey} data={viz} />;

      case 'stack':
        return <StackVisualizer key={vizKey} data={viz} />;
      
      case 'visited':
        return <QueueVisualizer key={vizKey} data={viz} />;
      
      case 'graph':
        return <GraphVisualizer key={vizKey} data={viz} />;
      
      case 'dict':
        return (
          <div className="dict-display" key={vizKey}>
            <div className="dict-header">
              <span className="dict-name">{viz.name}</span>
              <span className="dict-count">{Object.keys(viz.data || {}).length} keys</span>
            </div>
            <div className="dict-content">
              {viz.formatted && viz.formatted.map((line, idx) => (
                <div key={idx} className="dict-line">
                  <code>{line}</code>
                </div>
              ))}
            </div>
          </div>
        );
      
      case 'variable':
        return (
          <div className="variable-display" key={vizKey}>
            <div className="var-name">{viz.name}</div>
            <div className="var-value">{viz.value}</div>
            <div className="var-type">{viz.var_type}</div>
          </div>
        );
      
      case 'none':
        return (
          <div className="no-visualization" key={vizKey}>
            <p>ℹ️ {viz.message || 'No visualization available for this step'}</p>
          </div>
        );
      
      case 'error':
        return (
          <div className="viz-error" key={vizKey}>
            <p>⚠️ {viz.message}</p>
          </div>
        );
      
      default:
        return <div className="unknown-viz" key={vizKey}>Unknown visualization type: {viz.type}</div>;
    }
  };

  if (steps.length === 0) {
    return (
      <div className="visual-empty">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <h3>Loading visualization...</h3>
        <p>Preparing step-by-step execution</p>
      </div>
    );
  }

  // FIX 5: Safely get current step data with bounds checking
  const currentStepData = steps[currentStep] || steps[0];
  
  // FIX 6: Debug info - remove this after testing
  console.log('🎯 Rendering step', currentStep, 'of', steps.length, 'visualization:', currentStepData?.visualization?.type);

  return (
    <div className="visual-explainer-simple" ref={containerRef}>
      {/* FIX 7: Add step counter for debugging */}
      <div style={{
        position: 'sticky',
        top: 0,
        background: '#010409',
        padding: '0.5rem',
        borderBottom: '1px solid #30363d',
        zIndex: 100,
        fontSize: '0.9rem',
        color: '#8b949e'
      }}>
        Step {currentStep + 1} of {steps.length}
        {currentStepData?.line && ` | Line: ${currentStepData.line}`}
      </div>

      <div className="viz-container">
        {currentStepData?.visualization ? 
          renderVisualization(currentStepData.visualization) : 
          <div className="no-viz">No visualization for this step</div>
        }
      </div>

      <div className="legend">
        <h4>Legend:</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-box highlighted"></div>
            <span>Current operation</span>
          </div>
          <div className="legend-item">
            <div className="legend-box filled"></div>
            <span>Filled slot</span>
          </div>
          <div className="legend-item">
            <div className="legend-box empty"></div>
            <span>Empty slot</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualExplainer;