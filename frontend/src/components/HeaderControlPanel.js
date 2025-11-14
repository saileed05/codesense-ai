import React from 'react';
import { Play, Pause, RotateCcw, ChevronLeft, ChevronRight, BookOpen, Sparkles } from 'lucide-react';
import './HeaderControlPanel.css';

const HeaderControlPanel = ({
  language,
  level,
  executionSpeed,
  isExecuting,
  isPaused,
  loading,
  onLanguageChange,
  onLevelChange,
  onSpeedChange,
  onExplainCode,
  onVisualExplain,
  onPlay,
  onPause,
  onReset,
  onNext,
  onPrevious,
  viewMode,
  currentStep,
  totalSteps
}) => {
  return (
    <header className="header-control-panel">
      {/* Left Side - Logo & Settings */}
      <div className="header-left">
        <div className="logo">
          <span className="logo-icon">🧠</span>
          <h1>CodeSense AI</h1>
        </div>
        
        <div className="settings-group">
          <select 
            value={language} 
            onChange={(e) => onLanguageChange(e.target.value)}
            className="header-select"
          >
            <option value="python">🐍 Python</option>
            <option value="javascript">⚡ JavaScript</option>
            <option value="java">☕ Java</option>
            <option value="cpp">⚙️ C++</option>
          </select>
          
          <select 
            value={level} 
            onChange={(e) => onLevelChange(e.target.value)}
            className="header-select"
          >
            <option value="eli5">🍭 ELI5</option>
            <option value="beginner">🌱 Beginner</option>
            <option value="intermediate">🚀 Intermediate</option>
            <option value="expert">🎯 Expert</option>
          </select>
        </div>
      </div>

      {/* Center - Action Buttons WITH ICONS */}
      <div className="header-center">
        <button 
          className="action-btn explain-btn"
          onClick={onExplainCode}
          disabled={loading}
        >
          <BookOpen size={18} />
          <span className="btn-text">Explain Code</span>
        </button>
        
        <button 
          className="action-btn visual-btn"
          onClick={onVisualExplain}
          disabled={loading}
        >
          <Sparkles size={18} />
          <span className="btn-text">Visual Explain</span>
        </button>
      </div>

      {/* Right Side - Playback Controls WITH PROGRESS BAR */}
      <div className="header-right">
        {viewMode === 'visual' && totalSteps > 0 && (
          <>
            <div className="step-indicator">
              <span className="step-text">Step {currentStep + 1} / {totalSteps}</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
                />
              </div>
            </div>
            
            <div className="playback-controls">
              <button 
                className="control-btn"
                onClick={onReset}
                title="Reset (Ctrl+R)"
              >
                <RotateCcw size={18} />
              </button>
              
              <button 
                className="control-btn"
                onClick={onPrevious}
                disabled={currentStep === 0}
                title="Previous (Ctrl+←)"
              >
                <ChevronLeft size={18} />
              </button>
              
              <button 
                className="control-btn play-control"
                onClick={isPaused || !isExecuting ? onPlay : onPause}
                title={isPaused || !isExecuting ? 'Play (Ctrl+Space)' : 'Pause'}
              >
                {isPaused || !isExecuting ? <Play size={20} /> : <Pause size={20} />}
              </button>
              
              <button 
                className="control-btn"
                onClick={onNext}
                disabled={currentStep === totalSteps - 1}
                title="Next (Ctrl+→)"
              >
                <ChevronRight size={18} />
              </button>
            </div>
            
            <select 
              value={executionSpeed} 
              onChange={(e) => onSpeedChange(Number(e.target.value))}
              className="speed-select"
            >
              <option value={2500}>🐌 0.5x</option>
              <option value={1500}>⚡ 1x</option>
              <option value={1000}>🚀 1.5x</option>
              <option value={500}>⚡⚡ 2x</option>
            </select>
          </>
        )}
      </div>
    </header>
  );
};

export default HeaderControlPanel;