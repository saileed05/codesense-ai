/**
 * Dynamic Visualizer Component Registry
 * 
 * This registry maps visualization types to their corresponding React components.
 * Add new visualizers here without modifying switch statements.
 */

import ArrayVisualizer from './visualizations/ArrayVisualizer';
import GraphVisualizer from './visualizations/GraphVisualizer';
import QueueVisualizer from './visualizations/QueueVisualizer';
import GraphWithDSVisualizer from './visualizations/GraphWithDSVisualizer';
import StackVisualizer from './visualizations/StackVisualizer';

// Registry object mapping type strings to components
const visualizerRegistry = {
  // Graph algorithms
  'graph_with_ds': GraphWithDSVisualizer,
  'graph': GraphVisualizer,
  
  // Data structures
  'array': ArrayVisualizer,
  'queue': QueueVisualizer,
  'stack': StackVisualizer,
  'visited': QueueVisualizer, // Visited sets use queue-like display
  
  // Dictionary/Hash map
  'dict': 'dict', // Special case: rendered inline
  
  // Simple variables
  'variable': 'variable', // Special case: rendered inline
  
  // Error states
  'none': 'none',
  'error': 'error',
};

/**
 * Get the visualizer component for a given type
 * @param {string} type - The visualization type
 * @returns {React.Component|string|null} Component, special type string, or null
 */
export const getVisualizer = (type) => {
  return visualizerRegistry[type] || null;
};

/**
 * Check if a visualization type exists in the registry
 * @param {string} type - The visualization type
 * @returns {boolean}
 */
export const hasVisualizer = (type) => {
  return type in visualizerRegistry;
};

/**
 * Register a new visualizer component
 * Useful for plugins or dynamic extensions
 * @param {string} type - The visualization type
 * @param {React.Component|string} component - The component or special type
 */
export const registerVisualizer = (type, component) => {
  visualizerRegistry[type] = component;
  console.log(`✅ Registered visualizer: ${type}`);
};

/**
 * Get all registered visualization types
 * @returns {string[]}
 */
export const getRegisteredTypes = () => {
  return Object.keys(visualizerRegistry);
};

/**
 * Unregister a visualizer (for cleanup or testing)
 * @param {string} type - The visualization type
 */
export const unregisterVisualizer = (type) => {
  if (type in visualizerRegistry) {
    delete visualizerRegistry[type];
    console.log(`🗑️ Unregistered visualizer: ${type}`);
  }
};

export default visualizerRegistry;