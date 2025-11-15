import React, { useRef, useEffect, useState } from 'react';
import './CodeEditor.css';

const CodeEditor = ({ value, onChange, language, currentLine = null, readOnly = false }) => {
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const [lineCount, setLineCount] = useState(1);

  // Update line count when value changes
  useEffect(() => {
    const lines = value.split('\n').length;
    setLineCount(lines);
    console.log('📝 Code has', lines, 'lines, current line:', currentLine);
  }, [value, currentLine]);

  // Sync scroll between textarea and line numbers
  const handleScroll = (e) => {
    if (lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = e.target.scrollTop;
    }
  };

  // Handle tab key for indentation
  const handleTab = (e) => {
    if (e.key === 'Tab' && !readOnly) {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newValue = value.substring(0, start) + '    ' + value.substring(end);
      onChange(newValue);
      
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
        }
      }, 0);
    }
  };

  // Auto-scroll to current line when it changes
  useEffect(() => {
    if (currentLine && textareaRef.current && lineNumbersRef.current) {
      const lineHeight = 22.4; // Match CSS line height
      const scrollPosition = (currentLine - 1) * lineHeight - 100; // Center it
      
      textareaRef.current.scrollTo({
        top: Math.max(0, scrollPosition),
        behavior: 'smooth'
      });
      
      console.log('🎯 Scrolling to line', currentLine, 'at position', scrollPosition);
    }
  }, [currentLine]);

  return (
    <div className="code-editor-container">
      <div className="code-editor-wrapper">
        <div className="line-numbers" ref={lineNumbersRef}>
          {Array.from({ length: lineCount }, (_, i) => (
            <div 
              key={i + 1} 
              className={`line-number ${currentLine === i + 1 ? 'current-line' : ''}`}
            >
              {i + 1}
            </div>
          ))}
        </div>
        
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => !readOnly && onChange(e.target.value)}
          onScroll={handleScroll}
          onKeyDown={handleTab}
          placeholder={`Paste your ${language} code here...`}
          spellCheck={false}
          className="code-textarea"
          readOnly={readOnly}
        />
      </div>
      
      <div className="code-editor-footer">
        <span className="editor-info">Language: {language}</span>
        <span className="editor-info">{lineCount} lines</span>
        <span className="editor-info">{value.length} characters</span>
        {currentLine && <span className="editor-info" style={{ color: '#58a6ff', fontWeight: 'bold' }}>
          ▶ Line {currentLine}
        </span>}
      </div>
    </div>
  );
};

export default CodeEditor;