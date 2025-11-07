import React, { useState, useEffect } from 'react';
import ArrayVisualizer from './visualizations/ArrayVisualizer';
import GraphVisualizer from './visualizations/GraphVisualizer';
import QueueVisualizer from './visualizations/QueueVisualizer';
import GraphWithDSVisualizer from './visualizations/GraphWithDSVisualizer';
import './VisualExplainer.css';

const VisualExplainer = ({ code, language, apiUrl }) => {
  const [steps, setSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(2500);

  const API_URL = apiUrl || process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchVisualization = async () => {
    if (!code.trim()) {
      setError('Please enter some code first!');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      console.log('🎬 Fetching visualization from:', `${API_URL}/visualize`);
      
      const response = await fetch(`${API_URL}/visualize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, level: 'beginner' })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Received steps:', data.steps?.length || 0);
      
      setSteps(data.steps || []);
      setCurrentStep(0);
      setIsPlaying(false);
      
    } catch (err) {
      console.error('❌ Visualization error:', err);
      setError(`Failed to generate visualization: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      setIsPlaying(false);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const reset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  const togglePlay = () => {
    if (currentStep === steps.length - 1) {
      setCurrentStep(0);
    }
    setIsPlaying(!isPlaying);
  };

  useEffect(() => {
    let interval;
    if (isPlaying && currentStep < steps.length - 1) {
      interval = setInterval(nextStep, playbackSpeed);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentStep, steps, playbackSpeed]);

  const renderVisualization = (viz) => {
    if (!viz) return null;

    switch (viz.type) {
      case 'graph_with_ds':
        return <GraphWithDSVisualizer data={viz} />;
      
      case 'array':
        return <ArrayVisualizer data={viz} />;
      
      case 'queue':
        return <QueueVisualizer data={viz} />;
      
      case 'visited':
        return <QueueVisualizer data={viz} />;
      
      case 'graph':
        return <GraphVisualizer data={viz} />;
      
      case 'dict':
        return (
          <div className="dict-display">
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
          <div className="variable-display">
            <div className="var-name">{viz.name}</div>
            <div className="var-value">{viz.value}</div>
            <div className="var-type">{viz.var_type}</div>
          </div>
        );
      
      case 'none':
        return (
          <div className="no-visualization">
            <p>ℹ️ {viz.message || 'No visualization available for this step'}</p>
          </div>
        );
      
      case 'error':
        return (
          <div className="viz-error">
            <p>⚠️ {viz.message}</p>
          </div>
        );
      
      default:
        return <div className="unknown-viz">Unknown visualization type: {viz.type}</div>;
    }
  };

  const currentStepData = steps[currentStep];

  if (steps.length === 0 && !loading && !error) {
    return (
      <div className="visual-empty">
        <div className="empty-icon">🎬</div>
        <h3>Ready to see your code in action?</h3>
        <p>Watch variables, arrays, and data structures come to life</p>
        <button onClick={fetchVisualization} className="generate-btn">
          🚀 Generate Visual Execution
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="visual-loading">
        <div className="spinner"></div>
        <p>🔄 Analyzing code and generating visualization...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="visual-error">
        <div className="error-icon">⚠️</div>
        <h3>Visualization Failed</h3>
        <p>{error}</p>
        <button onClick={fetchVisualization} className="retry-btn">
          🔄 Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="visual-explainer">
      <div className="controls-bar">
        <div className="playback-controls">
          <button onClick={reset} className="control-btn reset-btn" title="Reset">
            ⏮️
          </button>
          <button onClick={prevStep} disabled={currentStep === 0} className="control-btn" title="Previous">
            ⏪
          </button>
          <button onClick={togglePlay} className="control-btn play-btn" title={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          <button onClick={nextStep} disabled={currentStep === steps.length - 1} className="control-btn" title="Next">
            ⏩
          </button>
        </div>

        <div className="speed-control">
          <label>Speed:</label>
          <select value={playbackSpeed} onChange={(e) => setPlaybackSpeed(Number(e.target.value))}>
            <option value={2500}>0.5x</option>
            <option value={1500}>1x</option>
            <option value={1000}>1.5x</option>
            <option value={500}>2x</option>
          </select>
        </div>
      </div>

      <div className="progress-section">
        <div className="progress-info">
          <span className="step-counter">Step {currentStep + 1} of {steps.length}</span>
          <span className="line-info">Line {currentStepData?.line || 0}</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }} />
        </div>
      </div>

      <div className="visual-content">
        <div className="code-display">
          <div className="code-label">Current Line:</div>
          <pre className="code-line"><code>{currentStepData?.code || ''}</code></pre>
          <div className="code-description">{currentStepData?.description || ''}</div>
        </div>

        <div className="visualization-area">
          <div className="viz-label">Memory & Variables:</div>
          <div className="viz-container">
            {currentStepData?.visualization ? 
              renderVisualization(currentStepData.visualization) : 
              <div className="no-viz">No visualization for this step</div>
            }
          </div>
        </div>
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

      <div className="actions">
        <button onClick={fetchVisualization} className="regenerate-btn">
          🔄 Regenerate Visualization
        </button>
      </div>
    </div>
  );
};

export default VisualExplainer;