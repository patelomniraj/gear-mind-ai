import { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/* ═══════════════════════════════════════════════════════════════════════════
 *  GearShaft
 *  Shaft cylinder + bearing torus rings + inner race discs.
 *  Placed inside the ROTATING gear group so shaft spins with gear.
 *  (A cylinder is rotationally symmetric — looks identical at any angle.)
 * ═══════════════════════════════════════════════════════════════════════════ */
export function GearShaft({ faceWidth = 0.60, shaftRadius = 0.22 }) {
  const shaftLen = faceWidth + 3.4;
  const bearingZ = faceWidth / 2 + 0.65;

  const shaftMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color:    new THREE.Color(0x2a3340),
    metalness: 0.98, roughness: 0.28, clearcoat: 0.3, clearcoatRoughness: 0.12,
  }), []);

  const bearingMat = useMemo(() => new THREE.MeshPhysicalMaterial({
    color:    new THREE.Color(0x111820),
    metalness: 0.92, roughness: 0.55,
  }), []);

  const shaftGeo = useMemo(() => {
    const g = new THREE.CylinderGeometry(shaftRadius, shaftRadius, shaftLen, 28);
    g.rotateX(Math.PI / 2);
    return g;
  }, [shaftRadius, shaftLen]);

  // Outer bearing torus
  const outerGeo = useMemo(() =>
    new THREE.TorusGeometry(shaftRadius * 2.3, shaftRadius * 0.58, 14, 28)
  , [shaftRadius]);

  // Inner race disc
  const raceGeo = useMemo(() => {
    const g = new THREE.CylinderGeometry(shaftRadius * 1.4, shaftRadius * 1.4, 0.09, 22);
    g.rotateX(Math.PI / 2);
    return g;
  }, [shaftRadius]);

  useEffect(() => () => {
    shaftGeo.dispose(); outerGeo.dispose(); raceGeo.dispose();
    shaftMat.dispose(); bearingMat.dispose();
  }, [shaftGeo, outerGeo, raceGeo, shaftMat, bearingMat]);

  return (
    <group>
      <mesh geometry={shaftGeo}  material={shaftMat}   castShadow />
      {/* −Z bearing */}
      <mesh geometry={outerGeo}  material={bearingMat} position={[0, 0, -bearingZ]} />
      <mesh geometry={raceGeo}   material={shaftMat}   position={[0, 0, -bearingZ]} />
      {/* +Z bearing */}
      <mesh geometry={outerGeo}  material={bearingMat} position={[0, 0,  bearingZ]} />
      <mesh geometry={raceGeo}   material={shaftMat}   position={[0, 0,  bearingZ]} />
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
 *  GearMount
 *  Tapered support pedestal beneath a gear.
 *  Internal positioning: top = y=0 (caller's origin), bottom = y=−height.
 *  STATIC — must NOT be placed inside a rotating gear group.
 * ═══════════════════════════════════════════════════════════════════════════ */
export function GearMount({ height = 4 }) {
  const mat = useMemo(() => new THREE.MeshStandardMaterial({
    color: new THREE.Color(0x1c2535), metalness: 0.85, roughness: 0.45,
  }), []);

  const postGeo  = useMemo(() => new THREE.CylinderGeometry(0.17, 0.25, height, 14),  [height]);
  const capGeo   = useMemo(() => new THREE.CylinderGeometry(0.56, 0.56, 0.10, 20),    []);
  const footGeo  = useMemo(() => new THREE.BoxGeometry(0.85, 0.10, 0.80),              []);

  useEffect(() => () => {
    postGeo.dispose(); capGeo.dispose(); footGeo.dispose(); mat.dispose();
  }, [postGeo, capGeo, footGeo, mat]);

  return (
    <group position={[0, -height / 2, 0]}>
      <mesh geometry={postGeo} material={mat} castShadow />
      <mesh geometry={capGeo}  material={mat} position={[0,  height / 2 - 0.05, 0]} />
      <mesh geometry={footGeo} material={mat} position={[0, -height / 2 + 0.05, 0]} />
    </group>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
 *  MeshSparks
 *  Spark particle burst at the gear tooth contact zone.
 *  Renders at LOCAL origin — caller wraps in <group position={meshPt}>.
 *  Intensity scales with vibration and health state.
 * ═══════════════════════════════════════════════════════════════════════════ */
const N_SPARKS = 60;

export function MeshSparks({ rpm = 60, vibration = 2.3, health = 'normal' }) {
  const posAttr = useRef();
  const pos = useMemo(() => new Float32Array(N_SPARKS * 3), []);
  const vel = useMemo(() => new Float32Array(N_SPARKS * 3), []);
  const age = useMemo(() => {
    const a = new Float32Array(N_SPARKS);
    for (let i = 0; i < N_SPARKS; i++) a[i] = Math.random();
    return a;
  }, []);

  const lifespan  = health === 'critical' ? 0.30 : health === 'warning' ? 0.50 : 0.70;
  const intensity = health === 'critical' ? 3.0  : health === 'warning' ? 1.8  :
                    Math.max(0.4, vibration / 8);

  const spawn = (i) => {
    pos[i*3]   = (Math.random() - 0.5) * 0.10;
    pos[i*3+1] = (Math.random() - 0.5) * 0.10;
    pos[i*3+2] = (Math.random() - 0.5) * 0.10;
    const spd   = (0.5 + Math.random() * 1.3) * intensity * 0.38;
    const theta = Math.random() * Math.PI * 2;
    const phi   = (Math.random() - 0.4) * Math.PI;
    vel[i*3]   = Math.cos(theta) * Math.cos(phi) * spd;
    vel[i*3+1] = Math.sin(phi)   * spd + 0.45;
    vel[i*3+2] = Math.sin(theta) * Math.cos(phi) * spd * 0.45;
    age[i] = 0;
  };

  // Stagger initial particles
  useMemo(() => { for (let i = 0; i < N_SPARKS; i++) spawn(i); }, []); // eslint-disable-line

  useFrame((_, delta) => {
    if (!posAttr.current) return;
    const dt = Math.min(delta, 0.05);
    for (let i = 0; i < N_SPARKS; i++) {
      age[i] += dt;
      if (age[i] >= lifespan) {
        spawn(i);
      } else {
        pos[i*3]   += vel[i*3]   * dt;
        pos[i*3+1] += vel[i*3+1] * dt;
        pos[i*3+2] += vel[i*3+2] * dt;
        vel[i*3+1] -= 4.5 * dt;
      }
    }
    posAttr.current.needsUpdate = true;
  });

  const color = health === 'critical' ? '#ff2200' :
                health === 'warning'  ? '#ff8000' : '#ffcc33';
  const size  = health === 'critical' ? 0.065 : 0.042;

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          ref={posAttr}
          attach="attributes-position"
          count={N_SPARKS}
          array={pos}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={size}
        color={color}
        transparent
        opacity={0.92}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
 *  HeatHaze
 *  Rising orange/red heat particles above a hot gear.
 *  Renders at local origin — caller wraps in <group position={[x, y+1, z]}>.
 *  Only visible when temperature > 75°C.
 * ═══════════════════════════════════════════════════════════════════════════ */
const N_HEAT = 40;

export function HeatHaze({ temperature = 72 }) {
  const intensity = Math.max(0, Math.min((temperature - 75) / 45, 1.0));
  const posAttr = useRef();

  const pos = useMemo(() => {
    const a = new Float32Array(N_HEAT * 3);
    for (let i = 0; i < N_HEAT; i++) {
      a[i*3]   = (Math.random() - 0.5) * 5.5;
      a[i*3+1] = Math.random() * 3.5;
      a[i*3+2] = (Math.random() - 0.5) * 2.0;
    }
    return a;
  }, []);

  const spd = useMemo(() => {
    const s = new Float32Array(N_HEAT);
    for (let i = 0; i < N_HEAT; i++) s[i] = 0.25 + Math.random() * 0.85;
    return s;
  }, []);

  useFrame((state, delta) => {
    if (!posAttr.current || intensity <= 0) return;
    const dt = Math.min(delta, 0.05);
    for (let i = 0; i < N_HEAT; i++) {
      pos[i*3+1] += spd[i] * dt * intensity * 1.3;
      pos[i*3]   += Math.sin(state.clock.elapsedTime * 0.6 + i * 1.4) * 0.006;
      if (pos[i*3+1] > 4.0) {
        pos[i*3]   = (Math.random() - 0.5) * 5.5;
        pos[i*3+1] = -0.3;
        pos[i*3+2] = (Math.random() - 0.5) * 2.0;
      }
    }
    posAttr.current.needsUpdate = true;
  });

  if (intensity <= 0) return null;

  const color = temperature > 110 ? '#ff1100' :
                temperature > 92  ? '#ff5500' : '#ff9933';

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          ref={posAttr}
          attach="attributes-position"
          count={N_HEAT}
          array={pos}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08 + intensity * 0.07}
        color={color}
        transparent
        opacity={0.22 + intensity * 0.32}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
 *  LubricationSheen
 *  Slow-orbiting green/gold droplets around the mesh zone.
 *  Visible ONLY when health === 'normal' (well-lubricated).
 * ═══════════════════════════════════════════════════════════════════════════ */
const N_OIL = 22;

export function LubricationSheen({ health = 'normal' }) {
  const posAttr = useRef();
  const pos = useMemo(() => {
    const a = new Float32Array(N_OIL * 3);
    for (let i = 0; i < N_OIL; i++) {
      const ang = (i / N_OIL) * Math.PI * 2;
      const r   = 0.35 + Math.random() * 0.25;
      a[i*3]   = Math.cos(ang) * r;
      a[i*3+1] = (Math.random() - 0.5) * 0.6;
      a[i*3+2] = Math.sin(ang) * r * 0.4;
    }
    return a;
  }, []);

  useFrame((state) => {
    if (!posAttr.current || health !== 'normal') return;
    const t = state.clock.elapsedTime;
    for (let i = 0; i < N_OIL; i++) {
      const ang = t * 0.35 + i * (Math.PI * 2 / N_OIL);
      const r   = 0.30 + Math.sin(t * 0.6 + i) * 0.14;
      pos[i*3]   = Math.cos(ang) * r;
      pos[i*3+1] = Math.sin(t * 0.5 + i * 0.9) * 0.22;
      pos[i*3+2] = Math.sin(ang) * r * 0.45;
    }
    posAttr.current.needsUpdate = true;
  });

  if (health !== 'normal') return null;

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          ref={posAttr}
          attach="attributes-position"
          count={N_OIL}
          array={pos}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.038}
        color="#44cc88"
        transparent
        opacity={0.65}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}
