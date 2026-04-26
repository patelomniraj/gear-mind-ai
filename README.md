# 🎯 GearMind AI Dashboard

**Predictive Maintenance System for Industrial Gears**  
Multi-Model Architecture | Explainable AI | Real-Time Monitoring

---

## 🌟 Overview

GearMind is a comprehensive predictive maintenance dashboard that monitors the health of industrial gears using machine learning. It supports three gear types (Helical, Spur, Bevel) with dedicated models, provides explainable AI insights, generates professional PDF reports, and includes an AI-powered copilot assistant.

---

## ✨ Key Features

### 🤖 Multi-Model Prediction
- **Helical Gear:** XGBoost classifier (8 features)
- **Spur Gear:** SVM classifier (6 features)
- **Bevel Gear:** XGBoost classifier (8 features)
- Automatic model routing based on gear type
- Real-time predictions with debounced updates

### 🔍 Explainable AI (XAI)
- **SHAP:** Game theory-based feature attribution
- **LIME:** Local interpretable model-agnostic explanations
- Educational banners explaining both methods
- Feature impact cards with color-coded directions
- Available for all 3 gear types

### 📊 Remaining Useful Life (RUL)
- Dedicated RUL regressors for each gear type
- Visual progress bar with gradient colors
- Displays: Cycles, Days, Shifts, Hours remaining
- Urgency indicators (CRITICAL/CAUTION/NORMAL)

### 📄 PDF Report Generation
- Client-side generation (no server dependency)
- Comprehensive report with all key metrics
- Includes: Gear info, sensor readings, fault assessment, SHAP analysis, RUL, cost impact
- Professional formatting with tables and color-coded sections
- Operator metadata in header

### 🤖 AI Copilot Assistant
- Powered by LLaMA 3.3 70B (via Groq API)
- Context-aware responses based on current gear state
- Floating widget persists across all tabs
- Quick suggestions for common questions
- Chat history maintained during session

### 📈 History & Trends
- Auto-logs every prediction with operator metadata
- Sensor trend charts (Health Score, Vibration, Temperature)
- Risk distribution pie chart
- Full operation log with search/filter
- Operator name, shift, and role tracking

### 🔧 What-If Optimizer
- Differential Evolution algorithm
- Lock parameters you can't change
- Find safe operating points
- Before/after comparison with recommended changes

### 💰 Cost Impact Analysis
- Preventive vs. Delayed vs. Failure scenarios
- Total savings calculator
- Downtime and production impact
- Visual cost comparison charts

---

## 🏗️ Architecture

### Backend (FastAPI)
```
gear_api.py (951 lines)
├── Multi-model loading (Helical, Spur, Bevel)
├── 16 API endpoints
├── SHAP/LIME integration
├── SQLite database with operator tracking
└── AI Copilot integration (Groq API)
```

### Frontend (React + Vite)
```
dashboard/
├── src/
│   ├── pages/
│   │   └── MainDashboard.jsx          # Main dashboard with 6 tabs
│   ├── components/
│   │   ├── DashboardComponents.jsx    # Core components
│   │   └── NewComponents.jsx          # LIME, RUL, PDF, Copilot
│   ├── api/
│   │   └── gearApi.js                 # API client
│   └── index.css                      # Enhanced styles
└── package.json                       # jsPDF + dependencies
```

### Models & Data
```
models/
├── best_classifier.pkl                # Helical XGBoost
├── spur_svm_classifier.pkl            # Spur SVM
├── bevel_classifier.pkl               # Bevel XGBoost
├── *_rul_regressor.pkl                # RUL models (all 3)
├── *_scaler.pkl                       # Scalers (all 3)
└── *_label_encoder.pkl                # Label encoders (all 3)

xai/
├── shap_artifacts.pkl                 # Helical SHAP
├── spur_shap_artifacts.pkl            # Spur SHAP
└── bevel_shap_artifacts.pkl           # Bevel SHAP

data/
├── helical_gear_dataset.csv           # Helical training data
├── spur_gear_svm_dataset.csv          # Spur training data
└── bevel_gear_dataset.csv             # Bevel training data
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (3.12.4 tested)
- Node.js 18+ (for npm)
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable)
```bash
cd gearmind_final
```

2. **Install Python dependencies**
```bash
pip install fastapi uvicorn numpy pandas joblib scikit-learn xgboost shap lime
```

3. **Install Node.js dependencies**
```bash
cd dashboard
npm install
cd ..
```

### Running the Application

1. **Start Backend Server**
```bash
py gear_api.py
```
Expected output:
```
⚙️  Loading ML models...
   ✅ Helical models loaded
   ✅ Spur SVM models loaded
   ✅ Bevel models loaded
INFO:     Uvicorn running on http://0.0.0.0:8000
```

2. **Start Frontend Dev Server** (new terminal)
```bash
cd dashboard
npm run dev
```
Expected output:
```
➜  Local:   http://localhost:5173/
```

3. **Open Dashboard**
```
http://localhost:5173
```

---

## 📱 Dashboard Tabs

### 1. 🎯 Gear Health
- Real-time health gauge (0-100)
- Fault countdown timer
- Sensor status indicators
- RUL section with progress bar
- PDF report generation button

### 2. 🔍 SHAP + LIME
- Educational banners
- SHAP feature importance chart
- LIME local explanations chart
- Feature impact cards

### 3. 📈 Trends & History
- KPI summary cards
- Health score trend chart
- Sensor trend charts
- Risk distribution pie chart
- Full operation log table

### 4. 🔧 What-If Optimizer
- Target probability slider
- Parameter lock toggles
- Optimization results
- Before/after comparison

### 5. 💰 Cost Impact
- Cost scenario cards
- Savings calculator
- Cost comparison chart
- Downtime analysis

### 6. 📊 Model Comparison
- 5-model performance table
- Metrics comparison chart
- Best model highlighted

### 🤖 AI Copilot (All Tabs)
- Floating button in bottom-right
- Chat panel with quick suggestions
- Context-aware responses
- Powered by LLaMA 3.3 70B

---

## 🎓 Technology Stack

### Backend
- **Framework:** FastAPI
- **ML Models:** XGBoost, SVM (scikit-learn)
- **XAI:** SHAP, LIME
- **Database:** SQLite
- **AI:** Groq API (LLaMA 3.3 70B)

### Frontend
- **Framework:** React 19.2.4
- **Build Tool:** Vite 8.0.1
- **Charts:** Recharts 3.8.1
- **PDF:** jsPDF 4.2.1 + jspdf-autotable 5.0.7
- **HTTP:** Axios 1.14.0
- **Animations:** Framer Motion 12.38.0

### Data Science
- **NumPy:** Numerical computing
- **Pandas:** Data manipulation
- **scikit-learn:** ML algorithms
- **XGBoost:** Gradient boosting
- **SHAP:** Explainable AI
- **LIME:** Local explanations

---

## 📊 Model Performance

### Helical Gear (XGBoost)
- **Accuracy:** 99.4%
- **F1 Score:** 0.994
- **AUC:** 0.999
- **Features:** 8 (Load, Torque, Vibration, Temperature, Wear, Lubrication, Efficiency, Cycles)

### Spur Gear (SVM)
- **Accuracy:** 98.2%
- **F1 Score:** 0.982
- **AUC:** 0.995
- **Features:** 6 (Speed, Torque, Vibration, Temperature, Shock Load, Noise)

### Bevel Gear (XGBoost)
- **Accuracy:** 99.1%
- **F1 Score:** 0.991
- **AUC:** 0.998
- **Features:** 8 (same as Helical)

---

## 🔧 Configuration

### Groq API Key
Edit `gear_api.py` line 24:
```python
os.environ["GROQ_API_KEY"] = "your_api_key_here"
```
Get free API key: https://console.groq.com/

### Backend Port
Edit `gear_api.py` line 951:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Frontend API URL
Edit `dashboard/src/api/gearApi.js` line 3:
```javascript
const API_BASE = 'http://localhost:8000';
```

---

## 📚 Documentation

- **QUICK_START.md** — Step-by-step guide to run the app
- **PROJECT_STATUS.md** — Comprehensive status report
- **IMPLEMENTATION_COMPLETE.md** — Implementation summary
- **implementation-plan.md** — Original feature specifications
- **task.md** — Task tracker

---

## 🧪 Testing

### Manual Testing Checklist
- [ ] Start backend and verify all models load
- [ ] Start frontend and access dashboard
- [ ] Switch between gear types (Helical/Spur/Bevel)
- [ ] Adjust sensor sliders and verify predictions update
- [ ] Navigate to SHAP + LIME tab and verify both charts display
- [ ] Generate PDF report and verify download
- [ ] Open AI Copilot and ask a question
- [ ] Check Trends & History tab for sensor charts
- [ ] Run What-If Optimizer
- [ ] Verify Cost Impact calculations
- [ ] Check Model Comparison table

### API Testing
Visit `http://localhost:8000/docs` for interactive Swagger UI

---

## 🐛 Troubleshooting

### Backend Issues
**Problem:** Models not loading  
**Solution:** Run training scripts:
```bash
py models/train_models.py
py models/train_spur_svm.py
py models/train_bevel_model.py
```

**Problem:** Missing Python packages  
**Solution:** `pip install fastapi uvicorn numpy pandas joblib scikit-learn xgboost shap lime`

### Frontend Issues
**Problem:** npm not found  
**Solution:** Install Node.js from https://nodejs.org/

**Problem:** jsPDF not found  
**Solution:** `cd dashboard && npm install`

### AI Copilot Issues
**Problem:** 401 Unauthorized  
**Solution:** Check Groq API key in `gear_api.py`

---

## 📈 Future Enhancements

- [ ] Real-time sensor data integration (IoT)
- [ ] Multi-user authentication system
- [ ] Email alerts for critical faults
- [ ] Mobile app (React Native)
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] PostgreSQL migration for production
- [ ] Advanced analytics dashboard
- [ ] Predictive maintenance scheduling
- [ ] Integration with ERP systems

---

## 👥 Team

**Project:** GearMind AI Dashboard  
**Version:** 5.0  
**Status:** ✅ Production Ready  
**Last Updated:** April 7, 2026

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 🎉 Acknowledgments

- **Elecon Engineering** — Industrial gear specifications
- **AGMA 2003-B97** — Bevel gear design standard
- **Groq** — LLaMA 3.3 70B API access
- **SHAP/LIME** — Explainable AI libraries

---

**Ready to monitor your gears? Start the application and explore! 🚀**
