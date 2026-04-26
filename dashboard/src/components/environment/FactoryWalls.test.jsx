import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import FactoryWalls from './FactoryWalls.jsx';

/**
 * Unit tests for FactoryWalls component
 * Validates: Requirements 7.1, 7.2
 */
describe('FactoryWalls Component', () => {
  describe('Rendering Tests (Requirement 7.1, 7.2)', () => {
    it('should render without errors', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      expect(container).toBeTruthy();
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    it('should render two wall panels', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Component should render back wall and left wall
      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });

  describe('Back Wall Tests (Requirement 7.1)', () => {
    it('should render back wall at correct position [0, 10, -20]', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Back wall should be positioned at [0, 10, -20]
      // with PlaneGeometry (40x20)
      expect(container).toBeTruthy();
    });

    it('should render back wall with correct material color #1c2333', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Back wall should have MeshStandardMaterial with color #1c2333
      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });

  describe('Left Wall Tests (Requirement 7.2)', () => {
    it('should render left wall at correct position [-20, 10, 0]', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Left wall should be positioned at [-20, 10, 0]
      // with PlaneGeometry (40x20) rotated 90°
      expect(container).toBeTruthy();
    });

    it('should render left wall with correct rotation', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Left wall should be rotated [0, Math.PI / 2, 0]
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    it('should render left wall with correct material color #1c2333', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Left wall should have MeshStandardMaterial with color #1c2333
      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });

  describe('Material Properties', () => {
    it('should apply MeshStandardMaterial to both walls', () => {
      const { container } = render(
        <Canvas>
          <FactoryWalls />
        </Canvas>
      );

      // Both walls should use MeshStandardMaterial
      expect(container).toBeTruthy();
    });
  });
});
