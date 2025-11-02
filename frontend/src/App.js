import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import ExplanationPanel from './components/ExplanationPanel';
import BugDetector from './components/BugDetector';
import VisualExplainer from './components/VisualExplainer';
import './App.css';

function App() {
  const [code, setCode] = useState(`# Paste your code here
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`);
  
  const [language, setLanguage] = useState('python');
  const [level, setLevel] = useState('beginner');
  const [explanation, setExplanation] = useState(null);
  const [bugAnalysis, setBugAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFeature, setActiveFeature] = useState('explain');

  const handleExplain = async () => {
    if (!code.trim()) {
      alert('Please enter some code first!');
      return;
    }

    setLoading(true);
    setError(null);
    setActiveFeature('explain');
    
    try {
      const response = await fetch('http://localhost:8000/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: language,
          level: level
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setExplanation(data);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to explain code. Make sure backend is running on http://localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  const handleDebug = async () => {
    if (!code.trim()) {
      alert('Please enter some code first!');
      return;
    }

    setLoading(true);
    setError(null);
    setActiveFeature('debug');
    
    try {
      const response = await fetch('http://localhost:8000/detect-bugs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: language,
          level: level
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setBugAnalysis(data);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to analyze bugs. Make sure backend is running on http://localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🧠 CodeSense AI</h1>
        <div className="controls">
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="eli5">🍭 ELI5</option>
            <option value="beginner">🌱 Beginner</option>
            <option value="intermediate">🚀 Intermediate</option>
            <option value="expert">🎯 Expert</option>
          </select>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      
      <div className="feature-selector">
        <button 
          className={activeFeature === 'explain' ? 'active' : ''}
          onClick={() => setActiveFeature('explain')}
        >
          💡 Explain Code
        </button>
        <button 
          className={activeFeature === 'debug' ? 'active' : ''}
          onClick={() => setActiveFeature('debug')}
        >
          🐛 Debug Code
        </button>
        {/* NEW: Visual Execution Button */}
        <button 
          className={activeFeature === 'visual' ? 'active' : ''}
          onClick={() => setActiveFeature('visual')}
        >
          🎬 Visual Execution
        </button>
      </div>

      <div className="main-content">
        <div className="editor-section">
          <h2>📝 Code Input</h2>
          <CodeEditor 
            value={code}
            onChange={setCode}
            language={language}
          />
        </div>

        <div className="explanation-section">
          {/* ========================================
              UPDATE HEADING (Line 157-163)
              ======================================== */}
          <h2>
            {activeFeature === 'explain' && '💡 Explanation'}
            {activeFeature === 'debug' && '🐛 Bug Analysis'}
            {activeFeature === 'visual' && '🎬 Visual Execution'}
          </h2>
          
          {/* Explain Panel */}
          {activeFeature === 'explain' && explanation && (
            <ExplanationPanel explanation={explanation} />
          )}
          
          {/* Debug Panel */}
          {activeFeature === 'debug' && bugAnalysis && (
            <BugDetector bugs={bugAnalysis} />
          )}
          
          
          {/* NEW: Visual Explainer */}
          {activeFeature === 'visual' && (
            <VisualExplainer code={code} language={language} />
          )}
          
          {/* Placeholders */}
          {activeFeature === 'explain' && !explanation && (
            <div className="placeholder">
              <div className="placeholder-icon">🤔</div>
              <h3>Ready to understand your code?</h3>
              <p>Paste your code on the left and click "Explain This Code"</p>
            </div>
          )}
          
          {activeFeature === 'debug' && !bugAnalysis && (
            <div className="placeholder">
              <div className="placeholder-icon">🔍</div>
              <h3>Ready to find bugs?</h3>
              <p>Paste your code on the left and click "Find Bugs"</p>
            </div>
          )}
          
          {/* NEW: Visual placeholder (optional - VisualExplainer has its own) */}
          {activeFeature === 'visual' && !code.trim() && (
            <div className="placeholder">
              <div className="placeholder-icon">🎬</div>
              <h3>Ready to see your code in action?</h3>
              <p>Paste your code on the left to visualize execution</p>
            </div>
          )}
        </div>
      </div>

      <div className="action-buttons">
        <button 
          className="explain-btn" 
          onClick={handleExplain}
          disabled={loading}
        >
          {loading && activeFeature === 'explain' ? '🤔 Analyzing...' : '🚀 Explain This Code'}
        </button>
        <button 
          className="debug-btn" 
          onClick={handleDebug}
          disabled={loading}
        >
          {loading && activeFeature === 'debug' ? '🔍 Analyzing...' : '🐛 Find Bugs'}
        </button>
      </div>
    </div>
  );
}

export default App;