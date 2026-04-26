import { Text } from '@react-three/drei';
import { useGearStore } from '../../store/gearStore';

/**
 * HUD3D Component
 * Displays a 3D HUD overlay showing current gear type and RPM value
 * Uses Text component from drei for 3D text rendering with glowing teal effect
 */
export default function HUD3D() {
  const activeGear = useGearStore((state) => state.activeGear);
  const rpm = useGearStore((state) => state.sensors.rpm);

  return (
    <group>
      {/* Gear name display */}
      <Text
        position={[-3, 4, 0]}
        fontSize={0.4}
        color="#05cd99"
        anchorX="left"
        anchorY="middle"
      >
        {activeGear}
        <meshStandardMaterial
          color="#05cd99"
          emissive="#05cd99"
          emissiveIntensity={0.5}
        />
      </Text>

      {/* RPM value display */}
      <Text
        position={[-3, 3.5, 0]}
        fontSize={0.3}
        color="#05cd99"
        anchorX="left"
        anchorY="middle"
      >
        {`RPM: ${rpm}`}
        <meshStandardMaterial
          color="#05cd99"
          emissive="#05cd99"
          emissiveIntensity={0.5}
        />
      </Text>
    </group>
  );
}
