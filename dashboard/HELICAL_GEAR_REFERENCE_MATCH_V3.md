# Helical Gear - Reference Image Match (Version 3.0)

## Changes Made to Match Reference Image

### 1. Tooth Geometry (`gearGeometry.js`)
**NEW: Proper helical tooth with involute profile**
- Created custom geometry with 16 segments along helix for smooth twist
- Tapered tooth profile (wider at base, narrower at tip) - matches involute shape
- Proper helix twist applied progressively along tooth length
- Tooth dimensions:
  - Width at base: 0.25 units
  - Radial height: 0.5 units
  - Taper ratio: base width → 2/3 width at tip

### 2. Gear Structure (`HelicalGearPair.jsx`)
**Matching reference image proportions:**
- **Hub**: 1.5 radius, 1.0 height - prominent central body
- **Rim**: 2.0 radius, 0.8 height - thick outer ring where teeth attach
- **Bore hole**: 0.6 radius - visible central hole
- **Teeth count**: 24 teeth (realistic for this size)
- **Helix angle**: 25° (increased from 20° for more visible twist)

### 3. Material (`sharedMaterials.js`)
**Medium-dark gray steel with machined finish:**
```javascript
color: '#7a8590'              // Medium-dark gray (matching reference)
metalness: 0.88               // High metallic appearance
roughness: 0.35               // Smooth machined finish (not mirror)
emissive: '#2a3038'           // Subtle dark glow
emissiveIntensity: 0.15       // Low intensity for realism
```

### 4. Meshing Behavior
- Opposite helix angles: +25° and -25°
- Counter-rotation for proper meshing
- Half-tooth offset for engagement: 15° (360°/24 teeth / 2)
- Proper spacing: 4.5 units apart

## Reference Image Characteristics

Based on the reference you provided, the helical gear should have:
- ✅ Medium-dark gray steel color (#7a8590)
- ✅ Smooth machined finish (roughness 0.35)
- ✅ Central bore hole clearly visible
- ✅ Prominent hub structure
- ✅ Thick rim supporting teeth
- ✅ Helical teeth with visible twist along length
- ✅ Tapered tooth profile (involute-like)
- ✅ Realistic proportions and tooth count

## Key Improvements from Previous Version

### Tooth Geometry:
- **Before**: Simple box with basic twist
- **After**: Custom geometry with 16 segments, proper taper, smooth helix

### Proportions:
- **Before**: Hub 1.8, Rim 2.2, 32 teeth
- **After**: Hub 1.5, Rim 2.0, 24 teeth (more realistic)

### Material:
- **Before**: Very bright light gray (#c0c8d0) for visibility
- **After**: Medium-dark gray (#7a8590) matching reference

### Helix Angle:
- **Before**: 20°
- **After**: 25° (more pronounced twist)

## Expected Visual Result

The helical gears should now show:
1. **Realistic steel color** - medium-dark gray, not too bright
2. **Visible helix twist** - teeth clearly spiral along the gear width
3. **Smooth tooth surfaces** - proper involute-like taper
4. **Prominent hub** - central body clearly visible
5. **Central bore hole** - dark hole in the center
6. **Proper meshing** - teeth engage correctly as gears rotate
7. **Machined finish** - metallic but not mirror-like

## Testing

After hard refresh (`Ctrl+Shift+R`):
1. Go to 3D Animation tab
2. Select Helical gear type
3. Observe:
   - Gear color should be medium-dark gray steel
   - Teeth should show clear helical twist
   - Hub and bore hole should be prominent
   - Gears should mesh smoothly as they rotate
   - Overall appearance should match your reference image

## If Still Not Matching

Please specify which aspects don't match:
- Color too light/dark?
- Teeth shape incorrect?
- Hub proportions wrong?
- Helix angle too steep/shallow?
- Material finish too shiny/matte?

I can fine-tune any of these parameters to exactly match your reference.
