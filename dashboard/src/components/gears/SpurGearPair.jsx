import { useRef, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { createSpurGearGeometry } from '../../utils/gearGeometry.js';
import { GearShaft, GearMount, MeshSparks, HeatHaze, LubricationSheen } from '../effects/GearEffects.jsx';
import * as THREE from 'three';

/* ─── Fixed geometry constants ──────────────────────────────────────────── */
const MODULE = 0.25;
const NUM_TEETH = 36;
const PITCH_R = (MODULE * NUM_TEETH) / 2;   // 4.5
const CENTER_D = PITCH_R * 2 + 0.06;          // 9.06
const TOOTH_OFFSET = Math.PI / NUM_TEETH;          // π/36 — interlock half-pitch

function visualSpeed(rpm) {
  const r = Math.max(100, Math.min(rpm, 3000));
  return 6.0 + (r / 1950) * 10.0;  // ~16 rad/s at 1950 rpm
}

export default function SpurGearPair({ rpm = 60, vibration = 2.3, health = 'normal', temperature = 72 }) {
  const gear1Ref = useRef();
  const gear2Ref = useRef();

  /* ── Per-instance material (allows health/temp colour changes) ─────────── */
  const gearMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x4e5d6e),
    metalness: 0.92,
    roughness: 0.22,
    clearcoat: 0.50,
    clearcoatRoughness: 0.08,
    envMapIntensity: 2.2,
    emissive: new THREE.Color(0x000000),
    emissiveIntensity: 0,
  }), []);

  const gearGeo = useMemo(() =>
    createSpurGearGeometry(MODULE, NUM_TEETH, 0.60, 0.55)
    , []);

  const edgeGeo = useMemo(() =>
    new THREE.EdgesGeometry(gearGeo, 20)
    , [gearGeo]);

  const edgeMat = useMemo(() => new THREE.LineBasicMaterial({
    color: 0x0a0e14, transparent: true, opacity: 0.45,
  }), []);

  useEffect(() => () => {
    gearGeo.dispose(); edgeGeo.dispose(); edgeMat.dispose(); gearMat.dispose();
  }, [gearGeo, edgeGeo, edgeMat, gearMat]);

  /* ── Animation + parameter-driven appearance ────────────────────────────── */
  useFrame((state, delta) => {
    if (!gear1Ref.current || !gear2Ref.current) return;
    const dt = Math.min(delta, 0.05);
    const step = visualSpeed(rpm) * dt;

    gear1Ref.current.rotation.z += step;
    gear2Ref.current.rotation.z -= step;

    const t = state.clock.elapsedTime;

    // Health-based colour + emissive
    if (health === 'critical') {
      gearMat.color.setHex(0x5c2020);
      gearMat.roughness = 0.58;
      gearMat.emissive.setHex(0xcc2200);
      gearMat.emissiveIntensity = 0.12 + Math.sin(t * 4) * 0.05;
    } else if (health === 'warning') {
      gearMat.color.setHex(0x504020);
      gearMat.roughness = 0.38;
      gearMat.emissive.setHex(0xff8800);
      gearMat.emissiveIntensity = 0.07;
    } else {
      gearMat.color.setHex(0x4e5d6e);
      gearMat.roughness = 0.22;
      gearMat.emissive.setHex(0x000000);
      gearMat.emissiveIntensity = 0;
    }

    // Temperature heat-glow overlay
    if (temperature > 80) {
      const hf = Math.min((temperature - 80) / 40, 1.0);
      gearMat.emissive.setHex(health === 'critical' ? 0xff1100 : 0xff6600);
      gearMat.emissiveIntensity = Math.max(gearMat.emissiveIntensity, hf * 0.28);
    }

    // Subtle rotational wobble when health is degraded
    if (health !== 'normal') {
      const w = Math.sin(t * 6) * vibration * 0.00025;
      gear1Ref.current.rotation.z += w;
      gear2Ref.current.rotation.z -= w;
    }
  });

  /* ── Declarative light driven by health prop ────────────────────────────── */
  const lightColor = health === 'critical' ? '#ff2200' :
    health === 'warning' ? '#ff8800' : '#88aaff';
  const lightIntensity = health === 'critical' ? 4.0 :
    health === 'warning' ? 2.0 : 0.7;

  return (
    <group position={[-CENTER_D / 2, 4, 0]}>

      {/* ───── Driving gear (left) — rotates +Z ───────────────────────── */}
      <group ref={gear1Ref}>
        <mesh geometry={gearGeo} material={gearMat} castShadow receiveShadow />
        <lineSegments geometry={edgeGeo} material={edgeMat} />
        <GearShaft faceWidth={0.60} />
      </group>
      {/* Static pedestal for gear 1 */}
      <GearMount height={4} />

      {/* ───── Driven gear (right) — rotates −Z ───────────────────────── */}
      <group
        ref={gear2Ref}
        position={[CENTER_D, 0, 0]}
        rotation={[0, 0, TOOTH_OFFSET]}
      >
        <mesh geometry={gearGeo} material={gearMat} castShadow receiveShadow />
        <lineSegments geometry={edgeGeo} material={edgeMat} />
        <GearShaft faceWidth={0.60} />
      </group>
      {/* Static pedestal for gear 2 */}
      <group position={[CENTER_D, 0, 0]}>
        <GearMount height={4} />
      </group>

      {/* ───── Mesh contact zone (at +PITCH_R from gear1 center) ──────── */}
      <group position={[PITCH_R, 0, 0]}>
        <MeshSparks rpm={rpm} vibration={vibration} health={health} />
        <LubricationSheen health={health} />
        {/* Dynamic coloured point light — health drives colour + intensity */}
        <pointLight color={lightColor} intensity={lightIntensity} distance={7} decay={2} />
      </group>

      {/* ───── Heat haze above each gear ──────────────────────────────── */}
      <group position={[0, 2.8, 0]}>
        <HeatHaze temperature={temperature} />
      </group>
      <group position={[CENTER_D, 2.8, 0]}>
        <HeatHaze temperature={temperature} />
      </group>

    </group>
  );
}