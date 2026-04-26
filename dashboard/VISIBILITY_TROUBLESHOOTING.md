# 3D Animation Not Visible - Troubleshooting

## Current Status
- ✅ Server running at http://localhost:5173/
- ✅ No syntax errors in code
- ✅ Helical gear geometry updated with proper helix twist
- ✅ Material updated to balanced brightness

## Possible Issues & Solutions

### Issue 1: Browser Cache (Most Likely)
**Solution:** Hard refresh the browser
- Windows: `Ctrl + Shift + R` or `Ctrl + F5`
- Mac: `Cmd + Shift + R`
- Or: Open DevTools (F12) → Right-click refresh → "Empty Cache and Hard Reload"

### Issue 2: Material Too Dark
**Current Material:**
```javascript
color: '#9aa5b0'           // Lighter gray (was #7a8590)
metalness: 0.85
roughness: 0.3
emissive: '#3a4550'
emissiveIntensity: 0.2
```

**If still too dark, we can:**
1. Increase color brightness to `#b0bac5`
2. Increase emissive intensity to 0.3
3. Decrease roughness to 0.2 for more reflection

### Issue 3: Geometry Error
The new helical tooth geometry might have issues. 

**Fallback:** Revert to simple box-based teeth:
```javascript
export function createHelicalTooth(helixAngle, height) {
  const tooth = new THREE.BoxGeometry(0.3, 0.6, height);
  const positions = tooth.attributes.position;
  const angleRad = (helixAngle * Math.PI) / 180;
  
  for (let i = 0; i < positions.count; i++) {
    const z = positions.getZ(i);
    const twist = (z / height) * angleRad;
    const x = positions.getX(i);
    const y = positions.getY(i);
    
    const newX = x * Math.cos(twist) - y * Math.sin(twist);
    const newY = x * Math.sin(twist) + y * Math.cos(twist);
    
    positions.setX(i, newX);
    positions.setY(i, newY);
  }
  
  positions.needsUpdate = true;
  tooth.computeVertexNormals();
  return tooth;
}
```

### Issue 4: Camera Position
The camera might be looking at the wrong position.

**Check:** In `GearScene.jsx`, camera should target `[0, 2, 0]` and Helical camera position should be `[6, 4, 4]`

### Issue 5: React Error Boundary
If there's a runtime error, the ErrorBoundary might be catching it.

**Check:** Look for error message on the page or in browser console (F12)

## Quick Test Steps

1. **Open browser console** (F12)
2. **Go to** http://localhost:5173/
3. **Click** 3D Animation tab
4. **Check console** for any errors
5. **Look for:**
   - Red error messages
   - "THREE" related errors
   - Geometry errors
   - Material errors

## What to Report

If still not visible, please check:
1. Is the page completely blank or just the 3D area?
2. Are there any error messages in browser console?
3. Does the error boundary show "Something went wrong"?
4. Do other tabs (Gear Health, SHAP+LIME) work?
5. Do other gear types (Spur, Bevel, Worm) show in 3D tab?

## Emergency Rollback

If nothing works, I can rollback to the previous working version with:
- Simple box teeth (no complex geometry)
- Bright material (#c0c8d0)
- Original lighting settings

Just let me know what you see and I'll fix it immediately.
