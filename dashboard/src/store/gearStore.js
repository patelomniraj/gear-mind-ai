import { create } from 'zustand';

export const useGearStore = create((set) => ({
  // Active gear type
  activeGear: 'Spur', // 'Spur' | 'Helical' | 'Bevel' | 'Worm'
  
  // Sensor data
  sensors: {
    rpm: 1950,           // Revolutions per minute (0-3000)
    temperature: 72,     // Celsius (20-120)
    vibration: 2.3,      // mm/s RMS (0-10)
    load: 45,            // Percentage (0-100)
    health: 'normal',    // 'normal' | 'warning' | 'critical'
  },
  
  // Actions
  setActiveGear: (gear) => set({ activeGear: gear }),
  updateSensors: (sensorData) => set((state) => ({
    sensors: { ...state.sensors, ...sensorData }
  })),
}));
