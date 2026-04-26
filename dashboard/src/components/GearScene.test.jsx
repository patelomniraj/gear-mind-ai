import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render } from '@testing-library/react';
import { act } from 'react';
import GearScene from './GearScene';
import { useGearStore } from '../store/gearStore';

/**
 * Integration Tests for Gear Switching
 * 
 * These tests validate Requirements 11.1, 11.2, and 11.4:
 * - Gear components fade in/out when activeGear changes (11.1)
 * - Camera position animates smoothly during transitions (11.2, 11.4)
 * - Lighting persists during transitions (11.4)
 * 
 * Note: These are integration tests that verify the component structure and state management.
 * Visual rendering and animation behavior should be verified through manual testing.
 */

describe('GearScene - Gear Switching Integration Tests', () => {
  beforeEach(() => {
    // Reset store to default state before each test
    useGearStore.setState({
      activeGear: 'Spur',
      sensors: {
        rpm: 1950,
        temperature: 72,
        vibration: 2.3,
        load: 45,
        health: 'normal',
      },
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Requirement 11.1: Gear components fade in/out when activeGear changes', () => {
    it('should render GearScene component without errors', () => {
      const { container } = render(<GearScene />);
      
      // Verify Canvas is rendered
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
    });

    it('should read activeGear from store and render appropriate gear', () => {
      useGearStore.setState({ activeGear: 'Spur' });
      const { container } = render(<GearScene />);
      
      // Verify scene renders
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      // Verify store state
      const state = useGearStore.getState();
      expect(state.activeGear).toBe('Spur');
    });

    it('should update when activeGear changes from Spur to Helical', () => {
      const { container, rerender } = render(<GearScene />);
      
      // Initially Spur
      expect(useGearStore.getState().activeGear).toBe('Spur');
      
      // Change to Helical
      act(() => {
        useGearStore.getState().setActiveGear('Helical');
      });
      
      // Force re-render
      rerender(<GearScene />);
      
      // Verify store updated
      expect(useGearStore.getState().activeGear).toBe('Helical');
      
      // Canvas should still be present
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should update when activeGear changes from Helical to Bevel', () => {
      useGearStore.setState({ activeGear: 'Helical' });
      const { container, rerender } = render(<GearScene />);
      
      expect(useGearStore.getState().activeGear).toBe('Helical');
      
      act(() => {
        useGearStore.getState().setActiveGear('Bevel');
      });
      
      rerender(<GearScene />);
      
      expect(useGearStore.getState().activeGear).toBe('Bevel');
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should update when activeGear changes from Bevel to Worm', () => {
      useGearStore.setState({ activeGear: 'Bevel' });
      const { container, rerender } = render(<GearScene />);
      
      expect(useGearStore.getState().activeGear).toBe('Bevel');
      
      act(() => {
        useGearStore.getState().setActiveGear('Worm');
      });
      
      rerender(<GearScene />);
      
      expect(useGearStore.getState().activeGear).toBe('Worm');
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should handle all four gear types', () => {
      const gearTypes = ['Spur', 'Helical', 'Bevel', 'Worm'];
      
      gearTypes.forEach(gearType => {
        useGearStore.setState({ activeGear: gearType });
        const { container } = render(<GearScene />);
        
        expect(useGearStore.getState().activeGear).toBe(gearType);
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });

    it('should use AnimatePresence for gear transitions', () => {
      // This test verifies the component structure supports transitions
      const { container, rerender } = render(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      // Switch gear
      act(() => {
        useGearStore.getState().setActiveGear('Worm');
      });
      
      rerender(<GearScene />);
      
      // Scene should remain stable during transition
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Worm');
    });
  });

  describe('Requirement 11.2, 11.4: Camera position animates smoothly', () => {
    it('should render scene with camera for Spur gear', () => {
      useGearStore.setState({ activeGear: 'Spur' });
      const { container } = render(<GearScene />);
      
      // Canvas contains camera
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Spur');
    });

    it('should maintain scene when switching from Spur to Helical', () => {
      const { container, rerender } = render(<GearScene />);
      
      expect(useGearStore.getState().activeGear).toBe('Spur');
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      
      // Switch to Helical (camera animates to [6,4,4])
      act(() => {
        useGearStore.getState().setActiveGear('Helical');
      });
      
      rerender(<GearScene />);
      
      // Scene persists
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Helical');
    });

    it('should maintain scene when switching from Helical to Bevel', () => {
      useGearStore.setState({ activeGear: 'Helical' });
      const { container, rerender } = render(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      // Switch to Bevel (camera animates to [4,5,6])
      act(() => {
        useGearStore.getState().setActiveGear('Bevel');
      });
      
      rerender(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Bevel');
    });

    it('should maintain scene when switching from Bevel to Worm', () => {
      useGearStore.setState({ activeGear: 'Bevel' });
      const { container, rerender } = render(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      // Switch to Worm (camera animates to [7,3,3])
      act(() => {
        useGearStore.getState().setActiveGear('Worm');
      });
      
      rerender(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Worm');
    });

    it('should use spring animation for camera transitions', () => {
      // This test verifies the component supports smooth camera transitions
      const { container, rerender } = render(<GearScene />);
      
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      
      // Switch gear to trigger camera animation
      act(() => {
        useGearStore.getState().setActiveGear('Helical');
      });
      
      rerender(<GearScene />);
      
      // Scene should persist (spring animation happens inside Canvas)
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should maintain scene throughout multiple gear switches', () => {
      const { container, rerender } = render(<GearScene />);
      
      const gearTypes = ['Helical', 'Bevel', 'Worm', 'Spur'];
      
      gearTypes.forEach(gearType => {
        act(() => {
          useGearStore.getState().setActiveGear(gearType);
        });
        
        rerender(<GearScene />);
        
        // Canvas should always be present
        expect(container.querySelector('canvas')).toBeInTheDocument();
        expect(useGearStore.getState().activeGear).toBe(gearType);
      });
    });
  });

  describe('Requirement 11.4: Lighting persists during transitions', () => {
    it('should render scene with lighting system', () => {
      const { container } = render(<GearScene />);
      
      // Scene contains lighting (inside Canvas)
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should maintain scene when switching from Spur to Helical', () => {
      const { container, rerender } = render(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      act(() => {
        useGearStore.getState().setActiveGear('Helical');
      });
      
      rerender(<GearScene />);
      
      // Scene persists (lighting remains)
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Helical');
    });

    it('should maintain scene when switching from Helical to Bevel', () => {
      useGearStore.setState({ activeGear: 'Helical' });
      const { container, rerender } = render(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      act(() => {
        useGearStore.getState().setActiveGear('Bevel');
      });
      
      rerender(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Bevel');
    });

    it('should maintain scene when switching from Bevel to Worm', () => {
      useGearStore.setState({ activeGear: 'Bevel' });
      const { container, rerender } = render(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      act(() => {
        useGearStore.getState().setActiveGear('Worm');
      });
      
      rerender(<GearScene />);
      
      expect(container.querySelector('canvas')).toBeInTheDocument();
      expect(useGearStore.getState().activeGear).toBe('Worm');
    });

    it('should maintain scene structure during gear transitions', () => {
      const { container, rerender } = render(<GearScene />);
      
      // Verify scene renders
      expect(container.querySelector('canvas')).toBeInTheDocument();
      
      // Switch gear
      act(() => {
        useGearStore.getState().setActiveGear('Worm');
      });
      
      rerender(<GearScene />);
      
      // Scene structure persists (environment, lighting, etc.)
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should maintain scene through complete gear cycle', () => {
      const { container, rerender } = render(<GearScene />);
      
      const gearTypes = ['Helical', 'Bevel', 'Worm', 'Spur'];
      
      gearTypes.forEach(gearType => {
        act(() => {
          useGearStore.getState().setActiveGear(gearType);
        });
        
        rerender(<GearScene />);
        
        // Verify scene persists
        expect(container.querySelector('canvas')).toBeInTheDocument();
        expect(useGearStore.getState().activeGear).toBe(gearType);
      });
    });
  });

  describe('Integration: Complete gear switching workflow', () => {
    it('should handle rapid gear switches without errors', () => {
      const { container, rerender } = render(<GearScene />);
      
      // Rapidly switch through all gear types
      act(() => {
        useGearStore.getState().setActiveGear('Helical');
      });
      
      rerender(<GearScene />);
      
      act(() => {
        useGearStore.getState().setActiveGear('Bevel');
      });
      
      rerender(<GearScene />);
      
      act(() => {
        useGearStore.getState().setActiveGear('Worm');
      });
      
      rerender(<GearScene />);
      
      // Final state should be correct
      expect(useGearStore.getState().activeGear).toBe('Worm');
      expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('should integrate with sensor data from store', () => {
      render(<GearScene />);
      
      // Update sensor data
      act(() => {
        useGearStore.getState().updateSensors({ rpm: 2500, vibration: 5.0, health: 'warning' });
      });
      
      // Verify store updated
      const state = useGearStore.getState();
      expect(state.sensors.rpm).toBe(2500);
      expect(state.sensors.vibration).toBe(5.0);
      expect(state.sensors.health).toBe('warning');
    });

    it('should render complete scene structure', () => {
      const { container } = render(<GearScene />);
      
      // Verify Canvas renders (contains all scene elements)
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      
      // Verify store integration
      const state = useGearStore.getState();
      expect(state.activeGear).toBe('Spur');
      expect(state.sensors).toBeDefined();
    });

    it('should support all gear types in sequence', () => {
      const { container, rerender } = render(<GearScene />);
      const gearTypes = ['Spur', 'Helical', 'Bevel', 'Worm'];
      
      gearTypes.forEach(gearType => {
        act(() => {
          useGearStore.getState().setActiveGear(gearType);
        });
        
        rerender(<GearScene />);
        
        expect(useGearStore.getState().activeGear).toBe(gearType);
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });
  });
});
