// Learn more: https://github.com/testing-library/jest-dom
require('@testing-library/jest-dom');

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() { }
  disconnect() { }
  observe() { }
  takeRecords() {
    return [];
  }
  unobserve() { }
};

// Mock localStorage
const localStorageMock = (() => {
  let store = {};

  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = String(value);
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (index) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Mock fetch global
global.fetch = jest.fn();

// Mock AbortController
global.AbortController = jest.fn().mockImplementation(() => ({
  abort: jest.fn(),
  signal: {
    aborted: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  },
}));

// Mock next/navigation
jest.mock('next/navigation', () => require('./__tests__/__mocks__/next-navigation'));

// Mock next/script
jest.mock('next/script', () => require('./__tests__/__mocks__/next-script'));

// Mock Google Client ID for tests
if (typeof window !== 'undefined') {
  window.__GOOGLE_CLIENT_ID__ = 'test-google-client-id';
}

// Mock import.meta.env for Vite/ESM compatibility
if (typeof global !== 'undefined') {
  global.import = global.import || {};
  global.import.meta = global.import.meta || {};
  global.import.meta.env = global.import.meta.env || {
    DEV: false,
    PROD: true,
    MODE: 'test',
  };
}
