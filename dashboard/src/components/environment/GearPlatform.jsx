import * as THREE from 'three';

/**
 * GearPlatform component
 * Renders a mounting platform/housing for the gears
 * Provides industrial context and realistic mounting
 */
export default function GearPlatform() {
  return (
    <group position={[0, 0.5, 0]}>
      {/* Main platform base */}
      <mesh position={[0, 0, 0]} receiveShadow castShadow>
        <boxGeometry args={[8, 0.4, 6]} />
        <meshStandardMaterial 
          color="#3a4a5c" 
          metalness={0.6} 
          roughness={0.5} 
        />
      </mesh>
      
      {/* Platform edges (reinforcement) */}
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[8.2, 0.2, 6.2]} />
        <meshStandardMaterial 
          color="#2a3447" 
          metalness={0.7} 
          roughness={0.4} 
        />
      </mesh>
      
      {/* Corner bolts */}
      {[
        [-3.8, 0.3, -2.8],
        [3.8, 0.3, -2.8],
        [-3.8, 0.3, 2.8],
        [3.8, 0.3, 2.8],
      ].map((pos, i) => (
        <mesh key={i} position={pos} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.15, 0.15, 0.3, 6]} />
          <meshStandardMaterial 
            color="#1a2030" 
            metalness={0.9} 
            roughness={0.2} 
          />
        </mesh>
      ))}
      
      {/* Support legs */}
      {[
        [-3.5, -0.5, -2.5],
        [3.5, -0.5, -2.5],
        [-3.5, -0.5, 2.5],
        [3.5, -0.5, 2.5],
      ].map((pos, i) => (
        <group key={`leg-${i}`} position={pos}>
          <mesh>
            <cylinderGeometry args={[0.2, 0.25, 1, 8]} />
            <meshStandardMaterial 
              color="#2a3447" 
              metalness={0.7} 
              roughness={0.4} 
            />
          </mesh>
          {/* Leg base plate */}
          <mesh position={[0, -0.6, 0]}>
            <cylinderGeometry args={[0.35, 0.35, 0.1, 8]} />
            <meshStandardMaterial 
              color="#1a2030" 
              metalness={0.8} 
              roughness={0.3} 
            />
          </mesh>
        </group>
      ))}
      
      {/* Mounting brackets for gears */}
      <mesh position={[-2, 0.5, 0]} castShadow>
        <boxGeometry args={[0.3, 0.6, 1]} />
        <meshStandardMaterial 
          color="#4a5a6a" 
          metalness={0.7} 
          roughness={0.4} 
        />
      </mesh>
      <mesh position={[2, 0.5, 0]} castShadow>
        <boxGeometry args={[0.3, 0.6, 1]} />
        <meshStandardMaterial 
          color="#4a5a6a" 
          metalness={0.7} 
          roughness={0.4} 
        />
      </mesh>
      
      {/* Oil drip tray underneath */}
      <mesh position={[0, -0.8, 0]}>
        <boxGeometry args={[7, 0.1, 5]} />
        <meshStandardMaterial 
          color="#1a1a1a" 
          metalness={0.3} 
          roughness={0.8} 
        />
      </mesh>
      
      {/* Warning stripes on platform edge */}
      <mesh position={[0, 0.21, 3.1]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[8, 0.3]} />
        <meshStandardMaterial 
          color="#ffcc00" 
          emissive="#ffcc00" 
          emissiveIntensity={0.2} 
        />
      </mesh>
      <mesh position={[0, 0.21, -3.1]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[8, 0.3]} />
        <meshStandardMaterial 
          color="#ffcc00" 
          emissive="#ffcc00" 
          emissiveIntensity={0.2} 
        />
      </mesh>
    </group>
  );
}
