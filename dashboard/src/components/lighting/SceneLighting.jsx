import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

/**
 * SceneLighting
 *
 * Lighting strategy for convincing machined-metal appearance:
 *
 *  1. Low ambient — keeps shadowed faces dark (dramatic, not flat)
 *  2. Key directional light (from upper-right) — primary shadow caster
 *  3. Fill spot (from left)  — softens harsh shadows
 *  4. Rim light (from behind, low) — edge separation from background
 *  5. Three small-radius point lights directly over the gear platform —
 *     produce the tight specular highlights that make metal look metallic.
 *  6. Two coloured accent lights (warm/cool) — add depth and colour variation
 *     typical of industrial lighting environments.
 *
 * No environment map here — that is handled by <Environment> in GearScene.
 */
export default function SceneLighting() {
  const rimRef = useRef();

  // Slow pulse on rim light for atmosphere (very subtle)
  useFrame(({ clock }) => {
    if (!rimRef.current) return;
    rimRef.current.intensity = 0.4 + Math.sin(clock.elapsedTime * 0.6) * 0.08;
  });

  return (
    <>
      {/* ── Ambient: very low so metals stay dark in shadow ────────────── */}
      <ambientLight intensity={0.18} color="#c8d4e0" />

      {/* ── Key light: main shadow-caster from upper right ──────────────── */}
      <directionalLight
        position={[8, 14, 6]}
        intensity={2.8}
        color="#f0f4ff"
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-near={1}
        shadow-camera-far={60}
        shadow-camera-left={-20}
        shadow-camera-right={20}
        shadow-camera-top={20}
        shadow-camera-bottom={-20}
        shadow-bias={-0.0004}
      />

      {/* ── Fill light: from left, cooler tone ──────────────────────────── */}
      <directionalLight
        position={[-10, 6, 4]}
        intensity={0.9}
        color="#8fadd0"
        castShadow={false}
      />

      {/* ── Rim light: from behind/below, warm metal sheen ──────────────── */}
      <directionalLight
        ref={rimRef}
        position={[-3, -2, -12]}
        intensity={0.45}
        color="#e8c87a"
        castShadow={false}
      />

      {/* ── Overhead industrial strip lights (point lights over gear area) ─ */}
      <pointLight position={[ 0,  9,  2]} intensity={1.4} distance={16} decay={2} color="#ddeeff" />
      <pointLight position={[-4,  8, -2]} intensity={0.9} distance={14} decay={2} color="#c8d8ff" />
      <pointLight position={[ 4,  8, -2]} intensity={0.9} distance={14} decay={2} color="#c8d8ff" />

      {/* ── Close-range specular highlights directly on gear surface ──────── */}
      {/* These tight point lights create the sharp hotspot that screams "metal" */}
      <pointLight position={[ 2,  5,  4]} intensity={1.8} distance={7} decay={2.5} color="#ffffff" />
      <pointLight position={[-2,  4,  3]} intensity={1.2} distance={6} decay={2.5} color="#e8f0ff" />

      {/* ── Warm accent: simulates reflected light from factory floor lamps ─ */}
      <pointLight position={[ 6, 1, 6]}  intensity={0.5} distance={12} decay={2} color="#f5c47a" />
      <pointLight position={[-6, 1, 6]}  intensity={0.5} distance={12} decay={2} color="#f5c47a" />

      {/* ── Cool ceiling accent: reinforces industrial atmosphere ──────────── */}
      <pointLight position={[0, 18, -8]} intensity={0.6} distance={20} decay={2} color="#aaccee" />
    </>
  );
}