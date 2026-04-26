import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock Three.js global
global.THREE = {
  WebGLRenderer: vi.fn(),
  Scene: vi.fn(),
  PerspectiveCamera: vi.fn(),
  AmbientLight: vi.fn(),
  DirectionalLight: vi.fn(),
  PointLight: vi.fn(),
  PCFSoftShadowMap: 'PCFSoftShadowMap',
};

// Mock ResizeObserver for React Three Fiber Canvas
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {
    // Mock observe - call callback with mock entry
    this.callback([{ contentRect: { width: 800, height: 600 } }], this);
  }
  unobserve() {}
  disconnect() {}
};
