"""
MODULE 5 — GEARMIND AI DASHBOARD (Ultimate Edition)
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

from copilot.llm_copilot import predict_gear_health, ask_gearmind, simulate_what_if, generate_maintenance_report

st.set_page_config(
    page_title="GearMind AI — Elecon Engineering",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def md_to_html(text):
    """Convert markdown to HTML for chat bubbles."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'^#{1,3}\s+(.+)$', r'<div class="ai-heading">\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^\* (.+)$', r'<div class="ai-bullet">▸ \1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\. (.+)$', lambda m: f'<div class="ai-bullet">▸ {m.group(1)}</div>', text, flags=re.MULTILINE)
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    return text

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

.stApp, .main { background: #070b14 !important; }
#MainMenu, footer, header { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0a1020 100%) !important;
    border-right: 1px solid #0f2040 !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label { color: #7a9cc4 !important; font-size: 11px !important; }

/* Sliders */
.stSlider > div > div > div { background: #0f2040 !important; }
.stSlider > div > div > div > div { background: linear-gradient(90deg, #2563eb, #3b82f6) !important; }
[data-testid="stSliderThumb"] { background: #3b82f6 !important; border: 2px solid #fff !important; }

/* Select */
.stSelectbox > div > div {
    background: #0d1829 !important;
    border: 1px solid #0f2040 !important;
    color: #c9d6e8 !important;
    border-radius: 8px !important;
}

/* Text input */
.stTextInput > div > div > input, .stTextArea textarea {
    background: #0d1829 !important;
    border: 1px solid #0f2040 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
    outline: none !important;
}

/* Buttons */
.stButton > button {
    background: #0d1829 !important;
    color: #60a5fa !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    padding: 8px 14px !important;
}
.stButton > button:hover {
    background: #1e3a5f !important;
    color: #93c5fd !important;
    border-color: #2563eb !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.4) !important;
    transform: translateY(-2px) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #080d1a !important;
    border-bottom: 1px solid #0f2040 !important;
    padding: 0 8px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #3d5a7a !important;
    border-radius: 6px 6px 0 0 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    letter-spacing: 0.3px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #0d1829 !important;
    color: #60a5fa !important;
    border-bottom: 2px solid #2563eb !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1829, #0a1422) !important;
    border: 1px solid #0f2040 !important;
    border-radius: 12px !important;
    padding: 18px !important;
    transition: all 0.2s !important;
}
[data-testid="metric-container"]:hover { border-color: #1e3a5f !important; }
[data-testid="metric-container"] label { color: #3d5a7a !important; font-size: 11px !important; letter-spacing: 0.5px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 22px !important; font-weight: 700 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #070b14; }
::-webkit-scrollbar-thumb { background: #0f2040; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #1e3a5f; }

/* Dataframe */
.stDataFrame { border: 1px solid #0f2040 !important; border-radius: 10px !important; overflow: hidden !important; }

/* ── CHAT STYLES ── */
.chat-wrapper {
    background: linear-gradient(180deg, #080d1a 0%, #070b14 100%);
    border: 1px solid #0f2040;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 12px;
}

.chat-header-bar {
    background: linear-gradient(90deg, #0d1829, #0a1422);
    border-bottom: 1px solid #0f2040;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.chat-dot { width: 8px; height: 8px; border-radius: 50%; }
.chat-dot-green { background: #10b981; box-shadow: 0 0 6px #10b981; }
.chat-dot-yellow { background: #f59e0b; }
.chat-dot-red { background: #ef4444; }

.chat-messages {
    padding: 20px;
    height: 380px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.chat-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #1e3a5f;
    text-align: center;
}

.chat-empty-icon { font-size: 48px; margin-bottom: 12px; filter: grayscale(0.3); }
.chat-empty-title { font-size: 15px; font-weight: 600; color: #1e3a5f; margin-bottom: 6px; }
.chat-empty-sub { font-size: 12px; color: #0f2040; line-height: 1.6; }

.msg-wrapper-user { display: flex; flex-direction: column; align-items: flex-end; }
.msg-wrapper-ai { display: flex; flex-direction: column; align-items: flex-start; }

.msg-meta {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 5px;
    font-family: 'JetBrains Mono', monospace;
}
.msg-meta-user { color: #2563eb; }
.msg-meta-ai { color: #059669; display: flex; align-items: center; gap: 6px; }

.msg-bubble-user {
    background: linear-gradient(135deg, #1e3a5f, #1d4ed8);
    border: 1px solid #2563eb;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    max-width: 75%;
    color: #e2e8f0;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(37,99,235,0.2);
}

.msg-bubble-ai {
    background: linear-gradient(135deg, #0d1829, #0a1422);
    border: 1px solid #0f2040;
    border-radius: 4px 16px 16px 16px;
    padding: 14px 18px;
    max-width: 90%;
    color: #c9d6e8;
    font-size: 14px;
    line-height: 1.7;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.ai-heading {
    font-size: 13px;
    font-weight: 700;
    color: #60a5fa;
    margin: 10px 0 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid #0f2040;
}

.ai-bullet {
    padding: 4px 0 4px 8px;
    border-left: 2px solid #1e3a5f;
    margin: 4px 0;
    color: #94a3b8;
    font-size: 13px;
}

.msg-bubble-ai strong { color: #93c5fd; }
.msg-bubble-ai em { color: #7dd3fc; font-style: normal; }

.chat-input-area {
    background: #0a1020;
    border-top: 1px solid #0f2040;
    padding: 16px 20px;
}

/* Sensor cards */
.sensor-card {
    background: linear-gradient(135deg, #0d1829, #0a1422);
    border: 1px solid #0f2040;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    transition: all 0.2s;
}
.sensor-card:hover { border-color: #1e3a5f; }
.sensor-card-bad { border-color: rgba(239,68,68,0.3) !important; background: linear-gradient(135deg, #1a0a0a, #130808) !important; }
.sensor-card-warn { border-color: rgba(245,158,11,0.3) !important; }

/* Status badges */
.badge-major { background: linear-gradient(135deg,rgba(239,68,68,0.15),rgba(220,38,38,0.1)); border:1px solid #ef4444; color:#ef4444; padding:5px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 0 20px rgba(239,68,68,0.15); }
.badge-minor { background: linear-gradient(135deg,rgba(245,158,11,0.15),rgba(217,119,6,0.1)); border:1px solid #f59e0b; color:#f59e0b; padding:5px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 0 20px rgba(245,158,11,0.15); }
.badge-ok    { background: linear-gradient(135deg,rgba(16,185,129,0.15),rgba(5,150,105,0.1)); border:1px solid #10b981; color:#10b981; padding:5px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 0 20px rgba(16,185,129,0.15); }

.section-title {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #1e3a5f;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #0f2040;
}

/* Pulse animation for critical status */
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
}
.pulse-red { animation: pulse-red 2s infinite; }

@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
}
.pulse-green { animation: pulse-green 2s infinite; }

/* Typing indicator */
@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-4px); opacity: 1; }
}
.typing-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #3b82f6;
    margin: 0 2px;
    animation: typing 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
</style>
""", unsafe_allow_html=True)

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

presets = {
    "GEAR-03 (Major Fault)": dict(load=74.0, torque=310.8, vib=12.4, temp=108.0, wear=1.8, lube=0.21, eff=85.2, cycles=84200),
    "GEAR-07 (Minor Fault)": dict(load=81.0, torque=340.2, vib=7.1,  temp=91.0,  wear=1.1, lube=0.42, eff=90.1, cycles=52000),
    "GEAR-01 (Healthy)":     dict(load=48.0, torque=201.6, vib=2.3,  temp=72.0,  wear=0.2, lube=0.82, eff=96.8, cycles=18000),
    "GEAR-05 (Healthy)":     dict(load=53.0, torque=222.6, vib=3.1,  temp=78.0,  wear=0.35,lube=0.71, eff=95.3, cycles=28000),
    "GEAR-12 (Healthy)":     dict(load=44.0, torque=184.8, vib=1.8,  temp=68.0,  wear=0.15,lube=0.88, eff=97.4, cycles=12000),
}

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 24px; border-bottom:1px solid #0f2040; margin-bottom:20px;'>
        <div style='font-size:22px; font-weight:800; color:#e2e8f0; letter-spacing:-0.5px;'>⚙ GearMind AI</div>
        <div style='font-size:10px; color:#1e3a5f; margin-top:5px; letter-spacing:2px; font-weight:600;'>ELECON ENGINEERING WORKS</div>
        <div style='margin-top:10px; display:flex; gap:6px;'>
            <span style='background:#0f2040; color:#3b82f6; font-size:9px; padding:3px 8px; border-radius:10px; font-weight:600;'>GBM 99.87%</span>
            <span style='background:#0f2040; color:#10b981; font-size:9px; padding:3px 8px; border-radius:10px; font-weight:600;'>RUL R²=0.99</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    groq_key = st.text_input("🔑 Groq API Key", type="password", placeholder="gsk_...")
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
        st.markdown("""
        <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
        border-radius:8px; padding:8px 12px; font-size:12px; color:#10b981; margin-top:4px;'>
            ✅ AI Copilot Active — LLaMA 3.3 70B
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:20px;">Gear Selection</div>', unsafe_allow_html=True)
    gear_id = st.selectbox("", list(presets.keys()), label_visibility="collapsed")
    p = presets[gear_id]
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

    st.markdown("""
    <div style='margin-top:24px; padding:14px; background:#080d1a; border:1px solid #0f2040;
    border-radius:10px; font-size:10px; color:#1e3a5f; line-height:2;'>
        <div style='color:#1e3a5f; font-weight:700; letter-spacing:1px; margin-bottom:6px;'>SYSTEM INFO</div>
        ML: GBM · XGBoost · RF · LR · SVM<br>
        XAI: SHAP · LIME · Isolation Forest<br>
        LLM: Groq · LLaMA 3.3 70B (Free)<br>
        Tracking: MLflow<br>
        <div style='margin-top:8px; color:#0f2040;'>v3.0 · Anand, Gujarat</div>
    </div>
    """, unsafe_allow_html=True)

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

# ── Top Header ────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between;
padding:20px 0 18px; border-bottom:1px solid #0f2040; margin-bottom:24px;'>
    <div>
        <div style='font-size:26px; font-weight:800; color:#e2e8f0; letter-spacing:-0.5px;'>
            ⚙ {gear_name} — Predictive Maintenance
        </div>
        <div style='font-size:12px; color:#1e3a5f; margin-top:5px; letter-spacing:0.5px;'>
            Elecon Engineering Works · Real-time ML Analysis · {len(prediction['violations'])} violations detected
        </div>
    </div>
    <div style='display:flex; align-items:center; gap:12px;'>
        <div style='text-align:right;'>
            <div style='font-size:10px; color:#1e3a5f; letter-spacing:1px;'>ANOMALY</div>
            <div style='font-size:13px; font-weight:700; color:{an_color};'>{an_icon} {prediction['anomaly_status']}</div>
        </div>
        <span class="{badge_class}">{badge_icon} {fault}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Confidence",    f"{conf:.1%}")
k2.metric("Fault Class",   fault)
k3.metric("RUL (cycles)",  f"{rul:,}")
k4.metric("RUL (shifts)",  f"{rul//400:,}")
k5.metric("Violations",    f"{len(prediction['violations'])}")

st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏭  Fleet Overview",
    "💬  AI Copilot",
    "📊  Model Comparison",
    "🔍  SHAP + LIME",
    "⚠️  Anomaly & Timeline",
    "🧪  What-If Simulator",
    "📄  Report Generator",
])

# ════════════════════════════════════════════════════════
# TAB 0 — FLEET OVERVIEW
# ════════════════════════════════════════════════════════
with tab0:
    st.markdown('<div class="section-title">Fleet Overview — All Gear Units</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#3d5a7a; font-size:13px; margin-bottom:24px;'>Real-time health monitoring across all 5 gear units. Click any gear to inspect in detail.</p>", unsafe_allow_html=True)

    # Define all 5 gears
    fleet = {
        "GEAR-01": dict(load=48.0, torque=201.6, vib=2.3,  temp=72.0,  wear=0.2,  lube=0.82, eff=96.8, cycles=18000),
        "GEAR-03": dict(load=74.0, torque=310.8, vib=12.4, temp=108.0, wear=1.8,  lube=0.21, eff=85.2, cycles=84200),
        "GEAR-05": dict(load=53.0, torque=222.6, vib=3.1,  temp=78.0,  wear=0.35, lube=0.71, eff=95.3, cycles=28000),
        "GEAR-07": dict(load=81.0, torque=340.2, vib=7.1,  temp=91.0,  wear=1.1,  lube=0.42, eff=90.1, cycles=52000),
        "GEAR-12": dict(load=44.0, torque=184.8, vib=1.8,  temp=68.0,  wear=0.15, lube=0.88, eff=97.4, cycles=12000),
    }

    # Calculate health score (0-100)
    def health_score(pred):
        score = 100
        v = pred["sensor_values"]
        score -= min(30, max(0, (v["Vibration RMS (mm/s)"] - 6) * 5))
        score -= min(20, max(0, (v["Temperature (°C)"] - 85) * 0.8))
        score -= min(25, max(0, (v["Wear (mm)"] - 0.8) * 30))
        score -= min(20, max(0, (0.5 - v["Lubrication Index"]) * 40))
        score -= min(10, max(0, (93 - v["Efficiency (%)"]) * 0.8))
        if pred["fault_label"] == "Major Fault": score = min(score, 25)
        elif pred["fault_label"] == "Minor Fault": score = min(score, 65)
        return max(0, round(score))

    # Run predictions for all gears
    fleet_preds = {}
    for gid, sensors in fleet.items():
        sv = {
            "Load (kN)": sensors["load"],
            "Torque (Nm)": sensors["torque"],
            "Vibration RMS (mm/s)": sensors["vib"],
            "Temperature (°C)": sensors["temp"],
            "Wear (mm)": sensors["wear"],
            "Lubrication Index": sensors["lube"],
            "Efficiency (%)": sensors["eff"],
            "Cycles in Use": sensors["cycles"],
        }
        fleet_preds[gid] = predict_gear_health(sv)

    # ── Summary KPIs ──
    total    = len(fleet_preds)
    critical = sum(1 for p in fleet_preds.values() if p["fault_label"] == "Major Fault")
    warning  = sum(1 for p in fleet_preds.values() if p["fault_label"] == "Minor Fault")
    healthy  = sum(1 for p in fleet_preds.values() if p["fault_label"] == "No Fault")
    avg_rul  = sum(p["rul_cycles"] for p in fleet_preds.values()) // total

    fk1, fk2, fk3, fk4, fk5 = st.columns(5)
    fk1.metric("Total Units",    total)
    fk2.metric("🔴 Critical",    critical)
    fk3.metric("⚠️ Warning",     warning)
    fk4.metric("✅ Healthy",     healthy)
    fk5.metric("Avg RUL",       f"{avg_rul:,}")

    st.markdown("<div style='margin:24px 0;'></div>", unsafe_allow_html=True)

    # ── Gear Cards ──
    fault_colors = {
        "Major Fault": ("#ef4444", "#1a0808"),
        "Minor Fault": ("#f59e0b", "#1a1408"),
        "No Fault":    ("#10b981", "#081a12"),
    }

    cols = st.columns(5)
    for i, (gid, pred) in enumerate(fleet_preds.items()):
        score  = health_score(pred)
        fault  = pred["fault_label"]
        color, bg = fault_colors.get(fault, ("#10b981", "#081a12"))
        rul_g  = pred["rul_cycles"]
        an     = pred["anomaly_status"]
        an_col = "#ef4444" if an == "SUSPICIOUS" else "#10b981"
        icon   = "🔴" if fault == "Major Fault" else "⚠️" if fault == "Minor Fault" else "✅"
        sv     = pred["sensor_values"]
        vib_c  = "#ef4444" if sv["Vibration RMS (mm/s)"] > 6   else "#10b981"
        tmp_c  = "#ef4444" if sv["Temperature (°C)"]    > 95   else "#10b981"
        wear_c = "#ef4444" if sv["Wear (mm)"]           > 1.0  else "#10b981"

        with cols[i]:
            st.markdown(f"""
<div style="background:{bg};border:1px solid {color}55;border-top:3px solid {color};
border-radius:14px;padding:16px;">
<div style="display:flex;justify-content:space-between;margin-bottom:10px;">
<b style="color:#e2e8f0;font-size:14px;">{gid}</b><span>{icon}</span></div>
<div style="text-align:center;margin-bottom:10px;">
<div style="font-size:44px;font-weight:900;color:{color};">{score}</div>
<div style="font-size:9px;color:{color};letter-spacing:1px;font-weight:700;">HEALTH SCORE</div>
</div>
<div style="background:{color}22;border:1px solid {color}44;border-radius:6px;
padding:5px;text-align:center;margin-bottom:10px;">
<span style="font-size:11px;font-weight:700;color:{color};">{fault}</span></div>
<div style="font-size:10px;display:flex;flex-direction:column;gap:5px;">
<div style="display:flex;justify-content:space-between;">
<span style="color:#3d5a7a;">RUL</span>
<span style="color:#e2e8f0;font-family:monospace;">{rul_g:,}</span></div>
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
<span style="color:{an_col};">{an}</span></div>
</div>
<div style="margin-top:10px;background:#070b14;border-radius:3px;height:4px;overflow:hidden;">
<div style="width:{score}%;background:{color};height:100%;border-radius:3px;"></div></div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:32px 0 0;'></div>", unsafe_allow_html=True)

    # ── Fleet Health Chart ──
    fc1, fc2 = st.columns(2)

    with fc1:
        st.markdown('<div class="section-title">Fleet Health Scores</div>', unsafe_allow_html=True)
        gears  = list(fleet_preds.keys())
        scores = [health_score(p) for p in fleet_preds.values()]
        fcolors = [fault_colors[p["fault_label"]][0] for p in fleet_preds.values()]

        fig_fleet = go.Figure(go.Bar(
            x=gears, y=scores,
            marker_color=fcolors,
            marker_line_width=0,
            text=scores,
            textposition="outside",
            textfont=dict(color="#94a3b8", size=13, family="JetBrains Mono")
        ))
        fig_fleet.add_hline(y=80, line_color="#10b981", line_dash="dash",
                            line_width=1, annotation_text="Safe threshold (80)",
                            annotation_font_color="#10b981", annotation_font_size=10)
        fig_fleet.add_hline(y=40, line_color="#ef4444", line_dash="dash",
                            line_width=1, annotation_text="Critical threshold (40)",
                            annotation_font_color="#ef4444", annotation_font_size=10)
        fig_fleet.update_layout(
            paper_bgcolor="#0d1829", plot_bgcolor="#0d1829",
            font_color="#64748b", height=320,
            xaxis=dict(gridcolor="#0f2040"),
            yaxis=dict(gridcolor="#0f2040", range=[0, 115]),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_fleet, use_container_width=True)

    with fc2:
        st.markdown('<div class="section-title">RUL Comparison</div>', unsafe_allow_html=True)
        ruls = [p["rul_cycles"] for p in fleet_preds.values()]
        rul_colors = [fault_colors[p["fault_label"]][0] for p in fleet_preds.values()]

        fig_rul = go.Figure(go.Bar(
            x=gears, y=ruls,
            marker_color=rul_colors,
            marker_line_width=0,
            text=[f"{r:,}" for r in ruls],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11, family="JetBrains Mono")
        ))
        fig_rul.update_layout(
            paper_bgcolor="#0d1829", plot_bgcolor="#0d1829",
            font_color="#64748b", height=320,
            xaxis=dict(gridcolor="#0f2040"),
            yaxis=dict(gridcolor="#0f2040", title="Remaining Cycles"),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_rul, use_container_width=True)

    # ── Maintenance Priority Table ──
    st.markdown("<div style='margin:8px 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Maintenance Priority Queue</div>', unsafe_allow_html=True)

    priority_data = []
    for gid, pred in fleet_preds.items():
        score = health_score(pred)
        fault = pred["fault_label"]
        rul_g = pred["rul_cycles"]
        if fault == "Major Fault":
            priority = "🔴 IMMEDIATE"
            action   = "Stop gear. Inspect and replace worn components."
            timeline = "Within 24 hours"
        elif fault == "Minor Fault":
            priority = "⚠️ URGENT"
            action   = "Schedule maintenance. Monitor closely."
            timeline = "Within 1 week"
        else:
            priority = "✅ ROUTINE"
            action   = "Continue operation. Routine check."
            timeline = "Next scheduled service"
        priority_data.append({
            "Gear": gid,
            "Health Score": score,
            "Status": fault,
            "RUL (cycles)": f"{rul_g:,}",
            "Priority": priority,
            "Recommended Action": action,
            "Timeline": timeline,
        })

    priority_df = pd.DataFrame(priority_data).sort_values("Health Score")
    st.dataframe(priority_df, use_container_width=True, hide_index=True, height=220)

# ════════════════════════════════════════════════════════
# TAB 1 — AI COPILOT
# ════════════════════════════════════════════════════════
with tab1:
    col_chat, col_status = st.columns([3, 1], gap="large")

    with col_chat:
        if not os.environ.get("GROQ_API_KEY"):
            st.markdown("""
            <div style='background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3);
            border-radius:10px; padding:12px 16px; margin-bottom:16px; font-size:13px; color:#f59e0b;'>
                ⚠️ Enter your Groq API key in the sidebar to activate the AI Copilot.
                Get it free at <strong>console.groq.com</strong>
            </div>""", unsafe_allow_html=True)

        if 'chat_history' not in st.session_state: st.session_state.chat_history = []
        if 'msgs_display' not in st.session_state: st.session_state.msgs_display = []
        if 'pending_q'    not in st.session_state: st.session_state.pending_q    = ""

        # Suggested questions
        st.markdown('<div class="section-title">Quick Questions</div>', unsafe_allow_html=True)
        sq1, sq2, sq3 = st.columns(3)
        sq4, sq5, sq6 = st.columns(3)
        suggestions = [
            ("Why did this fault happen?", sq1),
            ("How long until complete failure?", sq2),
            ("What action should I take now?", sq3),
            ("Explain the SHAP values", sq4),
            ("What is the root cause?", sq5),
            ("Generate a quick summary", sq6),
        ]
        for q, col in suggestions:
            if col.button(q, key=f"sq_{q[:10]}"):
                st.session_state.pending_q = q

        st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)

        # ── Chat Window ──
        if not st.session_state.msgs_display:
            chat_body = f"""
            <div class="chat-empty">
                <div class="chat-empty-icon">🤖</div>
                <div class="chat-empty-title">GearMind AI Ready</div>
                <div class="chat-empty-sub">
                    Currently monitoring <strong style="color:#1e3a5f">{gear_name}</strong><br>
                    Status: <strong style="color:{badge_color}">{fault}</strong> · Confidence: {conf:.0%}<br><br>
                    Ask me anything about gear health,<br>root cause, or recommended actions.
                </div>
            </div>"""
        else:
            chat_body = ""
            for msg in st.session_state.msgs_display:
                if msg['role'] == 'user':
                    chat_body += f"""
                    <div class="msg-wrapper-user">
                        <div class="msg-meta msg-meta-user">YOU</div>
                        <div class="msg-bubble-user">{msg['content']}</div>
                    </div>"""
                else:
                    formatted = md_to_html(msg['content'])
                    chat_body += f"""
                    <div class="msg-wrapper-ai">
                        <div class="msg-meta msg-meta-ai">
                            <span style='width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block;'></span>
                            GEARMIND AI
                        </div>
                        <div class="msg-bubble-ai">{formatted}</div>
                    </div>"""

        st.markdown(f"""
        <div class="chat-wrapper">
            <div class="chat-header-bar">
                <div class="chat-dot chat-dot-red"></div>
                <div class="chat-dot chat-dot-yellow"></div>
                <div class="chat-dot chat-dot-green"></div>
                <span style='margin-left:8px; font-size:12px; color:#1e3a5f; font-weight:600; letter-spacing:1px;'>
                    AI COPILOT — {gear_name} · LLaMA 3.3 70B via Groq
                </span>
                <span style='margin-left:auto; font-size:10px; color:#0f2040;'>
                    {len(st.session_state.msgs_display)//2} messages
                </span>
            </div>
            <div class="chat-messages">{chat_body}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Input Row ──
        user_input = st.text_area(
            "Message",
            value=st.session_state.pending_q,
            placeholder=f"Ask anything about {gear_name} — root cause, actions, costs, SHAP values...",
            height=90,
            label_visibility="collapsed",
            key="chat_input_area"
        )

        send_col, clear_col = st.columns([5, 1])
        send_clicked  = send_col.button("Send Message  ↑", type="primary", use_container_width=True)
        clear_clicked = clear_col.button("🗑", use_container_width=True)

        if clear_clicked:
            st.session_state.chat_history = []
            st.session_state.msgs_display = []
            st.session_state.pending_q    = ""
            st.rerun()

        final_input = (user_input or st.session_state.pending_q).strip()
        if send_clicked and final_input:
            st.session_state.pending_q = ""
            st.session_state.msgs_display.append({'role': 'user', 'content': final_input})
            if os.environ.get("GROQ_API_KEY"):
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
            else:
                st.session_state.msgs_display.append({'role': 'ai', 'content':
                    f"⚠️ API key not set. Status: **{fault}** with **{conf:.0%}** confidence. RUL: **{rul:,} cycles**. Add your Groq API key in the sidebar for full AI responses."})
            st.rerun()

    # ── Right Panel ──
    with col_status:
        st.markdown('<div class="section-title">Live Status</div>', unsafe_allow_html=True)

        # Confidence ring
        probs = prediction['class_probs']
        fig_p = go.Figure()
        colors_p = {'No Fault':'#10b981','Minor Fault':'#f59e0b','Major Fault':'#ef4444'}
        fig_p.add_trace(go.Bar(
            x=list(probs.values()), y=list(probs.keys()),
            orientation='h',
            marker_color=[colors_p.get(k,'#3b82f6') for k in probs.keys()],
            marker_line_width=0,
            text=[f"{v:.0%}" for v in probs.values()],
            textposition='outside',
            textfont=dict(size=11, color='#94a3b8', family='JetBrains Mono')
        ))
        fig_p.update_layout(
            paper_bgcolor='#070b14', plot_bgcolor='#070b14',
            font_color='#64748b', height=130,
            margin=dict(l=0,r=50,t=0,b=0),
            xaxis=dict(range=[0,1.1], showgrid=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False, showline=False),
            showlegend=False,
        )
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="section-title">Sensor Readings</div>', unsafe_allow_html=True)

        sensors_display = [
            ('Vibration', vib,  6.0,  'mm/s', False),
            ('Temp',      temp, 95.0, '°C',   False),
            ('Wear',      wear, 1.0,  'mm',   False),
            ('Lubric.',   lube, 0.5,  '',     True),
            ('Effic.',    eff,  93.0, '%',    True),
        ]
        for name, val, limit, unit, inv in sensors_display:
            is_bad = (val < limit) if inv else (val > limit)
            pct    = min(100, (val/limit*100) if not inv else ((1-(val/1))*100 if inv else 50))
            color  = "#ef4444" if is_bad else "#10b981"
            icon   = "●" if is_bad else "●"
            st.markdown(f"""
            <div class="sensor-card {'sensor-card-bad' if is_bad else ''}">
                <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                    <span style='font-size:11px; color:#3d5a7a;'>{icon} {name}</span>
                    <span style='font-size:12px; font-weight:700; color:{color};
                    font-family:"JetBrains Mono",monospace;'>{val:.2f}{unit}</span>
                </div>
                <div style='background:#070b14; border-radius:3px; height:3px; overflow:hidden;'>
                    <div style='width:{min(100,abs(pct))}%; background:{color}; height:100%;
                    border-radius:3px; transition:width 0.5s;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if prediction['violations']:
            st.markdown('<div class="section-title" style="margin-top:16px;">⚠️ Active Violations</div>', unsafe_allow_html=True)
            for feat, info in prediction['violations'].items():
                c = "#ef4444" if info['severity']=='CRITICAL' else "#f59e0b"
                short = feat.replace(' (kN)','').replace(' (Nm)','').replace(' RMS (mm/s)','').replace(' (°C)','').replace(' (mm)','').replace(' (%)','')
                st.markdown(f"""
                <div style='padding:8px 10px; background:rgba(239,68,68,0.06);
                border:1px solid {c}33; border-left:3px solid {c};
                border-radius:6px; margin-bottom:6px;'>
                    <span style='font-size:11px; color:{c}; font-weight:600;'>{short}</span>
                    <span style='font-size:10px; color:{c}88; margin-left:8px;'>{info['severity']}</span>
                    <div style='font-size:11px; color:#475569; margin-top:2px;'>{info['value']} / limit {info['safe_max']}</div>
                </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2 — MODEL COMPARISON
# ════════════════════════════════════════════════════════
with tab2:
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
            use_container_width=True, hide_index=True, height=220
        )

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            for metric, color in [('Accuracy','#3b82f6'),('F1 Score','#10b981'),('ROC-AUC','#f59e0b')]:
                fig.add_trace(go.Bar(name=metric, x=comp_df['Model'], y=comp_df[metric],
                    marker_color=color, opacity=0.9, marker_line_width=0))
            fig.update_layout(barmode='group', title='Model Metrics',
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
                line=dict(color='#1e3a5f', width=2), name='CV ± Std'))
            fig2.update_layout(title='Cross-Validation (5-Fold ± Std)',
                paper_bgcolor='#0d1829', plot_bgcolor='#0d1829', font_color='#64748b',
                height=350, xaxis=dict(gridcolor='#0f2040'), yaxis=dict(gridcolor='#0f2040', range=[0.88,1.01]),
                margin=dict(t=40,b=20))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        <div style='background:#0d1829; border:1px solid #0f2040; border-radius:10px; padding:14px 18px; font-size:13px; color:#64748b;'>
            💡 <strong style='color:#60a5fa;'>Best model auto-selected by ROC-AUC.</strong>
            SMOTE applied for class imbalance. All experiments tracked in MLflow.
            Run <code style='color:#f59e0b; background:#080d1a; padding:2px 6px; border-radius:4px;'>mlflow ui</code> to view experiment history.
        </div>""", unsafe_allow_html=True)

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
                text=[f"{v:+.4f}" for v in shap_df['SHAP Value']],
                textposition='outside',
                textfont=dict(family='JetBrains Mono', size=11, color='#94a3b8')
            ))
            fig.add_vline(x=0, line_color='#1e3a5f', line_width=1)
            fig.update_layout(
                title=f'SHAP Waterfall — {gear_name} ({fault})',
                paper_bgcolor='#0d1829', plot_bgcolor='#0d1829',
                font_color='#64748b', height=380,
                xaxis=dict(gridcolor='#0f2040', title='SHAP Impact'),
                yaxis=dict(gridcolor='#0f2040'),
                margin=dict(t=40,b=20,r=80)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟢 Green = keeping gear healthy | 🔴 Red = risk factor" if fault == "No Fault" else "🔴 Red = toward fault | 🟢 Green = reducing risk")

        with c2:
            st.markdown('<div class="section-title">Feature Impact Cards</div>', unsafe_allow_html=True)
            for _, row in shap_df.iterrows():
                val = row['SHAP Value']
                color = "#ef4444" if val > 0 else "#10b981"
                direction = "↑ Toward Fault" if val > 0 else "↓ Away from Fault"
                bar_w = min(100, int(abs(val)*250))
                st.markdown(f"""
                <div style='background:#0d1829; border:1px solid #0f2040; border-radius:8px;
                padding:10px 12px; margin-bottom:8px; transition:all 0.2s;'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                        <span style='font-size:12px; color:#64748b; font-weight:500;'>{row['Feature']}</span>
                        <span style='font-size:11px; color:{color}; font-family:monospace; font-weight:700;'>{val:+.4f}</span>
                    </div>
                    <div style='background:#070b14; border-radius:3px; height:5px; overflow:hidden; margin-bottom:5px;'>
                        <div style='width:{bar_w}%; background:linear-gradient(90deg,{color}88,{color});
                        height:100%; border-radius:3px;'></div>
                    </div>
                    <div style='font-size:10px; color:{color}; font-weight:600; letter-spacing:0.5px;'>{direction}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("Run `python xai/explain.py` to enable SHAP.")

    # ── LIME Section ──
    st.markdown("<div style='margin:32px 0 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">LIME — Local Interpretable Model-Agnostic Explanations</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#3d5a7a; font-size:13px; margin-bottom:20px;'>LIME perturbs the input locally and fits a simple linear model to cross-validate SHAP. If both agree on top features → model explanation is trustworthy.</p>", unsafe_allow_html=True)

    try:
        import lime
        import lime.lime_tabular

        shap_arts = joblib.load("xai/shap_artifacts.pkl")
        X_sample  = shap_arts["X_sample"]

        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_sample,
            feature_names=FEATURE_COLS,
            class_names=list(arts["le"].classes_),
            mode="classification",
            discretize_continuous=True,
            random_state=42
        )

        input_scaled = arts["scaler"].transform(
            np.array([sensor_values[f] for f in FEATURE_COLS]).reshape(1,-1)
        )[0]
        pred_encoded = arts["model"].predict(input_scaled.reshape(1,-1))[0]

        lime_result = lime_explainer.explain_instance(
            data_row=input_scaled,
            predict_fn=arts["model"].predict_proba,
            num_features=8,
            labels=[pred_encoded]
        )
        lime_list = lime_result.as_list(label=pred_encoded)
        lime_df   = pd.DataFrame(lime_list, columns=["Rule", "Weight"])
        lime_df   = lime_df.sort_values("Weight", key=abs, ascending=False)
        
        # For No Fault class: flip sign so green = healthy (same as SHAP fix)
        no_fault_idx = list(arts["le"].classes_).index("No Fault") if "No Fault" in list(arts["le"].classes_) else -1
        if pred_encoded == no_fault_idx:
            lime_df["Weight"] = -lime_df["Weight"]

        lc1, lc2 = st.columns([3, 2])

        with lc1:
            lime_colors = ["#ef4444" if w > 0 else "#10b981" for w in lime_df["Weight"]]
            fig_lime = go.Figure(go.Bar(
                x=lime_df["Weight"],
                y=lime_df["Rule"],
                orientation="h",
                marker_color=lime_colors,
                marker_line_width=0,
                text=[f"{w:+.4f}" for w in lime_df["Weight"]],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color="#94a3b8")
            ))
            fig_lime.add_vline(x=0, line_color="#1e3a5f", line_width=1)
            fig_lime.update_layout(
                title=f"LIME Explanation — {gear_name} ({fault})",
                paper_bgcolor="#0d1829", plot_bgcolor="#0d1829",
                font_color="#64748b", height=380,
                xaxis=dict(gridcolor="#0f2040", title="LIME Weight"),
                yaxis=dict(gridcolor="#0f2040"),
                margin=dict(t=40, b=20, r=80)
            )
            st.plotly_chart(fig_lime, use_container_width=True)
            st.caption("🔴 Toward fault  |  🟢 Away from fault  |  Rules show feature threshold conditions")

        with lc2:
            st.markdown('<div class="section-title">SHAP vs LIME Comparison</div>', unsafe_allow_html=True)

            # Compare top features from SHAP and LIME
            if prediction["shap_values"]:
                shap_top = sorted(prediction["shap_values"].items(), key=lambda x: abs(x[1]), reverse=True)[:5]
                lime_top = [(r.split(">")[0].split("<")[0].split("=")[0].strip(), w) for r, w in lime_list[:5]]

                for i, (sf, sv2) in enumerate(shap_top):
                    sc = "#ef4444" if sv2 > 0 else "#10b981"
                    lw = lime_df["Weight"].iloc[i] if i < len(lime_df) else 0
                    lc_color = "#ef4444" if lw > 0 else "#10b981"
                    agree = "✅" if (sv2 > 0) == (lw > 0) else "⚠️"
                    st.markdown(f"""
                    <div style='background:#0d1829; border:1px solid #0f2040; border-radius:8px;
                    padding:10px 12px; margin-bottom:8px;'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                            <span style='font-size:11px; color:#64748b; font-weight:500;'>{sf}</span>
                            <span style='font-size:12px;'>{agree}</span>
                        </div>
                        <div style='display:flex; justify-content:space-between;'>
                            <span style='font-size:11px; color:{sc}; font-family:monospace;'>SHAP: {sv2:+.4f}</span>
                            <span style='font-size:11px; color:{lc_color}; font-family:monospace;'>LIME: {lw:+.4f}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                agree_count = sum(1 for i, (sf, sv2) in enumerate(shap_top)
                                  if i < len(lime_df) and (sv2 > 0) == (lime_df["Weight"].iloc[i] > 0))
                agree_pct = agree_count / min(5, len(shap_top)) * 100
                agree_color = "#10b981" if agree_pct >= 80 else "#f59e0b"
                st.markdown(f"""
                <div style='background:{agree_color}11; border:1px solid {agree_color}44;
                border-radius:8px; padding:12px; text-align:center; margin-top:8px;'>
                    <div style='font-size:22px; font-weight:800; color:{agree_color};'>{agree_pct:.0f}%</div>
                    <div style='font-size:11px; color:{agree_color}; margin-top:4px;'>SHAP-LIME Agreement</div>
                    <div style='font-size:10px; color:#3d5a7a; margin-top:4px;'>
                        {"High agreement — explanations are trustworthy ✅" if agree_pct >= 80 else "Partial agreement — review borderline features"}
                    </div>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"LIME unavailable: {e}")

# ════════════════════════════════════════════════════════
# TAB 4 — ANOMALY & TIMELINE
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Anomaly Detection + Fault Progression Timeline</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Anomaly Status", prediction['anomaly_status'])
    c2.metric("Anomaly Score",  f"{prediction['anomaly_score']:.4f}")
    c3.metric("Violations",     len(prediction['violations']))

    st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)

    if arts.get('xai_ready') and arts.get('progression') is not None:
        prog = arts['progression']
        color_map = {'No Fault':'#10b981','Minor Fault':'#f59e0b','Major Fault':'#ef4444'}
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prog['Cycle'],y=prog['Vibration'],name='Vibration (mm/s)',
            line=dict(color='#3b82f6',width=2.5), fill='tozeroy', fillcolor='rgba(59,130,246,0.05)'))
        fig.add_trace(go.Scatter(x=prog['Cycle'],y=prog['Temperature']/15,name='Temp/15',
            line=dict(color='#f59e0b',width=2,dash='dot')))
        fig.add_trace(go.Scatter(x=prog['Cycle'],y=prog['Wear']*10,name='Wear×10',
            line=dict(color='#ef4444',width=2,dash='dash')))
        prev = None
        for _, row in prog.iterrows():
            if row['Fault Label'] != prev:
                fig.add_vline(x=row['Cycle'],
                    line_color=color_map.get(row['Fault Label'],'#fff'),
                    line_dash="dash", line_width=1.5,
                    annotation_text=row['Fault Label'],
                    annotation_font_color=color_map.get(row['Fault Label'],'#fff'),
                    annotation_font_size=11)
                prev = row['Fault Label']
        fig.update_layout(
            title='Gear Degradation Timeline — Vibration · Temperature · Wear',
            paper_bgcolor='#0d1829', plot_bgcolor='#0d1829',
            font_color='#64748b', height=420,
            xaxis=dict(gridcolor='#0f2040',title='Cycles in Use'),
            yaxis=dict(gridcolor='#0f2040',title='Sensor Value (scaled)'),
            legend=dict(bgcolor='#0d1829',bordercolor='#0f2040',borderwidth=1),
            margin=dict(t=50,b=30)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Dashed vertical lines = fault classification transition points | Anomaly detected before fault classification")
    else:
        st.warning("Run `python xai/explain.py` to generate timeline.")

# ════════════════════════════════════════════════════════
# TAB 5 — WHAT-IF SIMULATOR
# ════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">What-If Scenario Simulator</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#3d5a7a; font-size:13px; margin-bottom:20px;'>Simulate how changing one parameter affects fault prediction and RUL in real-time.</p>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        what_feature = st.selectbox("Parameter to modify:", FEATURE_COLS)
        mins = {'Load (kN)':10.0,'Torque (Nm)':50.0,'Vibration RMS (mm/s)':0.5,
                'Temperature (°C)':40.0,'Wear (mm)':0.0,'Lubrication Index':0.05,
                'Efficiency (%)':70.0,'Cycles in Use':0.0}
        maxs = {'Load (kN)':120.0,'Torque (Nm)':600.0,'Vibration RMS (mm/s)':30.0,
                'Temperature (°C)':150.0,'Wear (mm)':4.0,'Lubrication Index':1.0,
                'Efficiency (%)':99.0,'Cycles in Use':100000.0}
        new_val = st.slider(f"New value:", float(mins[what_feature]), float(maxs[what_feature]),
                            float(sensor_values[what_feature]), key="wif_slider")
        run_sim = st.button("▶ Run Simulation", type="primary", use_container_width=True)

    with c2:
        mod = sensor_values.copy()
        mod[what_feature] = new_val
        mod_pred  = predict_gear_health(mod)
        delta_rul = mod_pred['rul_cycles'] - rul
        delta_col = "#10b981" if delta_rul > 0 else "#ef4444"
        delta_icon= "📈" if delta_rul > 0 else "📉"

        st.markdown(f"""
        <div style='background:#0d1829; border:1px solid #0f2040; border-radius:14px; padding:22px;'>
            <div style='font-size:10px; color:#1e3a5f; letter-spacing:2px; font-weight:700; margin-bottom:18px;'>SIMULATION RESULT</div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:18px;'>
                <div style='background:#080d1a; border-radius:10px; padding:14px; border:1px solid #0f2040;'>
                    <div style='font-size:9px; color:#1e3a5f; letter-spacing:1px; margin-bottom:8px;'>BEFORE</div>
                    <div style='font-size:16px; font-weight:800; color:#e2e8f0;'>{fault}</div>
                    <div style='font-size:11px; color:#3d5a7a; margin-top:4px;'>{conf:.1%} confidence</div>
                    <div style='font-size:11px; color:#3d5a7a; margin-top:2px;'>{rul:,} cycles</div>
                </div>
                <div style='background:#080d1a; border-radius:10px; padding:14px; border:1px solid {delta_col}44;'>
                    <div style='font-size:9px; color:#1e3a5f; letter-spacing:1px; margin-bottom:8px;'>AFTER</div>
                    <div style='font-size:16px; font-weight:800; color:#e2e8f0;'>{mod_pred['fault_label']}</div>
                    <div style='font-size:11px; color:#3d5a7a; margin-top:4px;'>{mod_pred['confidence']:.1%} confidence</div>
                    <div style='font-size:11px; color:{delta_col}; margin-top:2px; font-weight:700;'>{mod_pred['rul_cycles']:,} cycles</div>
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

    if run_sim and os.environ.get("GROQ_API_KEY"):
        with st.spinner("Running AI analysis..."):
            try:
                result = simulate_what_if(sensor_values, what_feature, new_val, gear_name)
                formatted = md_to_html(result['explanation'])
                st.markdown(f"""
                <div style='background:#080d1a; border:1px solid #1e3a5f; border-radius:12px;
                padding:20px; margin-top:20px;'>
                    <div style='font-size:10px; color:#3b82f6; font-weight:700; letter-spacing:1.5px; margin-bottom:12px;'>
                        ⚙ GEARMIND AI ANALYSIS
                    </div>
                    <div style='font-size:14px; color:#c9d6e8; line-height:1.7;'>{formatted}</div>
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
            <div style='display:flex; flex-direction:column; gap:10px;'>
                {"".join([f'''<div style="display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid #0f2040;">
                <span style="color:#2563eb; font-size:12px;">✦</span>
                <span style="font-size:13px; color:#64748b;">{item}</span></div>'''
                for item in [
                    f'Executive Summary',
                    f'Fault Assessment — {fault} ({conf:.0%} confidence)',
                    'Root Cause Analysis (SHAP-backed)',
                    f'RUL Estimate — {rul:,} cycles ({rul//400} shifts)',
                    'Prioritized Action Plan with timeline',
                    'Cost-Benefit Analysis (INR)',
                    'Post-Maintenance Monitoring Protocol'
                ]])}
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)
        if st.button("📄 Generate AI Report", type="primary", use_container_width=True):
            if os.environ.get("GROQ_API_KEY"):
                with st.spinner("GearMind AI writing report..."):
                    try:
                        report = generate_maintenance_report(prediction, gear_name)
                        st.session_state.generated_report = report
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Add your Groq API key in the sidebar.")

    with r2:
        if 'generated_report' in st.session_state:
            formatted_report = md_to_html(st.session_state.generated_report)
            st.markdown(f"""
            <div style='background:#080d1a; border:1px solid #1e3a5f; border-radius:12px;
            padding:20px; max-height:450px; overflow-y:auto;'>
                <div style='font-size:10px; color:#3b82f6; font-weight:700; letter-spacing:1.5px; margin-bottom:14px;'>
                    ⚙ GEARMIND AI — MAINTENANCE REPORT
                </div>
                <div style='font-size:13px; color:#c9d6e8; line-height:1.8;'>{formatted_report}</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇️ Download Report (.txt)",
                data=st.session_state.generated_report,
                file_name=f"GearMind_Report_{gear_name}.txt",
                mime="text/plain", use_container_width=True)
        else:
            st.markdown("""
            <div style='background:#080d1a; border:2px dashed #0f2040; border-radius:14px;
            padding:60px 40px; text-align:center;'>
                <div style='font-size:40px; margin-bottom:16px;'>📄</div>
                <div style='font-size:15px; font-weight:600; color:#1e3a5f; margin-bottom:8px;'>Report will appear here</div>
                <div style='font-size:12px; color:#0f2040;'>Click Generate AI Report to create<br>a full maintenance analysis</div>
            </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:30px 0 10px; color:#0f2040; font-size:11px; letter-spacing:0.5px;'>
    ⚙ GearMind AI v3.0 · Elecon Engineering Works Pvt. Ltd., Anand, Gujarat<br>
    <span style='color:#0a1422;'>GBM · XGBoost · RF · LR · SVM · SHAP · LIME · Isolation Forest · LLaMA 3.3 70B · MLflow</span>
</div>
""", unsafe_allow_html=True)
