import { Canvas } from '@react-three/fiber';
import { PerspectiveCamera, OrbitControls, Environment } from '@react-three/drei';
import { useSpring, animated } from '@react-spring/three';
import * as THREE from 'three';
import { useGearStore } from '../store/gearStore';
import SceneLighting from './lighting/SceneLighting';
import FactoryFloor from './environment/FactoryFloor';
import FactoryWalls from './environment/FactoryWalls';
import StructuralColumns from './environment/StructuralColumns';
import GearPlatform from './environment/GearPlatform';
import AtmosphericParticles from './effects/AtmosphericParticles';
import HUD3D from './hud/HUD3D';
import SpurGearPair from './gears/SpurGearPair';
import HelicalGearPair from './gears/HelicalGearPair';
import BevelGearPair from './gears/BevelGearPair';
import WormGearAssembly from './gears/WormGearAssembly';

/**
 * AnimatedGear — wraps each gear with a framer-motion fade transition.
 */
function AnimatedGear({ children }) {
  return <group>{children}</group>;
}

/**
 * Scene — all 3-D objects live here, inside the Canvas.
 *
 * Key visual improvements over the old Scene:
 *
 *  1. <Environment preset="warehouse" />
 *     Loads a high-dynamic-range equirectangular environment map.
 *     MeshPhysicalMaterial uses it automatically for IBL (image-based lighting),
 *     which is the single biggest reason machined metal looks convincing in 3D.
 *     The "warehouse" preset has a neutral grey-blue tone that suits industrial steel.
 *     Other good choices: "studio", "city", "dawn".
 *
 *  2. background={false}  — lets the Canvas CSS background (#0d1117) show through
 *     so the HDRI is used only for reflections, not as a visible sky sphere.
 *
 *  3. Camera spring animation kept — smooth interpolation to per-gear positions.
 */
function Scene() {
  const activeGear = useGearStore((state) => state.activeGear);
  const sensors    = useGearStore((state) => state.sensors);

  // Camera positions tuned to each gear's actual geometry size.
  // Spur & Helical pairs are now centred on the origin (X=0) via a -CENTER_D/2 offset.
  const cameraPositions = {
    Spur:    [0, 5, 12],
    Helical: [0, 5, 11],
    Bevel:   [3, 6,  6],   // see horizontal crown + vertical pinion together
    Worm:    [4, 7,  7],   // see lifted worm shaft + wheel + housing
  };

  const springProps = useSpring({
    position: cameraPositions[activeGear],
    config: { tension: 120, friction: 14 },
  });

  return (
    <>
      {/* ─── HDRI Environment ─────────────────────────────────────────────
          This is the #1 upgrade. Without it, metallic materials look flat
          because they have nothing to reflect.
          background={false} keeps the scene background as set in <Canvas>.
      ──────────────────────────────────────────────────────────────────── */}
      <Environment preset="warehouse" background={false} />

      {/* Animated camera */}
      <animated.group position={springProps.position}>
        <PerspectiveCamera makeDefault fov={50} />
      </animated.group>

      {/* Lighting */}
      <SceneLighting />

      {/* Factory environment */}
      <FactoryFloor />
      <FactoryWalls />
      <StructuralColumns />
      <GearPlatform />

      {/* Atmospheric depth particles */}
      <AtmosphericParticles />

      {/* Active gear */}
      {activeGear === 'Spur' && (
        <AnimatedGear>
          <SpurGearPair
            rpm={sensors.rpm}
            vibration={sensors.vibration}
            health={sensors.health}
            temperature={sensors.temperature}
          />
        </AnimatedGear>
      )}
      {activeGear === 'Helical' && (
        <AnimatedGear>
          <HelicalGearPair
            rpm={sensors.rpm}
            vibration={sensors.vibration}
            health={sensors.health}
            temperature={sensors.temperature}
          />
        </AnimatedGear>
      )}
      {activeGear === 'Bevel' && (
        <AnimatedGear>
          <BevelGearPair
            rpm={sensors.rpm}
            vibration={sensors.vibration}
            health={sensors.health}
            temperature={sensors.temperature}
          />
        </AnimatedGear>
      )}
      {activeGear === 'Worm' && (
        <AnimatedGear>
          <WormGearAssembly rpm={sensors.rpm} vibration={sensors.vibration} health={sensors.health} />
        </AnimatedGear>
      )}

      {/* 3D HUD (uncomment when ready) */}
      {/* <HUD3D /> */}

      <OrbitControls
        enablePan={false}
        minDistance={4}
        maxDistance={20}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.2}
        target={[0, 4, 0]}
      />
    </>
  );
}

/**
 * GearScene — main export.
 *
 * Canvas changes:
 *  - background: '#0d1117'  (dark charcoal — industrial night scene)
 *    The old #f5f7fa whitish background made metal look plastic.
 *  - toneMapping: ACESFilmicToneMapping  (unchanged — good choice)
 *  - toneMappingExposure: 1.4  (slightly reduced from 2.0; ACES at 2.0 was overblown
 *    for the new brighter lighting setup)
 *  - dpr: [1, 2]  (unchanged — good)
 *
 * Optional post-processing bloom (install first):
 *   npm i @react-three/postprocessing
 * Then replace the bare <Scene /> block with the commented block below.
 */
export default function GearScene() {
  return (
    <Canvas
      shadows
      style={{ width: '100%', height: '100vh', background: '#0d1117' }}
      gl={{
        antialias:            true,
        alpha:                false,
        powerPreference:      'high-performance',
        toneMapping:          THREE.ACESFilmicToneMapping,
        toneMappingExposure:  1.4,
        pixelRatio:           Math.min(window.devicePixelRatio, 2),
      }}
      dpr={[1, 2]}
      frameloop="always"
    >
      <Scene />

      {/*
       * ── OPTIONAL: Bloom post-processing ──────────────────────────────────
       * Adds a soft glow around bright metallic highlights and emissive lights.
       * Requires:  npm i @react-three/postprocessing
       *
       * To enable:
       *  1. Remove <Scene /> above.
       *  2. Uncomment everything below.
       *  3. Add this import at the top of the file:
       *       import { EffectComposer, Bloom } from '@react-three/postprocessing';
       *
       * <EffectComposer>
       *   <Scene />
       *   <Bloom
       *     luminanceThreshold={0.75}
       *     luminanceSmoothing={0.4}
       *     intensity={0.6}
       *     mipmapBlur
       *   />
       * </EffectComposer>
       * ─────────────────────────────────────────────────────────────────────
       */}
    </Canvas>
  );
}