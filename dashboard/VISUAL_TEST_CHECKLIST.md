# 3D Gear Animation - Visual Test Checklist

Use this checklist to verify all features are working correctly.

---

## 🎯 Pre-Test Setup

- [ ] Development server running (`npm run dev`)
- [ ] Browser opened to dashboard
- [ ] Console open (F12) to check for errors
- [ ] No console errors on page load

---

## 🔧 Gear Type Tests

### Spur Gear
- [ ] Two flat gears visible
- [ ] 16 teeth on each gear
- [ ] Gears counter-rotate
- [ ] Teeth mesh properly (no overlap)
- [ ] Metallic blue-gray color (#8a9bb0)
- [ ] Shadows cast on floor
- [ ] Smooth rotation (no stuttering)

### Helical Gear
- [ ] Two gears with twisted teeth visible
- [ ] Teeth have helical twist (15° angle)
- [ ] Opposite hand helices (one left, one right)
- [ ] Axial oscillation visible (up/down motion)
- [ ] Counter-rotation
- [ ] Teeth mesh properly
- [ ] Shadows cast correctly

### Bevel Gear
- [ ] Two conical gears visible
- [ ] Gears positioned at 90° angle
- [ ] Tapered teeth along slant face
- [ ] One gear rotates on Z-axis
- [ ] Other gear rotates on X-axis
- [ ] Pitch cone apex meets at origin
- [ ] Simultaneous rotation

### Worm Gear
- [ ] Worm shaft visible (horizontal)
- [ ] Helical thread visible on shaft
- [ ] Worm wheel visible (vertical)
- [ ] 40 teeth on wheel
- [ ] Worm rotates fast
- [ ] Wheel rotates slow (20:1 ratio)
- [ ] Perpendicular axes (90° angle)

---

## 🏭 Factory Environment Tests

### Floor
- [ ] 40x40 plane visible
- [ ] Checker pattern texture (#1a2030 / #141824)
- [ ] Grid overlay visible
- [ ] Receives shadows from gears
- [ ] No texture stretching or distortion

### Walls
- [ ] Back wall visible (behind gears)
- [ ] Left wall visible (left side)
- [ ] Dark blue-gray color (#1c2333)
- [ ] Receives shadows
- [ ] No gaps or holes

### Structural Elements
- [ ] Four I-beam columns at corners
- [ ] Columns are tall (12 units)
- [ ] Dark metallic color (#2a3550)
- [ ] Two horizontal beams connecting columns
- [ ] Cast shadows

### Atmospheric Particles
- [ ] 200 small points visible
- [ ] Particles drift upward slowly
- [ ] Particles reset when reaching top
- [ ] Semi-transparent appearance
- [ ] Blue-gray color (#6b7a99)

---

## 💡 Lighting Tests

### Ambient Light
- [ ] Base illumination present (0.3 intensity)
- [ ] No completely black areas
- [ ] Soft overall lighting

### Key SpotLight (Warm)
- [ ] Warm orange-yellow color (#ffd4a3)
- [ ] Positioned above and to the right
- [ ] Casts shadows
- [ ] Intensity changes with load sensor
- [ ] Shadow map quality good (2048x2048)

### Fill SpotLights (Cool)
- [ ] Two cool blue lights visible
- [ ] One from left side (#a3c4ff)
- [ ] One from right side (#c4d4ff)
- [ ] Softer than key light
- [ ] No harsh shadows

### Temperature PointLight
- [ ] Positioned near gears
- [ ] Color changes with temperature
- [ ] Orange at 65°C (#ff6b35)
- [ ] Red at 95°C (#ff2200)
- [ ] Smooth color transition
- [ ] Intensity changes with health status

### Environment Map
- [ ] Warehouse preset loaded
- [ ] Reflections on metallic surfaces
- [ ] Enhances realism
- [ ] No performance issues

---

## 🎮 Interaction Tests

### Gear Switching
- [ ] Four buttons visible at top-left
- [ ] Buttons labeled correctly
- [ ] Active button highlighted
- [ ] Click switches gear type
- [ ] Fade transition smooth (300ms)
- [ ] No flashing or glitches
- [ ] Previous gear disappears completely
- [ ] New gear appears smoothly

### Camera Controls (OrbitControls)
- [ ] **Rotate**: Left mouse drag works
- [ ] Rotation smooth and responsive
- [ ] **Pan**: Right mouse drag works
- [ ] Pan moves camera position
- [ ] **Zoom**: Mouse wheel works
- [ ] Zoom limited to 3-12 units
- [ ] Damping enabled (smooth deceleration)
- [ ] No camera clipping through objects

### HUD Display
- [ ] 3D text visible above gears
- [ ] Gear name displays correctly
- [ ] RPM value displays correctly
- [ ] Health indicator sphere visible
- [ ] Text always faces camera (billboard)
- [ ] Text readable from all angles
- [ ] Health sphere color matches status:
  - [ ] Green for normal (#22c55e)
  - [ ] Amber for warning (#f59e0b)
  - [ ] Red for critical (#ef4444)

---

## 📊 Sensor Integration Tests

### RPM Sensor
- [ ] Gears rotate faster with higher RPM
- [ ] Gears rotate slower with lower RPM
- [ ] HUD displays correct RPM value
- [ ] Rotation speed smooth (no jumps)
- [ ] Default RPM is 1200

### Temperature Sensor
- [ ] PointLight color changes with temperature
- [ ] Orange at low temperature (65°C)
- [ ] Red at high temperature (95°C)
- [ ] Smooth color transition
- [ ] Default temperature is 72°C

### Vibration Sensor
- [ ] Gears shake on X-axis with vibration
- [ ] Higher vibration = more shake
- [ ] Shake follows sin wave pattern
- [ ] Frequency is 10 Hz
- [ ] Default vibration is 2.3

### Load Sensor
- [ ] SpotLight intensity changes with load
- [ ] Brighter at high load (100%)
- [ ] Dimmer at low load (0%)
- [ ] Smooth intensity transition
- [ ] Default load is 48%

### Health Status
- [ ] **Normal**: Standard lighting, 1x vibration
- [ ] **Warning**: Amber blinking light, 1.5x vibration
- [ ] **Critical**: Red light, 3x vibration, faster spin
- [ ] Health indicator sphere color matches status
- [ ] Transitions smooth between states

---

## 🔄 State Management Tests

### Zustand Store
- [ ] Store initializes correctly
- [ ] Default values set properly
- [ ] `setActiveGear()` updates gear type
- [ ] `setSensors()` updates sensor values
- [ ] `updateSensor()` updates single sensor
- [ ] Store persists across page navigation
- [ ] No console errors from store

### ML Dashboard Integration
- [ ] `syncSensorData()` utility works
- [ ] Sensor data syncs from ML dashboard
- [ ] Gear type syncs from ML dashboard
- [ ] Health status calculated correctly
- [ ] No data loss during sync
- [ ] Real-time updates work

---

## 🎨 Visual Quality Tests

### Materials
- [ ] Metallic appearance (#8a9bb0)
- [ ] Metalness value 0.85
- [ ] Roughness value 0.25
- [ ] Reflections visible
- [ ] No texture artifacts
- [ ] Consistent across all gears

### Shadows
- [ ] Gears cast shadows on floor
- [ ] Shadows cast on walls
- [ ] Shadow edges soft (penumbra)
- [ ] No shadow acne or artifacts
- [ ] Shadow map resolution good
- [ ] Shadows update with rotation

### Anti-aliasing
- [ ] No jagged edges on gears
- [ ] Smooth curves on cylinders
- [ ] Clean text rendering
- [ ] No flickering

---

## ⚡ Performance Tests

### Frame Rate
- [ ] 60 FPS maintained
- [ ] No frame drops during rotation
- [ ] No frame drops during gear switching
- [ ] No frame drops during camera movement
- [ ] Smooth animations throughout

### Memory Usage
- [ ] No memory leaks
- [ ] Memory usage stable over time
- [ ] No console warnings about memory
- [ ] Browser doesn't slow down

### Loading Time
- [ ] Page loads quickly (< 3 seconds)
- [ ] Gears appear immediately
- [ ] No long loading screens
- [ ] Smooth initial render

---

## 🌐 Browser Compatibility Tests

### Chrome
- [ ] All features work
- [ ] No console errors
- [ ] Performance good

### Firefox
- [ ] All features work
- [ ] No console errors
- [ ] Performance good

### Safari
- [ ] All features work
- [ ] No console errors
- [ ] Performance good

### Edge
- [ ] All features work
- [ ] No console errors
- [ ] Performance good

---

## 📱 Responsive Design Tests

### Desktop (1920x1080)
- [ ] Layout correct
- [ ] All elements visible
- [ ] No overflow

### Laptop (1366x768)
- [ ] Layout correct
- [ ] All elements visible
- [ ] No overflow

### Tablet (768x1024)
- [ ] Layout adapts
- [ ] Touch controls work
- [ ] Readable text

---

## 🐛 Error Handling Tests

### Invalid Sensor Values
- [ ] Handles negative RPM gracefully
- [ ] Handles extreme temperature values
- [ ] Handles NaN values
- [ ] Defaults to safe values

### Missing Store Data
- [ ] Handles undefined sensors
- [ ] Handles null values
- [ ] No crashes

### Network Issues
- [ ] Handles failed store updates
- [ ] No data corruption
- [ ] Graceful degradation

---

## ✅ Final Verification

### Documentation
- [ ] README files present
- [ ] Integration guide available
- [ ] Quick start guide available
- [ ] Architecture diagram available

### Code Quality
- [ ] No console errors
- [ ] No console warnings
- [ ] JSDoc comments present
- [ ] Code formatted consistently

### User Experience
- [ ] Intuitive controls
- [ ] Smooth interactions
- [ ] Clear visual feedback
- [ ] Professional appearance

---

## 📝 Test Results

**Date**: _______________  
**Tester**: _______________  
**Browser**: _______________  
**OS**: _______________

**Overall Status**: ⬜ Pass | ⬜ Fail

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🎉 Sign-off

- [ ] All critical tests passed
- [ ] No blocking issues found
- [ ] Performance acceptable
- [ ] Ready for production

**Approved by**: _______________  
**Date**: _______________

---

**Use this checklist to ensure the 3D Gear Animation system is fully functional before deployment.**
