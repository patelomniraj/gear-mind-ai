# 🪟 GearMind AI - Windows Quick Start

## ⚡ Super Quick Start (3 Steps)

### 1️⃣ Train Worm Model
```cmd
train_worm.bat
```
Wait 2-5 minutes for training to complete.

### 2️⃣ Start API Server
```cmd
start_api.bat
```
Keep this window open!

### 3️⃣ Start Dashboard (New Window)
```cmd
cd dashboard
npm run dev
```
Keep this window open too!

### 4️⃣ Open Browser
```
http://localhost:5173
```

---

## 🧪 Test Everything Works

Run the test script:
```cmd
py test_worm.py
```

Expected output:
```
🧪 Testing GearMind AI - Worm Gear Prediction
============================================================

1️⃣ Testing API connection...
   ✅ API is running!

2️⃣ Testing Worm Gear prediction...
   ✅ Prediction successful!
   
   📊 Results:
   Fault Label:    No Fault
   Confidence:     85.00%
   Health Score:   85/100
   RUL Cycles:     155,139
   Anomaly Status: NORMAL

3️⃣ Testing Model Comparison endpoint...
   ✅ Model comparison retrieved!

4️⃣ Testing Gear Configurations...
   ✅ Gear configurations retrieved!

✅ All tests completed successfully!
```

---

## 📋 What Was Implemented

### ✅ 1. Worm Gear Training
- Logistic Regression model
- 13 sensors (RPM, torque, vibration, temperature, oil analysis, etc.)
- 3-class classification (No Fault, Minor Fault, Major Fault)
- SHAP explainability

### ✅ 2. Model Comparison Enhancement
- Dropdown menu for gear type selection
- Overall comparison across all gears
- Individual gear comparisons
- Enhanced visualizations

### ✅ 3. Notification Icon Removed
- Cleaner header UI
- No unnecessary notification bell

### ✅ 4. Enhanced Reports
- 9 comprehensive sections
- Auto-save to `testing/` folder
- Filename includes today's date
- All actual numbers (no placeholders)

---

## 🎯 Features to Test

### In Dashboard (http://localhost:5173):

1. **Model Comparison Tab**
   - Click "Model Comparison" tab
   - Select "Overall Comparison" from dropdown
   - See statistics for all 4 gear types
   - Try selecting individual gear types

2. **Header**
   - Verify notification icon is removed
   - Cleaner, simpler header

3. **Report Generation**
   - Go to any gear health tab
   - Generate a report
   - Check `testing/` folder for saved report
   - Filename should be: `GearMind_Report_[Type]_[ID]_2026-04-13.txt`

4. **Worm Gear (Future)**
   - Currently backend is ready
   - Frontend integration coming soon

---

## 📁 Important Files

```
gearmind_final/
├── train_worm.bat              ← Run this first
├── start_api.bat               ← Run this second
├── test_worm.py                ← Test script
├── WINDOWS_SETUP.md            ← Detailed Windows guide
├── testing/
│   ├── IMPLEMENTATION_SUMMARY_2026-04-13.md
│   └── GearMind_Report_*.txt   ← Reports save here
└── models/
    ├── train_worm_model.py
    └── worm_*.pkl              ← Generated after training
```

---

## 🐛 Troubleshooting

### "uvicorn is not recognized"
✅ **Fixed!** Use `start_api.bat` or `py -m uvicorn`

### "Cannot connect to API"
1. Make sure API is running: `start_api.bat`
2. Check console for errors
3. Try: http://localhost:8000

### "Model not found"
1. Train the model first: `train_worm.bat`
2. Check `models/` folder for `worm_*.pkl` files

### "Port already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID)
taskkill /PID <PID> /F
```

---

## 📊 System Status

Your system has:
- ✅ Python 3.12.4
- ✅ pip 25.0
- ✅ fastapi 0.116.1
- ✅ uvicorn 0.43.0
- ✅ numpy 2.2.2
- ✅ pandas 2.2.3
- ✅ scikit-learn 1.6.1
- ✅ joblib 1.4.2
- ✅ groq 1.0.0

All dependencies are installed! ✨

---

## 🎓 Learning Resources

- **API Documentation:** `API_DOCUMENTATION.md`
- **Implementation Details:** `testing/IMPLEMENTATION_SUMMARY_2026-04-13.md`
- **Windows Setup:** `WINDOWS_SETUP.md`
- **Quick Start:** `QUICK_START_GUIDE.md`

---

## 🚀 Ready to Start?

1. Open PowerShell in project folder
2. Run: `train_worm.bat`
3. Wait for training to complete
4. Run: `start_api.bat` (keep window open)
5. Open new PowerShell window
6. Run: `cd dashboard && npm run dev` (keep window open)
7. Open browser: http://localhost:5173
8. Test: `py test_worm.py`

**That's it! You're ready to go!** 🎉

---

## 📞 Need Help?

Check these files:
1. `WINDOWS_SETUP.md` - Detailed Windows instructions
2. `API_DOCUMENTATION.md` - API reference
3. `testing/IMPLEMENTATION_SUMMARY_2026-04-13.md` - What was implemented

---

**Made with ❤️ for Elecon Engineering Works**
