import { describe, it, expect, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import HUD3D from './HUD3D';
import { useGearStore } from '../../store/gearStore';

describe('HUD3D', () => {
  beforeEach(() => {
    // Reset store to default state
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

  it('renders without crashing', () => {
    const { container } = render(
      <Canvas>
        <HUD3D />
      </Canvas>
    );
    expect(container).toBeTruthy();
  });

  it('displays the active gear name', () => {
    useGearStore.setState({ activeGear: 'Helical' });
    const { container } = render(
      <Canvas>
        <HUD3D />
      </Canvas>
    );
    expect(container).toBeTruthy();
  });

  it('displays the RPM value', () => {
    useGearStore.setState({
      sensors: {
        rpm: 2500,
        temperature: 72,
        vibration: 2.3,
        load: 45,
        health: 'normal',
      },
    });
    const { container } = render(
      <Canvas>
        <HUD3D />
      </Canvas>
    );
    expect(container).toBeTruthy();
  });
});
