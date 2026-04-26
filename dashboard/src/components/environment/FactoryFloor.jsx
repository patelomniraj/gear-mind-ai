import { useMemo } from 'react';
import * as THREE from 'three';

/**
 * FactoryFloor component
 * Renders a 40x40 unit floor plane with industrial concrete texture and grid overlay
 * Requirements: 6.1, 6.2, 6.3, 6.4
 */
export default function FactoryFloor() {
  // Generate industrial concrete texture
  const concreteTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1024;
    const ctx = canvas.getContext('2d');
    
    // Base concrete color
    ctx.fillStyle = '#2a3038';
    ctx.fillRect(0, 0, 1024, 1024);
    
    // Add concrete grain texture
    for (let i = 0; i < 5000; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 1024;
      const brightness = 30 + Math.random() * 40;
      ctx.fillStyle = `rgba(${brightness}, ${brightness}, ${brightness}, ${0.1 + Math.random() * 0.3})`;
      ctx.fillRect(x, y, 1 + Math.random() * 2, 1 + Math.random() * 2);
    }
    
    // Add larger concrete patches
    for (let i = 0; i < 50; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 1024;
      const size = 20 + Math.random() * 60;
      const brightness = 35 + Math.random() * 25;
      
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${brightness}, ${brightness}, ${brightness}, 0.15)`;
      ctx.fill();
    }
    
    // Add wear marks and stains
    for (let i = 0; i < 30; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 1024;
      const width = 50 + Math.random() * 150;
      const height = 20 + Math.random() * 40;
      
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(Math.random() * Math.PI * 2);
      ctx.fillStyle = `rgba(20, 25, 30, ${0.2 + Math.random() * 0.3})`;
      ctx.fillRect(-width / 2, -height / 2, width, height);
      ctx.restore();
    }
    
    // Add oil stains
    for (let i = 0; i < 20; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 1024;
      const size = 30 + Math.random() * 80;
      
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, size);
      gradient.addColorStop(0, 'rgba(15, 18, 22, 0.4)');
      gradient.addColorStop(1, 'rgba(15, 18, 22, 0)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x - size, y - size, size * 2, size * 2);
    }
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(8, 8);
    
    return texture;
  }, []);

  // Generate normal map for concrete bumps
  const normalMap = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Base normal (pointing up)
    ctx.fillStyle = '#8080ff';
    ctx.fillRect(0, 0, 512, 512);
    
    // Add bump variations
    for (let i = 0; i < 1000; i++) {
      const x = Math.random() * 512;
      const y = Math.random() * 512;
      const size = 1 + Math.random() * 3;
      const r = 100 + Math.random() * 55;
      const g = 100 + Math.random() * 55;
      const b = 200 + Math.random() * 55;
      
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.3)`;
      ctx.fillRect(x, y, size, size);
    }
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(8, 8);
    
    return texture;
  }, []);

  return (
    <group>
      {/* Floor plane with industrial concrete texture */}
      <mesh 
        rotation={[-Math.PI / 2, 0, 0]} 
        position={[0, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial 
          map={concreteTexture}
          normalMap={normalMap}
          normalScale={new THREE.Vector2(0.3, 0.3)}
          roughness={0.9}
          metalness={0.1}
        />
      </mesh>
      
      {/* Grid helper overlay - more subtle */}
      <gridHelper 
        args={[40, 40, '#3a4a5c', '#2a3447']} 
        position={[0, 0.01, 0]} 
      />
      
      {/* Safety line markings (yellow lines) */}
      <mesh position={[0, 0.02, -15]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 0.2]} />
        <meshStandardMaterial color="#ffd700" emissive="#ffd700" emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[0, 0.02, 15]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 0.2]} />
        <meshStandardMaterial color="#ffd700" emissive="#ffd700" emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}
