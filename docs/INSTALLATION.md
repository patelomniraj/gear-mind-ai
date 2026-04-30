# Installation Guide

Complete step-by-step instructions to set up GearMind AI locally.

## Prerequisites

- Python 3.8 or higher
- Node.js 20 LTS or higher
- Git
- pip and npm (usually come with Python and Node)

## Step 1: Clone the Repository

```bash
git clone https://github.com/patelomniraj/gearmind-ai.git
cd gearmind-ai
```

## Step 2: Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your actual values
# For Groq API key: Get from https://console.groq.com
```

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Test backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Frontend Setup (New Terminal)

```bash
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

## Step 5: Access the Application

Open your browser and go to:
```
http://localhost:5173
```

The application should load with:
- Upload interface
- Real-time detection
- Dashboard and analytics

## Troubleshooting

### Python Issues

**Module not found**
```bash
pip install -r requirements.txt
```

**Virtual environment not activating**
```bash
# Ensure you're in the project directory
python -m venv venv
# Then activate as shown above
```

### Frontend Issues

**Port 5173 already in use**
```bash
# Kill the process or specify different port
npm run dev -- --port 3000
```

**Module not found**
```bash
rm -rf node_modules package-lock.json
npm install
```

### API Connection

**Cannot connect to backend**
- Ensure backend is running on port 8000
- Check .env file for correct API_URL
- Check CORS is enabled in FastAPI

## Next Steps

1. Upload sample images for detection
2. Check the dashboard for results
3. Explore analytics and reports
4. Review API documentation at http://localhost:8000/docs

## Environment Variables Reference

```
GROQ_API_KEY          # Your Groq API key
GROQ_MODEL            # Model to use (default: llama-3.3-70b-versatile)
DATABASE_URL          # SQLite path
API_PORT              # Backend port (default: 8000)
REACT_APP_API_URL     # Frontend API URL
```

## Support

For issues:
1. Check README.md
2. Check API docs: http://localhost:8000/docs
3. Open an issue on GitHub

Happy analyzing! 🚀
