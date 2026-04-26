import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * AtmosphericParticles Component
 * Renders floating particles that drift upward to create atmospheric depth
 * 
 * Validates: Requirements 9.1, 9.2, 9.3
 */
export default function AtmosphericParticles() {
  const pointsRef = useRef();

  // Generate 200 random particle positions in volume [-15,15] × [0,15] × [-15,15]
  const positions = useMemo(() => {
    const posArray = new Float32Array(200 * 3);
    
    for (let i = 0; i < 200; i++) {
      const i3 = i * 3;
      posArray[i3] = (Math.random() - 0.5) * 30;     // x: -15 to 15
      posArray[i3 + 1] = Math.random() * 15;          // y: 0 to 15
      posArray[i3 + 2] = (Math.random() - 0.5) * 30;  // z: -15 to 15
    }
    
    return posArray;
  }, []);

  // Animation loop: drift particles upward and wrap at y=15
  useFrame(() => {
    if (!pointsRef.current) return;

    const positions = pointsRef.current.geometry.attributes.position.array;
    
    for (let i = 0; i < 200; i++) {
      const i3 = i * 3;
      
      // Drift upward
      positions[i3 + 1] += 0.01;
      
      // Wrap at y=15 back to y=0
      if (positions[i3 + 1] > 15) {
        positions[i3 + 1] = 0;
      }
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={200}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#ffffff"
        opacity={0.3}
        transparent={true}
        sizeAttenuation={true}
      />
    </points>
  );
}
