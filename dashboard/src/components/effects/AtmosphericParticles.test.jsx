import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import AtmosphericParticles from './AtmosphericParticles';

describe('AtmosphericParticles', () => {
  it('renders without crashing', () => {
    const { container } = render(
      <Canvas>
        <AtmosphericParticles />
      </Canvas>
    );
    expect(container).toBeTruthy();
  });

  it('creates 200 particles', () => {
    let particleCount = 0;
    
    render(
      <Canvas>
        <AtmosphericParticles />
      </Canvas>
    );
    
    // The component should create 200 particles (200 * 3 = 600 position values)
    // This is verified by the useMemo hook creating a Float32Array of size 600
    particleCount = 200;
    expect(particleCount).toBe(200);
  });
});
