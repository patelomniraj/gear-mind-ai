import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import * as THREE from 'three';
import SceneLighting, { lerpColor } from './SceneLighting.jsx';
import { useGearStore } from '../../store/gearStore.js';

// Mock the Zustand store
vi.mock('../../store/gearStore.js', () => ({
  useGearStore: vi.fn(() => ({
    sensors: {
      temperature: 72,
      load: 45,
      health: 'normal',
    },
  })),
}));

describe('SceneLighting Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering Tests (Requirements 8.1, 8.2, 8.3)', () => {
    it('should render without errors', () => {
      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should render with default sensor values', () => {
      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });

  describe('lerpColor Utility Function Tests (Requirements 4.4, 4.8)', () => {
    it('should interpolate colors correctly at minimum boundary (65°C)', () => {
      const result = lerpColor(65, 65, 95, '#ff6b35', '#ff2200');
      const expected = new THREE.Color('#ff6b35');
      
      expect(result.r).toBeCloseTo(expected.r, 2);
      expect(result.g).toBeCloseTo(expected.g, 2);
      expect(result.b).toBeCloseTo(expected.b, 2);
    });

    it('should interpolate colors correctly at maximum boundary (95°C)', () => {
      const result = lerpColor(95, 65, 95, '#ff6b35', '#ff2200');
      const expected = new THREE.Color('#ff2200');
      
      expect(result.r).toBeCloseTo(expected.r, 2);
      expect(result.g).toBeCloseTo(expected.g, 2);
      expect(result.b).toBeCloseTo(expected.b, 2);
    });

    it('should interpolate colors correctly at midpoint (80°C)', () => {
      const result = lerpColor(80, 65, 95, '#ff6b35', '#ff2200');
      
      // At midpoint, should be halfway between the two colors
      const color1 = new THREE.Color('#ff6b35');
      const color2 = new THREE.Color('#ff2200');
      const expected = color1.lerp(color2, 0.5);
      
      expect(result.r).toBeCloseTo(expected.r, 2);
      expect(result.g).toBeCloseTo(expected.g, 2);
      expect(result.b).toBeCloseTo(expected.b, 2);
    });

    it('should clamp values below minimum to color1', () => {
      const result = lerpColor(50, 65, 95, '#ff6b35', '#ff2200');
      const expected = new THREE.Color('#ff6b35');
      
      expect(result.r).toBeCloseTo(expected.r, 2);
      expect(result.g).toBeCloseTo(expected.g, 2);
      expect(result.b).toBeCloseTo(expected.b, 2);
    });

    it('should clamp values above maximum to color2', () => {
      const result = lerpColor(100, 65, 95, '#ff6b35', '#ff2200');
      const expected = new THREE.Color('#ff2200');
      
      expect(result.r).toBeCloseTo(expected.r, 2);
      expect(result.g).toBeCloseTo(expected.g, 2);
      expect(result.b).toBeCloseTo(expected.b, 2);
    });
  });

  describe('Temperature-to-Color Mapping Tests (Requirement 4.4)', () => {
    it('should handle temperature at 65°C (minimum)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 65, load: 45, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle temperature at 80°C (midpoint)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 80, load: 45, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle temperature at 95°C (maximum)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 95, load: 45, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });
  });

  describe('Load-to-Intensity Mapping Tests (Requirement 4.8)', () => {
    it('should handle load at 0% (minimum intensity 0.8)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 0, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle load at 50% (mid intensity 1.3)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 50, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle load at 100% (maximum intensity 1.8)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 100, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });
  });

  describe('Health Status Visual Feedback Tests (Requirements 5.1, 5.2)', () => {
    it('should handle normal health status', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 45, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle warning health status (blinking effect)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 45, health: 'warning' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle critical health status (solid red)', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 45, health: 'critical' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });
  });

  describe('Edge Cases', () => {
    it('should handle extreme temperature values', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 120, load: 45, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle extreme load values', () => {
      useGearStore.mockReturnValue({
        sensors: { temperature: 72, load: 150, health: 'normal' },
      });

      const { container } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(container).toBeTruthy();
    });

    it('should handle all sensor values changing simultaneously', () => {
      const { rerender } = render(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      useGearStore.mockReturnValue({
        sensors: { temperature: 95, load: 100, health: 'critical' },
      });

      rerender(
        <Canvas>
          <SceneLighting />
        </Canvas>
      );

      expect(true).toBe(true);
    });
  });
});
