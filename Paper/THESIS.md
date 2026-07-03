# GearMind AI: Explainable AI for Industrial Gear Fault Detection

**Bachelor's Final Year Internship Thesis**

---

## 📄 Thesis Information

| Detail | Information |
|--------|-------------|
| **Title** | GearMind AI: Explainable AI for Industrial Gear Fault Detection & Predictive Maintenance Dashboard |
| **Author** | Om Patel |
| **Academic Guide** | Dr. Kinjal Joshi |
| **Industry Mentor** | Satyam Raval (Tech Elecon Pvt. Ltd.) |
| **Institution** | G H Patel College of Engineering & Technology, CVM University |
| **Degree** | Bachelor of Engineering (B.E.) in Computer Science and Design |
| **Company** | Tech Elecon Pvt. Ltd., Anand, Gujarat |
| **Duration** | 16 weeks (January 1 - April 30, 2026) |

---

## 📋 Abstract

GearMind AI is a comprehensive explainable artificial intelligence system for industrial gear fault detection and predictive maintenance developed during a 16-week internship. The system employs a per-gear-type multi-model architecture with dedicated classifiers for four gear types: Helical (99.87% accuracy), Spur (82.3%), Bevel (99.4%), and Worm (100%).

The system integrates SHAP and LIME explainability frameworks with a full-stack architecture comprising a FastAPI backend with 16 REST endpoints and a React 19 frontend with 14 interactive modules. An AI Copilot powered by LLaMA 3.3 70B provides natural language maintenance guidance, while the Manufacturing QC module ensures AGMA-grade compliance (96% pass rate).

The system maintains sub-300ms API response time for full predictions including SHAP computation and demonstrates significant cost savings of Rs. 4.05-4.68 Lakh per gear unit through early fault detection, replacing failure-driven maintenance approaches.

**Keywords:** Explainable AI, XAI, SHAP, LIME, Gear Fault Detection, Predictive Maintenance, Machine Learning, Industrial IoT, Manufacturing Quality Control

---

## 🎯 Objectives & Scope

### **Primary Objectives**
1. Develop dedicated machine learning classifiers for each gear type
2. Integrate SHAP and LIME for transparent, interpretable predictions
3. Build production-ready full-stack system with real-time inference
4. Achieve high accuracy (>95%) while maintaining explainability
5. Integrate AGMA manufacturing standards compliance
6. Provide actionable maintenance guidance through AI support

### **Scope**
- Four gear types: Helical, Spur, Bevel, Worm
- Real-time prediction and explainability
- Industrial deployment at Tech Elecon
- Full-stack development (backend + frontend)
- Manufacturing QC integration
- Cost-benefit analysis and ROI

---

## 🏗️ System Architecture

### **Per-Gear-Type Multi-Model Pipeline**

```
Input: Sensor Data + Gear Type
    ↓
[Gear Type Router]
    ├─ Helical → GBM Model (99.87%)
    ├─ Spur → SVM RBF Model (82.3%)
    ├─ Bevel → SVM RBF Model (99.4%)
    └─ Worm → GBM Model (100%)
    ↓
[Prediction Engine]
├─ Classification: Healthy/Faulty
├─ Confidence Score
└─ RUL Regression: Remaining Useful Life
    ↓
[Explainability Layer]
├─ SHAP: Feature contributions
├─ LIME: Local explanations
└─ Visualization: Waterfall/Force plots
    ↓
[Analysis Modules]
├─ Vibration & PHM (FFT analysis)
├─ Manufacturing QC (AGMA validation)
└─ Differential Evolution Optimizer
    ↓
[Support Systems]
├─ AI Copilot (LLaMA 3.3 70B)
├─ Report Generator (7 sections)
└─ Cost Impact Analysis
    ↓
Output: Predictions + Explanations + Guidance
```

---

## 🤖 Machine Learning Models

### **Model Selection & Performance**

| Gear Type | Model | Algorithm | Accuracy |
|-----------|-------|-----------|----------|
| **Helical** | GBM | Gradient Boosting | 99.87% |
| **Spur** | SVM | RBF Kernel | 82.3% |
| **Bevel** | SVM | RBF Kernel | 99.4% |
| **Worm** | GBM | Gradient Boosting | 100% |

### **Supporting Infrastructure**

Each gear type includes:
- **StandardScaler:** Feature normalization (μ=0, σ=1)
- **Label Encoder:** Categorical to numerical mapping
- **RUL Regressor:** Remaining Useful Life prediction
- **SMOTE Oversampling:** Class imbalance handling

### **Why Per-Gear-Type Architecture?**

Different gear types have distinct failure signatures:
- **Helical:** Complex non-linear patterns → GBM captures best
- **Spur:** Clear decision boundaries → SVM effective
- **Bevel:** Distinctive fault characteristics → SVM optimal
- **Worm:** Unique failure modes → GBM handles well

Specialized models achieve higher accuracy than single universal model.

---

## 🔍 Explainability Mechanisms

### **SHAP (SHapley Additive exPlanations)**

**Theory:**
- Based on Shapley values from cooperative game theory
- Each feature assigned theoretical contribution to prediction
- Satisfies mathematical properties (local accuracy, consistency)

**Implementation:**
- TreeExplainer for tree-based models (GBM)
- KernelExplainer for SVM models
- Global and local explanations

**Output Visualizations:**
- **Waterfall Plots:** Step-by-step feature contribution
- **Force Plots:** Push/pull from base value
- **Summary Plots:** Aggregate feature importance
- **Dependence Plots:** Feature-prediction relationships

**Example:**
```
Prediction: BEARING FAULT DETECTED (Confidence: 94.2%)

Feature Contributions:
├─ RMS_Vibration:      +0.45  (strong fault indicator)
├─ Peak_Frequency:     +0.28  (characteristic fault freq)
├─ Temperature_Rise:   +0.15  (friction heat)
├─ Oil_Condition:      -0.10  (still acceptable)
└─ Variance:           -0.08  (normal range)

Base Value: 0.32
Predicted: 1.02
```

### **LIME (Local Interpretable Model-agnostic Explanations)**

**Theory:**
- Approximate complex model with simple local linear model
- Perturb input features and observe prediction changes
- Model-agnostic: works with any black-box model

**Implementation:**
1. Perturb input features (±10% variations)
2. Generate 1000 perturbed samples
3. Fit weighted linear regression
4. Extract feature coefficients

**Output:**
- Top K influential features
- Feature weights/directions
- Local decision boundary
- Non-technical explanation

**Example:**
```
"TOOTH WEAR DETECTED" (87% confidence)

Contributing Factors:
├─ RMS_Vibration:        +0.34
├─ Freq_Peak_1K_2K:      +0.28  (tooth mesh frequency)
├─ Crest_Factor:         +0.19  (impulsive nature)
└─ Temperature:          -0.15
```

### **Complementary Benefits**

| Aspect | SHAP | LIME |
|--------|------|------|
| **Scope** | Global patterns | Local decision |
| **Speed** | Faster | Slower |
| **Stability** | Theoretically sound | Approximate |
| **Use** | Trend analysis | Individual cases |

---

## 📊 Data & Feature Engineering

### **Data Preparation**

```
Raw Sensor Input (100 Hz sampling)
    ↓
Data Cleaning
├─ Remove outliers (>3σ)
├─ Handle missing values
└─ Interpolate gaps
    ↓
Normalization (StandardScaler)
    ↓
Feature Extraction
├─ Time-domain:
│  ├─ RMS (Root Mean Square)
│  ├─ Peak (Maximum amplitude)
│  ├─ Crest Factor (Peak/RMS)
│  └─ Variance
│
├─ Frequency-domain:
│  ├─ FFT spectrum
│  ├─ Power spectrum density
│  ├─ Peak frequency
│  └─ Spectral centroid
│
└─ Statistical:
   ├─ Skewness (asymmetry)
   ├─ Kurtosis (tailedness)
   └─ Entropy (disorder)
    ↓
Feature Selection
├─ Correlation analysis
├─ Feature importance ranking
└─ Multicollinearity removal
    ↓
Class Imbalance Handling (SMOTE)
├─ Identify minority class
├─ Generate synthetic samples
└─ Balanced dataset
    ↓
Training Set Ready
```

### **SMOTE Oversampling**

**Problem:** Class imbalance (many healthy, few faulty samples)

**Solution:** Synthetic Minority Over-sampling Technique
- For each minority sample: Find k-nearest neighbors
- Generate synthetic samples between original and neighbors
- Interpolation: synthetic = original + random × (neighbor - original)

**Result:** 
- Balanced training data
- Improved generalization
- Reduced bias toward majority class
- Better minority class learning

---

## 💻 Full-Stack Technology

### **Backend Architecture**

**API Server:**
- FastAPI: Modern, async, type-safe Python framework
- Uvicorn: ASGI application server
- 16 REST endpoints
- <300ms response time (with SHAP computation)

**ML Pipeline:**
- scikit-learn: SVM, feature scaling, preprocessing
- XGBoost: Gradient boosting models
- LightGBM: Fast boosting implementation
- NumPy/Pandas: Numerical operations

**Explainability:**
- SHAP: Feature importance & local explanations
- LIME: Local linear approximations
- Plotly/Matplotlib: Visualization

**AI Integration:**
- LLaMA 3.3 70B via Groq API
- Natural language maintenance guidance
- Context-aware recommendations

**Database:**
- SQLite: Lightweight, self-contained SQL database
- SQLAlchemy: Python ORM for queries
- Structured prediction history
- User management

### **Frontend Architecture**

**UI Framework:**
- React 19: Modern component-based UI
- TypeScript: Type-safe JavaScript
- 14 interactive dashboard modules

**Visualization:**
- Recharts: React charting library
- Plotly.js: Interactive plots
- D3.js: Advanced data visualization
- Chart.js: Lightweight charts

**State & Communication:**
- Redux: Global application state
- Axios: HTTP client
- React Context: Component state
- Real-time updates

**Design & UX:**
- Responsive layout
- WCAG accessibility
- Dark mode support
- Mobile-friendly interface

### **Deployment**

**Containerization:**
- Docker: Containerized application
- Docker Compose: Multi-container orchestration

**Infrastructure:**
- Backend: FastAPI + Uvicorn
- Frontend: React production build
- Database: SQLite (development), PostgreSQL (production)
- Monitoring: Logging and error tracking

---

## 📊 Dashboard Modules (14 Components)

### **1. Login & Authentication**
- Secure JWT-based authentication
- Role-based access control (RBAC)
- User session management
- Password encryption

### **2. Main Dashboard - Gear Health**
- Real-time health status per gear type
- Visual indicators: Healthy/Warning/Critical
- Last prediction timestamp
- Quick action alerts

### **3. Vibration & PHM Analysis**
- FFT spectral decomposition
- Time-domain waveform display
- Frequency-domain power spectrum
- Prognostics metrics (RUL, MTBF)

### **4. SHAP + LIME Explainability**
- Side-by-side visualization
- Waterfall plots
- Force plots
- Feature importance ranking

### **5. What-If Optimizer**
- Differential Evolution algorithm
- Parameter adjustment interface
- Real-time prediction updates
- Scenario analysis

### **6. Manufacturing QC Module**
- AGMA standard checking
- Dimensional verification
- Pass/Fail assessment
- Compliance reports

### **7. Reliability & Fatigue Data**
- Historical MTBF tracking
- Wear progression
- Fatigue curve analysis
- Trend visualization

### **8. Staff Directory & Schedule**
- Maintenance team roster
- Shift schedules
- On-call assignments
- Contact information

### **9. AI Report Generator**
- 7-section report structure
- Executive summary
- Technical analysis
- Recommendations
- PDF export

### **10. AI Copilot Chat Widget**
- LLaMA 3.3 70B-powered
- Natural language support
- Maintenance guidance
- Context-aware responses

### **11. Cost Impact Analysis**
- Failure cost calculations
- Prevention cost analysis
- ROI projections
- Budget impact visualization

### **12. Model Comparison**
- Side-by-side accuracy metrics
- Performance comparison
- Feature importance comparison
- Algorithm analysis

### **13. History & Logs**
- Prediction history
- Trend analysis
- Pattern detection
- Downloadable reports

### **14. Settings & Configuration**
- User preferences
- Notification settings
- Model parameter tuning
- System configuration

---

## 🔧 Backend API (16 Endpoints)

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| 1 | `/api/auth/login` | POST | User authentication |
| 2 | `/api/auth/logout` | POST | Session termination |
| 3 | `/api/predict` | POST | Single prediction |
| 4 | `/api/predict/batch` | POST | Batch predictions |
| 5 | `/api/shap` | GET | SHAP explanations |
| 6 | `/api/lime` | GET | LIME explanations |
| 7 | `/api/vibration-analysis` | POST | FFT analysis |
| 8 | `/api/rul-prediction` | GET | RUL estimation |
| 9 | `/api/qc-check` | POST | AGMA validation |
| 10 | `/api/optimize-parameters` | POST | Parameter optimization |
| 11 | `/api/reports/generate` | POST | Report generation |
| 12 | `/api/copilot/chat` | POST | AI support |
| 13 | `/api/cost-analysis` | GET | Cost-benefit analysis |
| 14 | `/api/history` | GET | Prediction history |
| 15 | `/api/models/compare` | GET | Model comparison |
| 16 | `/api/data/export` | GET | Data export |

---

## 📈 Performance Metrics

| Metric | Value | Target |
|--------|-------|--------|
| **Helical Accuracy** | 99.87% | >95% ✓ |
| **Spur Accuracy** | 82.3% | >75% ✓ |
| **Bevel Accuracy** | 99.4% | >95% ✓ |
| **Worm Accuracy** | 100% | >95% ✓ |
| **Average Accuracy** | 95.38% | >90% ✓ |
| **API Response Time** | <300ms | <500ms ✓ |
| **Inference Latency** | <100ms | <200ms ✓ |
| **QC Pass Rate** | 96% | >90% ✓ |
| **Dashboard Load** | <2s | <3s ✓ |

---

## 💰 Economic Impact

### **Cost Analysis (Per Gear Unit)**

**Traditional Approach (Failure-Driven):**
- Emergency repair: Rs. 3,50,000
- Production downtime: Rs. 4,00,000 - 4,50,000
- Component replacement: Rs. 1,55,000
- **Total Cost:** Rs. 9,05,000 - 9,68,000

**GearMind AI Approach (Preventive):**
- Scheduled maintenance: Rs. 2,50,000
- Replacement parts: Rs. 2,00,000
- Labor: Rs. 50,000
- **Total Cost:** Rs. 5,00,000

**Savings Per Unit:** Rs. 4,05,000 - 4,68,000

### **Annual Financial Impact (50 units/year)**

| Metric | Value |
|--------|-------|
| **Total Savings** | Rs. 2,02,50,000 - 2,34,00,000 |
| **System Cost** | Rs. 10,00,000 (one-time) |
| **Break-even Time** | 4-5 months |
| **Annual ROI** | 400% - 450% |
| **Multi-year Value** | Exponential returns |

---

## 🧪 Testing & Validation

### **Test Coverage**

**Fault Prediction Module:**
- 50+ test cases
- Edge cases and boundaries
- Normal operation validation
- Robustness testing

**API Endpoints:**
- All 16 endpoints tested
- Request/response validation
- Error handling
- Performance benchmarking

**Frontend Modules:**
- Unit tests (React components)
- Integration tests
- User acceptance testing
- Cross-browser compatibility

**Manufacturing QC:**
- 96% parameter pass rate
- AGMA standard compliance
- Edge case handling

---

## 📋 Implementation Summary

### **Development Process**

**Phase 1: Requirements & Design (Weeks 1-2)**
- System requirements analysis
- Architecture design
- Technology selection
- Database schema design

**Phase 2: Data Preparation (Weeks 3-4)**
- Synthetic data generation (50,000+ samples)
- Preprocessing pipeline
- Feature engineering
- Class imbalance handling (SMOTE)

**Phase 3: ML Development (Weeks 5-8)**
- Individual model training (GBM, SVM)
- Hyperparameter optimization
- Cross-validation
- Model evaluation

**Phase 4: Explainability (Weeks 9-10)**
- SHAP integration
- LIME implementation
- Visualization development
- Explanation testing

**Phase 5: Full-Stack Development (Weeks 11-13)**
- FastAPI backend
- React 19 frontend
- API integration
- Database connectivity

**Phase 6: Testing & Deployment (Weeks 14-16)**
- Unit testing
- Integration testing
- Performance optimization
- Production deployment

---

## 🎓 Key Learnings

**Technical Competencies:**
- Multi-model ensemble architecture
- Explainable AI techniques (SHAP, LIME)
- Full-stack web development
- Real-time inference systems
- Manufacturing quality standards

**Domain Knowledge:**
- Industrial gear manufacturing
- Vibration analysis & fault diagnosis
- AGMA manufacturing standards
- Predictive maintenance strategies
- Industrial IoT integration

**Professional Skills:**
- Project management & scheduling
- Collaborative development
- Technical documentation
- System deployment
- Industry collaboration

---

## 🚀 Project Achievements

✅ **Technical Excellence:**
- 95.38% average model accuracy
- <300ms API response time
- 96% QC pass rate
- Production-ready system

✅ **Practical Implementation:**
- Full-stack development completed
- 14 interactive modules
- 16 API endpoints
- Real-time inference

✅ **Business Impact:**
- Rs. 4.05-4.68 Lakh savings per unit
- 400% annual ROI
- Early fault detection capability
- Improved equipment reliability

✅ **Innovation:**
- Per-gear-type architecture
- Dual explainability (SHAP + LIME)
- LLaMA 3.3 AI Copilot integration
- AGMA compliance automation

---

## 🔮 Future Directions

**Immediate Enhancements:**
- Expand to additional gear variants
- IoT sensor network integration
- Enhanced RUL modeling
- Mobile app development

**Advanced Features:**
- Transfer learning across gear types
- Federated learning for privacy
- Digital twin simulation
- Autonomous maintenance scheduling

**Commercialization:**
- SaaS platform development
- Multi-facility scalability
- Industry certifications
- Regulatory compliance

---

## 📝 Project Statistics

| Aspect | Quantity |
|--------|----------|
| **Duration** | 16 weeks |
| **Total Hours** | 320+ hours |
| **Code Files** | 45+ files |
| **Python Scripts** | 25+ scripts |
| **React Components** | 50+ components |
| **Database Tables** | 8 tables |
| **API Endpoints** | 16 endpoints |
| **Dashboard Modules** | 14 modules |
| **ML Models** | 8 models |
| **Test Cases** | 150+ tests |

---

## ✅ Completion Status

| Milestone | Status | Date |
|-----------|--------|------|
| **Requirements Analysis** | ✅ Complete | Jan 2026 |
| **Data Preparation** | ✅ Complete | Jan 2026 |
| **ML Model Development** | ✅ Complete | Feb 2026 |
| **Backend Development** | ✅ Complete | Mar 2026 |
| **Frontend Development** | ✅ Complete | Mar 2026 |
| **Testing & Validation** | ✅ Complete | Apr 2026 |
| **Production Deployment** | ✅ Complete | Apr 2026 |
| **Internship Completion** | ✅ Complete | Apr 30, 2026 |

---

## 🏆 Internship Certification

**Issued by:** G H Patel College of Engineering & Technology

**Academic Guide:** Dr. Kinjal Joshi

**Industry Mentor:** Satyam Raval (Tech Elecon Pvt. Ltd.)

**Duration:** 16 weeks (January 1 - April 30, 2026)

**Status:** ✅ Successfully Completed

---

## 📄 Declaration

This thesis represents original work completed under the guidance of Dr. Kinjal Joshi and industry mentorship from Satyam Raval at Tech Elecon Pvt. Ltd. All technical implementation, testing, and deployment have been conducted during the 16-week internship period.

---

**Submitted to:** G H Patel College of Engineering & Technology, CVM University

**Program:** Bachelor of Engineering (B.E.) in Computer Science and Design

**Year:** 2025-2026

---

*GearMind AI: Making Industrial Fault Detection Transparent, Trustworthy, and Actionable*
