import { useRef, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { GearMount, MeshSparks, HeatHaze, LubricationSheen } from '../effects/GearEffects.jsx';

/*
 * BEVEL GEAR PAIR — built from raw THREE.js primitives to match the reference photo.
 *
 * CROWN GEAR (large horizontal disc — reference "flat ring" gear):
 *   Body  : CylinderGeometry(tipR, baseR, H, segs)  axis=Y, wide ring at bottom
 *   Teeth : N BoxGeometry blocks standing on the TOP face of the disc, arranged in a
 *           ring at radius r_teeth, each rotated to face radially outward.
 *   Hub   : narrow cylinder through the bore
 *   Shaft : long vertical cylinder through the bore center
 *   Group animation: rotation.y += step  (spins like a record player / roundabout)
 *
 * PINION (smaller bevel gear at 90° — reference "upright coin" gear):
 *   Same construction but smaller, then geometry pre-rotated rotateZ(−π/2) so
 *   the disc lies in the YZ plane with axis along X (like a car wheel).
 *   Group animation: rotation.x += step * ratio  (spins like a car wheel)
 *
 * APEX (shared cone tip):
 *   Crown narrow face at y = +H_C/2  →  group at y=−(H_C/2+GAP)  →  apex at y≈0 ✓
 *   Pinion narrow face at x = +H_P/2  →  group at x=+(H_P/2+GAP)  →  apex at x≈0 ✓
 *   Crown body: y < 0 (below apex)   Pinion body: x > 0 (right of apex)  → zero overlap ✓
 */

// ── Crown gear dimensions ────────────────────────────────────────────────────
const C_BASE_R = 2.10;  // outer radius (wide face, at the bottom)
const C_TIP_R  = 1.15;  // inner radius (narrow face, apex side)
const C_H      = 0.70;  // cone height (distance between wide and narrow faces)
const C_HF     = C_H / 2;
const N_CT     = 22;    // crown tooth count
const C_T_H    = 0.52;  // tooth height (standing up from cone face)
const C_T_R    = (C_BASE_R + C_TIP_R) / 2;   // tooth ring radius = 1.625
const C_T_W    = 2 * C_T_R * Math.sin(Math.PI / N_CT) * 0.70;   // tooth width (circumferential)
const C_T_D    = (C_BASE_R - C_TIP_R) * 0.55; // tooth depth (radial extent)
const C_BORE   = 0.42;

// ── Pinion dimensions ────────────────────────────────────────────────────────
const P_BASE_R = 1.35;  // outer radius (wide face)
const P_TIP_R  = 0.68;  // inner radius (narrow/apex face)
const P_H      = 0.65;  // cone height
const P_HF     = P_H / 2;
const N_PT     = 16;    // pinion tooth count
const P_T_H    = 0.42;
const P_T_R    = (P_BASE_R + P_TIP_R) / 2;
const P_T_W    = 2 * P_T_R * Math.sin(Math.PI / N_PT) * 0.70;
const P_T_D    = (P_BASE_R - P_TIP_R) * 0.55;
const P_BORE   = 0.26;

const GAP   = 0.04;
const RATIO = N_CT / N_PT;  // ~1.375 — pinion spins faster

/** Build bevel gear BufferGeometry: frustum body + tooth boxes on the NARROW face */
function buildBevelGeo(baseR, tipR, H, nTeeth, tH, tR, tW, tD, boreR, forPinion) {
  const segs = Math.max(nTeeth * 2, 40);

  // Body: CylinderGeometry(topRadius, bottomRadius, height, segments)
  //   topRadius=tipR (narrow/apex end at y=+H/2), bottomRadius=baseR (wide end at y=-H/2)
  const body = new THREE.CylinderGeometry(tipR, baseR, H, segs, 1);

  // Hub: reinforcement column through bore
  const hub = new THREE.CylinderGeometry(boreR + 0.10, boreR + 0.10, H * 1.25, 20, 1);

  // Bottom rim flange
  const rim = new THREE.CylinderGeometry(baseR + 0.07, baseR + 0.07, 0.07, segs, 1);
  rim.translate(0, -H / 2 + 0.035, 0);

  // Teeth: stand on the NARROW face (y=+H/2, the apex/thin end)
  // Each tooth faces outward radially and stands perpendicular to the disc face (+Y)
  // For visual realism, tilted slightly outward (following the cone slope)
  const coneAngle = Math.atan2(baseR - tipR, H);  // cone half-angle (slope from vertical)
  const toothTilt = coneAngle * 0.6;               // tooth leans outward by ~60% of cone angle

  const toothGeos = [];
  for (let i = 0; i < nTeeth; i++) {
    const ang = (i / nTeeth) * Math.PI * 2;
    const tx = Math.cos(ang) * tR;
    const tz = Math.sin(ang) * tR;
    // Tooth center is on the narrow face, lifted by tH/2 so tooth base sits on the cone face
    const ty = H / 2 + tH / 2;

    const tooth = new THREE.BoxGeometry(tW, tH, tD);

    // 1. Tilt outward so tooth leans away from axis following cone slope
    tooth.applyMatrix4(new THREE.Matrix4().makeRotationX(toothTilt));
    // 2. Rotate around Y to correct angular position
    tooth.applyMatrix4(new THREE.Matrix4().makeRotationY(-ang));
    // 3. Translate to final position
    tooth.translate(tx, ty, tz);

    toothGeos.push(tooth);
  }

  const merged = mergeGeometries([body, hub, rim, ...toothGeos]);
  if (merged) {
    merged.computeVertexNormals();
    merged.computeBoundingSphere();
  }
  return merged || body;
}

/** Maps real sensor RPM → smooth visual rotation speed (rad/s). ~10.5 rad/s at 1950 rpm. */
function gearSpeed(rpm) {
  const r = Math.max(100, Math.min(rpm, 3000));
  return 3.5 + (r / 1950) * 7.0;
}

export default function BevelGearPair({ rpm = 1950, vibration = 2.3, health = 'normal', temperature = 72 }) {
  const crownRef  = useRef();
  const pinionRef = useRef();

  const gearMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color:              new THREE.Color(0x4e5d6e),
    metalness:          0.92,
    roughness:          0.20,
    clearcoat:          0.55,
    clearcoatRoughness: 0.07,
    envMapIntensity:    2.4,
    emissive:           new THREE.Color(0x000000),
    emissiveIntensity:  0,
  }), []);

  const shaftMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x2a3848), metalness: 0.96, roughness: 0.15, clearcoat: 0.5,
  }), []);

  // ── CROWN: large horizontal disc (axis=Y, built by buildBevelGeo directly)
  const crownGeo = useMemo(() =>
    buildBevelGeo(C_BASE_R, C_TIP_R, C_H, N_CT, C_T_H, C_T_R, C_T_W, C_T_D, C_BORE, false)
  , []);

  // ── PINION: smaller gear, pre-rotated so axis=X (rotateZ(-π/2) inside useMemo)
  const pinionGeo = useMemo(() => {
    const geo = buildBevelGeo(P_BASE_R, P_TIP_R, P_H, N_PT, P_T_H, P_T_R, P_T_W, P_T_D, P_BORE, true);
    // Rz(−90°): y→x, x→−y  →  puts gear axis along X (disc stands vertical in YZ plane)
    // tipR (narrow, was at y=+P_HF) → now at x=+P_HF
    // baseR (wide, was at y=−P_HF) → now at x=−P_HF
    geo.rotateZ(-Math.PI / 2);
    geo.computeVertexNormals();
    geo.computeBoundingSphere();
    return geo;
  }, []);

  // Vertical drive shaft through crown bore (axis=Y by default)
  const crownShaftGeo = useMemo(() => new THREE.CylinderGeometry(0.18, 0.18, 7.0, 18), []);

  // Horizontal shaft through pinion bore (axis=X: rotateZ(−π/2) on Y-cylinder)
  const pinionShaftGeo = useMemo(() => {
    const g = new THREE.CylinderGeometry(0.13, 0.13, 5.5, 16);
    g.rotateZ(Math.PI / 2);
    return g;
  }, []);

  useEffect(() => () => {
    crownGeo.dispose(); pinionGeo.dispose();
    crownShaftGeo.dispose(); pinionShaftGeo.dispose();
    gearMat.dispose(); shaftMat.dispose();
  }, [crownGeo, pinionGeo, crownShaftGeo, pinionShaftGeo, gearMat, shaftMat]);

  useFrame((state, delta) => {
    if (!crownRef.current || !pinionRef.current) return;

    // Clamp delta for frame-rate stability — prevents big jumps after tab switch
    const dt   = Math.min(delta, 0.033);
    const step = gearSpeed(rpm) * dt;

    // Crown: rotates like a roundabout / record player (around vertical Y axis)
    crownRef.current.rotation.y  += step;
    // Pinion: rotates like a car wheel (around its horizontal X axis)
    pinionRef.current.rotation.x += step * RATIO;

    const t = state.clock.elapsedTime;

    if (health === 'critical') {
      gearMat.color.setHex(0x5c2020); gearMat.roughness = 0.58;
      gearMat.emissive.setHex(0xcc2200);
      gearMat.emissiveIntensity = 0.12 + Math.sin(t * 4) * 0.05;
    } else if (health === 'warning') {
      gearMat.color.setHex(0x504020); gearMat.roughness = 0.38;
      gearMat.emissive.setHex(0xff8800); gearMat.emissiveIntensity = 0.07;
    } else {
      gearMat.color.setHex(0x4e5d6e); gearMat.roughness = 0.20;
      gearMat.emissive.setHex(0x000000); gearMat.emissiveIntensity = 0;
    }

    if (temperature > 80) {
      const hf = Math.min((temperature - 80) / 40, 1.0);
      gearMat.emissive.setHex(health === 'critical' ? 0xff1100 : 0xff6600);
      gearMat.emissiveIntensity = Math.max(gearMat.emissiveIntensity, hf * 0.28);
    }
  });

  const lightColor     = health === 'critical' ? '#ff2200' : health === 'warning' ? '#ff8800' : '#88aaff';
  const lightIntensity = health === 'critical' ? 4.0 : health === 'warning' ? 2.0 : 0.8;

  return (
    <group position={[0, 4, 0]}>

      {/*
       * CROWN GEAR — horizontal plate, axis=Y
       * buildBevelGeo creates the frustum+teeth with axis=Y directly (no extra rotation needed).
       * Narrow face (tipR, apex) at local y=+C_HF.
       * Group at y=−(C_HF+GAP) → apex at world y≈0. Crown body entirely in y<0.
       */}
      <group ref={crownRef} position={[0, -(C_HF + GAP), 0]}>
        <mesh geometry={crownGeo}       material={gearMat}  castShadow receiveShadow />
        <mesh geometry={crownShaftGeo}  material={shaftMat} castShadow />
      </group>

      {/*
       * PINION — vertical disc, axis=X (geometry pre-rotated Rz(−90°))
       * After Rz(−90°): tipR (narrow) now at x=+P_HF, baseR (wide) at x=−P_HF.
       * Group at x=+(P_HF+GAP) → apex at world x≈0. Pinion body entirely in x>0.
       */}
      <group ref={pinionRef} position={[P_HF + GAP, 0, 0]}>
        <mesh geometry={pinionGeo}      material={gearMat}  castShadow receiveShadow />
        <mesh geometry={pinionShaftGeo} material={shaftMat} castShadow />
      </group>

      <GearMount height={4.5} />

      {/* Mesh-point effects at the shared apex (0,0,0 in group space) */}
      <group position={[0, 0, 0]}>
        <MeshSparks rpm={rpm} vibration={vibration} health={health} />
        <LubricationSheen health={health} />
        <pointLight color={lightColor} intensity={lightIntensity} distance={8} decay={2} />
      </group>

      <group position={[0, 2.5, 0]}>
        <HeatHaze temperature={temperature} />
      </group>

    </group>
  );
}