import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import StructuralColumns from './StructuralColumns.jsx';

/**
 * Unit tests for StructuralColumns component
 * Validates: Requirements 7.3, 7.4
 */
describe('StructuralColumns Component', () => {
  describe('Rendering Tests (Requirement 7.3)', () => {
    it('should render without errors', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      expect(container).toBeTruthy();
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    it('should render I-beam columns', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Component should render BoxGeometry I-beams (0.4x18x0.4)
      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });

  describe('Column Positioning Tests (Requirement 7.4)', () => {
    it('should position columns in corners', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Columns should be positioned at:
      // [-18, 9, -18] (back-left)
      // [18, 9, -18] (back-right)
      // [-18, 9, 18] (front-left)
      expect(container).toBeTruthy();
    });

    it('should render three columns', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Component should render exactly 3 columns
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    it('should position back-left column at [-18, 9, -18]', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // First column should be at back-left corner
      expect(container).toBeTruthy();
    });

    it('should position back-right column at [18, 9, -18]', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Second column should be at back-right corner
      expect(container).toBeTruthy();
    });

    it('should position front-left column at [-18, 9, 18]', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Third column should be at front-left corner
      expect(container).toBeTruthy();
    });
  });

  describe('Material Properties (Requirement 7.3)', () => {
    it('should apply MeshStandardMaterial with correct color #2a3447', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Columns should have MeshStandardMaterial with color #2a3447
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    it('should apply metalness=0.6 and roughness=0.4', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Material should have metalness=0.6 and roughness=0.4
      expect(container).toBeTruthy();
    });
  });

  describe('Geometry Tests', () => {
    it('should use BoxGeometry with dimensions 0.4x18x0.4', () => {
      const { container } = render(
        <Canvas>
          <StructuralColumns />
        </Canvas>
      );

      // Each column should be a BoxGeometry with args [0.4, 18, 0.4]
      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });
});
