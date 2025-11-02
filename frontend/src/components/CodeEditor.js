import React from 'react';

const CodeEditor = ({ value, onChange, language }) => {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Paste your ${language} code here...`}
        spellCheck={false}
        style={{
          flex: 1,
          minHeight: '500px',
          background: '#0d1117',
          color: '#c9d1d9',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '1rem',
          fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
          fontSize: '14px',
          lineHeight: '1.6',
          resize: 'none',
          outline: 'none',
        }}
      />
      <div style={{ 
        marginTop: '0.5rem', 
        fontSize: '0.85rem', 
        color: '#8b949e',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <span>Language: {language}</span>
        <span>{value.split('\n').length} lines</span>
      </div>
    </div>
  );
};

export default CodeEditor;