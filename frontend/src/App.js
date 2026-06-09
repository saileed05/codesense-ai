import React, { useState, useEffect } from 'react';
import HeaderControlPanel from './components/HeaderControlPanel';
import CodeExecutionPanel from './components/CodeExecutionPanel';
import { ExplanationOverlay, StatusBar } from './components/ExplanationOverlay';
import './NewApp.css';

// ===== DEBUG CONFIGURATION =====
const DEBUG = process.env.NODE_ENV !== 'production' || process.env.REACT_APP_DISABLE_LOGS !== 'true';
// ================================

const API_URL = process.env.REACT_APP_API_URL || 'https://codesense-ai-dx0b.onrender.com';

function App() {
  // Code and settings state
  const [code, setCode] = useState(`# Paste your code here
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`);
  
  const [language, setLanguage] = useState('python');
  const [level, setLevel] = useState('beginner');
  
  // Execution state
  const [currentLine, setCurrentLine] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionSpeed, setExecutionSpeed] = useState(1500);
  const [isPaused, setIsPaused] = useState(false);
  
  // View mode state
  const [viewMode, setViewMode] = useState('editor');
  const [explanation, setExplanation] = useState(null);
  const [visualSteps, setVisualSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  
  // Status state
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  // ==================== EXPLAIN CODE ====================
  const handleExplainCode = async () => {
    if (!code.trim()) {
      showStatus('error', 'Please enter some code first!');
      return;
    }

    setLoading(true);
    setViewMode('explain');
    showStatus('processing', 'Analyzing your code...');
    
    try {
      const response = await fetch(`${API_URL}/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, level })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setExplanation(data);
      showStatus('success', 'Code explanation generated!');
    } catch (error) {
      if (DEBUG) console.error('Explain error:', error);
      showStatus('error', `Failed: ${error.message}`);
      setViewMode('editor');
    } finally {
      setLoading(false);
    }
  };

  // ==================== VISUAL EXPLAIN ====================
  const handleVisualExplain = async () => {
    if (!code.trim()) {
      showStatus('error', 'Please enter some code first!');
      return;
    }

    setLoading(true);
    setViewMode('visual');
    showStatus('processing', 'Generating visualization...');
    
    try {
      const response = await fetch(`${API_URL}/visualize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, level })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }
      
      const data = await response.json();
      const steps = data.steps || [];
      
      setVisualSteps(steps);
      setCurrentStep(0);
      
      if (steps.length > 0 && steps[0]?.line !== undefined) {
        setCurrentLine(steps[0].line);
        if (DEBUG) console.log('🎬 Starting at line:', steps[0].line);
      }
      
      setIsExecuting(false);
      setIsPaused(true);
      showStatus('success', 'Visualization ready! Press play to start.');
    } catch (error) {
      if (DEBUG) console.error('Visualization error:', error);
      showStatus('error', `Failed: ${error.message}`);
      setViewMode('editor');
    } finally {
      setLoading(false);
    }
  };

  // ==================== PLAYBACK CONTROLS ====================
  const handlePlay = () => {
    if (visualSteps.length === 0) {
      showStatus('error', 'No visualization loaded. Click "Visual Explain" first.');
      return;
    }
    setIsExecuting(true);
    setIsPaused(false);
    showStatus('info', 'Execution started');
  };

  const handlePause = () => {
    setIsPaused(true);
    showStatus('info', 'Execution paused');
  };

  const handleReset = () => {
    setCurrentStep(0);
    setIsPaused(true);
    setIsExecuting(false);
    if (visualSteps.length > 0 && visualSteps[0]?.line !== undefined) {
      setCurrentLine(visualSteps[0].line);
    } else {
      setCurrentLine(null);
    }
    showStatus('info', 'Reset to beginning');
  };

  const handleNext = () => {
    if (currentStep < visualSteps.length - 1) {
      const nextStep = currentStep + 1;
      const nextStepData = visualSteps[nextStep];
      setCurrentStep(nextStep);
      if (nextStepData?.line !== undefined) {
        setCurrentLine(nextStepData.line);
        if (DEBUG) console.log('➡️ Moving to step', nextStep, 'line:', nextStepData?.line);
      }
    } else {
      showStatus('success', 'Execution completed!');
      setIsExecuting(false);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      const prevStep = currentStep - 1;
      const prevStepData = visualSteps[prevStep];
      setCurrentStep(prevStep);
      if (prevStepData?.line !== undefined) {
        setCurrentLine(prevStepData.line);
        if (DEBUG) console.log('⬅️ Moving to step', prevStep, 'line:', prevStepData?.line);
      }
    }
  };

  // ==================== KEYBOARD SHORTCUTS ====================
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (viewMode !== 'visual') return;
      if (e.target.matches('input, textarea')) return;
      
      if ((e.ctrlKey && e.code === 'Space') || e.code === 'Space') {
        e.preventDefault();
        if (isPaused || !isExecuting) {
          handlePlay();
        } else {
          handlePause();
        }
      } else if (e.ctrlKey && e.code === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      } else if (e.ctrlKey && e.code === 'ArrowLeft') {
        e.preventDefault();
        handlePrevious();
      } else if (e.ctrlKey && e.code === 'KeyR') {
        e.preventDefault();
        handleReset();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [viewMode, isPaused, isExecuting]);

  // ==================== AUTO PLAYBACK ====================
  useEffect(() => {
    let interval;
    
    if (isExecuting && !isPaused && visualSteps.length > 0) {
      if (currentStep < visualSteps.length - 1) {
        interval = setInterval(() => {
          setCurrentStep(prev => {
            const nextStep = prev + 1;
            const nextStepData = visualSteps[nextStep];
            if (nextStepData?.line !== undefined) {
              setCurrentLine(nextStepData.line);
              if (DEBUG) console.log('⏩ Auto-advancing to step', nextStep, 'line:', nextStepData.line);
            }
            if (nextStep >= visualSteps.length - 1) {
              setIsExecuting(false);
              showStatus('success', 'Execution completed!');
            }
            return nextStep;
          });
        }, executionSpeed);
      } else {
        setIsExecuting(false);
        showStatus('success', 'Execution completed!');
      }
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isExecuting, isPaused, currentStep, visualSteps, executionSpeed]);

  // ==================== UTILITY FUNCTIONS ====================
  const showStatus = (type, message) => {
    setStatus({ type, message });
    setTimeout(() => setStatus({ type: '', message: '' }), 4000);
  };

  const handleCloseExplanation = () => {
    setViewMode('editor');
    setExplanation(null);
  };

  const handleBackToEditor = () => {
    setViewMode('editor');
    setIsExecuting(false);
    setIsPaused(true);
    setCurrentLine(null);
  };

  return (
    <div className="app-container">
      <HeaderControlPanel
        language={language}
        level={level}
        executionSpeed={executionSpeed}
        isExecuting={isExecuting}
        isPaused={isPaused}
        loading={loading}
        onLanguageChange={setLanguage}
        onLevelChange={setLevel}
        onSpeedChange={setExecutionSpeed}
        onExplainCode={handleExplainCode}
        onVisualExplain={handleVisualExplain}
        onPlay={handlePlay}
        onPause={handlePause}
        onReset={handleReset}
        onNext={handleNext}
        onPrevious={handlePrevious}
        viewMode={viewMode}
        currentStep={currentStep}
        totalSteps={visualSteps.length}
      />

      <CodeExecutionPanel
        code={code}
        language={language}
        currentLine={currentLine}
        viewMode={viewMode}
        visualSteps={visualSteps}
        currentStep={currentStep}
        onCodeChange={setCode}
        onBackToEditor={handleBackToEditor}
      />

      {viewMode === 'explain' && explanation && (
        <ExplanationOverlay explanation={explanation} onClose={handleCloseExplanation} />
      )}

      <StatusBar status={status} />
    </div>
  );
}

export default App;