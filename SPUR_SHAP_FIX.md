# Spur Gear SHAP Fix - COMPLETE

## Problem
SHAP analysis was showing "unavailable" for Spur gear with the message:
> "Spur gear SHAP artifacts may not be loaded. Check backend console for SHAP loading status."

## Root Cause
The spur gear model uses an SVM classifier with `LinearExplainer` for SHAP analysis. The code was calling:
```python
sv = explainer.shap_values(input_scaled, nsamples=50)
```

However, `LinearExplainer.shap_values()` **does not accept** the `nsamples` parameter - that's only for `KernelExplainer`. This caused the SHAP computation to fail with:
```
LinearExplainer.shap_values() got an unexpected keyword argument 'nsamples'
```

## The Fix

**File**: `gear_api.py` - `predict_spur()` function

Added explainer type detection before calling `shap_values()`:

```python
# LinearExplainer doesn't accept nsamples parameter
explainer_type = type(explainer).__name__
if 'Linear' in explainer_type:
    sv = explainer.shap_values(input_scaled)  # No nsamples
else:
    sv = explainer.shap_values(input_scaled, nsamples=50)  # With nsamples
```

## How It Works Now

1. **Spur gear prediction** is requested
2. **SHAP computation** starts
3. **Explainer type** is checked:
   - If `LinearExplainer` → call without `nsamples`
   - If `KernelExplainer` or other → call with `nsamples=50`
4. **SHAP values** are computed successfully
5. **Dashboard displays** SHAP analysis with feature importance

## Test the Fix

**IMPORTANT**: You must restart the API server for the fix to take effect!

```bash
# Stop the API server (Ctrl+C)
# Then restart:
py -m uvicorn gear_api:app --reload --port 8000
```

After restarting:

1. Open dashboard: http://localhost:5173
2. Click **Spur gear** button
3. Go to **SHAP + LIME** tab
4. **Expected**: SHAP chart should display with 6 features:
   - Speed_RPM
   - Torque_Nm
   - Vibration_mm_s
   - Temperature_C
   - Shock_Load_g
   - Noise_dB

## What You Should See

### Before Fix:
```
📊 SHAP Analysis Unavailable
Spur gear SHAP artifacts may not be loaded.
Check backend console for SHAP loading status.
```

### After Fix:
- ✅ SHAP bar chart showing feature contributions
- ✅ Red bars (increase fault risk) and green bars (decrease fault risk)
- ✅ Feature importance values displayed
- ✅ Explanation text below the chart

## API Console Output

When you make a spur gear prediction, you should see:
```
🔍 Computing SHAP for Spur gear...
   Explainer type: <class 'shap.explainers._linear.Linear'>
   Input shape: (1, 6)
   SHAP output type: <class 'list'>
   SHAP is list with 3 elements
   SHAP values shape: (6,)
   ✅ SHAP computed: 6 features
```

## Why This Matters

SHAP (SHapley Additive exPlanations) provides explainability by showing:
- Which sensor readings contribute most to the fault prediction
- Whether each feature increases or decreases fault risk
- The magnitude of each feature's impact

This is critical for:
- Understanding why the AI predicted a fault
- Identifying which parameters to focus on during maintenance
- Building trust in the AI's decisions

## Files Modified

1. ✅ `gear_api.py` - Fixed `predict_spur()` SHAP computation

## Verification

Run the check script to verify:
```bash
py check_shap_artifacts.py
```

Expected output:
```
2️⃣ Spur Gear SHAP
──────────────────────────────────────────────────
✅ File loaded successfully
✅ Explainer found
✅ SHAP computation works
```

---

**Status**: FIX COMPLETE - RESTART API SERVER TO TEST

**Critical**: Must restart API server for Python code changes to take effect!
