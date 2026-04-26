import { useRef, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { createHelicalGearGeometry } from '../../utils/gearGeometry.js';
import { GearShaft, GearMount, MeshSparks, HeatHaze, LubricationSheen } from '../effects/GearEffects.jsx';
import * as THREE from 'three';

/* ─── Fixed geometry constants ──────────────────────────────────────────── */
const MODULE       = 0.28;
const NUM_TEETH    = 28;
const PITCH_R      = (MODULE * NUM_TEETH) / 2;   // 3.92
const CENTER_D     = PITCH_R * 2 + 0.06;          // 7.90
const TOOTH_OFFSET = Math.PI / NUM_TEETH;          // π/28

/** Maps real sensor RPM → smooth visual rotation speed (rad/s). ~10 rad/s at 1950 rpm. */
function visualSpeed(rpm) {
  const r = Math.max(100, Math.min(rpm, 3000));
  return 3.5 + (r / 1950) * 7.0;
}

export default function HelicalGearPair({ rpm = 60, vibration = 2.3, health = 'normal', temperature = 72 }) {
  const gear1Ref = useRef();
  const gear2Ref = useRef();

  /* ── Per-instance material ──────────────────────────────────────────────── */
  const gearMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color:              new THREE.Color(0x4e5d6e),
    metalness:          0.92,
    roughness:          0.22,
    clearcoat:          0.50,
    clearcoatRoughness: 0.08,
    envMapIntensity:    2.2,
    emissive:           new THREE.Color(0x000000),
    emissiveIntensity:  0,
  }), []);

  // Gear 1: right-hand helix (+18°),  Gear 2: left-hand helix (−18°)
  const gear1Geo = useMemo(() =>
    createHelicalGearGeometry(MODULE, NUM_TEETH, 0.80, +18, 0.42)
  , []);

  const gear2Geo = useMemo(() =>
    createHelicalGearGeometry(MODULE, NUM_TEETH, 0.80, -18, 0.42)
  , []);

  const edge1Geo = useMemo(() => new THREE.EdgesGeometry(gear1Geo, 20), [gear1Geo]);
  const edge2Geo = useMemo(() => new THREE.EdgesGeometry(gear2Geo, 20), [gear2Geo]);

  const edgeMat = useMemo(() => new THREE.LineBasicMaterial({
    color: 0x0a0e14, transparent: true, opacity: 0.45,
  }), []);

  useEffect(() => () => {
    gear1Geo.dispose(); gear2Geo.dispose();
    edge1Geo.dispose(); edge2Geo.dispose();
    edgeMat.dispose();  gearMat.dispose();
  }, [gear1Geo, gear2Geo, edge1Geo, edge2Geo, edgeMat, gearMat]);

  /* ── Animation + parameter-driven appearance ────────────────────────────── */
  useFrame((state, delta) => {
    if (!gear1Ref.current || !gear2Ref.current) return;
    const dt   = Math.min(delta, 0.05);
    const step = visualSpeed(rpm) * dt;

    gear1Ref.current.rotation.z += step;
    gear2Ref.current.rotation.z -= step;

    // Helical axial thrust: gears shift slightly along Z in opposite directions
    const axial = Math.sin(state.clock.elapsedTime * 1.8) * 0.014;
    gear1Ref.current.position.z =  axial;
    gear2Ref.current.position.z = -axial;

    const t = state.clock.elapsedTime;

    // Health-based material update
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

    // Temperature heat glow
    if (temperature > 80) {
      const hf = Math.min((temperature - 80) / 40, 1.0);
      gearMat.emissive.setHex(health === 'critical' ? 0xff1100 : 0xff6600);
      gearMat.emissiveIntensity = Math.max(gearMat.emissiveIntensity, hf * 0.28);
    }

    // Degraded-health rotational wobble
    if (health !== 'normal') {
      const w = Math.sin(t * 6) * vibration * 0.00025;
      gear1Ref.current.rotation.z += w;
      gear2Ref.current.rotation.z -= w;
    }
  });

  const lightColor     = health === 'critical' ? '#ff2200' :
                         health === 'warning'  ? '#ff8800' : '#88aaff';
  const lightIntensity = health === 'critical' ? 4.0 :
                         health === 'warning'  ? 2.0 : 0.7;

  return (
    <group position={[-CENTER_D / 2, 4, 0]}>

      {/* ───── Right-hand helical driving gear ────────────────────────── */}
      <group ref={gear1Ref}>
        <mesh geometry={gear1Geo} material={gearMat} castShadow receiveShadow />
        <lineSegments geometry={edge1Geo} material={edgeMat} />
        <GearShaft faceWidth={0.80} />
      </group>
      <GearMount height={4} />

      {/* ───── Left-hand helical driven gear ──────────────────────────── */}
      <group
        ref={gear2Ref}
        position={[CENTER_D, 0, 0]}
        rotation={[0, 0, TOOTH_OFFSET]}
      >
        <mesh geometry={gear2Geo} material={gearMat} castShadow receiveShadow />
        <lineSegments geometry={edge2Geo} material={edgeMat} />
        <GearShaft faceWidth={0.80} />
      </group>
      <group position={[CENTER_D, 0, 0]}>
        <GearMount height={4} />
      </group>

      {/* ───── Mesh contact zone ──────────────────────────────────────── */}
      <group position={[PITCH_R, 0, 0]}>
        <MeshSparks rpm={rpm} vibration={vibration} health={health} />
        <LubricationSheen health={health} />
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