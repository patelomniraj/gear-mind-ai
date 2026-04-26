import { useMemo } from 'react';
import * as THREE from 'three';

/**
 * FactoryWalls component
 * Renders back and left wall panels with industrial metal texture
 * Requirements: 7.1, 7.2
 */
export default function FactoryWalls() {
  // Generate industrial metal wall texture
  const wallTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Base metal color
    ctx.fillStyle = '#1c2333';
    ctx.fillRect(0, 0, 1024, 512);
    
    // Add metal panels (vertical lines)
    for (let x = 0; x < 1024; x += 128) {
      ctx.strokeStyle = '#141a28';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 512);
      ctx.stroke();
      
      // Highlight edge
      ctx.strokeStyle = '#252d3f';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + 2, 0);
      ctx.lineTo(x + 2, 512);
      ctx.stroke();
    }
    
    // Add horizontal rivets
    for (let y = 50; y < 512; y += 100) {
      for (let x = 64; x < 1024; x += 128) {
        // Rivet shadow
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = '#0f1419';
        ctx.fill();
        
        // Rivet highlight
        ctx.beginPath();
        ctx.arc(x - 1, y - 1, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#2a3447';
        ctx.fill();
        
        // Rivet center
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#1a2030';
        ctx.fill();
      }
    }
    
    // Add rust and wear
    for (let i = 0; i < 100; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 512;
      const size = 10 + Math.random() * 30;
      
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${60 + Math.random() * 30}, ${40 + Math.random() * 20}, ${30 + Math.random() * 15}, 0.2)`;
      ctx.fill();
    }
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    
    return texture;
  }, []);

  return (
    <group>
      {/* Back wall with industrial texture */}
      <mesh position={[0, 10, -20]}>
        <planeGeometry args={[40, 20]} />
        <meshStandardMaterial 
          map={wallTexture}
          roughness={0.8}
          metalness={0.3}
        />
      </mesh>
      
      {/* Left wall with industrial texture */}
      <mesh position={[-20, 10, 0]} rotation={[0, Math.PI / 2, 0]}>
        <planeGeometry args={[40, 20]} />
        <meshStandardMaterial 
          map={wallTexture}
          roughness={0.8}
          metalness={0.3}
        />
      </mesh>
      
      {/* Warning signs on back wall */}
      <mesh position={[-8, 12, -19.9]}>
        <planeGeometry args={[1.5, 1.5]} />
        <meshStandardMaterial 
          color="#ffd700" 
          emissive="#ffd700" 
          emissiveIntensity={0.5}
        />
      </mesh>
      <mesh position={[8, 12, -19.9]}>
        <planeGeometry args={[1.5, 1.5]} />
        <meshStandardMaterial 
          color="#ff4444" 
          emissive="#ff4444" 
          emissiveIntensity={0.5}
        />
      </mesh>
    </group>
  );
}
