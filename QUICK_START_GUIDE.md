# GearMind AI - Quick Start Guide

## 🚀 Getting Started

### Step 1: Train the Worm Gear Model

```bash
cd models
python train_worm_model.py
```

**Expected Output:**
```
🌀 Worm Gear Logistic Regression Training Starting...
============================================================
   Dataset: 50000 rows x 16 columns
   Classes: ['Major Fault' 'Minor Fault' 'No Fault']
   ...
   Results:
   Accuracy : 0.8XXX
   F1 Score : 0.8XXX
   AUC      : 0.9XXX
   ...
✅ Worm Gear Logistic Regression Training Complete!
```

### Step 2: Start the API Server

```bash
uvicorn gear_api:app --reload --port 8000
```

**Expected Output:**
```
⚙️  Loading ML models...
   ✅ Helical models loaded
   ✅ Helical XAI loaded
   ✅ Spur SVM models loaded
   ✅ Spur XAI loaded
   ✅ Bevel models loaded
   ✅ Bevel XAI loaded
   ✅ Worm models loaded
   ✅ Worm XAI loaded
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start the Dashboard

```bash
cd dashboard
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 4: Access the Dashboard

Open your browser and navigate to: `http://localhost:5173`

---

## 🧪 Testing the New Features

### 1. Test Worm Gear Prediction

**Using Python:**
```python
import requests

# Worm gear sensor data
payload = {
    "gear_type": "Worm",
    "load": 1321.0,      # Worm_RPM
    "torque": 86.8,      # Input_Torque
    "vib": 5.2,          # Axial_Vib
    "temp": 56.5,        # Oil_Temp
    "wear": 2.3,         # Radial_Vib
    "lube": 0.85,        # Efficiency_Calc (normalized)
    "eff": 85.0,         # Efficiency_Calc
    "cycles": 155139     # RUL_Cycles
}

response = requests.post(
    "http://localhost:8000/api/predict",
    json=payload
)

print(response.json())
```

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "gear_type": "Worm",
    "load": 1321.0,
    "torque": 86.8,
    "vib": 5.2,
    "temp": 56.5,
    "wear": 2.3,
    "lube": 0.85,
    "eff": 85.0,
    "cycles": 155139
  }'
```

### 2. Test Model Comparison API

```bash
# Get overall comparison
curl http://localhost:8000/api/models/comparison
```

**Expected Response:**
```json
{
  "gear_types": {
    "Helical": { ... },
    "Spur": { ... },
    "Bevel": { ... },
    "Worm": { ... }
  },
  "overall": {
    "total_gear_types": 4,
    "total_models": 8,
    "avg_accuracy": 0.92,
    "avg_f1": 0.91,
    "avg_auc": 0.95,
    "best_accuracy": 0.99,
    "best_f1": 0.98,
    "best_auc": 0.99
  }
}
```

### 3. Test Enhanced Report Generation

```python
import requests
from datetime import datetime

response = requests.post(
    "http://localhost:8000/api/report",
    json={
        "gear_id": "WG-01",
        "gear_type": "Worm",
        "sensor_values": {
            "Worm_RPM": 1321.0,
            "Input_Torque": 86.8,
            "Output_Torque": 2951.0,
            "Motor_Current": 26.0,
            "Oil_Temp": 56.5,
            "Ambient_Temp": 24.6,
            "Axial_Vib": 5.2,
            "Radial_Vib": 2.3,
            "Cu_PPM": 25.0,
            "Fe_PPM": 9.0,
            "Efficiency_Calc": 0.85,
            "Friction_Coeff": 0.031,
            "Backlash": 0.115
        }
    }
)

result = response.json()
print(f"Report saved to: {result['saved_to']}")
print(f"\nReport preview:\n{result['report'][:500]}...")
```

**Check the saved report:**
```bash
cat testing/GearMind_Report_Worm_WG-01_2026-04-13.txt
```

### 4. Test Dashboard Features

1. **Open Dashboard:** `http://localhost:5173`
2. **Login:** Use any credentials (demo mode)
3. **Navigate to Model Comparison Tab**
4. **Select Dropdown:** Choose "Overall Comparison (All Gears)"
5. **Verify:** You should see:
   - Overall statistics card with purple gradient
   - Top 10 models across all gear types
   - Comparison chart with all models
6. **Switch Gear Types:** Try selecting Helical, Spur, Bevel, Worm
7. **Verify Notification Icon:** Should be removed from header

---

## 📊 Verify All Features

### ✅ Checklist

- [ ] Worm gear model trained successfully
- [ ] API server starts without errors
- [ ] Dashboard loads without errors
- [ ] Worm gear predictions work via API
- [ ] Model comparison dropdown appears
- [ ] Overall comparison shows statistics
- [ ] Individual gear comparisons work
- [ ] Notification icon is removed from header
- [ ] Report generation creates detailed reports
- [ ] Reports save to testing folder with today's date
- [ ] Report contains actual numbers (no placeholders)

---

## 🐛 Troubleshooting

### Issue: Worm model not loading

**Solution:**
```bash
# Make sure you trained the model first
cd models
python train_worm_model.py

# Check if files exist
ls -la models/worm_*.pkl
ls -la xai/worm_shap_artifacts.pkl
```

### Issue: API returns 503 for worm gear

**Solution:**
```bash
# Check API logs for error messages
# Restart API server
uvicorn gear_api:app --reload --port 8000
```

### Issue: Dashboard doesn't show dropdown

**Solution:**
```bash
# Clear browser cache
# Restart dashboard
cd dashboard
npm run dev
```

### Issue: Reports not saving

**Solution:**
```bash
# Create testing folder if it doesn't exist
mkdir -p testing

# Check permissions
ls -la testing/
```

---

## 📁 File Structure

```
.
├── models/
│   ├── train_worm_model.py          # NEW: Worm gear training script
│   ├── worm_classifier.pkl          # NEW: Worm LR model
│   ├── worm_scaler.pkl              # NEW: Worm scaler
│   ├── worm_label_encoder.pkl       # NEW: Worm label encoder
│   ├── worm_rul_regressor.pkl       # NEW: Worm RUL model
│   ├── worm_scaler_rul.pkl          # NEW: Worm RUL scaler
│   └── worm_model_comparison.json   # NEW: Worm comparison
├── xai/
│   └── worm_shap_artifacts.pkl      # NEW: Worm SHAP data
├── testing/
│   ├── IMPLEMENTATION_SUMMARY_2026-04-13.md  # NEW: Summary
│   └── GearMind_Report_*.txt        # NEW: Auto-saved reports
├── gear_api.py                      # MODIFIED: Added worm support
├── copilot/llm_copilot.py          # MODIFIED: Enhanced reports
├── dashboard/
│   ├── src/
│   │   ├── App.jsx                 # MODIFIED: Removed notification
│   │   └── components/
│   │       └── DashboardComponents.jsx  # MODIFIED: Enhanced comparison
│   └── ...
└── QUICK_START_GUIDE.md            # NEW: This file
```

---

## 🎯 Next Steps

1. **Train the Model:** Run `python models/train_worm_model.py`
2. **Start Services:** API + Dashboard
3. **Test Features:** Follow testing section above
4. **Generate Reports:** Test report generation with different gear types
5. **Explore Dashboard:** Try all tabs and features

---

## 💡 Tips

- **Model Training:** Takes 2-5 minutes depending on your machine
- **API Startup:** Should load all 4 gear types (Helical, Spur, Bevel, Worm)
- **Dashboard:** Use Chrome/Edge for best experience
- **Reports:** Check `testing/` folder for saved reports
- **Logs:** Watch API console for prediction logs

---

## 📞 Need Help?

If you encounter any issues:

1. Check the console logs (API and Dashboard)
2. Verify all dependencies are installed
3. Ensure all model files exist
4. Check file permissions
5. Review the implementation summary in `testing/IMPLEMENTATION_SUMMARY_2026-04-13.md`

---

**Happy Testing! 🚀**
