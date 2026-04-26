"""
MODULE 5 — GEARMIND AI DASHBOARD (Ultimate Pro Edition)
GearMind AI · Elecon Engineering Works Pvt. Ltd.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import joblib
import json
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from copilot.llm_copilot import predict_gear_health, ask_gearmind, simulate_what_if, generate_maintenance_report

st.set_page_config(
    page_title="GearMind AI — Elecon Engineering",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
code, .mono { font-family: 'JetBrains Mono', monospace !important; }
.stApp, .main { background: #070b14 !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0a1020 100%) !important;
    border-right: 1px solid #0f2040 !important;
}
section[data-testid="stSidebar"] * { color: #7a9cc4 !important; }
section[data-testid="stSidebar"] label { font-size: 11px !important; color: #7a9cc4 !important; }
.stSlider > div > div > div { background: #0f2040 !important; }
.stSlider > div > div > div > div { background: linear-gradient(90deg, #2563eb, #3b82f6) !important; }
[data-testid="stSliderThumb"] { background: #3b82f6 !important; border: 2px solid #fff !important; }
.stSelectbox > div > div { background: #0d1829 !important; border: 1px solid #0f2040 !important; color: #c9d6e8 !important; border-radius: 8px !important; }
.stTextInput > div > div > input, .stTextArea textarea {
    background: #0d1829 !important; border: 1px solid #0f2040 !important;
    color: #e2e8f0 !important; border-radius: 10px !important; font-size: 14px !important; padding: 12px 16px !important;
}
.stTextArea textarea:focus { border-color: #2563eb !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important; }
.stButton > button { background: #0d1829 !important; color: #60a5fa !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; font-size: 12px !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
.stButton > button:hover { background: #1e3a5f !important; color: #93c5fd !important; border-color: #2563eb !important; transform: translateY(-1px) !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #1d4ed8, #2563eb) !important; color: white !important; border: none !important; font-weight: 600 !important; box-shadow: 0 4px 15px rgba(37,99,235,0.3) !important; }
.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #1e40af, #1d4ed8) !important; transform: translateY(-2px) !important; }
.stTabs [data-baseweb="tab-list"] { background: #080d1a !important; border-bottom: 1px solid #0f2040 !important; padding: 0 8px !important; gap: 2px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #3d5a7a !important; font-size: 12px !important; font-weight: 500 !important; padding: 10px 16px !important; border-bottom: 2px solid transparent !important; }
.stTabs [aria-selected="true"] { background: #0d1829 !important; color: #60a5fa !important; border-bottom: 2px solid #2563eb !important; }
[data-testid="metric-container"] { background: linear-gradient(135deg, #0d1829, #0a1422) !important; border: 1px solid #0f2040 !important; border-radius: 12px !important; padding: 18px !important; }
[data-testid="metric-container"] label { color: #3d5a7a !important; font-size: 11px !important; letter-spacing: 0.5px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 22px !important; font-weight: 700 !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #070b14; }
::-webkit-scrollbar-thumb { background: #0f2040; border-radius: 3px; }
.stDataFrame { border: 1px solid #0f2040 !important; border-radius: 10px !important; overflow: hidden !important; }
.chat-wrapper { background: linear-gradient(180deg, #080d1a, #070b14); border: 1px solid #0f2040; border-radius: 16px; overflow: hidden; margin-bottom: 12px; }
.chat-header-bar { background: linear-gradient(90deg, #0d1829, #0a1422); border-bottom: 1px solid #0f2040; padding: 14px 20px; display: flex; align-items: center; gap: 10px; }
.chat-dot { width: 8px; height: 8px; border-radius: 50%; }
.chat-dot-green { background: #10b981; box-shadow: 0 0 6px #10b981; }
.chat-dot-yellow { background: #f59e0b; }
.chat-dot-red { background: #ef4444; }
.chat-messages { padding: 20px; height: 380px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
.chat-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }
.chat-empty-icon { font-size: 48px; margin-bottom: 12px; }
.chat-empty-title { font-size: 15px; font-weight: 600; color: #1e3a5f; margin-bottom: 6px; }
.chat-empty-sub { font-size: 12px; color: #0f2040; line-height: 1.6; }
.msg-wrapper-user { display: flex; flex-direction: column; align-items: flex-end; }
.msg-wrapper-ai { display: flex; flex-direction: column; align-items: flex-start; }
.msg-meta { font-size: 9px; font-weight: 600; letter-spacing: 1px; margin-bottom: 5px; font-family: 'JetBrains Mono', monospace; }
.msg-meta-user { color: #2563eb; text-align: right; }
.msg-meta-ai { color: #059669; display: flex; align-items: center; gap: 6px; }
.msg-bubble-user { background: linear-gradient(135deg, #1e3a5f, #1d4ed8); border: 1px solid #2563eb; border-radius: 16px 16px 4px 16px; padding: 12px 16px; max-width: 75%; color: #e2e8f0; font-size: 14px; line-height: 1.6; }
.msg-bubble-ai { background: linear-gradient(135deg, #0d1829, #0a1422); border: 1px solid #0f2040; border-radius: 4px 16px 16px 16px; padding: 14px 18px; max-width: 90%; color: #c9d6e8; font-size: 14px; line-height: 1.7; }
.msg-bubble-ai strong { color: #93c5fd; }
.msg-bubble-ai em { color: #7dd3fc; font-style: normal; }
.sensor-card { background: linear-gradient(135deg, #0d1829, #0a1422); border: 1px solid #0f2040; border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; }
.sensor-card-bad { border-color: rgba(239,68,68,0.3) !important; background: linear-gradient(135deg, #1a0808, #130808) !important; }
.badge-major { background: linear-gradient(135deg,rgba(239,68,68,0.15),rgba(220,38,38,0.1)); border:1px solid #ef4444; color:#ef4444; padding:5px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 0 20px rgba(239,68,68,0.15); }
.badge-minor { background: linear-gradient(135deg,rgba(245,158,11,0.15),rgba(217,119,6,0.1)); border:1px solid #f59e0b; color:#f59e0b; padding:5px 16px; border-radius:20px; font-size:13px; font-weight:600; }
.badge-ok    { background: linear-gradient(135deg,rgba(16,185,129,0.15),rgba(5,150,105,0.1)); border:1px solid #10b981; color:#10b981; padding:5px 16px; border-radius:20px; font-size:13px; font-weight:600; }
.section-title { font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #1e3a5f; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #0f2040; }
@keyframes pulse-red { 0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.4);}50%{box-shadow:0 0 0 8px rgba(239,68,68,0);} }
@keyframes pulse-green { 0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0.4);}50%{box-shadow:0 0 0 8px rgba(16,185,129,0);} }
@keyframes pulse-amber { 0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,0.4);}50%{box-shadow:0 0 0 8px rgba(245,158,11,0);} }
.pulse-red { animation: pulse-red 2s infinite; border-radius: 50%; display:inline-block; }
.pulse-green { animation: pulse-green 2s infinite; border-radius: 50%; display:inline-block; }
.pulse-amber { animation: pulse-amber 2s infinite; border-radius: 50%; display:inline-block; }
@keyframes countdown-pulse { 0%,100%{opacity:1;} 50%{opacity:0.6;} }
.countdown-critical { animation: countdown-pulse 1.5s infinite; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────
def md_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)
    text = re.sub(r'### (.+)',  r'<div style="font-size:13px;font-weight:700;color:#60a5fa;margin:10px 0 6px;padding-bottom:4px;border-bottom:1px solid #0f2040;">\1</div>', text)
    text = re.sub(r'## (.+)',   r'<div style="font-size:13px;font-weight:700;color:#60a5fa;margin:10px 0 6px;">\1</div>', text)
    text = re.sub(r'# (.+)',    r'<div style="font-size:13px;font-weight:700;color:#60a5fa;margin:10px 0 6px;">\1</div>', text)
    text = re.sub(r'^[-•] (.+)', r'<div style="padding:4px 0 4px 8px;border-left:2px solid #1e3a5f;margin:4px 0;color:#94a3b8;font-size:13px;">• \1</div>', text, flags=re.MULTILINE)
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    return text

# ── Load Artifacts ───────────────────────────────────────
@st.cache_resource
def load_artifacts():
    arts = {}
    try:
        arts['model']      = joblib.load('models/best_classifier.pkl')
        arts['scaler']     = joblib.load('models/scaler.pkl')
        arts['le']         = joblib.load('models/label_encoder.pkl')
        arts['rul_model']  = joblib.load('models/rul_regressor.pkl')
        arts['comparison'] = json.load(open('models/model_comparison.json'))
    except Exception as e:
        st.error(f"❌ Run python models/train_models.py first\n{e}")
    try:
        arts['shap_data']   = joblib.load('xai/shap_artifacts.pkl')
        arts['anomaly']     = joblib.load('xai/anomaly_model.pkl')
        arts['progression'] = pd.read_csv('xai/fault_progression.csv')
        arts['xai_ready']   = True
    except:
        arts['xai_ready'] = False
    return arts

arts = load_artifacts()

FEATURE_COLS = [
    'Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)',
    'Temperature (°C)', 'Wear (mm)', 'Lubrication Index',
    'Efficiency (%)', 'Cycles in Use'
]

# ── Gear Type Configurations ─────────────────────────────
GEAR_CONFIGS = {
    "Helical": {
        "icon": "⚙️", "color": "#2563eb",
        "spec": "Helix Angle: 20° | Module: 4 | Teeth: 32 | Pressure Angle: 14.5°",
        "description": "High-efficiency helical gear — smooth, quiet, ideal for high-speed industrial drives",
        "vib_limit": 6.0, "temp_limit": 95.0, "wear_limit": 1.0, "lube_limit": 0.5, "eff_limit": 93.0,
        "daily_cycles": 8000,
        "repair_cost": 45000, "overhaul_cost": 120000, "failure_cost": 450000,
        "units": {
            "HG-01 (Standard — Healthy)":       dict(load=48.0, torque=201.6, vib=2.3,  temp=72.0,  wear=0.20, lube=0.82, eff=96.8, cycles=18000),
            "HG-03 (Heavy Duty — Major Fault)": dict(load=74.0, torque=310.8, vib=12.4, temp=108.0, wear=1.80, lube=0.21, eff=85.2, cycles=84200),
            "HG-05 (Standard — Healthy)":       dict(load=53.0, torque=222.6, vib=3.1,  temp=78.0,  wear=0.35, lube=0.71, eff=95.3, cycles=28000),
            "HG-07 (Precision — Minor Fault)":  dict(load=81.0, torque=340.2, vib=7.1,  temp=91.0,  wear=1.10, lube=0.42, eff=90.1, cycles=52000),
            "HG-12 (New — Healthy)":            dict(load=44.0, torque=184.8, vib=1.8,  temp=68.0,  wear=0.15, lube=0.88, eff=97.4, cycles=12000),
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
            "SG-02 (Standard — Healthy)":       dict(load=42.0, torque=188.0, vib=3.2,  temp=70.0,  wear=0.25, lube=0.78, eff=94.5, cycles=22000),
            "SG-04 (Industrial — Major Fault)": dict(load=68.0, torque=298.0, vib=14.1, temp=102.0, wear=2.10, lube=0.18, eff=83.0, cycles=91000),
            "SG-06 (Standard — Healthy)":       dict(load=50.0, torque=215.0, vib=4.1,  temp=76.0,  wear=0.40, lube=0.68, eff=93.8, cycles=31000),
            "SG-08 (Heavy — Minor Fault)":      dict(load=76.0, torque=325.0, vib=9.3,  temp=88.0,  wear=1.35, lube=0.38, eff=89.2, cycles=58000),
            "SG-14 (New — Healthy)":            dict(load=38.0, torque=172.0, vib=2.1,  temp=65.0,  wear=0.12, lube=0.91, eff=96.1, cycles=8000),
        },
        "fault_types": ["Tooth Fracture", "General Wear", "Overload Vibration"],
        "teammate": "Integration in Progress — Spur Gear Module"
    },
}

if "gear_type" not in st.session_state:
    st.session_state.gear_type = "Helical"

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 24px; border-bottom:1px solid #0f2040; margin-bottom:20px;'>
        <div style='font-size:22px; font-weight:800; color:#e2e8f0; letter-spacing:-0.5px;'>⚙ GearMind AI</div>
        <div style='font-size:10px; color:#3d5a7a; margin-top:5px; letter-spacing:2px; font-weight:600;'>ELECON ENGINEERING WORKS</div>
        <div style='margin-top:10px; display:flex; gap:6px;'>
            <span style='background:#0f2040; color:#3b82f6; font-size:9px; padding:3px 8px; border-radius:10px; font-weight:600;'>GBM 99.87%</span>
            <span style='background:#0f2040; color:#10b981; font-size:9px; padding:3px 8px; border-radius:10px; font-weight:600;'>RUL R²=0.99</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
    border-radius:8px; padding:8px 12px; font-size:12px; color:#10b981; margin-bottom:16px;'>
        ✅ AI Copilot Active — LLaMA 3.3 70B
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Gear Type</div>', unsafe_allow_html=True)
    col_h, col_s = st.columns(2)
    with col_h:
        if st.button("⚙️ Helical", use_container_width=True,
                     type="primary" if st.session_state.gear_type == "Helical" else "secondary"):
            st.session_state.gear_type = "Helical"
            st.rerun()
    with col_s:
        if st.button("🔧 Spur", use_container_width=True,
                     type="primary" if st.session_state.gear_type == "Spur" else "secondary"):
            st.session_state.gear_type = "Spur"
            st.rerun()

    col_b, col_w = st.columns(2)
    with col_b:
        st.markdown("""<div style='text-align:center; padding:8px; background:#080d1a; border:1px solid #0a1020;
        border-radius:8px; font-size:11px; color:#1e3a5f; font-weight:600;'>🔩 Bevel<br>
        <span style='font-size:9px; color:#0f2040;'>Coming Soon</span></div>""", unsafe_allow_html=True)
    with col_w:
        st.markdown("""<div style='text-align:center; padding:8px; background:#080d1a; border:1px solid #0a1020;
        border-radius:8px; font-size:11px; color:#1e3a5f; font-weight:600;'>🌀 Worm<br>
        <span style='font-size:9px; color:#0f2040;'>Coming Soon</span></div>""", unsafe_allow_html=True)

    gtype = st.session_state.gear_type
    gc    = GEAR_CONFIGS[gtype]
    gcolor = gc["color"]

    st.markdown(f"""
    <div style='background:rgba(37,99,235,0.05); border:1px solid {gcolor}33;
    border-radius:8px; padding:10px 12px; font-size:10px; color:#3d5a7a; margin:8px 0 12px;'>
        <span style='color:{gcolor}; font-weight:700;'>{gc["icon"]} {gtype} Gear</span><br>
        <span style='color:#1e3a5f;'>{gc["spec"]}</span>
    </div>""", unsafe_allow_html=True)

    # Use first unit as default sensor values
    gear_id = list(gc["units"].keys())[0]
    p = gc["units"][gear_id]
    gear_name = gear_id.split(" ")[0]

    st.markdown('<div class="section-title">Live Sensor Parameters</div>', unsafe_allow_html=True)
    load   = st.slider("Load (kN)",           10.0, 120.0, p['load'],   0.5)
    torque = st.slider("Torque (Nm)",          50.0, 600.0, p['torque'], 1.0)
    vib    = st.slider("Vibration RMS (mm/s)", 0.5,  30.0,  p['vib'],   0.1)
    temp   = st.slider("Temperature (°C)",     40.0, 150.0, p['temp'],  0.5)
    wear   = st.slider("Wear (mm)",            0.0,   4.0,  p['wear'],  0.01)
    lube   = st.slider("Lubrication Index",    0.05,  1.0,  p['lube'],  0.01)
    eff    = st.slider("Efficiency (%)",       70.0,  99.0, p['eff'],   0.1)
    cycles = st.slider("Cycles in Use",        0, 100000,   p['cycles'], 100)

    st.markdown(f"""
    <div style='margin-top:16px; padding:14px; background:#080d1a; border:1px solid #0f2040;
    border-radius:10px; font-size:10px; color:#3d5a7a; line-height:2;'>
        <div style='color:#1e3a5f; font-weight:700; letter-spacing:1px; margin-bottom:6px;'>SYSTEM INFO</div>
        ML: GBM · XGBoost · RF · LR · SVM<br>
        XAI: SHAP · LIME · Isolation Forest<br>
        LLM: Groq · LLaMA 3.3 70B<br>
        Tracking: MLflow · v4.0
    </div>""", unsafe_allow_html=True)

# ── Prediction ────────────────────────────────────────────
sensor_values = {
    'Load (kN)': load, 'Torque (Nm)': torque,
    'Vibration RMS (mm/s)': vib, 'Temperature (°C)': temp,
    'Wear (mm)': wear, 'Lubrication Index': lube,
    'Efficiency (%)': eff, 'Cycles in Use': cycles,
}
prediction = predict_gear_health(sensor_values)
fault = prediction['fault_label']
conf  = prediction['confidence']
rul   = prediction['rul_cycles']

badge_map = {
    'Major Fault': ('badge-major', '🔴', '#ef4444'),
    'Minor Fault': ('badge-minor', '⚠️', '#f59e0b'),
    'No Fault':    ('badge-ok',    '✅', '#10b981'),
}
badge_class, badge_icon, badge_color = badge_map.get(fault, ('badge-ok','✅','#10b981'))
an_color = "#ef4444" if prediction['anomaly_status'] == "SUSPICIOUS" else "#10b981"
an_icon  = "🔴" if prediction['anomaly_status'] == "SUSPICIOUS" else "🟢"

# ── Health Score ──────────────────────────────────────────
def calc_health_score(pred, gear_cfg):
    score = 100
    v = pred["sensor_values"]
    score -= min(30, max(0, (v["Vibration RMS (mm/s)"] - gear_cfg["vib_limit"]) * 5))
    score -= min(20, max(0, (v["Temperature (°C)"]    - gear_cfg["temp_limit"]) * 0.8))
    score -= min(25, max(0, (v["Wear (mm)"]           - gear_cfg["wear_limit"]) * 30))
    score -= min(20, max(0, (gear_cfg["lube_limit"]   - v["Lubrication Index"]) * 40))
    score -= min(10, max(0, (gear_cfg["eff_limit"]    - v["Efficiency (%)"]) * 0.8))
    if pred["fault_label"] == "Major Fault": score = min(score, 25)
    elif pred["fault_label"] == "Minor Fault": score = min(score, 65)
    return max(0, round(score))

health_score_val = calc_health_score(prediction, gc)

# ── Countdown Calculation ─────────────────────────────────
daily_cycles = gc["daily_cycles"]
days_left    = rul / daily_cycles
hours_left   = (days_left % 1) * 24
days_int     = int(days_left)
hours_int    = int(hours_left)

# ── Cost Calculations ─────────────────────────────────────
repair_now   = gc["repair_cost"]
delay_cost   = gc["overhaul_cost"]
failure_cost = gc["failure_cost"]
money_saved  = failure_cost - repair_now
downtime_prevented_hrs = int(rul / (daily_cycles / 8))

# ── Top Header ────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between;
padding:20px 0 18px; border-bottom:1px solid #0f2040; margin-bottom:16px;'>
    <div>
        <div style='font-size:26px; font-weight:800; color:#e2e8f0; letter-spacing:-0.5px;'>
            {gc["icon"]} GearMind AI — {gtype} Gear Predictive Maintenance
        </div>
        <div style='font-size:12px; color:#3d5a7a; margin-top:6px;'>
            {gc["spec"]} &nbsp;·&nbsp; Elecon Engineering Works &nbsp;·&nbsp; {len(prediction['violations'])} violation(s) detected
        </div>
    </div>
    <div style='display:flex; align-items:center; gap:16px;'>
        <div style='text-align:right;'>
            <div style='font-size:10px; color:#1e3a5f; letter-spacing:1px;'>ANOMALY STATUS</div>
            <div style='font-size:13px; font-weight:700; color:{an_color};'>{an_icon} {prediction['anomaly_status']}</div>
        </div>
        <span class="{badge_class}">{badge_icon} {fault}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Gear Type Banner ─────────────────────────────────────
st.markdown(f"""
<div style='display:flex; gap:10px; margin-bottom:20px; align-items:center; flex-wrap:wrap;'>
    <div style='background:linear-gradient(135deg,{gcolor}22,{gcolor}11); border:1px solid {gcolor}44;
    border-radius:10px; padding:10px 20px; display:flex; align-items:center; gap:10px;'>
        <span style='font-size:20px;'>{gc["icon"]}</span>
        <div>
            <div style='font-size:13px; font-weight:700; color:{gcolor};'>{gtype} Gear Module — ACTIVE</div>
            <div style='font-size:10px; color:#3d5a7a;'>{gc["teammate"]}</div>
        </div>
    </div>
    <div style='background:#080d1a; border:1px solid #0f2040; border-radius:10px;
    padding:10px 20px; display:flex; align-items:center; gap:10px; opacity:0.4;'>
        <span style='font-size:20px;'>🔩</span>
        <div>
            <div style='font-size:13px; font-weight:600; color:#1e3a5f;'>Bevel Gear Module</div>
            <div style='font-size:10px; color:#0f2040;'>Integration Pending</div>
        </div>
    </div>
    <div style='background:#080d1a; border:1px solid #0f2040; border-radius:10px;
    padding:10px 20px; display:flex; align-items:center; gap:10px; opacity:0.4;'>
        <span style='font-size:20px;'>🌀</span>
        <div>
            <div style='font-size:13px; font-weight:600; color:#1e3a5f;'>Worm Gear Module</div>
            <div style='font-size:10px; color:#0f2040;'>Integration Pending</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Confidence",   f"{conf:.1%}")
k2.metric("Fault Class",  fault)
k3.metric("RUL (cycles)", f"{rul:,}")
k4.metric("RUL (shifts)", f"{rul//400:,}")
k5.metric("Health Score", f"{health_score_val}/100")
st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯  Gear Health",
    "💰  Cost Impact",
    "🔍  SHAP + LIME",
    "📊  Model Comparison",
    "🔧  What-If Optimizer",
    "📈  History",
    "📄  Report Generator",
])


# ════════════════════════════════════════════════════════
# TAB 1 — GEAR HEALTH (NEW — Gauge + Countdown + AI Copilot)
# ════════════════════════════════════════════════════════
with tab1:
    g1, g2, g3 = st.columns([1, 1, 1])

    # ── Gauge ──
    with g1:
        st.markdown('<div class="section-title">Gear Health Gauge</div>', unsafe_allow_html=True)
        score = health_score_val
        if score >= 70:   gauge_color = "#10b981"
        elif score >= 40: gauge_color = "#f59e0b"
        else:             gauge_color = "#ef4444"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            delta={'reference': 80, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#ef4444'}},
            title={'text': f"<b>{gear_name}</b><br><span style='font-size:13px;color:#64748b;'>{fault}</span>",
                   'font': {'color': '#e2e8f0', 'size': 16}},
            number={'font': {'color': gauge_color, 'size': 52, 'family': 'JetBrains Mono'},
                    'suffix': '/100'},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#1e3a5f', 'tickfont': {'color': '#3d5a7a', 'size': 11}},
                'bar': {'color': gauge_color, 'thickness': 0.25},
                'bgcolor': '#0d1829',
                'bordercolor': '#0f2040',
                'steps': [
                    {'range': [0,  40],  'color': 'rgba(239,68,68,0.15)'},
                    {'range': [40, 70],  'color': 'rgba(245,158,11,0.1)'},
                    {'range': [70, 100], 'color': 'rgba(16,185,129,0.1)'},
                ],
                'threshold': {
                    'line': {'color': '#ffffff', 'width': 3},
                    'thickness': 0.85,
                    'value': score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='#0d1829', font_color='#e2e8f0',
            height=300, margin=dict(t=40, b=20, l=30, r=30)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Zone labels
        st.markdown("""
        <div style='display:flex; justify-content:space-between; font-size:10px; font-weight:600; margin-top:-10px;'>
            <span style='color:#ef4444;'>● CRITICAL (0-40)</span>
            <span style='color:#f59e0b;'>● WARNING (40-70)</span>
            <span style='color:#10b981;'>● SAFE (70-100)</span>
        </div>""", unsafe_allow_html=True)

    # ── Fault Countdown ──
    with g2:
        st.markdown('<div class="section-title">Fault Countdown Timer</div>', unsafe_allow_html=True)

        if fault == "Major Fault":
            countdown_color = "#ef4444"
            countdown_bg    = "rgba(239,68,68,0.08)"
            countdown_border= "rgba(239,68,68,0.3)"
            urgency_text    = "⚠️ IMMEDIATE ACTION REQUIRED"
            urgency_color   = "#ef4444"
            pulse_class     = "pulse-red"
            action_text     = "Stop gear immediately. Schedule emergency maintenance."
        elif fault == "Minor Fault":
            countdown_color = "#f59e0b"
            countdown_bg    = "rgba(245,158,11,0.08)"
            countdown_border= "rgba(245,158,11,0.3)"
            urgency_text    = "⚠️ SCHEDULE MAINTENANCE SOON"
            urgency_color   = "#f59e0b"
            pulse_class     = "pulse-amber"
            action_text     = "Plan maintenance within this week to avoid escalation."
        else:
            countdown_color = "#10b981"
            countdown_bg    = "rgba(16,185,129,0.08)"
            countdown_border= "rgba(16,185,129,0.3)"
            urgency_text    = "✅ OPERATING NORMALLY"
            urgency_color   = "#10b981"
            pulse_class     = "pulse-green"
            action_text     = "Continue operation. Next routine check at scheduled interval."

        st.markdown(f"""
        <div style='background:{countdown_bg}; border:1px solid {countdown_border};
        border-radius:16px; padding:28px 20px; text-align:center; margin-bottom:16px;'>
            <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{countdown_color}; margin-bottom:16px;'>
                ⏱ ESTIMATED TIME TO MAJOR FAULT
            </div>
            <div class="{'countdown-critical' if fault == 'Major Fault' else ''}"
                 style='display:flex; justify-content:center; gap:16px; margin-bottom:16px;'>
                <div style='background:#080d1a; border:1px solid {countdown_color}33;
                border-radius:12px; padding:16px 20px;'>
                    <div style='font-size:48px; font-weight:900; color:{countdown_color};
                    font-family:JetBrains Mono; line-height:1;'>{days_int:03d}</div>
                    <div style='font-size:10px; color:#3d5a7a; letter-spacing:2px; margin-top:6px;'>DAYS</div>
                </div>
                <div style='font-size:36px; color:{countdown_color}; align-self:center; font-weight:300;'>:</div>
                <div style='background:#080d1a; border:1px solid {countdown_color}33;
                border-radius:12px; padding:16px 20px;'>
                    <div style='font-size:48px; font-weight:900; color:{countdown_color};
                    font-family:JetBrains Mono; line-height:1;'>{hours_int:02d}</div>
                    <div style='font-size:10px; color:#3d5a7a; letter-spacing:2px; margin-top:6px;'>HOURS</div>
                </div>
            </div>
            <div style='display:flex; align-items:center; justify-content:center; gap:8px; margin-bottom:12px;'>
                <div class="{pulse_class}" style='width:10px; height:10px; background:{countdown_color};'></div>
                <span style='font-size:12px; font-weight:700; color:{urgency_color}; letter-spacing:1px;'>{urgency_text}</span>
            </div>
            <div style='font-size:11px; color:#3d5a7a; line-height:1.6;'>{action_text}</div>
            <div style='margin-top:12px; padding-top:12px; border-top:1px solid #0f2040;
            font-size:11px; color:#1e3a5f;'>
                Based on {rul:,} cycles RUL ÷ {daily_cycles:,} daily cycles
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Probability + Sensor Status ──
    with g3:
        st.markdown('<div class="section-title">Fault Probability</div>', unsafe_allow_html=True)
        probs = prediction['class_probs']
        colors_p = {'No Fault':'#10b981','Minor Fault':'#f59e0b','Major Fault':'#ef4444'}
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(
            x=list(probs.values()), y=list(probs.keys()), orientation='h',
            marker_color=[colors_p.get(k,'#3b82f6') for k in probs.keys()],
            marker_line_width=0,
            text=[f"{v:.1%}" for v in probs.values()], textposition='outside',
            textfont=dict(size=12, color='#64748b', family='JetBrains Mono')
        ))
        fig_p.update_layout(
            paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
            height=160, margin=dict(l=0,r=60,t=10,b=10),
            xaxis=dict(range=[0,1.2], showgrid=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False, showline=False), showlegend=False,
        )
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="section-title">Sensor Status</div>', unsafe_allow_html=True)
        sensors_display = [
            ('Vibration', vib,  gc["vib_limit"],  'mm/s', False),
            ('Temp',      temp, gc["temp_limit"],  '°C',   False),
            ('Wear',      wear, gc["wear_limit"],  'mm',   False),
            ('Lubric.',   lube, gc["lube_limit"],  '',     True),
            ('Effic.',    eff,  gc["eff_limit"],   '%',    True),
        ]
        for name, val, limit, unit, inv in sensors_display:
            is_bad = (val < limit) if inv else (val > limit)
            pct    = min(100, (val/limit*100))
            color  = "#ef4444" if is_bad else "#10b981"
            st.markdown(f"""
            <div class="sensor-card {'sensor-card-bad' if is_bad else ''}">
                <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                    <span style='font-size:11px; color:#3d5a7a;'>{'🔴' if is_bad else '🟢'} {name}</span>
                    <span style='font-size:11px; font-weight:700; color:{color};
                    font-family:"JetBrains Mono",monospace;'>{val:.2f}{unit}</span>
                </div>
                <div style='background:#0f2040; border-radius:3px; height:3px; overflow:hidden;'>
                    <div style='width:{min(100,abs(pct))}%; background:{color}; height:100%; border-radius:3px;'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # ── AI Copilot below ──
    st.markdown("<div style='margin:24px 0 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 AI Copilot — Ask GearMind</div>', unsafe_allow_html=True)

    col_chat, col_quick = st.columns([3, 1])
    with col_quick:
        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
        suggestions = ["Why did this fault happen?", "What action should I take?",
                       "How long until failure?", "Explain SHAP values", "Root cause analysis"]
        for q in suggestions:
            if st.button(q, key=f"sq2_{q[:12]}"):
                st.session_state.pending_q = q

    with col_chat:
        if 'chat_history' not in st.session_state: st.session_state.chat_history = []
        if 'msgs_display' not in st.session_state: st.session_state.msgs_display = []
        if 'pending_q'    not in st.session_state: st.session_state.pending_q    = ""

        if not st.session_state.msgs_display:
            chat_body = f"""
            <div class="chat-empty">
                <div class="chat-empty-icon">🤖</div>
                <div class="chat-empty-title">GearMind AI Ready</div>
                <div class="chat-empty-sub">
                    Monitoring <strong style="color:#1e3a5f">{gear_name}</strong> ({gtype})<br>
                    Status: <strong style="color:{badge_color}">{fault}</strong> · {conf:.0%} confidence<br>
                    Health Score: <strong style="color:{gauge_color}">{score}/100</strong>
                </div>
            </div>"""
        else:
            chat_body = ""
            for msg in st.session_state.msgs_display:
                if msg['role'] == 'user':
                    chat_body += f'<div class="msg-wrapper-user"><div class="msg-meta msg-meta-user">YOU</div><div class="msg-bubble-user">{msg["content"]}</div></div>'
                else:
                    chat_body += f'<div class="msg-wrapper-ai"><div class="msg-meta msg-meta-ai"><span style="width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block;"></span>GEARMIND AI</div><div class="msg-bubble-ai">{md_to_html(msg["content"])}</div></div>'

        st.markdown(f"""
        <div class="chat-wrapper">
            <div class="chat-header-bar">
                <div class="chat-dot chat-dot-red"></div>
                <div class="chat-dot chat-dot-yellow"></div>
                <div class="chat-dot chat-dot-green"></div>
                <span style='margin-left:8px; font-size:12px; color:#3d5a7a; font-weight:600; letter-spacing:1px;'>
                    AI COPILOT — {gear_name} ({gtype}) · LLaMA 3.3 70B via Groq
                </span>
            </div>
            <div class="chat-messages">{chat_body}</div>
        </div>""", unsafe_allow_html=True)

        user_input  = st.text_area("Message", value=st.session_state.pending_q,
            placeholder=f"Ask anything about {gear_name}...", height=80,
            label_visibility="collapsed", key="chat_input_area")
        sc2, cc2 = st.columns([5, 1])
        send_clicked  = sc2.button("Send Message ↑", type="primary", use_container_width=True)
        clear_clicked = cc2.button("🗑", use_container_width=True)

        if clear_clicked:
            st.session_state.chat_history = []
            st.session_state.msgs_display = []
            st.session_state.pending_q    = ""
            st.rerun()

        final_input = (user_input or st.session_state.pending_q).strip()
        if send_clicked and final_input:
            st.session_state.pending_q = ""
            st.session_state.msgs_display.append({'role': 'user', 'content': final_input})
            with st.spinner(""):
                try:
                    response = ask_gearmind(final_input, prediction, gear_name,
                                            chat_history=st.session_state.chat_history)
                except Exception as e:
                    response = f"⚠️ Error: {str(e)}"
            st.session_state.chat_history.extend([
                {"role": "user",      "content": final_input},
                {"role": "assistant", "content": response}
            ])
            st.session_state.msgs_display.append({'role': 'ai', 'content': response})
            st.rerun()

# ════════════════════════════════════════════════════════
# TAB 2 — COST IMPACT (NEW)
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">💰 Maintenance Cost Impact Calculator</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#3d5a7a; font-size:13px; margin-bottom:24px;'>Real-time financial analysis showing exactly how much GearMind saves for {gtype} gear — {gear_name}</p>", unsafe_allow_html=True)

    ci1, ci2, ci3 = st.columns(3)

    with ci1:
        st.markdown(f"""
        <div style='background:rgba(16,185,129,0.08); border:2px solid rgba(16,185,129,0.3);
        border-radius:16px; padding:28px; text-align:center;'>
            <div style='font-size:13px; font-weight:700; color:#10b981; letter-spacing:1px; margin-bottom:16px;'>
                ✅ PREVENTIVE MAINTENANCE<br><span style='font-size:10px; color:#3d5a7a;'>Act Now — Recommended</span>
            </div>
            <div style='font-size:48px; font-weight:900; color:#10b981; font-family:JetBrains Mono;'>
                ₹{repair_now:,}
            </div>
            <div style='font-size:12px; color:#3d5a7a; margin-top:8px;'>One-time repair cost</div>
            <div style='margin-top:20px; display:flex; flex-direction:column; gap:8px; text-align:left;'>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Downtime</span>
                    <span style='color:#10b981; font-weight:600;'>4-6 hours</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Production Loss</span>
                    <span style='color:#10b981; font-weight:600;'>Minimal</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Risk</span>
                    <span style='color:#10b981; font-weight:600;'>Low</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    with ci2:
        st.markdown(f"""
        <div style='background:rgba(245,158,11,0.08); border:2px solid rgba(245,158,11,0.3);
        border-radius:16px; padding:28px; text-align:center;'>
            <div style='font-size:13px; font-weight:700; color:#f59e0b; letter-spacing:1px; margin-bottom:16px;'>
                ⚠️ DELAYED MAINTENANCE<br><span style='font-size:10px; color:#3d5a7a;'>Wait 1 Month</span>
            </div>
            <div style='font-size:48px; font-weight:900; color:#f59e0b; font-family:JetBrains Mono;'>
                ₹{delay_cost:,}
            </div>
            <div style='font-size:12px; color:#3d5a7a; margin-top:8px;'>Overhaul cost if delayed</div>
            <div style='margin-top:20px; display:flex; flex-direction:column; gap:8px; text-align:left;'>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Downtime</span>
                    <span style='color:#f59e0b; font-weight:600;'>1-2 days</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Production Loss</span>
                    <span style='color:#f59e0b; font-weight:600;'>Significant</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Risk</span>
                    <span style='color:#f59e0b; font-weight:600;'>Medium-High</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    with ci3:
        st.markdown(f"""
        <div style='background:rgba(239,68,68,0.08); border:2px solid rgba(239,68,68,0.3);
        border-radius:16px; padding:28px; text-align:center;'>
            <div style='font-size:13px; font-weight:700; color:#ef4444; letter-spacing:1px; margin-bottom:16px;'>
                🔴 COMPLETE FAILURE<br><span style='font-size:10px; color:#3d5a7a;'>No Maintenance</span>
            </div>
            <div style='font-size:48px; font-weight:900; color:#ef4444; font-family:JetBrains Mono;'>
                ₹{failure_cost:,}
            </div>
            <div style='font-size:12px; color:#3d5a7a; margin-top:8px;'>Full replacement cost</div>
            <div style='margin-top:20px; display:flex; flex-direction:column; gap:8px; text-align:left;'>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Downtime</span>
                    <span style='color:#ef4444; font-weight:600;'>5-7 days</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Production Loss</span>
                    <span style='color:#ef4444; font-weight:600;'>Severe</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span style='color:#3d5a7a;'>Risk</span>
                    <span style='color:#ef4444; font-weight:600;'>Critical</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:32px 0;'></div>", unsafe_allow_html=True)

    # ── Big Money Saved Banner ──
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.08));
    border:2px solid rgba(16,185,129,0.4); border-radius:20px; padding:32px; text-align:center;'>
        <div style='font-size:14px; font-weight:700; color:#10b981; letter-spacing:2px; margin-bottom:12px;'>
            💰 TOTAL SAVINGS BY USING GEARMIND AI
        </div>
        <div style='font-size:64px; font-weight:900; color:#10b981; font-family:JetBrains Mono;
        text-shadow: 0 0 40px rgba(16,185,129,0.4);'>
            ₹{money_saved:,}
        </div>
        <div style='font-size:14px; color:#3d5a7a; margin-top:8px;'>
            Saved per gear unit by catching faults early vs reactive replacement
        </div>
        <div style='display:flex; justify-content:center; gap:40px; margin-top:24px;'>
            <div style='text-align:center;'>
                <div style='font-size:28px; font-weight:800; color:#3b82f6; font-family:JetBrains Mono;'>{downtime_prevented_hrs}h</div>
                <div style='font-size:11px; color:#3d5a7a;'>Downtime Prevented</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:28px; font-weight:800; color:#a78bfa; font-family:JetBrains Mono;'>{rul:,}</div>
                <div style='font-size:11px; color:#3d5a7a;'>Remaining Cycles</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:28px; font-weight:800; color:#f59e0b; font-family:JetBrains Mono;'>{days_int}d</div>
                <div style='font-size:11px; color:#3d5a7a;'>Days to Act</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:28px; font-weight:800; color:#10b981; font-family:JetBrains Mono;'>{5*money_saved//100000}L+</div>
                <div style='font-size:11px; color:#3d5a7a;'>Fleet Annual Savings</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:32px 0;'></div>", unsafe_allow_html=True)

    # ── Cost comparison bar chart ──
    fig_cost = go.Figure()
    categories = ['Preventive\n(Act Now)', 'Delayed\n(1 Month)', 'Failure\n(No Action)']
    values = [repair_now, delay_cost, failure_cost]
    colors_cost = ['#10b981', '#f59e0b', '#ef4444']
    fig_cost.add_trace(go.Bar(
        x=categories, y=values,
        marker_color=colors_cost, marker_line_width=0,
        text=[f"₹{v:,}" for v in values], textposition='outside',
        textfont=dict(color='#94a3b8', size=13, family='JetBrains Mono')
    ))
    fig_cost.update_layout(
        title=f'{gtype} Gear — Cost Comparison (INR)',
        paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
        height=380, xaxis=dict(gridcolor='#0f2040'),
        yaxis=dict(gridcolor='#0f2040', title='Cost (INR)', tickprefix='₹'),
        margin=dict(t=50, b=20)
    )
    st.plotly_chart(fig_cost, use_container_width=True)
    st.caption(f"💡 GearMind AI saves ₹{money_saved:,} per gear unit by enabling preventive maintenance decisions")

# ════════════════════════════════════════════════════════
# TAB 3 — SHAP + LIME
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Explainable AI — SHAP Feature Importance</div>', unsafe_allow_html=True)
    if prediction['shap_values']:
        shap_df = pd.DataFrame([
            {'Feature': k, 'SHAP Value': v}
            for k, v in sorted(prediction['shap_values'].items(), key=lambda x: abs(x[1]), reverse=True)
        ])
        c1, c2 = st.columns([3,2])
        with c1:
            bar_colors = ['#ef4444' if v > 0 else '#10b981' for v in shap_df['SHAP Value']]
            fig = go.Figure(go.Bar(
                x=shap_df['SHAP Value'], y=shap_df['Feature'], orientation='h',
                marker_color=bar_colors, marker_line_width=0,
                text=[f"{v:+.4f}" for v in shap_df['SHAP Value']], textposition='outside',
                textfont=dict(family='JetBrains Mono', size=11, color='#64748b')
            ))
            fig.add_vline(x=0, line_color='#1e3a5f', line_width=1)
            fig.update_layout(title=f'SHAP Waterfall — {gear_name} ({gtype}) ({fault})',
                paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
                height=380, xaxis=dict(gridcolor='#0f2040', title='SHAP Impact'),
                yaxis=dict(gridcolor='#0f2040'), margin=dict(t=40,b=20,r=80))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟢 Green = healthy factor | 🔴 Red = risk factor")

        with c2:
            st.markdown('<div class="section-title">Feature Impact Cards</div>', unsafe_allow_html=True)
            for _, row in shap_df.iterrows():
                val = row['SHAP Value']
                color = "#ef4444" if val > 0 else "#10b981"
                direction = "↑ Toward Fault" if val > 0 else "↓ Away from Fault"
                bar_w = min(100, int(abs(val)*250))
                st.markdown(f"""
                <div style='background:#0d1829; border:1px solid #0f2040; border-radius:8px;
                padding:10px 12px; margin-bottom:8px;'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                        <span style='font-size:12px; color:#3d5a7a;'>{row['Feature']}</span>
                        <span style='font-size:11px; color:{color}; font-family:monospace; font-weight:700;'>{val:+.4f}</span>
                    </div>
                    <div style='background:#0f2040; border-radius:3px; height:5px; overflow:hidden; margin-bottom:5px;'>
                        <div style='width:{bar_w}%; background:linear-gradient(90deg,{color}88,{color}); height:100%; border-radius:3px;'></div>
                    </div>
                    <div style='font-size:10px; color:{color}; font-weight:600;'>{direction}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("Run `python xai/explain.py` to enable SHAP.")

    st.markdown("<div style='margin:32px 0 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">LIME — Cross-Validation of SHAP</div>', unsafe_allow_html=True)

    try:
        import lime, lime.lime_tabular
        shap_arts = joblib.load("xai/shap_artifacts.pkl")
        X_sample  = shap_arts["X_sample"]
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_sample, feature_names=FEATURE_COLS,
            class_names=list(arts["le"].classes_), mode="classification",
            discretize_continuous=True, random_state=42)
        input_scaled = arts["scaler"].transform(np.array([sensor_values[f] for f in FEATURE_COLS]).reshape(1,-1))[0]
        pred_encoded = arts["model"].predict(input_scaled.reshape(1,-1))[0]
        lime_result  = lime_explainer.explain_instance(data_row=input_scaled,
            predict_fn=arts["model"].predict_proba, num_features=8, labels=[pred_encoded])
        lime_list = lime_result.as_list(label=pred_encoded)
        lime_df   = pd.DataFrame(lime_list, columns=["Rule","Weight"]).sort_values("Weight", key=abs, ascending=False)
        no_fault_idx = list(arts["le"].classes_).index("No Fault") if "No Fault" in list(arts["le"].classes_) else -1
        if pred_encoded == no_fault_idx:
            lime_df["Weight"] = -lime_df["Weight"]

        lc1, lc2 = st.columns([3,2])
        with lc1:
            lime_colors = ["#ef4444" if w > 0 else "#10b981" for w in lime_df["Weight"]]
            fig_lime = go.Figure(go.Bar(
                x=lime_df["Weight"], y=lime_df["Rule"], orientation="h",
                marker_color=lime_colors, marker_line_width=0,
                text=[f"{w:+.4f}" for w in lime_df["Weight"]], textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color="#64748b")))
            fig_lime.add_vline(x=0, line_color="#1e3a5f", line_width=1)
            fig_lime.update_layout(title=f"LIME Explanation — {gear_name} ({gtype})",
                paper_bgcolor="#0d1829", plot_bgcolor="#0d1829", font_color="#64748b",
                height=380, xaxis=dict(gridcolor="#0f2040", title="LIME Weight"),
                yaxis=dict(gridcolor="#0f2040"), margin=dict(t=40,b=20,r=80))
            st.plotly_chart(fig_lime, use_container_width=True)

        with lc2:
            st.markdown('<div class="section-title">SHAP vs LIME Agreement</div>', unsafe_allow_html=True)
            if prediction["shap_values"]:
                shap_top = sorted(prediction["shap_values"].items(), key=lambda x: abs(x[1]), reverse=True)[:5]
                for i, (sf, sv2) in enumerate(shap_top):
                    sc_c = "#ef4444" if sv2 > 0 else "#10b981"
                    lw   = lime_df["Weight"].iloc[i] if i < len(lime_df) else 0
                    lc_c = "#ef4444" if lw > 0 else "#10b981"
                    agree = "✅" if (sv2 > 0) == (lw > 0) else "⚠️"
                    st.markdown(f"""
                    <div style='background:#0d1829; border:1px solid #0f2040; border-radius:8px;
                    padding:10px 12px; margin-bottom:8px;'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                            <span style='font-size:11px; color:#3d5a7a;'>{sf}</span>
                            <span>{agree}</span>
                        </div>
                        <div style='display:flex; justify-content:space-between;'>
                            <span style='font-size:11px; color:{sc_c}; font-family:monospace;'>SHAP: {sv2:+.4f}</span>
                            <span style='font-size:11px; color:{lc_c}; font-family:monospace;'>LIME: {lw:+.4f}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                agree_count = sum(1 for i,(sf,sv2) in enumerate(shap_top)
                                  if i < len(lime_df) and (sv2>0)==(lime_df["Weight"].iloc[i]>0))
                agree_pct   = agree_count / min(5,len(shap_top)) * 100
                ac = "#10b981" if agree_pct >= 80 else "#f59e0b"
                st.markdown(f"""
                <div style='background:{ac}11; border:1px solid {ac}44; border-radius:8px;
                padding:12px; text-align:center; margin-top:8px;'>
                    <div style='font-size:28px; font-weight:800; color:{ac};'>{agree_pct:.0f}%</div>
                    <div style='font-size:11px; color:{ac};'>SHAP-LIME Agreement</div>
                    <div style='font-size:10px; color:#3d5a7a; margin-top:4px;'>
                        {"✅ Trustworthy explanation" if agree_pct >= 80 else "⚠️ Review borderline features"}
                    </div>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"LIME unavailable: {e}")

# ════════════════════════════════════════════════════════
# TAB 4 — MODEL COMPARISON
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">5-Model Performance Comparison</div>', unsafe_allow_html=True)
    if 'comparison' in arts:
        comp_df = pd.DataFrame(arts['comparison']).T.reset_index()
        comp_df.columns = ['Model','Accuracy','F1 Score','ROC-AUC','CV Mean','CV Std']
        comp_df = comp_df.sort_values('ROC-AUC', ascending=False).reset_index(drop=True)
        comp_df['Rank'] = ['1st','2nd','3rd','4th','5th'][:len(comp_df)]
        st.dataframe(
            comp_df[['Rank','Model','CV Mean','Accuracy','F1 Score','ROC-AUC','CV Std']]
            .style.format({'CV Mean':'{:.4f}','Accuracy':'{:.4f}','F1 Score':'{:.4f}','ROC-AUC':'{:.4f}','CV Std':'{:.4f}'})
            .highlight_max(subset=['Accuracy','F1 Score','ROC-AUC'], color='#0d2a1a'),
            use_container_width=True, hide_index=True, height=220)

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            for metric, color in [('Accuracy','#3b82f6'),('F1 Score','#10b981'),('ROC-AUC','#f59e0b')]:
                fig.add_trace(go.Bar(name=metric, x=comp_df['Model'], y=comp_df[metric],
                    marker_color=color, opacity=0.9, marker_line_width=0))
            fig.update_layout(barmode='group', title='Model Metrics Comparison',
                paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
                height=350, xaxis=dict(gridcolor='#0f2040'), yaxis=dict(gridcolor='#0f2040', range=[0.88,1.01]),
                legend=dict(bgcolor='#0d1829'), margin=dict(t=40,b=20))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=comp_df['Model'], y=comp_df['CV Mean'],
                error_y=dict(type='data', array=comp_df['CV Std'], visible=True, color='#3b82f6'),
                mode='markers+lines',
                marker=dict(size=12, color='#3b82f6', line=dict(color='#fff',width=2)),
                line=dict(color='#1e3a5f', width=2)))
            fig2.update_layout(title='Cross-Validation Stability (5-Fold)',
                paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
                height=350, xaxis=dict(gridcolor='#0f2040'), yaxis=dict(gridcolor='#0f2040', range=[0.88,1.01]),
                margin=dict(t=40,b=20))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)
        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown('<div class="section-title">Feature Importance — GBM</div>', unsafe_allow_html=True)
            try:
                if hasattr(arts['model'], 'feature_importances_'):
                    fi = arts['model'].feature_importances_
                    fi_df = pd.DataFrame({'Feature': FEATURE_COLS, 'Importance': fi}).sort_values('Importance', ascending=True)
                    fi_colors = ['#3b82f6' if i < len(fi_df)-3 else '#f59e0b' if i < len(fi_df)-1 else '#ef4444'
                                 for i in range(len(fi_df))]
                    fig_fi = go.Figure(go.Bar(x=fi_df['Importance'], y=fi_df['Feature'],
                        orientation='h', marker_color=fi_colors, marker_line_width=0,
                        text=[f"{v:.4f}" for v in fi_df['Importance']], textposition='outside',
                        textfont=dict(family='JetBrains Mono', size=11, color='#64748b')))
                    fig_fi.update_layout(paper_bgcolor='#0d1829', plot_bgcolor='#0d1829',
                        font_color='#64748b', height=320,
                        xaxis=dict(gridcolor='#0f2040'), yaxis=dict(gridcolor='#0f2040'),
                        margin=dict(t=20, b=20, r=80))
                    st.plotly_chart(fig_fi, use_container_width=True)
                    st.caption("🔴 Most important | 🟡 High | 🔵 Moderate")
            except Exception as e:
                st.warning(f"Feature importance error: {e}")

        with mc2:
            st.markdown('<div class="section-title">Confusion Matrix — 50,000 Samples</div>', unsafe_allow_html=True)
            try:
                from sklearn.metrics import confusion_matrix
                df_cm = pd.read_csv('data/helical_gear_dataset.csv')
                X_cm  = arts['scaler'].transform(df_cm[FEATURE_COLS].values)
                y_cm  = arts['le'].transform(df_cm['Fault Label'].values)
                cm    = confusion_matrix(y_cm, arts['model'].predict(X_cm))
                labels = list(arts['le'].classes_)
                fig_cm = go.Figure(go.Heatmap(
                    z=cm, x=[f'Pred: {l}' for l in labels], y=[f'True: {l}' for l in labels],
                    colorscale=[[0,'#070b14'],[0.5,'#1e3a5f'],[1,'#2563eb']],
                    text=cm, texttemplate='%{text}',
                    textfont=dict(size=14, color='white', family='JetBrains Mono'), showscale=True))
                fig_cm.update_layout(paper_bgcolor='#0d1829', plot_bgcolor='#0d1829',
                    font_color='#64748b', height=320, margin=dict(t=20, b=20))
                st.plotly_chart(fig_cm, use_container_width=True)
                st.caption("Strong diagonal = high accuracy")
            except Exception as e:
                st.warning(f"Confusion matrix error: {e}")

# ════════════════════════════════════════════════════════
# TAB 5 — WHAT-IF OPTIMIZER
# ════════════════════════════════════════════════════════
with tab5:
    from scipy.optimize import differential_evolution

    OPT_LABELS = ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)',
                  'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use']
    OPT_BOUNDS = [(10.0,120.0),(50.0,600.0),(0.5,30.0),(40.0,150.0),
                  (0.0,4.0),(0.05,1.0),(70.0,99.0),(0.0,100000.0)]
    OPT_UNITS  = ['kN','Nm','mm/s','°C','mm','','%','cycles']
    _live      = [load, torque, vib, temp, wear, lube, eff, float(cycles)]

    def _opt_predict_prob(raw_vals):
        sv = dict(zip(FEATURE_COLS, raw_vals))
        p  = predict_gear_health(sv)
        fault_map = {'No Fault': 0.05, 'Minor Fault': 0.55, 'Major Fault': 0.92}
        return fault_map.get(p['fault_label'], 0.5) * 100 + (1 - p['confidence']) * 10

    cur_prob_opt = _opt_predict_prob(_live)
    if cur_prob_opt < 30:   _cp_color = "#10b981"
    elif cur_prob_opt < 55: _cp_color = "#f59e0b"
    elif cur_prob_opt < 80: _cp_color = "#ef4444"
    else:                   _cp_color = "#ef4444"

    # ── Header ──
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(37,99,235,0.08),rgba(37,99,235,0.03));
    border:1px solid #1e3a5f; border-radius:14px; padding:20px 24px; margin-bottom:20px;'>
        <div style='font-size:16px; font-weight:800; color:#e2e8f0; margin-bottom:6px;'>
            🔧 What-If Optimizer — Safe Operating Zone Finder
        </div>
        <div style='font-size:13px; color:#3d5a7a; line-height:1.7;'>
            Answers: <strong style='color:#60a5fa'>"What is the minimum change to reach a safe operating zone?"</strong><br>
            Lock parameters you cannot change. The optimizer adjusts free ones using
            <strong style='color:#60a5fa'>Differential Evolution</strong> — a global search that avoids local minima.
        </div>
    </div>""", unsafe_allow_html=True)

    # ── KPI strip ──
    ok1, ok2, ok3, ok4 = st.columns(4)
    ok1.metric("Current Fault", fault)
    ok2.metric("Confidence", f"{conf:.1%}")
    ok3.metric("Health Score", f"{health_score_val}/100")
    ok4.metric("RUL (cycles)", f"{rul:,}")
    st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)

    # ── Configure ──
    st.markdown('<div class="section-title">Configure Optimization</div>', unsafe_allow_html=True)
    cfg_l, cfg_r = st.columns([1, 2])
    with cfg_l:
        user_target = st.slider("Target Failure Probability (%)", 5, 50, 20, step=5,
            help="Optimizer finds the nearest safe operating point below this threshold.")
        gap = max(0, cur_prob_opt - user_target)
        st.markdown(f"""
        <div style='background:#080d1a; border:1px solid #0f2040; border-radius:10px;
        padding:16px; text-align:center; margin-top:12px;'>
            <div style='font-size:10px; color:#1e3a5f; letter-spacing:1.5px; margin-bottom:6px;'>GAP TO CLOSE</div>
            <div style='font-size:32px; font-weight:900; color:#3b82f6; font-family:JetBrains Mono;'>
                {gap:.1f}<span style='font-size:14px;'>pp</span>
            </div>
            <div style='font-size:11px; color:#3d5a7a; margin-top:4px;'>{cur_prob_opt:.1f}% → target {user_target}%</div>
        </div>""", unsafe_allow_html=True)

    with cfg_r:
        st.markdown("<p style='font-size:12px; font-weight:700; color:#e2e8f0; margin-bottom:8px;'>Parameter Lock Configuration</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:11px; color:#3d5a7a; margin-bottom:14px;'>☑ Checked = <span style='color:#ef4444;'>LOCKED</span> (fixed) &nbsp;·&nbsp; Unchecked = <span style='color:#10b981;'>FREE</span> (optimizer adjusts)</p>", unsafe_allow_html=True)
        lock_cols = st.columns(4)
        locks = {}
        for i, (lbl, unit) in enumerate(zip(OPT_LABELS, OPT_UNITS)):
            with lock_cols[i % 4]:
                short = lbl.split(' ')[0]
                locked = st.checkbox(short, value=False, key=f"optlock_{i}")
                locks[lbl] = locked
                val_now = _live[i]
                col = "#ef4444" if locked else "#10b981"
                icon = "🔒" if locked else "🟢"
                st.markdown(f"<div style='font-size:10px; color:{col}; margin-top:-4px;'>{icon} {val_now:.1f} {unit}</div>", unsafe_allow_html=True)

        free_n = sum(1 for v in locks.values() if not v)
        locked_n = sum(1 for v in locks.values() if v)
        st.markdown(f"<p style='font-size:12px; color:#3d5a7a; margin-top:8px;'>"
                    f"<strong style='color:#10b981;'>{free_n} free</strong> · "
                    f"<strong style='color:#ef4444;'>{locked_n} locked</strong></p>", unsafe_allow_html=True)

    st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

    # ── Sensitivity Preview ──
    st.markdown('<div class="section-title">Parameter Sensitivity — Leverage Analysis</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#3d5a7a; font-size:12px; margin-bottom:16px;'>How much does fault probability shift when each parameter is nudged ±5% of its range?</p>", unsafe_allow_html=True)

    sens_data = []
    for i, (lbl, (lo, hi)) in enumerate(zip(OPT_LABELS, OPT_BOUNDS)):
        step = (hi - lo) * 0.05
        base = _live.copy()
        p_up = base.copy(); p_up[i] = min(hi, base[i] + step)
        p_dn = base.copy(); p_dn[i] = max(lo, base[i] - step)
        eff_up = _opt_predict_prob(p_up) - cur_prob_opt
        eff_dn = _opt_predict_prob(p_dn) - cur_prob_opt
        lev = max(abs(eff_up), abs(eff_dn))
        sens_data.append(dict(label=lbl.split('(')[0].strip(), leverage=lev,
                               locked=locks[lbl], unit=OPT_UNITS[i]))
    sens_data.sort(key=lambda x: x["leverage"], reverse=True)

    fig_sens = go.Figure(go.Bar(
        x=[d["leverage"] for d in sens_data],
        y=[d["label"] for d in sens_data],
        orientation='h',
        marker_color=["#1e3a5f" if d["locked"] else
                      ("#ef4444" if d["leverage"] > 5 else
                       "#f59e0b" if d["leverage"] > 2 else "#10b981")
                      for d in sens_data],
        marker_line_width=0,
        text=[f"{d['leverage']:.2f} pp{'  🔒' if d['locked'] else ''}" for d in sens_data],
        textposition='outside',
        textfont=dict(size=10, color='#64748b', family='JetBrains Mono')
    ))
    fig_sens.update_layout(
        paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
        height=300, margin=dict(t=10, b=20, r=100),
        xaxis=dict(gridcolor='#0f2040', title='Max probability change per ±5% of range (pp)'),
        yaxis=dict(gridcolor='#0f2040'), showlegend=False
    )
    st.plotly_chart(fig_sens, use_container_width=True)

    top_s = sens_data[0]
    if top_s["locked"]:
        st.markdown(f"""<div style='background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3);
        border-radius:8px; padding:12px 16px; font-size:13px; color:#f59e0b; margin-bottom:16px;'>
        ⚠ <strong>Highest-leverage parameter ({top_s['label']}) is locked.</strong>
        Unlocking it gives the optimizer the most powerful lever to reduce risk.</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style='background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.3);
        border-radius:8px; padding:12px 16px; font-size:13px; color:#60a5fa; margin-bottom:16px;'>
        ⚡ <strong>{top_s['label']}</strong> is the most influential free parameter —
        a ±5% change shifts probability by up to <strong>{top_s['leverage']:.2f} pp</strong>.
        The optimizer will prioritise this lever.</div>""", unsafe_allow_html=True)

    # ── Run Button ──
    st.markdown('<div class="section-title">Run Optimizer</div>', unsafe_allow_html=True)
    if cur_prob_opt < user_target:
        st.markdown(f"""<div style='background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.3);
        border-radius:10px; padding:16px; font-size:13px; color:#10b981;'>
        ✅ <strong>Already safe.</strong> Current probability ({cur_prob_opt:.1f}%) is already below
        target ({user_target}%). Lower the target or raise a parameter in the sidebar.</div>""", unsafe_allow_html=True)
        run_opt = False
    else:
        rb1, rb2 = st.columns([2, 1])
        with rb1:
            run_opt = st.button("⚡  Find Safe Operating Point", type="primary", use_container_width=True)
        with rb2:
            if st.button("✕  Clear Result", use_container_width=True):
                st.session_state.opt_result = None
                st.rerun()

    # ── Optimizer Engine ──
    @st.cache_data(show_spinner="Running global optimizer…")
    def _run_gearmind_optimizer(live_tuple, locks_tuple, target, bounds_tuple):
        live_arr   = np.array(live_tuple, dtype=float)
        locked_arr = np.array(locks_tuple, dtype=bool)
        bounds_arr = np.array(bounds_tuple)
        ranges     = bounds_arr[:, 1] - bounds_arr[:, 0]
        free_idx   = np.where(~locked_arr)[0]
        free_bnds  = [tuple(bounds_arr[i]) for i in free_idx]
        if len(free_idx) == 0:
            return None, None, "All parameters locked — unlock at least one."

        def objective(x):
            cand = live_arr.copy()
            cand[free_idx] = x
            prob     = _opt_predict_prob(cand.tolist())
            prob_pen = max(0.0, prob - target) ** 2
            norm_chg = (x - live_arr[free_idx]) / ranges[free_idx]
            chg_pen  = 5.0 * float(np.sum(norm_chg ** 2))
            return prob_pen + chg_pen

        res     = differential_evolution(objective, bounds=free_bnds, seed=42,
                                         maxiter=300, tol=1e-4, popsize=12,
                                         mutation=(0.5, 1.2), recombination=0.9, polish=True)
        opt_arr = live_arr.copy()
        opt_arr[free_idx] = res.x
        opt_prob = _opt_predict_prob(opt_arr.tolist())
        return opt_arr.tolist(), opt_prob, None

    if "opt_result" not in st.session_state:
        st.session_state.opt_result = None

    if run_opt and cur_prob_opt >= user_target:
        if free_n == 0:
            st.error("All parameters are locked. Unlock at least one.")
        else:
            locks_tuple = tuple(locks[k] for k in OPT_LABELS)
            opt_vals_r, opt_prob_r, err = _run_gearmind_optimizer(
                tuple(_live), locks_tuple, user_target, tuple(map(tuple, OPT_BOUNDS))
            )
            if err:
                st.error(err)
            else:
                st.session_state.opt_result = dict(
                    opt_vals=opt_vals_r, opt_prob=opt_prob_r,
                    live_snapshot=list(_live), target_snapshot=user_target
                )

    # ── Results ──
    if st.session_state.get("opt_result"):
        _r       = st.session_state.opt_result
        opt_vals = _r["opt_vals"]
        opt_prob = _r["opt_prob"]
        _before  = _r["live_snapshot"]
        _tgt     = _r["target_snapshot"]
        before_prob = _opt_predict_prob(_before)
        reduction   = before_prob - opt_prob
        achieved    = opt_prob < _tgt

        if list(_live) != _before:
            st.markdown("""<div style='background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3);
            border-radius:8px; padding:10px 16px; font-size:12px; color:#f59e0b; margin-bottom:12px;'>
            ⚠ Sidebar values changed since last run. Press <em>Find Safe Operating Point</em> to recompute.</div>""",
            unsafe_allow_html=True)

        opt_color = "#10b981" if opt_prob < 30 else "#f59e0b" if opt_prob < 55 else "#ef4444"

        st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{"✅ Target Achieved" if achieved else "⚠ Best Reachable Point"}</div>',
                    unsafe_allow_html=True)

        # Before/After KPIs
        ra, rb, rc, rd = st.columns(4)
        ra.metric("Before", f"{before_prob:.1f}%")
        rb.metric("After (Optimized)", f"{opt_prob:.1f}%")
        rc.metric("Probability Reduction", f"−{reduction:.1f}pp")
        opt_hs  = max(0, 1.0 - opt_prob / 100)
        opt_rul = int(opt_hs * gc["daily_cycles"] * 10)
        rd.metric("Est. RUL After", f"{opt_rul:,} cycles")

        st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

        # Recommended changes
        st.markdown('<div class="section-title">Recommended Parameter Changes</div>', unsafe_allow_html=True)
        for i, (lbl, unit) in enumerate(zip(OPT_LABELS, OPT_UNITS)):
            before_v = _before[i]
            after_v  = opt_vals[i]
            delta    = after_v - before_v
            lo, hi   = OPT_BOUNDS[i]
            pct_rng  = abs(delta) / (hi - lo) * 100
            if locks[lbl]:
                st.markdown(f"""<div style='background:#080d1a; border-left:3px solid #1e3a5f;
                border-radius:0 8px 8px 0; padding:10px 18px; margin:5px 0; font-size:13px; color:#3d5a7a;'>
                🔒 <strong>{lbl}</strong> — fixed at <strong style='color:#e2e8f0;'>{before_v:.2f} {unit}</strong></div>""",
                unsafe_allow_html=True)
            elif abs(delta) < 0.01:
                st.markdown(f"""<div style='background:#080d1a; border-left:3px solid #1e3a5f;
                border-radius:0 8px 8px 0; padding:10px 18px; margin:5px 0; font-size:13px; color:#3d5a7a;'>
                ➖ <strong>{lbl}</strong> — no change needed · stays at <strong style='color:#e2e8f0;'>{before_v:.2f} {unit}</strong></div>""",
                unsafe_allow_html=True)
            elif delta < 0:
                st.markdown(f"""<div style='background:rgba(16,185,129,0.06); border-left:3px solid #10b981;
                border-radius:0 8px 8px 0; padding:10px 18px; margin:5px 0; font-size:13px; color:#10b981;'>
                ⬇ <strong>{lbl}</strong> — reduce from
                <strong style='color:#e2e8f0;'>{before_v:.2f} → {after_v:.2f} {unit}</strong>
                &nbsp;·&nbsp; decrease by <strong>{abs(delta):.2f} {unit}</strong>
                <span style='color:#3d5a7a;'>({pct_rng:.1f}% of range)</span></div>""",
                unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style='background:rgba(239,68,68,0.06); border-left:3px solid #ef4444;
                border-radius:0 8px 8px 0; padding:10px 18px; margin:5px 0; font-size:13px; color:#ef4444;'>
                ⬆ <strong>{lbl}</strong> — increase from
                <strong style='color:#e2e8f0;'>{before_v:.2f} → {after_v:.2f} {unit}</strong>
                &nbsp;·&nbsp; increase by <strong>{abs(delta):.2f} {unit}</strong>
                <span style='color:#3d5a7a;'>({pct_rng:.1f}% of range)</span></div>""",
                unsafe_allow_html=True)

        st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

        # Before vs After bar chart
        st.markdown('<div class="section-title">Before vs After — Parameter Comparison</div>', unsafe_allow_html=True)
        cmp_l, cmp_r = st.columns(2)
        norm_before = [(v - lo) / (hi - lo) for v, (lo, hi) in zip(_before, OPT_BOUNDS)]
        norm_after  = [(v - lo) / (hi - lo) for v, (lo, hi) in zip(opt_vals, OPT_BOUNDS)]
        for col, norms, vals, title, prob_show in [
            (cmp_l, norm_before, _before, "Before", before_prob),
            (cmp_r, norm_after,  opt_vals, "After (Optimized)", opt_prob),
        ]:
            with col:
                col_c = "#10b981" if prob_show < 30 else "#f59e0b" if prob_show < 55 else "#ef4444"
                st.markdown(f"<div style='font-size:13px; font-weight:700; color:#e2e8f0; margin-bottom:12px;'>{title} — <span style='color:{col_c};'>{prob_show:.1f}%</span></div>", unsafe_allow_html=True)
                for lbl, val, unit, norm in zip(OPT_LABELS, vals, OPT_UNITS, norms):
                    bar_col = "#10b981" if norm < 0.4 else "#f59e0b" if norm < 0.65 else "#ef4444"
                    short = lbl.split('(')[0].strip()
                    st.markdown(f"""
                    <div style='margin-bottom:10px;'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                            <span style='font-size:11px; color:#3d5a7a;'>{short}</span>
                            <span style='font-size:11px; font-weight:700; color:#e2e8f0; font-family:JetBrains Mono;'>{val:.1f} {unit}</span>
                        </div>
                        <div style='background:#0f2040; border-radius:3px; height:6px; overflow:hidden;'>
                            <div style='width:{min(norm*100,100):.1f}%; height:100%; background:{bar_col}; border-radius:3px;'></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

        # Radar chart
        st.markdown('<div class="section-title">Operating Profile — Radar View</div>', unsafe_allow_html=True)
        short_labels = [lbl.split('(')[0].strip() for lbl in OPT_LABELS]
        theta    = short_labels + [short_labels[0]]
        r_before = norm_before + [norm_before[0]]
        r_after  = norm_after  + [norm_after[0]]
        fig_rad  = go.Figure()
        fig_rad.add_trace(go.Scatterpolar(r=r_before, theta=theta, fill="toself", name="Before",
            line=dict(color="#ef4444", width=2), fillcolor="rgba(239,68,68,0.1)"))
        fig_rad.add_trace(go.Scatterpolar(r=r_after, theta=theta, fill="toself", name="After",
            line=dict(color="#10b981", width=2), fillcolor="rgba(16,185,129,0.12)"))
        fig_rad.add_trace(go.Scatterpolar(r=[0.75]*len(theta), theta=theta, mode="lines",
            line=dict(color="#f59e0b", width=1.5, dash="dot"), name="Danger (75%)", hoverinfo="skip"))
        fig_rad.update_layout(
            polar=dict(bgcolor="#0d1829",
                radialaxis=dict(visible=True, range=[0,1], tickvals=[0.25,0.5,0.75,1.0],
                    ticktext=["25%","50%","75%","100%"], tickfont=dict(color="#3d5a7a", size=9),
                    gridcolor="#0f2040", linecolor="#1e3a5f"),
                angularaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="#0f2040", linecolor="#1e3a5f")),
            paper_bgcolor="#080d1a", height=400,
            margin=dict(t=30, b=30, l=40, r=40),
            legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)",
                        orientation="h", yanchor="bottom", y=-0.18, x=0.15),
            font=dict(color="#94a3b8")
        )
        st.plotly_chart(fig_rad, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 6 — HISTORY
# ════════════════════════════════════════════════════════
with tab6:
    import sqlite3
    from datetime import datetime as dt

    DB_PATH = "gear_history.db"

    def init_db():
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        # Check if table exists and has the right columns; if not, recreate it
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gear_log'")
        exists = cur.fetchone()
        if exists:
            cur.execute("PRAGMA table_info(gear_log)")
            cols = [row[1] for row in cur.fetchall()]
            if "gear_unit" not in cols:
                cur.execute("DROP TABLE gear_log")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gear_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT NOT NULL,
                gear_type   TEXT,
                gear_unit   TEXT,
                fault_label TEXT,
                confidence  REAL,
                health_score INTEGER,
                rul_cycles  INTEGER,
                load_kn     REAL,
                torque_nm   REAL,
                vibration   REAL,
                temperature REAL,
                wear        REAL,
                lubrication REAL,
                efficiency  REAL,
                cycles      INTEGER
            )
        """)
        con.commit(); con.close()

    def log_reading_gm(gear_type, gear_unit, fault_label, confidence,
                       health_score, rul_cycles, sv):
        init_db()
        con = sqlite3.connect(DB_PATH)
        con.execute("""
            INSERT INTO gear_log
                (timestamp, gear_type, gear_unit, fault_label, confidence,
                 health_score, rul_cycles, load_kn, torque_nm, vibration,
                 temperature, wear, lubrication, efficiency, cycles)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (dt.now().strftime("%Y-%m-%d %H:%M:%S"), gear_type, gear_unit,
              fault_label, confidence, health_score, rul_cycles,
              sv['Load (kN)'], sv['Torque (Nm)'], sv['Vibration RMS (mm/s)'],
              sv['Temperature (°C)'], sv['Wear (mm)'], sv['Lubrication Index'],
              sv['Efficiency (%)'], sv['Cycles in Use']))
        con.commit(); con.close()

    def load_history_gm():
        init_db()
        con = sqlite3.connect(DB_PATH)
        df  = pd.read_sql_query("SELECT * FROM gear_log ORDER BY timestamp DESC", con)
        con.close()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def clear_history_gm():
        con = sqlite3.connect(DB_PATH)
        con.execute("DELETE FROM gear_log")
        con.commit(); con.close()

    # Auto-log on every unique config change
    _sig = (gtype, gear_id, fault, conf, health_score_val, rul,
            load, torque, vib, temp, wear, lube, eff, cycles)
    if "last_logged_sig_gm" not in st.session_state:
        st.session_state.last_logged_sig_gm = None
    if _sig != st.session_state.last_logged_sig_gm:
        log_reading_gm(gtype, gear_name, fault, conf, health_score_val, rul, sensor_values)
        st.session_state.last_logged_sig_gm = _sig

    hist_df = load_history_gm()

    # ── Header ──
    h_l, h_r = st.columns([3, 1])
    with h_l:
        st.markdown('<div class="section-title">📈 Historical Data Logger & Trend Analysis</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#3d5a7a; font-size:13px;'>Readings are <strong style='color:#60a5fa;'>logged automatically</strong> whenever you change any slider or setting. Each unique configuration is saved to a local SQLite database.</p>", unsafe_allow_html=True)
    with h_r:
        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        if st.button("🗑 Clear All History", use_container_width=True):
            clear_history_gm()
            st.rerun()

    if hist_df.empty:
        st.markdown("""<div style='background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3);
        border-radius:10px; padding:16px; font-size:13px; color:#f59e0b; margin-top:12px;'>
        ⚠ <strong>No data yet.</strong> Adjust any slider — readings are saved automatically.</div>""",
        unsafe_allow_html=True)
    else:
        total_logs   = len(hist_df)
        failure_logs = int((hist_df["fault_label"] == "Major Fault").sum())
        avg_score    = hist_df["health_score"].mean()
        avg_rul      = hist_df["rul_cycles"].mean()

        hk1, hk2, hk3, hk4 = st.columns(4)
        hk1.metric("Total Readings", total_logs)
        hk2.metric("🔴 Major Fault Events", failure_logs)
        hk3.metric("Avg Health Score", f"{avg_score:.0f}/100")
        hk4.metric("Avg RUL", f"{avg_rul:,.0f} cycles")
        st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

        plot_df = hist_df.sort_values("timestamp").reset_index(drop=True)
        plot_df["reading_no"] = range(1, len(plot_df) + 1)

        # Failure probability trend
        st.markdown('<div class="section-title">Health Score Over Time</div>', unsafe_allow_html=True)
        fault_color_map = {"No Fault": "#10b981", "Minor Fault": "#f59e0b", "Major Fault": "#ef4444"}
        pt_colors = [fault_color_map.get(f, "#3b82f6") for f in plot_df["fault_label"]]
        fig_hs = go.Figure()
        fig_hs.add_hrect(y0=70, y1=100, fillcolor="rgba(16,185,129,0.05)", line_width=0)
        fig_hs.add_hrect(y0=40, y1=70,  fillcolor="rgba(245,158,11,0.05)", line_width=0)
        fig_hs.add_hrect(y0=0,  y1=40,  fillcolor="rgba(239,68,68,0.05)",  line_width=0)
        fig_hs.add_hline(y=70, line_dash="dot", line_color="#10b981", line_width=1,
                         annotation_text="Safe (70)", annotation_font_color="#10b981", annotation_font_size=10)
        fig_hs.add_hline(y=40, line_dash="dot", line_color="#ef4444", line_width=1,
                         annotation_text="Critical (40)", annotation_font_color="#ef4444", annotation_font_size=10)
        fig_hs.add_trace(go.Scatter(
            x=plot_df["reading_no"], y=plot_df["health_score"],
            mode="lines+markers",
            line=dict(color="#3b82f6", width=2),
            marker=dict(color=pt_colors, size=9, line=dict(color="#080d1a", width=1.5)),
            text=plot_df["timestamp"].dt.strftime("%d %b %H:%M"),
            hovertemplate="<b>Reading #%{x}</b><br>%{text}<br>Health: %{y}/100<extra></extra>",
        ))
        fig_hs.update_layout(
            height=300, paper_bgcolor="#0d1829", plot_bgcolor="#080d1a",
            margin=dict(t=20, b=40, l=10, r=80),
            xaxis=dict(title="Reading #", color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
            yaxis=dict(title="Health Score", range=[0,105], color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
            showlegend=False
        )
        st.plotly_chart(fig_hs, use_container_width=True)

        # RUL Trend
        st.markdown('<div class="section-title">RUL Over Time</div>', unsafe_allow_html=True)
        fig_rul_h = go.Figure()
        fig_rul_h.add_trace(go.Scatter(
            x=plot_df["reading_no"], y=plot_df["rul_cycles"],
            mode="lines+markers",
            line=dict(color="#10b981", width=2),
            marker=dict(color=pt_colors, size=9, line=dict(color="#080d1a", width=1.5)),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.06)",
            hovertemplate="<b>Reading #%{x}</b><br>RUL: %{y:,} cycles<extra></extra>",
        ))
        fig_rul_h.update_layout(
            height=260, paper_bgcolor="#0d1829", plot_bgcolor="#080d1a",
            margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(title="Reading #", color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
            yaxis=dict(title="RUL (cycles)", color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
            showlegend=False
        )
        st.plotly_chart(fig_rul_h, use_container_width=True)

        # Sensor param trends
        st.markdown('<div class="section-title">Sensor Parameter Trends</div>', unsafe_allow_html=True)
        param_opts = {
            "Vibration (mm/s)": ("vibration", "mm/s", gc["vib_limit"],  "#f472b6"),
            "Temperature (°C)": ("temperature","°C",  gc["temp_limit"], "#fb923c"),
            "Wear (mm)":         ("wear",      "mm",   gc["wear_limit"], "#facc15"),
            "Load (kN)":         ("load_kn",   "kN",   90.0,            "#60a5fa"),
        }
        sel_param = st.selectbox("Select Parameter", list(param_opts.keys()), label_visibility="collapsed")
        col_key, unit_h, danger_th, line_col_h = param_opts[sel_param]
        breach_mask = plot_df[col_key] >= danger_th
        fig_par = go.Figure()
        fig_par.add_hline(y=danger_th, line_dash="dash", line_color="#ef4444", line_width=1.5,
                          annotation_text=f"Limit: {danger_th} {unit_h}",
                          annotation_font_color="#ef4444", annotation_font_size=10,
                          annotation_position="top right")
        fig_par.add_trace(go.Scatter(
            x=plot_df["reading_no"], y=plot_df[col_key],
            mode="lines+markers",
            line=dict(color=line_col_h, width=2),
            marker=dict(color=["#ef4444" if b else line_col_h for b in breach_mask],
                        size=9, line=dict(color="#080d1a", width=1.5)),
            hovertemplate=f"<b>Reading #%{{x}}</b><br>{sel_param}: %{{y}} {unit_h}<extra></extra>",
        ))
        fig_par.update_layout(
            height=260, paper_bgcolor="#0d1829", plot_bgcolor="#080d1a",
            margin=dict(t=10, b=40, l=10, r=10),
            xaxis=dict(title="Reading #", color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
            yaxis=dict(title=sel_param, color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
            showlegend=False
        )
        st.plotly_chart(fig_par, use_container_width=True)

        # Risk Distribution + Gear Type breakdown
        st.markdown('<div class="section-title">Risk Distribution & Gear Breakdown</div>', unsafe_allow_html=True)
        pc1, pc2 = st.columns(2)
        with pc1:
            risk_counts = hist_df["fault_label"].value_counts().reset_index()
            risk_counts.columns = ["fault_label", "count"]
            rcm = {"No Fault": "#10b981", "Minor Fault": "#f59e0b", "Major Fault": "#ef4444"}
            fig_pie = go.Figure(go.Pie(
                labels=risk_counts["fault_label"], values=risk_counts["count"],
                marker_colors=[rcm.get(r,"#3b82f6") for r in risk_counts["fault_label"]],
                hole=0.5, textfont=dict(color="#e2e8f0", size=12),
                hovertemplate="<b>%{label}</b><br>%{value} readings (%{percent})<extra></extra>",
            ))
            fig_pie.update_layout(height=260, paper_bgcolor="#0d1829",
                margin=dict(t=10,b=10,l=10,r=10),
                legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_pie, use_container_width=True)

        with pc2:
            gear_counts = hist_df["gear_type"].value_counts().reset_index()
            gear_counts.columns = ["gear_type", "count"]
            fig_gear_h = go.Figure(go.Bar(
                x=gear_counts["gear_type"], y=gear_counts["count"],
                marker_color=["#3b82f6","#10b981","#f59e0b"][:len(gear_counts)],
                marker_line_color="#080d1a", marker_line_width=1.5,
                text=gear_counts["count"], textposition="outside",
                textfont=dict(color="#94a3b8"),
            ))
            fig_gear_h.update_layout(height=260, paper_bgcolor="#0d1829", plot_bgcolor="#080d1a",
                margin=dict(t=10,b=30,l=10,r=10),
                xaxis=dict(color="#3d5a7a", tickfont=dict(color="#94a3b8")),
                yaxis=dict(title="Count", color="#3d5a7a", gridcolor="#0f2040", tickfont=dict(color="#3d5a7a")),
                showlegend=False)
            st.plotly_chart(fig_gear_h, use_container_width=True)

        # Full log table
        st.markdown('<div class="section-title">📋 Full Session Log</div>', unsafe_allow_html=True)
        display_df = hist_df.copy()
        display_df["timestamp"]   = display_df["timestamp"].dt.strftime("%d %b %Y  %H:%M:%S")
        display_df["confidence"]  = display_df["confidence"].map("{:.1%}".format)
        display_df["rul_cycles"]  = display_df["rul_cycles"].map("{:,}".format)
        display_df = display_df.rename(columns={
            "timestamp":"Time","gear_type":"Type","gear_unit":"Unit",
            "fault_label":"Fault","confidence":"Conf","health_score":"Health",
            "rul_cycles":"RUL","load_kn":"Load(kN)","torque_nm":"Torque",
            "vibration":"Vib","temperature":"Temp","wear":"Wear",
            "lubrication":"Lube","efficiency":"Eff%","cycles":"Cycles"
        }).drop(columns=["id"])
        st.dataframe(display_df, use_container_width=True, height=300)
        csv_bytes = hist_df.to_csv(index=False).encode()
        st.download_button("⬇️ Export as CSV", data=csv_bytes,
            file_name=f"gearmind_history_{dt.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv")

# ════════════════════════════════════════════════════════
# TAB 7 — REPORT GENERATOR
# ════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-title">Auto-Generate Maintenance Report</div>', unsafe_allow_html=True)
    r1,r2 = st.columns(2)
    with r1:
        st.markdown(f"""
        <div style='background:#0d1829; border:1px solid #0f2040; border-radius:14px; padding:22px;'>
            <div style='font-size:10px; color:#1e3a5f; letter-spacing:2px; font-weight:700; margin-bottom:16px;'>REPORT CONTENTS</div>
            {"".join([f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #0f2040;"><span style="color:#2563eb;font-size:12px;">✦</span><span style="font-size:13px;color:#3d5a7a;">{item}</span></div>'
            for item in [
                f'Executive Summary — {gtype} Gear {gear_name}',
                f'Fault Assessment — {fault} ({conf:.0%} confidence)',
                f'Health Score — {health_score_val}/100',
                'Root Cause Analysis (SHAP-backed)',
                f'RUL — {rul:,} cycles / {days_int} days remaining',
                f'Cost Impact — Savings of ₹{money_saved:,}',
                'Prioritized Action Plan with timeline',
                'Post-Maintenance Monitoring Protocol'
            ]])}
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)
        if st.button("📄 Generate AI Report", type="primary", use_container_width=True):
            with st.spinner("GearMind AI writing report..."):
                try:
                    report = generate_maintenance_report(prediction, gear_name)
                    st.session_state.generated_report = report
                except Exception as e:
                    st.error(f"Error: {e}")

    with r2:
        if 'generated_report' in st.session_state:
            st.markdown(f"""
            <div style='background:#0d1829; border:1px solid #1e3a5f; border-radius:12px;
            padding:20px; max-height:450px; overflow-y:auto;'>
                <div style='font-size:10px; color:#3b82f6; font-weight:700; letter-spacing:1.5px; margin-bottom:14px;'>
                    ⚙ GEARMIND AI — MAINTENANCE REPORT
                </div>
                <div style='font-size:13px; color:#c9d6e8; line-height:1.8;'>{md_to_html(st.session_state.generated_report)}</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇️ Download Report (.txt)",
                data=st.session_state.generated_report,
                file_name=f"GearMind_Report_{gtype}_{gear_name}.txt",
                mime="text/plain", use_container_width=True)
        else:
            st.markdown("""
            <div style='background:#080d1a; border:2px dashed #0f2040; border-radius:14px;
            padding:60px 40px; text-align:center;'>
                <div style='font-size:40px; margin-bottom:16px;'>📄</div>
                <div style='font-size:15px; font-weight:600; color:#1e3a5f; margin-bottom:8px;'>Report will appear here</div>
                <div style='font-size:12px; color:#0f2040;'>Click Generate AI Report above</div>
            </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; padding:30px 0 10px; color:#1e3a5f; font-size:11px; letter-spacing:0.5px;'>
    ⚙ GearMind AI v4.0 · {gtype} Gear Module · Elecon Engineering Works Pvt. Ltd., Anand, Gujarat<br>
    <span style='color:#0a1422;'>GBM · XGBoost · RF · LR · SVM · SHAP · LIME · Isolation Forest · LLaMA 3.3 70B · MLflow</span>
</div>
""", unsafe_allow_html=True)
