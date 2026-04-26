import { describe, it, expect, beforeEach } from 'vitest';
import { getSharedGearMaterial, disposeSharedGearMaterial } from './sharedMaterials';

/**
 * Tests for Shared Materials Utility
 * Validates: Requirement 18.4 - Reuse materials across similar geometry instances
 */

describe('Shared Materials Utility', () => {
  beforeEach(() => {
    // Clean up before each test
    disposeSharedGearMaterial();
  });

  it('should return a MeshStandardMaterial instance', () => {
    const material = getSharedGearMaterial();
    
    expect(material).toBeDefined();
    expect(material.type).toBe('MeshStandardMaterial');
  });

  it('should return the same material instance on multiple calls', () => {
    const material1 = getSharedGearMaterial();
    const material2 = getSharedGearMaterial();
    const material3 = getSharedGearMaterial();
    
    // All references should point to the same object
    expect(material1).toBe(material2);
    expect(material2).toBe(material3);
    expect(material1).toBe(material3);
  });

  it('should have correct material properties', () => {
    const material = getSharedGearMaterial();
    
    expect(material.metalness).toBe(0.85);
    expect(material.roughness).toBe(0.25);
    expect(material.color.getHexString()).toBe('8a9bb0');
  });

  it('should dispose material when disposeSharedGearMaterial is called', () => {
    const material = getSharedGearMaterial();
    const disposeSpy = { called: false };
    
    // Mock the dispose method
    const originalDispose = material.dispose;
    material.dispose = () => {
      disposeSpy.called = true;
      originalDispose.call(material);
    };
    
    disposeSharedGearMaterial();
    
    expect(disposeSpy.called).toBe(true);
  });

  it('should create a new material after disposal', () => {
    const material1 = getSharedGearMaterial();
    disposeSharedGearMaterial();
    const material2 = getSharedGearMaterial();
    
    // After disposal, a new material should be created
    expect(material1).not.toBe(material2);
  });

  it('should handle multiple disposal calls safely', () => {
    getSharedGearMaterial();
    
    // Multiple disposal calls should not throw errors
    expect(() => {
      disposeSharedGearMaterial();
      disposeSharedGearMaterial();
      disposeSharedGearMaterial();
    }).not.toThrow();
  });
});
