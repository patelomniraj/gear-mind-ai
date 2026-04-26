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

    st.markdown('<div class="section-title">Unit Selection</div>', unsafe_allow_html=True)
    gear_id = st.selectbox("", list(gc["units"].keys()), label_visibility="collapsed")
    p = gc["units"][gear_id]
    gear_name = gear_id.split(" ")[0]

    st.markdown('<div class="section-title" style="margin-top:16px;">Live Sensor Parameters</div>', unsafe_allow_html=True)
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
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏭  Fleet Overview",
    "🎯  Gear Health",
    "💰  Cost Impact",
    "🔍  SHAP + LIME",
    "📊  Model Comparison",
    "🧪  What-If Simulator",
    "📄  Report Generator",
])

# ════════════════════════════════════════════════════════
# TAB 0 — FLEET OVERVIEW
# ════════════════════════════════════════════════════════
with tab0:
    st.markdown(f'<div class="section-title">{gc["icon"]} {gtype} Gear Fleet — All Units Live</div>', unsafe_allow_html=True)

    fleet = gc["units"]
    fleet_preds = {}
    for gid, sensors in fleet.items():
        sv = {"Load (kN)": sensors["load"], "Torque (Nm)": sensors["torque"],
              "Vibration RMS (mm/s)": sensors["vib"], "Temperature (°C)": sensors["temp"],
              "Wear (mm)": sensors["wear"], "Lubrication Index": sensors["lube"],
              "Efficiency (%)": sensors["eff"], "Cycles in Use": sensors["cycles"]}
        fleet_preds[gid] = predict_gear_health(sv)

    total    = len(fleet_preds)
    critical = sum(1 for fp in fleet_preds.values() if fp["fault_label"] == "Major Fault")
    warning  = sum(1 for fp in fleet_preds.values() if fp["fault_label"] == "Minor Fault")
    healthy  = sum(1 for fp in fleet_preds.values() if fp["fault_label"] == "No Fault")
    avg_rul  = sum(fp["rul_cycles"] for fp in fleet_preds.values()) // total

    fk1,fk2,fk3,fk4,fk5 = st.columns(5)
    fk1.metric("Total Units", total)
    fk2.metric("🔴 Critical", critical)
    fk3.metric("⚠️ Warning",  warning)
    fk4.metric("✅ Healthy",  healthy)
    fk5.metric("Avg RUL",    f"{avg_rul:,}")
    st.markdown("<div style='margin:24px 0;'></div>", unsafe_allow_html=True)

    fault_colors = {
        "Major Fault": ("#ef4444", "#1a0808"),
        "Minor Fault": ("#f59e0b", "#1a1408"),
        "No Fault":    ("#10b981", "#081a12"),
    }

    cols = st.columns(5)
    for i, (gid, pred) in enumerate(fleet_preds.items()):
        score  = calc_health_score(pred, gc)
        f_lbl  = pred["fault_label"]
        color, bg = fault_colors.get(f_lbl, ("#10b981","#081a12"))
        rul_g  = pred["rul_cycles"]
        an     = pred["anomaly_status"]
        an_col = "#ef4444" if an == "SUSPICIOUS" else "#10b981"
        icon   = "🔴" if f_lbl == "Major Fault" else "⚠️" if f_lbl == "Minor Fault" else "✅"
        sv     = pred["sensor_values"]
        vib_c  = "#ef4444" if sv["Vibration RMS (mm/s)"] > gc["vib_limit"]  else "#10b981"
        tmp_c  = "#ef4444" if sv["Temperature (°C)"]     > gc["temp_limit"] else "#10b981"
        wear_c = "#ef4444" if sv["Wear (mm)"]            > gc["wear_limit"] else "#10b981"
        short_id = gid.split(" ")[0]
        d_left = int(rul_g / daily_cycles)

        with cols[i]:
            st.markdown(f"""
<div style="background:{bg};border:1px solid {color}55;border-top:3px solid {color};border-radius:14px;padding:16px;">
<div style="display:flex;justify-content:space-between;margin-bottom:8px;">
<b style="color:#e2e8f0;font-size:14px;">{short_id}</b><span>{icon}</span></div>
<div style="text-align:center;margin-bottom:8px;">
<div style="font-size:44px;font-weight:900;color:{color};text-shadow:0 0 20px {color}44;">{score}</div>
<div style="font-size:9px;color:{color};letter-spacing:1px;font-weight:700;">HEALTH SCORE</div></div>
<div style="background:{color}22;border:1px solid {color}44;border-radius:6px;padding:4px;text-align:center;margin-bottom:8px;">
<span style="font-size:11px;font-weight:700;color:{color};">{f_lbl}</span></div>
<div style="font-size:10px;display:flex;flex-direction:column;gap:4px;">
<div style="display:flex;justify-content:space-between;">
<span style="color:#3d5a7a;">Days Left</span>
<span style="color:{color};font-family:monospace;font-weight:700;">{d_left}d</span></div>
<div style="display:flex;justify-content:space-between;">
<span style="color:#3d5a7a;">Vibration</span>
<span style="color:{vib_c};font-family:monospace;">{sv["Vibration RMS (mm/s)"]:.1f} mm/s</span></div>
<div style="display:flex;justify-content:space-between;">
<span style="color:#3d5a7a;">Temp</span>
<span style="color:{tmp_c};font-family:monospace;">{sv["Temperature (°C)"]:.0f}°C</span></div>
<div style="display:flex;justify-content:space-between;">
<span style="color:#3d5a7a;">Wear</span>
<span style="color:{wear_c};font-family:monospace;">{sv["Wear (mm)"]:.2f} mm</span></div>
<div style="display:flex;justify-content:space-between;">
<span style="color:#3d5a7a;">Anomaly</span>
<span style="color:{an_col};font-size:10px;">{an}</span></div></div>
<div style="margin-top:10px;background:#0f2040;border-radius:3px;height:4px;overflow:hidden;">
<div style="width:{score}%;background:{color};height:100%;border-radius:3px;box-shadow:0 0 8px {color}66;"></div></div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:32px 0 0;'></div>", unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown('<div class="section-title">Fleet Health Scores</div>', unsafe_allow_html=True)
        gears  = [g.split(" ")[0] for g in fleet_preds.keys()]
        scores = [calc_health_score(fp, gc) for fp in fleet_preds.values()]
        fcolors_c = [fault_colors[fp["fault_label"]][0] for fp in fleet_preds.values()]
        fig_fleet = go.Figure(go.Bar(x=gears, y=scores, marker_color=fcolors_c, marker_line_width=0,
            text=scores, textposition="outside", textfont=dict(color="#64748b", size=13, family="JetBrains Mono")))
        fig_fleet.add_hline(y=80, line_color="#10b981", line_dash="dash", line_width=1,
                            annotation_text="Safe (80)", annotation_font_color="#10b981", annotation_font_size=10)
        fig_fleet.add_hline(y=40, line_color="#ef4444", line_dash="dash", line_width=1,
                            annotation_text="Critical (40)", annotation_font_color="#ef4444", annotation_font_size=10)
        fig_fleet.update_layout(paper_bgcolor="#0d1829", plot_bgcolor="#0d1829", font_color="#64748b",
            height=300, xaxis=dict(gridcolor="#0f2040"), yaxis=dict(gridcolor="#0f2040", range=[0,115]),
            margin=dict(t=20, b=20))
        st.plotly_chart(fig_fleet, use_container_width=True)

    with fc2:
        st.markdown('<div class="section-title">Maintenance Priority Queue</div>', unsafe_allow_html=True)
        priority_data = []
        for gid, pred in fleet_preds.items():
            sc    = calc_health_score(pred, gc)
            f_lbl = pred["fault_label"]
            rul_g = pred["rul_cycles"]
            d_l   = int(rul_g / daily_cycles)
            sid   = gid.split(" ")[0]
            if f_lbl == "Major Fault":   p_str, tl = "🔴 IMMEDIATE", "< 24 hours"
            elif f_lbl == "Minor Fault": p_str, tl = "⚠️ URGENT",   "< 1 week"
            else:                         p_str, tl = "✅ ROUTINE",  "Next service"
            priority_data.append({"Unit": sid, "Score": sc, "Status": f_lbl,
                                   "Days Left": f"{d_l}d", "Priority": p_str, "Timeline": tl})
        pdf = pd.DataFrame(priority_data).sort_values("Score")
        st.dataframe(pdf, use_container_width=True, hide_index=True, height=280)

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
                <div style='font-size:28px; font-weight:800; color:#10b981; font-family:JetBrains Mono;'>{len(fleet)*money_saved//100000}L+</div>
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
        comp_df['Rank'] = ['🥇','🥈','🥉','4th','5th'][:len(comp_df)]
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
# TAB 5 — WHAT-IF SIMULATOR
# ════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">What-If Scenario Simulator</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#3d5a7a; font-size:13px; margin-bottom:20px;'>Simulate how changing one sensor parameter affects fault prediction and RUL instantly.</p>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        what_feature = st.selectbox("Parameter to modify:", FEATURE_COLS)
        mins = {'Load (kN)':10.0,'Torque (Nm)':50.0,'Vibration RMS (mm/s)':0.5,
                'Temperature (°C)':40.0,'Wear (mm)':0.0,'Lubrication Index':0.05,
                'Efficiency (%)':70.0,'Cycles in Use':0.0}
        maxs = {'Load (kN)':120.0,'Torque (Nm)':600.0,'Vibration RMS (mm/s)':30.0,
                'Temperature (°C)':150.0,'Wear (mm)':4.0,'Lubrication Index':1.0,
                'Efficiency (%)':99.0,'Cycles in Use':100000.0}
        new_val  = st.slider(f"New value:", float(mins[what_feature]), float(maxs[what_feature]),
                             float(sensor_values[what_feature]), key="wif_slider")
        run_sim  = st.button("▶ Run Simulation", type="primary", use_container_width=True)

    with c2:
        mod = sensor_values.copy()
        mod[what_feature] = new_val
        mod_pred  = predict_gear_health(mod)
        delta_rul = mod_pred['rul_cycles'] - rul
        delta_col = "#10b981" if delta_rul > 0 else "#ef4444"
        delta_icon= "📈" if delta_rul > 0 else "📉"
        mod_score = calc_health_score(mod_pred, gc)

        st.markdown(f"""
        <div style='background:#0d1829; border:1px solid #0f2040; border-radius:14px; padding:22px;'>
            <div style='font-size:10px; color:#1e3a5f; letter-spacing:2px; font-weight:700; margin-bottom:18px;'>SIMULATION RESULT</div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:18px;'>
                <div style='background:#080d1a; border-radius:10px; padding:14px; border:1px solid #0f2040;'>
                    <div style='font-size:9px; color:#1e3a5f; letter-spacing:1px; margin-bottom:8px;'>BEFORE</div>
                    <div style='font-size:16px; font-weight:800; color:#e2e8f0;'>{fault}</div>
                    <div style='font-size:11px; color:#3d5a7a; margin-top:4px;'>{conf:.1%} confidence</div>
                    <div style='font-size:11px; color:#3d5a7a;'>Score: {health_score_val}/100</div>
                    <div style='font-size:11px; color:#3d5a7a;'>{rul:,} cycles</div>
                </div>
                <div style='background:#080d1a; border-radius:10px; padding:14px; border:1px solid {delta_col}44;'>
                    <div style='font-size:9px; color:#1e3a5f; letter-spacing:1px; margin-bottom:8px;'>AFTER</div>
                    <div style='font-size:16px; font-weight:800; color:#e2e8f0;'>{mod_pred['fault_label']}</div>
                    <div style='font-size:11px; color:#3d5a7a; margin-top:4px;'>{mod_pred['confidence']:.1%} confidence</div>
                    <div style='font-size:11px; color:#3d5a7a;'>Score: {mod_score}/100</div>
                    <div style='font-size:11px; color:{delta_col}; font-weight:700;'>{mod_pred['rul_cycles']:,} cycles</div>
                </div>
            </div>
            <div style='background:{delta_col}11; border:1px solid {delta_col}33; border-radius:8px;
            padding:12px; text-align:center;'>
                <span style='font-size:20px;'>{delta_icon}</span>
                <span style='font-size:14px; font-weight:700; color:{delta_col}; margin-left:8px;'>
                    RUL {delta_rul:+,} cycles ({delta_rul//400:+,} shifts)
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

    if run_sim:
        with st.spinner("Running AI analysis..."):
            try:
                result = simulate_what_if(sensor_values, what_feature, new_val, gear_name)
                st.markdown(f"""
                <div style='background:#0d1829; border:1px solid #1e3a5f; border-radius:12px;
                padding:20px; margin-top:20px;'>
                    <div style='font-size:10px; color:#3b82f6; font-weight:700; letter-spacing:1.5px; margin-bottom:12px;'>
                        ⚙ GEARMIND AI ANALYSIS
                    </div>
                    <div style='font-size:14px; color:#c9d6e8; line-height:1.7;'>{md_to_html(result['explanation'])}</div>
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

# ════════════════════════════════════════════════════════
# TAB 6 — REPORT GENERATOR
# ════════════════════════════════════════════════════════
with tab6:
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
