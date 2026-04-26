# ⚠️ RESTART API SERVER NOW

## Critical: API Server Must Be Restarted

The worm gear slider fix requires restarting the API server because we modified the Pydantic model (`SensorInput`). Python needs to reload the module for changes to take effect.

## How to Restart

### Step 1: Stop Current API Server
In the terminal running the API server, press:
```
Ctrl + C
```

### Step 2: Restart API Server
```bash
py -m uvicorn gear_api:app --reload --port 8000
```

### Step 3: Wait for Startup
You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✅ Helical model loaded
✅ Spur model loaded
✅ Bevel model loaded
✅ Worm model loaded
```

### Step 4: Test Worm Gear
1. Go to dashboard: http://localhost:5173
2. Click "🌀 Worm" button
3. Move any slider (e.g., Oil Temperature from 56 to 80)
4. **Watch the health gauge** - it should update immediately!
5. Fault label, RUL, and confidence should also change

## What Was Fixed

**Before**: Worm gear sliders didn't work because the API was ignoring worm gear fields (rpm, in_torque, oil_temp, etc.)

**After**: API now accepts all 13 worm gear fields and processes them correctly

## If Sliders Still Don't Work

1. Check browser console (F12) for errors
2. Check API terminal for errors
3. Verify the API restarted successfully
4. Try hard refresh in browser (Ctrl + Shift + R)

---

**DO THIS NOW**: Restart the API server, then test worm gear sliders!
