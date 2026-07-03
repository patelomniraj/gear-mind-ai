"""
═══════════════════════════════════════════════════════════
GEAR API v5.0 — FastAPI Backend for GearMind AI Dashboard
═══════════════════════════════════════════════════════════

Multi-model architecture: Helical (XGBoost), Spur (SVM), Bevel (XGBoost)
Each gear type has its own model, scaler, label encoder, RUL regressor,
and SHAP/LIME artifacts.

HOW TO RUN:
  pip install fastapi uvicorn
  uvicorn gear_api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
from scipy.stats import kurtosis as scipy_kurtosis
import pandas as pd
import joblib
import json
import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="GearMind AI API", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gear-mind-5p7hdk1tv-gear-build.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# LOAD ML ARTIFACTS — Helical (primary), Spur SVM, Bevel XGB
# ═══════════════════════════════════════════════════════════

print("⚙️  Loading ML models...")

# ── Helical (existing) ──────────────────────────────────
try:
    helical_model     = joblib.load('models/best_classifier.pkl')
    helical_rul       = joblib.load('models/rul_regressor.pkl')
    helical_scaler    = joblib.load('models/scaler.pkl')
    helical_scaler_rl = joblib.load('models/scaler_rul.pkl')
    helical_le        = joblib.load('models/label_encoder.pkl')
    comparison        = json.load(open('models/model_comparison.json'))
    print("   ✅ Helical models loaded")
except Exception as e:
    print(f"   ❌ Helical model error: {e}")
    helical_model = helical_rul = helical_scaler = helical_scaler_rl = helical_le = None
    comparison = {}

helical_shap = anomaly_model = None
try:
    helical_shap  = joblib.load('xai/shap_artifacts.pkl')
    anomaly_model = joblib.load('xai/anomaly_model.pkl')
    print("   ✅ Helical XAI loaded")
except:
    print("   ⚠  Helical XAI not available")

# ── Spur (SVM) ──────────────────────────────────────────
spur_model = spur_rul = spur_scaler = spur_scaler_rl = spur_le = spur_shap = None
try:
    spur_model     = joblib.load('models/spur_svm_classifier.pkl')
    spur_rul       = joblib.load('models/spur_svm_rul_regressor.pkl')
    spur_scaler    = joblib.load('models/spur_svm_scaler.pkl')
    spur_scaler_rl = joblib.load('models/spur_svm_scaler_rul.pkl')
    spur_le        = joblib.load('models/spur_svm_label_encoder.pkl')
    print("   ✅ Spur SVM models loaded")
except Exception as e:
    print(f"   ⚠  Spur models not available: {e}")

try:
    spur_shap = joblib.load('xai/spur_shap_artifacts.pkl')
    print("   ✅ Spur XAI loaded")
    # Verify required data exists
    if spur_shap:
        explainer = spur_shap.get('explainer')
        if explainer is None:
            # This is expected - KernelExplainer can't be pickled
            if 'X_background' in spur_shap and 'model' in spur_shap:
                print(f"      Explainer: Will be created on-demand (KernelExplainer can't be pickled)")
                print(f"      Background data shape: {spur_shap['X_background'].shape}")
                print(f"      Model: {type(spur_shap['model'])}")
            else:
                print("      ⚠️  Warning: Missing background data or model for explainer recreation")
        else:
            print(f"      Explainer type: {type(explainer)}")
        
        if 'X_sample' in spur_shap:
            print(f"      Sample data shape: {spur_shap['X_sample'].shape}")
    else:
        print("      ⚠️  Warning: Artifacts loaded but empty")
except Exception as e:
    print(f"   ⚠  Spur XAI not available: {e}")

# ── Bevel (XGBoost) ─────────────────────────────────────
bevel_model = bevel_rul = bevel_scaler = bevel_scaler_rl = bevel_le = bevel_shap = None
try:
    bevel_model     = joblib.load('models/bevel_classifier.pkl')
    bevel_rul       = joblib.load('models/bevel_rul_regressor.pkl')
    bevel_scaler    = joblib.load('models/bevel_scaler.pkl')
    bevel_scaler_rl = joblib.load('models/bevel_scaler_rul.pkl')
    bevel_le        = joblib.load('models/bevel_label_encoder.pkl')
    print("   ✅ Bevel models loaded")
except Exception as e:
    print(f"   ⚠  Bevel models not available: {e}")

try:
    bevel_shap = joblib.load('xai/bevel_shap_artifacts.pkl')
    print("   ✅ Bevel XAI loaded")
except Exception as e:
    print(f"   ⚠  Bevel XAI not available: {e}")

# ── Worm (Logistic Regression) ──────────────────────────
worm_model = worm_rul = worm_scaler = worm_scaler_rl = worm_le = worm_shap = None
try:
    worm_model     = joblib.load('models/worm_classifier.pkl')
    worm_rul       = joblib.load('models/worm_rul_regressor.pkl')
    worm_scaler    = joblib.load('models/worm_scaler.pkl')
    worm_scaler_rl = joblib.load('models/worm_scaler_rul.pkl')
    worm_le        = joblib.load('models/worm_label_encoder.pkl')
    print("   ✅ Worm models loaded")
except Exception as e:
    print(f"   ⚠  Worm models not available: {e}")

try:
    worm_shap = joblib.load('xai/worm_shap_artifacts.pkl')
    print("   ✅ Worm XAI loaded")
except Exception as e:
    print(f"   ⚠  Worm XAI not available: {e}")

# ── CMS Bearing (Random Forest) ─────────────────────────
cms_model = cms_scaler = None
cms_lifecycle_signal = None
cms_signal_index = [0]
CMS_WINDOW_SIZE = 2048
CMS_FS = 12000
try:
    cms_model  = joblib.load('models/cms_rf_fault_model.pkl')
    cms_scaler = joblib.load('models/cms_health_scaler.pkl')
    print("   ✅ CMS Bearing models loaded")
    # Load lifecycle signal for live vibration/FFT visualization
    try:
        inner_sig = np.load('data/inner_fault.npy')
        outer_sig = np.load('data/outer_fault.npy')
        healthy_seg = inner_sig[:len(inner_sig) // 4] * 0.1
        cms_lifecycle_signal = np.concatenate([healthy_seg, inner_sig[:len(inner_sig)//2], outer_sig[:len(outer_sig)//2]])
        total_windows = len(cms_lifecycle_signal) // CMS_WINDOW_SIZE
        print(f"   ✅ CMS vibration signal loaded: {total_windows} windows")
    except Exception as e:
        print(f"   ⚠  CMS vibration data not available (signal viz disabled): {e}")
except Exception as e:
    print(f"   ⚠  CMS Bearing models not available: {e}")

# ═══════════════════════════════════════════════════════════
# FEATURE COLUMNS PER GEAR TYPE
# ═══════════════════════════════════════════════════════════

HELICAL_FEATURES = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]

SPUR_FEATURES = [
    'Speed_RPM', 'Torque_Nm', 'Vibration_mm_s',
    'Temperature_C', 'Shock_Load_g', 'Noise_dB'
]

BEVEL_FEATURES = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]

WORM_FEATURES = [
    'Worm_RPM', 'Input_Torque', 'Output_Torque', 'Motor_Current',
    'Oil_Temp', 'Ambient_Temp', 'Axial_Vib', 'Radial_Vib',
    'Cu_PPM', 'Fe_PPM', 'Efficiency_Calc', 'Friction_Coeff', 'Backlash'
]

CMS_FEATURES = ['rms', 'kurtosis', 'fft_energy', 'health_index']
CMS_LABELS = {0: 'Healthy', 1: 'Inner Race', 2: 'Ball', 3: 'Outer Race'}

# Backward-compat alias
FEATURE_COLS = HELICAL_FEATURES

SAFE_RANGES = {
    'Load (kN)':            (10, 80),
    'Torque (Nm)':          (50, 400),
    'Vibration RMS (mm/s)': (0, 6),
    'Temperature (°C)':     (40, 95),
    'Wear (mm)':            (0, 1.0),
    'Lubrication Index':    (0.5, 1.0),
    'Efficiency (%)':       (93, 99),
    'Cycles in Use':        (0, 100000),
}

GEAR_CONFIGS = {
    "Helical": {
        "icon": "⚙️", "color": "#2563eb",
        "spec": "Helix Angle: 20° | Module: 4 | Teeth: 32 | Pressure Angle: 14.5°",
        "description": "High-efficiency helical gear — smooth, quiet, ideal for high-speed industrial drives",
        "vib_limit": 6.0, "temp_limit": 95.0, "wear_limit": 1.0, "lube_limit": 0.5, "eff_limit": 93.0,
        "daily_cycles": 8000,
        "repair_cost": 45000, "overhaul_cost": 120000, "failure_cost": 450000,
        "units": {
            "HG-01 (Standard — Healthy)":       {"load":48.0,"torque":201.6,"vib":2.3,"temp":72.0,"wear":0.20,"lube":0.82,"eff":96.8,"cycles":18000},
            "HG-03 (Heavy Duty — Major Fault)":  {"load":74.0,"torque":310.8,"vib":12.4,"temp":108.0,"wear":1.80,"lube":0.21,"eff":85.2,"cycles":84200},
            "HG-05 (Standard — Healthy)":        {"load":53.0,"torque":222.6,"vib":3.1,"temp":78.0,"wear":0.35,"lube":0.71,"eff":95.3,"cycles":28000},
            "HG-07 (Precision — Minor Fault)":   {"load":81.0,"torque":340.2,"vib":7.1,"temp":91.0,"wear":1.10,"lube":0.42,"eff":90.1,"cycles":52000},
            "HG-12 (New — Healthy)":             {"load":44.0,"torque":184.8,"vib":1.8,"temp":68.0,"wear":0.15,"lube":0.88,"eff":97.4,"cycles":12000},
        },
        "fault_types": ["Surface Pitting", "Wear Fatigue", "Thermal Degradation"],
        "teammate": "Isha Patel — Helical Gear Module"
    },
    "Spur": {
        "icon": "🔧", "color": "#10b981",
        "spec": "Pressure Angle: 20° | Module: 5 | Teeth: 28 | Face Width: 50mm",
        "description": "Standard spur gear — straight teeth, cost-effective, medium-speed drives",
        "vib_limit": 8.0, "temp_limit": 90.0, "wear_limit": 1.2, "lube_limit": 0.45, "eff_limit": 92.0,
        "daily_cycles": 7000,
        "repair_cost": 38000, "overhaul_cost": 95000, "failure_cost": 380000,
        "units": {
            "SG-02 (Standard — Healthy)":        {"speed":1200,"torque":180,"vib":3.2,"temp":70.0,"shock":1.2,"noise":62},
            "SG-04 (Industrial — Failure)":      {"speed":2800,"torque":420,"vib":14.1,"temp":102.0,"shock":4.8,"noise":88},
            "SG-06 (Standard — Healthy)":        {"speed":1500,"torque":210,"vib":4.1,"temp":76.0,"shock":1.8,"noise":65},
            "SG-08 (Heavy — Failure Risk)":      {"speed":2200,"torque":340,"vib":9.3,"temp":88.0,"shock":3.5,"noise":79},
            "SG-14 (New — Healthy)":             {"speed":900,"torque":145,"vib":2.1,"temp":65.0,"shock":0.9,"noise":58},
        },
        "fault_types": ["Tooth Fracture", "General Wear", "Overload Vibration"],
        "teammate": "Spur Gear Module — SVM Classifier"
    },
    "Bevel": {
        "icon": "🔩", "color": "#a78bfa",
        "spec": "Pressure Angle: 20° | Module: 4 | Teeth: 18 | Shaft Angle: 90° | AGMA 2003-B97",
        "description": "Straight bevel gear (miter) — right-angle drives, high-torque applications",
        "vib_limit": 7.0, "temp_limit": 90.0, "wear_limit": 0.9, "lube_limit": 0.5, "eff_limit": 91.0,
        "daily_cycles": 7500,
        "repair_cost": 52000, "overhaul_cost": 140000, "failure_cost": 520000,
        "units": {
            "BG-01 (Miter — Healthy)":           {"load":42.0,"torque":168.0,"vib":2.5,"temp":70.0,"wear":0.18,"lube":0.85,"eff":95.2,"cycles":15000},
            "BG-03 (Heavy Duty — Major Fault)":  {"load":72.0,"torque":285.0,"vib":13.5,"temp":112.0,"wear":2.00,"lube":0.19,"eff":82.5,"cycles":88000},
            "BG-05 (Standard — Healthy)":        {"load":48.0,"torque":192.0,"vib":3.4,"temp":76.0,"wear":0.30,"lube":0.72,"eff":94.0,"cycles":25000},
            "BG-07 (Precision — Minor Fault)":   {"load":78.0,"torque":312.0,"vib":8.2,"temp":94.0,"wear":1.15,"lube":0.38,"eff":88.5,"cycles":55000},
            "BG-10 (New — Healthy)":             {"load":38.0,"torque":152.0,"vib":1.9,"temp":65.0,"wear":0.12,"lube":0.90,"eff":96.5,"cycles":10000},
        },
        "fault_types": ["Cone Surface Pitting", "Tooth Root Fracture", "Axial Misalignment", "Heel-Toe Wear"],
        "teammate": "Bevel Gear Module — AGMA 2003-B97"
    },
    "Worm": {
        "icon": "🌀", "color": "#f59e0b",
        "spec": "Ratio: 30:1 | Lead Angle: 5.2° | Worm Threads: 2 | Wheel Teeth: 60",
        "description": "High-ratio worm gear — self-locking, high torque multiplication, compact design",
        "vib_limit": 6.0, "temp_limit": 120.0, "wear_limit": 1.5, "lube_limit": 0.4, "eff_limit": 75.0,
        "daily_cycles": 6000,
        "repair_cost": 58000, "overhaul_cost": 155000, "failure_cost": 580000,
        "units": {
            "WG-01 (Standard — Healthy)":        {"rpm":1321,"in_torque":86.8,"out_torque":2951,"current":26.0,"oil_temp":56.5,"amb_temp":24.6,"ax_vib":5.2,"rad_vib":2.3,"cu_ppm":25,"fe_ppm":9,"eff":85.0,"friction":0.031,"backlash":0.115},
            "WG-03 (Heavy Duty — Major Fault)":  {"rpm":3467,"in_torque":78.1,"out_torque":2311,"current":27.8,"oil_temp":155.0,"amb_temp":23.5,"ax_vib":5.8,"rad_vib":2.1,"cu_ppm":91,"fe_ppm":16,"eff":74.0,"friction":0.055,"backlash":0.158},
            "WG-05 (Standard — Healthy)":        {"rpm":2876,"in_torque":69.4,"out_torque":2367,"current":21.1,"oil_temp":84.9,"amb_temp":30.1,"ax_vib":4.5,"rad_vib":2.2,"cu_ppm":80,"fe_ppm":14,"eff":85.3,"friction":0.024,"backlash":0.098},
            "WG-07 (Precision — Minor Fault)":   {"rpm":2516,"in_torque":47.9,"out_torque":1547,"current":19.0,"oil_temp":63.5,"amb_temp":24.9,"ax_vib":3.9,"rad_vib":1.3,"cu_ppm":44,"fe_ppm":17,"eff":80.7,"friction":0.042,"backlash":0.131},
            "WG-12 (New — Healthy)":             {"rpm":1057,"in_torque":64.1,"out_torque":2242,"current":19.8,"oil_temp":44.4,"amb_temp":32.4,"ax_vib":3.9,"rad_vib":2.0,"cu_ppm":29,"fe_ppm":6,"eff":87.4,"friction":0.021,"backlash":0.088},
        },
        "fault_types": ["Thermal Breakdown", "General Degradation", "Bearing Instability"],
        "teammate": "Worm Gear Module — Logistic Regression"
    },
    "Bearing": {
        "icon": "🔴", "color": "#ef4444",
        "spec": "Type: Deep Groove Ball | Bore: 25mm | OD: 52mm | CWRU 6205-2RS",
        "description": "Bearing CMS — vibration-feature fault detection using CWRU dataset, Random Forest classifier",
        "vib_limit": 0.5, "temp_limit": 85.0, "wear_limit": 0.5, "lube_limit": 0.5, "eff_limit": 90.0,
        "daily_cycles": 12000,
        "repair_cost": 15000, "overhaul_cost": 45000, "failure_cost": 180000,
        "units": {
            "BR-01 (Normal — Healthy)":           {"rms":0.03, "kurtosis":2.9, "fft_energy":1200.0},
            "BR-03 (Inner Race — Fault)":         {"rms":0.45, "kurtosis":6.8, "fft_energy":58000.0},
            "BR-05 (Ball — Fault)":               {"rms":0.38, "kurtosis":5.2, "fft_energy":42000.0},
            "BR-07 (Outer Race — Fault)":         {"rms":0.52, "kurtosis":7.5, "fft_energy":72000.0},
            "BR-10 (New — Healthy)":              {"rms":0.02, "kurtosis":2.8, "fft_energy":800.0},
        },
        "fault_types": ["Inner Race Fault", "Ball Fault", "Outer Race Fault"],
        "teammate": "CMS Bearing Module — Random Forest (CWRU)"
    },
}

DB_PATH = "gear_history.db"

# ═══════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════

class SensorInput(BaseModel):
    # Helical/Bevel fields
    load: float = 48.0
    torque: float = 201.6
    vib: float = 2.3
    temp: float = 72.0
    wear: float = 0.20
    lube: float = 0.82
    eff: float = 96.8
    cycles: int = 18000
    
    # Worm gear fields (optional)
    rpm: Optional[float] = None
    in_torque: Optional[float] = None
    out_torque: Optional[float] = None
    current: Optional[float] = None
    oil_temp: Optional[float] = None
    amb_temp: Optional[float] = None
    ax_vib: Optional[float] = None
    rad_vib: Optional[float] = None
    cu_ppm: Optional[float] = None
    fe_ppm: Optional[float] = None
    friction: Optional[float] = None
    backlash: Optional[float] = None
    
    gear_type: str = "Helical"

class SpurSensorInput(BaseModel):
    speed: float = 1200.0
    torque: float = 180.0
    vib: float = 3.2
    temp: float = 70.0
    shock: float = 1.2
    noise: float = 62.0

class ChatRequest(BaseModel):
    question: str
    gear_id: str = "HG-01"
    sensor_values: dict
    chat_history: list = []

class ReportRequest(BaseModel):
    gear_id: str = "HG-01"
    sensor_values: dict
    gear_type: str = "Helical"

class OptimizeRequest(BaseModel):
    sensor_values: dict
    locks: dict
    target_probability: float = 20.0

class HistoryEntry(BaseModel):
    gear_type: str
    gear_unit: str
    fault_label: str
    confidence: float
    health_score: int
    rul_cycles: int
    sensor_values: dict
    operator_name: Optional[str] = "Unknown"
    shift: Optional[str] = "Day"
    role: Optional[str] = "Operator"

# ═══════════════════════════════════════════════════════════
# PREDICTION FUNCTIONS
# ═══════════════════════════════════════════════════════════

def predict_helical(sensor_dict: dict) -> dict:
    """Predict using Helical XGBoost model."""
    input_arr    = np.array([sensor_dict[f] for f in HELICAL_FEATURES])
    input_scaled = helical_scaler.transform(input_arr.reshape(1, -1))

    pred_enc   = helical_model.predict(input_scaled)[0]
    pred_label = helical_le.inverse_transform([pred_enc])[0]
    pred_proba = helical_model.predict_proba(input_scaled)[0]
    confidence = float(pred_proba.max())
    class_probs = dict(zip([str(c) for c in helical_le.classes_], [float(p) for p in pred_proba]))

    rul_scaled = helical_scaler_rl.transform(input_arr.reshape(1, -1))
    rul_cycles = max(0, int(helical_rul.predict(rul_scaled)[0]))

    shap_values = {}
    if helical_shap:
        try:
            explainer = helical_shap['explainer']
            sv = explainer.shap_values(input_scaled)
            if hasattr(sv, 'ndim') and sv.ndim == 3:
                sv_for_class = sv[0, :, pred_enc]
            elif isinstance(sv, list):
                sv_for_class = sv[min(pred_enc, len(sv)-1)][0]
            else:
                sv_for_class = sv[0]
            no_fault_idx = list(helical_le.classes_).index("No Fault") if "No Fault" in list(helical_le.classes_) else -1
            if pred_enc == no_fault_idx:
                sv_for_class = -sv_for_class
            shap_values = dict(zip(HELICAL_FEATURES, [float(v) for v in sv_for_class]))
        except:
            shap_values = {}

    anomaly_score, anomaly_status = 0.0, "UNKNOWN"
    if anomaly_model:
        try:
            score  = anomaly_model.decision_function(input_scaled)[0]
            status = anomaly_model.predict(input_scaled)[0]
            anomaly_score  = float(score)
            anomaly_status = "NORMAL" if status == 1 else "SUSPICIOUS"
        except:
            pass

    violations = {}
    for feat, (low, high) in SAFE_RANGES.items():
        val = sensor_dict.get(feat)
        if val is not None and (val < low or val > high):
            violations[feat] = {
                'value': val, 'safe_min': low, 'safe_max': high,
                'severity': 'CRITICAL' if (val < low * 0.8 or val > high * 1.2) else 'WARNING'
            }

    return {
        'fault_label': pred_label, 'confidence': confidence,
        'class_probs': class_probs, 'rul_cycles': rul_cycles,
        'shap_values': shap_values, 'anomaly_score': anomaly_score,
        'anomaly_status': anomaly_status, 'violations': violations,
        'sensor_values': sensor_dict, 'gear_type': 'Helical',
        'feature_names': HELICAL_FEATURES,
    }


def predict_spur(sensor_dict: dict) -> dict:
    """Predict using Spur SVM model."""
    if spur_model is None:
        raise HTTPException(status_code=503, detail="Spur model not loaded. Run train_spur_svm.py first.")

    # Map from generic keys if needed
    speed   = sensor_dict.get('Speed_RPM',      sensor_dict.get('speed', 1200.0))
    torque  = sensor_dict.get('Torque_Nm',      sensor_dict.get('torque', 180.0))
    vib     = sensor_dict.get('Vibration_mm_s', sensor_dict.get('vib', 3.2))
    temp    = sensor_dict.get('Temperature_C',  sensor_dict.get('temp', 70.0))
    shock   = sensor_dict.get('Shock_Load_g',   sensor_dict.get('shock', 1.2))
    noise   = sensor_dict.get('Noise_dB',       sensor_dict.get('noise', 62.0))

    input_arr    = np.array([[speed, torque, vib, temp, shock, noise]])
    input_scaled = spur_scaler.transform(input_arr)

    pred_enc   = spur_model.predict(input_scaled)[0]
    pred_label = spur_le.inverse_transform([pred_enc])[0]
    pred_proba = spur_model.predict_proba(input_scaled)[0]
    confidence = float(pred_proba.max())
    class_probs = dict(zip([str(c) for c in spur_le.classes_], [float(p) for p in pred_proba]))

    rul_scaled = spur_scaler_rl.transform(input_arr)
    rul_cycles = max(0, int(spur_rul.predict(rul_scaled)[0]))

    # Health score: No Failure → high score
    no_fail_idx = list(spur_le.classes_).index('No Failure') if 'No Failure' in spur_le.classes_ else 0
    health_score = int(pred_proba[no_fail_idx] * 100)

    shap_values = {}
    if spur_shap:
        try:
            print(f"   🔍 Computing SHAP for Spur gear...")
            
            # Check if we have a pre-computed explainer or need to create one
            explainer = spur_shap.get('explainer')
            
            if explainer is None:
                # KernelExplainer can't be pickled, so we recreate it on-demand
                print(f"      Creating KernelExplainer on-demand...")
                import shap
                
                # Get background data and model from artifacts
                X_background = spur_shap.get('X_background')
                model = spur_shap.get('model')
                
                if X_background is None or model is None:
                    print(f"      ⚠️  Missing background data or model in artifacts")
                    shap_values = {}
                else:
                    explainer = shap.KernelExplainer(model.predict_proba, X_background)
                    print(f"      ✅ Explainer created")
            
            if explainer is not None:
                print(f"      Explainer type: {type(explainer)}")
                print(f"      Input shape: {input_scaled.shape}")
                
                # LinearExplainer doesn't accept nsamples parameter
                explainer_type = type(explainer).__name__
                if 'Linear' in explainer_type:
                    sv = explainer.shap_values(input_scaled)
                else:
                    sv = explainer.shap_values(input_scaled, nsamples=50)
                    
                print(f"      SHAP output type: {type(sv)}")
                
                # Handle different SHAP output formats
                if isinstance(sv, list):
                    print(f"      SHAP is list with {len(sv)} elements")
                    sv_for_class = sv[pred_enc][0] if len(sv) > pred_enc else sv[0][0]
                elif hasattr(sv, 'ndim') and sv.ndim == 3:
                    print(f"      SHAP is 3D array: {sv.shape}")
                    sv_for_class = sv[0, :, pred_enc]
                elif hasattr(sv, 'ndim') and sv.ndim == 2:
                    print(f"      SHAP is 2D array: {sv.shape}")
                    sv_for_class = sv[0]
                else:
                    print(f"      SHAP is 1D or other format")
                    sv_for_class = sv
                
                print(f"      SHAP values shape: {np.array(sv_for_class).shape}")
                
                # For "No Failure" class, invert SHAP values (higher = better)
                no_fail_idx = list(spur_le.classes_).index('No Failure') if 'No Failure' in spur_le.classes_ else -1
                if pred_enc == no_fail_idx:
                    sv_for_class = -sv_for_class
                
                shap_values = dict(zip(SPUR_FEATURES, [float(v) for v in sv_for_class]))
                print(f"      ✅ SHAP computed: {len(shap_values)} features")
            
        except Exception as e:
            print(f"   ❌ Spur SHAP computation failed: {e}")
            import traceback
            traceback.print_exc()
            shap_values = {}
    else:
        print(f"   ⚠️  Spur SHAP not available: artifacts not loaded")

    # Basic violation checks for spur
    violations = {}
    spur_limits = {
        'Vibration_mm_s': (0, 8.0), 'Temperature_C': (40, 90),
        'Noise_dB': (50, 85), 'Shock_Load_g': (0, 4.0)
    }
    spur_vals = {'Speed_RPM': speed, 'Torque_Nm': torque, 'Vibration_mm_s': vib,
                 'Temperature_C': temp, 'Shock_Load_g': shock, 'Noise_dB': noise}
    for feat, (lo, hi) in spur_limits.items():
        val = spur_vals[feat]
        if val < lo or val > hi:
            violations[feat] = {
                'value': val, 'safe_min': lo, 'safe_max': hi,
                'severity': 'CRITICAL' if (val < lo * 0.8 or val > hi * 1.2) else 'WARNING'
            }

    full_sensor = {'Speed_RPM': speed, 'Torque_Nm': torque, 'Vibration_mm_s': vib,
                   'Temperature_C': temp, 'Shock_Load_g': shock, 'Noise_dB': noise}
    return {
        'fault_label': pred_label, 'confidence': confidence,
        'class_probs': class_probs, 'rul_cycles': rul_cycles,
        'health_score': health_score,
        'shap_values': shap_values, 'anomaly_score': 0.0,
        'anomaly_status': 'NORMAL' if pred_label == 'No Failure' else 'SUSPICIOUS',
        'violations': violations, 'sensor_values': full_sensor,
        'gear_type': 'Spur', 'feature_names': SPUR_FEATURES,
    }


def predict_bevel(sensor_dict: dict) -> dict:
    """Predict using Bevel XGBoost model."""
    if bevel_model is None:
        raise HTTPException(status_code=503, detail="Bevel model not loaded. Run train_bevel_model.py first.")

    input_arr    = np.array([sensor_dict[f] for f in BEVEL_FEATURES])
    input_scaled = bevel_scaler.transform(input_arr.reshape(1, -1))

    pred_enc   = bevel_model.predict(input_scaled)[0]
    pred_label = bevel_le.inverse_transform([pred_enc])[0]
    pred_proba = bevel_model.predict_proba(input_scaled)[0]
    confidence = float(pred_proba.max())
    class_probs = dict(zip([str(c) for c in bevel_le.classes_], [float(p) for p in pred_proba]))

    rul_scaled = bevel_scaler_rl.transform(input_arr.reshape(1, -1))
    rul_cycles = max(0, int(bevel_rul.predict(rul_scaled)[0]))

    shap_values = {}
    if bevel_shap:
        try:
            explainer = bevel_shap['explainer']
            sv = explainer.shap_values(input_scaled)
            if hasattr(sv, 'ndim') and sv.ndim == 3:
                sv_for_class = sv[0, :, pred_enc]
            elif isinstance(sv, list):
                sv_for_class = sv[min(pred_enc, len(sv)-1)][0]
            else:
                sv_for_class = sv[0]
            no_fault_idx = list(bevel_le.classes_).index("No Fault") if "No Fault" in list(bevel_le.classes_) else -1
            if pred_enc == no_fault_idx:
                sv_for_class = -sv_for_class
            shap_values = dict(zip(BEVEL_FEATURES, [float(v) for v in sv_for_class]))
        except:
            shap_values = {}

    violations = {}
    for feat, (low, high) in SAFE_RANGES.items():
        val = sensor_dict.get(feat)
        if val is not None and (val < low or val > high):
            violations[feat] = {
                'value': val, 'safe_min': low, 'safe_max': high,
                'severity': 'CRITICAL' if (val < low * 0.8 or val > high * 1.2) else 'WARNING'
            }

    return {
        'fault_label': pred_label, 'confidence': confidence,
        'class_probs': class_probs, 'rul_cycles': rul_cycles,
        'shap_values': shap_values, 'anomaly_score': 0.0,
        'anomaly_status': 'NORMAL' if pred_label == 'No Fault' else 'SUSPICIOUS',
        'violations': violations, 'sensor_values': sensor_dict,
        'gear_type': 'Bevel', 'feature_names': BEVEL_FEATURES,
    }


def predict_worm(sensor_dict: dict) -> dict:
    """Predict using Worm Logistic Regression model."""
    if worm_model is None:
        raise HTTPException(status_code=503, detail="Worm model not loaded. Run train_worm_model.py first.")

    # Map from generic keys if needed
    rpm         = sensor_dict.get('Worm_RPM',        sensor_dict.get('rpm', 1321.0))
    in_torque   = sensor_dict.get('Input_Torque',    sensor_dict.get('in_torque', 86.8))
    out_torque  = sensor_dict.get('Output_Torque',   sensor_dict.get('out_torque', 2951.0))
    current     = sensor_dict.get('Motor_Current',   sensor_dict.get('current', 26.0))
    oil_temp    = sensor_dict.get('Oil_Temp',        sensor_dict.get('oil_temp', 56.5))
    amb_temp    = sensor_dict.get('Ambient_Temp',    sensor_dict.get('amb_temp', 24.6))
    ax_vib      = sensor_dict.get('Axial_Vib',       sensor_dict.get('ax_vib', 5.2))
    rad_vib     = sensor_dict.get('Radial_Vib',      sensor_dict.get('rad_vib', 2.3))
    cu_ppm      = sensor_dict.get('Cu_PPM',          sensor_dict.get('cu_ppm', 25.0))
    fe_ppm      = sensor_dict.get('Fe_PPM',          sensor_dict.get('fe_ppm', 9.0))
    eff         = sensor_dict.get('Efficiency_Calc', sensor_dict.get('eff', 85.0))
    friction    = sensor_dict.get('Friction_Coeff',  sensor_dict.get('friction', 0.031))
    backlash    = sensor_dict.get('Backlash',        sensor_dict.get('backlash', 0.115))

    input_arr    = np.array([[rpm, in_torque, out_torque, current, oil_temp, amb_temp,
                              ax_vib, rad_vib, cu_ppm, fe_ppm, eff, friction, backlash]])
    input_scaled = worm_scaler.transform(input_arr)

    pred_enc   = worm_model.predict(input_scaled)[0]
    pred_label = worm_le.inverse_transform([pred_enc])[0]
    pred_proba = worm_model.predict_proba(input_scaled)[0]
    confidence = float(pred_proba.max())
    class_probs = dict(zip([str(c) for c in worm_le.classes_], [float(p) for p in pred_proba]))

    rul_scaled = worm_scaler_rl.transform(input_arr)
    rul_cycles = max(0, int(worm_rul.predict(rul_scaled)[0]))

    # Health score: No Fault → high score
    no_fault_idx = list(worm_le.classes_).index('No Fault') if 'No Fault' in worm_le.classes_ else 0
    health_score = int(pred_proba[no_fault_idx] * 100)

    shap_values = {}
    if worm_shap:
        try:
            explainer = worm_shap['explainer']
            sv = explainer.shap_values(input_scaled)
            if hasattr(sv, 'ndim') and sv.ndim == 3:
                sv_for_class = sv[0, :, pred_enc]
            elif isinstance(sv, list):
                sv_for_class = sv[min(pred_enc, len(sv)-1)][0]
            else:
                sv_for_class = sv[0]
            no_fault_idx = list(worm_le.classes_).index("No Fault") if "No Fault" in list(worm_le.classes_) else -1
            if pred_enc == no_fault_idx:
                sv_for_class = -sv_for_class
            shap_values = dict(zip(WORM_FEATURES, [float(v) for v in sv_for_class]))
        except:
            shap_values = {}

    # Basic violation checks for worm
    violations = {}
    worm_limits = {
        'Oil_Temp': (40, 120), 'Axial_Vib': (0, 6.0), 'Radial_Vib': (0, 3.0),
        'Cu_PPM': (0, 100), 'Fe_PPM': (0, 20), 'Friction_Coeff': (0.02, 0.06)
    }
    worm_vals = {'Worm_RPM': rpm, 'Input_Torque': in_torque, 'Output_Torque': out_torque,
                 'Motor_Current': current, 'Oil_Temp': oil_temp, 'Ambient_Temp': amb_temp,
                 'Axial_Vib': ax_vib, 'Radial_Vib': rad_vib, 'Cu_PPM': cu_ppm, 'Fe_PPM': fe_ppm,
                 'Efficiency_Calc': eff, 'Friction_Coeff': friction, 'Backlash': backlash}
    for feat, (lo, hi) in worm_limits.items():
        val = worm_vals[feat]
        if val < lo or val > hi:
            violations[feat] = {
                'value': val, 'safe_min': lo, 'safe_max': hi,
                'severity': 'CRITICAL' if (val < lo * 0.8 or val > hi * 1.2) else 'WARNING'
            }

    full_sensor = worm_vals
    return {
        'fault_label': pred_label, 'confidence': confidence,
        'class_probs': class_probs, 'rul_cycles': rul_cycles,
        'health_score': health_score,
        'shap_values': shap_values, 'anomaly_score': 0.0,
        'anomaly_status': 'NORMAL' if pred_label == 'No Fault' else 'SUSPICIOUS',
        'violations': violations, 'sensor_values': full_sensor,
        'gear_type': 'Worm', 'feature_names': WORM_FEATURES,
    }


def predict_bearing(sensor_dict: dict) -> dict:
    """Predict bearing health from extracted vibration features (RMS, Kurtosis, FFT Energy)."""
    if cms_model is None or cms_scaler is None:
        raise HTTPException(status_code=503, detail="CMS Bearing model not loaded.")

    rms_val  = float(sensor_dict.get('rms', 0.03))
    kurt_val = float(sensor_dict.get('kurtosis', 2.9))
    fft_val  = float(sensor_dict.get('fft_energy', 1200.0))

    # Compute health index via scaler
    row = pd.DataFrame([{'rms': rms_val, 'fft_energy': fft_val}])
    row[['rms_n', 'fft_n']] = cms_scaler.transform(row[['rms', 'fft_energy']])
    health_index = 0.5 * float(row['rms_n']) + 0.5 * float(row['fft_n'])
    health = max(0, min(100, 100 * (1 - health_index)))

    X = pd.DataFrame([{'rms': rms_val, 'kurtosis': kurt_val,
                        'fft_energy': fft_val, 'health_index': health_index}])
    fault_int = cms_model.predict(X)[0]
    fault = CMS_LABELS[fault_int]

    explanation = ''
    if rms_val > 0.3: explanation += 'High vibration detected. '
    if kurt_val > 4:  explanation += 'Impulsive faults detected. '
    if not explanation: explanation = 'Normal operation.'

    anomaly = bool(health < 70)
    class_probs = {}
    try:
        probs = cms_model.predict_proba(X)[0]
        class_probs = {CMS_LABELS[i]: float(p) for i, p in enumerate(probs)}
    except:
        pass

    # Violation checks for bearing features
    violations = {}
    bearing_limits = {'rms': (0, 0.4), 'kurtosis': (2.0, 5.0), 'fft_energy': (0, 50000)}
    for feat, (lo, hi) in bearing_limits.items():
        val = sensor_dict.get(feat, 0)
        if val < lo or val > hi:
            violations[feat] = {
                'value': val, 'safe_min': lo, 'safe_max': hi,
                'severity': 'CRITICAL' if (val < lo * 0.8 or val > hi * 1.2) else 'WARNING'
            }

    return {
        'health': float(health),
        'health_score': int(health),
        'fault_label': fault,
        'confidence': float(max(class_probs.values())) if class_probs else 0.0,
        'class_probs': class_probs,
        'rul_cycles': int(health * 500),
        'explanation': explanation,
        'shap_values': {},
        'anomaly': anomaly,
        'anomaly_score': 0.0,
        'anomaly_status': 'NORMAL' if not anomaly else 'SUSPICIOUS',
        'violations': violations,
        'sensor_values': {'rms': rms_val, 'kurtosis': kurt_val, 'fft_energy': fft_val, 'health_index': health_index},
        'gear_type': 'Bearing',
        'feature_names': CMS_FEATURES,
    }


def predict_gear_health(sensor_dict: dict, gear_type: str = "Helical") -> dict:
    """Unified prediction dispatcher."""
    gt = gear_type.strip().lower()
    if gt == "spur":
        return predict_spur(sensor_dict)
    elif gt == "bevel":
        return predict_bevel(sensor_dict)
    elif gt == "worm":
        return predict_worm(sensor_dict)
    elif gt == "bearing":
        return predict_bearing(sensor_dict)
    else:
        return predict_helical(sensor_dict)


def sensor_input_to_dict(s: SensorInput) -> dict:
    # For worm gear, return worm-specific fields
    if s.gear_type.lower() == "worm":
        return {
            'rpm': s.rpm,
            'in_torque': s.in_torque,
            'out_torque': s.out_torque,
            'current': s.current,
            'oil_temp': s.oil_temp,
            'amb_temp': s.amb_temp,
            'ax_vib': s.ax_vib,
            'rad_vib': s.rad_vib,
            'cu_ppm': s.cu_ppm,
            'fe_ppm': s.fe_ppm,
            'eff': s.eff,
            'friction': s.friction,
            'backlash': s.backlash,
        }
    # For helical/bevel, return standard fields
    return {
        'Load (kN)': s.load, 'Torque (Nm)': s.torque,
        'Vibration RMS (mm/s)': s.vib, 'Temperature (°C)': s.temp,
        'Wear (mm)': s.wear, 'Lubrication Index': s.lube,
        'Efficiency (%)': s.eff, 'Cycles in Use': s.cycles,
    }

def _opt_predict_prob(raw_vals):
    sv = dict(zip(FEATURE_COLS, raw_vals))
    p = predict_helical(sv)
    fault_map = {'No Fault': 0.05, 'Minor Fault': 0.55, 'Major Fault': 0.92}
    return fault_map.get(p['fault_label'], 0.5) * 100 + (1 - p['confidence']) * 10

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # Always attempt to add new columns (gracefully ignore if they exist)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gear_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT NOT NULL,
            gear_type     TEXT,
            gear_unit     TEXT,
            fault_label   TEXT,
            confidence    REAL,
            health_score  INTEGER,
            rul_cycles    INTEGER,
            load_kn       REAL,
            torque_nm     REAL,
            vibration     REAL,
            temperature   REAL,
            wear          REAL,
            lubrication   REAL,
            efficiency    REAL,
            cycles        INTEGER,
            operator_name TEXT DEFAULT 'Unknown',
            shift         TEXT DEFAULT 'Day',
            role          TEXT DEFAULT 'Operator'
        )
    """)
    # Add new columns if they don't exist (migration)
    for col, coldef in [
        ("operator_name", "TEXT DEFAULT 'Unknown'"),
        ("shift",         "TEXT DEFAULT 'Day'"),
        ("role",          "TEXT DEFAULT 'Operator'"),
    ]:
        try:
            cur.execute(f"ALTER TABLE gear_log ADD COLUMN {col} {coldef}")
        except:
            pass  # Column already exists
    con.commit()
    con.close()

init_db()

# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {"message": "GearMind AI API v5.0 — Multi-Model Architecture", "status": "running"}


@app.post("/api/predict")
def api_predict(sensors: SensorInput):
    """Unified prediction — routes to correct model based on gear_type."""
    sensor_dict = sensor_input_to_dict(sensors)
    if sensors.gear_type.lower() == "spur":
        # For spur, frontend sends helical-format dict; convert to spur expected fields
        # The gear_type drives the routing but sliders still send helical-mapped values
        # We pass them through and predict_spur handles key aliasing
        result = predict_spur(sensor_dict)
    elif sensors.gear_type.lower() == "bevel":
        result = predict_bevel(sensor_dict)
    elif sensors.gear_type.lower() == "worm":
        result = predict_worm(sensor_dict)
    else:
        result = predict_helical(sensor_dict)

    # Compute unified health score for helical/bevel
    if 'health_score' not in result:
        cm = result.get('class_probs', {})
        no_fault_prob = cm.get('No Fault', cm.get('No Failure', 0.5))
        result['health_score'] = int(no_fault_prob * 100)

    return result


@app.post("/api/predict-spur")
def api_predict_spur(sensors: SpurSensorInput):
    """Dedicated Spur SVM predict endpoint."""
    sensor_dict = {
        'Speed_RPM': sensors.speed, 'Torque_Nm': sensors.torque,
        'Vibration_mm_s': sensors.vib, 'Temperature_C': sensors.temp,
        'Shock_Load_g': sensors.shock, 'Noise_dB': sensors.noise,
    }
    return predict_spur(sensor_dict)


@app.post("/api/predict-bearing")
def api_predict_bearing(sensors: dict = {"rms": 0.03, "kurtosis": 2.9, "fft_energy": 1200.0}):
    """CMS Bearing: predict from extracted vibration features."""
    return predict_bearing(sensors)


@app.get("/api/bearing-signal")
def api_bearing_signal():
    """Return live vibration waveform (next window from lifecycle signal)."""
    if cms_lifecycle_signal is None:
        raise HTTPException(status_code=503, detail="CMS vibration data not loaded.")
    total = len(cms_lifecycle_signal) // CMS_WINDOW_SIZE
    if cms_signal_index[0] >= total:
        cms_signal_index[0] = 0
    start = cms_signal_index[0] * CMS_WINDOW_SIZE
    window = cms_lifecycle_signal[start:start + CMS_WINDOW_SIZE]
    cms_signal_index[0] += 1

    # Vibration waveform (downsample to 256 points for frontend)
    step = max(1, len(window) // 256)
    samples = window[::step].tolist()
    time_axis = [i / CMS_FS for i in range(0, len(window), step)]

    # FFT spectrum
    fft_vals = np.fft.rfft(window)
    mag = np.abs(fft_vals).tolist()
    freqs = np.fft.rfftfreq(len(window), d=1/CMS_FS).tolist()

    # Downsample FFT too
    fft_step = max(1, len(mag) // 256)
    mag_ds = mag[::fft_step]
    freqs_ds = freqs[::fft_step]

    # Also compute features from this window for context
    from scipy.stats import kurtosis as scipy_kurtosis
    rms_val = float(np.sqrt(np.mean(window ** 2)))
    kurt_val = float(scipy_kurtosis(window, fisher=False))
    fft_energy = float(np.sum(np.abs(fft_vals) ** 2))

    return {
        "window_index": cms_signal_index[0] - 1,
        "total_windows": total,
        "waveform": {"time": time_axis, "amplitude": samples},
        "fft": {"frequency": freqs_ds, "magnitude": mag_ds},
        "features": {"rms": rms_val, "kurtosis": kurt_val, "fft_energy": fft_energy},
    }


@app.post("/api/bearing-signal-reset")
def api_bearing_signal_reset():
    """Reset signal playback to start."""
    cms_signal_index[0] = 0
    total = len(cms_lifecycle_signal) // CMS_WINDOW_SIZE if cms_lifecycle_signal is not None else 0
    return {"message": "Signal reset", "total_windows": total}


@app.get("/api/gear-configs")
def api_gear_configs():
    return GEAR_CONFIGS


@app.get("/api/models")
def api_models():
    """Return merged model comparison across all gear types."""
    merged = dict(comparison)
    try:
        spur_cmp = json.load(open('models/spur_model_comparison.json'))
        merged.update(spur_cmp)
    except:
        pass
    try:
        bevel_cmp = json.load(open('models/bevel_model_comparison.json'))
        merged.update(bevel_cmp)
    except:
        pass
    try:
        worm_cmp = json.load(open('models/worm_model_comparison.json'))
        merged.update(worm_cmp)
    except:
        pass
    return merged


@app.get("/api/models/comparison")
def api_models_comparison():
    """Return structured comparison of all gear types with overall summary."""
    gear_comparisons = {}
    
    # Helical
    try:
        helical_cmp = json.load(open('models/model_comparison.json'))
        gear_comparisons['Helical'] = helical_cmp
    except:
        pass
    
    # Spur
    try:
        spur_cmp = json.load(open('models/spur_model_comparison.json'))
        gear_comparisons['Spur'] = spur_cmp
    except:
        pass
    
    # Bevel
    try:
        bevel_cmp = json.load(open('models/bevel_model_comparison.json'))
        gear_comparisons['Bevel'] = bevel_cmp
    except:
        pass
    
    # Worm
    try:
        worm_cmp = json.load(open('models/worm_model_comparison.json'))
        gear_comparisons['Worm'] = worm_cmp
    except:
        pass
    
    # Calculate overall statistics
    all_accuracies = []
    all_f1_scores = []
    all_aucs = []
    
    for gear_type, models in gear_comparisons.items():
        for model_name, metrics in models.items():
            if 'accuracy' in metrics:
                all_accuracies.append(metrics['accuracy'])
            if 'f1' in metrics:
                all_f1_scores.append(metrics['f1'])
            if 'auc' in metrics:
                all_aucs.append(metrics['auc'])
    
    overall_summary = {
        'total_gear_types': len(gear_comparisons),
        'total_models': sum(len(models) for models in gear_comparisons.values()),
        'avg_accuracy': float(np.mean(all_accuracies)) if all_accuracies else 0.0,
        'avg_f1': float(np.mean(all_f1_scores)) if all_f1_scores else 0.0,
        'avg_auc': float(np.mean(all_aucs)) if all_aucs else 0.0,
        'best_accuracy': float(max(all_accuracies)) if all_accuracies else 0.0,
        'best_f1': float(max(all_f1_scores)) if all_f1_scores else 0.0,
        'best_auc': float(max(all_aucs)) if all_aucs else 0.0,
    }
    
    return {
        'gear_types': gear_comparisons,
        'overall': overall_summary
    }


@app.get("/api/bevel-specs")
def api_bevel_specs():
    """Return bevel gear AGMA dataset."""
    try:
        import math
        power_kw = 15.0; pinion_speed_rpm = 1450.0; pressure_angle_deg = 20.0
        shaft_angle_deg = 90.0; module_outer_mm = 4.0
        num_teeth_pinion = 18; num_teeth_gear = 18
        alpha = math.radians(pressure_angle_deg)
        sigma = math.radians(shaft_angle_deg)
        ratio_m = num_teeth_gear / num_teeth_pinion
        gamma_p_rad = math.atan(math.sin(sigma) / (ratio_m + math.cos(sigma)))
        gamma_g_rad = math.atan(math.sin(sigma) * ratio_m / (1 + ratio_m * math.cos(sigma)))
        d_outer_p = num_teeth_pinion * module_outer_mm
        cone_distance_a = d_outer_p / (2 * math.sin(gamma_p_rad))
        face_width_f = 35.0
        module_mean = module_outer_mm * (1 - (face_width_f / (2 * cone_distance_a)))
        d_mean_p = num_teeth_pinion * module_mean
        addendum_outer = 1.0 * module_outer_mm; dedendum_outer = 1.25 * module_outer_mm
        d_outer_tip_p = d_outer_p + 2 * addendum_outer * math.cos(gamma_p_rad)
        d_outer_tip_g = d_outer_p + 2 * addendum_outer * math.cos(gamma_g_rad)
        zv_p = num_teeth_pinion / math.cos(gamma_p_rad)
        zv_g = num_teeth_gear / math.cos(gamma_g_rad)
        torque_pinion_nm = (power_kw * 1000) / (2 * math.pi * pinion_speed_rpm / 60)
        tangential_force_n = (2 * torque_pinion_nm) / (d_mean_p / 1000)
        pitch_line_velocity_ms = (math.pi * d_mean_p * pinion_speed_rpm) / (60 * 1000)
        return {
            "identification": {"project_name": "High-Torque Right-Angle Drive - Prototype",
                               "standard_applied": "AGMA 2003-B97", "units": "Metric (mm, degrees, N, Nm)",
                               "gear_type": "Straight Bevel Gear (Miter)"},
            "geometric_data": {
                "shared_dimensions": {"outer_module_mm": module_outer_mm, "mean_module_mm": round(module_mean, 4),
                                      "cone_distance_mm": round(cone_distance_a, 2), "face_width_mm": face_width_f,
                                      "addendum_mm": addendum_outer, "dedendum_mm": dedendum_outer},
                "pinion": {"teeth": num_teeth_pinion, "pitch_cone_angle_deg": round(math.degrees(gamma_p_rad), 4),
                           "outer_pitch_diameter_mm": round(d_outer_p, 2), "mean_pitch_diameter_mm": round(d_mean_p, 2),
                           "outer_tip_diameter_mm": round(d_outer_tip_p, 2), "virtual_teeth": round(zv_p, 2)},
                "gear": {"teeth": num_teeth_gear, "pitch_cone_angle_deg": round(math.degrees(gamma_g_rad), 4),
                         "outer_pitch_diameter_mm": round(d_outer_p, 2), "mean_pitch_diameter_mm": round(d_mean_p, 2),
                         "outer_tip_diameter_mm": round(d_outer_tip_g, 2), "virtual_teeth": round(zv_g, 2)},
            },
            "performance": {"torque_nm": round(torque_pinion_nm, 2), "tangential_force_n": round(tangential_force_n, 2),
                            "pitch_line_velocity_ms": round(pitch_line_velocity_ms, 2), "power_kw": power_kw,
                            "pinion_rpm": pinion_speed_rpm},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    """AI Copilot — ask GearMind a question."""
    try:
        from copilot.llm_copilot import ask_gearmind, predict_gear_health as ph
        prediction = ph(req.sensor_values)
        response = ask_gearmind(req.question, prediction, req.gear_id, req.chat_history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report")
def api_report(req: ReportRequest):
    """LLM-based maintenance report with auto-save to testing folder."""
    try:
        from copilot.llm_copilot import generate_maintenance_report, predict_gear_health as ph
        prediction = ph(req.sensor_values)
        report = generate_maintenance_report(prediction, req.gear_id)
        
        # Save report to testing folder with today's date
        os.makedirs('testing', exist_ok=True)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"testing/GearMind_Report_{req.gear_type}_{req.gear_id}_{today}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"GearMind AI - Maintenance Report\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Gear Type: {req.gear_type}\n")
            f.write(f"Gear ID: {req.gear_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(report)
            f.write(f"\n\n{'=' * 60}\n")
            f.write(f"SENSOR READINGS\n")
            f.write(f"{'=' * 60}\n")
            for key, value in req.sensor_values.items():
                f.write(f"{key}: {value}\n")
            f.write(f"\n{'=' * 60}\n")
            f.write(f"PREDICTION RESULTS\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Fault Label: {prediction['fault_label']}\n")
            f.write(f"Confidence: {prediction['confidence']:.2%}\n")
            f.write(f"RUL Cycles: {prediction['rul_cycles']:,}\n")
            f.write(f"Health Score: {prediction.get('health_score', 'N/A')}\n")
            f.write(f"Anomaly Status: {prediction['anomaly_status']}\n")
        
        return {"report": report, "saved_to": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report-pdf-data")
def api_report_pdf_data(req: ReportRequest):
    """Return structured JSON data for client-side PDF generation."""
    try:
        result = predict_gear_health(req.sensor_values, req.gear_type)
        gear_cfg = GEAR_CONFIGS.get(req.gear_type, GEAR_CONFIGS["Helical"])

        cm = result.get('class_probs', {})
        no_fault_prob = cm.get('No Fault', cm.get('No Failure', 0.5))
        health_score = result.get('health_score', int(no_fault_prob * 100))
        rul_cycles   = result.get('rul_cycles', 0)
        daily_cycles = gear_cfg.get('daily_cycles', 8000)
        rul_days     = round(rul_cycles / daily_cycles, 1) if daily_cycles else 0
        rul_shifts   = round(rul_cycles / (daily_cycles / 3), 1) if daily_cycles else 0

        fault_label  = result.get('fault_label', 'Unknown')
        confidence   = result.get('confidence', 0.0)
        shap_values  = result.get('shap_values', {})

        # Recommendations based on fault label
        recommendations = {
            'No Fault':    ["Continue normal operations", "Schedule routine inspection in 30 days"],
            'No Failure':  ["Continue normal operations", "Schedule routine inspection in 30 days"],
            'Minor Fault': ["Reduce operating load by 15%", "Inspect lubrication system within 7 days",
                            "Schedule maintenance within 2 weeks"],
            'Major Fault': ["IMMEDIATE SHUTDOWN RECOMMENDED", "Do not operate under full load",
                            "Schedule emergency maintenance NOW", "Replace worn components"],
            'Failure':     ["STOP OPERATION IMMEDIATELY", "Full inspection required",
                            "Replace critical components before restart"],
        }.get(fault_label, ["Schedule inspection"])

        return {
            "gear_type":       req.gear_type,
            "gear_id":         req.gear_id,
            "gear_spec":       gear_cfg.get('spec', ''),
            "fault_label":     fault_label,
            "confidence":      round(confidence * 100, 1),
            "health_score":    health_score,
            "rul_cycles":      rul_cycles,
            "rul_days":        rul_days,
            "rul_shifts":      rul_shifts,
            "shap_values":     shap_values,
            "class_probs":     result.get('class_probs', {}),
            "sensor_values":   result.get('sensor_values', req.sensor_values),
            "violations":      result.get('violations', {}),
            "repair_cost":     gear_cfg.get('repair_cost', 0),
            "overhaul_cost":   gear_cfg.get('overhaul_cost', 0),
            "failure_cost":    gear_cfg.get('failure_cost', 0),
            "recommendations": recommendations,
            "generated_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize")
def api_optimize(req: OptimizeRequest):
    """Run differential evolution optimizer for any gear type - improved version."""
    try:
        from scipy.optimize import differential_evolution
        
        # Detect gear type from sensor_values keys
        gear_type = 'Helical'  # default
        if 'Speed_RPM' in req.sensor_values or 'Noise_dB' in req.sensor_values:
            gear_type = 'Spur'
        elif 'gear_type' in req.sensor_values:
            gear_type = req.sensor_values['gear_type']
        
        print(f"🔧 Optimizer called for {gear_type} gear")
        print(f"   Sensor values keys: {list(req.sensor_values.keys())}")
        print(f"   Target probability: {req.target_probability}%")
        
        # Define bounds and features per gear type
        if gear_type == 'Spur':
            features = SPUR_FEATURES
            feature_labels = ['Speed', 'Torque', 'Vibration', 'Temperature', 'Shock Load', 'Noise Level']
            units = ['RPM', 'Nm', 'mm/s', '°C', 'g', 'dB']
            OPT_BOUNDS = [(500.0,3000.0),(50.0,500.0),(0.5,20.0),(40.0,120.0),(0.0,5.0),(50.0,95.0)]
            
            def predict_prob(vals):
                sv = dict(zip(features, vals))
                p = predict_spur(sv)
                # Map Failure/No Failure to probability
                failure_prob = p['class_probs'].get('Failure', 0.0)
                return failure_prob * 100
        elif gear_type == 'Bevel':
            features = BEVEL_FEATURES
            feature_labels = ['Load', 'Torque', 'Vibration', 'Temperature', 'Wear', 'Lubrication', 'Efficiency', 'Cycles']
            units = ['kN', 'Nm', 'mm/s', '°C', 'mm', '', '%', 'cycles']
            OPT_BOUNDS = [(10.0,120.0),(50.0,600.0),(0.5,30.0),(40.0,150.0),
                          (0.0,4.0),(0.05,1.0),(70.0,99.0),(0.0,100000.0)]
            
            def predict_prob(vals):
                sv = dict(zip(features, vals))
                p = predict_bevel(sv)
                fault_map = {'No Fault': 0.05, 'Minor Fault': 0.55, 'Major Fault': 0.92}
                return fault_map.get(p['fault_label'], 0.5) * 100 + (1 - p['confidence']) * 10
        else:  # Helical
            features = HELICAL_FEATURES
            feature_labels = ['Load', 'Torque', 'Vibration', 'Temperature', 'Wear', 'Lubrication', 'Efficiency', 'Cycles']
            units = ['kN', 'Nm', 'mm/s', '°C', 'mm', '', '%', 'cycles']
            OPT_BOUNDS = [(10.0,120.0),(50.0,600.0),(0.5,30.0),(40.0,150.0),
                          (0.0,4.0),(0.05,1.0),(70.0,99.0),(0.0,100000.0)]
            
            def predict_prob(vals):
                sv = dict(zip(features, vals))
                p = predict_helical(sv)
                fault_map = {'No Fault': 0.05, 'Minor Fault': 0.55, 'Major Fault': 0.92}
                return fault_map.get(p['fault_label'], 0.5) * 100 + (1 - p['confidence']) * 10
        
        # Extract live values - handle missing keys gracefully
        live_vals = []
        for f in features:
            if f in req.sensor_values:
                live_vals.append(float(req.sensor_values[f]))
            else:
                # Feature not found - use midpoint of bounds as default
                idx = features.index(f)
                default_val = (OPT_BOUNDS[idx][0] + OPT_BOUNDS[idx][1]) / 2
                print(f"   ⚠️  Feature '{f}' not found, using default: {default_val}")
                live_vals.append(default_val)
        
        live_arr   = np.array(live_vals, dtype=float)
        locked_arr = np.array([req.locks.get(f, False) for f in features], dtype=bool)
        bounds_arr = np.array(OPT_BOUNDS)
        ranges     = bounds_arr[:, 1] - bounds_arr[:, 0]
        free_idx   = np.where(~locked_arr)[0]
        
        print(f"   Live values: {live_arr}")
        print(f"   Locked features: {[features[i] for i, locked in enumerate(locked_arr) if locked]}")
        print(f"   Free features: {[features[i] for i in free_idx]}")
        
        if len(free_idx) == 0:
            return {"error": "All parameters locked — unlock at least one."}
        
        # Compute sensitivity analysis (optimized - only for free parameters)
        before_prob = predict_prob(live_arr.tolist())
        sensitivity = []
        
        # Only compute sensitivity for free parameters to save time
        for i, (lbl, feat, unit, (lo, hi)) in enumerate(zip(feature_labels, features, units, OPT_BOUNDS)):
            if locked_arr[i]:
                # Skip computation for locked parameters
                sensitivity.append({
                    'feature': feat,
                    'label': lbl,
                    'leverage': 0.0,
                    'locked': True
                })
            else:
                step = (hi - lo) * 0.05  # 5% of range
                p_up = live_arr.copy(); p_up[i] = min(hi, live_arr[i] + step)
                p_dn = live_arr.copy(); p_dn[i] = max(lo, live_arr[i] - step)
                eff_up = predict_prob(p_up.tolist()) - before_prob
                eff_dn = predict_prob(p_dn.tolist()) - before_prob
                leverage = max(abs(eff_up), abs(eff_dn))
                sensitivity.append({
                    'feature': feat,
                    'label': lbl,
                    'leverage': round(leverage, 4),
                    'locked': False
                })
        sensitivity.sort(key=lambda x: x['leverage'], reverse=True)
        
        free_bnds = [tuple(bounds_arr[i]) for i in free_idx]
        target = req.target_probability
        
        # Create smart initial population (speeds up convergence)
        # Start with current values and some strategic variations
        init_pop = []
        if len(free_idx) > 0:
            # Add current point
            init_pop.append(live_arr[free_idx])
            
            # Add points that reduce high-risk parameters
            for i in free_idx:
                candidate = live_arr[free_idx].copy()
                # If parameter is in upper half of range, try reducing it
                mid_point = (bounds_arr[i][0] + bounds_arr[i][1]) / 2
                if live_arr[i] > mid_point:
                    candidate[list(free_idx).index(i)] = mid_point
                else:
                    candidate[list(free_idx).index(i)] = bounds_arr[i][0] + (bounds_arr[i][1] - bounds_arr[i][0]) * 0.3
                init_pop.append(candidate)
            
            # Limit to popsize
            init_pop = init_pop[:6 if gear_type == 'Spur' else 8]

        def objective(x):
            cand = live_arr.copy()
            cand[free_idx] = x
            prob = predict_prob(cand.tolist())
            prob_pen = max(0.0, prob - target) ** 2
            norm_chg = (x - live_arr[free_idx]) / ranges[free_idx]
            chg_pen  = 5.0 * float(np.sum(norm_chg ** 2))
            return prob_pen + chg_pen

        print(f"   Starting optimization...")
        # Optimized for speed while maintaining quality
        # Reduced iterations and population for faster convergence
        if gear_type == 'Spur':
            res = differential_evolution(
                objective, bounds=free_bnds, seed=42, 
                maxiter=60,          # Further reduced for speed
                tol=1e-2,            # Relaxed tolerance
                popsize=6,           # Small population
                mutation=(0.5, 1.0),
                recombination=0.7,
                polish=False,        # Disabled for speed
                workers=1,
                strategy='best1bin', 
                atol=0.01,
                updating='deferred', # Faster updates
                init=np.array(init_pop) if init_pop else 'latinhypercube'
            )
        else:
            res = differential_evolution(
                objective, bounds=free_bnds, seed=42, 
                maxiter=100,         # Further reduced for speed
                tol=1e-3,            # Relaxed tolerance
                popsize=8,           # Small population
                mutation=(0.5, 1.0),
                recombination=0.7,
                polish=False,        # Disabled for speed
                workers=1,
                updating='deferred', # Faster updates
                init=np.array(init_pop) if init_pop else 'latinhypercube'
            )
        
        opt_arr = live_arr.copy()
        opt_arr[free_idx] = res.x
        opt_prob    = predict_prob(opt_arr.tolist())
        before_prob = predict_prob(live_arr.tolist())
        
        # Compute detailed changes (like spur_app.py)
        changes = []
        for i, (lbl, feat, unit, (lo, hi)) in enumerate(zip(feature_labels, features, units, OPT_BOUNDS)):
            before = float(live_arr[i])
            after = float(opt_arr[i])
            delta = after - before
            pct_range = abs(delta) / (hi - lo) * 100 if (hi - lo) > 0 else 0
            changes.append({
                'feature': feat,
                'label': lbl,
                'unit': unit,
                'before': round(before, 4),
                'after': round(after, 4),
                'delta': round(delta, 4),
                'pct_range': round(pct_range, 2),
                'locked': bool(locked_arr[i]),
                'normalized_before': round((before - lo) / (hi - lo), 4) if (hi - lo) > 0 else 0,
                'normalized_after': round((after - lo) / (hi - lo), 4) if (hi - lo) > 0 else 0,
            })
        
        print(f"   ✅ Optimization complete!")
        print(f"   Before: {before_prob:.2f}% → After: {opt_prob:.2f}% (Target: {target}%)")
        
        return {
            "optimized_values":      dict(zip(features, [float(v) for v in opt_arr])),
            "optimized_probability": opt_prob,
            "before_probability": before_prob,
            "before_values":         dict(zip(features, [float(v) for v in live_arr])),
            "target": target,
            "achieved": opt_prob < target,
            "reduction": before_prob - opt_prob,
            "gear_type": gear_type,
            "sensitivity": sensitivity,
            "changes": changes,
            "feature_labels": feature_labels,
            "units": units,
        }
    except Exception as e:
        import traceback
        print(f"   ❌ Optimization error:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sensitivity")
def api_sensitivity(sensors: SensorInput):
    """Parameter sensitivity analysis."""
    OPT_BOUNDS = [(10.0,120.0),(50.0,600.0),(0.5,30.0),(40.0,150.0),
                  (0.0,4.0),(0.05,1.0),(70.0,99.0),(0.0,100000.0)]
    sensor_dict = sensor_input_to_dict(sensors)
    live = [sensor_dict[f] for f in FEATURE_COLS]
    cur_prob = _opt_predict_prob(live)
    results = []
    for i, (lbl, (lo, hi)) in enumerate(zip(FEATURE_COLS, OPT_BOUNDS)):
        step = (hi - lo) * 0.05
        p_up = live.copy(); p_up[i] = min(hi, live[i] + step)
        p_dn = live.copy(); p_dn[i] = max(lo, live[i] - step)
        lev  = max(abs(_opt_predict_prob(p_up) - cur_prob), abs(_opt_predict_prob(p_dn) - cur_prob))
        results.append({"label": lbl, "leverage": round(lev, 4)})
    results.sort(key=lambda x: x["leverage"], reverse=True)
    return {"current_probability": cur_prob, "sensitivity": results}


@app.get("/api/lime")
def api_lime(load: float=48, torque: float=201.6, vib: float=2.3,
             temp: float=72, wear: float=0.2, lube: float=0.82,
             eff: float=96.8, cycles: int=18000):
    """LIME explanation for Helical gear."""
    try:
        import lime, lime.lime_tabular
        sensor_dict = {
            'Load (kN)': load, 'Torque (Nm)': torque, 'Vibration RMS (mm/s)': vib,
            'Temperature (°C)': temp, 'Wear (mm)': wear, 'Lubrication Index': lube,
            'Efficiency (%)': eff, 'Cycles in Use': cycles,
        }
        X_sample    = helical_shap["X_sample"]
        lime_exp    = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_sample, feature_names=HELICAL_FEATURES,
            class_names=list(helical_le.classes_), mode="classification",
            discretize_continuous=True, random_state=42)
        input_arr   = np.array([sensor_dict[f] for f in HELICAL_FEATURES])
        input_scaled = helical_scaler.transform(input_arr.reshape(1, -1))[0]
        pred_enc    = helical_model.predict(input_scaled.reshape(1, -1))[0]
        lime_result = lime_exp.explain_instance(data_row=input_scaled,
                                                predict_fn=helical_model.predict_proba,
                                                num_features=8, labels=[pred_enc])
        lime_list   = lime_result.as_list(label=pred_enc)
        no_fault_idx = list(helical_le.classes_).index("No Fault") if "No Fault" in list(helical_le.classes_) else -1
        result = []
        for rule, weight in lime_list:
            w = -weight if pred_enc == no_fault_idx else weight
            result.append({"rule": rule, "weight": round(w, 6)})
        result.sort(key=lambda x: abs(x["weight"]), reverse=True)
        return {"lime_results": result, "predicted_class": str(helical_le.classes_[pred_enc])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/lime-spur")
def api_lime_spur(speed: float=1200, torque: float=180, vib: float=3.2,
                  temp: float=70, shock: float=1.2, noise: float=62):
    """LIME explanation for Spur SVM."""
    try:
        import lime, lime.lime_tabular
        if spur_model is None or spur_shap is None:
            raise HTTPException(status_code=503, detail="Spur model/XAI not loaded")
        input_arr   = np.array([[speed, torque, vib, temp, shock, noise]])
        input_scaled = spur_scaler.transform(input_arr)
        X_sample    = spur_shap["X_sample"]
        lime_exp    = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_sample, feature_names=SPUR_FEATURES,
            class_names=list(spur_le.classes_), mode="classification",
            discretize_continuous=True, random_state=42)
        pred_enc    = spur_model.predict(input_scaled)[0]
        lime_result = lime_exp.explain_instance(data_row=input_scaled[0],
                                                predict_fn=spur_model.predict_proba,
                                                num_features=6, labels=[pred_enc])
        lime_list   = lime_result.as_list(label=pred_enc)
        no_fail_idx = list(spur_le.classes_).index('No Failure') if 'No Failure' in spur_le.classes_ else -1
        result = []
        for rule, weight in lime_list:
            w = -weight if pred_enc == no_fail_idx else weight
            result.append({"rule": rule, "weight": round(w, 6)})
        result.sort(key=lambda x: abs(x["weight"]), reverse=True)
        return {"lime_results": result, "predicted_class": str(spur_le.classes_[pred_enc])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/lime-bevel")
def api_lime_bevel(load: float=42, torque: float=168, vib: float=2.5,
                   temp: float=70, wear: float=0.18, lube: float=0.85,
                   eff: float=95.2, cycles: int=15000):
    """LIME explanation for Bevel XGBoost."""
    try:
        import lime, lime.lime_tabular
        if bevel_model is None or bevel_shap is None:
            raise HTTPException(status_code=503, detail="Bevel model/XAI not loaded")
        sensor_dict = {
            'Load (kN)': load, 'Torque (Nm)': torque, 'Vibration RMS (mm/s)': vib,
            'Temperature (°C)': temp, 'Wear (mm)': wear, 'Lubrication Index': lube,
            'Efficiency (%)': eff, 'Cycles in Use': cycles,
        }
        input_arr    = np.array([sensor_dict[f] for f in BEVEL_FEATURES])
        input_scaled = bevel_scaler.transform(input_arr.reshape(1, -1))
        X_sample     = bevel_shap["X_sample"]
        lime_exp     = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_sample, feature_names=BEVEL_FEATURES,
            class_names=list(bevel_le.classes_), mode="classification",
            discretize_continuous=True, random_state=42)
        pred_enc     = bevel_model.predict(input_scaled)[0]
        lime_result  = lime_exp.explain_instance(data_row=input_scaled[0],
                                                 predict_fn=bevel_model.predict_proba,
                                                 num_features=8, labels=[pred_enc])
        lime_list    = lime_result.as_list(label=pred_enc)
        no_fault_idx = list(bevel_le.classes_).index("No Fault") if "No Fault" in list(bevel_le.classes_) else -1
        result = []
        for rule, weight in lime_list:
            w = -weight if pred_enc == no_fault_idx else weight
            result.append({"rule": rule, "weight": round(w, 6)})
        result.sort(key=lambda x: abs(x["weight"]), reverse=True)
        return {"lime_results": result, "predicted_class": str(bevel_le.classes_[pred_enc])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def api_history():
    """Get all historical readings."""
    try:
        con = sqlite3.connect(DB_PATH)
        df  = pd.read_sql_query("SELECT * FROM gear_log ORDER BY timestamp DESC", con)
        con.close()
        return {"history": df.to_dict(orient="records"), "total": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/history")
def api_log_history(entry: HistoryEntry):
    """Log a new reading with operator metadata."""
    try:
        con = sqlite3.connect(DB_PATH)
        sv  = entry.sensor_values
        
        # Handle different gear types with different sensor parameters
        if entry.gear_type == 'Spur':
            # For Spur: Speed_RPM → load_kn, Shock_Load_g → wear, Noise_dB → lubrication
            load_val = sv.get('Speed_RPM', sv.get('load_kn', 0))
            torque_val = sv.get('Torque_Nm', sv.get('torque_nm', 0))
            vib_val = sv.get('Vibration_mm_s', sv.get('vibration', 0))
            temp_val = sv.get('Temperature_C', sv.get('temperature', 0))
            wear_val = sv.get('Shock_Load_g', sv.get('wear', 0))
            lube_val = sv.get('Noise_dB', sv.get('lubrication', 0))
            eff_val = 0  # Spur doesn't have efficiency
            cycles_val = 0  # Spur doesn't have cycles
        else:
            # For Helical and Bevel: use standard mapping
            load_val = sv.get('Load (kN)', sv.get('load_kn', 0))
            torque_val = sv.get('Torque (Nm)', sv.get('torque_nm', 0))
            vib_val = sv.get('Vibration RMS (mm/s)', sv.get('vibration', 0))
            temp_val = sv.get('Temperature (°C)', sv.get('temperature', 0))
            wear_val = sv.get('Wear (mm)', sv.get('wear', 0))
            lube_val = sv.get('Lubrication Index', sv.get('lubrication', 0))
            eff_val = sv.get('Efficiency (%)', sv.get('efficiency', 0))
            cycles_val = sv.get('Cycles in Use', sv.get('cycles', 0))
        
        con.execute("""
            INSERT INTO gear_log
                (timestamp, gear_type, gear_unit, fault_label, confidence,
                 health_score, rul_cycles, load_kn, torque_nm, vibration,
                 temperature, wear, lubrication, efficiency, cycles,
                 operator_name, shift, role)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              entry.gear_type, entry.gear_unit, entry.fault_label,
              entry.confidence, entry.health_score, entry.rul_cycles,
              load_val, torque_val, vib_val, temp_val, wear_val, lube_val,
              eff_val, cycles_val,
              entry.operator_name, entry.shift, entry.role))
        con.commit()
        con.close()
        return {"status": "logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history")
def api_clear_history():
    try:
        con = sqlite3.connect(DB_PATH)
        con.execute("DELETE FROM gear_log")
        con.commit(); con.close()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/confusion-matrix")
def api_confusion_matrix():
    try:
        from sklearn.metrics import confusion_matrix
        df_cm = pd.read_csv('data/helical_gear_dataset.csv')
        X_cm  = helical_scaler.transform(df_cm[HELICAL_FEATURES].values)
        y_cm  = helical_le.transform(df_cm['Fault Label'].values)
        cm    = confusion_matrix(y_cm, helical_model.predict(X_cm))
        return {"matrix": cm.tolist(), "labels": [str(c) for c in helical_le.classes_]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feature-importance")
def api_feature_importance():
    try:
        if hasattr(helical_model, 'feature_importances_'):
            fi = helical_model.feature_importances_
            result = [{"feature": f, "importance": round(float(v), 6)}
                      for f, v in zip(HELICAL_FEATURES, fi)]
            result.sort(key=lambda x: x["importance"], reverse=True)
            return {"importance": result}
        return {"importance": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
