@echo off
echo Starting GearMind AI API Server...
echo.
py -m uvicorn gear_api:app --reload --port 8000
