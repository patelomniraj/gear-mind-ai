import { describe, it, expect, beforeEach } from 'vitest';
import { useGearStore } from './gearStore';

describe('gearStore', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
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

  it('should initialize with default values', () => {
    const state = useGearStore.getState();
    
    expect(state.activeGear).toBe('Spur');
    expect(state.sensors.rpm).toBe(1950);
    expect(state.sensors.temperature).toBe(72);
    expect(state.sensors.vibration).toBe(2.3);
    expect(state.sensors.load).toBe(45);
    expect(state.sensors.health).toBe('normal');
  });

  it('should update activeGear when setActiveGear is called', () => {
    const { setActiveGear } = useGearStore.getState();
    
    setActiveGear('Helical');
    expect(useGearStore.getState().activeGear).toBe('Helical');
    
    setActiveGear('Bevel');
    expect(useGearStore.getState().activeGear).toBe('Bevel');
    
    setActiveGear('Worm');
    expect(useGearStore.getState().activeGear).toBe('Worm');
  });

  it('should merge sensor data when updateSensors is called', () => {
    const { updateSensors } = useGearStore.getState();
    
    updateSensors({ rpm: 2500 });
    
    const state = useGearStore.getState();
    expect(state.sensors.rpm).toBe(2500);
    expect(state.sensors.temperature).toBe(72); // unchanged
    expect(state.sensors.vibration).toBe(2.3); // unchanged
    expect(state.sensors.load).toBe(45); // unchanged
    expect(state.sensors.health).toBe('normal'); // unchanged
  });

  it('should merge multiple sensor values at once', () => {
    const { updateSensors } = useGearStore.getState();
    
    updateSensors({
      rpm: 2800,
      temperature: 85,
      vibration: 4.5,
    });
    
    const state = useGearStore.getState();
    expect(state.sensors.rpm).toBe(2800);
    expect(state.sensors.temperature).toBe(85);
    expect(state.sensors.vibration).toBe(4.5);
    expect(state.sensors.load).toBe(45); // unchanged
    expect(state.sensors.health).toBe('normal'); // unchanged
  });

  it('should update health status', () => {
    const { updateSensors } = useGearStore.getState();
    
    updateSensors({ health: 'warning' });
    expect(useGearStore.getState().sensors.health).toBe('warning');
    
    updateSensors({ health: 'critical' });
    expect(useGearStore.getState().sensors.health).toBe('critical');
    
    updateSensors({ health: 'normal' });
    expect(useGearStore.getState().sensors.health).toBe('normal');
  });

  it('should handle all sensor updates together', () => {
    const { updateSensors } = useGearStore.getState();
    
    updateSensors({
      rpm: 3000,
      temperature: 95,
      vibration: 8.0,
      load: 90,
      health: 'critical',
    });
    
    const state = useGearStore.getState();
    expect(state.sensors.rpm).toBe(3000);
    expect(state.sensors.temperature).toBe(95);
    expect(state.sensors.vibration).toBe(8.0);
    expect(state.sensors.load).toBe(90);
    expect(state.sensors.health).toBe('critical');
  });
});
