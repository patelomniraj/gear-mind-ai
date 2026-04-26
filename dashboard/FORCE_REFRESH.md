# FORCE BROWSER REFRESH - CRITICAL STEPS

## The Problem
Browser is caching old JavaScript files, so changes to materials and lighting aren't visible.

## SOLUTION - Follow These Steps EXACTLY:

### Step 1: Stop the Dev Server
Press `Ctrl+C` in the terminal running `npm run dev`

### Step 2: Clear Vite Cache
```bash
cd dashboard
rm -rf node_modules/.vite
rm -rf dist
```

### Step 3: Restart Dev Server
```bash
npm run dev
```

### Step 4: Hard Refresh Browser
When the page loads, do a HARD REFRESH:

**Windows/Linux:**
- Chrome/Edge: `Ctrl + Shift + R` or `Ctrl + F5`
- Firefox: `Ctrl + Shift + R`

**Mac:**
- Chrome/Edge: `Cmd + Shift + R`
- Firefox: `Cmd + Shift + R`

### Step 5: Clear Browser Cache (If Still Not Working)
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

OR

1. Open DevTools (F12)
2. Go to Application tab
3. Click "Clear storage"
4. Click "Clear site data"
5. Refresh page

## What Changed (Version 2.0):

### Materials (sharedMaterials.js):
- Color: `#c0c8d0` (very bright light gray)
- Metalness: 0.9 (highly reflective)
- Roughness: 0.15 (very shiny)
- Emissive: `#4a5560` with intensity 0.3 (self-illuminating)

### Lighting (SceneLighting.jsx):
- Ambient: 2.5 intensity (was 1.5)
- Key spotlight: 6.0 intensity (was 4.0)
- Fill spotlights: 5.0 intensity (was 3.0)
- Front spotlight: 5.5 intensity (was 3.5)
- Directional: 3.5 intensity (was 2.0)
- Point lights: 3.5 and 2.0 intensity
- Hemisphere: 3.0 intensity (was 2.0)
- Added 2 rim lights for edge definition

### Scene (GearScene.jsx):
- Background: `#f5f7fa` (very light gray, almost white)
- Tone mapping exposure: 2.0 (was 1.5)

## Expected Result:
- Scene should be VERY BRIGHT - almost like a photo studio
- Gears should be clearly visible with bright light gray color
- Gears should have metallic shine and slight glow
- Background should be light, not dark

## If STILL Not Working:
Try opening in Incognito/Private browsing mode - this guarantees no cache.
