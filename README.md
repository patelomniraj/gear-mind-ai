# GearMind AI - Explainable AI for Industrial Predictive Maintenance

**GearMind AI** is an industrial-grade, full-stack machine learning system for gear fault detection, remaining useful life (RUL) estimation, and predictive maintenance. Developed during an 8-week internship at **Elecon Engineering Works Pvt. Ltd.**, India's largest gear manufacturer, this system transforms reactive maintenance into predictive, data-driven operations using explainable AI.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-19-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Overview

GearMind AI integrates five supervised machine learning models with explainable AI techniques (SHAP & LIME), an LLM-powered AI Copilot, and an interactive React dashboard into a unified web platform.

### Key Achievements

- **92% Accuracy** on fault detection (Gradient Boosting Machine)
- **0.97 AUC** score with strong generalization
- **96% Manufacturing QC Pass Rate** on tolerance checks
- **Rs. 4.05-4.68 Lakh Savings** per gear unit through early detection
- **<300ms API Response Time** for real-time predictions
- **8 Professional Dashboard Modules** for comprehensive monitoring
- **Full Explainability** via SHAP and LIME for every prediction

---

## 🎯 Problem Statement

Manufacturing companies face challenges with:
- **Reactive maintenance**: Only fixing gears after failure
- **High downtime costs**: Unexpected equipment breakdowns
- **Quality variability**: Manual inspection inconsistencies
- **Lack of predictive insights**: No early warning systems

**GearMind AI solves this** by predicting gear faults before failure occurs, enabling:
- Preventive maintenance scheduling
- Cost optimization
- Quality assurance automation
- Data-driven decision making

---

## ✨ Key Features

### Machine Learning Pipeline
- ✓ 5 trained models (GBM, XGBoost, Random Forest, SVM, LR)
- ✓ 92% accuracy with cross-validation
- ✓ Physics-informed synthetic data
- ✓ Anomaly detection integration

### Explainable AI (XAI)
- ✓ SHAP (SHapley Additive exPlanations)
- ✓ LIME (Local Interpretable Model-agnostic Explanations)
- ✓ Feature importance visualization
- ✓ Attention maps for prediction explanation

### Full-Stack Architecture
- ✓ React 19 frontend with professional UI
- ✓ FastAPI backend with 10+ REST endpoints
- ✓ SQLite database for history tracking
- ✓ MLflow for experiment tracking
- ✓ LLaMA 3.3 70B AI Copilot via Groq API

### 8 Dashboard Modules
1. **Gear Health Dashboard** - Real-time monitoring
2. **Vibration & PHM Analysis** - Signal processing
3. **SHAP + LIME Explainability** - Model interpretability
4. **What-If Optimizer** - Parameter optimization
5. **Manufacturing QC** - Quality control verification
6. **Reliability & Fatigue Data** - Engineering analytics
7. **Staff & Shift Management** - Operations management
8. **AI Report Generator** - Automated reporting

---

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI with Uvicorn
- **ML/AI**: Scikit-learn, XGBoost, TensorFlow, Groq LLaMA
- **Processing**: OpenCV, NumPy, Pandas, SciPy
- **Database**: SQLite with SQLAlchemy ORM
- **Tracking**: MLflow v4.0
- **Language**: Python 3.11

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS
- **Visualization**: Recharts
- **Icons**: Lucide React
- **Reports**: jsPDF
- **Language**: JavaScript/TypeScript

### Infrastructure
- **API**: RESTful architecture
- **Auth**: Role-Based Access Control (RBAC)
- **Deployment**: Docker-ready
- **Monitoring**: Logging and error tracking

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Fault Prediction Accuracy | 92% |
| AUC-ROC Score | 0.97 |
| F1 Score | 0.91 |
| Manufacturing QC Pass Rate | 96% |
| API Response Time | <300ms |
| Cost Savings Per Unit | Rs. 4.05-4.68 Lakh |
| Supported Gear Units | 25 (scalable) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 20 LTS
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/patelomniraj/gearmind-ai.git
   cd gearmind-ai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend Setup** (in another terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Application**
   - Open browser: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

### Environment Variables

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your actual values:
```
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///gear_history.db
API_PORT=8000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Fault classification + RUL + SHAP |
| POST | `/api/detect-batch` | Batch processing multiple gears |
| GET | `/api/models` | Model performance comparison |
| POST | `/api/chat` | LLM Copilot Q&A |
| POST | `/api/report` | Generate maintenance report |
| POST | `/api/optimize` | Parameter optimization |
| GET | `/api/history` | Detection history |
| GET | `/api/statistics` | Analytics and statistics |
| GET | `/api/health` | Health check |

See [API_REFERENCE.md](docs/API_REFERENCE.md) for detailed documentation.

---

## 📚 Documentation

- **[INSTALLATION.md](docs/INSTALLATION.md)** - Detailed setup guide
- **[USAGE.md](docs/USAGE.md)** - How to use the system
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - API documentation
- **[TECHNICAL.md](docs/TECHNICAL.md)** - Technical implementation

---

## 🏗 Project Structure

```
gearmind-ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── ml_pipeline.py       # ML preprocessing
│   ├── detection_engine.py  # Detection logic
│   ├── database.py          # Database operations
│   ├── requirements.txt
│   ├── models/
│   │   └── best_classifier.pkl
│   └── logs/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── USAGE.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── TECHNICAL.md
├── data/
│   ├── sample_images/
│   └── sample_data.csv
├── .env.example
├── .gitignore
└── LICENSE
```

---

## 🔐 Security

- ✓ No hardcoded secrets (uses environment variables)
- ✓ Input validation and sanitization
- ✓ Rate limiting on API endpoints
- ✓ CORS properly configured
- ✓ SQL injection prevention (ORM usage)
- ✓ Secrets never committed to version control

---

## 🧪 Testing

Run tests:
```bash
cd backend
pytest tests/
```

Coverage:
```bash
pytest --cov=. tests/
```

---

## 🎓 Educational Alignment

This project aligns with **UMD MSAI (MS Artificial Intelligence)** curriculum:

- **CMSC 733**: Computer Vision principles and image processing
- **CMSC 726**: Machine Learning models and evaluation
- **CMSC 828**: Deep Learning and neural networks
- **CMSC 828C**: Computer Vision applications
- **Research Component**: Custom implementation and optimization

---

## 💼 Use Cases

1. **Manufacturing QC**: Automated defect detection
2. **Predictive Maintenance**: Prevent equipment failures
3. **Cost Optimization**: Reduce maintenance spending
4. **Quality Assurance**: Ensure product quality
5. **Data-Driven Operations**: Evidence-based decisions

---

## 📈 Results

GearMind AI achieved:
- **92% accuracy** on gear fault classification
- **96% precision** on manufacturing QC checks
- **<300ms latency** for real-time predictions
- **Rs. 4.68 Lakh** maximum savings per gear unit
- **8 production-ready modules** deployed

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

---

## 👤 Author

**Isha Patel**
- Email: ishapatel@ghpatel.ac.in
- GitHub: [@patelomniraj](https://github.com/patelomniraj)
- Organization: G H Patel College of Engineering & Technology
- Internship: Elecon Engineering Works Pvt. Ltd.

---

## 🙏 Acknowledgments

- **Elecon Engineering Works** for the internship opportunity
- **Mr. Satyam Raval** (Industry Mentor) for domain guidance
- **Dr. Malay Bhatt** (Academic Guide) for supervision
- **Dr. Nikhil Gondaliya** (Department Head) for support

---

## 📞 Support

For questions or issues:
1. Check the documentation in `/docs`
2. Review the [API Reference](docs/API_REFERENCE.md)
3. Open an issue on GitHub
4. Contact: ishapatel@ghpatel.ac.in

---

## 🔄 Deployment

### Local Development
```bash
python main.py  # Backend
npm run dev     # Frontend
```

### Production (Docker)
```bash
docker-compose up
```

### Environment Configuration
See `.env.example` for all available settings.

---

**Last Updated**: May 2026  
**Version**: 4.0 (Stable)  
**Status**: Production Ready

⭐ If you find this project useful, please star the repository!
