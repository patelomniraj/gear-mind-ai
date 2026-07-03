# GearMind AI: Explainable AI for Industrial Gear Fault Detection

**Bachelor's Final Year Internship Project (16 Weeks)**

---

## 📄 Project Information

| Detail | Information |
|--------|-------------|
| **Project Title** | GearMind AI: Full-Stack Industrial Gear Fault Detection & Predictive Maintenance Dashboard |
| **Author** | Om Patel |
| **Guide** | Dr. Kinjal Joshi |
| **Industry Mentor** | Satyam Raval (Tech Elecon Pvt. Ltd.) |
| **Institution** | G H Patel College of Engineering & Technology (GCET), CVM University |
| **Degree** | Bachelor of Engineering (B.E.) in Computer Science and Design |
| **Internship Company** | Tech Elecon Pvt. Ltd., Anand, Gujarat |
| **Internship Duration** | 16 weeks (January 1 - April 30, 2026) |
| **Location** | Vallabh Vidyanagar, Gujarat, India |

---

## 📋 Overview

**GearMind AI** is a production-ready, full-stack industrial gear fault detection and predictive maintenance system developed during a 16-week internship at Tech Elecon Pvt. Ltd. The system employs a sophisticated per-gear-type multi-model architecture with dedicated machine learning classifiers trained for each gear type (Helical, Spur, Bevel, Worm), integrated with explainable AI frameworks (SHAP and LIME).

The system successfully demonstrates practical application of explainable artificial intelligence in real-world manufacturing environments, delivering significant cost savings through early fault detection.

---

## 🎯 Key Objectives

- Develop dedicated ML classifiers for each of the four gear types
- Achieve high classification accuracy while maintaining interpretability
- Implement XAI frameworks (SHAP and LIME) for transparent predictions
- Build a production-ready full-stack system with real-time inference
- Integrate manufacturing QC standards (AGMA compliance)
- Provide actionable maintenance guidance through AI support

---

## 🤖 Machine Learning Models

### **Per-Gear-Type Architecture**

| Gear Type | Model | Accuracy |
|-----------|-------|----------|
| **Helical Gears** | Gradient Boosting Machine (GBM) | 99.87% |
| **Spur Gears** | SVM with RBF Kernel | 82.3% |
| **Bevel Gears** | SVM with RBF Kernel | 99.4% |
| **Worm Gears** | Gradient Boosting Machine (GBM) | 100% |

### **Supporting Components**

Each gear type includes:
- StandardScaler for normalization
- Label Encoder for categorical mapping
- RUL (Remaining Useful Life) Regressor
- SMOTE oversampling for class balance

---

## 🔍 Explainability Frameworks

### **SHAP (SHapley Additive exPlanations)**
- Global feature importance
- Waterfall plots
- Force plots for visualization
- Per-prediction contribution breakdown

### **LIME (Local Interpretable Model-agnostic Explanations)**
- Local linear approximations
- Feature weight visualization
- Individual prediction explanations
- Decision boundary analysis

---

## 💻 Technology Stack

### **Backend**
- **Framework:** FastAPI with Uvicorn
- **Language:** Python 3.8+
- **ML Libraries:** scikit-learn, XGBoost, LightGBM
- **Explainability:** SHAP, LIME
- **Database:** SQLite with SQLAlchemy ORM
- **API:** 16 REST endpoints with JSON format

### **Frontend**
- **Framework:** React 19 with TypeScript
- **Components:** 14 interactive dashboard modules
- **Visualization:** Recharts, Plotly.js, D3.js
- **State Management:** Redux + Context API
- **HTTP Client:** Axios

### **AI & NLP**
- **LLaMA 3.3 70B** via Groq API
- Natural language decision support
- Maintenance guidance generation

### **Additional Features**
- Manufacturing QC with AGMA compliance
- Vibration & PHM analysis with FFT
- Differential Evolution optimizer
- 7-section AI-generated maintenance reports with PDF export

---

## 📊 Dashboard Modules (14 Components)

1. **Login & Authentication** - Secure role-based access
2. **Main Dashboard** - Gear health overview
3. **Vibration & PHM Analysis** - FFT spectral decomposition
4. **SHAP + LIME Explanations** - Explainability visualizations
5. **What-If Optimizer** - Parameter optimization
6. **Manufacturing QC** - AGMA compliance checking
7. **Reliability & Fatigue Data** - Historical metrics
8. **Staff Directory** - Team management
9. **AI Report Generator** - Automated 7-section reports
10. **AI Copilot Chat** - LLaMA-powered support
11. **Cost Impact Analysis** - ROI projections
12. **Model Comparison** - Performance metrics
13. **History Module** - Prediction logs
14. **Settings & Configuration** - System preferences

---

## 🚀 Backend API Endpoints (16 Total)

- `/api/auth/login` - User authentication
- `/api/auth/logout` - Session termination
- `/api/predict` - Single prediction
- `/api/predict/batch` - Batch predictions
- `/api/shap` - SHAP explanations
- `/api/lime` - LIME explanations
- `/api/vibration-analysis` - FFT analysis
- `/api/rul-prediction` - Remaining useful life
- `/api/qc-check` - AGMA compliance validation
- `/api/optimize-parameters` - Parameter optimization
- `/api/reports/generate` - Report generation
- `/api/copilot/chat` - AI support
- `/api/cost-analysis` - Cost-benefit analysis
- `/api/history` - Prediction history
- `/api/models/compare` - Model comparison
- Additional endpoints for data retrieval

---

## 📈 System Performance

| Metric | Value |
|--------|-------|
| **Average Model Accuracy** | 95.38% |
| **API Response Time** | <300ms (with SHAP) |
| **QC Pass Rate** | 96% |
| **Inference Latency** | <100ms per prediction |
| **Database Query Time** | <50ms |
| **Dashboard Load Time** | <2 seconds |

---

## 💰 Cost-Benefit Analysis

### **Economic Impact (Per Gear Unit)**

| Scenario | Cost (INR) |
|----------|-----------|
| **Early Detection** | 5,00,000 |
| **Failure-Driven Maintenance** | 9,05,000 - 9,68,000 |
| **Savings per Unit** | 4,05,000 - 4,68,000 |

### **Annual Impact (50 Units)**
- **Total Savings:** Rs. 2,02,50,000 - 2,34,00,000
- **Break-even Time:** 4-5 months
- **ROI:** 400% - 450% annually

---

## 📊 System Architecture

```
Raw Sensor Data
    ↓
Data Preprocessing
    ↓
Gear Type Classification
    ↓
Gear-Specific ML Pipeline
├─ Normalization (StandardScaler)
├─ Feature Extraction (Time/Freq/Stats)
├─ Classification (GBM/SVM)
└─ RUL Regression
    ↓
Explainability (SHAP + LIME)
    ↓
Vibration & PHM Analysis
    ↓
QC Validation (AGMA Standards)
    ↓
AI Report & Copilot Support
    ↓
Final Output: Predictions + Guidance
```

---

## 📊 Database Schema

### **Key Tables**
- `gear_history` - Prediction logs and results
- `users` - User accounts
- `roles` - Role definitions
- `permissions` - Access control
- `predictions` - Detailed prediction records
- `reports` - Generated maintenance reports
- `cost_analysis` - Cost tracking

---

## 🔧 Implementation Highlights

### **Data Preparation**
- Physics-informed synthetic data generation
- 50,000+ training samples per gear type
- SMOTE oversampling for class balance
- Robust feature engineering

### **Model Development**
- Per-gear-type optimization
- 5-fold cross-validation
- Grid search hyperparameter tuning
- 70% training / 15% validation / 15% test split

### **Production Deployment**
- Sub-300ms API response time
- Real-time inference capability
- Database-backed predictions
- Scalable architecture

---

## ✅ Testing & Quality

### **Test Coverage**
- 50+ fault prediction test cases
- 16 API endpoint tests
- 14 frontend module tests
- Manufacturing QC validation (96% pass rate)
- Edge case and boundary condition testing

---

## 🎓 Key Features

✅ Per-gear-type dedicated models  
✅ Dual explainability (SHAP + LIME)  
✅ Production-ready full-stack system  
✅ LLaMA 3.3 70B AI Copilot  
✅ AGMA compliance module  
✅ 7-section AI report generation  
✅ Differential Evolution optimizer  
✅ Real-time inference (<300ms)  
✅ Comprehensive dashboard (14 modules)  
✅ Cost-benefit analysis tools  

---

## 📁 Project Structure

```
gearmind-ai/
├── backend/
│   ├── main.py
│   ├── models/
│   ├── api/
│   ├── database/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── package.json
├── data/
│   └── sample_data/
├── docs/
│   └── API_documentation.md
├── README.md
└── THESIS.md
```

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- Node.js 14+
- pip, npm

### **Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/gearmind-ai.git
cd gearmind-ai

# Backend setup
cd backend
pip install -r requirements.txt
python main.py

# Frontend setup (in new terminal)
cd frontend
npm install
npm start
```

### **Access Dashboard**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

---

## 🔬 ML Pipeline Overview

### **Feature Engineering**
- **Time-domain:** RMS, Peak, Crest Factor, Variance
- **Frequency-domain:** FFT-based features, Power Spectrum
- **Statistical:** Skewness, Kurtosis, Entropy

### **Model Training**
1. Data preprocessing and normalization
2. Feature extraction and selection
3. SMOTE oversampling for class balance
4. Model training with cross-validation
5. Hyperparameter optimization
6. Explainability layer integration

### **Inference**
1. Real-time sensor data input
2. Feature extraction (same as training)
3. Gear type classification
4. Gear-specific model prediction
5. SHAP + LIME explanation generation
6. QC validation
7. Report generation with AI guidance

---

## 📊 Results

### **Model Performance**
- Helical: 99.87% accuracy
- Spur: 82.3% accuracy
- Bevel: 99.4% accuracy
- Worm: 100% accuracy

### **System Metrics**
- API response time: <300ms
- QC pass rate: 96%
- Dashboard load: <2 seconds
- Cost savings: Rs. 4.05-4.68 Lakh per unit

---

## 🎓 Learning Outcomes

**Technical Skills:**
- ML pipeline development
- Explainable AI implementation
- Full-stack web development
- FastAPI backend development
- React 19 frontend development
- Real-time inference systems
- API design and implementation

**Domain Knowledge:**
- Industrial gear manufacturing
- Vibration analysis and fault diagnosis
- AGMA manufacturing standards
- Predictive maintenance strategies
- Prognostics and Health Management

**Professional Skills:**
- Project management
- Collaborative development
- Technical documentation
- System deployment
- Industry collaboration

---

## 🚀 Future Enhancements

- Expand to other machinery types
- Implement transfer learning
- Develop mobile app for field technicians
- Add federated learning for privacy
- Create digital twin simulation
- Develop SaaS platform
- Regulatory certifications

---

## 📄 Internship Completion

**Internship Certification:**
- Issued by: G H Patel College of Engineering & Technology
- Internal Guide: Dr. Kinjal Joshi
- Industry Mentor: Satyam Raval (Tech Elecon Pvt. Ltd.)
- Duration: 16 weeks (01.01.2026 - 30.04.2026)
- Status: ✅ Successfully Completed

---

## 📝 Project Statistics

| Metric | Value |
|--------|-------|
| **Duration** | 16 weeks |
| **Development Hours** | 320+ hours |
| **Code Files** | 45+ |
| **Python Scripts** | 25+ |
| **React Components** | 50+ |
| **Database Tables** | 8 |
| **API Endpoints** | 16 |
| **Dashboard Modules** | 14 |
| **ML Models** | 8 (2 per gear type) |
| **Test Cases** | 150+ |

---

## 📄 License

This project is open source and available for educational and commercial use.

---

## 🔗 References

**Project Documentation:**
- Full Thesis: See THESIS.md
- API Documentation: /docs/API_documentation.md
- Technical Specifications: /docs/TECHNICAL_SPECS.md

**Associated Materials:**
- Internship Report: Official documentation at GCET
- Certificates: Available upon request

---

**Status:** ✅ Complete & Deployed

**Internship Guide:** Dr. Kinjal Joshi  
**Industry Mentor:** Satyam Raval (Tech Elecon Pvt. Ltd.)

**Submitted to:** G H Patel College of Engineering & Technology, CVM University

---

*Developed during Bachelor's Final Year Internship*

*G H Patel College of Engineering & Technology*

*Vallabh Vidyanagar, Gujarat, India*
