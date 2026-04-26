import { useRef, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

// ── constants ────────────────────────────────────────────────────────────────
const WORM_R      = 0.42;   // worm shaft radius
const WORM_LEN    = 5.6;    // worm shaft length along Z
const WHEEL_R     = 1.55;   // worm wheel pitch radius  (wheel disc radius)
const WHEEL_T     = 24;     // number of wheel teeth
const WHEEL_FW    = 0.48;   // face width (thickness of wheel disc)
const CENTRE      = WORM_R + WHEEL_R;   // = 1.97  (worm centre → wheel centre)

// Speed: ~10.5 rad/s at 1950 rpm  (same formula as other gears)
function gearSpeed(rpm) {
  return 3.5 + (Math.max(100, Math.min(rpm, 3000)) / 1950) * 7.0;
}

// ── Build worm shaft geometry (cylinder + flanges + helical ridge) ───────────
function buildWormGeo() {
  const shaft = new THREE.CylinderGeometry(WORM_R, WORM_R, WORM_LEN, 32);
  shaft.rotateZ(Math.PI / 2);   // lay along X (like a car axle)

  const flange = (x) => {
    const f = new THREE.CylinderGeometry(0.60, 0.60, 0.22, 24);
    f.rotateZ(Math.PI / 2);
    f.translate(x, 0, 0);
    return f;
  };

  // Helical ridge: stack of angled tori approximated by rotated thin-cylinder rings
  const ridges = [];
  const turns  = 6;
  const pitch  = (WORM_LEN * 0.75) / turns;
  for (let i = 0; i < turns; i++) {
    const x   = -WORM_LEN * 0.35 + i * pitch;
    const seg = new THREE.TorusGeometry(WORM_R + 0.14, 0.07, 8, 20);
    seg.rotateY(Math.PI / 2);  // orient torus for X-axis
    seg.translate(x, 0, 0);
    ridges.push(seg);
  }

  const geo = mergeGeometries([shaft, flange(-2.55), flange(+2.55), ...ridges]);
  ridges.forEach(r => r.dispose());
  if (geo) { geo.computeVertexNormals(); geo.computeBoundingSphere(); }
  return geo || shaft;
}

// ── Build worm wheel geometry (flat disc + radial teeth) ─────────────────────
function buildWheelGeo() {
  // Disc body: CylinderGeometry, axis=Y. Will be rotated to axis=Z (like a car wheel).
  const disc = new THREE.CylinderGeometry(WHEEL_R, WHEEL_R, WHEEL_FW, 48, 1);

  // Hub boss
  const hub = new THREE.CylinderGeometry(0.28, 0.28, WHEEL_FW * 1.6, 18);

  // Teeth: boxes arranged radially on the outer disc rim
  const tW = 2 * WHEEL_R * Math.sin(Math.PI / WHEEL_T) * 0.72;
  const tH = 0.28;   // tooth radial height
  const tD = WHEEL_FW * 0.88;

  const toothGeos = [];
  for (let i = 0; i < WHEEL_T; i++) {
    const ang = (i / WHEEL_T) * Math.PI * 2;
    const r   = WHEEL_R + tH / 2;
    const tooth = new THREE.BoxGeometry(tW, tH, tD);
    // rotate box so its "height" (local Y) points radially outward
    tooth.applyMatrix4(new THREE.Matrix4().makeRotationZ(ang));
    tooth.translate(Math.cos(ang) * r, Math.sin(ang) * r, 0);
    toothGeos.push(tooth);
  }

  const geo = mergeGeometries([disc, hub, ...toothGeos]);
  toothGeos.forEach(t => t.dispose());
  if (geo) {
    // Rotate so the disc stands vertically like a car wheel
    // rotateZ(π/2): makes wheel vertical, spinning around X-axis
    geo.rotateZ(Math.PI / 2);
    geo.computeVertexNormals();
    geo.computeBoundingSphere();
  }
  return geo || disc;
}

export default function WormGearAssembly({ rpm = 1950, vibration = 2.3, health = 'normal' }) {
  const wormRef  = useRef();
  const wheelRef = useRef();

  // ── Material (local — no shared singleton that might be undefined) ──────────
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

  const shaftMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x2a3848), metalness: 0.96, roughness: 0.16, clearcoat: 0.5,
  }), []);

  const housingMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x1e2a3a), metalness: 0.88, roughness: 0.42, clearcoat: 0.2,
  }), []);

  // ── Geometries ───────────────────────────────────────────────────────────────
  const wormGeo    = useMemo(() => buildWormGeo(),  []);
  const wheelGeo   = useMemo(() => buildWheelGeo(), []);

  // Axle rod through wheel (axis=X for vertical wheel)
  const axleGeo = useMemo(() => {
    const g = new THREE.CylinderGeometry(0.12, 0.12, 5.8, 16);
    g.rotateZ(Math.PI / 2);  // orient along X-axis (horizontal through vertical wheel)
    return g;
  }, []);

  useEffect(() => () => {
    wormGeo.dispose(); wheelGeo.dispose();
    axleGeo.dispose();
    gearMat.dispose(); shaftMat.dispose(); housingMat.dispose();
  }, [wormGeo, wheelGeo, axleGeo, gearMat, shaftMat, housingMat]);

  // ── Animation ─────────────────────────────────────────────────────────────
  useFrame((_state, delta) => {
    const dt = Math.min(delta, 0.033);
    const ws = gearSpeed(rpm) * dt;       // worm angular step  (~10 rad/s)
    const hs = ws / WHEEL_T;             // wheel angular step (1/24 worm speed)

    if (wormRef.current)  wormRef.current.rotation.x  += ws;  // rotate around longitudinal axis (like a screw/car axle)
    if (wheelRef.current) wheelRef.current.rotation.x += hs;  // rotate like a car wheel (around horizontal axle)
  });

  // ── JSX ──────────────────────────────────────────────────────────────────
  return (
    <group position={[0, 5.5, 0]}>

      {/* Worm shaft — horizontal, spins around Z */}
      <mesh ref={wormRef} geometry={wormGeo} material={gearMat} castShadow receiveShadow />

      {/* Shaft bearing blocks at each end */}
      {[-3.1, 3.1].map((x, i) => (
        <group key={i} position={[x, 0, 0]}>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.18, 0.18, 0.40, 16]} />
            <meshStandardMaterial color={0x0a0e14} />
          </mesh>
        </group>
      ))}

      {/* Worm wheel — spins around X, centre below worm */}
      <mesh
        ref={wheelRef}
        geometry={wheelGeo}
        material={gearMat}
        position={[0, -CENTRE, 0]}
        castShadow receiveShadow
      />

      {/* Axle through wheel */}
      <mesh geometry={axleGeo} material={shaftMat} position={[0, -CENTRE, 0]} castShadow />

      {/* Wheel bearing blocks */}
      {[-2.5, 2.5].map((x, i) => (
        <group key={i} position={[x, -CENTRE, 0]}>
          <mesh castShadow>
            <boxGeometry args={[0.32, 0.48, 0.45]} />
            <primitive object={housingMat} attach="material" />
          </mesh>
        </group>
      ))}

      {/* Support columns */}
      {[-2.5, 2.5].map((x, i) => (
        <mesh key={i} position={[x, -CENTRE / 2, 0]} castShadow>
          <boxGeometry args={[0.22, CENTRE, 0.22]} />
          <primitive object={housingMat} attach="material" />
        </mesh>
      ))}

      {/* Base plate */}
      <mesh position={[0, -CENTRE - 0.45, 0]} castShadow>
        <boxGeometry args={[6.5, 0.18, 1.80]} />
        <meshPhysicalMaterial color={0x161e28} metalness={0.85} roughness={0.50} />
      </mesh>

      <pointLight position={[0, -CENTRE * 0.5, 0]} color="#88aaff" intensity={0.8} distance={7} decay={2} />

    </group>
  );
}