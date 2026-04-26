/**
 * StructuralColumns component
 * Renders I-beam columns at scene corners with industrial details
 * Requirements: 7.3, 7.4
 */
export default function StructuralColumns() {
  const columnPositions = [
    [-18, 9, -18], // Back-left
    [18, 9, -18],  // Back-right
    [-18, 9, 18],  // Front-left
  ];

  return (
    <group>
      {/* I-beam columns */}
      {columnPositions.map((position, index) => (
        <group key={index} position={position}>
          {/* Main column */}
          <mesh>
            <boxGeometry args={[0.4, 18, 0.4]} />
            <meshStandardMaterial 
              color="#2a3447" 
              metalness={0.7} 
              roughness={0.4} 
            />
          </mesh>
          
          {/* Column base plate */}
          <mesh position={[0, -9, 0]}>
            <boxGeometry args={[0.8, 0.2, 0.8]} />
            <meshStandardMaterial 
              color="#1a2030" 
              metalness={0.8} 
              roughness={0.3} 
            />
          </mesh>
          
          {/* Column cap */}
          <mesh position={[0, 9, 0]}>
            <boxGeometry args={[0.6, 0.3, 0.6]} />
            <meshStandardMaterial 
              color="#1a2030" 
              metalness={0.8} 
              roughness={0.3} 
            />
          </mesh>
        </group>
      ))}
      
      {/* Overhead crane rail */}
      <mesh position={[0, 18, -10]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.15, 0.15, 36, 16]} />
        <meshStandardMaterial 
          color="#3a4a5c" 
          metalness={0.8} 
          roughness={0.3} 
        />
      </mesh>
      
      {/* Support beams */}
      <mesh position={[-10, 17, -18]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[0.3, 20, 0.3]} />
        <meshStandardMaterial 
          color="#2a3447" 
          metalness={0.7} 
          roughness={0.4} 
        />
      </mesh>
      <mesh position={[10, 17, -18]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[0.3, 20, 0.3]} />
        <meshStandardMaterial 
          color="#2a3447" 
          metalness={0.7} 
          roughness={0.4} 
        />
      </mesh>
      
      {/* Control panel on left wall */}
      <group position={[-19.5, 3, 0]}>
        <mesh>
          <boxGeometry args={[0.3, 2, 1.5]} />
          <meshStandardMaterial 
            color="#3a4a5c" 
            metalness={0.6} 
            roughness={0.5} 
          />
        </mesh>
        {/* Panel lights */}
        <mesh position={[0.2, 0.5, 0]}>
          <circleGeometry args={[0.1, 16]} />
          <meshStandardMaterial 
            color="#00ff00" 
            emissive="#00ff00" 
            emissiveIntensity={1.5} 
          />
        </mesh>
        <mesh position={[0.2, 0.2, 0]}>
          <circleGeometry args={[0.1, 16]} />
          <meshStandardMaterial 
            color="#ffff00" 
            emissive="#ffff00" 
            emissiveIntensity={1.5} 
          />
        </mesh>
        <mesh position={[0.2, -0.1, 0]}>
          <circleGeometry args={[0.1, 16]} />
          <meshStandardMaterial 
            color="#ff0000" 
            emissive="#ff0000" 
            emissiveIntensity={1.5} 
          />
        </mesh>
      </group>
      
      {/* Tool cabinet */}
      <group position={[15, 1.5, -19]}>
        <mesh>
          <boxGeometry args={[2, 3, 1]} />
          <meshStandardMaterial 
            color="#cc3333" 
            metalness={0.5} 
            roughness={0.6} 
          />
        </mesh>
        {/* Cabinet handles */}
        <mesh position={[0.3, 0.5, 0.6]}>
          <cylinderGeometry args={[0.05, 0.05, 0.4, 8]} />
          <meshStandardMaterial 
            color="#888888" 
            metalness={0.9} 
            roughness={0.2} 
          />
        </mesh>
        <mesh position={[-0.3, 0.5, 0.6]}>
          <cylinderGeometry args={[0.05, 0.05, 0.4, 8]} />
          <meshStandardMaterial 
            color="#888888" 
            metalness={0.9} 
            roughness={0.2} 
          />
        </mesh>
      </group>
      
      {/* Workbench */}
      <group position={[-15, 1, -19]}>
        {/* Table top */}
        <mesh position={[0, 0.5, 0]}>
          <boxGeometry args={[3, 0.1, 1.5]} />
          <meshStandardMaterial 
            color="#4a5a6a" 
            metalness={0.4} 
            roughness={0.7} 
          />
        </mesh>
        {/* Legs */}
        {[[-1.3, -0.5, -0.6], [1.3, -0.5, -0.6], [-1.3, -0.5, 0.6], [1.3, -0.5, 0.6]].map((pos, i) => (
          <mesh key={i} position={pos}>
            <cylinderGeometry args={[0.05, 0.05, 1, 8]} />
            <meshStandardMaterial 
              color="#2a3447" 
              metalness={0.7} 
              roughness={0.4} 
            />
          </mesh>
        ))}
      </group>
    </group>
  );
}
