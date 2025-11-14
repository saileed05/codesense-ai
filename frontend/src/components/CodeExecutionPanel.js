import React, { useState } from 'react';
import CodeEditor from './CodeEditor';
import VisualExplainer from './VisualExplainer';
import { ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import './CodeExecutionPanel.css';

const CodeExecutionPanel = ({
  code,
  language,
  currentLine,
  viewMode,
  visualSteps,
  currentStep,
  onCodeChange,
  onBackToEditor
}) => {
  // NEW: Collapsible code panel state
  const [isCodePanelCollapsed, setIsCodePanelCollapsed] = useState(false);
  
  console.log('CodeExecutionPanel render:', { 
    viewMode, 
    currentStep, 
    totalSteps: visualSteps?.length,
    hasSteps: !!visualSteps && visualSteps.length > 0,
    currentLine // Debug line number
  });
  
  const renderVisualization = () => {
    if (!visualSteps || visualSteps.length === 0) {
      return (
        <div className="empty-visualization">
          <div className="loading-spinner">
            <div className="spinner"></div>
          </div>
          <h3>Generating Visualization...</h3>
          <p>Analyzing your code and building step-by-step execution</p>
        </div>
      );
    }

    const stepData = visualSteps[currentStep] || visualSteps[0];
    
    return (
      <div className="visualization-content">
        {/* FIXED: Show current step info */}
        <div className="current-line-display">
          <div className="line-badge">
            <span className="line-label">
              Step {currentStep + 1}/{visualSteps.length} | Line {stepData.line || 'N/A'}
            </span>
          </div>
          <div className="code-preview-card">
            <pre className="code-preview">
              <code>{stepData.code || 'No code available'}</code>
            </pre>
          </div>
          <div className="line-description">
            💡 {stepData.description || 'Processing step...'}
          </div>
        </div>

        <div className="viz-area">
          <VisualExplainer 
            code={code}
            language={language}
            apiUrl=""
            preloadedSteps={visualSteps}
            currentStep={currentStep}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="code-execution-panel">
      {viewMode === 'editor' && (
        <div className="editor-mode">
          <div className="editor-header">
            <h2>📝 Code Input</h2>
            <div className="editor-info">
              <span>{code.split('\n').length} lines</span>
              <span>•</span>
              <span>{code.length} characters</span>
            </div>
          </div>
          <CodeEditor 
            value={code}
            onChange={onCodeChange}
            language={language}
            currentLine={currentLine}
          />
        </div>
      )}

      {viewMode === 'visual' && (
        <div className="visual-mode">
          <div className="visual-header">
            <button className="back-btn" onClick={onBackToEditor}>
              <ArrowLeft size={18} />
              <span>Back to Editor</span>
            </button>
            <h2>🎬 Visual Execution</h2>
            <div className="spacer"></div>
          </div>
          
          <div className="visual-content-wrapper">
            {/* NEW: Updated split-view with collapsible support */}
            <div className={`split-view ${isCodePanelCollapsed ? 'code-collapsed' : ''}`}>
              
              {/* Code Panel with Collapse Button */}
              <div className="code-panel">
                <div className="code-panel-header">
                  <span className="panel-title">📄 Code</span>
                  <button 
                    className="collapse-btn" 
                    onClick={() => setIsCodePanelCollapsed(!isCodePanelCollapsed)}
                    aria-label={isCodePanelCollapsed ? "Expand code panel" : "Collapse code panel"}
                  >
                    {isCodePanelCollapsed ? <ChevronDown size={20} /> : <ChevronUp size={20} />}
                    <span>{isCodePanelCollapsed ? 'Show Code' : 'Hide Code'}</span>
                  </button>
                </div>
                
                {!isCodePanelCollapsed && (
                  <div className="code-panel-content">
                    <CodeEditor 
                      value={code}
                      onChange={() => {}}
                      language={language}
                      currentLine={currentLine}
                      readOnly={true}
                    />
                  </div>
                )}
              </div>
              
              {/* Visualization Panel */}
              <div className="visualization-panel">
                {renderVisualization()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeExecutionPanel;