/**
 * Dynamic Visualizer Component Registry
 */
import ArrayVisualizer from './visualizations/ArrayVisualizer';
import GraphVisualizer from './visualizations/GraphVisualizer';
import QueueVisualizer from './visualizations/QueueVisualizer';
import GraphWithDSVisualizer from './visualizations/GraphWithDSVisualizer';
import StackVisualizer from './visualizations/StackVisualizer';

// ===== DEBUG CONFIGURATION =====
const DEBUG = process.env.NODE_ENV !== 'production' || process.env.REACT_APP_DISABLE_LOGS !== 'true';
// ================================

const visualizerRegistry = {
  'graph_with_ds': GraphWithDSVisualizer,
  'graph': GraphVisualizer,
  'array': ArrayVisualizer,
  'queue': QueueVisualizer,
  'stack': StackVisualizer,
  'visited': QueueVisualizer,
  'dict': 'dict',
  'variable': 'variable',
  'none': 'none',
  'error': 'error',
};

export const getVisualizer = (type) => {
  return visualizerRegistry[type] || null;
};

export const hasVisualizer = (type) => {
  return type in visualizerRegistry;
};

export const registerVisualizer = (type, component) => {
  visualizerRegistry[type] = component;
  if (DEBUG) console.log(`✅ Registered visualizer: ${type}`);
};

export const getRegisteredTypes = () => {
  return Object.keys(visualizerRegistry);
};

export const unregisterVisualizer = (type) => {
  if (type in visualizerRegistry) {
    delete visualizerRegistry[type];
    if (DEBUG) console.log(`🗑️ Unregistered visualizer: ${type}`);
  }
};

export default visualizerRegistry;