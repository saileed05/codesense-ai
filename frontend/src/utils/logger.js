// src/utils/logger.js

const isDevelopment = process.env.NODE_ENV === 'development';
const disableLogs = process.env.REACT_APP_DISABLE_LOGS === 'true';
const DEBUG = isDevelopment || !disableLogs;

const logger = {
  log: (...args) => {
    if (DEBUG) {
      console.log(...args);
    }
  },
  warn: (...args) => {
    if (DEBUG) {
      console.warn(...args);
    }
  },
  error: (...args) => {
    // Always log errors, even in production
    console.error(...args);
  },
  info: (...args) => {
    if (DEBUG) {
      console.info(...args);
    }
  },
  group: (...args) => {
    if (DEBUG) {
      console.group(...args);
    }
  },
  groupEnd: () => {
    if (DEBUG) {
      console.groupEnd();
    }
  }
};

export default logger;