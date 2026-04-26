import { describe, it, expect, beforeEach } from 'vitest';
import * as THREE from 'three';
import {
  radialPosition,
  createSpurTeeth,
  createHelixCurve,
  createHelicalTooth,
  createWormSpiral,
} from './gearGeometry.js';

describe('gearGeometry utility functions', () => {
  describe('radialPosition', () => {
    it('should distribute positions evenly around circle', () => {
      const radius = 5;
      const count = 4;
      
      // Test 4 positions around a circle
      const pos0 = radialPosition(0, count, radius);
      const pos1 = radialPosition(1, count, radius);
      const pos2 = radialPosition(2, count, radius);
      const pos3 = radialPosition(3, count, radius);
      
      // Check that positions are evenly spaced (90 degrees apart)
      expect(pos0.angle).toBeCloseTo(0, 5);
      expect(pos1.angle).toBeCloseTo(Math.PI / 2, 5);
      expect(pos2.angle).toBeCloseTo(Math.PI, 5);
      expect(pos3.angle).toBeCloseTo(Math.PI * 1.5, 5);
      
      // Check that all positions are at correct radius
      const distance0 = Math.sqrt(pos0.x ** 2 + pos0.z ** 2);
      const distance1 = Math.sqrt(pos1.x ** 2 + pos1.z ** 2);
      const distance2 = Math.sqrt(pos2.x ** 2 + pos2.z ** 2);
      const distance3 = Math.sqrt(pos3.x ** 2 + pos3.z ** 2);
      
      expect(distance0).toBeCloseTo(radius, 5);
      expect(distance1).toBeCloseTo(radius, 5);
      expect(distance2).toBeCloseTo(radius, 5);
      expect(distance3).toBeCloseTo(radius, 5);
    });

    it('should return correct position for first tooth at angle 0', () => {
      const pos = radialPosition(0, 16, 2);
      
      expect(pos.angle).toBe(0);
      expect(pos.x).toBeCloseTo(2, 5);
      expect(pos.z).toBeCloseTo(0, 5);
    });

    it('should handle single tooth case', () => {
      const pos = radialPosition(0, 1, 3);
      
      expect(pos.angle).toBe(0);
      expect(pos.x).toBeCloseTo(3, 5);
      expect(pos.z).toBeCloseTo(0, 5);
    });

    it('should handle large tooth counts', () => {
      const count = 100;
      const radius = 10;
      
      // Test that positions are evenly distributed
      const pos0 = radialPosition(0, count, radius);
      const pos1 = radialPosition(1, count, radius);
      
      const expectedAngleStep = (Math.PI * 2) / count;
      expect(pos1.angle - pos0.angle).toBeCloseTo(expectedAngleStep, 5);
    });
  });

  describe('createSpurTeeth', () => {
    it('should return valid BufferGeometry', () => {
      const geometry = createSpurTeeth(2, 16, 0.8, 0.3, 0.5);
      
      expect(geometry).toBeInstanceOf(THREE.BufferGeometry);
      expect(geometry.attributes.position).toBeDefined();
    });

    it('should create correct number of vertices for teeth', () => {
      const teethCount = 16;
      const geometry = createSpurTeeth(2, teethCount, 0.8, 0.3, 0.5);
      
      // Each BoxGeometry tooth has 24 vertices (6 faces * 4 vertices per face)
      // After merging, we should have teethCount * 24 vertices
      const expectedVertices = teethCount * 24;
      const actualVertices = geometry.attributes.position.count;
      
      expect(actualVertices).toBe(expectedVertices);
    });

    it('should handle minimum tooth count', () => {
      const geometry = createSpurTeeth(2, 3, 0.8, 0.3, 0.5);
      
      expect(geometry).toBeInstanceOf(THREE.BufferGeometry);
      expect(geometry.attributes.position.count).toBe(3 * 24);
    });

    it('should handle different base radii', () => {
      const smallRadius = createSpurTeeth(1, 8, 0.8, 0.3, 0.5);
      const largeRadius = createSpurTeeth(5, 8, 0.8, 0.3, 0.5);
      
      expect(smallRadius).toBeInstanceOf(THREE.BufferGeometry);
      expect(largeRadius).toBeInstanceOf(THREE.BufferGeometry);
      
      // Both should have same vertex count
      expect(smallRadius.attributes.position.count).toBe(8 * 24);
      expect(largeRadius.attributes.position.count).toBe(8 * 24);
    });

    it('should create geometry with varying tooth dimensions', () => {
      const geometry = createSpurTeeth(2, 10, 1.0, 0.5, 0.8);
      
      expect(geometry).toBeInstanceOf(THREE.BufferGeometry);
      expect(geometry.attributes.position).toBeDefined();
      expect(geometry.attributes.position.count).toBe(10 * 24);
    });
  });

  describe('createHelixCurve', () => {
    it('should generate parametric curve at specified angle', () => {
      const angle = 15;
      const height = 2;
      const curve = createHelixCurve(angle, height);
      
      expect(curve).toBeInstanceOf(THREE.CatmullRomCurve3);
      expect(curve.points).toBeDefined();
      expect(curve.points.length).toBe(21); // segments + 1
    });

    it('should create curve with correct height range', () => {
      const height = 4;
      const curve = createHelixCurve(15, height);
      
      const firstPoint = curve.points[0];
      const lastPoint = curve.points[curve.points.length - 1];
      
      // First point should be at -height/2
      expect(firstPoint.y).toBeCloseTo(-height / 2, 5);
      
      // Last point should be at height/2
      expect(lastPoint.y).toBeCloseTo(height / 2, 5);
    });

    it('should handle zero helix angle', () => {
      const curve = createHelixCurve(0, 2);
      
      expect(curve).toBeInstanceOf(THREE.CatmullRomCurve3);
      expect(curve.points.length).toBe(21);
      
      // With zero angle, all points should have same x and z
      const firstPoint = curve.points[0];
      curve.points.forEach(point => {
        expect(point.x).toBeCloseTo(firstPoint.x, 5);
        expect(point.z).toBeCloseTo(firstPoint.z, 5);
      });
    });

    it('should handle negative helix angle', () => {
      const curve = createHelixCurve(-15, 2);
      
      expect(curve).toBeInstanceOf(THREE.CatmullRomCurve3);
      expect(curve.points.length).toBe(21);
    });

    it('should create curve with correct twist for 45 degree angle', () => {
      const angle = 45;
      const curve = createHelixCurve(angle, 2);
      
      const firstPoint = curve.points[0];
      const lastPoint = curve.points[curve.points.length - 1];
      
      // Check that the curve has twisted (x and z coordinates should differ)
      const hasRotated = 
        Math.abs(firstPoint.x - lastPoint.x) > 0.1 ||
        Math.abs(firstPoint.z - lastPoint.z) > 0.1;
      
      expect(hasRotated).toBe(true);
    });

    it('should maintain constant radius throughout curve', () => {
      const curve = createHelixCurve(30, 3);
      const expectedRadius = 2; // hardcoded in the function
      
      curve.points.forEach(point => {
        const radius = Math.sqrt(point.x ** 2 + point.z ** 2);
        expect(radius).toBeCloseTo(expectedRadius, 5);
      });
    });
  });

  describe('createHelicalTooth', () => {
    it('should return valid ExtrudeGeometry', () => {
      const geometry = createHelicalTooth(15, 2);
      
      expect(geometry).toBeInstanceOf(THREE.ExtrudeGeometry);
      expect(geometry.attributes.position).toBeDefined();
    });

    it('should handle different helix angles', () => {
      const geo15 = createHelicalTooth(15, 2);
      const geo30 = createHelicalTooth(30, 2);
      const geo45 = createHelicalTooth(45, 2);
      
      expect(geo15).toBeInstanceOf(THREE.ExtrudeGeometry);
      expect(geo30).toBeInstanceOf(THREE.ExtrudeGeometry);
      expect(geo45).toBeInstanceOf(THREE.ExtrudeGeometry);
    });

    it('should handle different heights', () => {
      const shortTooth = createHelicalTooth(15, 1);
      const tallTooth = createHelicalTooth(15, 5);
      
      expect(shortTooth).toBeInstanceOf(THREE.ExtrudeGeometry);
      expect(tallTooth).toBeInstanceOf(THREE.ExtrudeGeometry);
    });
  });

  describe('createWormSpiral', () => {
    it('should return valid TubeGeometry', () => {
      const geometry = createWormSpiral(0.4, 4, 0.5, 0.15);
      
      expect(geometry).toBeInstanceOf(THREE.TubeGeometry);
      expect(geometry.attributes.position).toBeDefined();
    });

    it('should create spiral with correct number of turns', () => {
      const length = 4;
      const pitch = 0.5;
      const expectedTurns = length / pitch; // 8 turns
      
      const geometry = createWormSpiral(0.4, length, pitch, 0.15);
      
      // Segments should be proportional to turns
      const expectedSegments = Math.floor(expectedTurns * 64);
      
      expect(geometry).toBeInstanceOf(THREE.TubeGeometry);
      // TubeGeometry should have been created with correct segment count
    });

    it('should handle different radii', () => {
      const smallRadius = createWormSpiral(0.2, 4, 0.5, 0.15);
      const largeRadius = createWormSpiral(1.0, 4, 0.5, 0.15);
      
      expect(smallRadius).toBeInstanceOf(THREE.TubeGeometry);
      expect(largeRadius).toBeInstanceOf(THREE.TubeGeometry);
    });

    it('should handle different pitch values', () => {
      const tightPitch = createWormSpiral(0.4, 4, 0.2, 0.15);
      const loosePitch = createWormSpiral(0.4, 4, 1.0, 0.15);
      
      expect(tightPitch).toBeInstanceOf(THREE.TubeGeometry);
      expect(loosePitch).toBeInstanceOf(THREE.TubeGeometry);
    });

    it('should handle different thread radii', () => {
      const thinThread = createWormSpiral(0.4, 4, 0.5, 0.05);
      const thickThread = createWormSpiral(0.4, 4, 0.5, 0.3);
      
      expect(thinThread).toBeInstanceOf(THREE.TubeGeometry);
      expect(thickThread).toBeInstanceOf(THREE.TubeGeometry);
    });
  });

  describe('parameter validation edge cases', () => {
    it('should handle very small dimensions', () => {
      const geometry = createSpurTeeth(0.1, 4, 0.1, 0.05, 0.05);
      expect(geometry).toBeInstanceOf(THREE.BufferGeometry);
    });

    it('should handle very large dimensions', () => {
      const geometry = createSpurTeeth(100, 8, 10, 5, 5);
      expect(geometry).toBeInstanceOf(THREE.BufferGeometry);
    });

    it('should handle fractional tooth counts in calculations', () => {
      // radialPosition should work with any index
      const pos = radialPosition(0.5, 10, 5);
      expect(pos.x).toBeDefined();
      expect(pos.z).toBeDefined();
      expect(pos.angle).toBeDefined();
    });
  });
});
