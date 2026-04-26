# Requirements Document

## Introduction

This document specifies the requirements for a production-ready 3D Gear Animation Tab for the React/Vite predictive maintenance dashboard. The feature renders industrial gear types (Spur, Helical, Bevel, Worm) using Three.js and React Three Fiber, with real-time sensor data integration from a Zustand store. The 3D scene includes a factory environment, dynamic lighting, and smooth transitions between gear types.

**Integration Approach**: The 3D Gear Animation is implemented as a **tab within the MainDashboard component**, positioned after the "What-If Optimizer" tab. This tab-based approach provides seamless access to 3D visualization without requiring separate routing or sidebar navigation, allowing users to quickly switch between health metrics, SHAP analysis, and 3D visualization while preserving dashboard state.

## Glossary

- **Gear_Animation_Tab**: The new React component that renders 3D gear visualizations
- **Zustand_Store**: Shared state management store containing activeGear and sensor data
- **Three.js**: JavaScript 3D graphics library (r128 compatible)
- **React_Three_Fiber**: React renderer for Three.js
- **Spur_Gear**: Flat disc gear with radially arranged rectangular teeth
- **Helical_Gear**: Gear with twisted teeth along a helical path (15° helix angle)
- **Bevel_Gear**: Conical gear with tapered teeth for 90° axis transmission
- **Worm_Gear**: Worm shaft with spiral ridge driving a perpendicular wheel (20:1 ratio)
- **MeshStandardMaterial**: Three.js physically-based material with metalness and roughness
- **useFrame**: React Three Fiber hook for animation loop updates
- **OrbitControls**: Three.js camera control for user interaction
- **AnimatePresence**: Framer-motion component for transition animations
- **Procedural_Geometry**: Geometry created programmatically without external model files

## Requirements

### Requirement 1: Gear Type Rendering

**User Story:** As a maintenance operator, I want to view exactly one of four industrial gear types at a time, so that I can visually inspect the currently monitored gear.

#### Acceptance Criteria

1. WHEN activeGear value is "Spur", THE Gear_Animation_Tab SHALL render a Spur_Gear using CylinderGeometry base with 16 BoxGeometry teeth merged radially
2. WHEN activeGear value is "Helical", THE Gear_Animation_Tab SHALL render a Helical_Gear using CylinderGeometry base with ExtrudeGeometry teeth twisted at 15° helix angle
3. WHEN activeGear value is "Bevel", THE Gear_Animation_Tab SHALL render a Bevel_Gear using ConeGeometry frustum base with tapered teeth along slant face
4. WHEN activeGear value is "Worm", THE Gear_Animation_Tab SHALL render a Worm_Gear using CylinderGeometry shaft with TubeGeometry spiral ridge
5. THE Gear_Animation_Tab SHALL render exactly one gear type at any given time based on activeGear value from Zustand_Store
6. THE Gear_Animation_Tab SHALL use only Procedural_Geometry without external 3D model files

### Requirement 2: Meshing Gear Pairs

**User Story:** As a maintenance operator, I want to see meshing gear pairs, so that I can understand the mechanical interaction between gears.

#### Acceptance Criteria

1. WHEN Spur_Gear is rendered, THE Gear_Animation_Tab SHALL render a second meshing Spur_Gear slightly offset and counter-rotating
2. WHEN Helical_Gear is rendered, THE Gear_Animation_Tab SHALL render two meshing gears with opposite hand helices and subtle axial oscillation
3. WHEN Bevel_Gear is rendered, THE Gear_Animation_Tab SHALL render a mating gear at 90° on X axis with pitch cone apex meeting at origin
4. WHEN Worm_Gear is rendered, THE Gear_Animation_Tab SHALL render a worm shaft on Z axis and wheel on Y axis with 20:1 rotation ratio
5. THE Gear_Animation_Tab SHALL ensure worm drives wheel only in Worm_Gear configuration

### Requirement 3: Material and Rendering Properties

**User Story:** As a maintenance operator, I want realistic metallic gear rendering, so that the visualization appears professional and industrial.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL apply MeshStandardMaterial to all gears with metalness 0.85
2. THE Gear_Animation_Tab SHALL apply MeshStandardMaterial to all gears with roughness 0.25
3. THE Gear_Animation_Tab SHALL apply MeshStandardMaterial to all gears with color #8a9bb0
4. THE Gear_Animation_Tab SHALL add environment map using useEnvironment preset 'warehouse'
5. THE Gear_Animation_Tab SHALL enable castShadow property on all gear meshes
6. THE Gear_Animation_Tab SHALL enable receiveShadow property on all gear meshes

### Requirement 4: Sensor Data Integration

**User Story:** As a maintenance operator, I want gear rotation speed to reflect real-time RPM sensor data, so that the visualization matches actual equipment behavior.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL read sensors.rpm value from Zustand_Store
2. WHEN useFrame hook executes, THE Gear_Animation_Tab SHALL update gear rotation speed based on sensors.rpm multiplier
3. THE Gear_Animation_Tab SHALL read sensors.temperature value from Zustand_Store
4. WHEN sensors.temperature changes, THE Gear_Animation_Tab SHALL interpolate PointLight color from #ff6b35 to #ff2200 between 65°C and 95°C
5. THE Gear_Animation_Tab SHALL read sensors.vibration value from Zustand_Store
6. WHEN sensors.vibration changes, THE Gear_Animation_Tab SHALL apply mesh shake on X axis using sin(clock.elapsedTime)
7. THE Gear_Animation_Tab SHALL read sensors.load value from Zustand_Store
8. WHEN sensors.load changes, THE Gear_Animation_Tab SHALL interpolate SpotLight intensity from 0.8 to 1.8 over 0-100% load range

### Requirement 5: Health Status Visual Feedback

**User Story:** As a maintenance operator, I want visual alerts when gear health degrades, so that I can quickly identify critical conditions.

#### Acceptance Criteria

1. WHEN sensors.health equals 'warning', THE Gear_Animation_Tab SHALL render a blinking amber PointLight
2. WHEN sensors.health equals 'critical', THE Gear_Animation_Tab SHALL render a red PointLight
3. WHEN sensors.health equals 'critical', THE Gear_Animation_Tab SHALL multiply vibration effect by 3
4. WHEN sensors.health equals 'critical', THE Gear_Animation_Tab SHALL increase rotation speed multiplier

### Requirement 6: Factory Environment Floor

**User Story:** As a maintenance operator, I want a realistic factory floor, so that the gear visualization has industrial context.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL render a PlaneGeometry floor with dimensions 40x40 units
2. THE Gear_Animation_Tab SHALL apply a canvas-generated checker texture to the floor with colors #1a2030 and #141824
3. THE Gear_Animation_Tab SHALL overlay a GridHelper on the floor plane
4. THE Gear_Animation_Tab SHALL enable receiveShadow property on the floor plane

### Requirement 7: Factory Environment Backdrop

**User Story:** As a maintenance operator, I want factory walls and structural elements, so that the scene feels like an industrial setting.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL render a back wall plane panel with color #1c2333
2. THE Gear_Animation_Tab SHALL render a left wall plane panel with color #1c2333
3. THE Gear_Animation_Tab SHALL render tall BoxGeometry I-beam columns in corners
4. THE Gear_Animation_Tab SHALL position structural columns to frame the scene

### Requirement 8: Lighting System

**User Story:** As a maintenance operator, I want dynamic lighting that responds to sensor data, so that the scene provides visual feedback about equipment status.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL render an AmbientLight with intensity 0.3
2. THE Gear_Animation_Tab SHALL render three SpotLights: one warm top key light and two cool fill lights
3. THE Gear_Animation_Tab SHALL render a PointLight inside gear housing area
4. WHEN sensors.temperature changes, THE Gear_Animation_Tab SHALL update PointLight color based on temperature interpolation
5. WHEN sensors.load changes, THE Gear_Animation_Tab SHALL update SpotLight intensity based on load interpolation

### Requirement 9: Atmospheric Effects

**User Story:** As a maintenance operator, I want atmospheric particles, so that the scene has depth and realism.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL render 200 Points as atmospheric particles
2. THE Gear_Animation_Tab SHALL animate particles drifting upward slowly
3. THE Gear_Animation_Tab SHALL distribute particles throughout the scene volume

### Requirement 10: 3D HUD Display

**User Story:** As a maintenance operator, I want to see current gear name and RPM in the 3D scene, so that I have contextual information without leaving the visualization.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL render 3D text using Text component from drei
2. THE Gear_Animation_Tab SHALL display current gear name from activeGear value
3. THE Gear_Animation_Tab SHALL display current RPM from sensors.rpm value
4. THE Gear_Animation_Tab SHALL update 3D text when activeGear or sensors.rpm changes

### Requirement 11: Gear Switching Transitions

**User Story:** As a maintenance operator, I want smooth transitions when switching between gear types, so that the interface feels polished and professional.

#### Acceptance Criteria

1. WHEN activeGear value changes, THE Gear_Animation_Tab SHALL use AnimatePresence to fade-swap gear components
2. WHEN activeGear value changes, THE Gear_Animation_Tab SHALL smoothly transition camera position using useSpring from @react-spring/three
3. THE Gear_Animation_Tab SHALL complete fade transition before rendering new gear type
4. THE Gear_Animation_Tab SHALL maintain scene lighting and environment during transitions

### Requirement 12: Camera Controls

**User Story:** As a maintenance operator, I want to orbit and zoom the camera, so that I can inspect gears from different angles.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL use OrbitControls for camera interaction
2. THE Gear_Animation_Tab SHALL set OrbitControls minDistance to 3 units
3. THE Gear_Animation_Tab SHALL set OrbitControls maxDistance to 12 units
4. THE Gear_Animation_Tab SHALL allow user to rotate camera around gear center point
5. THE Gear_Animation_Tab SHALL allow user to zoom camera within distance constraints

### 13. Component Interface

**User Story:** As a developer, I want a clean component interface, so that the Gear_Animation_Tab integrates easily with the dashboard.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL export GearScene as default React component
2. THE Gear_Animation_Tab SHALL accept no required props
3. THE Gear_Animation_Tab SHALL read all state from Zustand_Store
4. THE Gear_Animation_Tab SHALL use only Three.js r128 compatible APIs
5. THE MainDashboard SHALL render GearScene when activeTab equals '3d-animation'
6. THE MainDashboard tab navigation SHALL include a "3D Gear Animation" tab positioned after "What-If Optimizer"
7. THE tab navigation SHALL use appropriate icon (e.g., 🎨 or 🔮) for the 3D animation tab

### Requirement 14: Gear Geometry Specifications - Spur

**User Story:** As a maintenance operator, I want accurate Spur gear geometry, so that the visualization matches real industrial gears.

#### Acceptance Criteria

1. WHEN rendering Spur_Gear, THE Gear_Animation_Tab SHALL create base disc using CylinderGeometry
2. WHEN rendering Spur_Gear, THE Gear_Animation_Tab SHALL create 16 teeth using BoxGeometry
3. WHEN rendering Spur_Gear, THE Gear_Animation_Tab SHALL arrange teeth radially around disc perimeter
4. WHEN rendering Spur_Gear, THE Gear_Animation_Tab SHALL set rotation axis to Z
5. WHEN rendering Spur_Gear, THE Gear_Animation_Tab SHALL render second gear counter-rotating

### Requirement 15: Gear Geometry Specifications - Helical

**User Story:** As a maintenance operator, I want accurate Helical gear geometry, so that the visualization shows the characteristic twisted teeth.

#### Acceptance Criteria

1. WHEN rendering Helical_Gear, THE Gear_Animation_Tab SHALL create base disc using CylinderGeometry
2. WHEN rendering Helical_Gear, THE Gear_Animation_Tab SHALL create twisted teeth using ExtrudeGeometry along helical path
3. WHEN rendering Helical_Gear, THE Gear_Animation_Tab SHALL set helix angle to 15 degrees
4. WHEN rendering Helical_Gear, THE Gear_Animation_Tab SHALL render two gears with opposite hand helices
5. WHEN rendering Helical_Gear, THE Gear_Animation_Tab SHALL add subtle axial oscillation to simulate thrust

### Requirement 16: Gear Geometry Specifications - Bevel

**User Story:** As a maintenance operator, I want accurate Bevel gear geometry, so that the visualization shows 90-degree axis transmission.

#### Acceptance Criteria

1. WHEN rendering Bevel_Gear, THE Gear_Animation_Tab SHALL create frustum base using ConeGeometry with open top
2. WHEN rendering Bevel_Gear, THE Gear_Animation_Tab SHALL create tapered teeth along slant face
3. WHEN rendering Bevel_Gear, THE Gear_Animation_Tab SHALL position mating gear at 90 degrees on X axis
4. WHEN rendering Bevel_Gear, THE Gear_Animation_Tab SHALL ensure pitch cone apex meets at origin
5. WHEN rendering Bevel_Gear, THE Gear_Animation_Tab SHALL rotate both gears simultaneously at right angles

### Requirement 17: Gear Geometry Specifications - Worm

**User Story:** As a maintenance operator, I want accurate Worm gear geometry, so that the visualization shows the characteristic worm drive mechanism.

#### Acceptance Criteria

1. WHEN rendering Worm_Gear, THE Gear_Animation_Tab SHALL create worm shaft using CylinderGeometry
2. WHEN rendering Worm_Gear, THE Gear_Animation_Tab SHALL create raised spiral ridge using TubeGeometry along helical parametric curve
3. WHEN rendering Worm_Gear, THE Gear_Animation_Tab SHALL create worm wheel as standard spur gear on perpendicular axis
4. WHEN rendering Worm_Gear, THE Gear_Animation_Tab SHALL position worm on Z axis
5. WHEN rendering Worm_Gear, THE Gear_Animation_Tab SHALL position wheel on Y axis
6. WHEN rendering Worm_Gear, THE Gear_Animation_Tab SHALL implement 20:1 rotation ratio where worm drives wheel

### Requirement 18: Performance and Compatibility

**User Story:** As a developer, I want the 3D scene to perform well, so that the dashboard remains responsive.

#### Acceptance Criteria

1. THE Gear_Animation_Tab SHALL use only Three.js r128 compatible APIs
2. THE Gear_Animation_Tab SHALL generate all geometry procedurally without external model files
3. THE Gear_Animation_Tab SHALL optimize mesh merging for teeth geometry
4. THE Gear_Animation_Tab SHALL reuse materials across similar geometry instances
5. THE Gear_Animation_Tab SHALL dispose of geometry and materials when gear type changes
