# Implementation Plan: 3D Gear Animation Tab

## Overview

This implementation plan breaks down the 3D Gear Animation Tab feature into discrete coding tasks. The approach follows a bottom-up strategy: first establishing the state management foundation, then building reusable geometry utilities, followed by individual gear components, environment elements, and finally integrating everything into the main scene with transitions and controls.

**IMPORTANT ARCHITECTURAL NOTE**: This feature is integrated as a **tab within MainDashboard**, NOT as a separate route or sidebar navigation item. The GearScene component renders conditionally when `activeTab === '3d-animation'`, positioned after the "What-If Optimizer" tab.

## Tasks

- [x] 1. Create Zustand store for gear state management
  - Create `dashboard/src/store/gearStore.js` with activeGear and sensors state
  - Implement `setActiveGear` action to update active gear type
  - Implement `updateSensors` action to merge sensor data updates
  - Initialize with default values: activeGear='Spur', rpm=1950, temperature=72, vibration=2.3, load=45, health='normal'
  - _Requirements: 13.3, 4.1, 4.3, 4.5, 4.7_

- [x] 2. Create procedural geometry utility functions
  - [x] 2.1 Create `dashboard/src/utils/gearGeometry.js` with base geometry generators
    - Implement `createSpurTeeth(baseRadius, teethCount, toothHeight, toothWidth, toothDepth)` returning merged BufferGeometry
    - Implement `createHelicalTooth(helixAngle, height)` using ExtrudeGeometry with helical path
    - Implement `createHelixCurve(angle, height)` returning CatmullRomCurve3 for helical paths
    - Implement `createWormSpiral(radius, length, pitch, threadRadius)` using TubeGeometry
    - Implement `radialPosition(index, count, radius)` for tooth distribution
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 14.2, 14.3, 15.2, 16.2, 17.2_
  
  - [x] 2.2 Write unit tests for geometry utility functions
    - Test `createSpurTeeth` returns valid geometry with correct vertex count
    - Test `createHelixCurve` generates parametric curve at specified angle
    - Test `radialPosition` distributes positions evenly around circle
    - Test parameter validation rejects invalid inputs (negative radius, zero teeth)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [-] 3. Implement Spur Gear component
  - [x] 3.1 Create `dashboard/src/components/gears/SpurGearPair.jsx`
    - Generate base disc using CylinderGeometry (radius=2, height=0.5, segments=32)
    - Generate 16 teeth using `createSpurTeeth` utility and merge with base
    - Apply MeshStandardMaterial with metalness=0.85, roughness=0.25, color=#8a9bb0
    - Create second meshing gear offset by 4.2 units, counter-rotating
    - Implement useFrame hook to update rotation based on rpm prop
    - Apply vibration shake effect on X axis using sin(clock.elapsedTime) * vibration
    - Enable castShadow and receiveShadow properties
    - _Requirements: 1.1, 2.1, 3.1, 3.2, 3.3, 3.5, 3.6, 4.2, 4.6, 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [x] 3.2 Write unit tests for SpurGearPair component
    - Test component renders without errors
    - Test rotation speed updates when rpm prop changes
    - Test vibration effect applies mesh shake
    - _Requirements: 1.1, 4.2, 4.6_

- [-] 4. Implement Helical Gear component
  - [x] 4.1 Create `dashboard/src/components/gears/HelicalGearPair.jsx`
    - Generate base disc using CylinderGeometry (radius=2, height=0.6, segments=32)
    - Generate 18 twisted teeth using `createHelicalTooth` with 15° helix angle
    - Apply MeshStandardMaterial with metalness=0.85, roughness=0.25, color=#8a9bb0
    - Create second gear with opposite hand helix, offset by 4.3 units
    - Implement useFrame hook for rotation and axial oscillation (amplitude=0.05)
    - Apply vibration shake effect on X axis
    - Enable castShadow and receiveShadow properties
    - _Requirements: 1.2, 2.2, 3.1, 3.2, 3.3, 3.5, 3.6, 4.2, 4.6, 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [x] 4.2 Write unit tests for HelicalGearPair component
    - Test component renders with helical teeth
    - Test axial oscillation animates correctly
    - Test opposite hand helices on mating gears
    - _Requirements: 1.2, 15.4, 15.5_

- [x] 5. Implement Bevel Gear component
  - [x] 5.1 Create `dashboard/src/components/gears/BevelGearPair.jsx`
    - Generate frustum base using ConeGeometry (radiusTop=1.5, radiusBottom=2.5, height=1.5, segments=32)
    - Generate 14 tapered teeth along slant face using scaled BoxGeometry
    - Apply MeshStandardMaterial with metalness=0.85, roughness=0.25, color=#8a9bb0
    - Create mating gear rotated 90° on X axis with pitch cone apex at origin
    - Implement useFrame hook for synchronized rotation at right angles
    - Apply vibration shake effect on X axis
    - Enable castShadow and receiveShadow properties
    - _Requirements: 1.3, 2.3, 3.1, 3.2, 3.3, 3.5, 3.6, 4.2, 4.6, 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [ ]* 5.2 Write unit tests for BevelGearPair component
    - Test component renders conical frustum geometry
    - Test mating gear positioned at 90° angle
    - Test pitch cone apex alignment
    - _Requirements: 1.3, 16.3, 16.4_

- [-] 6. Implement Worm Gear component
  - [x] 6.1 Create `dashboard/src/components/gears/WormGearAssembly.jsx`
    - Generate worm shaft using CylinderGeometry (radius=0.4, height=4, segments=16)
    - Generate spiral ridge using `createWormSpiral` with TubeGeometry
    - Generate worm wheel as standard spur gear (20 teeth, radius=2)
    - Apply MeshStandardMaterial with metalness=0.85, roughness=0.25, color=#8a9bb0
    - Position worm on Z axis, wheel on Y axis
    - Implement useFrame hook with 20:1 rotation ratio (worm drives wheel)
    - Apply vibration shake effect on X axis
    - Enable castShadow and receiveShadow properties
    - _Requirements: 1.4, 2.4, 2.5, 3.1, 3.2, 3.3, 3.5, 3.6, 4.2, 4.6, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_
  
  - [ ]* 6.2 Write unit tests for WormGearAssembly component
    - Test component renders worm shaft and wheel
    - Test 20:1 rotation ratio implementation
    - Test worm drives wheel (not vice versa)
    - _Requirements: 1.4, 2.5, 17.6_

- [x] 7. Create factory environment components
  - [x] 7.1 Create `dashboard/src/components/environment/FactoryFloor.jsx`
    - Generate PlaneGeometry (40x40 units) rotated to horizontal
    - Create canvas-generated checker texture with colors #1a2030 and #141824
    - Apply texture with RepeatWrapping and repeat.set(4, 4)
    - Apply MeshStandardMaterial with texture
    - Add GridHelper overlay (size=40, divisions=40, colors=#3a4a5c and #2a3447)
    - Enable receiveShadow property on floor plane
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 7.2 Create `dashboard/src/components/environment/FactoryWalls.jsx`
    - Generate back wall PlaneGeometry (40x20) at position [0, 10, -20]
    - Generate left wall PlaneGeometry (40x20) at position [-20, 10, 0] rotated 90°
    - Apply MeshStandardMaterial with color #1c2333
    - _Requirements: 7.1, 7.2_
  
  - [x] 7.3 Create `dashboard/src/components/environment/StructuralColumns.jsx`
    - Generate BoxGeometry I-beams (0.4x18x0.4)
    - Position columns at corners: [-18,9,-18], [18,9,-18], [-18,9,18]
    - Apply MeshStandardMaterial with color #2a3447, metalness=0.6, roughness=0.4
    - _Requirements: 7.3, 7.4_
  
  - [x] 7.4 Write unit tests for environment components
    - Test FactoryFloor renders with checker texture
    - Test FactoryWalls render at correct positions
    - Test StructuralColumns positioned in corners
    - _Requirements: 6.1, 7.1, 7.3_

- [x] 8. Implement lighting system with sensor integration
  - [x] 8.1 Create `dashboard/src/components/lighting/SceneLighting.jsx`
    - Add AmbientLight with intensity=0.3, color=#ffffff
    - Add key SpotLight at [5,8,5] with intensity=1.2, color=#fff5e6 (warm)
    - Add fill SpotLight at [-4,6,3] with intensity=0.6, color=#e6f2ff (cool)
    - Add fill SpotLight at [2,5,-4] with intensity=0.5, color=#e6f2ff (cool)
    - Add PointLight at [0,2,0] for sensor-responsive effects
    - Enable castShadow on key SpotLight and PointLight
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x] 8.2 Implement sensor-responsive lighting effects
    - Implement `lerpColor(temp, min, max, color1, color2)` utility function
    - Update PointLight color based on temperature (65-95°C maps to #ff6b35 to #ff2200)
    - Update SpotLight intensity based on load (0-100% maps to 0.8 to 1.8)
    - Implement blinking effect for PointLight when health='warning' (opacity oscillates 0.3-1.0)
    - Set PointLight to solid red (#ff0000) when health='critical'
    - _Requirements: 4.4, 4.8, 5.1, 5.2, 8.4, 8.5_
  
  - [ ]* 8.3 Write unit tests for lighting utilities
    - Test `lerpColor` interpolates colors correctly at boundaries and midpoint
    - Test temperature-to-color mapping at 65°C, 80°C, and 95°C
    - Test load-to-intensity mapping at 0%, 50%, and 100%
    - _Requirements: 4.4, 4.8_

- [x] 9. Create atmospheric particle system
  - [x] 9.1 Create `dashboard/src/components/effects/AtmosphericParticles.jsx`
    - Generate BufferGeometry with 200 random point positions
    - Distribute positions in volume [-15,15] × [0,15] × [-15,15]
    - Apply PointsMaterial with size=0.05, color=#ffffff, opacity=0.3, transparent=true
    - Implement useFrame hook to drift particles upward (position.y += 0.01)
    - Wrap particles at y=15 back to y=0
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ]* 9.2 Write unit tests for AtmosphericParticles
    - Test component renders 200 particles
    - Test particles distributed in correct volume
    - Test upward drift animation
    - _Requirements: 9.1, 9.2_

- [-] 10. Implement 3D HUD text display
  - [x] 10.1 Create `dashboard/src/components/hud/HUD3D.jsx`
    - Use Text component from @react-three/drei
    - Display gear name from activeGear at position [-3, 4, 0], fontSize=0.4
    - Display RPM value from sensors.rpm at position [-3, 3.5, 0], fontSize=0.3
    - Apply material with color=#05cd99, emissive=#05cd99, emissiveIntensity=0.5
    - Update text when activeGear or sensors.rpm changes
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 10.2 Write unit tests for HUD3D component
    - Test component displays correct gear name
    - Test component displays correct RPM value
    - Test text updates when activeGear changes
    - _Requirements: 10.2, 10.3, 10.4_

- [x] 11. Checkpoint - Ensure all component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Create main GearScene component with Canvas setup
  - [x] 12.1 Create `dashboard/src/components/GearScene.jsx` main component
    - Import Canvas from @react-three/fiber
    - Configure Canvas with shadows, camera settings (fov=50, position=[5,3,5])
    - Set up PerspectiveCamera with makeDefault
    - Add Environment component with preset='warehouse'
    - Render Scene component inside Canvas
    - _Requirements: 13.1, 13.2, 13.3, 3.4_
  
  - [x] 12.2 Create internal Scene component
    - Read activeGear and sensors from useGearStore
    - Render SceneLighting component with sensor props
    - Render FactoryFloor, FactoryWalls, StructuralColumns components
    - Render AtmosphericParticles component
    - Render HUD3D component with activeGear and rpm props
    - _Requirements: 13.3, 4.1, 4.3, 4.5, 4.7_
  
  - [ ]* 12.3 Write integration tests for GearScene
    - Test Canvas renders without errors
    - Test Scene component reads from Zustand store
    - Test all environment components render together
    - _Requirements: 13.1, 13.3_

- [x] 13. Implement gear switching with AnimatePresence
  - [x] 13.1 Add gear assembly with transition animations
    - Wrap gear components in AnimatePresence from framer-motion
    - Conditionally render SpurGearPair when activeGear='Spur'
    - Conditionally render HelicalGearPair when activeGear='Helical'
    - Conditionally render BevelGearPair when activeGear='Bevel'
    - Conditionally render WormGearAssembly when activeGear='Worm'
    - Configure fade transition with initial={{ opacity: 0 }}, animate={{ opacity: 1 }}, exit={{ opacity: 0 }}
    - _Requirements: 1.5, 11.1, 11.3_
  
  - [x] 13.2 Implement camera position transitions with useSpring
    - Import useSpring and animated from @react-spring/three
    - Define camera positions for each gear type: Spur=[5,3,5], Helical=[6,4,4], Bevel=[4,5,6], Worm=[7,3,3]
    - Create spring animation for camera position based on activeGear
    - Configure spring with tension=120, friction=14
    - Wrap camera in animated.group with spring position
    - _Requirements: 11.2, 11.4_
  
  - [x] 13.3 Write integration tests for gear switching
    - Test gear components fade in/out when activeGear changes
    - Test camera position animates smoothly
    - Test lighting persists during transitions
    - _Requirements: 11.1, 11.2, 11.4_

- [x] 14. Implement camera controls
  - [x] 14.1 Add OrbitControls to Scene component
    - Import OrbitControls from @react-three/drei
    - Set enablePan=false
    - Set minDistance=3, maxDistance=12
    - Set minPolarAngle=Math.PI/6, maxPolarAngle=Math.PI/2.2
    - Set target=[0, 1, 0] to orbit around gear center
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 14.2 Write integration tests for OrbitControls
    - Test camera can orbit around gear center
    - Test zoom constraints enforced (min=3, max=12)
    - Test panning disabled
    - _Requirements: 12.2, 12.3, 12.4_

- [-] 15. Integrate GearScene into dashboard as a tab
  - [x] 15.1 Add 3D Gear Animation tab to MainDashboard
    - Import GearScene component in `dashboard/src/pages/MainDashboard.jsx`
    - Add new tab entry to TABS array: `{ id: '3d-animation', label: '🎨 3D Gear Animation' }`
    - Position tab after 'optimizer' (What-If Optimizer) in the TABS array
    - Add conditional rendering in tab content area: `{activeTab === '3d-animation' && <GearScene />}`
    - Remove any sidebar navigation references for gear animation
    - Test tab switching to GearScene component
    - _Requirements: 13.1, 13.5, 13.6, 13.7_
  
  - [x] 15.2 Write integration tests for tab navigation
    - Test tab renders GearScene component when activeTab='3d-animation'
    - Test tab appears in correct position (after What-If Optimizer)
    - Test tab switching preserves other dashboard state
    - _Requirements: 13.1, 13.5_

- [x] 16. Implement resource disposal and cleanup
  - [x] 16.1 Add useEffect cleanup for geometry and materials
    - Track created geometries and materials in refs
    - Implement useEffect cleanup function to dispose resources
    - Dispose geometries when gear type changes
    - Dispose materials when component unmounts
    - _Requirements: 18.5_
  
  - [ ]* 16.2 Write tests for resource disposal
    - Test geometries disposed when activeGear changes
    - Test materials disposed when component unmounts
    - Test no memory leaks during gear switching
    - _Requirements: 18.5_

- [-] 17. Optimize performance with mesh merging
  - [x] 17.1 Implement mesh merging for gear teeth
    - Use BufferGeometryUtils.mergeGeometries() to combine teeth
    - Merge all teeth into single mesh per gear
    - Reuse materials across similar meshes
    - Verify draw call reduction (target: <50 per frame)
    - _Requirements: 18.3, 18.4_
  
  - [ ]* 17.2 Write performance tests
    - Measure vertex count for each gear type (target: <50k)
    - Measure FPS during continuous animation (target: 60 FPS)
    - Test memory usage during gear switching
    - _Requirements: 18.3_

- [x] 18. Final checkpoint - Ensure all tests pass and verify visual quality
  - Run all unit and integration tests
  - Verify all four gear types render correctly
  - Verify sensor data updates reflect in visualization
  - Verify smooth transitions between gear types
  - Verify camera controls work as expected
  - Verify performance targets met (60 FPS, <50k vertices)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- All geometry is procedurally generated without external 3D models
- Three.js r128 compatibility maintained throughout (note: package.json shows 0.183.2 which is r183, may need version alignment)
- Resource disposal prevents memory leaks during gear switching
- Mesh merging optimizes performance by reducing draw calls

### Architectural Change: Tab-Based Integration

**Previous Approach** (Removed):
- Sidebar navigation item for "3D Gear Animation"
- Route definition in App.jsx for '/gear-animation'
- Separate page component accessed via routing

**Current Approach** (Implemented):
- Tab within MainDashboard component
- Positioned after "What-If Optimizer" tab
- Conditional rendering based on `activeTab === '3d-animation'`
- No routing or sidebar navigation required
- Seamless integration with dashboard state (gear type, sensors)

**Benefits**:
- Faster access (no page reload)
- Shared state with dashboard
- Better UX flow for comparing metrics with 3D visualization
- Reduced complexity (no route parameters or state passing)
