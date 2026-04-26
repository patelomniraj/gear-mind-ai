import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import joblib
import shap
import lime.lime_tabular
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import sqlite3
from datetime import datetime, timedelta
import calendar
from scipy.optimize import minimize, differential_evolution
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
import os
import json
import openai
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Spur Gear AI Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# ANIMATED BACKGROUND
# -------------------------------------------------------
st.markdown("""
<canvas id="gear-canvas"></canvas>
<script>
(function() {
    const canvas = document.getElementById('gear-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Particle config
    const NUM_PARTICLES = 55;
    const CYAN   = 'rgba(0,174,239,';
    const TEAL   = 'rgba(0,200,150,';

    const particles = Array.from({length: NUM_PARTICLES}, () => ({
        x:    Math.random() * window.innerWidth,
        y:    Math.random() * window.innerHeight,
        r:    1.2 + Math.random() * 2.8,
        vx:   (Math.random() - 0.5) * 0.35,
        vy:   (Math.random() - 0.5) * 0.35,
        alpha: 0.15 + Math.random() * 0.55,
        color: Math.random() > 0.5 ? CYAN : TEAL,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.008 + Math.random() * 0.012,
    }));

    // Connection lines between nearby particles
    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 140) {
                    const opacity = (1 - dist / 140) * 0.12;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0,174,239,${opacity})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }
    }

    // Slow horizontal scan line
    let scanY = 0;

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Scan line
        scanY = (scanY + 0.4) % canvas.height;
        const scanGrad = ctx.createLinearGradient(0, scanY - 40, 0, scanY + 40);
        scanGrad.addColorStop(0,   'rgba(0,174,239,0)');
        scanGrad.addColorStop(0.5, 'rgba(0,174,239,0.04)');
        scanGrad.addColorStop(1,   'rgba(0,174,239,0)');
        ctx.fillStyle = scanGrad;
        ctx.fillRect(0, scanY - 40, canvas.width, 80);

        drawLines();

        for (const p of particles) {
            p.pulse += p.pulseSpeed;
            const glowAlpha = p.alpha * (0.7 + 0.3 * Math.sin(p.pulse));

            // Glow halo
            const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 5);
            grd.addColorStop(0,   p.color + (glowAlpha * 0.6).toFixed(3) + ')');
            grd.addColorStop(1,   p.color + '0)');
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * 5, 0, Math.PI * 2);
            ctx.fillStyle = grd;
            ctx.fill();

            // Core dot
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color + glowAlpha.toFixed(3) + ')';
            ctx.fill();

            p.x += p.vx;
            p.y += p.vy;

            if (p.x < -10) p.x = canvas.width + 10;
            if (p.x > canvas.width + 10) p.x = -10;
            if (p.y < -10) p.y = canvas.height + 10;
            if (p.y > canvas.height + 10) p.y = -10;
        }

        requestAnimationFrame(animate);
    }
    animate();
})();
</script>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# THEME
# -------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/*
 * PALETTE — COLD INDUSTRIAL / CONTROL ROOM
 *
 * Background:  #0B0E14  near-black with blue-grey undertone (night sky / control room)
 * Base noise:  SVG grain overlay for realism
 * Surface:     #111620  deep navy-charcoal panels
 * Raised:      #182030  elevated cards — clear depth step
 * Border:      #243048  cool slate-blue border
 * Muted text:  #5A6A80  desaturated cool blue-grey
 * Body text:   #A8B8CC  cool silver
 * Bright text: #D6E4F0  near-white with blue tint (SCADA readout)
 * Accent:      #00AEEF  electric cyan — HMI/SCADA active blue
 * Acc dim:     #007DB3  darker cyan for depth
 * OK:          #00C896  cool teal-green (not warm green)
 * Warn:        #F5A623  amber — universal caution (kept warm intentionally for contrast)
 * Danger:      #E8394A  cool red
 */

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Realistic background: deep blue-grey + subtle noise grain */
.stApp {
    background-color: #0B0E14;
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    background-repeat: repeat;
}

/* ── ANIMATED BACKGROUND CANVAS ── */
#gear-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0;
    pointer-events: none;
    opacity: 0.55;
}

.stApp, .stApp p, .stApp span, .stApp div,
[data-testid="stAppViewContainer"] { color: #A8B8CC; }

/* ── SIDEBAR ── cool dark navy with cyan border */
section[data-testid="stSidebar"] {
    background: #0D1018;
    border-right: 2px solid #00AEEF !important;
    box-shadow: 4px 0 24px rgba(0,174,239,0.06);
}
section[data-testid="stSidebar"] * { color: #7A8DA0 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #D6E4F0 !important; font-weight: 600; }
section[data-testid="stSidebar"] .stSelectbox label {
    color: #00AEEF !important; font-size: 12px !important;
    text-transform: uppercase; letter-spacing: 0.08em;
}
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
    background: #00AEEF !important; border: 2px solid #5DD4F7 !important;
}
section[data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {
    background: #007DB3 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent; gap: 4px;
    border-bottom: 1px solid #243048; padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border: none; color: #5A6A80;
    font-weight: 500; font-size: 14px; padding: 10px 20px;
    border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    background: transparent !important; color: #D6E4F0 !important;
    border-bottom: 2px solid #00AEEF !important; font-weight: 600;
}

/* ── CARDS ── frosted steel panels */
.metric-card {
    background: #111620;
    border-radius: 10px; padding: 20px 24px;
    border: 1px solid #243048;
    box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset,
                0 4px 16px rgba(0,0,0,0.5),
                0 0 0 0.5px rgba(0,174,239,0.05);
}
.section-card {
    background: #111620;
    border-radius: 12px; padding: 28px 32px;
    border: 1px solid #243048;
    box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset,
                0 6px 20px rgba(0,0,0,0.45),
                0 0 0 0.5px rgba(0,174,239,0.05);
    margin-bottom: 20px;
}

/* ── BADGES ── */
.badge-failure {
    display: inline-block; background: #1E0D11; color: #E8394A;
    border: 1px solid #4A1820; border-radius: 6px; padding: 6px 16px;
    font-weight: 600; font-size: 14px;
}
.badge-ok {
    display: inline-block; background: #0A2018; color: #00C896;
    border: 1px solid #0F3828; border-radius: 6px; padding: 6px 16px;
    font-weight: 600; font-size: 14px;
}

/* ── TYPOGRAPHY ── */
h1 { color: #D6E4F0 !important; font-weight: 700 !important; }
h2, h3 { color: #A8B8CC !important; font-weight: 600 !important; }
strong { color: #D6E4F0; }

.metric-label {
    font-size: 11px; color: #5A6A80; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 500; margin-bottom: 4px;
}
.metric-value {
    font-size: 28px; font-weight: 700; color: #D6E4F0;
    font-family: 'DM Mono', monospace;
}

/* ── INSIGHT BOXES ── */
.insight-box {
    background: #0A1C18; border-left: 3px solid #00C896;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 12px 0;
    font-size: 14px; color: #5EEBC8; line-height: 1.6;
}
.insight-box-warn {
    background: #1C1608; border-left: 3px solid #F5A623;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 12px 0;
    font-size: 14px; color: #F8C96A; line-height: 1.6;
}
.insight-box-danger {
    background: #1E0D11; border-left: 3px solid #E8394A;
    border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 12px 0;
    font-size: 14px; color: #F0707A; line-height: 1.6;
}

/* ── BUTTONS ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #007DB3, #00AEEF) !important;
    color: #FFFFFF !important;
    border: 1px solid #5DD4F7 !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #00AEEF, #5DD4F7) !important;
    box-shadow: 0 0 20px rgba(0,174,239,0.45) !important;
}

.stButton > button {
    background-color: #182030 !important;
    color: #A8B8CC !important;
    border: 1px solid #243048 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background-color: #00AEEF !important;
    color: #0B0E14 !important;
    border-color: #00AEEF !important;
    box-shadow: 0 0 14px rgba(0,174,239,0.4) !important;
}

/* ── TEXT INPUT ── */
.stTextInput > div > div > input {
    background: #0D1018 !important;
    color: #D6E4F0 !important;
    border: 1px solid #243048 !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00AEEF !important;
    box-shadow: 0 0 0 2px rgba(0,174,239,0.2) !important;
}
.stTextInput > div > div > input::placeholder { color: #3A4A5C !important; }

/* ── SELECTBOX ── */
.stSelectbox > div > div {
    background: #111620 !important;
    color: #A8B8CC !important;
    border: 1px solid #243048 !important;
}

/* ── CHAT BUBBLES ── */
.chat-user {
    background: linear-gradient(135deg, #0F1E35, #182848) !important;
    color: #7DD4F8 !important;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 18px; margin: 8px 0 8px auto; max-width: 75%;
    font-size: 14px; line-height: 1.6; width: fit-content; margin-left: auto;
    border: 1px solid #243D60 !important;
}
.chat-ai {
    background: #111620 !important; color: #A8B8CC !important;
    border-radius: 16px 16px 16px 4px;
    padding: 12px 18px; margin: 8px auto 8px 0; max-width: 80%;
    font-size: 14px; line-height: 1.7;
    border: 1px solid #243048 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.4); width: fit-content;
}
.chat-label-user {
    text-align: right; font-size: 11px; color: #5A6A80;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-bottom: 2px; margin-right: 4px;
}
.chat-label-ai {
    font-size: 11px; color: #00AEEF;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-bottom: 2px; margin-left: 4px;
}

/* Briefing box */
.briefing-box {
    background: #0D1018 !important; border: 1px solid #243048 !important;
    border-radius: 10px; padding: 16px 20px;
    font-size: 13px; color: #5DD4F7 !important;
    font-family: 'DM Mono', monospace; line-height: 1.8; margin-bottom: 20px;
}
.briefing-title {
    font-size: 11px; color: #00AEEF; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 600; margin-bottom: 10px;
    font-family: 'DM Sans', sans-serif;
}

/* Divider */
hr { border: none; border-top: 1px solid #243048; margin: 20px 0; }

/* Spinner */
.stSpinner > div { border-top-color: #00AEEF !important; }


/* Scrollbar */
::-webkit-scrollbar { width: 6px; background: #0B0E14; }
::-webkit-scrollbar-thumb { background: #243048; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00AEEF; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------
st.markdown(f"""
<div style='position:relative;overflow:hidden;padding:0 0 18px 0;margin-bottom:4px'>

  <!-- Photorealistic spur gear SVGs — left side (large, fading into background) -->
  <div style='position:absolute;left:-28px;top:-18px;opacity:0.22;pointer-events:none;z-index:0'>
    <svg width="210" height="210" viewBox="-110 -110 220 220" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="gL1" cx="35%" cy="30%" r="65%">
          <stop offset="0%" stop-color="#B8C8DC"/>
          <stop offset="40%" stop-color="#6A7A8C"/>
          <stop offset="100%" stop-color="#1A2230"/>
        </radialGradient>
        <radialGradient id="gL2" cx="40%" cy="35%" r="60%">
          <stop offset="0%" stop-color="#8899AA"/>
          <stop offset="100%" stop-color="#141E28"/>
        </radialGradient>
        <filter id="fL"><feGaussianBlur in="SourceAlpha" stdDeviation="1.2"/><feOffset dx="2" dy="3"/><feComposite in2="SourceGraphic" operator="over"/></filter>
        <linearGradient id="toothGL" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#C8D8E8"/>
          <stop offset="50%" stop-color="#7A8A9A"/>
          <stop offset="100%" stop-color="#2A3A4A"/>
        </linearGradient>
      </defs>
      <!-- Gear body with teeth - 18 teeth -->
      <g filter="url(#fL)">
      {"".join([
        f'<path d="M {85*__import__("math").cos(i*3.14159*2/18-0.09):.1f} {85*__import__("math").sin(i*3.14159*2/18-0.09):.1f} L {100*__import__("math").cos(i*3.14159*2/18-0.05):.1f} {100*__import__("math").sin(i*3.14159*2/18-0.05):.1f} L {100*__import__("math").cos(i*3.14159*2/18+0.05):.1f} {100*__import__("math").sin(i*3.14159*2/18+0.05):.1f} L {85*__import__("math").cos(i*3.14159*2/18+0.09):.1f} {85*__import__("math").sin(i*3.14159*2/18+0.09):.1f} Z" fill="url(#toothGL)" stroke="#1A2530" stroke-width="0.5"/>'
        for i in range(18)
      ])}
      <circle r="85" fill="url(#gL1)" stroke="#0A1520" stroke-width="1"/>
      <!-- Spoke holes -->
      {"".join([f'<circle cx="{60*__import__("math").cos(i*3.14159*2/6):.1f}" cy="{60*__import__("math").sin(i*3.14159*2/6):.1f}" r="14" fill="#050A10" stroke="#1A2530" stroke-width="0.8"/>' for i in range(6)])}
      <!-- Hub ring -->
      <circle r="28" fill="url(#gL2)" stroke="#0A1520" stroke-width="1.2"/>
      <circle r="14" fill="#030608" stroke="#1A2530" stroke-width="0.8"/>
      <!-- Surface highlight arc -->
      <path d="M -55 -60 A 85 85 0 0 1 30 -80" stroke="#D6E4F0" stroke-width="1.5" fill="none" opacity="0.4" stroke-linecap="round"/>
      <!-- Rim groove -->
      <circle r="78" fill="none" stroke="#0A1520" stroke-width="2"/>
      <circle r="72" fill="none" stroke="#3A4A5A" stroke-width="0.5"/>
      </g>
    </svg>
  </div>

  <!-- Photorealistic spur gear SVGs — right side (medium, partially clipped) -->
  <div style='position:absolute;right:-15px;top:-22px;opacity:0.18;pointer-events:none;z-index:0'>
    <svg width="180" height="180" viewBox="-90 -90 180 180" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="gR1" cx="40%" cy="28%" r="62%">
          <stop offset="0%" stop-color="#A8B8C8"/>
          <stop offset="45%" stop-color="#586878"/>
          <stop offset="100%" stop-color="#141E28"/>
        </radialGradient>
        <linearGradient id="toothGR" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#B8C8D8"/>
          <stop offset="50%" stop-color="#6A7A8A"/>
          <stop offset="100%" stop-color="#222E3A"/>
        </linearGradient>
      </defs>
      <!-- 24 teeth gear -->
      {"".join([
        f'<path d="M {68*__import__("math").cos(i*3.14159*2/24-0.07):.1f} {68*__import__("math").sin(i*3.14159*2/24-0.07):.1f} L {80*__import__("math").cos(i*3.14159*2/24-0.04):.1f} {80*__import__("math").sin(i*3.14159*2/24-0.04):.1f} L {80*__import__("math").cos(i*3.14159*2/24+0.04):.1f} {80*__import__("math").sin(i*3.14159*2/24+0.04):.1f} L {68*__import__("math").cos(i*3.14159*2/24+0.07):.1f} {68*__import__("math").sin(i*3.14159*2/24+0.07):.1f} Z" fill="url(#toothGR)" stroke="#1A2530" stroke-width="0.4"/>'
        for i in range(24)
      ])}
      <circle r="68" fill="url(#gR1)" stroke="#0A1520" stroke-width="1"/>
      {"".join([f'<circle cx="{48*__import__("math").cos(i*3.14159*2/6):.1f}" cy="{48*__import__("math").sin(i*3.14159*2/6):.1f}" r="11" fill="#050A10" stroke="#1A2530" stroke-width="0.6"/>' for i in range(6)])}
      <circle r="22" fill="#0A1018" stroke="#0A1520" stroke-width="1"/>
      <circle r="11" fill="#030608" stroke="#1A2530" stroke-width="0.6"/>
      <path d="M -40 -50 A 68 68 0 0 1 25 -62" stroke="#C8D8E8" stroke-width="1.2" fill="none" opacity="0.35" stroke-linecap="round"/>
      <circle r="62" fill="none" stroke="#0A1520" stroke-width="1.5"/>
    </svg>
  </div>

  <!-- Third small gear — bottom right accent -->
  <div style='position:absolute;right:80px;bottom:-8px;opacity:0.12;pointer-events:none;z-index:0'>
    <svg width="90" height="90" viewBox="-45 -45 90 90" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="gS1" cx="35%" cy="30%" r="65%"><stop offset="0%" stop-color="#8898A8"/><stop offset="100%" stop-color="#0E1820"/></radialGradient>
      </defs>
      {"".join([f'<path d="M {34*__import__("math").cos(i*3.14159*2/12-0.14):.1f} {34*__import__("math").sin(i*3.14159*2/12-0.14):.1f} L {40*__import__("math").cos(i*3.14159*2/12-0.08):.1f} {40*__import__("math").sin(i*3.14159*2/12-0.08):.1f} L {40*__import__("math").cos(i*3.14159*2/12+0.08):.1f} {40*__import__("math").sin(i*3.14159*2/12+0.08):.1f} L {34*__import__("math").cos(i*3.14159*2/12+0.14):.1f} {34*__import__("math").sin(i*3.14159*2/12+0.14):.1f} Z" fill="#4A5A6A" stroke="#1A2530" stroke-width="0.4"/>' for i in range(12)])}
      <circle r="34" fill="url(#gS1)" stroke="#0A1520" stroke-width="0.8"/>
      {"".join([f'<circle cx="{22*__import__("math").cos(i*3.14159*2/4):.1f}" cy="{22*__import__("math").sin(i*3.14159*2/4):.1f}" r="5" fill="#050A10" stroke="#1A2530" stroke-width="0.5"/>' for i in range(4)])}
      <circle r="10" fill="#050A10" stroke="#0A1520" stroke-width="0.7"/>
      <circle r="5" fill="#030608"/>
    </svg>
  </div>

  <!-- Actual header content on top -->
  <div style='position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;padding:10px 0 4px 0'>
    <div style='display:flex;align-items:center;gap:14px'>
      <div style='background:linear-gradient(135deg,#005A8A,#00AEEF);border-radius:10px;padding:11px 13px;
                  box-shadow:0 0 18px rgba(0,174,239,.35),0 2px 8px rgba(0,0,0,.4);flex-shrink:0'>
        <span style='font-size:22px;line-height:1'>⚙</span>
      </div>
      <div>
        <h1 style='margin:0;font-size:23px;font-weight:800;color:#D6E4F0;letter-spacing:-.01em;
                   text-shadow:0 0 30px rgba(0,174,239,.15)'>Spur Gear AI Failure Monitor</h1>
        <p style='margin:0;font-size:12px;color:#4A6080;margin-top:3px;letter-spacing:.04em'>
          Predictive Maintenance &nbsp;·&nbsp; Machine Learning &nbsp;·&nbsp; Explainable AI
        </p>
      </div>
    </div>
    <div style='text-align:right;flex-shrink:0'>
      <div style='font-size:10px;color:#374A60;text-transform:uppercase;letter-spacing:.1em'>Last Updated</div>
      <div style='font-size:13px;font-weight:600;color:#D6E4F0;font-family:"DM Mono",monospace;margin-top:2px'>
        {datetime.now().strftime('%d %b %Y  %H:%M')}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOAD MODEL + DATASET
# -------------------------------------------------------
model  = joblib.load("spur_gear_svm_model.pkl")
scaler = joblib.load("spur_gear_scaler.pkl")

# Load dataset — used as SHAP background (100 random samples)
@st.cache_resource(show_spinner=False)
def load_background():
    df   = pd.read_csv("spur_gear_svm_dataset.csv")
    X    = df.drop(columns=["Failure"])
    X_sc = scaler.transform(X)
    # Sample 100 rows — enough for KernelExplainer, keeps it fast
    rng  = np.random.default_rng(0)
    idx  = rng.choice(len(X_sc), size=100, replace=False)
    return X_sc[idx]

bg_data = load_background()

# -------------------------------------------------------
# MODULE 1 — SQLITE HISTORY LOGGER
# -------------------------------------------------------
DB_PATH = "gear_history.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gear_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            gear_type   TEXT,
            speed       REAL,
            torque      REAL,
            vibration   REAL,
            temperature REAL,
            shock       REAL,
            noise       REAL,
            max_cycles  INTEGER,
            fail_prob   REAL,
            prediction  INTEGER,
            risk_label  TEXT,
            health_score REAL,
            rul_cycles  REAL,
            rul_hours   REAL
        )
    """)
    con.commit()
    con.close()

init_db()

def log_reading(gear_type, speed, torque, vibration, temperature, shock, noise,
                max_cycles, fail_prob, prediction, risk_label, health_score,
                rul_cycles, rul_hours):
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        INSERT INTO gear_log
            (timestamp, gear_type, speed, torque, vibration, temperature, shock, noise,
             max_cycles, fail_prob, prediction, risk_label, health_score, rul_cycles, rul_hours)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          gear_type, speed, torque, vibration, temperature, shock, noise,
          max_cycles, fail_prob, prediction, risk_label, health_score,
          rul_cycles, rul_hours))
    con.commit()
    con.close()

def load_history() -> pd.DataFrame:
    con = sqlite3.connect(DB_PATH)
    df  = pd.read_sql_query(
        "SELECT * FROM gear_log ORDER BY timestamp DESC", con)
    con.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def clear_history():
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM gear_log")
    con.commit()
    con.close()

# Danger-zone thresholds (mirrors sidebar ranges — top 25% of each param range)
DANGER_THRESHOLDS = {
    "speed":       2375,   # RPM  > 75 % of 500-3000
    "torque":      287,    # Nm   > 75 % of 50-400
    "vibration":   7.6,    # mm/s > 75 % of 0.5-10
    "temperature": 97,     # °C   > 75 % of 30-120
    "shock":       4.4,    # g    > 75 % of 0.1-6
    "noise":       87,     # dB   > 75 % of 50-100
}

# -------------------------------------------------------
st.sidebar.markdown("""
<div style='padding:16px 0 8px 0'>
    <div style='font-size:11px;color:#00AEEF;text-transform:uppercase;
                letter-spacing:0.1em;font-weight:600;margin-bottom:4px'>Gear Configuration</div>
</div>
""", unsafe_allow_html=True)
gear_type = st.sidebar.selectbox("Gear Type", ["Spur Gear A", "Spur Gear B", "Spur Gear C"])

st.sidebar.markdown("""
<div style='padding:16px 0 8px 0'>
    <div style='font-size:11px;color:#00AEEF;text-transform:uppercase;
                letter-spacing:0.1em;font-weight:600'>Operational Parameters</div>
</div>
""", unsafe_allow_html=True)

speed       = st.sidebar.slider("Speed (RPM)",       500,  3000,  1050)
torque      = st.sidebar.slider("Torque (Nm)",        50,   400,   110)
vibration   = st.sidebar.slider("Vibration (mm/s)",  0.5,  10.0,  1.4)
temperature = st.sidebar.slider("Temperature (°C)",   30,   120,   57)
shock       = st.sidebar.slider("Shock Load (g)",     0.1,   6.0,  1.7)
noise       = st.sidebar.slider("Noise (dB)",         50,   100,   74)

st.sidebar.markdown("""
<div style='padding:16px 0 8px 0'>
    <div style='font-size:11px;color:#00AEEF;text-transform:uppercase;
                letter-spacing:0.1em;font-weight:600'>RUL Configuration</div>
</div>
""", unsafe_allow_html=True)
max_cycles = st.sidebar.slider(
    "Max Expected Cycles", 500, 5000, 1000, step=100,
    help="Total cycles expected before scheduled overhaul. Set based on your gear's service spec."
)

st.sidebar.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='font-size:11px;color:#00AEEF;text-transform:uppercase;
            letter-spacing:0.1em;font-weight:600;margin-bottom:6px'>Data Logger</div>
""", unsafe_allow_html=True)
# Auto-log status placeholder — updated after prediction is computed below
_sidebar_log_status = st.sidebar.empty()

feature_names  = ["Speed_RPM","Torque_Nm","Vibration_mm_s","Temperature_C","Shock_Load_g","Noise_dB"]
feature_labels = ["Speed","Torque","Vibration","Temperature","Shock Load","Noise Level"]
param_values   = [speed, torque, vibration, temperature, shock, noise]
param_units    = ["RPM","Nm","mm/s","°C","g","dB"]
param_ranges   = [(500,3000),(50,400),(0.5,10.0),(30,120),(0.1,6.0),(50,100)]

input_df     = pd.DataFrame([param_values], columns=feature_names)
input_scaled = scaler.transform(input_df)

# -------------------------------------------------------
# PREDICTION
# -------------------------------------------------------
prediction  = model.predict(input_scaled)[0]
probability = model.predict_proba(input_scaled)[0][1]
prob_pct    = probability * 100

if prob_pct < 30:
    risk_label = "LOW RISK";      risk_color = "#16a34a"
elif prob_pct < 55:
    risk_label = "MODERATE RISK"; risk_color = "#d97706"
elif prob_pct < 80:
    risk_label = "HIGH RISK";     risk_color = "#ea580c"
else:
    risk_label = "CRITICAL RISK"; risk_color = "#dc2626"

# -------------------------------------------------------
# RUL COMPUTATION
# Derived from failure probability — no separate model needed.
# RUL = (1 - P_failure) × max_cycles
# Time = RUL / speed_rpm  (cycles ÷ rev/min = minutes)
# -------------------------------------------------------
health_score  = 1.0 - probability                        # 0 = dead, 1 = perfect
rul_cycles    = max(0, health_score * max_cycles)        # estimated cycles remaining
rul_minutes   = rul_cycles / speed if speed > 0 else 0  # convert to time at current RPM
rul_hours     = rul_minutes / 60

# ±10% confidence band
rul_low  = max(0, rul_cycles * 0.90)
rul_high = rul_cycles * 1.10

# RUL health label
if health_score > 0.70:
    rul_label = "GOOD";     rul_color = "#16a34a"
elif health_score > 0.45:
    rul_label = "DEGRADING"; rul_color = "#d97706"
elif health_score > 0.20:
    rul_label = "CRITICAL";  rul_color = "#ea580c"
else:
    rul_label = "END OF LIFE"; rul_color = "#dc2626"

# -------------------------------------------------------
# AUTO-LOG — fires whenever slider values change
# Compares current config against last-logged config stored in session_state.
# -------------------------------------------------------
_current_sig = (gear_type, speed, torque, vibration, temperature,
                shock, noise, max_cycles)

if "last_logged_sig" not in st.session_state:
    st.session_state.last_logged_sig = None

_auto_logged = False
if _current_sig != st.session_state.last_logged_sig:
    log_reading(gear_type, speed, torque, vibration, temperature, shock, noise,
                max_cycles, prob_pct, int(prediction), risk_label,
                health_score, rul_cycles, rul_hours)
    st.session_state.last_logged_sig = _current_sig
    _auto_logged = True

# Update sidebar status indicator
if _auto_logged:
    _sidebar_log_status.markdown(
        "<div style='font-size:12px;color:#00C896;padding:4px 0'>🟢 Auto-logged</div>",
        unsafe_allow_html=True)
else:
    _sidebar_log_status.markdown(
        "<div style='font-size:12px;color:#5A6A80;padding:4px 0'>⚪ No changes since last log</div>",
        unsafe_allow_html=True)

# -------------------------------------------------------
# REAL SHAP — KernelExplainer with 100-sample background
# Cached per unique input so it doesn't rerun on unrelated changes
# -------------------------------------------------------
@st.cache_data(show_spinner="Computing SHAP values…")
def compute_shap(input_tuple):
    arr       = np.array(input_tuple).reshape(1, -1)
    explainer = shap.KernelExplainer(model.predict_proba, bg_data)
    shap_vals = explainer.shap_values(arr, nsamples=200)

    # shap_vals can come back in different shapes depending on SHAP version + model:
    #   - list of 2 arrays [class0, class1], each shape (1, n_features)  → take [1][0]
    #   - single 2D array of shape (1, n_features)                        → take [0]
    #   - single 3D array of shape (1, n_features, n_classes)             → take [0, :, 1]
    if isinstance(shap_vals, list):
        # list of per-class arrays
        vals = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
    elif isinstance(shap_vals, np.ndarray):
        if shap_vals.ndim == 3:
            # shape (1, n_features, n_classes)
            vals = shap_vals[0, :, 1]
        else:
            # shape (1, n_features) — single output
            vals = shap_vals[0]
    else:
        vals = np.array(shap_vals).flatten()

    return vals

shap_values = compute_shap(tuple(input_scaled[0]))

shap_df = pd.DataFrame({
    "Feature": feature_labels,
    "Impact":  shap_values,
    "Value":   param_values,
    "Unit":    param_units,
}).assign(Abs=lambda d: d["Impact"].abs()).sort_values("Impact")

# -------------------------------------------------------
# LIME — Gaussian neighbourhood around scaled input
# -------------------------------------------------------
@st.cache_data(show_spinner="Computing LIME explanation…")
def compute_lime(input_tuple):
    arr = np.array(input_tuple).reshape(1, -1)
    rng = np.random.default_rng(42)
    bg  = arr + rng.normal(0, 0.20, (80, arr.shape[1]))
    exp = lime.lime_tabular.LimeTabularExplainer(
        training_data=bg,
        feature_names=feature_labels,
        class_names=["No Failure","Failure"],
        mode="classification",
        random_state=42,
    )
    result = exp.explain_instance(arr[0], model.predict_proba, num_features=6)
    return result.as_list()

lime_list = compute_lime(tuple(input_scaled[0]))

# -------------------------------------------------------
# AI COPILOT — system prompt (built here so the floating widget can access it)
# -------------------------------------------------------
_top_shap_feature = shap_df.sort_values("Impact", ascending=False).iloc[0]
_top_shap_stable  = shap_df.sort_values("Impact").iloc[0]
_top_lime_feat    = sorted(lime_list, key=lambda x: abs(x[1]), reverse=True)[0]

_briefing = f"""GEAR HEALTH BRIEFING — {datetime.now().strftime('%d %b %Y %H:%M')}
Gear Type        : {gear_type}
Failure Probability : {prob_pct:.1f}%
Risk Level       : {risk_label}
Prediction       : {"FAILURE DETECTED" if prediction == 1 else "NO FAILURE DETECTED"}

REMAINING USEFUL LIFE
Health Score     : {health_score * 100:.1f}% ({rul_label})
Est. RUL         : {rul_cycles:,.0f} cycles  (~{rul_hours:.1f} hrs at {speed} RPM)
RUL Range        : {rul_low:,.0f} – {rul_high:,.0f} cycles

CURRENT SENSOR READINGS
Speed            : {speed} RPM
Torque           : {torque} Nm
Vibration        : {vibration} mm/s
Temperature      : {temperature} °C
Shock Load       : {shock} g
Noise Level      : {noise} dB

SHAP ANALYSIS (top drivers)
Highest risk driver   : {_top_shap_feature['Feature']} = {_top_shap_feature['Value']} {_top_shap_feature['Unit']}  (SHAP {_top_shap_feature['Impact']:+.4f})
Greatest stabiliser   : {_top_shap_stable['Feature']} = {_top_shap_stable['Value']} {_top_shap_stable['Unit']}  (SHAP {_top_shap_stable['Impact']:+.4f})

LIME ANALYSIS (top local factor)
{_top_lime_feat[0]}  (score {_top_lime_feat[1]:+.4f})"""

_system_prompt = f"""You are an expert AI assistant embedded in an industrial spur gear predictive maintenance dashboard. You are highly knowledgeable in mechanical engineering, rotating machinery, tribology, vibration analysis, condition monitoring, lubrication, failure modes, ISO standards, and industrial maintenance best practices.

You have real-time gear health data from the live ML models:

{_briefing}

CORE BEHAVIOUR:
- You answer ALL questions — not just ones about this gear. If someone asks about gear theory, bearing failure modes, ISO standards, lubrication science, maintenance strategies, engineering calculations, or any other topic, answer it fully and expertly.
- When the question relates to the current gear data above, ground your answer in those specific numbers.
- When the question is general (e.g. "what causes gear pitting?", "how does vibration relate to bearing wear?", "explain SHAP values"), give a thorough, expert answer from your knowledge.
- Never refuse a question by saying it's "outside scope". If you genuinely don't know something, say so — but always try to help.
- Be conversational and practical. Engineers want clear, actionable answers.
- Use numbered steps, bullet points, or short paragraphs when it aids clarity.
- If asked for calculations (e.g. gear ratios, power, torque conversions, Hz from RPM), do the maths and show working.
- If asked about safety, maintenance schedules, failure analysis, root cause, or industry standards (ISO 10816, AGMA, etc.), answer with expertise.
- Adapt your depth to the question — a simple question gets a concise answer; a complex one gets a detailed breakdown.
- You may ask clarifying questions if a query is ambiguous.
- Never mention that you are a specific LLM model or reference any AI company."""

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def style_ax(ax, fig):
    ax.set_facecolor("#0D1018")
    fig.patch.set_facecolor("#111620")
    ax.tick_params(colors="#A8B8CC", labelsize=10)
    ax.grid(axis="x", color="#182030", linewidth=0.7, zorder=1)
    for sp in ax.spines.values():
        sp.set_color("#243048"); sp.set_linewidth(0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def bar_label(ax, bars, values, fmt="{:+.4f}"):
    x_max  = max(abs(v) for v in values) if values else 1
    offset = x_max * 0.018 or 0.0005
    for bar, val in zip(bars, values):
        ha = "left" if val >= 0 else "right"
        xp = val + (offset if val >= 0 else -offset)
        ax.text(xp, bar.get_y() + bar.get_height()/2,
                fmt.format(val), va="center", ha=ha,
                fontsize=9, color="#5A6A80", fontfamily="monospace")

# -------------------------------------------------------
# PDF REPORT
# -------------------------------------------------------
def _make_table(story, data, widths):
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0),  rl_colors.HexColor("#0B1628")),
        ("TEXTCOLOR",      (0,0),(-1,0),  rl_colors.white),
        ("FONTNAME",       (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0,0),(-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [rl_colors.HexColor("#f8fafc"), rl_colors.white]),
        ("GRID",           (0,0),(-1,-1), 0.5, rl_colors.HexColor("#e2e8f0")),
        ("PADDING",        (0,0),(-1,-1), 8),
        ("FONTNAME",       (0,1),(-1,-1), "Helvetica"),
    ]))
    story.append(t)

def build_pdf_report():
    buf  = io.BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=A4,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2*cm,  bottomMargin=2*cm)
    ss   = getSampleStyleSheet()
    t_s  = ParagraphStyle("t",  parent=ss["Heading1"], fontSize=18, spaceAfter=4,
                            textColor=rl_colors.HexColor("#0B1628"))
    sub  = ParagraphStyle("s",  parent=ss["Normal"],   fontSize=10, spaceAfter=16,
                            textColor=rl_colors.HexColor("#5A6A80"))
    body = ParagraphStyle("b",  parent=ss["Normal"],   fontSize=10, leading=15,
                            textColor=rl_colors.HexColor("#182030"))
    h2   = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13,
                            spaceBefore=16, spaceAfter=6,
                            textColor=rl_colors.HexColor("#0B1628"))
    story = []

    story.append(Paragraph("Spur Gear AI Failure Report", t_s))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y  %H:%M')}  |  Gear: {gear_type}", sub))
    story.append(Table([[""]], colWidths=[17*cm],
        style=TableStyle([("LINEBELOW",(0,0),(-1,-1),1,rl_colors.HexColor("#e2e8f0"))])))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Prediction Summary", h2))
    _make_table(story, [
        ["Parameter","Value"],
        ["Prediction",          "FAILURE DETECTED" if prediction==1 else "NO FAILURE DETECTED"],
        ["Failure Probability",  f"{prob_pct:.1f}%"],
        ["Risk Level",           risk_label],
        ["Gear Type",            gear_type],
        ["Health Score",         f"{health_score*100:.1f}%  ({rul_label})"],
        ["RUL (cycles)",         f"{rul_cycles:,.0f}  (range: {rul_low:,.0f} – {rul_high:,.0f})"],
        ["RUL (time)",           f"{rul_hours:.1f} hrs at {speed} RPM"],
    ], [6*cm, 11*cm])
    story.append(Spacer(1, 16))

    story.append(Paragraph("Operational Parameters", h2))
    rows = [["Parameter","Value","Unit"]]
    for lbl, val, unit in zip(feature_labels, param_values, param_units):
        rows.append([lbl, str(val), unit])
    _make_table(story, rows, [6*cm,6*cm,5*cm])
    story.append(Spacer(1, 16))

    # SHAP chart for PDF
    story.append(Paragraph("SHAP Feature Importance", h2))
    story.append(Paragraph(
        "SHAP values show how much each parameter pushed the failure probability above or below "
        "the model's average baseline prediction. Computed using 100-sample background from the training dataset.",
        body))
    story.append(Spacer(1, 8))
    fig_pdf, ax_pdf = plt.subplots(figsize=(7, 3.5))
    bc = ["#dc2626" if v > 0 else "#16a34a" for v in shap_df["Impact"]]
    ax_pdf.barh(shap_df["Feature"], shap_df["Impact"], color=bc, height=0.55, edgecolor="none")
    ax_pdf.axvline(0, color="#5A6A80", linewidth=0.8, linestyle="--")
    ax_pdf.set_facecolor("#F5F5F5"); fig_pdf.patch.set_facecolor("#FFFFFF")
    ax_pdf.tick_params(colors="#5A6A80", labelsize=9)
    ax_pdf.set_xlabel("SHAP Value (impact on failure probability)", fontsize=9, color="#5A6A80")
    for sp in ax_pdf.spines.values(): sp.set_color("#e2e8f0")
    ax_pdf.spines["top"].set_visible(False); ax_pdf.spines["right"].set_visible(False)
    plt.tight_layout()
    ibuf = io.BytesIO()
    fig_pdf.savefig(ibuf, format="png", dpi=150, bbox_inches="tight")
    ibuf.seek(0); plt.close(fig_pdf)
    story.append(RLImage(ibuf, width=15*cm, height=7*cm))
    story.append(Spacer(1, 16))

    story.append(Paragraph("LIME Local Explanation — Top Factors", h2))
    story.append(Paragraph(
        "LIME fits a local linear model around this operating point to explain the model's decision.", body))
    story.append(Spacer(1, 8))
    lime_rows = [["Condition","LIME Score (→ Failure)"]]
    for feat, val in lime_list[:6]:
        lime_rows.append([feat, f"{val:+.4f}"])
    _make_table(story, lime_rows, [11*cm, 6*cm])
    story.append(Spacer(1, 16))

    story.append(Paragraph("Maintenance Recommendation", h2))
    if prob_pct < 30:
        rec = "System operating within normal parameters. Continue standard monitoring."
    elif prob_pct < 60:
        rec = (f"Moderate risk detected ({prob_pct:.1f}%). Schedule inspection at next maintenance "
               "window. Check vibration levels and lubrication condition.")
    else:
        rec = (f"Critical failure probability ({prob_pct:.1f}%). Reduce operational load immediately "
               "and conduct emergency inspection of gear mesh, bearings, cooling, and lubrication.")
    story.append(Paragraph(rec, body))

    doc.build(story)
    buf.seek(0)
    return buf.read()




# =====================================================================
# 3D GEAR HTML GENERATOR  (v5 — Digital Twin Edition)
# =====================================================================
def create_gear_html(speed, torque, vibration, temperature, shock, noise_db,
                     health_score, prob_pct, risk_color, risk_label, gear_type):

    teeth_map  = {"Spur Gear A": 18, "Spur Gear B": 24, "Spur Gear C": 32}
    num_teeth  = teeth_map.get(gear_type, 24)

    cfg = (
        f"var SPD={speed},TRQ={torque},VIB={float(vibration):.2f},"
        f"TMP={temperature},SHK={float(shock):.2f},NSE={noise_db},"
        f"HLT={health_score:.4f},PRB={prob_pct:.1f},"
        f'RCL="{risk_color}",RLB="{risk_label}",'
        f"NTH={num_teeth};"
        f'var GTY="{gear_type}";'
    )

    HTML = r"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden;background:#06080E}
#cv{position:absolute;inset:0;width:100%;height:100%}
#vig{position:absolute;inset:0;pointer-events:none;z-index:3;
  background:radial-gradient(ellipse 75% 75% at 50% 50%,transparent 40%,rgba(0,0,0,.85) 100%)}
#scn{position:absolute;inset:0;pointer-events:none;z-index:3;opacity:.18;
  background:repeating-linear-gradient(0deg,rgba(0,0,0,.08) 0,rgba(0,0,0,.08) 1px,transparent 1px,transparent 3px)}

/* ── DIGITAL TWIN HEADER BAR ─────────────────────────────────────── */
#dt-header{position:absolute;top:0;left:0;right:0;z-index:15;pointer-events:none;
  background:linear-gradient(180deg,rgba(4,7,13,.95) 0%,rgba(4,7,13,0) 100%);
  padding:10px 16px 20px 16px;display:flex;align-items:center;justify-content:space-between}
.dt-brand{display:flex;align-items:center;gap:8px}
.dt-logo{width:28px;height:28px;border-radius:6px;
  background:linear-gradient(135deg,#005A8A,#00AEEF);
  display:flex;align-items:center;justify-content:center;font-size:14px;pointer-events:none}
.dt-title{font-size:12px;font-weight:700;color:#D6E4F0;letter-spacing:.04em}
.dt-sub{font-size:9px;color:#00AEEF;text-transform:uppercase;letter-spacing:.14em;margin-top:1px}
.dt-status{display:flex;align-items:center;gap:6px;font-size:10px;color:#5A6A80}
.dt-dot{width:6px;height:6px;border-radius:50%;animation:blink 1.4s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}

/* ── VIEW MODE BUTTONS ───────────────────────────────────────────── */
#view-btns{position:absolute;top:52px;right:14px;z-index:15;display:flex;flex-direction:column;gap:5px}
.vbtn{padding:5px 10px;border-radius:6px;font-size:9px;font-weight:700;letter-spacing:.08em;
  cursor:pointer;border:1px solid;text-transform:uppercase;transition:all .2s;
  background:rgba(8,12,22,.85);color:#5A6A80;border-color:#1E2D45;
  backdrop-filter:blur(10px);pointer-events:all}
.vbtn.active{background:rgba(0,174,239,.18);color:#00AEEF;border-color:#00AEEF}
.vbtn:hover{background:rgba(0,174,239,.12);color:#7DD4F8;border-color:#3A6A8A}

/* ── CAMERA PRESET BUTTONS ───────────────────────────────────────── */
#cam-btns{position:absolute;bottom:110px;right:14px;z-index:15;display:flex;flex-direction:column;gap:4px}
.cbtn{padding:4px 10px;border-radius:5px;font-size:8px;font-weight:700;letter-spacing:.08em;
  cursor:pointer;border:1px solid #1E2D45;text-transform:uppercase;
  background:rgba(8,12,22,.8);color:#4A6080;backdrop-filter:blur(10px);pointer-events:all;
  transition:all .2s}
.cbtn:hover{color:#D6E4F0;border-color:#2A3D55;background:rgba(20,30,50,.9)}

/* ── MINI OSCILLOSCOPE ───────────────────────────────────────────── */
#osc-panel{position:absolute;bottom:110px;left:14px;z-index:10;pointer-events:none}
.osc-wrap{background:rgba(4,8,16,.9);border:1px solid #0D2030;border-radius:8px;
  padding:8px 10px;backdrop-filter:blur(12px);
  box-shadow:0 0 0 .5px rgba(0,174,239,.08),0 4px 20px rgba(0,0,0,.7)}
.osc-hdr{font-size:8px;color:#00AEEF;text-transform:uppercase;letter-spacing:.12em;
  margin-bottom:5px;display:flex;justify-content:space-between;align-items:center}
#osc-canvas{display:block;border-radius:4px;background:#020508}

/* ── HUD LEFT ────────────────────────────────────────────────────── */
#hud-l{position:absolute;top:56px;left:14px;z-index:10;pointer-events:none;width:188px}
.hpanel{background:rgba(5,9,18,.88);border:1px solid #172538;border-radius:10px;
  padding:12px 13px;backdrop-filter:blur(16px);
  box-shadow:0 0 0 .5px rgba(0,174,239,.07),0 8px 32px rgba(0,0,0,.8),
             inset 0 1px 0 rgba(255,255,255,.03)}
.hdr{font-size:8px;color:#00AEEF;text-transform:uppercase;letter-spacing:.14em;
  font-weight:700;margin-bottom:9px;display:flex;align-items:center;gap:5px}
.hdr::before,.hdr::after{content:'';flex:1;height:1px;
  background:linear-gradient(90deg,transparent,#00AEEF44,transparent)}
.prow{margin-bottom:7px}
.plbl{font-size:8px;color:#374A60;text-transform:uppercase;letter-spacing:.08em;margin-bottom:2px;
  display:flex;justify-content:space-between;align-items:center}
.pval{font-size:10px;font-weight:700;color:#B8C8DC;font-family:'DM Mono',monospace}
.pbar{height:2px;background:#060D18;border-radius:2px;overflow:hidden;margin-top:2px}
.pfill{height:100%;border-radius:2px;transition:width .6s ease,background .6s ease}
.hsep{border-top:1px solid #101C2C;margin:8px 0}
.hrow{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.hval{font-size:13px;font-weight:800;font-family:'DM Mono',monospace}
.hbar{height:4px;background:#060D18;border-radius:3px;overflow:hidden;margin-bottom:6px}
.hfill{height:100%;border-radius:3px;transition:width .6s,background .6s}
.badge{text-align:center;padding:4px 8px;border-radius:5px;font-size:8px;
  font-weight:800;letter-spacing:.12em;text-transform:uppercase}

/* ── HUD RIGHT ───────────────────────────────────────────────────── */
#hud-r{position:absolute;top:56px;right:14px;z-index:10;pointer-events:none;width:138px}
.gname{font-size:13px;font-weight:700;color:#D6E4F0;margin-bottom:2px}
.gsub{font-size:9px;color:#4A6080;line-height:1.6}
.tip{font-size:8px;color:#1A2C3E;margin-top:7px;border-top:1px solid #101C2C;padding-top:6px;line-height:1.5}

/* ── BOTTOM STRIP ────────────────────────────────────────────────── */
#hud-b{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);z-index:10;pointer-events:none}
.strip{display:flex;gap:0;background:rgba(5,9,18,.9);border:1px solid #172538;
  border-radius:10px;overflow:hidden;backdrop-filter:blur(16px);
  box-shadow:0 0 0 .5px rgba(0,174,239,.07),0 8px 32px rgba(0,0,0,.8)}
.scell{padding:9px 18px;text-align:center;border-right:1px solid #101C2C}
.scell:last-child{border-right:none}
.slbl{font-size:7px;color:#374A60;text-transform:uppercase;letter-spacing:.12em;margin-bottom:2px}
.sval{font-size:13px;font-weight:700;font-family:'DM Mono',monospace;color:#D6E4F0;line-height:1}

/* ── ALERT POPUPS ────────────────────────────────────────────────── */
#popup-container{position:absolute;top:56px;left:50%;transform:translateX(-50%);
  z-index:20;display:flex;flex-direction:column;gap:5px;pointer-events:none;width:360px;
  align-items:center}
.popup{width:100%;padding:9px 14px;border-radius:7px;font-size:10px;font-weight:600;
  line-height:1.5;border-left:3px solid;animation:popIn .25s ease,popOut .35s ease 3.6s forwards;
  backdrop-filter:blur(14px);box-shadow:0 4px 20px rgba(0,0,0,.7)}
@keyframes popIn{from{opacity:0;transform:translateY(-10px) scale(.96)}to{opacity:1;transform:none}}
@keyframes popOut{from{opacity:1}to{opacity:0;transform:translateY(-6px)}}
.popup-info{background:rgba(0,25,50,.9);border-color:#00AEEF;color:#7DD4F8}
.popup-warn{background:rgba(35,20,4,.9);border-color:#F5A623;color:#F8C96A}
.popup-crit{background:rgba(40,6,10,.9);border-color:#E8394A;color:#F0707A}
.popup-ok{background:rgba(4,22,14,.9);border-color:#00C896;color:#5EEBC8}

/* ── FAULT INDICATOR ─────────────────────────────────────────────── */
#fault-ring{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  z-index:2;pointer-events:none;opacity:0;transition:opacity .5s}

/* corner brackets */
.cbr{position:absolute;pointer-events:none}
.ctlx{top:4px;left:4px;width:8px;height:8px;border-top:1.5px solid #00AEEF33;border-left:1.5px solid #00AEEF33}
.ctrx{top:4px;right:4px;width:8px;height:8px;border-top:1.5px solid #00AEEF33;border-right:1.5px solid #00AEEF33}
.cblx{bottom:4px;left:4px;width:8px;height:8px;border-bottom:1.5px solid #00AEEF33;border-left:1.5px solid #00AEEF33}
.cbrx{bottom:4px;right:4px;width:8px;height:8px;border-bottom:1.5px solid #00AEEF33;border-right:1.5px solid #00AEEF33}
.relp{position:relative}
</style>
</head><body>

<canvas id="cv"></canvas>
<div id="vig"></div><div id="scn"></div>

<!-- DIGITAL TWIN HEADER -->
<div id="dt-header">
  <div class="dt-brand">
    <div class="dt-logo">⚙</div>
    <div>
      <div class="dt-title">Digital Twin — Live Simulation</div>
      <div class="dt-sub">Spur Gear Condition Monitor</div>
    </div>
  </div>
  <div class="dt-status">
    <div class="dt-dot" id="status-dot" style="background:#00C896"></div>
    <span id="status-txt">SYNCED</span>
    <span style="margin-left:10px;color:#1E2D45">|</span>
    <span style="margin-left:10px" id="dt-time"></span>
  </div>
</div>

<!-- VIEW MODE BUTTONS -->
<div id="view-btns">
  <div class="vbtn active" id="vb-solid" onclick="setView('solid')">SOLID</div>
  <div class="vbtn" id="vb-wire" onclick="setView('wire')">WIRE</div>
  <div class="vbtn" id="vb-xray" onclick="setView('xray')">X-RAY</div>
</div>

<!-- CAMERA PRESETS -->
<div id="cam-btns">
  <div class="cbtn" onclick="setCamera('iso')">ISO</div>
  <div class="cbtn" onclick="setCamera('front')">FRONT</div>
  <div class="cbtn" onclick="setCamera('side')">SIDE</div>
  <div class="cbtn" onclick="setCamera('top')">TOP</div>
</div>

<!-- LEFT HUD -->
<div id="hud-l">
<div class="hpanel relp">
  <div class="cbr ctlx"></div><div class="cbr ctrx"></div>
  <div class="cbr cblx"></div><div class="cbr cbrx"></div>
  <div class="hdr">Live Parameters</div>

  <div class="prow"><div class="plbl"><span>Speed</span><span class="pval" id="v0"></span></div>
  <div class="pbar"><div class="pfill" id="b0"></div></div></div>

  <div class="prow"><div class="plbl"><span>Torque</span><span class="pval" id="v1"></span></div>
  <div class="pbar"><div class="pfill" id="b1"></div></div></div>

  <div class="prow"><div class="plbl"><span>Vibration</span><span class="pval" id="v2"></span></div>
  <div class="pbar"><div class="pfill" id="b2"></div></div></div>

  <div class="prow"><div class="plbl"><span>Temperature</span><span class="pval" id="v3"></span></div>
  <div class="pbar"><div class="pfill" id="b3"></div></div></div>

  <div class="prow"><div class="plbl"><span>Shock</span><span class="pval" id="v4"></span></div>
  <div class="pbar"><div class="pfill" id="b4"></div></div></div>

  <div class="prow"><div class="plbl"><span>Noise</span><span class="pval" id="v5"></span></div>
  <div class="pbar"><div class="pfill" id="b5"></div></div></div>

  <div class="hsep"></div>
  <div class="hrow"><span style="font-size:9px;color:#374A60">Health Score</span>
    <span class="hval" id="v-h"></span></div>
  <div class="hbar"><div class="hfill" id="b-h"></div></div>
  <div class="badge" id="v-risk"></div>
</div>
</div>

<!-- RIGHT HUD -->
<div id="hud-r">
<div class="hpanel relp">
  <div class="cbr ctlx"></div><div class="cbr ctrx"></div>
  <div class="cbr cblx"></div><div class="cbr cbrx"></div>
  <div class="hdr">Gear Spec</div>
  <div class="gname" id="r-gt"></div>
  <div class="gsub" id="r-sub"></div>
  <div class="tip">🖱 Drag · Scroll zoom<br>Click view/camera buttons →</div>
</div>
</div>

<!-- OSCILLOSCOPE -->
<div id="osc-panel">
<div class="osc-wrap">
  <div class="osc-hdr">
    <span>Vibration Waveform</span>
    <span id="osc-hz" style="color:#5A6A80"></span>
  </div>
  <canvas id="osc-canvas" width="188" height="44"></canvas>
</div>
</div>

<!-- BOTTOM STRIP -->
<div id="hud-b">
<div class="strip">
  <div class="scell"><div class="slbl">Failure Prob</div><div class="sval" id="s0"></div></div>
  <div class="scell"><div class="slbl">Mesh Rate</div><div class="sval" id="s1"></div></div>
  <div class="scell"><div class="slbl">Pitch Vel</div><div class="sval" id="s2"></div></div>
  <div class="scell"><div class="slbl">Face Width</div><div class="sval" id="s3"></div></div>
  <div class="scell"><div class="slbl">Twin Status</div><div class="sval" id="s4"></div></div>
</div>
</div>

<!-- POPUPS -->
<div id="popup-container"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
CFG_PLACEHOLDER

// ── Clock ─────────────────────────────────────────────────────────────
function tickClock(){
  const n=new Date();
  document.getElementById('dt-time').textContent=
    n.getHours().toString().padStart(2,'0')+':'+
    n.getMinutes().toString().padStart(2,'0')+':'+
    n.getSeconds().toString().padStart(2,'0')+' UTC';
}
tickClock(); setInterval(tickClock,1000);

// Status dot colour
const sdot=document.getElementById('status-dot');
const stxt=document.getElementById('status-txt');
if(PRB>=80){sdot.style.background='#E8394A';stxt.textContent='CRITICAL';}
else if(PRB>=55){sdot.style.background='#F5A623';stxt.textContent='WARNING';}
else if(PRB>=30){sdot.style.background='#F5A623';stxt.style.opacity='.7';stxt.textContent='ELEVATED';}
else{sdot.style.background='#00C896';stxt.textContent='NOMINAL';}

// ── DOM fill ──────────────────────────────────────────────────────────
const RISK_STYLES={
  'LOW RISK':     {bg:'rgba(4,18,12,.9)',c:'#00C896',b:'#0F3828'},
  'MODERATE RISK':{bg:'rgba(35,20,4,.9)',c:'#F5A623',b:'#2E2108'},
  'HIGH RISK':    {bg:'rgba(40,6,10,.9)',c:'#E8394A',b:'#4A1820'},
  'CRITICAL RISK':{bg:'rgba(40,6,10,.9)',c:'#E8394A',b:'#4A1820'},
};
function bc(n){return n<0.4?'#00C896':n<0.72?'#F5A623':'#E8394A';}
function setBar(id,n){
  const el=document.getElementById(id); if(!el)return;
  el.style.width=Math.min(100,n*100).toFixed(1)+'%';
  el.style.background=bc(n);
}
const PARAMS=[
  [SPD,'RPM',(SPD-500)/2500],
  [TRQ,'Nm',(TRQ-50)/350],
  [VIB.toFixed(1),'mm/s',(VIB-0.5)/9.5],
  [TMP,'°C',(TMP-30)/90],
  [SHK.toFixed(1),'g',(SHK-0.1)/5.9],
  [NSE,'dB',(NSE-50)/50],
];
PARAMS.forEach(([v,u,n],i)=>{
  document.getElementById('v'+i).textContent=v+' '+u;
  setBar('b'+i,n);
});
document.getElementById('v-h').textContent=(HLT*100).toFixed(1)+'%';
document.getElementById('v-h').style.color=bc(1-HLT);
setBar('b-h',HLT);
document.getElementById('b-h').style.background=bc(1-HLT);
const rs=RISK_STYLES[RLB]||RISK_STYLES['LOW RISK'];
const rb=document.getElementById('v-risk');
rb.textContent=RLB;
Object.assign(rb.style,{background:rs.bg,color:rs.c,border:'1px solid '+rs.b});
document.getElementById('r-gt').textContent=GTY;
document.getElementById('r-sub').innerHTML=NTH+' teeth &middot; Module 0.22<br>Pitch dia '+(0.22*NTH).toFixed(1)+' mm<br>Pressure ang 20°';
document.getElementById('s0').textContent=PRB.toFixed(1)+'%';
document.getElementById('s0').style.color=rs.c;
document.getElementById('s1').textContent=(SPD*NTH/60).toFixed(0)+'/s';
const pitchVel=(Math.PI*0.22*NTH*SPD/60/1000).toFixed(2);
document.getElementById('s2').textContent=pitchVel+' m/s';
const faceWidth=(0.25+(TRQ-50)/350*0.55).toFixed(2);
document.getElementById('s3').textContent=faceWidth+' m';
document.getElementById('s4').textContent=HLT>0.7?'NOMINAL':HLT>0.4?'DEGRADED':'CRITICAL';
document.getElementById('s4').style.color=bc(1-HLT);

document.getElementById('osc-hz').textContent=(VIB*8.5+12).toFixed(0)+' Hz';

// ── OSCILLOSCOPE ──────────────────────────────────────────────────────
const oscCanvas=document.getElementById('osc-canvas');
const oscCtx=oscCanvas.getContext('2d');
const OSC_W=188, OSC_H=44;
const oscHistory=new Float32Array(OSC_W).fill(OSC_H/2);
let oscT=0;
const vibFreq=0.04+VIB*0.018;
const vibAmpPx=(VIB/10)*14;
const noiseAmp=(NSE-50)/100*5;

function drawOsc(){
  // Shift left
  oscHistory.copyWithin(0,1);
  const val=OSC_H/2 - Math.sin(oscT*vibFreq*6.28)*vibAmpPx
    - Math.sin(oscT*vibFreq*12.56+0.8)*(vibAmpPx*0.4)
    + (Math.random()-0.5)*noiseAmp*2;
  oscHistory[OSC_W-1]=val;
  oscT++;

  oscCtx.clearRect(0,0,OSC_W,OSC_H);
  // Grid
  oscCtx.strokeStyle='rgba(0,60,30,.4)';oscCtx.lineWidth=.5;
  for(let x=0;x<OSC_W;x+=OSC_W/6){oscCtx.beginPath();oscCtx.moveTo(x,0);oscCtx.lineTo(x,OSC_H);oscCtx.stroke();}
  for(let y=0;y<OSC_H;y+=OSC_H/3){oscCtx.beginPath();oscCtx.moveTo(0,y);oscCtx.lineTo(OSC_W,y);oscCtx.stroke();}
  // Midline
  oscCtx.strokeStyle='rgba(0,174,239,.18)';oscCtx.lineWidth=.5;
  oscCtx.beginPath();oscCtx.moveTo(0,OSC_H/2);oscCtx.lineTo(OSC_W,OSC_H/2);oscCtx.stroke();

  // Waveform
  const col=VIB>7?'#E8394A':VIB>4?'#F5A623':'#00C896';
  oscCtx.beginPath();
  oscCtx.strokeStyle=col;oscCtx.lineWidth=1.5;
  for(let x=0;x<OSC_W;x++){
    if(x===0)oscCtx.moveTo(x,oscHistory[x]);
    else oscCtx.lineTo(x,oscHistory[x]);
  }
  oscCtx.stroke();
  // Glow
  oscCtx.strokeStyle=col.replace(')',',0.25)').replace('#','rgba(').replace(/rgba\(([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i,(m,r,g,b)=>`rgba(${parseInt(r,16)},${parseInt(g,16)},${parseInt(b,16)}`);
  oscCtx.lineWidth=4;
  oscCtx.beginPath();
  for(let x=0;x<OSC_W;x++){
    if(x===0)oscCtx.moveTo(x,oscHistory[x]);
    else oscCtx.lineTo(x,oscHistory[x]);
  }
  oscCtx.stroke();
}

// ── POPUP SYSTEM ──────────────────────────────────────────────────────
const popContainer=document.getElementById('popup-container');
function showPopup(msg,type='info'){
  const d=document.createElement('div');
  d.className='popup popup-'+type;
  d.innerHTML=msg;
  popContainer.prepend(d);
  setTimeout(()=>{if(d.parentNode)d.parentNode.removeChild(d);},4200);
}
setTimeout(()=>{
  if(PRB>=80){
    showPopup('🔴 <b>CRITICAL FAILURE RISK</b> — '+PRB.toFixed(1)+'%. Immediate action required!','crit');
    setTimeout(()=>showPopup('🔴 Health at '+(HLT*100).toFixed(0)+'% — End of life imminent.','crit'),700);
  } else if(PRB>=55){
    showPopup('🔶 HIGH RISK — Failure probability '+PRB.toFixed(1)+'%. Inspect within 24–48h.','warn');
  } else if(PRB>=30){
    showPopup('⚠ MODERATE RISK — Probability '+PRB.toFixed(1)+'%. Monitor closely.','warn');
  } else {
    showPopup('✅ System nominal — Probability '+PRB.toFixed(1)+'%. All parameters healthy.','ok');
  }
  if(TMP>97) setTimeout(()=>showPopup('🌡 Temperature CRITICAL: '+TMP+'°C — Over threshold!','crit'),1000);
  else if(TMP>80) setTimeout(()=>showPopup('🌡 Temperature elevated: '+TMP+'°C','warn'),1000);
  if(SPD>2375) setTimeout(()=>showPopup('⚡ Speed '+SPD+' RPM — Above 2375 RPM danger zone.','warn'),1400);
  if(VIB>7.6) setTimeout(()=>showPopup('〰 Vibration CRITICAL: '+VIB.toFixed(1)+' mm/s','crit'),1700);
  if(SHK>4.4) setTimeout(()=>showPopup('💥 Shock Load '+SHK.toFixed(1)+'g — High impact.','warn'),2000);
},500);

// ── VIEW MODE ─────────────────────────────────────────────────────────
let viewMode='solid';
function setView(m){
  viewMode=m;
  ['solid','wire','xray'].forEach(v=>{
    document.getElementById('vb-'+v).classList.toggle('active',v===m);
  });
  applyViewMode();
}
function applyViewMode(){
  if(!mesh1)return;
  if(viewMode==='solid'){
    [mesh1,mesh2].forEach(m=>{m.material.wireframe=false;m.material.transparent=false;m.material.opacity=1;});
  } else if(viewMode==='wire'){
    [mesh1,mesh2].forEach(m=>{m.material.wireframe=true;m.material.transparent=false;m.material.opacity=1;});
  } else {
    [mesh1,mesh2].forEach(m=>{m.material.wireframe=false;m.material.transparent=true;m.material.opacity=0.32;});
  }
}

// ── CAMERA PRESETS ────────────────────────────────────────────────────
const CAM_PRESETS={
  iso:  {theta:0.65,phi:1.05,r:5.5},
  front:{theta:Math.PI/2,phi:Math.PI/2,r:4.5},
  side: {theta:0,phi:Math.PI/2,r:5.0},
  top:  {theta:0.65,phi:0.18,r:5.5},
};
let camTarget={theta:0.65,phi:1.05,r:5.0};
let camCurrent={theta:0.65,phi:1.05,r:5.0};
function setCamera(preset){
  const p=CAM_PRESETS[preset];
  camTarget.theta=p.theta; camTarget.phi=p.phi; camTarget.r=p.r;
}

// ── THREE.JS SETUP ────────────────────────────────────────────────────
const canvas=document.getElementById('cv');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.VSMShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.05;
renderer.outputEncoding=THREE.sRGBEncoding;

const scene=new THREE.Scene();
scene.background=new THREE.Color(0x06080E);
scene.fog=new THREE.Fog(0x06080E,14,40);

// ─── IMAGE BASED LIGHTING (IBL) ─────────────────────────────────────────
// Procedural industrial HDR environment for PBR reflections on all metals
(function(){
  const pmrem=new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();
  const ec=document.createElement('canvas'); ec.width=2048; ec.height=1024;
  const ex=ec.getContext('2d');
  // Dark industrial ceiling base
  ex.fillStyle='#050710'; ex.fillRect(0,0,2048,1024);
  const cg=ex.createLinearGradient(0,0,0,380); cg.addColorStop(0,'#04060D'); cg.addColorStop(1,'#0B1525');
  ex.fillStyle=cg; ex.fillRect(0,0,2048,380);
  // Floor bounce (warm concrete reflection)
  const fg=ex.createLinearGradient(0,660,0,1024); fg.addColorStop(0,'#091220'); fg.addColorStop(1,'#030407');
  ex.fillStyle=fg; ex.fillRect(0,660,2048,364);
  // Mid-wall ambient brightness band
  const mg=ex.createLinearGradient(0,380,0,660);
  mg.addColorStop(0,'rgba(18,30,50,0)'); mg.addColorStop(0.5,'rgba(24,38,62,0.28)'); mg.addColorStop(1,'rgba(18,30,50,0)');
  ex.fillStyle=mg; ex.fillRect(0,380,2048,280);
  // Overhead sodium lamp hotspots (warm orange-white glow)
  [[341,72],[683,72],[1024,72],[1365,72],[1707,72],[204,60],[1844,60]].forEach(([lx,ly])=>{
    const lg=ex.createRadialGradient(lx,ly,0,lx,ly,305);
    lg.addColorStop(0,'rgba(255,230,148,0.98)'); lg.addColorStop(0.12,'rgba(255,198,88,0.72)');
    lg.addColorStop(0.35,'rgba(255,158,52,0.28)'); lg.addColorStop(1,'rgba(255,128,32,0)');
    ex.fillStyle=lg; ex.beginPath(); ex.ellipse(lx,ly,305,240,0,0,Math.PI*2); ex.fill();
  });
  // Factory window cold daylight (left — cool blue-grey)
  [[0,320],[0,540],[10,435]].forEach(([wx,wy])=>{
    const wg=ex.createRadialGradient(wx,wy,0,wx,wy,420);
    wg.addColorStop(0,'rgba(138,172,232,0.72)'); wg.addColorStop(0.25,'rgba(108,148,208,0.44)');
    wg.addColorStop(1,'rgba(68,108,172,0)');
    ex.fillStyle=wg; ex.fillRect(0,wy-420,640,840);
  });
  // Cyan HMI/SCADA control panel glow (right)
  const cng=ex.createRadialGradient(1900,512,0,1900,512,325);
  cng.addColorStop(0,'rgba(0,174,239,0.44)'); cng.addColorStop(1,'rgba(0,98,182,0)');
  ex.fillStyle=cng; ex.beginPath(); ex.ellipse(1900,512,325,325,0,0,Math.PI*2); ex.fill();
  // Risk-coloured accent (health indicator hue)
  const rHex=parseInt(RCL.replace('#',''),16);
  const rR=(rHex>>16)&255, rG=(rHex>>8)&255, rB=rHex&255;
  const rg=ex.createRadialGradient(1024,580,0,1024,580,385);
  rg.addColorStop(0,'rgba('+rR+','+rG+','+rB+',0.36)'); rg.addColorStop(1,'rgba('+rR+','+rG+','+rB+',0)');
  ex.fillStyle=rg; ex.beginPath(); ex.ellipse(1024,580,385,385,0,0,Math.PI*2); ex.fill();
  // Cool steel floor reflection (bottom-right)
  const brg=ex.createRadialGradient(1200,900,0,1200,900,255);
  brg.addColorStop(0,'rgba(38,58,92,0.32)'); brg.addColorStop(1,'rgba(18,32,58,0)');
  ex.fillStyle=brg; ex.fillRect(945,745,510,279);
  // Apply as scene environment (drives all PBR material reflections)
  const envTex=new THREE.CanvasTexture(ec);
  envTex.mapping=THREE.EquirectangularReflectionMapping;
  const envMap=pmrem.fromEquirectangular(envTex).texture;
  scene.environment=envMap;
  pmrem.dispose(); envTex.dispose();
})();


const W=()=>canvas.clientWidth, H=()=>canvas.clientHeight;
const camera=new THREE.PerspectiveCamera(40,W()/H(),0.01,100);
function onResize(){renderer.setSize(W(),H(),false);camera.aspect=W()/H();camera.updateProjectionMatrix();}
new ResizeObserver(onResize).observe(canvas); onResize();

// ══════════════════════════════════════════════════════════════════════
// FACTORY ENVIRONMENT — full immersive factory interior
// ══════════════════════════════════════════════════════════════════════
function makeCanvasTex(w,h,drawFn){
  const c=document.createElement('canvas'); c.width=w; c.height=h;
  drawFn(c.getContext('2d'),w,h);
  return new THREE.CanvasTexture(c);
}

// ── Corrugated metal wall texture ─────────────────────────────────────
const corrWallTex=makeCanvasTex(512,512,(ctx,w,h)=>{
  ctx.fillStyle='#0A0E16'; ctx.fillRect(0,0,w,h);
  // Vertical corrugation ridges
  for(let x=0;x<w;x+=18){
    const lg=ctx.createLinearGradient(x,0,x+18,0);
    lg.addColorStop(0,'rgba(30,42,60,0)');
    lg.addColorStop(0.35,'rgba(28,40,58,0.85)');
    lg.addColorStop(0.5,'rgba(38,55,80,1)');
    lg.addColorStop(0.65,'rgba(22,32,48,0.85)');
    lg.addColorStop(1,'rgba(14,20,32,0)');
    ctx.fillStyle=lg; ctx.fillRect(x,0,18,h);
  }
  // Horizontal weld seams
  for(let y=0;y<h;y+=h/5){
    ctx.strokeStyle='rgba(8,12,22,0.9)'; ctx.lineWidth=3;
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke();
    ctx.strokeStyle='rgba(50,70,100,0.3)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(0,y+2); ctx.lineTo(w,y+2); ctx.stroke();
  }
  // Bolts at seams
  for(let y=0;y<h;y+=h/5){
    for(let x=12;x<w;x+=36){
      ctx.beginPath(); ctx.arc(x,y,3,0,Math.PI*2);
      const rg=ctx.createRadialGradient(x-1,y-1,0,x,y,3.5);
      rg.addColorStop(0,'#2A3C54'); rg.addColorStop(1,'#060A12');
      ctx.fillStyle=rg; ctx.fill();
      ctx.strokeStyle='#1A2838'; ctx.lineWidth=0.6; ctx.stroke();
    }
  }
  // Grime streaks
  for(let i=0;i<40;i++){
    const x=Math.random()*w;
    ctx.strokeStyle=`rgba(0,0,0,${0.2+Math.random()*0.4})`; ctx.lineWidth=1+Math.random()*2;
    ctx.beginPath(); ctx.moveTo(x,Math.random()*h*0.5); ctx.lineTo(x+Math.random()*10-5,h); ctx.stroke();
  }
  // Rust patches
  for(let i=0;i<12;i++){
    const x=Math.random()*w,y=Math.random()*h;
    const rg=ctx.createRadialGradient(x,y,0,x,y,8+Math.random()*15);
    rg.addColorStop(0,'rgba(80,35,10,0.35)'); rg.addColorStop(1,'rgba(80,35,10,0)');
    ctx.fillStyle=rg; ctx.beginPath(); ctx.ellipse(x,y,15,8,Math.random()*Math.PI,0,Math.PI*2); ctx.fill();
  }
});
corrWallTex.wrapS=corrWallTex.wrapT=THREE.RepeatWrapping; corrWallTex.repeat.set(6,3);

// ── Concrete floor texture ─────────────────────────────────────────────
const concreteTex=makeCanvasTex(1024,1024,(ctx,w,h)=>{
  ctx.fillStyle='#0D1118'; ctx.fillRect(0,0,w,h);
  // Aggregate variation
  for(let i=0;i<2000;i++){
    const x=Math.random()*w, y=Math.random()*h;
    const sz=1+Math.random()*12;
    const v=8+Math.floor(Math.random()*18);
    ctx.fillStyle=`rgb(${v},${v+1},${v+2})`;
    ctx.beginPath(); ctx.ellipse(x,y,sz,sz*(0.4+Math.random()*0.6),Math.random()*Math.PI,0,Math.PI*2);
    ctx.fill();
  }
  // Large concrete slab joints
  ctx.strokeStyle='#060A0F'; ctx.lineWidth=5;
  [h*0.33,h*0.66].forEach(y=>{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();});
  [w*0.5].forEach(x=>{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();});
  // Yellow lane marking stripe
  ctx.strokeStyle='rgba(255,200,0,0.22)'; ctx.lineWidth=18; ctx.setLineDash([60,40]);
  ctx.beginPath(); ctx.moveTo(0,h*0.5); ctx.lineTo(w,h*0.5); ctx.stroke(); ctx.setLineDash([]);
  // Yellow hazard border
  ctx.strokeStyle='rgba(255,190,0,0.14)'; ctx.lineWidth=28;
  ctx.strokeRect(50,50,w-100,h-100);
  // Oil/grease stains
  for(let i=0;i<18;i++){
    const x=Math.random()*w, y=Math.random()*h;
    const grd=ctx.createRadialGradient(x,y,0,x,y,20+Math.random()*50);
    grd.addColorStop(0,'rgba(0,4,10,0.7)'); grd.addColorStop(1,'rgba(0,4,10,0)');
    ctx.fillStyle=grd; ctx.beginPath(); ctx.ellipse(x,y,50,25,Math.random()*Math.PI,0,Math.PI*2); ctx.fill();
  }
  // Scuff marks
  for(let i=0;i<60;i++){
    const x=Math.random()*w, y=Math.random()*h;
    ctx.strokeStyle=`rgba(0,0,0,${0.15+Math.random()*0.35})`; ctx.lineWidth=Math.random()*3;
    ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+Math.random()*40-20,y+Math.random()*20-10); ctx.stroke();
  }
});
concreteTex.wrapS=concreteTex.wrapT=THREE.RepeatWrapping; concreteTex.repeat.set(6,4);

// ── Metal grating texture (catwalk) ───────────────────────────────────
const gratingTex=makeCanvasTex(256,256,(ctx,w,h)=>{
  ctx.fillStyle='#060A10'; ctx.fillRect(0,0,w,h);
  ctx.strokeStyle='rgba(30,50,80,0.9)'; ctx.lineWidth=3;
  for(let x=0;x<w;x+=16){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();}
  for(let y=0;y<h;y+=16){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
  ctx.strokeStyle='rgba(18,30,50,0.6)'; ctx.lineWidth=1;
  for(let x=0;x<w;x+=16){for(let y=0;y<h;y+=16){
    ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+16,y+16);ctx.stroke();
  }}
});
gratingTex.wrapS=gratingTex.wrapT=THREE.RepeatWrapping; gratingTex.repeat.set(8,4);

// ── Window glass texture ───────────────────────────────────────────────
const windowTex=makeCanvasTex(256,256,(ctx,w,h)=>{
  // Murky factory daylight
  const sky=ctx.createLinearGradient(0,0,0,h);
  sky.addColorStop(0,'rgba(80,100,140,0.5)');
  sky.addColorStop(0.5,'rgba(100,120,160,0.35)');
  sky.addColorStop(1,'rgba(50,60,80,0.2)');
  ctx.fillStyle=sky; ctx.fillRect(0,0,w,h);
  // Smudges/grime on glass
  for(let i=0;i<30;i++){
    const x=Math.random()*w, y=Math.random()*h;
    ctx.fillStyle=`rgba(0,0,0,${0.05+Math.random()*0.15})`;
    ctx.beginPath(); ctx.ellipse(x,y,5+Math.random()*20,3+Math.random()*10,Math.random()*Math.PI,0,Math.PI*2); ctx.fill();
  }
  // Frame dividers
  ctx.fillStyle='rgba(8,12,20,0.95)'; ctx.fillRect(w/2-2,0,4,h); ctx.fillRect(0,h/2-2,w,4);
});

// ── Ceiling panel texture ──────────────────────────────────────────────
const ceilTex=makeCanvasTex(512,512,(ctx,w,h)=>{
  ctx.fillStyle='#090D14'; ctx.fillRect(0,0,w,h);
  // Acoustic/insulation tiles
  for(let tx=0;tx<w;tx+=w/4){for(let ty=0;ty<h;ty+=h/4){
    ctx.strokeStyle='rgba(5,8,14,1)'; ctx.lineWidth=3;
    ctx.strokeRect(tx+1,ty+1,w/4-2,h/4-2);
    for(let i=0;i<30;i++){
      const px=tx+Math.random()*w/4, py=ty+Math.random()*h/4;
      ctx.fillStyle=`rgba(20,28,40,${0.3+Math.random()*0.4})`;
      ctx.fillRect(px,py,1,1);
    }
  }}
  // Duct shadow strips
  ctx.fillStyle='rgba(0,0,0,0.4)'; ctx.fillRect(0,0,w,18); ctx.fillRect(0,h-18,w,18);
});
ceilTex.wrapS=ceilTex.wrapT=THREE.RepeatWrapping; ceilTex.repeat.set(4,4);

// ── FACTORY LIGHTING RIG ──────────────────────────────────────────────
// Very low ambient — dim factory floor
scene.add(new THREE.AmbientLight(0x0D1420,1.15));
// Main overhead key from high sodium lamp angle — warm orange-white
const keyL=new THREE.DirectionalLight(0xFFE090,2.1);
keyL.position.set(2,14,3); keyL.castShadow=true;
keyL.shadow.mapSize.set(4096,4096);
keyL.shadow.camera.near=0.5; keyL.shadow.camera.far=40;
keyL.shadow.camera.left=-14; keyL.shadow.camera.right=14;
keyL.shadow.camera.top=14; keyL.shadow.camera.bottom=-14;
keyL.shadow.bias=-0.0006; scene.add(keyL);
// Cold blue-grey fill from factory windows (overcast sky)
const winL=new THREE.DirectionalLight(0x7090C0,0.55);
winL.position.set(-10,4,6); scene.add(winL);
// Bounce off concrete floor
const bounceL=new THREE.DirectionalLight(0x1A2030,0.35);
bounceL.position.set(0,-8,2); scene.add(bounceL);

const riskHex=parseInt(RCL.replace('#',''),16);
const ptRisk=new THREE.PointLight(riskHex,2.8,9);
ptRisk.position.set(0,0.3,2.8); scene.add(ptRisk);
const tempN=Math.max(0,(TMP-30)/90);
const tempCol=new THREE.Color().setHSL(0.07*(1-tempN),0.9,0.55);
const ptTemp=new THREE.PointLight(tempCol,tempN*2.8,8);
ptTemp.position.set(0,2,2); scene.add(ptTemp);
const ptCyan=new THREE.PointLight(0x00AEEF,0.9,12);
ptCyan.position.set(0,3.5,-3); scene.add(ptCyan);
// Rim/kicker: cold blue edge-highlight on gear teeth (backlight)
const ptRim=new THREE.DirectionalLight(0xA8C8F0,0.80);
ptRim.position.set(-3.5,1.5,4.5); scene.add(ptRim);
// Under-fill: warm concrete bounce off floor
const ptFloor=new THREE.PointLight(0xFFD080,0.32,10);
ptFloor.position.set(0,-3.2,1.0); scene.add(ptFloor);

// ── MATERIALS ─────────────────────────────────────────────────────────
// ─── SURFACE NORMAL + ROUGHNESS MAPS ────────────────────────────────────
// Simulate CNC face-grinding rings, bore chamfer, micro-scratches, wear
function makeGearNormalMap(){
  const c=document.createElement('canvas'); c.width=512; c.height=512;
  const ctx=c.getContext('2d'); const cx=256,cy=256;
  // Flat base normal (127,127,255) = no surface deflection
  ctx.fillStyle='#8080ff'; ctx.fillRect(0,0,512,512);
  // Concentric CNC face-grinding rings (alternating groove/ridge)
  for(let r=14;r<252;r+=2.4){
    const isGroove=(Math.floor(r/2.4)%2===0);
    ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.strokeStyle=isGroove?'rgba(68,68,232,0.58)':'rgba(150,150,255,0.46)';
    ctx.lineWidth=isGroove?1.6:1.0; ctx.stroke();
  }
  // Radial micro-scratches from tooling passes
  for(let i=0;i<40;i++){
    const a=Math.random()*Math.PI*2, r1=18+Math.random()*90, r2=r1+12+Math.random()*80;
    ctx.beginPath(); ctx.moveTo(cx+Math.cos(a)*r1,cy+Math.sin(a)*r1);
    ctx.lineTo(cx+Math.cos(a)*r2,cy+Math.sin(a)*r2);
    ctx.strokeStyle='rgba(78,78,212,0.28)'; ctx.lineWidth=0.7; ctx.stroke();
  }
  // Hub bore chamfer ring (precision machined edge highlight)
  ctx.beginPath(); ctx.arc(cx,cy,36,0,Math.PI*2);
  ctx.strokeStyle='rgba(52,52,202,0.68)'; ctx.lineWidth=4; ctx.stroke();
  ctx.beginPath(); ctx.arc(cx,cy,41,0,Math.PI*2);
  ctx.strokeStyle='rgba(172,172,255,0.42)'; ctx.lineWidth=2; ctx.stroke();
  // Micro-pitting/forge-grain noise for cast texture variance
  for(let i=0;i<9000;i++){
    const x=Math.random()*512, y=Math.random()*512;
    const v=Math.floor(94+Math.random()*62);
    const vb=Math.min(255,v+65);
    ctx.fillStyle='rgba('+v+','+v+','+vb+',0.07)'; ctx.fillRect(x,y,1,1);
  }
  const t=new THREE.CanvasTexture(c);
  t.wrapS=t.wrapT=THREE.RepeatWrapping;
  t.anisotropy=renderer.capabilities.getMaxAnisotropy();
  return t;
}
function makeGearRoughnessMap(){
  const c=document.createElement('canvas'); c.width=512; c.height=512;
  const ctx=c.getContext('2d'); const cx=256,cy=256;
  ctx.fillStyle='#181818'; ctx.fillRect(0,0,512,512); // base: polished
  // Tooth tips (outer ring) rougher from rolling contact fatigue
  const tg=ctx.createRadialGradient(cx,cy,188,cx,cy,256);
  tg.addColorStop(0,'rgba(12,12,12,0)'); tg.addColorStop(1,'rgba(50,50,50,0.75)');
  ctx.fillStyle=tg; ctx.fillRect(0,0,512,512);
  // Hub bore: precision-ground smooth
  const hg=ctx.createRadialGradient(cx,cy,0,cx,cy,42);
  hg.addColorStop(0,'rgba(4,4,4,0.95)'); hg.addColorStop(1,'rgba(22,22,22,0)');
  ctx.fillStyle=hg; ctx.fillRect(0,0,512,512);
  // Spoke hole rims: slightly rougher cast surfaces
  const nSp=NTH>=24?6:4;
  for(let i=0;i<nSp;i++){
    const a=i*(Math.PI*2/nSp), hr=145;
    const sg=ctx.createRadialGradient(cx+Math.cos(a)*hr,cy+Math.sin(a)*hr,0,cx+Math.cos(a)*hr,cy+Math.sin(a)*hr,30);
    sg.addColorStop(0,'rgba(55,55,55,0.52)'); sg.addColorStop(1,'rgba(28,28,28,0)');
    ctx.fillStyle=sg; ctx.fillRect(cx+Math.cos(a)*hr-32,cy+Math.sin(a)*hr-32,64,64);
  }
  // Micro-pitting noise (wear particles)
  for(let i=0;i<18000;i++){
    const r=22+Math.random()*220, a2=Math.random()*Math.PI*2;
    const x=cx+Math.cos(a2)*r, y=cy+Math.sin(a2)*r, v=Math.floor(Math.random()*34);
    ctx.fillStyle='rgba('+v+','+v+','+v+',0.07)'; ctx.fillRect(x,y,1.5,1.5);
  }
  const t=new THREE.CanvasTexture(c);
  t.wrapS=t.wrapT=THREE.RepeatWrapping;
  t.anisotropy=renderer.capabilities.getMaxAnisotropy();
  return t;
}
const gearNormalMap=makeGearNormalMap();
const gearRoughnessMap=makeGearRoughnessMap();

const healthDmg=Math.max(0,1-HLT);
const gearColor=new THREE.Color().setHSL(0.57-tempN*0.57,0.10+tempN*0.28,0.62+tempN*0.05);
const mat1=new THREE.MeshPhysicalMaterial({
  color:gearColor,metalness:0.95,roughness:0.06,
  clearcoat:0.90,clearcoatRoughness:0.06,reflectivity:1.0,envMapIntensity:1.55,
  normalMap:gearNormalMap,normalScale:new THREE.Vector2(0.28,0.28),
  roughnessMap:gearRoughnessMap,
  emissive:new THREE.Color(0xE8394A),emissiveIntensity:healthDmg*0.65,
});
const mat2=new THREE.MeshPhysicalMaterial({
  color:new THREE.Color(0.70,0.73,0.82),metalness:0.92,roughness:0.10,
  clearcoat:0.75,clearcoatRoughness:0.08,reflectivity:0.92,envMapIntensity:1.35,
  normalMap:gearNormalMap,normalScale:new THREE.Vector2(0.22,0.22),
  roughnessMap:gearRoughnessMap,
  emissive:new THREE.Color(0x00AEEF),emissiveIntensity:0.045,
});
const shaftMat=new THREE.MeshPhysicalMaterial({color:new THREE.Color(0.22,0.25,0.32),metalness:0.97,roughness:0.07,clearcoat:0.65,clearcoatRoughness:0.09,envMapIntensity:1.2});
const floorMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.04,0.06,0.09),metalness:0.25,roughness:0.88});
const hubMat=new THREE.MeshPhysicalMaterial({color:new THREE.Color(0.12,0.17,0.27),metalness:0.88,roughness:0.16,clearcoat:0.55,clearcoatRoughness:0.12,envMapIntensity:1.1});

// ── GEAR SHAPE ────────────────────────────────────────────────────────
function spurGearShape(N,m){
  const Rp=m*N/2,Ra=Rp+m,Rd=Rp-1.25*m;
  const shape=new THREE.Shape();
  const pitchAngle=Math.PI*2/N;
  for(let i=0;i<N;i++){
    const base=i*pitchAngle;
    const halfTooth=pitchAngle*0.2;
    const rootS=base-pitchAngle/2+halfTooth*0.6;
    const rootE=base-halfTooth;
    if(i===0)shape.moveTo(Rd*Math.cos(rootS),Rd*Math.sin(rootS));
    shape.absarc(0,0,Rd,rootS,rootE,false);
    const pts=8;
    for(let p=0;p<=pts;p++){
      const t2=p/pts,r=Rd+(Ra-Rd)*t2,a=rootE+t2*(halfTooth*2);
      shape.lineTo(r*Math.cos(a),r*Math.sin(a));
    }
    shape.absarc(0,0,Ra,base-halfTooth*0.18,base+halfTooth*0.18,false);
    for(let p=pts;p>=0;p--){
      const t2=p/pts,r=Rd+(Ra-Rd)*t2,a=base+halfTooth*0.18+(halfTooth*2)*(1-t2)*0.82;
      shape.lineTo(r*Math.cos(a),r*Math.sin(a));
    }
    shape.absarc(0,0,Rd,base+halfTooth,base+pitchAngle/2-halfTooth*0.6,false);
  }
  shape.closePath();
  const bore=new THREE.Path();
  bore.absarc(0,0,Math.max(0.06,Rd*0.28),0,Math.PI*2,true);
  shape.holes.push(bore);
  const nSpokes=N>=24?6:4;
  const spokeR=Rd*0.60,spokeHoleR=Rd*0.13;
  for(let i=0;i<nSpokes;i++){
    const a=i*(Math.PI*2/nSpokes),h=new THREE.Path();
    h.absarc(spokeR*Math.cos(a),spokeR*Math.sin(a),spokeHoleR,0,Math.PI*2,true);
    shape.holes.push(h);
  }
  return{shape,Rp,Ra,Rd};
}
function buildGear(N,m,faceW){
  const{shape,Rp,Ra,Rd}=spurGearShape(N,m);
  const geom=new THREE.ExtrudeGeometry(shape,{steps:1,depth:faceW,
    bevelEnabled:true,bevelThickness:faceW*0.04,bevelSize:0.006,bevelSegments:3});
  geom.center();
  return{geom,Rp,Ra,Rd};
}

const MOD=0.22,N1=NTH,N2=Math.max(10,Math.round(N1*0.65));
const FW=0.25+(TRQ-50)/350*0.55;
const g1=buildGear(N1,MOD,FW);
const g2=buildGear(N2,MOD,FW*0.88);
const CD=g1.Rp+g2.Rp;

function makeHub(R,fw){
  const g=new THREE.CylinderGeometry(R*1.22,R*1.22,fw*0.18,32);
  return new THREE.Mesh(g,hubMat);
}

let mesh1,mesh2;
mesh1=new THREE.Mesh(g1.geom,mat1);
mesh1.castShadow=true; mesh1.receiveShadow=true; scene.add(mesh1);
const hub1f=makeHub(g1.Rd,FW); hub1f.rotation.x=Math.PI/2; hub1f.position.z=FW*0.62; mesh1.add(hub1f);
const hub1b=makeHub(g1.Rd,FW); hub1b.rotation.x=Math.PI/2; hub1b.position.z=-FW*0.62; mesh1.add(hub1b);

mesh2=new THREE.Mesh(g2.geom,mat2);
mesh2.castShadow=true; mesh2.receiveShadow=true; mesh2.position.set(CD,0,0); scene.add(mesh2);
const hub2f=makeHub(g2.Rd,FW*0.88); hub2f.rotation.x=Math.PI/2; hub2f.position.z=FW*0.58; mesh2.add(hub2f);
const hub2b=makeHub(g2.Rd,FW*0.88); hub2b.rotation.x=Math.PI/2; hub2b.position.z=-FW*0.58; mesh2.add(hub2b);

function makeShaft(r,len){
  const g=new THREE.CylinderGeometry(r,r,len,28);
  const m=new THREE.Mesh(g,shaftMat); m.rotation.x=Math.PI/2; m.castShadow=true; return m;
}
const sh1=makeShaft(Math.max(0.04,g1.Rd*0.28),FW*8); scene.add(sh1);
const sh2=makeShaft(Math.max(0.04,g2.Rd*0.28),FW*7); sh2.position.set(CD,0,0); scene.add(sh2);
function shaftCollar(r,z){
  const g=new THREE.CylinderGeometry(r*2.1,r*2.1,0.045,24);
  const m=new THREE.Mesh(g,shaftMat); m.rotation.x=Math.PI/2; m.position.z=z; return m;
}
[-FW*3.2,FW*3.2].forEach(z=>{
  const c1=shaftCollar(g1.Rd*0.28,z); scene.add(c1);
  const c2=shaftCollar(g2.Rd*0.28,z); c2.position.set(CD,0,0); scene.add(c2);
});

// ── FACTORY FLOOR ─────────────────────────────────────────────────────
const floorY=-(Math.max(g1.Ra,g2.Ra)+0.55);
const concFloorMat=new THREE.MeshStandardMaterial({
  map:concreteTex,color:new THREE.Color(0.10,0.12,0.16),metalness:0.06,roughness:0.97
});
const floorMesh=new THREE.Mesh(new THREE.PlaneGeometry(60,40),concFloorMat);
floorMesh.rotation.x=-Math.PI/2; floorMesh.position.set(CD/2,floorY,0);
floorMesh.receiveShadow=true; scene.add(floorMesh);
// Grid lines on floor (faint)
const gridHelper=new THREE.GridHelper(60,48,0x0B1520,0x070E18);
gridHelper.position.set(CD/2,floorY+0.02,0); scene.add(gridHelper);

// ══ VOLUMETRIC LIGHT SHAFTS ══════════════════════════════════════════════
function mkVolMat(op,hex){return new THREE.MeshBasicMaterial({color:hex,transparent:true,opacity:op,blending:THREE.AdditiveBlending,side:THREE.BackSide,depthWrite:false});}
const vMatA=mkVolMat(0.048,0xFFD070),vMatB=mkVolMat(0.028,0xFFB840),vMatC=mkVolMat(0.016,0xFF9020);
// Lens flare sprite texture
const _flC=document.createElement('canvas');_flC.width=128;_flC.height=128;
const _flX=_flC.getContext('2d'),_flG=_flX.createRadialGradient(64,64,0,64,64,64);
_flG.addColorStop(0,'rgba(255,255,220,1)');_flG.addColorStop(0.1,'rgba(255,210,100,0.9)');
_flG.addColorStop(0.4,'rgba(255,160,40,0.4)');_flG.addColorStop(1,'rgba(0,0,0,0)');
_flX.fillStyle=_flG;_flX.fillRect(0,0,128,128);
const flareMatA=new THREE.SpriteMaterial({map:new THREE.CanvasTexture(_flC),blending:THREE.AdditiveBlending,depthWrite:false,transparent:true,opacity:0.88});
const flareMatB=new THREE.SpriteMaterial({map:new THREE.CanvasTexture(_flC),blending:THREE.AdditiveBlending,depthWrite:false,transparent:true,opacity:0.55});
const lampVolGroup=new THREE.Group();
[CD/2-5,CD/2,CD/2+5].forEach((lx,li)=>{
  [-2,2].forEach((lz,zi)=>{
    const h=12.0-floorY,r=2.1;
    const cg=new THREE.ConeGeometry(r,h,14,1,true); cg.translate(0,-h/2,0);
    const cv=new THREE.Mesh(cg,vMatA); cv.position.set(lx,12.1,lz); lampVolGroup.add(cv);
    const cg2=new THREE.ConeGeometry(r*0.4,h*0.9,10,1,true); cg2.translate(0,-h*0.9/2,0);
    const cv2=new THREE.Mesh(cg2,vMatB); cv2.position.set(lx,12.1,lz); lampVolGroup.add(cv2);
    const cg3=new THREE.ConeGeometry(r*0.12,h*0.85,8,1,true); cg3.translate(0,-h*0.85/2,0);
    const cv3=new THREE.Mesh(cg3,vMatC); cv3.position.set(lx,12.1,lz); lampVolGroup.add(cv3);
    const sp=new THREE.Sprite(li===1&&zi===0?flareMatA:flareMatB);
    sp.scale.setScalar(li===1&&zi===0?2.0:1.3); sp.position.set(lx,12.3,lz); lampVolGroup.add(sp);
    const halo=new THREE.Mesh(new THREE.CircleGeometry(0.85,20),mkVolMat(0.20,0xFFE090));
    halo.rotation.x=-Math.PI/2; halo.position.set(lx,12.05,lz); lampVolGroup.add(halo);
  });
});
scene.add(lampVolGroup);
// Cold daylight god rays slanting in from factory windows on left wall
const winRayGroup=new THREE.Group();
const winRayMat=mkVolMat(0.028,0x80AAEE),winRayCore=mkVolMat(0.014,0x6090CC);
[[0,5.5],[0,2.0],[-4,5.5],[-4,2.0]].forEach(([dz,y])=>{
  const rm=new THREE.Mesh(new THREE.PlaneGeometry(10,4),winRayMat);
  rm.rotation.y=Math.PI/2+0.22; rm.rotation.z=0.13; rm.position.set(-10.5,y,dz); winRayGroup.add(rm);
  const rm2=new THREE.Mesh(new THREE.PlaneGeometry(7,1.1),winRayCore);
  rm2.rotation.y=Math.PI/2+0.24; rm2.rotation.z=0.10; rm2.position.set(-9.5,y,dz+0.1); winRayGroup.add(rm2);
  const dpB=new Float32Array(30*3);
  for(let i=0;i<30;i++){dpB[i*3]=-16+Math.random()*6;dpB[i*3+1]=y-1.5+Math.random()*3;dpB[i*3+2]=dz-1+Math.random()*2;}
  const dpG=new THREE.BufferGeometry(); dpG.setAttribute('position',new THREE.BufferAttribute(dpB,3));
  winRayGroup.add(new THREE.Points(dpG,new THREE.PointsMaterial({color:0xCCDDFF,size:0.07,transparent:true,opacity:0.50,blending:THREE.AdditiveBlending,depthWrite:false})));
});
scene.add(winRayGroup);

// ── FACTORY WALLS ─────────────────────────────────────────────────────
const wallMat=new THREE.MeshStandardMaterial({map:corrWallTex,color:new THREE.Color(0.09,0.11,0.17),metalness:0.55,roughness:0.82});
// Back wall
const backWall=new THREE.Mesh(new THREE.PlaneGeometry(60,22),wallMat);
backWall.position.set(CD/2,4.5,-14); scene.add(backWall);
// Left wall
const leftWall=new THREE.Mesh(new THREE.PlaneGeometry(30,22),wallMat);
leftWall.rotation.y=Math.PI/2; leftWall.position.set(-16,4.5,0); scene.add(leftWall);
// Right wall
const rightWall=new THREE.Mesh(new THREE.PlaneGeometry(30,22),wallMat);
rightWall.rotation.y=-Math.PI/2; rightWall.position.set(CD+16,4.5,0); scene.add(rightWall);
// Front wall (low, just for depth)
const frontWall=new THREE.Mesh(new THREE.PlaneGeometry(60,8),wallMat);
frontWall.rotation.y=Math.PI; frontWall.position.set(CD/2,0,14); scene.add(frontWall);

// ── FACTORY CEILING ────────────────────────────────────────────────────
const ceilMat=new THREE.MeshStandardMaterial({map:ceilTex,color:new THREE.Color(0.06,0.08,0.12),metalness:0.2,roughness:0.95});
const ceilMesh=new THREE.Mesh(new THREE.PlaneGeometry(60,30),ceilMat);
ceilMesh.rotation.x=Math.PI/2; ceilMesh.position.set(CD/2,13,0); scene.add(ceilMesh);

// ── STRUCTURAL STEEL ROOF TRUSSES ──────────────────────────────────────
const steelMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.12,0.15,0.22),metalness:0.88,roughness:0.35});
const steelDarkMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.07,0.09,0.14),metalness:0.92,roughness:0.28});
[-6,0,6].forEach(z=>{
  // Main horizontal beam (I-beam)
  const beam=new THREE.Mesh(new THREE.BoxGeometry(50,0.30,0.22),steelMat);
  beam.position.set(CD/2,12.6,z); scene.add(beam);
  const flgT=new THREE.Mesh(new THREE.BoxGeometry(50,0.08,0.60),steelMat);
  flgT.position.set(CD/2,12.73,z); scene.add(flgT);
  const flgB=new THREE.Mesh(new THREE.BoxGeometry(50,0.08,0.60),steelMat);
  flgB.position.set(CD/2,12.47,z); scene.add(flgB);
  // Diagonal truss members
  for(let x=-20;x<20;x+=8){
    const diag=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,3.5,8),steelDarkMat);
    diag.rotation.z=Math.PI/4*(x%16===0?1:-1);
    diag.position.set(CD/2+x,11.5,z); scene.add(diag);
  }
});
// Cross braces between trusses
[-3,3].forEach(z=>{
  const xbrace=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,12,6),steelDarkMat);
  xbrace.rotation.z=Math.PI/2; xbrace.position.set(CD/2,12.5,z); scene.add(xbrace);
});

// ── VENTILATION DUCTS ──────────────────────────────────────────────────
const ductMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.14,0.17,0.24),metalness:0.85,roughness:0.40});
// Main horizontal duct runs
[-3,3].forEach(z=>{
  const duct=new THREE.Mesh(new THREE.BoxGeometry(50,0.55,0.70),ductMat);
  duct.position.set(CD/2,11.8,z+1.2); scene.add(duct);
  // Duct flanges (connector rings)
  for(let x=-20;x<22;x+=8){
    const fl=new THREE.Mesh(new THREE.BoxGeometry(0.08,0.62,0.78),ductMat);
    fl.position.set(CD/2+x,11.8,z+1.2); scene.add(fl);
  }
});
// Vertical drop ducts to vents
[[CD/2-6,10],[CD/2+6,10],[CD/2,9.5]].forEach(([x,y])=>{
  const vduct=new THREE.Mesh(new THREE.BoxGeometry(0.50,2.0,0.50),ductMat);
  vduct.position.set(x,y,-3); scene.add(vduct);
  // Vent grille
  const vgrille=new THREE.Mesh(new THREE.BoxGeometry(0.55,0.08,0.55),steelDarkMat);
  vgrille.position.set(x,y-1.1,-3); scene.add(vgrille);
});

// ── FACTORY WINDOWS — LEFT WALL ────────────────────────────────────────
const winGlassMat=new THREE.MeshStandardMaterial({
  map:windowTex,color:new THREE.Color(0.3,0.45,0.7),
  transparent:true,opacity:0.45,metalness:0.1,roughness:0.05,
  emissive:new THREE.Color(0.12,0.18,0.30),emissiveIntensity:0.6
});
const winFrameMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.08,0.10,0.15),metalness:0.8,roughness:0.4});
[[0,5.5],[0,2],[-4,5.5],[-4,2]].forEach(([dz,y])=>{
  // Window pane
  const win=new THREE.Mesh(new THREE.PlaneGeometry(2.2,1.8),winGlassMat);
  win.rotation.y=Math.PI/2; win.position.set(-15.9,y,dz); scene.add(win);
  // Window frame border
  const frTop=new THREE.Mesh(new THREE.BoxGeometry(0.1,0.10,2.4),winFrameMat);
  frTop.position.set(-15.8,y+0.95,dz); scene.add(frTop);
  const frBot=frTop.clone(); frBot.position.set(-15.8,y-0.95,dz); scene.add(frBot);
  const frL=new THREE.Mesh(new THREE.BoxGeometry(0.1,2.0,0.10),winFrameMat);
  frL.position.set(-15.8,y,dz-1.2); scene.add(frL);
  const frR=frL.clone(); frR.position.set(-15.8,y,dz+1.2); scene.add(frR);
  // Window light shaft (volumetric beam)
  const shaftMesh=new THREE.Mesh(
    new THREE.CylinderGeometry(0.01,1.8,12,8,1,true),
    new THREE.MeshBasicMaterial({color:0x8AACCC,transparent:true,opacity:0.04,
      blending:THREE.AdditiveBlending,side:THREE.BackSide,depthWrite:false})
  );
  shaftMesh.rotation.z=-Math.PI/2; shaftMesh.position.set(-9,y,dz); scene.add(shaftMesh);
  // Window point light spill
  const winPt=new THREE.PointLight(0x7090C0,0.6,10);
  winPt.position.set(-12,y,dz); scene.add(winPt);
});

// ── OVERHEAD FLUORESCENT/SODIUM LAMP ARRAY ────────────────────────────
const lampHousingMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.14,0.16,0.22),metalness:0.9,roughness:0.3});
const sodiumGlowMat=new THREE.MeshBasicMaterial({color:new THREE.Color(1,0.88,0.55),transparent:true,opacity:0.95});
// 3x2 grid of overhead industrial lamps
[CD/2-5,CD/2,CD/2+5].forEach(lx=>{
  [-2,2].forEach(lz=>{
    // Lamp housing rectangle
    const hous=new THREE.Mesh(new THREE.BoxGeometry(1.4,0.18,0.35),lampHousingMat);
    hous.position.set(lx,12.2,lz); scene.add(hous);
    // Glow panel
    const glow=new THREE.Mesh(new THREE.PlaneGeometry(1.2,0.28),sodiumGlowMat);
    glow.rotation.x=Math.PI/2; glow.position.set(lx,12.1,lz); scene.add(glow);
    // Suspension rods
    [-0.5,0.5].forEach(rx=>{
      const rod=new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,0.8,6),steelDarkMat);
      rod.position.set(lx+rx,12.55,lz); scene.add(rod);
    });
    // Actual light source
    const lamp=new THREE.PointLight(0xFFE8A0,1.4,12);
    lamp.position.set(lx,11.8,lz); scene.add(lamp);
  });
});

// ── HEAVY MACHINERY IN BACKGROUND ─────────────────────────────────────
const machineMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.10,0.14,0.22),metalness:0.75,roughness:0.50});
const machineAccentMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.06,0.10,0.18),metalness:0.85,roughness:0.35});
const industrialYellow=new THREE.MeshStandardMaterial({color:new THREE.Color(0.55,0.42,0.04),metalness:0.5,roughness:0.7,
  emissive:new THREE.Color(0.04,0.03,0),emissiveIntensity:0.4});
// Motor housing (left background)
function makeMotorUnit(px,py,pz,scale=1){
  const grp=new THREE.Group();
  // Main housing cylinder
  const body=new THREE.Mesh(new THREE.CylinderGeometry(0.9*scale,0.9*scale,1.8*scale,24),machineMat);
  body.rotation.z=Math.PI/2; grp.add(body);
  // End caps
  [-0.9*scale,0.9*scale].forEach(dx=>{
    const cap=new THREE.Mesh(new THREE.CylinderGeometry(0.92*scale,0.92*scale,0.12*scale,24),machineAccentMat);
    cap.rotation.z=Math.PI/2; cap.position.x=dx; grp.add(cap);
  });
  // Cooling fins
  for(let a=0;a<Math.PI*2;a+=Math.PI/6){
    const fin=new THREE.Mesh(new THREE.BoxGeometry(1.6*scale,0.06*scale,0.12*scale),machineAccentMat);
    fin.rotation.x=a; fin.position.y=Math.sin(a)*0.92*scale; fin.position.z=Math.cos(a)*0.92*scale; grp.add(fin);
  }
  // Output shaft
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(0.12*scale,0.12*scale,0.6*scale,16),steelMat);
  shaft.rotation.z=Math.PI/2; shaft.position.x=1.2*scale; grp.add(shaft);
  // Base mount
  const base=new THREE.Mesh(new THREE.BoxGeometry(2.2*scale,0.22*scale,1.6*scale),machineAccentMat);
  base.position.y=-0.95*scale; grp.add(base);
  // Warning stripe
  const stripe=new THREE.Mesh(new THREE.BoxGeometry(2.0*scale,0.12*scale,0.08),industrialYellow);
  stripe.position.y=0.7*scale; grp.add(stripe);
  grp.position.set(px,py,pz); return grp;
}
scene.add(makeMotorUnit(-10,floorY+1.1,-11,1.1));
scene.add(makeMotorUnit(CD+9,floorY+1.1,-11,0.9));
scene.add(makeMotorUnit(-12,floorY+1.1,-8,0.75));

// Gearbox/reducer in back (boxy industrial shape)
function makeGearbox(px,py,pz){
  const grp=new THREE.Group();
  const box=new THREE.Mesh(new THREE.BoxGeometry(2.2,1.4,1.0),machineMat); grp.add(box);
  // Inspection covers (circles on face)
  [[-0.5,0.2],[0.5,-0.2]].forEach(([dx,dy])=>{
    const cov=new THREE.Mesh(new THREE.CylinderGeometry(0.25,0.25,0.06,16),machineAccentMat);
    cov.rotation.x=Math.PI/2; cov.position.set(dx,dy,0.53); grp.add(cov);
    const bolt=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,0.05,6),steelMat);
    for(let a=0;a<Math.PI*2;a+=Math.PI/2){
      const b=bolt.clone(); b.rotation.x=Math.PI/2;
      b.position.set(dx+Math.cos(a)*0.18,dy+Math.sin(a)*0.18,0.56); grp.add(b);
    }
  });
  // Oil drain plug
  const plug=new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,0.1,8),steelMat);
  plug.position.set(0,-0.73,0.2); grp.add(plug);
  // Yellow hazard edge
  const hy=new THREE.Mesh(new THREE.BoxGeometry(2.3,0.10,1.1),industrialYellow);
  hy.position.y=-0.72; grp.add(hy);
  const base=new THREE.Mesh(new THREE.BoxGeometry(2.5,0.2,1.3),machineAccentMat);
  base.position.y=-0.8; grp.add(base);
  grp.position.set(px,py,pz); return grp;
}
scene.add(makeGearbox(CD/2-8,floorY+1.0,-12));
scene.add(makeGearbox(CD/2+6,floorY+1.0,-12));

// Control cabinet on right wall
function makeControlPanel(px,py,pz){
  const grp=new THREE.Group();
  // Cabinet body
  const body=new THREE.Mesh(new THREE.BoxGeometry(1.2,2.4,0.5),machineMat); grp.add(body);
  // Door panel
  const door=new THREE.Mesh(new THREE.BoxGeometry(1.0,2.0,0.04),machineAccentMat);
  door.position.set(0,0,0.27); grp.add(door);
  // Indicator lights (green/red/amber)
  [[0.2,0.6,0x00FF44],[0.2,0.2,0xFF2222],[0.2,-0.2,0xFFAA00],[-0.2,0.6,0x00DDFF]].forEach(([dx,dy,col])=>{
    const led=new THREE.Mesh(new THREE.CircleGeometry(0.04,12),
      new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:0.9,blending:THREE.AdditiveBlending}));
    led.position.set(dx,dy,0.30); grp.add(led);
  });
  // Display screen (dim glow)
  const screen=new THREE.Mesh(new THREE.PlaneGeometry(0.55,0.35),
    new THREE.MeshBasicMaterial({color:0x002244,transparent:true,opacity:0.8,
      emissive:new THREE.Color(0,0.08,0.2)}));
  screen.position.set(0,-0.55,0.30); grp.add(screen);
  // Handle bar
  const handle=new THREE.Mesh(new THREE.BoxGeometry(0.06,0.3,0.08),steelMat);
  handle.position.set(0.42,0,0.30); grp.add(handle);
  // Base feet
  [[-0.4,-0.8],[-0.4,0.8],[0.4,-0.8],[0.4,0.8]].forEach(([dx,dz])=>{
    const ft=new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.08,0.15,8),steelDarkMat);
    ft.position.set(dx,-1.27,dz*0.35); grp.add(ft);
  });
  grp.position.set(px,py,pz); return grp;
}
scene.add(makeControlPanel(CD+13,floorY+2.3,-5));
scene.add(makeControlPanel(CD+13,floorY+2.3,2));

// Workbench / tool table (left side)
function makeWorkbench(px,py,pz,w=3){
  const grp=new THREE.Group();
  const top=new THREE.Mesh(new THREE.BoxGeometry(w,0.12,0.8),machineAccentMat); top.position.y=0.86; grp.add(top);
  const shelf=new THREE.Mesh(new THREE.BoxGeometry(w,0.08,0.75),machineMat); shelf.position.y=0.1; grp.add(shelf);
  [-(w/2-0.1),0,w/2-0.1].forEach(lx=>{
    const leg=new THREE.Mesh(new THREE.BoxGeometry(0.08,1.8,0.08),steelDarkMat);
    leg.position.set(lx,-0.04,0); grp.add(leg);
  });
  // Some tools/parts on top
  [[0.5,0.14,0.1],[-0.3,0.16,0.2],[-0.8,0.13,-0.1]].forEach(([tx,ty,tz])=>{
    const part=new THREE.Mesh(new THREE.BoxGeometry(0.2+Math.random()*0.3,0.08,0.12),machineMat);
    part.position.set(tx,ty+0.86,tz); grp.add(part);
  });
  grp.position.set(px,py,pz); return grp;
}
scene.add(makeWorkbench(-11,floorY+0.0,-6,2.8));

// ══ INDUSTRIAL PIPE NETWORK ═══════════════════════════════════════════════
const pipeMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.18,0.20,0.28),metalness:0.82,roughness:0.45});
const pipeGrnMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.07,0.28,0.12),metalness:0.70,roughness:0.55});
const pipeRedMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.32,0.05,0.05),metalness:0.72,roughness:0.52});
const insulMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.52,0.46,0.24),metalness:0.04,roughness:0.94});
const steelDkMat2=new THREE.MeshStandardMaterial({color:new THREE.Color(0.09,0.10,0.16),metalness:0.90,roughness:0.38});
function mkPipeH(x1,y,z,x2,r,m){const l=Math.abs(x2-x1),p=new THREE.Mesh(new THREE.CylinderGeometry(r,r,l,14),m);p.rotation.z=Math.PI/2;p.position.set((x1+x2)/2,y,z);p.castShadow=true;return p;}
function mkPipeV(x,y1,z,y2,r,m){const l=Math.abs(y2-y1),p=new THREE.Mesh(new THREE.CylinderGeometry(r,r,l,14),m);p.position.set(x,(y1+y2)/2,z);p.castShadow=true;return p;}
function mkPipeZ(x,y,z1,z2,r,m){const l=Math.abs(z2-z1),p=new THREE.Mesh(new THREE.CylinderGeometry(r,r,l,14),m);p.rotation.x=Math.PI/2;p.position.set(x,y,(z1+z2)/2);p.castShadow=true;return p;}
function mkElbow(x,y,z,r,m){const s=new THREE.Mesh(new THREE.SphereGeometry(r*1.1,12,10),m);s.position.set(x,y,z);return s;}
function mkCollar(x,y,z,r,m){const c=new THREE.Mesh(new THREE.CylinderGeometry(r*1.38,r*1.38,0.055,14),m);c.position.set(x,y,z);return c;}
function mkGauge(x,y,z,ry){
  const g=new THREE.Group();
  const bd=new THREE.Mesh(new THREE.CylinderGeometry(0.22,0.22,0.11,18),steelDkMat2); bd.rotation.x=Math.PI/2; g.add(bd);
  const fc=new THREE.Mesh(new THREE.CircleGeometry(0.18,18),new THREE.MeshBasicMaterial({color:0xDDE8F2})); fc.position.z=0.07; g.add(fc);
  const nd=new THREE.Mesh(new THREE.PlaneGeometry(0.022,0.13),new THREE.MeshBasicMaterial({color:0x111111}));
  nd.rotation.z=-0.4+Math.random()*1.2; nd.position.set(0.0,0.04,0.075); g.add(nd);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(0.195,0.024,8,22),steelDkMat2); rim.position.z=0.055; g.add(rim);
  g.position.set(x,y,z); g.rotation.y=ry||0; return g;
}
const pipeGrp=new THREE.Group();
// Main header pipe across back wall
pipeGrp.add(mkPipeH(-16,9.4,-13,CD+18,0.20,pipeMat));   // main coolant grey
pipeGrp.add(mkPipeH(-16,8.8,-13.6,CD+18,0.15,insulMat)); // insulated steam
pipeGrp.add(mkPipeH(-16,9.05,-12.5,CD+18,0.09,pipeGrnMat)); // green coolant return
pipeGrp.add(mkPipeH(-16,10.3,-12.9,CD+18,0.08,pipeRedMat)); // red fire suppression
// Sprinkler heads every 3.5m along fire line
for(let x=-14;x<CD+16;x+=3.5){
  const sh=new THREE.Group();
  sh.add(new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,0.18,8),pipeRedMat));
  const head=new THREE.Mesh(new THREE.SphereGeometry(0.07,10,8),
    new THREE.MeshStandardMaterial({color:new THREE.Color(0.60,0.25,0.04),metalness:0.85,roughness:0.22}));
  head.position.y=-0.13; sh.add(head);
  sh.position.set(x,10.2,-12.9); pipeGrp.add(sh);
}
// Left wall vertical drops
[-10,-4,2].forEach((pz,pi)=>{
  pipeGrp.add(mkPipeV(-14.5,2.5,pz,9.4,0.10,pi===1?pipeGrnMat:pipeMat));
  pipeGrp.add(mkElbow(-14.5,9.4,pz,0.10,pi===1?pipeGrnMat:pipeMat));
  [4.0,5.5,7.0].forEach(py=>pipeGrp.add(mkCollar(-14.5,py,pz,0.10,steelDkMat2)));
  const ggg=mkGauge(-14.1,5.5+pi*0.4,pz+0.22,Math.PI/2); pipeGrp.add(ggg);
});
// Right wall process pipes
pipeGrp.add(mkPipeH(CD-2,7.8,CD+16,CD+18,0.13,pipeMat));
pipeGrp.add(mkPipeH(CD-2,7.2,CD+16,CD+18,0.09,pipeRedMat));
[7.8,6.8].forEach((gy,gi)=>{ const gc=mkGauge(CD+15.6,gy,-2+gi*2.5,-Math.PI/2); pipeGrp.add(gc); });
// Collars on main header
for(let x=-14;x<CD+14;x+=3.8){
  pipeGrp.add(mkCollar(x,9.4,-13,0.20,steelDkMat2));
  pipeGrp.add(mkCollar(x,8.8,-13.6,0.15,steelDkMat2));
}
scene.add(pipeGrp);

// ══ STEAM VENT PARTICLES ══════════════════════════════════════════════════
const NSTM=90;
const steamBuf=new Float32Array(NSTM*3);
const steamVel=[];
const steamSrc=[[CD/2-5,8.6,-13.4],[CD/2+4,8.8,-13.2],[-14.5,5.5,-10]];
for(let i=0;i<NSTM;i++){
  const s=steamSrc[i%3];
  steamBuf[i*3]=s[0]+(Math.random()-0.5)*0.4;
  steamBuf[i*3+1]=s[1]+Math.random()*2.5;
  steamBuf[i*3+2]=s[2]+(Math.random()-0.5)*0.4;
  steamVel.push({x:(Math.random()-0.5)*0.010,y:0.013+Math.random()*0.018,z:(Math.random()-0.5)*0.008});
}
const steamGeo=new THREE.BufferGeometry();
steamGeo.setAttribute('position',new THREE.BufferAttribute(steamBuf,3));
const steamPts=new THREE.Points(steamGeo,new THREE.PointsMaterial({
  color:0xC8D8E8,size:0.28,transparent:true,opacity:0.24,
  blending:THREE.AdditiveBlending,depthWrite:false,sizeAttenuation:true
}));
steamPts.frustumCulled=false; scene.add(steamPts);

// ══ CABLE TRAYS OVERHEAD ══════════════════════════════════════════════════
const cTrayMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.10,0.12,0.18),metalness:0.88,roughness:0.48});
[-4.5,0,4.5].forEach(tz=>{
  const base=new THREE.Mesh(new THREE.BoxGeometry(50,0.07,0.38),cTrayMat); base.position.set(CD/2,10.9,tz+5); scene.add(base);
  const lw=new THREE.Mesh(new THREE.BoxGeometry(50,0.14,0.05),cTrayMat); lw.position.set(CD/2,10.97,tz+4.81); scene.add(lw);
  const rw=lw.clone(); rw.position.z=tz+5.19; scene.add(rw);
  // Coloured cable bundles
  [[0xCC2222,0.048],[0x2255CC,0.048],[0x228833,0.040],[0xCCAA11,0.036]].forEach(([col,cr],ci)=>{
    const cMat=new THREE.MeshStandardMaterial({color:col,metalness:0.03,roughness:0.87});
    for(let cx=-24;cx<26;cx+=0.9){
      const seg=new THREE.Mesh(new THREE.SphereGeometry(cr,5,4),cMat);
      seg.position.set(CD/2+cx,10.93,tz+4.82+ci*0.055+Math.sin(cx*0.55+ci)*0.012);
      scene.add(seg);
    }
  });
  for(let cx=-22;cx<24;cx+=3.2){
    const hgr=new THREE.Mesh(new THREE.BoxGeometry(0.055,0.50,0.40),steelDkMat2); hgr.position.set(CD/2+cx,11.14,tz+5); scene.add(hgr);
  }
});

// ══ FLOOR DRAINS ══════════════════════════════════════════════════════════
const drainMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.05,0.06,0.09),metalness:0.82,roughness:0.55});
[[0,-1],[CD+2,2],[CD/2-6,-3]].forEach(([dx,dz])=>{
  const df=new THREE.Mesh(new THREE.PlaneGeometry(0.52,0.52),drainMat);
  df.rotation.x=-Math.PI/2; df.position.set(dx,floorY+0.003,dz); scene.add(df);
  for(let gi=0;gi<5;gi++){
    const bar=new THREE.Mesh(new THREE.BoxGeometry(0.46,0.028,0.038),steelDkMat2);
    bar.rotation.x=-Math.PI/2; bar.position.set(dx,floorY+0.006,dz-0.20+gi*0.10); scene.add(bar);
  }
});

// ══ OIL / WATER PUDDLES ═══════════════════════════════════════════════════
const puddleMat=new THREE.MeshPhysicalMaterial({color:new THREE.Color(0.012,0.016,0.024),metalness:0.30,roughness:0.03,transparent:true,opacity:0.90,envMapIntensity:2.5});
const oilMat=new THREE.MeshPhysicalMaterial({color:new THREE.Color(0.022,0.015,0.008),metalness:0.18,roughness:0.02,transparent:true,opacity:0.86,envMapIntensity:3.0,iridescence:0.7,iridescenceIOR:1.42});
[[CD/2-3,floorY+0.004,-4.5],[CD/2+5,floorY+0.004,2.2],[-8,floorY+0.004,-5],
 [CD+4,floorY+0.004,1.2],[CD/2+1,floorY+0.004,5.5]].forEach(([px,py,pz],i)=>{
  const rx=0.55+Math.random()*1.1,rz=0.30+Math.random()*0.75;
  const pm=new THREE.Mesh(new THREE.PlaneGeometry(rx*2,rz*2),i%3===0?oilMat:puddleMat);
  pm.rotation.x=-Math.PI/2; pm.rotation.z=Math.random()*Math.PI; pm.position.set(px,py,pz);
  scene.add(pm);
});

// Tool/parts shelf rack (right background)
function makeShelfRack(px,py,pz){
  const grp=new THREE.Group();
  const col=new THREE.Mesh(new THREE.BoxGeometry(0.06,4,0.06),steelMat);
  [-0.8,0.8].forEach(dx=>{ const c=col.clone(); c.position.set(dx,0,0); grp.add(c); });
  [-1.5,-0.5,0.5,1.5].forEach(dy=>{
    const shelf=new THREE.Mesh(new THREE.BoxGeometry(1.8,0.05,0.5),machineAccentMat);
    shelf.position.set(0,dy,0); grp.add(shelf);
    // Parts boxes on shelves
    for(let i=-2;i<3;i++){
      if(Math.random()>0.3){
        const box=new THREE.Mesh(new THREE.BoxGeometry(0.18,0.22,0.22),machineMat);
        box.position.set(i*0.3,dy+0.14,0); grp.add(box);
      }
    }
  });
  grp.position.set(px,py,pz); return grp;
}
scene.add(makeShelfRack(-13,floorY+2.0,-2));
scene.add(makeShelfRack(-13,floorY+2.0,4));

// ── CATWALK / MEZZANINE WALKWAY ────────────────────────────────────────
const gratingMat=new THREE.MeshStandardMaterial({map:gratingTex,color:new THREE.Color(0.09,0.11,0.18),metalness:0.75,roughness:0.65,transparent:true,opacity:0.92});
// Catwalk deck (left side at height)
const catwalk=new THREE.Mesh(new THREE.PlaneGeometry(3.5,28),gratingMat);
catwalk.rotation.x=-Math.PI/2; catwalk.position.set(-11,5.5,0); scene.add(catwalk);
// Catwalk handrails
const railMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.55,0.42,0.04),metalness:0.7,roughness:0.5}); // yellow safety railing
[[-12.5,5],[-9.5,5]].forEach(([rx])=>{
  const rail=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.035,28,8),railMat);
  rail.rotation.z=Math.PI/2; rail.position.set(-11,6.0,rx-rx+0); // horizontal rail
  // Actually place properly
  const railH=new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,28,8),railMat);
  railH.rotation.z=Math.PI/2; railH.position.set(-11,6.2,0); scene.add(railH);
  const railL=new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,28,8),railMat);
  railL.rotation.z=Math.PI/2; railL.position.set(-11,5.7,0); scene.add(railL);
});
// Catwalk uprights / stanchions
for(let z=-12;z<=12;z+=3){
  const post=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,0.7,8),railMat);
  post.position.set(-9.4,5.85,z); scene.add(post);
  const post2=post.clone(); post2.position.set(-12.6,5.85,z); scene.add(post2);
}
// Catwalk support brackets to wall
for(let z=-10;z<=10;z+=5){
  const brk=new THREE.Mesh(new THREE.BoxGeometry(1.8,0.10,0.10),steelMat);
  brk.position.set(-12,5.5,z); scene.add(brk);
  const diagonal=new THREE.Mesh(new THREE.BoxGeometry(0.06,1.5,0.06),steelDarkMat);
  diagonal.rotation.z=Math.PI/5; diagonal.position.set(-13.2,4.9,z); scene.add(diagonal);
}

// ── SAFETY BARRIERS AROUND GEAR ───────────────────────────────────────
const barrierYellow=new THREE.MeshStandardMaterial({
  color:new THREE.Color(0.6,0.45,0.02),metalness:0.5,roughness:0.7,
  emissive:new THREE.Color(0.08,0.06,0),emissiveIntensity:0.35
});
const barrierDark=new THREE.MeshStandardMaterial({color:new THREE.Color(0.05,0.05,0.05),metalness:0.4,roughness:0.7});
const postR=0.045, postH=1.1;
function makeSafetyPost(px,py,pz){
  const grp=new THREE.Group();
  const post=new THREE.Mesh(new THREE.CylinderGeometry(postR,postR,postH,10),barrierYellow);
  post.position.y=postH/2; grp.add(post);
  // Black band
  const band=new THREE.Mesh(new THREE.CylinderGeometry(postR+0.01,postR+0.01,0.12,10),barrierDark);
  band.position.y=postH*0.4; grp.add(band);
  const band2=band.clone(); band2.position.y=postH*0.7; grp.add(band2);
  // Base plate
  const base=new THREE.Mesh(new THREE.CylinderGeometry(0.14,0.14,0.05,12),steelDarkMat);
  base.position.y=0.025; grp.add(base);
  grp.position.set(px,py,pz); return grp;
}
function makeSafetyRail(x1,z1,x2,z2,y){
  const dx=x2-x1, dz=z2-z1;
  const len=Math.sqrt(dx*dx+dz*dz);
  const ang=Math.atan2(dz,dx);
  const rail=new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,len,8),barrierYellow);
  rail.rotation.z=Math.PI/2; rail.rotation.y=ang;
  rail.position.set((x1+x2)/2,y,(z1+z2)/2);
  return rail;
}
const safetyR=Math.max(g1.Ra,g2.Ra)*2+1.5;
const postPositions=[
  [-safetyR,floorY,  -safetyR],[-safetyR,floorY, 0],[-safetyR,floorY, safetyR],
  [CD/2,floorY,-safetyR*1.3],[CD/2,floorY,safetyR*1.3],
  [CD+safetyR,floorY,-safetyR],[CD+safetyR,floorY, 0],[CD+safetyR,floorY, safetyR],
];
postPositions.forEach(([px,py,pz])=>{ scene.add(makeSafetyPost(px,py,pz)); });
// Connect with rails
const railY=floorY+postH*0.7;
const railY2=floorY+postH*0.38;
[[0,1],[1,2],[5,6],[6,7],[0,3],[2,4],[5,3],[7,4]].forEach(([a,b])=>{
  const pa=postPositions[a], pb=postPositions[b];
  scene.add(makeSafetyRail(pa[0],pa[2],pb[0],pb[2],railY));
  scene.add(makeSafetyRail(pa[0],pa[2],pb[0],pb[2],railY2));
});

// ══ ROTATING AMBER WARNING BEACON ════════════════════════════════════════
const beaconGroup=new THREE.Group();
beaconGroup.add(new THREE.Mesh(new THREE.CylinderGeometry(0.11,0.14,0.11,16),steelMat));
const domeM=new THREE.MeshPhysicalMaterial({color:new THREE.Color(0.80,0.44,0.02),metalness:0.04,roughness:0.13,transparent:true,opacity:0.80,clearcoat:0.95,clearcoatRoughness:0.04,emissive:new THREE.Color(0.55,0.22,0),emissiveIntensity:0.35});
const domeMesh=new THREE.Mesh(new THREE.SphereGeometry(0.14,16,10,0,Math.PI*2,0,Math.PI*0.62),domeM);
domeMesh.position.y=0.09; beaconGroup.add(domeMesh);
const beaconLight=new THREE.SpotLight(0xFF8800,0,20,Math.PI*0.18,0.55,1.4);
beaconLight.position.y=0.14; beaconGroup.add(beaconLight);
beaconGroup.position.set(CD/2+2,floorY+2.9,-13.9);
scene.add(beaconGroup);

// ══ EXIT SIGNS ════════════════════════════════════════════════════════════
function mkExitSign(x,y,z,ry){
  const g=new THREE.Group();
  g.add(Object.assign(new THREE.Mesh(new THREE.BoxGeometry(0.64,0.28,0.055),new THREE.MeshStandardMaterial({color:0x002200,metalness:0.5,roughness:0.6})),{}));
  const face=new THREE.Mesh(new THREE.PlaneGeometry(0.56,0.21),new THREE.MeshBasicMaterial({color:0x00EE44,transparent:true,opacity:0.88,blending:THREE.AdditiveBlending}));
  face.position.z=0.032; g.add(face);
  const gl=new THREE.PointLight(0x00DD44,0.50,3.8); gl.position.z=0.12; g.add(gl);
  g.position.set(x,y,z); g.rotation.y=ry||0; return g;
}
scene.add(mkExitSign(-15.6,4.2,0,Math.PI/2));
scene.add(mkExitSign(CD+15.6,4.2,0,-Math.PI/2));

// ══ ELECTRICAL CONDUIT RUNS ════════════════════════════════════════════════
const condMat=new THREE.MeshStandardMaterial({color:new THREE.Color(0.13,0.14,0.21),metalness:0.87,roughness:0.42});
for(let x=-12;x<CD+12;x+=5.5){
  const cond=new THREE.Mesh(new THREE.CylinderGeometry(0.038,0.038,3.8,10),condMat);
  cond.rotation.z=Math.PI/2; cond.position.set(x,5.6,-13.88); scene.add(cond);
  const jb=new THREE.Mesh(new THREE.BoxGeometry(0.24,0.24,0.10),new THREE.MeshStandardMaterial({color:0x0D0F18,metalness:0.88,roughness:0.35}));
  jb.position.set(x,5.6,-13.84); scene.add(jb);
}
// Vertical conduit on left wall
[-9,-3,3].forEach(cz=>{
  const vc=new THREE.Mesh(new THREE.CylinderGeometry(0.032,0.032,8.5,10),condMat);
  vc.position.set(-15.88,5,cz); scene.add(vc);
});

// ══ EMERGENCY RED LIGHT ═══════════════════════════════════════════════════
const emL=new THREE.PointLight(0xFF1111,0.28,9); emL.position.set(-15.5,7.5,-5); scene.add(emL);
const emH=new THREE.Mesh(new THREE.BoxGeometry(0.17,0.11,0.08),condMat); emH.position.set(-15.42,7.5,-5); scene.add(emH);
const emLED=new THREE.Mesh(new THREE.PlaneGeometry(0.09,0.06),new THREE.MeshBasicMaterial({color:0xFF2200,transparent:true,opacity:0.90,blending:THREE.AdditiveBlending}));
emLED.rotation.y=Math.PI/2; emLED.position.set(-15.38,7.5,-5); scene.add(emLED);

// ── FLOOR MARKINGS (yellow lines + hazard zone) ────────────────────────
const lineMatY=new THREE.MeshBasicMaterial({color:0xFFCC00,transparent:true,opacity:0.28});
const lineMatW=new THREE.MeshBasicMaterial({color:0xFFFFFF,transparent:true,opacity:0.15});
// Safety zone boundary lines
const zoneR=safetyR+0.2;
for(let a=0;a<Math.PI*2;a+=Math.PI/16){
  const seg=new THREE.Mesh(new THREE.PlaneGeometry(0.6,0.12),lineMatY);
  seg.rotation.x=-Math.PI/2; seg.rotation.z=a;
  seg.position.set(CD/2+Math.cos(a)*zoneR,floorY+0.03,Math.sin(a)*zoneR);
  scene.add(seg);
}
// Centre axis walkway line
const axisLine=new THREE.Mesh(new THREE.PlaneGeometry(0.08,30),lineMatW);
axisLine.rotation.x=-Math.PI/2; axisLine.position.set(CD/2,floorY+0.03,0); scene.add(axisLine);
// Hazard stripes near gear
for(let i=-4;i<=4;i++){
  const strp=new THREE.Mesh(new THREE.PlaneGeometry(0.18,1.8),
    new THREE.MeshBasicMaterial({color:i%2===0?0xFFCC00:0x111111,transparent:true,opacity:0.22}));
  strp.rotation.x=-Math.PI/2; strp.rotation.z=Math.PI/4;
  strp.position.set(CD/2+i*0.5,floorY+0.04,-safetyR-0.1); scene.add(strp);
  const strp2=strp.clone(); strp2.position.z=safetyR+0.1; scene.add(strp2);
}

// ── AMBIENT DUST PARTICLES ─────────────────────────────────────────────
const NDUST=180;
const dustBuf=new Float32Array(NDUST*3);
for(let i=0;i<NDUST;i++){
  dustBuf[i*3]  =CD/2+(Math.random()-0.5)*20;
  dustBuf[i*3+1]=floorY+Math.random()*9;
  dustBuf[i*3+2]=(Math.random()-0.5)*18;
}
const dustGeom=new THREE.BufferGeometry();
dustGeom.setAttribute('position',new THREE.BufferAttribute(dustBuf,3));
const dustMat=new THREE.PointsMaterial({
  color:0x8090A8,size:0.045,transparent:true,opacity:0.35,
  blending:THREE.AdditiveBlending,depthWrite:false
});
const dustPts=new THREE.Points(dustGeom,dustMat); dustPts.frustumCulled=false; scene.add(dustPts);
const dustVel=Array.from({length:NDUST},()=>new THREE.Vector3(
  (Math.random()-0.5)*0.002,(Math.random()-0.5)*0.001,(Math.random()-0.5)*0.002
));

// ── HEALTH RINGS ──────────────────────────────────────────────────────
const ringCol=HLT>0.7?0x00C896:HLT>0.4?0xF5A623:0xE8394A;
const ringMat2=new THREE.MeshBasicMaterial({color:ringCol,transparent:true,opacity:0.55,blending:THREE.AdditiveBlending,depthWrite:false});
const healthRing=new THREE.Mesh(new THREE.TorusGeometry(g1.Ra+0.30,0.028,10,80),ringMat2); scene.add(healthRing);
const innerRingMat=new THREE.MeshBasicMaterial({color:0x00AEEF,transparent:true,opacity:0.20,blending:THREE.AdditiveBlending,depthWrite:false});
const innerRing=new THREE.Mesh(new THREE.TorusGeometry(g1.Ra+0.12,0.013,8,64),innerRingMat); scene.add(innerRing);

// Outer danger ring (only when health < 0.45)
const dangerRingMat=new THREE.MeshBasicMaterial({color:0xE8394A,transparent:true,opacity:Math.max(0,(0.45-HLT)*1.5),blending:THREE.AdditiveBlending,depthWrite:false});
const dangerRing=new THREE.Mesh(new THREE.TorusGeometry(g1.Ra+0.54,0.016,8,80),dangerRingMat); scene.add(dangerRing);

// ── HOLOGRAPHIC SCAN RINGS ────────────────────────────────────────────
const scanRings=[];
for(let i=0;i<3;i++){
  const rm=new THREE.MeshBasicMaterial({color:0x00AEEF,transparent:true,opacity:0.12,blending:THREE.AdditiveBlending,depthWrite:false});
  const rr=new THREE.Mesh(new THREE.TorusGeometry(g1.Ra+0.8+i*0.3,0.008,6,60),rm);
  rr.rotation.x=Math.PI/2*(i%2===0?1:-1);
  scene.add(rr); scanRings.push({mesh:rr,mat:rm,phase:i*2.1});
}

// ── SPARKS ────────────────────────────────────────────────────────────
const NS=220,spkBuf=new Float32Array(NS*3).fill(-999);
const spkVel=Array.from({length:NS},()=>new THREE.Vector3());
const spkAge=new Float32Array(NS).fill(0);
const spkGeom2=new THREE.BufferGeometry();
spkGeom2.setAttribute('position',new THREE.BufferAttribute(spkBuf,3));
const spkMat2=new THREE.PointsMaterial({color:0xFFCC44,size:0.06,transparent:true,opacity:0.95,blending:THREE.AdditiveBlending,depthWrite:false});
const sparkPts=new THREE.Points(spkGeom2,spkMat2); sparkPts.frustumCulled=false; scene.add(sparkPts);
let spkHead2=0;
function emitSparks(n,ox,oy,oz){
  for(let i=0;i<n;i++){
    const k=spkHead2%NS; spkHead2++;
    spkBuf[k*3]=ox;spkBuf[k*3+1]=oy;spkBuf[k*3+2]=oz;
    const ang=Math.random()*Math.PI*2,sp=0.03+Math.random()*0.08;
    spkVel[k].set(Math.cos(ang)*sp,0.03+Math.random()*0.08,Math.sin(ang)*sp);
    spkAge[k]=1.0;
  }
}

// Metal debris (dark flakes for low health)
const ND=80,dBuf=new Float32Array(ND*3).fill(-999);
const dVel=Array.from({length:ND},()=>new THREE.Vector3());
const dAge=new Float32Array(ND).fill(0);
const dGeom=new THREE.BufferGeometry();
dGeom.setAttribute('position',new THREE.BufferAttribute(dBuf,3));
const dMat=new THREE.PointsMaterial({color:0x203040,size:0.04,transparent:true,opacity:Math.max(0,(0.5-HLT)*1.8),blending:THREE.AdditiveBlending,depthWrite:false});
const debrisPts=new THREE.Points(dGeom,dMat); debrisPts.frustumCulled=false; scene.add(debrisPts);
let dHead=0;
function emitDebris(n,ox,oy,oz){
  for(let i=0;i<n;i++){
    const k=dHead%ND; dHead++;
    dBuf[k*3]=ox;dBuf[k*3+1]=oy;dBuf[k*3+2]=oz;
    const ang=Math.random()*Math.PI*2,sp=0.005+Math.random()*0.025;
    dVel[k].set(Math.cos(ang)*sp*0.5,0.008+Math.random()*0.018,Math.sin(ang)*sp);
    dAge[k]=1.0;
  }
}

// ── HEAT ──────────────────────────────────────────────────────────────
const NH2=55,hBuf=new Float32Array(NH2*3);
const hVel=Array.from({length:NH2},()=>new THREE.Vector3((Math.random()-.5)*0.014,0.009+Math.random()*0.02,(Math.random()-.5)*0.011));
for(let i=0;i<NH2;i++){const a=Math.random()*Math.PI*2,r=Math.random()*g1.Rp*0.85;hBuf[i*3]=r*Math.cos(a);hBuf[i*3+1]=r*Math.sin(a);hBuf[i*3+2]=(Math.random()-.5)*FW;}
const hGeom2=new THREE.BufferGeometry(); hGeom2.setAttribute('position',new THREE.BufferAttribute(hBuf,3));
const hAlpha2=Math.min(0.75,Math.max(0,(TMP-55)/65)*0.75);
const hMat2=new THREE.PointsMaterial({color:0xFF6612,size:0.11,transparent:true,opacity:hAlpha2,blending:THREE.AdditiveBlending,depthWrite:false});
const heatPts=new THREE.Points(hGeom2,hMat2); heatPts.frustumCulled=false; scene.add(heatPts);

// ── SMOKE ─────────────────────────────────────────────────────────────
const NSM=80,sBuf=new Float32Array(NSM*3);
const sSpd=Array.from({length:NSM},()=>0.003+Math.random()*0.009);
for(let i=0;i<NSM;i++){const a=Math.random()*Math.PI*2,r=Math.random()*g1.Rp*0.95;sBuf[i*3]=r*Math.cos(a);sBuf[i*3+1]=(Math.random()-.5)*g1.Rp*0.5;sBuf[i*3+2]=(Math.random()-.5)*FW;}
const sGeom2=new THREE.BufferGeometry(); sGeom2.setAttribute('position',new THREE.BufferAttribute(sBuf,3));
const sAlpha2=Math.max(0,(0.5-HLT)*1.2);
const sMat2=new THREE.PointsMaterial({color:0x405060,size:0.20,transparent:true,opacity:sAlpha2,blending:THREE.AdditiveBlending,depthWrite:false});
const smokePts=new THREE.Points(sGeom2,sMat2); smokePts.frustumCulled=false; scene.add(smokePts);

// ── ORBIT CONTROLS ────────────────────────────────────────────────────
let drag=false,px=0,py=0;
let sTheta=camCurrent.theta,sPhi=camCurrent.phi,sR={v:camCurrent.r};
function clampPhi(p){return Math.max(0.10,Math.min(1.52,p));}
canvas.addEventListener('mousedown',e=>{drag=true;px=e.clientX;py=e.clientY;});
window.addEventListener('mouseup',()=>drag=false);
window.addEventListener('mousemove',e=>{
  if(!drag)return;
  sTheta-=(e.clientX-px)*0.007; sPhi=clampPhi(sPhi-(e.clientY-py)*0.007);
  px=e.clientX;py=e.clientY;
  camTarget.theta=sTheta;camTarget.phi=sPhi;
});
canvas.addEventListener('wheel',e=>{sR.v=Math.max(1.8,Math.min(22,sR.v+e.deltaY*0.011));camTarget.r=sR.v;},{passive:true});
canvas.addEventListener('touchstart',e=>{if(e.touches.length===1){drag=true;px=e.touches[0].clientX;py=e.touches[0].clientY;}},{passive:true});
canvas.addEventListener('touchend',()=>drag=false,{passive:true});
canvas.addEventListener('touchmove',e=>{
  if(!drag||e.touches.length!==1)return;
  sTheta-=(e.touches[0].clientX-px)*0.007;
  sPhi=clampPhi(sPhi-(e.touches[0].clientY-py)*0.007);
  px=e.touches[0].clientX;py=e.touches[0].clientY;
  camTarget.theta=sTheta;camTarget.phi=sPhi;
},{passive:true});

const gCenter=new THREE.Vector3(CD/2,0,0);

// ── ANIMATION ─────────────────────────────────────────────────────────
const omega=(SPD*Math.PI/30)/60;
const ratio=N1/N2;
let angle=0,vibPh=0,shockTmr=0,shockAct=0,t=0;
const vibAmp=(VIB/10)*0.08;
const vibFq=0.045+VIB*0.018;
const shockInt=Math.max(28,Math.round(85/Math.max(0.1,SHK)));
const shockMag=SHK*0.02;
const sparkRate=Math.max(2,Math.round(12/Math.max(0.5,SHK+1)));
let spkTmr=0;
const debrisRate=Math.max(5,Math.round(30/(Math.max(0,(0.5-HLT)*4)+0.1)));
let debrisTmr=0;

applyViewMode();

function animate(){
  requestAnimationFrame(animate);
  t++;
  vibPh+=vibFq; shockTmr++;
  if(shockTmr>=shockInt){shockAct=16;shockTmr=0;}
  let dRot=0;
  if(shockAct>0){dRot=shockMag*Math.sin((1-shockAct/16)*Math.PI);shockAct--;}
  angle+=omega+dRot;
  const vx=Math.sin(vibPh)*vibAmp,vy=Math.cos(vibPh*1.38)*vibAmp*0.45;

  mesh1.rotation.z=angle; mesh1.position.set(vx,vy,0);
  healthRing.rotation.z=-angle*0.025; healthRing.position.set(vx,vy,0);
  innerRing.rotation.z=angle*0.04; innerRing.position.set(vx,vy,0);
  dangerRing.rotation.z=angle*0.015; dangerRing.position.set(vx,vy,0);
  sh1.position.set(vx,vy,0);
  mesh2.rotation.z=-(angle*ratio)+Math.PI/N2; mesh2.position.set(CD+vx*0.3,vy*0.3,0);
  sh2.position.set(CD+vx*0.3,vy*0.3,0);

  // Holographic scan rings animate
  scanRings.forEach((sr,i)=>{
    sr.mesh.rotation.x+=0.005*(i%2===0?1:-1);
    sr.mesh.rotation.y+=0.003*(i%2===0?-1:1);
    sr.mat.opacity=0.06+0.08*Math.sin(t*0.03+sr.phase);
  });

  // Sparks
  spkTmr++;
  if(spkTmr>=sparkRate){
    spkTmr=0;
    const spx=vx+g1.Rp*Math.cos(angle),spy=vy+g1.Rp*Math.sin(angle);
    emitSparks(Math.max(1,Math.round(SHK+0.5)),spx,spy,(Math.random()-.5)*FW*0.5);
  }
  for(let i=0;i<NS;i++){
    if(spkAge[i]<=0)continue;
    spkAge[i]-=0.065;
    spkBuf[i*3]+=spkVel[i].x;spkBuf[i*3+1]+=spkVel[i].y;spkBuf[i*3+2]+=spkVel[i].z;
    spkVel[i].y-=0.004;
    if(spkAge[i]<=0)spkBuf[i*3+1]=-999;
  }
  spkGeom2.attributes.position.needsUpdate=true;

  // Debris (wear particles for low health)
  if(HLT<0.5){
    debrisTmr++;
    if(debrisTmr>=debrisRate){
      debrisTmr=0;
      emitDebris(1,vx+(Math.random()-.5)*g1.Ra,vy+(Math.random()-.5)*g1.Ra,(Math.random()-.5)*FW);
    }
    for(let i=0;i<ND;i++){
      if(dAge[i]<=0)continue;
      dAge[i]-=0.03;
      dBuf[i*3]+=dVel[i].x;dBuf[i*3+1]+=dVel[i].y;dBuf[i*3+2]+=dVel[i].z;
      dVel[i].y-=0.002;
      if(dAge[i]<=0)dBuf[i*3+1]=-999;
    }
    dGeom.attributes.position.needsUpdate=true;
  }

  // Ambient factory dust drift
  for(let i=0;i<NDUST;i++){
    dustBuf[i*3]  +=dustVel[i].x;
    dustBuf[i*3+1]+=dustVel[i].y;
    dustBuf[i*3+2]+=dustVel[i].z;
    // Wrap vertically
    if(dustBuf[i*3+1]>floorY+10) dustBuf[i*3+1]=floorY+0.2;
    if(dustBuf[i*3+1]<floorY)    dustBuf[i*3+1]=floorY+9;
    // Slow gentle swirl from vibration
    dustBuf[i*3]  +=Math.sin(t*0.008+i)*0.0003*VIB;
    dustBuf[i*3+2]+=Math.cos(t*0.011+i)*0.0002*VIB;
  }
  dustGeom.attributes.position.needsUpdate=true;

  // Pulse window light shafts with slight flicker
  scene.children.forEach(ch=>{
    if(ch.isPointLight && ch.color.b>0.5 && ch.color.r<0.5){
      ch.intensity=0.5+0.15*Math.sin(t*0.04+ch.position.z);
    }
  });

  // Heat
  for(let i=0;i<NH2;i++){
    hBuf[i*3]+=hVel[i].x;hBuf[i*3+1]+=hVel[i].y;hBuf[i*3+2]+=hVel[i].z;
    if(hBuf[i*3+1]>g1.Ra+0.65){
      const a=Math.random()*Math.PI*2,r=Math.random()*g1.Rp*0.9;
      hBuf[i*3]=r*Math.cos(a)+vx;hBuf[i*3+1]=-g1.Rp*0.3+vy;hBuf[i*3+2]=(Math.random()-.5)*FW;
    }
  }
  hGeom2.attributes.position.needsUpdate=true;

  // Smoke
  for(let i=0;i<NSM;i++){
    sBuf[i*3]+=(Math.random()-.5)*0.005;sBuf[i*3+1]+=sSpd[i];sBuf[i*3+2]+=(Math.random()-.5)*0.003;
    if(sBuf[i*3+1]>g1.Ra+1.6){
      const a=Math.random()*Math.PI*2,r=Math.random()*g1.Rp*0.85;
      sBuf[i*3]=r*Math.cos(a)+vx;sBuf[i*3+1]=-g1.Rp*0.5+vy;sBuf[i*3+2]=(Math.random()-.5)*FW;
    }
  }
  sGeom2.attributes.position.needsUpdate=true;

  // Pulse lights & rings
  ptRisk.intensity=1.0+1.5*Math.sin(t*0.065);
  ptCyan.intensity=0.5+0.4*Math.sin(t*0.042+1);
  ringMat2.opacity=0.28+0.28*Math.sin(t*0.048);
  innerRingMat.opacity=0.10+0.12*Math.sin(t*0.082+0.8);
  dangerRingMat.opacity=Math.max(0,(0.45-HLT)*1.5)*(0.5+0.5*Math.sin(t*0.1));

  // Smooth camera

  // Steam particles rise from vents
  for(let i=0;i<NSTM;i++){
    steamBuf[i*3]+=steamVel[i].x; steamBuf[i*3+1]+=steamVel[i].y; steamBuf[i*3+2]+=steamVel[i].z;
    const s=steamSrc[i%3];
    if(steamBuf[i*3+1]>s[1]+4.0){
      steamBuf[i*3]=s[0]+(Math.random()-0.5)*0.4;
      steamBuf[i*3+1]=s[1]; steamBuf[i*3+2]=s[2]+(Math.random()-0.5)*0.4;
    }
  }
  steamGeo.attributes.position.needsUpdate=true;
  // Rotating amber beacon (faster + brighter at high risk)
  beaconGroup.rotation.y=t*0.060;
  const bPulse=0.5+0.5*Math.sin(t*0.10);
  beaconLight.intensity=(PRB>=30?3.2:1.5)*bPulse;
  domeMesh.material.emissiveIntensity=0.15+0.50*bPulse;
  // Window god ray gentle cloud flicker
  winRayGroup.children.forEach((m,mi)=>{
    if(m.material&&m.material.opacity!==undefined&&!m.isPoints){
      m.material.opacity=0.018+0.012*Math.sin(t*0.007+mi*0.8);
    }
  });
  // Sodium lamp shaft industrial flicker (power fluctuation)
  lampVolGroup.children.forEach((m,mi)=>{
    if(m.isSprite){m.material.opacity=(mi%2===0?0.88:0.55)*(0.82+0.20*Math.sin(t*0.07+mi*1.2));}
    else if(m.material&&m.material.opacity!==undefined){
      m.material.opacity*=(0.90+0.12*Math.sin(t*0.05+mi));
    }
  });
  const lerpK=0.06;
  sTheta+=(camTarget.theta-sTheta)*lerpK;
  sPhi+=(camTarget.phi-sPhi)*lerpK;
  sR.v+=(camTarget.r-sR.v)*lerpK;
  const sp=Math.sin(sPhi),cp=Math.cos(sPhi),st2=Math.sin(sTheta),ct2=Math.cos(sTheta);
  camera.position.set(gCenter.x+sR.v*sp*st2,gCenter.y+sR.v*cp,gCenter.z+sR.v*sp*ct2);
  camera.lookAt(gCenter);

  // Oscilloscope
  drawOsc();

  renderer.render(scene,camera);
}
animate();
</script></body></html>"""

    HTML=HTML.replace('CFG_PLACEHOLDER', cfg)
    return HTML



tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊  Prediction & Risk", "🧠  Explainability", "📈  Trends & History", "🔧  What-If Optimizer", "⚙️  3D Gear Model", "🗓  Maintenance Scheduler"])

# =====================================================================
# TAB 1
# =====================================================================
with tab1:

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Failure Probability</div>
            <div class='metric-value' style='color:{risk_color}'>{prob_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        badge = "<span class='badge-failure'>⚠ FAILURE DETECTED</span>" if prediction==1 \
                else "<span class='badge-ok'>✔ NO FAILURE</span>"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Model Prediction</div>
            <div style='margin-top:10px'>{badge}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Risk Classification</div>
            <div class='metric-value' style='font-size:18px;color:{risk_color}'>{risk_label}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Remaining Useful Life</div>
            <div class='metric-value' style='color:{rul_color};font-size:22px'>
                {rul_cycles:,.0f} <span style='font-size:13px;font-weight:500;color:#5A6A80'>cycles</span>
            </div>
            <div style='font-size:12px;color:#5A6A80;margin-top:4px;font-family:"DM Mono",monospace'>
                ≈ {rul_hours:.1f} hrs at {speed} RPM
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col_gauge, col_params = st.columns(2)

    with col_gauge:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("**Failure Risk Gauge**")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:0'>"
                    "Real-time failure probability based on current operational inputs.</p>",
                    unsafe_allow_html=True)

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            number={'suffix':"%",'font':{'size':38,'color':risk_color,'family':'DM Mono'}},
            gauge={
                'axis':{'range':[0,100],'tickcolor':'#5A6A80',
                        'tickfont':{'size':11,'color':'#5A6A80'}},
                'bar': {'color':risk_color,'thickness':0.22},
                'bgcolor':'#111620','borderwidth':0,
                'steps':[
                    {'range':[0, 30],'color':'#081A14'},
                    {'range':[30,55],'color':'#181208'},
                    {'range':[55,80],'color':'#1C1208'},
                    {'range':[80,100],'color':'#180810'},
                ],
                'threshold':{'line':{'color':risk_color,'width':3},
                             'thickness':0.75,'value':prob_pct}
            }
        ))
        fig_g.update_layout(height=310, margin=dict(t=20,b=10,l=20,r=20),
                             paper_bgcolor="#111620",
                             font={'color':'#A8B8CC','family':'DM Sans'})
        st.plotly_chart(fig_g, use_container_width=True)

        if prob_pct < 30:
            st.markdown("<div class='insight-box'>✅ <strong>Healthy Operation</strong> — All parameters within safe ranges. No action required.</div>", unsafe_allow_html=True)
        elif prob_pct < 55:
            st.markdown("<div class='insight-box-warn'>⚠ <strong>Elevated Risk</strong> — Some parameters approaching warning thresholds. Schedule inspection at next maintenance window.</div>", unsafe_allow_html=True)
        elif prob_pct < 80:
            st.markdown("<div class='insight-box-danger'>🔶 <strong>High Risk</strong> — Multiple parameters outside optimal range. Inspect within 24–48 hours.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='insight-box-danger'>🔴 <strong>Critical — Immediate Action</strong> — Failure probability very high. Reduce load and arrange emergency inspection now.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_params:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("**Current Operational Parameters**")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:0'>"
                    "Bar fill shows where each reading sits within its operating range.</p>",
                    unsafe_allow_html=True)

        for lbl, val, unit, (lo, hi) in zip(feature_labels, param_values, param_units, param_ranges):
            norm    = (val - lo) / (hi - lo)
            bar_col = "#16a34a" if norm < 0.4 else ("#d97706" if norm < 0.65 else "#dc2626")
            st.markdown(f"""
            <div style='margin-bottom:14px'>
                <div style='display:flex;justify-content:space-between;margin-bottom:5px'>
                    <span style='font-size:13px;color:#5A6A80;font-weight:500'>{lbl}</span>
                    <span style='font-size:13px;font-weight:600;color:#D6E4F0;
                                 font-family:"DM Mono",monospace'>{val} {unit}</span>
                </div>
                <div style='background:#e2e8f0;border-radius:4px;height:7px;overflow:hidden'>
                    <div style='width:{norm*100:.1f}%;height:100%;background:{bar_col};
                                border-radius:4px'></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ---- RUL Detail Card ----
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Remaining Useful Life (RUL) Estimate")
    st.markdown("""
    <p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:20px;line-height:1.6'>
        Derived from the SVM's failure probability using health score mapping:
        <code>RUL = (1 - P_failure) × Max Cycles</code>.
        Adjust <strong>Max Expected Cycles</strong> in the sidebar to match your gear's service spec.
        The ±10% band reflects estimation uncertainty.
    </p>
    """, unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown(f"""
        <div style='text-align:center;padding:16px 8px'>
            <div class='metric-label' style='text-align:center'>Health Score</div>
            <div style='font-size:32px;font-weight:700;color:{rul_color};
                        font-family:"DM Mono",monospace'>{health_score*100:.1f}%</div>
            <div style='font-size:12px;color:{rul_color};font-weight:600;margin-top:4px'>{rul_label}</div>
        </div>""", unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
        <div style='text-align:center;padding:16px 8px'>
            <div class='metric-label' style='text-align:center'>Est. Cycles Remaining</div>
            <div style='font-size:28px;font-weight:700;color:#D6E4F0;
                        font-family:"DM Mono",monospace'>{rul_cycles:,.0f}</div>
            <div style='font-size:12px;color:#5A6A80;margin-top:4px'>
                Range: {rul_low:,.0f} – {rul_high:,.0f}
            </div>
        </div>""", unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div style='text-align:center;padding:16px 8px'>
            <div class='metric-label' style='text-align:center'>Est. Time Remaining</div>
            <div style='font-size:28px;font-weight:700;color:#D6E4F0;
                        font-family:"DM Mono",monospace'>{rul_hours:.1f} <span style='font-size:14px'>hrs</span></div>
            <div style='font-size:12px;color:#5A6A80;margin-top:4px'>at {speed} RPM</div>
        </div>""", unsafe_allow_html=True)

    with r4:
        st.markdown(f"""
        <div style='text-align:center;padding:16px 8px'>
            <div class='metric-label' style='text-align:center'>Max Configured Cycles</div>
            <div style='font-size:28px;font-weight:700;color:#D6E4F0;
                        font-family:"DM Mono",monospace'>{max_cycles:,}</div>
            <div style='font-size:12px;color:#5A6A80;margin-top:4px'>service interval</div>
        </div>""", unsafe_allow_html=True)

    # RUL progress bar
    rul_pct = min(health_score * 100, 100)
    bar_segments = ""
    bar_col_rul = rul_color
    st.markdown(f"""
    <div style='margin-top:8px'>
        <div style='display:flex;justify-content:space-between;margin-bottom:6px'>
            <span style='font-size:12px;color:#5A6A80'>End of Life</span>
            <span style='font-size:12px;color:#5A6A80;font-weight:600'>
                Life Remaining: {rul_pct:.1f}%
            </span>
            <span style='font-size:12px;color:#5A6A80'>Full Life</span>
        </div>
        <div style='background:#e2e8f0;border-radius:6px;height:12px;overflow:hidden'>
            <div style='width:{rul_pct:.1f}%;height:100%;background:{bar_col_rul};
                        border-radius:6px;transition:width 0.4s ease'></div>
        </div>
        <div style='display:flex;justify-content:space-between;margin-top:4px'>
            <span style='font-size:11px;color:#5A6A80'>0</span>
            <span style='font-size:11px;color:#5A6A80'>{max_cycles:,} cycles</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # RUL insight
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if health_score > 0.70:
        st.markdown(f"""
        <div class='insight-box'>
        ✅ <strong>Gear is in good health.</strong> Estimated <strong>{rul_cycles:,.0f} cycles</strong>
        ({rul_hours:.1f} hrs) of useful life remaining before the next service interval.
        No immediate action required.
        </div>""", unsafe_allow_html=True)
    elif health_score > 0.45:
        st.markdown(f"""
        <div class='insight-box-warn'>
        ⚠ <strong>Health degrading.</strong> Approximately <strong>{rul_cycles:,.0f} cycles</strong>
        ({rul_hours:.1f} hrs) remaining. Plan maintenance within this window to avoid unplanned downtime.
        </div>""", unsafe_allow_html=True)
    elif health_score > 0.20:
        st.markdown(f"""
        <div class='insight-box-danger'>
        🔶 <strong>Critical health.</strong> Only <strong>{rul_cycles:,.0f} cycles</strong>
        ({rul_hours:.1f} hrs) estimated remaining. Schedule inspection immediately —
        do not wait for the next routine window.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='insight-box-danger'>
        🔴 <strong>End of life imminent.</strong> Estimated <strong>{rul_cycles:,.0f} cycles</strong>
        remaining ({rul_hours:.1f} hrs). Continued operation risks catastrophic failure.
        Stop and inspect now.
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_dl, _ = st.columns([1, 2])
    with col_dl:
        pdf_bytes = build_pdf_report()
        fname = f"gear_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        st.download_button(
            label="⬇  Download PDF Report",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )

# =====================================================================
# TAB 2 — EXPLAINABILITY
# =====================================================================
with tab2:

    # ---- SHAP ----
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### SHAP Feature Importance")
    st.markdown("""
    <p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:16px;line-height:1.65'>
        SHAP (SHapley Additive exPlanations) uses game theory to calculate exactly how much each
        parameter <em>contributed</em> to pushing the failure probability above or below the model's
        average baseline — computed using 100 representative samples from the training dataset.
        <strong style='color:#dc2626'>Red bars</strong> = parameter is increasing failure risk.
        <strong style='color:#16a34a'>Green bars</strong> = parameter is reducing failure risk.
        Bar length = strength of influence. <em>Updates as you adjust sliders.</em>
    </p>
    """, unsafe_allow_html=True)

    fig_s, ax_s = plt.subplots(figsize=(9, 4.5))
    bc_s   = ["#dc2626" if v > 0 else "#16a34a" for v in shap_df["Impact"]]
    bars_s = ax_s.barh(shap_df["Feature"], shap_df["Impact"],
                        color=bc_s, height=0.52, edgecolor="none", zorder=3)
    bar_label(ax_s, bars_s, shap_df["Impact"].tolist())
    ax_s.axvline(0, color="#5A6A80", linewidth=1.0, linestyle="--", zorder=2)
    style_ax(ax_s, fig_s)
    ax_s.set_xlabel("← Reduces Failure Risk    |    Increases Failure Risk →",
                    fontsize=10, color="#5A6A80", labelpad=10)
    plt.tight_layout()
    st.pyplot(fig_s)
    plt.close(fig_s)

    top_pos = shap_df.sort_values("Impact", ascending=False).iloc[0]
    top_neg = shap_df.sort_values("Impact").iloc[0]

    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown(f"""
        <div class='insight-box-danger'>
            <strong>⬆ Highest Risk Driver</strong><br>
            <strong>{top_pos['Feature']}</strong> ({top_pos['Value']} {top_pos['Unit']}) is the
            strongest factor pushing failure probability higher.
            SHAP value = <code>{top_pos['Impact']:+.4f}</code> above baseline.
            Consider reducing or closely monitoring this parameter.
        </div>""", unsafe_allow_html=True)
    with cs2:
        st.markdown(f"""
        <div class='insight-box'>
            <strong>⬇ Greatest Stabilising Factor</strong><br>
            <strong>{top_neg['Feature']}</strong> ({top_neg['Value']} {top_neg['Unit']}) is the
            strongest factor holding failure risk down.
            SHAP value = <code>{top_neg['Impact']:+.4f}</code> below baseline.
            Keeping this parameter at its current level is beneficial.
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ---- LIME ----
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### LIME — Local Decision Explanation")
    st.markdown("""
    <p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:16px;line-height:1.65'>
        LIME (Local Interpretable Model-agnostic Explanations) fits a simple linear model
        <em>around this exact operating point</em> to explain why the AI reached this specific
        prediction. Each bar is a condition observed in your current readings.
        <strong style='color:#dc2626'>Positive score</strong> = condition is pushing toward
        <strong>Failure</strong>.
        <strong style='color:#16a34a'>Negative score</strong> = pushing toward <strong>No Failure</strong>.
        <em>SHAP tells you feature importance globally; LIME explains this exact prediction locally.</em>
    </p>
    """, unsafe_allow_html=True)

    sorted_lime = sorted(lime_list, key=lambda x: x[1])
    l_feats = [f for f, _ in sorted_lime]
    l_vals  = [v for _, v in sorted_lime]

    fig_l, ax_l = plt.subplots(figsize=(9, 4.5))
    lc     = ["#dc2626" if v > 0 else "#16a34a" for v in l_vals]
    bars_l = ax_l.barh(l_feats, l_vals, color=lc, height=0.52, edgecolor="none", zorder=3)
    bar_label(ax_l, bars_l, l_vals)
    ax_l.axvline(0, color="#5A6A80", linewidth=1.0, linestyle="--", zorder=2)
    style_ax(ax_l, fig_l)
    ax_l.set_xlabel("← Toward No Failure    |    Toward Failure →",
                    fontsize=10, color="#5A6A80", labelpad=10)
    ax_l.tick_params(axis="y", labelsize=9, colors="#A8B8CC")
    plt.tight_layout()
    st.pyplot(fig_l)
    plt.close(fig_l)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px;font-weight:600;color:#D6E4F0;margin-bottom:8px'>"
                "Top 3 Conditions Driving This Prediction</p>", unsafe_allow_html=True)

    top3 = sorted(lime_list, key=lambda x: abs(x[1]), reverse=True)[:3]
    c1, c2, c3 = st.columns(3)
    for col, (feat, val) in zip([c1, c2, c3], top3):
        direction = "toward Failure" if val > 0 else "toward No Failure"
        box_cls   = "insight-box-danger" if val > 0 else "insight-box"
        col.markdown(f"""
        <div class='{box_cls}'>
            <div style='font-size:10px;text-transform:uppercase;letter-spacing:0.06em;
                        opacity:0.7;margin-bottom:6px'>Condition</div>
            <div style='font-size:13px;font-weight:600;margin-bottom:4px'>{feat}</div>
            <div style='font-size:12px'>Score <code>{val:+.4f}</code><br>{direction}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ---- Maintenance Recommendation ----
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Maintenance Recommendation")

    if prob_pct < 30:
        st.markdown("""
        <div class='insight-box'>
        ✅ <strong>No action required.</strong> The gear system is operating well within normal
        parameters. Continue your standard periodic monitoring schedule.
        </div>""", unsafe_allow_html=True)
    elif prob_pct < 60:
        st.markdown(f"""
        <div class='insight-box-warn'>
        ⚠ <strong>Schedule an inspection.</strong> Parameters suggest early-stage wear or thermal stress.<br><br>
        (1) Inspect lubrication levels and contamination.<br>
        (2) Check vibration — current reading is <strong>{vibration} mm/s</strong>.<br>
        (3) Verify gear mesh alignment.<br><br>
        <em>Action timeline: Within the next planned maintenance window.</em>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='insight-box-danger'>
        🔴 <strong>Immediate inspection required.</strong>
        Failure probability is critically high at <strong>{prob_pct:.1f}%</strong>.<br><br>
        (1) Reduce operational load immediately.<br>
        (2) Inspect gear teeth, bearings, and shaft.<br>
        (3) Check cooling — temperature at <strong>{temperature}°C</strong>.<br>
        (4) Check lubrication — vibration at <strong>{vibration} mm/s</strong> may indicate dry running.<br><br>
        <em>Do not defer: operating in this condition risks catastrophic failure.</em>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 3 — TRENDS & HISTORY  (Module 1)
# =====================================================================
with tab3:

    hist_df = load_history()

    # ── Top controls ──────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        st.markdown("### 📈 Historical Data Logger & Trend Analysis")
        st.markdown("""
        <p style='font-size:14px;color:#5A6A80;margin-top:-4px;line-height:1.65'>
            Readings are <strong>logged automatically</strong> whenever you change any slider or setting —
            no button needed. Each unique configuration is saved once to a local SQLite database.
            This tab shows time-series trends, threshold-breach counts, and the full log table.
        </p>""", unsafe_allow_html=True)
    with hdr_r:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        if st.button("🗑  Clear All History", use_container_width=True):
            clear_history()
            st.rerun()

    if hist_df.empty:
        st.markdown("""
        <div class='insight-box-warn' style='margin-top:12px'>
            ⚠ <strong>No data logged yet.</strong> Adjust any slider on the left —
            readings are saved automatically on every change.
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # ── Summary KPI strip ────────────────────────────────────────
        total_logs     = len(hist_df)
        failure_logs   = int((hist_df["prediction"] == 1).sum())
        avg_prob       = hist_df["fail_prob"].mean()
        avg_rul        = hist_df["rul_cycles"].mean()
        latest_risk    = hist_df.iloc[0]["risk_label"]
        latest_color   = {"LOW RISK":"#16a34a","MODERATE RISK":"#d97706",
                          "HIGH RISK":"#ea580c","CRITICAL RISK":"#dc2626"}.get(latest_risk,"#5A6A80")

        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Readings</div>
            <div class='metric-value'>{total_logs}</div>
        </div>""", unsafe_allow_html=True)
        k2.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Failure Events</div>
            <div class='metric-value' style='color:#dc2626'>{failure_logs}</div>
        </div>""", unsafe_allow_html=True)
        k3.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Avg Failure Probability</div>
            <div class='metric-value'>{avg_prob:.1f}%</div>
        </div>""", unsafe_allow_html=True)
        k4.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Avg RUL Remaining</div>
            <div class='metric-value' style='font-size:22px'>{avg_rul:,.0f} <span style='font-size:13px;color:#5A6A80'>cycles</span></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Failure Probability trend ────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### Failure Probability Over Time")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px'>Each point is one logged reading. Shaded bands mark risk thresholds.</p>", unsafe_allow_html=True)

        plot_df = hist_df.sort_values("timestamp").reset_index(drop=True)
        plot_df["reading_no"] = range(1, len(plot_df) + 1)

        fig_prob = go.Figure()

        # Risk zone bands
        fig_prob.add_hrect(y0=0,  y1=30,  fillcolor="#081A14", opacity=0.4, line_width=0)
        fig_prob.add_hrect(y0=30, y1=55,  fillcolor="#181208", opacity=0.4, line_width=0)
        fig_prob.add_hrect(y0=55, y1=80,  fillcolor="#1C1208", opacity=0.4, line_width=0)
        fig_prob.add_hrect(y0=80, y1=100, fillcolor="#180810", opacity=0.4, line_width=0)

        # Threshold lines
        for y, label, col in [(30,"Low/Moderate","#16a34a"),(55,"Moderate/High","#d97706"),
                               (80,"High/Critical","#dc2626")]:
            fig_prob.add_hline(y=y, line_dash="dot", line_color=col, line_width=1,
                               annotation_text=label, annotation_font_size=10,
                               annotation_font_color=col,
                               annotation_position="top right")

        # Colour each point by risk
        point_colors = []
        for v in plot_df["fail_prob"]:
            if v < 30:   point_colors.append("#16a34a")
            elif v < 55: point_colors.append("#d97706")
            elif v < 80: point_colors.append("#ea580c")
            else:        point_colors.append("#dc2626")

        fig_prob.add_trace(go.Scatter(
            x=plot_df["reading_no"], y=plot_df["fail_prob"],
            mode="lines+markers",
            line=dict(color="#00AEEF", width=2),
            marker=dict(color=point_colors, size=9, line=dict(color="#0B0E14", width=1.5)),
            text=plot_df["timestamp"].dt.strftime("%d %b %H:%M"),
            hovertemplate="<b>Reading #%{x}</b><br>%{text}<br>Failure Prob: %{y:.1f}%<extra></extra>",
            name="Failure Probability"
        ))

        fig_prob.update_layout(
            height=340, paper_bgcolor="#111620", plot_bgcolor="#0D1018",
            margin=dict(t=20, b=40, l=10, r=10),
            xaxis=dict(title="Reading #", color="#5A6A80", gridcolor="#182030",
                       tickfont=dict(color="#5A6A80")),
            yaxis=dict(title="Failure Probability (%)", range=[0,100],
                       color="#5A6A80", gridcolor="#182030", tickfont=dict(color="#5A6A80")),
            showlegend=False,
        )
        st.plotly_chart(fig_prob, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── RUL trend ────────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### Remaining Useful Life (RUL) Over Time")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px'>RUL in estimated cycles. Downward trend signals accelerating wear.</p>", unsafe_allow_html=True)

        rul_colors = []
        for v in plot_df["rul_cycles"]:
            pct = v / plot_df["rul_cycles"].max() if plot_df["rul_cycles"].max() > 0 else 0
            if pct > 0.70:   rul_colors.append("#16a34a")
            elif pct > 0.45: rul_colors.append("#d97706")
            elif pct > 0.20: rul_colors.append("#ea580c")
            else:            rul_colors.append("#dc2626")

        fig_rul = go.Figure()
        fig_rul.add_trace(go.Scatter(
            x=plot_df["reading_no"], y=plot_df["rul_cycles"],
            mode="lines+markers",
            line=dict(color="#00C896", width=2),
            marker=dict(color=rul_colors, size=9, line=dict(color="#0B0E14", width=1.5)),
            fill="tozeroy", fillcolor="rgba(0,200,150,0.07)",
            text=plot_df["timestamp"].dt.strftime("%d %b %H:%M"),
            hovertemplate="<b>Reading #%{x}</b><br>%{text}<br>RUL: %{y:,.0f} cycles<extra></extra>",
        ))
        fig_rul.update_layout(
            height=300, paper_bgcolor="#111620", plot_bgcolor="#0D1018",
            margin=dict(t=20, b=40, l=10, r=10),
            xaxis=dict(title="Reading #", color="#5A6A80", gridcolor="#182030",
                       tickfont=dict(color="#5A6A80")),
            yaxis=dict(title="RUL (cycles)", color="#5A6A80", gridcolor="#182030",
                       tickfont=dict(color="#5A6A80")),
            showlegend=False,
        )
        st.plotly_chart(fig_rul, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Sensor parameter trends ───────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### Sensor Parameter Trends")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px'>Select a parameter to view its trend. The red dashed line marks the danger-zone threshold.</p>", unsafe_allow_html=True)

        param_options = {
            "Speed (RPM)":        ("speed",       "RPM",  DANGER_THRESHOLDS["speed"],       "#00AEEF"),
            "Torque (Nm)":        ("torque",      "Nm",   DANGER_THRESHOLDS["torque"],      "#A78BFA"),
            "Vibration (mm/s)":   ("vibration",   "mm/s", DANGER_THRESHOLDS["vibration"],   "#F472B6"),
            "Temperature (°C)":   ("temperature", "°C",   DANGER_THRESHOLDS["temperature"], "#FB923C"),
            "Shock Load (g)":     ("shock",       "g",    DANGER_THRESHOLDS["shock"],       "#FACC15"),
            "Noise Level (dB)":   ("noise",       "dB",   DANGER_THRESHOLDS["noise"],       "#34D399"),
        }
        selected_param = st.selectbox("Parameter", list(param_options.keys()), label_visibility="collapsed")
        col_key, unit, danger_thresh, line_col = param_options[selected_param]

        fig_param = go.Figure()
        fig_param.add_hline(y=danger_thresh, line_dash="dash", line_color="#dc2626", line_width=1.5,
                            annotation_text=f"Danger threshold: {danger_thresh} {unit}",
                            annotation_font_color="#dc2626", annotation_font_size=10,
                            annotation_position="top right")
        breach_mask = plot_df[col_key] >= danger_thresh
        fig_param.add_trace(go.Scatter(
            x=plot_df["reading_no"], y=plot_df[col_key],
            mode="lines+markers",
            line=dict(color=line_col, width=2),
            marker=dict(
                color=["#dc2626" if b else line_col for b in breach_mask],
                size=9, line=dict(color="#0B0E14", width=1.5)
            ),
            text=plot_df["timestamp"].dt.strftime("%d %b %H:%M"),
            hovertemplate=f"<b>Reading #%{{x}}</b><br>%{{text}}<br>{selected_param}: %{{y}} {unit}<extra></extra>",
        ))
        fig_param.update_layout(
            height=300, paper_bgcolor="#111620", plot_bgcolor="#0D1018",
            margin=dict(t=20, b=40, l=10, r=10),
            xaxis=dict(title="Reading #", color="#5A6A80", gridcolor="#182030",
                       tickfont=dict(color="#5A6A80")),
            yaxis=dict(title=f"{selected_param}", color="#5A6A80", gridcolor="#182030",
                       tickfont=dict(color="#5A6A80")),
            showlegend=False,
        )
        st.plotly_chart(fig_param, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Threshold Breach Counter ─────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚠ Danger-Zone Breach Counter")
        st.markdown("""
        <p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>
            Number of logged readings where each parameter exceeded its danger threshold
            (top 25% of its operating range). High breach counts signal a systemic problem.
        </p>""", unsafe_allow_html=True)

        breach_data = []
        param_display = [
            ("Speed",       "speed",       "RPM",  "#00AEEF"),
            ("Torque",      "torque",      "Nm",   "#A78BFA"),
            ("Vibration",   "vibration",   "mm/s", "#F472B6"),
            ("Temperature", "temperature", "°C",   "#FB923C"),
            ("Shock Load",  "shock",       "g",    "#FACC15"),
            ("Noise Level", "noise",       "dB",   "#34D399"),
        ]
        for label, key, unit, color in param_display:
            thresh     = DANGER_THRESHOLDS[key]
            breaches   = int((hist_df[key] >= thresh).sum())
            breach_pct = breaches / total_logs * 100 if total_logs > 0 else 0
            breach_data.append({"label": label, "breaches": breaches,
                                 "pct": breach_pct, "color": color,
                                 "thresh": thresh, "unit": unit})

        fig_breach = go.Figure(go.Bar(
            x=[d["label"] for d in breach_data],
            y=[d["breaches"] for d in breach_data],
            marker_color=[d["color"] for d in breach_data],
            marker_line_color="#0B0E14",
            marker_line_width=1.5,
            text=[f"{d['breaches']} ({d['pct']:.0f}%)" for d in breach_data],
            textposition="outside",
            textfont=dict(color="#A8B8CC", size=11),
            hovertemplate="<b>%{x}</b><br>Breaches: %{y}<extra></extra>",
        ))
        fig_breach.update_layout(
            height=300, paper_bgcolor="#111620", plot_bgcolor="#0D1018",
            margin=dict(t=30, b=40, l=10, r=10),
            xaxis=dict(color="#5A6A80", gridcolor="#182030", tickfont=dict(color="#A8B8CC")),
            yaxis=dict(title="Breach Count", color="#5A6A80", gridcolor="#182030",
                       tickfont=dict(color="#5A6A80")),
            showlegend=False,
        )
        st.plotly_chart(fig_breach, use_container_width=True)

        # Breach insight callouts
        top_breach = max(breach_data, key=lambda d: d["breaches"])
        if top_breach["breaches"] > 0:
            st.markdown(f"""
            <div class='insight-box-danger'>
                🔴 <strong>{top_breach['label']}</strong> has the most danger-zone breaches —
                <strong>{top_breach['breaches']} readings</strong> ({top_breach['pct']:.0f}% of sessions)
                exceeded {top_breach['thresh']} {top_breach['unit']}.
                This parameter warrants priority attention.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='insight-box'>
                ✅ No danger-zone breaches recorded across any parameter so far.
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Risk Distribution Pie ────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        risk_col, session_col = st.columns(2)

        with risk_col:
            st.markdown("#### Risk Level Distribution")
            risk_counts = hist_df["risk_label"].value_counts().reset_index()
            risk_counts.columns = ["risk_label", "count"]
            risk_color_map = {
                "LOW RISK":      "#16a34a",
                "MODERATE RISK": "#d97706",
                "HIGH RISK":     "#ea580c",
                "CRITICAL RISK": "#dc2626",
            }
            fig_pie = go.Figure(go.Pie(
                labels=risk_counts["risk_label"],
                values=risk_counts["count"],
                marker_colors=[risk_color_map.get(r, "#5A6A80") for r in risk_counts["risk_label"]],
                hole=0.5,
                textfont=dict(color="#D6E4F0", size=12),
                hovertemplate="<b>%{label}</b><br>%{value} readings (%{percent})<extra></extra>",
            ))
            fig_pie.update_layout(
                height=280, paper_bgcolor="#111620",
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(font=dict(color="#A8B8CC"), bgcolor="rgba(0,0,0,0)"),
                showlegend=True,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with session_col:
            st.markdown("#### Gear Type Breakdown")
            gear_counts = hist_df["gear_type"].value_counts().reset_index()
            gear_counts.columns = ["gear_type", "count"]
            fig_gear = go.Figure(go.Bar(
                x=gear_counts["gear_type"],
                y=gear_counts["count"],
                marker_color=["#00AEEF","#A78BFA","#34D399"][:len(gear_counts)],
                marker_line_color="#0B0E14", marker_line_width=1.5,
                text=gear_counts["count"], textposition="outside",
                textfont=dict(color="#A8B8CC"),
                hovertemplate="<b>%{x}</b><br>%{y} readings<extra></extra>",
            ))
            fig_gear.update_layout(
                height=280, paper_bgcolor="#111620", plot_bgcolor="#0D1018",
                margin=dict(t=10, b=30, l=10, r=10),
                xaxis=dict(color="#5A6A80", tickfont=dict(color="#A8B8CC")),
                yaxis=dict(title="Count", color="#5A6A80", gridcolor="#182030",
                           tickfont=dict(color="#5A6A80")),
                showlegend=False,
            )
            st.plotly_chart(fig_gear, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Raw log table ────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 📋 Full Session Log")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:12px'>Complete record of every logged reading, newest first.</p>", unsafe_allow_html=True)

        display_df = hist_df.copy()
        display_df["timestamp"]   = display_df["timestamp"].dt.strftime("%d %b %Y  %H:%M:%S")
        display_df["fail_prob"]   = display_df["fail_prob"].map("{:.1f}%".format)
        display_df["health_score"]= display_df["health_score"].map("{:.1%}".format)
        display_df["rul_cycles"]  = display_df["rul_cycles"].map("{:,.0f}".format)
        display_df["rul_hours"]   = display_df["rul_hours"].map("{:.1f} hrs".format)
        display_df["prediction"]  = display_df["prediction"].map({1:"⚠ FAILURE", 0:"✔ OK"})

        display_df = display_df.rename(columns={
            "id":"#", "timestamp":"Timestamp", "gear_type":"Gear",
            "speed":"RPM", "torque":"Torque (Nm)", "vibration":"Vib (mm/s)",
            "temperature":"Temp (°C)", "shock":"Shock (g)", "noise":"Noise (dB)",
            "max_cycles":"Max Cycles", "fail_prob":"Fail Prob",
            "prediction":"Prediction", "risk_label":"Risk",
            "health_score":"Health", "rul_cycles":"RUL (cycles)", "rul_hours":"RUL (time)"
        }).drop(columns=["#"])

        st.dataframe(display_df, use_container_width=True, height=320)

        # CSV download
        csv_bytes = hist_df.to_csv(index=False).encode()
        st.download_button(
            label="⬇  Export Full Log as CSV",
            data=csv_bytes,
            file_name=f"gear_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=False,
        )
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 5 — WHAT-IF OPTIMIZER  (Module 3)
# =====================================================================
with tab3:

    # ── shared constants (mirror sidebar ranges exactly) ─────────────
    OPT_LABELS  = ["Speed", "Torque", "Vibration", "Temperature", "Shock Load", "Noise Level"]
    OPT_KEYS    = ["Speed_RPM", "Torque_Nm", "Vibration_mm_s", "Temperature_C", "Shock_Load_g", "Noise_dB"]
    OPT_UNITS   = ["RPM", "Nm", "mm/s", "°C", "g", "dB"]
    OPT_BOUNDS  = [(500, 3000), (50, 400), (0.5, 10.0), (30, 120), (0.1, 6.0), (50, 100)]
    # current live values straight from sidebar sliders (same variables Tab 1 uses)
    _live = [speed, torque, vibration, temperature, shock, noise]

    def _predict_prob(raw):
        df_in  = pd.DataFrame([raw], columns=OPT_KEYS)
        scaled = scaler.transform(df_in)
        return float(model.predict_proba(scaled)[0][1]) * 100

    # ─────────────────────────────────────────────────────────────────
    # HEADER  — same style as Tab 1 / Tab 4
    # ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### 🔧 What-If Optimizer — Safe Operating Zone Finder")
    st.markdown("""
    <p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:0;line-height:1.65'>
        Answers: <strong>"What is the minimum change to my current settings that brings failure
        probability below the target?"</strong><br>
        Lock the parameters you cannot change. The optimizer adjusts the free ones using
        Differential Evolution — a global search that avoids local minima.
        <em>Current sidebar values are used as the starting point.</em>
    </p>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # STEP 1 — KPIs + target slider
    # ─────────────────────────────────────────────────────────────────
    cur_prob = _predict_prob(_live)

    if cur_prob < 30:   _cp_color = "#16a34a"
    elif cur_prob < 55: _cp_color = "#d97706"
    elif cur_prob < 80: _cp_color = "#ea580c"
    else:               _cp_color = "#dc2626"

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Current Failure Probability</div>
        <div class='metric-value' style='color:{_cp_color}'>{cur_prob:.1f}%</div>
    </div>""", unsafe_allow_html=True)
    k2.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Health Score</div>
        <div class='metric-value' style='color:{rul_color}'>{health_score*100:.1f}%</div>
    </div>""", unsafe_allow_html=True)
    k3.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Risk Level</div>
        <div class='metric-value' style='font-size:18px;color:{_cp_color}'>{risk_label}</div>
    </div>""", unsafe_allow_html=True)
    k4.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>RUL Remaining</div>
        <div class='metric-value' style='font-size:22px'>{rul_cycles:,.0f}
            <span style='font-size:13px;font-weight:500;color:#5A6A80'>cycles</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # STEP 2 — Lock controls + target  (section-card)
    # ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Configure Optimization")
    st.markdown("""
    <p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:20px;line-height:1.65'>
        Set your target probability, then tick the parameters that are <strong>physically fixed</strong>
        (machine limits, process constraints). The optimizer will only adjust the unlocked ones.
    </p>""", unsafe_allow_html=True)

    cfg_l, cfg_r = st.columns([1, 2])
    with cfg_l:
        user_target = st.slider(
            "Target Failure Probability (%)", 5, 50, 30, step=5,
            help="Optimizer finds the nearest operating point below this threshold."
        )
        st.markdown(f"""
        <div style='margin-top:12px;padding:14px 18px;background:#0D1018;
                    border:1px solid #243048;border-radius:8px;text-align:center'>
            <div class='metric-label' style='text-align:center'>Gap to Close</div>
            <div style='font-size:26px;font-weight:700;color:#00AEEF;
                        font-family:"DM Mono",monospace'>
                {max(0, cur_prob - user_target):.1f}<span style='font-size:14px'>pp</span>
            </div>
            <div style='font-size:12px;color:#5A6A80;margin-top:2px'>
                {cur_prob:.1f}% → target {user_target}%
            </div>
        </div>""", unsafe_allow_html=True)

    with cfg_r:
        st.markdown("<p style='font-size:13px;font-weight:600;color:#D6E4F0;margin-bottom:10px'>Parameter Lock Configuration</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px;color:#5A6A80;margin-bottom:14px'>☑ Checked = <strong style='color:#E8394A'>LOCKED</strong> (fixed at current value) &nbsp;|&nbsp; Unchecked = <strong style='color:#00C896'>FREE</strong> (optimizer can adjust)</p>", unsafe_allow_html=True)

        lock_c = st.columns(3)
        locks  = {}
        lbl_key_pairs = list(zip(OPT_LABELS, OPT_KEYS))
        for i, (lbl, key) in enumerate(lbl_key_pairs):
            with lock_c[i % 3]:
                locked = st.checkbox(lbl, value=False, key=f"optlock_{key}")
                locks[key] = locked
                val_now = _live[i]
                unit    = OPT_UNITS[i]
                if locked:
                    st.markdown(f"<div style='font-size:11px;color:#E8394A;margin-top:-6px;margin-bottom:8px'>🔒 Fixed at {val_now} {unit}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-size:11px;color:#00C896;margin-top:-6px;margin-bottom:8px'>🟢 Free &nbsp;·&nbsp; now {val_now} {unit}</div>", unsafe_allow_html=True)

        free_n   = sum(1 for v in locks.values() if not v)
        locked_n = sum(1 for v in locks.values() if v)
        st.markdown(f"<p style='font-size:12px;color:#5A6A80;margin-top:4px'>"
                    f"<strong style='color:#00C896'>{free_n} free</strong> · "
                    f"<strong style='color:#E8394A'>{locked_n} locked</strong></p>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # SENSITIVITY PREVIEW — always visible, same chart style as Tab 4
    # ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Parameter Sensitivity")
    st.markdown("""
    <p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:16px;line-height:1.65'>
        How much does failure probability shift when each parameter is nudged ±5% of its range?
        High-leverage parameters are the most effective levers — consider leaving them <strong style='color:#00C896'>free</strong>.
    </p>""", unsafe_allow_html=True)

    sens_data = []
    for i, (lbl, key, unit, (lo, hi)) in enumerate(zip(OPT_LABELS, OPT_KEYS, OPT_UNITS, OPT_BOUNDS)):
        step   = (hi - lo) * 0.05
        base   = _live.copy()
        p_up   = base.copy(); p_up[i]  = min(hi, base[i] + step)
        p_dn   = base.copy(); p_dn[i]  = max(lo, base[i] - step)
        eff_up = _predict_prob(p_up) - cur_prob
        eff_dn = _predict_prob(p_dn) - cur_prob
        lev    = max(abs(eff_up), abs(eff_dn))
        sens_data.append(dict(label=lbl, leverage=lev, eff_up=eff_up, eff_dn=eff_dn,
                               unit=unit, locked=locks[key]))

    sens_data.sort(key=lambda x: x["leverage"], reverse=True)

    # matplotlib bar chart — exactly like Tab 2 SHAP bars
    fig_sens, ax_sens = plt.subplots(figsize=(9, 3.8))
    s_labels = [d["label"] for d in sens_data]
    s_vals   = [d["leverage"] for d in sens_data]
    s_colors = ["#5A6A80" if d["locked"] else
                ("#dc2626" if d["leverage"] > 5 else
                 "#d97706" if d["leverage"] > 2 else "#16a34a")
                for d in sens_data]
    bars_sens = ax_sens.barh(s_labels, s_vals, color=s_colors, height=0.52,
                              edgecolor="none", zorder=3)
    # value labels
    x_max  = max(s_vals) if s_vals else 1
    offset = x_max * 0.018 or 0.001
    for bar, val, d in zip(bars_sens, s_vals, sens_data):
        suffix = " (locked)" if d["locked"] else f" pp / 5% move"
        ax_sens.text(val + offset, bar.get_y() + bar.get_height() / 2,
                     f"{val:.2f}{suffix}", va="center", ha="left",
                     fontsize=9, color="#5A6A80", fontfamily="monospace")
    ax_sens.axvline(0, color="#5A6A80", linewidth=0.8, linestyle="--", zorder=2)
    style_ax(ax_sens, fig_sens)
    ax_sens.set_xlabel("Max probability change per ±5% of parameter range (percentage points)",
                       fontsize=10, color="#5A6A80", labelpad=8)
    plt.tight_layout()
    st.pyplot(fig_sens)
    plt.close(fig_sens)

    # top insight — same pattern as SHAP insight boxes
    top_s = sens_data[0]
    if top_s["locked"]:
        st.markdown(f"<div class='insight-box-warn'>⚠ <strong>Highest-leverage parameter ({top_s['label']}) is locked.</strong> Unlocking it would give the optimizer the most powerful lever to reduce risk.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='insight-box-warn'>⚡ <strong>{top_s['label']}</strong> is the most influential free parameter — a ±5% change shifts failure probability by up to <strong>{top_s['leverage']:.2f} pp</strong>. The optimizer will prioritise this lever.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # RUN BUTTON
    # ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### Run Optimizer")

    if cur_prob < user_target:
        st.markdown(f"""
        <div class='insight-box'>
            ✅ <strong>Already safe.</strong> Current failure probability ({cur_prob:.1f}%) is
            already below your target of {user_target}%. Lower the target slider or raise
            a parameter in the sidebar to see the optimizer work.
        </div>""", unsafe_allow_html=True)
        run_btn = False
    else:
        st.markdown(f"""
        <p style='font-size:13px;color:#5A6A80;margin-top:0;margin-bottom:16px'>
            Current probability is <strong style='color:{_cp_color}'>{cur_prob:.1f}%</strong>.
            The optimizer will search for the nearest safe operating point below
            <strong style='color:#00C896'>{user_target}%</strong>
            by adjusting the <strong>{free_n} free</strong> parameter(s).
        </p>""", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            run_btn = st.button("⚡  Find Safe Operating Point", use_container_width=True)
        with btn_col2:
            if st.button("✕  Clear Result", use_container_width=True):
                st.session_state.opt_result = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # OPTIMIZER ENGINE + RESULTS
    # ─────────────────────────────────────────────────────────────────
    @st.cache_data(show_spinner="Running global optimizer — this takes a few seconds…")
    def _run_optimizer(live_tuple, locks_tuple, target, bounds_tuple):
        live_arr   = np.array(live_tuple, dtype=float)
        locked_arr = np.array(locks_tuple, dtype=bool)
        bounds_arr = np.array(bounds_tuple)
        ranges     = bounds_arr[:, 1] - bounds_arr[:, 0]
        free_idx   = np.where(~locked_arr)[0]
        free_bnds  = [tuple(bounds_arr[i]) for i in free_idx]

        if len(free_idx) == 0:
            return None, None, "All parameters are locked — unlock at least one."

        def objective(x):
            cand             = live_arr.copy()
            cand[free_idx]   = x
            prob             = _predict_prob(cand.tolist())
            prob_pen         = max(0.0, prob - target) ** 2
            norm_chg         = (x - live_arr[free_idx]) / ranges[free_idx]
            chg_pen          = 5.0 * float(np.sum(norm_chg ** 2))
            return prob_pen + chg_pen

        res      = differential_evolution(objective, bounds=free_bnds, seed=42,
                                          maxiter=400, tol=1e-5, popsize=14,
                                          mutation=(0.5, 1.2), recombination=0.9,
                                          polish=True)
        opt_arr  = live_arr.copy()
        opt_arr[free_idx] = res.x
        opt_prob = _predict_prob(opt_arr.tolist())
        return opt_arr.tolist(), opt_prob, None

    # ── Persist result in session_state so it survives slider reruns ──
    if "opt_result" not in st.session_state:
        st.session_state.opt_result = None   # {opt_vals, opt_prob, live_snapshot, target_snapshot}

    if run_btn and cur_prob >= user_target:
        if free_n == 0:
            st.markdown("<div class='insight-box-danger'>🔴 All parameters are locked. Unlock at least one so the optimizer has something to adjust.</div>", unsafe_allow_html=True)
        else:
            with st.spinner("Searching for safe operating point…"):
                locks_tuple = tuple(locks[k] for k in OPT_KEYS)
                opt_vals_r, opt_prob_r, err = _run_optimizer(
                    tuple(_live), locks_tuple, user_target, tuple(map(tuple, OPT_BOUNDS))
                )
            if err:
                st.error(err)
            else:
                # Save result + the exact slider snapshot it was computed from
                st.session_state.opt_result = dict(
                    opt_vals        = opt_vals_r,
                    opt_prob        = opt_prob_r,
                    live_snapshot   = list(_live),
                    target_snapshot = user_target,
                    locks_snapshot  = dict(locks),
                )

    # ── Clear stored result if the user presses Run again with new settings ──
    # (handled automatically: st.cache_data invalidates when args change)

    # ── Render results from session_state if available ────────────────
    if st.session_state.opt_result is not None:
        _r        = st.session_state.opt_result
        opt_vals  = _r["opt_vals"]
        opt_prob  = _r["opt_prob"]
        _before   = _r["live_snapshot"]   # the values at the time of optimization
        _tgt      = _r["target_snapshot"]
        _lks      = _r["locks_snapshot"]
        achieved  = opt_prob < _tgt
        reduction = _r["live_snapshot"]   # re-compute below
        # re-compute before prob from snapshot (not live, since sliders may have changed)
        before_prob = _predict_prob(_before)
        reduction   = before_prob - opt_prob

        # show a notice if live sliders have drifted from the snapshot
        if list(_live) != _before:
            st.markdown("""
            <div class='insight-box-warn' style='margin-bottom:4px'>
                ⚠ <strong>Sidebar values have changed since this result was computed.</strong>
                The results below still show the optimized point from the previous run.
                Press <em>Find Safe Operating Point</em> again to recompute with current values.
            </div>""", unsafe_allow_html=True)

        if True:  # always show block (replaces old `else:` indent)
            achieved = opt_prob < _tgt
            reduction = before_prob - opt_prob

            # ── Before / After KPI row ────────────────────────────
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown(f"### {'✅ Target Achieved' if achieved else '⚠ Best Reachable Point'}")
            st.markdown(f"""
            <p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:20px;line-height:1.65'>
                {'Failure probability successfully reduced below target.' if achieved else
                 'The optimizer reached the best possible point with these locks — target was not fully achievable.'}
                Failure probability reduced by <strong style='color:#00C896'>{reduction:.1f} percentage points</strong>.
            </p>""", unsafe_allow_html=True)

            res_a, res_b, res_c, res_d = st.columns(4)
            opt_color = "#16a34a" if opt_prob < 30 else ("#d97706" if opt_prob < 55 else ("#ea580c" if opt_prob < 80 else "#dc2626"))
            opt_hs    = 1.0 - opt_prob / 100
            opt_rul   = max(0, opt_hs * max_cycles)

            res_a.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Before (Current)</div>
                <div class='metric-value' style='color:{_cp_color}'>{cur_prob:.1f}%</div>
                <div style='font-size:11px;color:#5A6A80;margin-top:4px'>{risk_label}</div>
            </div>""", unsafe_allow_html=True)
            res_b.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>After (Optimized)</div>
                <div class='metric-value' style='color:{opt_color}'>{opt_prob:.1f}%</div>
                <div style='font-size:11px;color:#00C896;margin-top:4px'>
                    {"TARGET MET ✅" if achieved else "BEST POSSIBLE"}
                </div>
            </div>""", unsafe_allow_html=True)
            res_c.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Probability Reduction</div>
                <div class='metric-value' style='color:#00C896'>-{reduction:.1f}<span style='font-size:14px'>pp</span></div>
            </div>""", unsafe_allow_html=True)
            res_d.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>RUL After Optimization</div>
                <div class='metric-value' style='font-size:22px'>{opt_rul:,.0f}
                    <span style='font-size:13px;font-weight:500;color:#5A6A80'>cycles</span>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Recommended changes ───────────────────────────────
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("### Recommended Parameter Changes")
            st.markdown("<p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:16px;line-height:1.65'>Minimum adjustments to reach the safe operating zone. Parameters are sorted by magnitude of change required.</p>", unsafe_allow_html=True)

            changes = []
            for i, (lbl, key, unit, (lo, hi)) in enumerate(zip(OPT_LABELS, OPT_KEYS, OPT_UNITS, OPT_BOUNDS)):
                before  = _live[i]
                after   = opt_vals[i]
                delta   = after - before
                pct_rng = abs(delta) / (hi - lo) * 100
                changes.append(dict(label=lbl, unit=unit, before=before, after=after,
                                    delta=delta, pct_rng=pct_rng, locked=locks[key]))
            changes.sort(key=lambda x: abs(x["delta"]) if not x["locked"] else -1, reverse=True)

            for ch in changes:
                if ch["locked"]:
                    st.markdown(f"""
                    <div style='background:#111620;border-left:3px solid #243048;
                                border-radius:0 8px 8px 0;padding:10px 18px;margin:6px 0;
                                font-size:13px;color:#5A6A80'>
                        🔒 <strong>{ch['label']}</strong> — fixed at
                        <strong style='color:#D6E4F0'>{ch['before']} {ch['unit']}</strong>
                        &nbsp;(locked)
                    </div>""", unsafe_allow_html=True)
                elif abs(ch["delta"]) < 0.01:
                    st.markdown(f"""
                    <div style='background:#111620;border-left:3px solid #243048;
                                border-radius:0 8px 8px 0;padding:10px 18px;margin:6px 0;
                                font-size:13px;color:#5A6A80'>
                        ➖ <strong>{ch['label']}</strong> — no change needed
                        &nbsp;·&nbsp; stays at <strong style='color:#D6E4F0'>{ch['before']} {ch['unit']}</strong>
                    </div>""", unsafe_allow_html=True)
                elif ch["delta"] < 0:
                    st.markdown(f"""
                    <div style='background:#0A1C18;border-left:3px solid #00C896;
                                border-radius:0 8px 8px 0;padding:10px 18px;margin:6px 0;
                                font-size:13px;color:#5EEBC8'>
                        ⬇ <strong>{ch['label']}</strong> — reduce from
                        <strong style='color:#D6E4F0'>{ch['before']} → {ch['after']:.2f} {ch['unit']}</strong>
                        &nbsp;·&nbsp; decrease by <strong>{abs(ch['delta']):.2f} {ch['unit']}</strong>
                        &nbsp;<span style='color:#5A6A80'>({ch['pct_rng']:.1f}% of range)</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:#1E0D11;border-left:3px solid #E8394A;
                                border-radius:0 8px 8px 0;padding:10px 18px;margin:6px 0;
                                font-size:13px;color:#F0707A'>
                        ⬆ <strong>{ch['label']}</strong> — increase from
                        <strong style='color:#D6E4F0'>{ch['before']} → {ch['after']:.2f} {ch['unit']}</strong>
                        &nbsp;·&nbsp; increase by <strong>{abs(ch['delta']):.2f} {ch['unit']}</strong>
                        &nbsp;<span style='color:#5A6A80'>({ch['pct_rng']:.1f}% of range)</span>
                    </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Before / After bar chart — same style as Tab 1 param bars ──
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("### Before vs After — Parameter Comparison")
            st.markdown("<p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:16px;line-height:1.65'>Bar fill shows where each parameter sits within its operating range. Values beyond 75% of range enter the danger zone (red line).</p>", unsafe_allow_html=True)

            cmp_l, cmp_r = st.columns(2)
            norm_before = [(v - lo) / (hi - lo) for v, (lo, hi) in zip(_live, OPT_BOUNDS)]
            norm_after  = [(v - lo) / (hi - lo) for v, (lo, hi) in zip(opt_vals, OPT_BOUNDS)]

            for col, norms, vals, title in [
                (cmp_l, norm_before, _live,    f"**Before** — {cur_prob:.1f}% probability"),
                (cmp_r, norm_after,  opt_vals, f"**After** — {opt_prob:.1f}% probability"),
            ]:
                with col:
                    st.markdown(title)
                    for lbl, val, unit, norm in zip(OPT_LABELS, vals, OPT_UNITS, norms):
                        bar_col = "#16a34a" if norm < 0.4 else ("#d97706" if norm < 0.65 else "#dc2626")
                        st.markdown(f"""
                        <div style='margin-bottom:12px'>
                            <div style='display:flex;justify-content:space-between;margin-bottom:5px'>
                                <span style='font-size:13px;color:#5A6A80;font-weight:500'>{lbl}</span>
                                <span style='font-size:13px;font-weight:600;color:#D6E4F0;
                                             font-family:"DM Mono",monospace'>{val:.1f} {unit}</span>
                            </div>
                            <div style='background:#182030;border-radius:4px;height:7px;overflow:hidden'>
                                <div style='width:{min(norm*100,100):.1f}%;height:100%;
                                            background:{bar_col};border-radius:4px'></div>
                            </div>
                        </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Radar chart ───────────────────────────────────────
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("### Operating Profile — Radar View")
            st.markdown("<p style='font-size:14px;color:#5A6A80;margin-top:-4px;margin-bottom:16px;line-height:1.65'>Smaller polygon = safer operating profile. Amber ring marks the 75% danger threshold across all parameters.</p>", unsafe_allow_html=True)

            theta    = OPT_LABELS + [OPT_LABELS[0]]
            r_before = norm_before + [norm_before[0]]
            r_after  = norm_after  + [norm_after[0]]

            fig_rad = go.Figure()
            fig_rad.add_trace(go.Scatterpolar(
                r=r_before, theta=theta, fill="toself", name="Before",
                line=dict(color="#dc2626", width=2),
                fillcolor="rgba(220,38,38,0.12)",
                hovertemplate="%{theta}: %{r:.0%}<extra>Before</extra>",
            ))
            fig_rad.add_trace(go.Scatterpolar(
                r=r_after, theta=theta, fill="toself", name="After (Optimized)",
                line=dict(color="#00C896", width=2),
                fillcolor="rgba(0,200,150,0.15)",
                hovertemplate="%{theta}: %{r:.0%}<extra>After</extra>",
            ))
            fig_rad.add_trace(go.Scatterpolar(
                r=[0.75] * len(theta), theta=theta, mode="lines",
                line=dict(color="#d97706", width=1.5, dash="dot"),
                name="Danger Threshold (75%)",
                hoverinfo="skip",
            ))
            fig_rad.update_layout(
                polar=dict(
                    bgcolor="#0D1018",
                    radialaxis=dict(
                        visible=True, range=[0, 1],
                        tickvals=[0.25, 0.5, 0.75, 1.0],
                        ticktext=["25%", "50%", "75%", "100%"],
                        tickfont=dict(color="#5A6A80", size=9),
                        gridcolor="#182030", linecolor="#243048",
                    ),
                    angularaxis=dict(
                        tickfont=dict(color="#A8B8CC", size=11),
                        gridcolor="#182030", linecolor="#243048",
                    ),
                ),
                paper_bgcolor="#111620",
                height=420,
                margin=dict(t=30, b=30, l=40, r=40),
                legend=dict(
                    font=dict(color="#A8B8CC", size=12),
                    bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=-0.15, x=0.2
                ),
                font=dict(color="#A8B8CC", family="DM Sans"),
            )
            st.plotly_chart(fig_rad, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)


# =====================================================================
# TAB 6 — 3D Gear Model  (Digital Twin Edition)
# =====================================================================
with tab3:
    _nth = {"Spur Gear A":18,"Spur Gear B":24,"Spur Gear C":32}.get(gear_type,24)
    _fw  = round(0.25+(torque-50)/350*0.55,2)
    _effects = []
    if shock > 2:           _effects.append(("⚡","SPARKS","#F5A623"))
    if temperature > 60:    _effects.append(("🌡","HEAT","#FB923C"))
    if health_score < 0.45: _effects.append(("💨","SMOKE","#7A8DA0"))
    if vibration > 5:       _effects.append(("〰","VIBE","#A78BFA"))
    if health_score < 0.2:  _effects.append(("🔴","DEBRIS","#E8394A"))
    if not _effects:        _effects.append(("✅","CLEAN","#00C896"))

    # Computed gear specs
    _pitch_vel = round(3.14159*0.22*_nth*speed/60/1000, 3)
    _mesh_rate  = round(speed*_nth/60, 1)
    _module     = 0.22
    _pitch_dia  = round(_module*_nth, 2)
    _pressure_a = 20

    # Status bar
    effects_html = " &nbsp;&nbsp; ".join(
        f"<span style='color:{c}'>{ico} {lbl}</span>"
        for ico,lbl,c in _effects
    )
    st.markdown(f"""
    <div style='display:flex;align-items:center;justify-content:space-between;
                padding:12px 20px;background:linear-gradient(135deg,#04070D,#080D18);
                border:1px solid #152030;border-radius:12px 12px 0 0;margin-bottom:0;
                box-shadow:0 2px 0 rgba(0,174,239,.05)'>
      <div style='display:flex;align-items:center;gap:12px'>
        <div style='background:linear-gradient(135deg,#005A90,#00AEEF);border-radius:8px;
                    padding:8px 11px;font-size:18px;line-height:1;
                    box-shadow:0 0 14px rgba(0,174,239,.3)'>⚙️</div>
        <div>
          <div style='font-size:13px;font-weight:700;color:#D6E4F0;letter-spacing:.02em'>
            Digital Twin · Live 3D Simulation</div>
          <div style='font-size:10px;color:#374A60;margin-top:2px;letter-spacing:.04em'>
            Involute spur gear · Real-time parameter coupling · Condition-reactive effects</div>
        </div>
      </div>
      <div style='display:flex;gap:28px;align-items:center'>
        <div>
          <div style='font-size:8px;color:#374A60;text-transform:uppercase;letter-spacing:.12em'>Active Effects</div>
          <div style='font-size:11px;font-weight:700;margin-top:3px'>{effects_html}</div>
        </div>
        <div style='border-left:1px solid #152030;padding-left:24px'>
          <div style='font-size:8px;color:#374A60;text-transform:uppercase;letter-spacing:.12em'>Gear Spec</div>
          <div style='font-size:11px;font-weight:700;color:#D6E4F0;font-family:"DM Mono",monospace;margin-top:3px'>
            {gear_type} &nbsp;·&nbsp; {_nth}T &nbsp;·&nbsp; ⌀{_pitch_dia}mm &nbsp;·&nbsp; {_fw}m face</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    gear_html = create_gear_html(
        speed=speed, torque=torque, vibration=vibration,
        temperature=temperature, shock=shock, noise_db=noise,
        health_score=health_score, prob_pct=prob_pct,
        risk_color=risk_color, risk_label=risk_label, gear_type=gear_type,
    )
    components.html(gear_html, height=700, scrolling=False)

    # ── Gear spec cards row ───────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols_spec = st.columns(6)
    spec_items = [
        ("⚙","Speed","RPM",f"{speed}","Gear rotation rate","#00AEEF"),
        ("📐","Torque","Nm",f"{torque}","Applied torque — sets face width","#A78BFA"),
        ("〰","Vibration","mm/s",f"{vibration:.1f}","Orbital wobble amplitude","#F472B6"),
        ("🌡","Temperature","°C",f"{temperature}","Thermal glow + heat shimmer","#FB923C"),
        ("⚡","Shock","g",f"{shock:.1f}","Spark emission intensity","#FACC15"),
        ("🩺","Health","%",f"{health_score*100:.1f}","Ring colour + smoke + debris","#34D399"),
    ]
    for col,(icon,lbl,unit,val,tip,color) in zip(cols_spec, spec_items):
        with col:
            st.markdown(f"""
            <div style='background:#04080F;border:1px solid #0E1C2C;border-radius:9px;
                        padding:10px 10px;text-align:center;border-top:2px solid {color}22'>
              <div style='font-size:16px;margin-bottom:4px'>{icon}</div>
              <div style='font-size:10px;font-weight:700;color:#D6E4F0'>{lbl}</div>
              <div style='font-size:13px;font-weight:800;color:{color};
                          font-family:"DM Mono",monospace;margin:3px 0'>{val}<span style='font-size:9px;color:#374A60;font-weight:400'> {unit}</span></div>
              <div style='font-size:8px;color:#2A3A4C;line-height:1.4;margin-top:2px'>{tip}</div>
            </div>""", unsafe_allow_html=True)

    # ── Gear engineering metrics ───────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### ⚙ Gear Engineering Metrics")
    st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>Derived mechanical specifications calculated from the current parameter set.</p>", unsafe_allow_html=True)

    mc1,mc2,mc3,mc4,mc5,mc6 = st.columns(6)
    mets = [
        ("Pitch Diameter",f"{_pitch_dia} mm","D = m × N"),
        ("Pitch Velocity",f"{_pitch_vel} m/s","v = π·D·n/60"),
        ("Mesh Rate",f"{_mesh_rate} t/s","f = n·N/60"),
        ("Module",f"{_module} mm","Tooth size unit"),
        ("Pressure Angle",f"{_pressure_a}°","Involute profile"),
        ("Gear Ratio",f"{round(_nth/max(1,round(_nth*0.65)),2)}:1","N₁/N₂"),
    ]
    for col,(lbl,val,formula) in zip([mc1,mc2,mc3,mc4,mc5,mc6], mets):
        with col:
            st.markdown(f"""
            <div style='text-align:center;padding:12px 8px;background:#080E18;
                        border:1px solid #0E1C2C;border-radius:8px'>
              <div style='font-size:8px;color:#374A60;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px'>{lbl}</div>
              <div style='font-size:14px;font-weight:700;color:#D6E4F0;font-family:"DM Mono",monospace'>{val}</div>
              <div style='font-size:8px;color:#1E2D45;margin-top:3px'>{formula}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 7 — MAINTENANCE SCHEDULER  (Enhanced Edition)
# =====================================================================
with tab3:

    # ── session state init ─────────────────────────────────────────────
    if "sched_tasks"      not in st.session_state: st.session_state.sched_tasks      = []
    if "sched_generated"  not in st.session_state: st.session_state.sched_generated  = False
    if "task_done"        not in st.session_state: st.session_state.task_done        = {}
    if "sched_start"      not in st.session_state: st.session_state.sched_start      = datetime.now().date()

    # ── URGENCY BANNER ─────────────────────────────────────────────────
    if prob_pct >= 80:
        banner_bg,banner_brd,banner_col,banner_icon,banner_title = "#1E0D11","#E8394A","#E8394A","🚨","CRITICAL — EMERGENCY MAINTENANCE REQUIRED"
        banner_body = f"Failure probability at <strong>{prob_pct:.1f}%</strong>. Estimated <strong>{rul_hours:.1f} hrs</strong> remaining. Do not defer — action required immediately."
    elif prob_pct >= 55:
        banner_bg,banner_brd,banner_col,banner_icon,banner_title = "#1C1608","#F5A623","#F5A623","⚠️","HIGH RISK — Schedule inspection this week"
        banner_body = f"Failure probability at <strong>{prob_pct:.1f}%</strong>. Estimated <strong>{rul_hours:.1f} hrs</strong> remaining. Plan maintenance within 24–48 hours."
    else:
        banner_bg,banner_brd,banner_col,banner_icon,banner_title = "#0A1C18","#00C896","#00C896","✅","NOMINAL — Routine maintenance window applies"
        banner_body = f"Failure probability at <strong>{prob_pct:.1f}%</strong>. Estimated <strong>{rul_hours:.1f} hrs</strong> remaining. Schedule next inspection before <strong>{rul_cycles:,.0f} cycles</strong>."

    st.markdown(f"""
    <div style='background:{banner_bg};border:1px solid {banner_brd};border-radius:12px;
                padding:16px 22px;margin-bottom:20px;display:flex;align-items:center;gap:16px;
                box-shadow:0 0 0 1px {banner_brd}18,0 4px 20px rgba(0,0,0,.5)'>
      <div style='font-size:30px;flex-shrink:0'>{banner_icon}</div>
      <div style='flex:1'>
        <div style='font-size:13px;font-weight:800;color:{banner_col};letter-spacing:.02em'>{banner_title}</div>
        <div style='font-size:12px;color:{banner_col};opacity:.75;margin-top:4px;line-height:1.6'>{banner_body}</div>
      </div>
      <div style='text-align:right;flex-shrink:0'>
        <div style='font-size:8px;color:#374A60;text-transform:uppercase;letter-spacing:.1em'>Maintenance Score</div>
        <div style='font-size:28px;font-weight:800;color:{banner_col};font-family:"DM Mono",monospace'>{max(0,min(100,health_score*100)):.0f}</div>
        <div style='font-size:9px;color:#374A60'>/100</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── CONFIGURATION ─────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Schedule Configuration")
    st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:20px'>Set operational parameters, crew availability and cost baseline to generate the optimal maintenance plan.</p>", unsafe_allow_html=True)

    cfg_a, cfg_b, cfg_c = st.columns(3)
    with cfg_a:
        st.markdown("**📅 Planning Horizon**")
        sched_start_date = st.date_input("Schedule Start Date", value=datetime.now().date(), key="ms_start")
        horizon_weeks    = st.slider("Planning Horizon (weeks)", 1, 12, 4, key="ms_horizon")
        shifts_per_day   = st.selectbox("Shifts per Day", [1, 2, 3], index=1, key="ms_shifts")
        hours_per_shift  = st.selectbox("Hours per Shift", [6, 8, 10, 12], index=1, key="ms_hrs")

    with cfg_b:
        st.markdown("**👷 Crew Availability**")
        crew_size     = st.slider("Maintenance Crew Size", 1, 8, 2, key="ms_crew")
        work_days     = st.multiselect("Working Days", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                                        default=["Mon","Tue","Wed","Thu","Fri"], key="ms_days")
        blackout_note = st.text_input("Blackout periods (note)", placeholder="e.g. Public holiday 15 Dec", key="ms_blackout")
        mttr_hours    = st.slider("MTTR — Mean Time to Repair (hrs)", 1, 24, 4, key="ms_mttr")

    with cfg_c:
        st.markdown("**💰 Cost Parameters**")
        downtime_cost_hr   = st.number_input("Unplanned Downtime ($/hr)",   value=2500,  step=100, key="ms_dtcost")
        planned_maint_cost = st.number_input("Planned Maintenance Cost ($)", value=800,   step=50,  key="ms_pmcost")
        emergency_mult     = st.number_input("Emergency Multiplier",         value=3.5,   step=0.5, key="ms_emult")
        part_cost          = st.number_input("Spare Parts Cost ($)",         value=350,   step=50,  key="ms_parts")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── GENERATE BUTTON ────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### 🤖 AI Schedule Generator")
    st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>Generates prioritised task list with urgency windows, crew allocation, and cost breakdown based on live sensor readings and failure probability.</p>", unsafe_allow_html=True)

    if st.button("⚡  Generate Maintenance Schedule", key="ms_gen", use_container_width=True):
        tasks = []
        _now  = datetime.combine(sched_start_date, datetime.min.time())
        if prob_pct >= 80:   urgency_days = 1
        elif prob_pct >= 55: urgency_days = 3
        elif prob_pct >= 30: urgency_days = 7
        else:                urgency_days = max(7, int(rul_hours/(shifts_per_day*hours_per_shift)))

        norm_spd = (speed-500)/2500; norm_trq = (torque-50)/350
        norm_vib = (vibration-0.5)/9.5; norm_tmp = (temperature-30)/90
        norm_shk = (shock-0.1)/5.9; norm_nse = (noise-50)/50

        def days_offset(base_days):
            target = _now + timedelta(days=max(0,base_days))
            day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            for _ in range(7):
                if day_names[target.weekday()] in work_days: break
                target += timedelta(days=1)
            return target

        tasks.append({"id":"T01","task":"Full Visual Inspection","desc":"Inspect gear teeth for pitting, spalling, wear, and surface fatigue. Check for cracks at root fillets.","priority":"CRITICAL" if prob_pct>=55 else "HIGH","category":"Inspection","duration_hrs":1.5,"crew_needed":1,"due":days_offset(urgency_days),"trigger":f"Routine — Prob {prob_pct:.1f}%","cost":0,"impact":"HIGH"})
        tasks.append({"id":"T02","task":"Lubrication & Oil Analysis","desc":"Replace/top-up gear lubricant. Send oil sample for particle count and viscosity analysis.","priority":"HIGH" if norm_tmp>0.5 or norm_spd>0.6 else "MEDIUM","category":"Lubrication","duration_hrs":1.0,"crew_needed":1,"due":days_offset(urgency_days),"trigger":f"Temp {temperature}°C · Speed {speed} RPM","cost":120,"impact":"HIGH"})
        if norm_vib>0.4:
            tasks.append({"id":"T03","task":"Vibration Analysis & Balancing","desc":f"Vibration {vibration:.1f} mm/s exceeds threshold. Run FFT spectrum analysis and dynamic balance if required.","priority":"CRITICAL" if norm_vib>0.7 else "HIGH","category":"Vibration","duration_hrs":2.5,"crew_needed":2,"due":days_offset(min(urgency_days,2) if norm_vib>0.7 else urgency_days),"trigger":f"Vibration {vibration:.1f} mm/s — {norm_vib*100:.0f}% of range","cost":280,"impact":"CRITICAL"})
        if norm_tmp>0.45:
            tasks.append({"id":"T04","task":"Thermal Inspection & Cooling Check","desc":f"Temperature {temperature}°C. Inspect cooling system, heat exchangers, and oil cooler.","priority":"CRITICAL" if norm_tmp>0.75 else "HIGH","category":"Thermal","duration_hrs":2.0,"crew_needed":1,"due":days_offset(1 if norm_tmp>0.75 else urgency_days),"trigger":f"Temperature {temperature}°C — {norm_tmp*100:.0f}% of range","cost":200,"impact":"HIGH"})
        if norm_shk>0.45:
            tasks.append({"id":"T05","task":"Tooth Profile & Backlash Measurement","desc":f"Shock load {shock:.1f}g indicates impact loading. Measure backlash and inspect for chipped/fractured teeth.","priority":"CRITICAL" if norm_shk>0.7 else "HIGH","category":"Structural","duration_hrs":3.0,"crew_needed":2,"due":days_offset(1 if norm_shk>0.7 else urgency_days),"trigger":f"Shock {shock:.1f}g — {norm_shk*100:.0f}% of range","cost":150,"impact":"CRITICAL"})
        if norm_nse>0.5:
            tasks.append({"id":"T06","task":"Bearing Inspection & Replacement Check","desc":f"Noise {noise} dB may indicate bearing degradation. Inspect all bearings and measure clearances.","priority":"HIGH","category":"Bearings","duration_hrs":2.0,"crew_needed":2,"due":days_offset(urgency_days),"trigger":f"Noise {noise} dB — {norm_nse*100:.0f}% of range","cost":350,"impact":"HIGH"})
        if norm_trq>0.6:
            tasks.append({"id":"T07","task":"Torque Overload & Coupling Inspection","desc":f"Torque {torque} Nm elevated. Inspect shaft couplings, key-ways, and torque limiting devices.","priority":"HIGH" if norm_trq>0.75 else "MEDIUM","category":"Mechanical","duration_hrs":1.5,"crew_needed":1,"due":days_offset(urgency_days),"trigger":f"Torque {torque} Nm — {norm_trq*100:.0f}% of range","cost":100,"impact":"MEDIUM"})
        if health_score<0.45:
            tasks.append({"id":"T08","task":"Full Gear Overhaul — Replacement Assessment","desc":f"Health {health_score*100:.0f}% — significant degradation. Measure wear depth vs rejection limits. Prepare for replacement.","priority":"CRITICAL","category":"Overhaul","duration_hrs":8.0,"crew_needed":crew_size,"due":days_offset(urgency_days),"trigger":f"Health score {health_score*100:.0f}% below 45%","cost":part_cost+500,"impact":"CRITICAL"})
        tasks.append({"id":"T09","task":"Alignment Check & Shaft Runout","desc":"Use dial indicator to check shaft runout and gear mesh alignment.","priority":"MEDIUM","category":"Alignment","duration_hrs":1.5,"crew_needed":1,"due":days_offset(min(urgency_days*2,horizon_weeks*7)),"trigger":"Routine periodic check","cost":80,"impact":"MEDIUM"})
        tasks.append({"id":"T10","task":"Fastener Torque & Seal Inspection","desc":"Re-torque all housing fasteners. Inspect shaft seals for leakage.","priority":"LOW","category":"General","duration_hrs":1.0,"crew_needed":1,"due":days_offset(min(urgency_days*3,horizon_weeks*7)),"trigger":"Routine periodic check","cost":60,"impact":"LOW"})

        priority_order={"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3}
        tasks.sort(key=lambda x:(priority_order[x["priority"]],x["due"]))
        st.session_state.sched_tasks    = tasks
        st.session_state.sched_generated= True
        st.session_state.sched_start    = sched_start_date
        st.session_state.task_done      = {t["id"]:False for t in tasks}

    # ── RENDER SCHEDULE ────────────────────────────────────────────────
    if st.session_state.sched_generated and st.session_state.sched_tasks:
        tasks = st.session_state.sched_tasks

        total_cost    = sum(t["cost"] for t in tasks)+planned_maint_cost
        total_hrs     = sum(t["duration_hrs"] for t in tasks)
        n_critical    = sum(1 for t in tasks if t["priority"]=="CRITICAL")
        unplanned_est = downtime_cost_hr*mttr_hours*(prob_pct/100)*emergency_mult
        savings       = max(0,unplanned_est-total_cost)
        n_done        = sum(1 for tid,done in st.session_state.task_done.items() if done)
        pct_done      = n_done/len(tasks)*100 if tasks else 0

        st.markdown("</div>", unsafe_allow_html=True)

        # ── KPI strip ────────────────────────────────────────────────
        kx1,kx2,kx3,kx4,kx5,kx6 = st.columns(6)
        for col,lbl,val,col2,sub in [
            (kx1,"Total Tasks",    str(len(tasks)),   "#D6E4F0", "scheduled"),
            (kx2,"Critical",       str(n_critical),   "#E8394A" if n_critical>0 else "#00C896","priority"),
            (kx3,"Work Hours",     f"{total_hrs:.1f}","#D6E4F0","total"),
            (kx4,"Planned Cost",   f"${total_cost:,.0f}","#00C896","estimate"),
            (kx5,"Savings vs Unplanned",f"${savings:,.0f}","#00AEEF","potential"),
            (kx6,"Completion",     f"{pct_done:.0f}%","#A78BFA","tasks done"),
        ]:
            with col:
                st.markdown(f"""
                <div class='metric-card' style='text-align:center'>
                  <div class='metric-label'>{lbl}</div>
                  <div class='metric-value' style='color:{col2};font-size:22px'>{val}</div>
                  <div style='font-size:10px;color:#374A60;margin-top:2px'>{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # ── Completion progress bar ───────────────────────────────────
        st.markdown(f"""
        <div style='background:#080E18;border:1px solid #0E1C2C;border-radius:10px;padding:16px 20px;margin-bottom:16px'>
          <div style='display:flex;justify-content:space-between;margin-bottom:8px;align-items:center'>
            <span style='font-size:12px;font-weight:700;color:#D6E4F0'>Schedule Progress</span>
            <span style='font-size:11px;color:#A78BFA;font-family:"DM Mono",monospace;font-weight:700'>{n_done}/{len(tasks)} tasks completed</span>
          </div>
          <div style='background:#0A1020;border-radius:6px;height:10px;overflow:hidden'>
            <div style='width:{pct_done:.1f}%;height:100%;
                        background:linear-gradient(90deg,#7B61FF,#00AEEF);
                        border-radius:6px;transition:width .4s ease'></div>
          </div>
          <div style='display:flex;justify-content:space-between;margin-top:6px;font-size:10px;color:#374A60'>
            <span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── GANTT CHART ───────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Maintenance Gantt — Timeline View")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>Visual schedule showing task timing and duration. Bar width = task duration. Colour = priority level. TODAY marked in cyan.</p>", unsafe_allow_html=True)

        priority_colors={"CRITICAL":"#E8394A","HIGH":"#F5A623","MEDIUM":"#00AEEF","LOW":"#00C896"}
        fig_gantt=go.Figure()
        _base_dt=datetime.combine(sched_start_date,datetime.min.time())
        for t in tasks:
            done_alpha = 0.35 if st.session_state.task_done.get(t["id"],False) else 0.90
            fig_gantt.add_trace(go.Bar(
                name=t["priority"],
                x=[t["duration_hrs"]],
                y=[f"{t['id']} · {t['task']}"],
                base=[(t["due"]-_base_dt).days*24+(t["due"]-_base_dt).seconds/3600],
                orientation="h",
                marker_color=priority_colors[t["priority"]],
                marker_line_width=0,
                opacity=done_alpha,
                hovertemplate=(
                    f"<b>{t['task']}</b><br>Priority: {t['priority']}<br>"
                    f"Due: {t['due'].strftime('%d %b %Y')}<br>"
                    f"Duration: {t['duration_hrs']} hrs<br>"
                    f"Crew: {t['crew_needed']}<br>"
                    f"Est. Cost: ${t['cost']:,}<br>"
                    f"Trigger: {t['trigger']}<extra></extra>"
                ),
                showlegend=False,
            ))
        today_offset=(datetime.now()-_base_dt).days*24
        fig_gantt.add_vline(x=today_offset,line_color="#00AEEF",line_dash="dot",line_width=1.5,
                            annotation_text="TODAY",annotation_font_color="#00AEEF",annotation_font_size=10)
        fig_gantt.update_layout(
            barmode="overlay",paper_bgcolor="#111620",plot_bgcolor="#0D1018",
            height=max(320,len(tasks)*40+80),margin=dict(t=20,b=40,l=20,r=20),
            font=dict(color="#A8B8CC",family="DM Sans",size=11),
            xaxis=dict(title="Hours from Schedule Start",gridcolor="#182030",linecolor="#243048",tickfont=dict(color="#5A6A80")),
            yaxis=dict(autorange="reversed",gridcolor="#182030",linecolor="#243048",tickfont=dict(color="#A8B8CC",size=11)),
        )
        for p,c in priority_colors.items():
            fig_gantt.add_trace(go.Bar(x=[0],y=[""],orientation="h",marker_color=c,name=p,showlegend=True))
        fig_gantt.update_layout(legend=dict(font=dict(color="#A8B8CC",size=11),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.18,x=0.25))
        st.plotly_chart(fig_gantt, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── PRIORITY MATRIX ───────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Priority Urgency Matrix")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>Eisenhower-style matrix showing task urgency vs maintenance impact. Top-right = act immediately.</p>", unsafe_allow_html=True)

        impact_score = {"CRITICAL":1.0,"HIGH":0.75,"MEDIUM":0.45,"LOW":0.20}
        urgency_score= {"CRITICAL":1.0,"HIGH":0.72,"MEDIUM":0.42,"LOW":0.18}
        matrix_col = {"CRITICAL":"#E8394A","HIGH":"#F5A623","MEDIUM":"#00AEEF","LOW":"#00C896"}

        fig_mat = go.Figure()
        # Quadrant backgrounds
        for x0,x1,y0,y1,label,bg in [
            (0,0.5,0,0.5,"Schedule →\nLow urgency, High impact","rgba(0,174,239,.06)"),
            (0.5,1,0,0.5,"Monitor\nLow urgency, Low impact","rgba(0,200,150,.03)"),
            (0,0.5,0.5,1,"Do First ✅\nHigh urgency, High impact","rgba(232,57,74,.08)"),
            (0.5,1,0.5,1,"Delegate\nHigh urgency, Low impact","rgba(245,166,35,.05)"),
        ]:
            fig_mat.add_shape(type="rect",x0=x0,y0=y0,x1=x1,y1=y1,
                              fillcolor=bg,line=dict(color="#182030",width=0.5))
            fig_mat.add_annotation(x=(x0+x1)/2,y=(y0+y1)/2,text=label,
                                   showarrow=False,font=dict(size=9,color="#2A3A50"),
                                   xanchor="center",yanchor="middle",align="center")

        for t in tasks:
            imp = impact_score.get(t["impact"],0.5)
            urg = urgency_score.get(t["priority"],0.5)
            done_marker = "✓ " if st.session_state.task_done.get(t["id"],False) else ""
            fig_mat.add_trace(go.Scatter(
                x=[imp],y=[urg],mode="markers+text",
                marker=dict(size=14,color=matrix_col[t["priority"]],
                            line=dict(color="#0B0E14",width=1.5),
                            symbol="circle" if not st.session_state.task_done.get(t["id"],False) else "circle-open"),
                text=[done_marker+t["id"]],textposition="top center",
                textfont=dict(size=8,color="#A8B8CC"),
                name=t["id"],
                hovertemplate=f"<b>{t['task']}</b><br>Priority: {t['priority']}<br>Due: {t['due'].strftime('%d %b')}<extra></extra>",
            ))

        fig_mat.add_vline(x=0.5,line_color="#182030",line_width=1)
        fig_mat.add_hline(y=0.5,line_color="#182030",line_width=1)
        fig_mat.update_layout(
            paper_bgcolor="#111620",plot_bgcolor="#0D1018",height=380,
            margin=dict(t=20,b=50,l=60,r=20),
            xaxis=dict(title="Impact",range=[0,1],gridcolor="#141E2C",tickvals=[0,0.25,0.5,0.75,1],
                       ticktext=["None","Low","Medium","High","Critical"],tickfont=dict(color="#5A6A80",size=9)),
            yaxis=dict(title="Urgency",range=[0,1],gridcolor="#141E2C",tickvals=[0,0.25,0.5,0.75,1],
                       ticktext=["None","Low","Medium","High","Critical"],tickfont=dict(color="#5A6A80",size=9)),
            showlegend=False,
            font=dict(color="#A8B8CC",family="DM Sans"),
        )
        st.plotly_chart(fig_mat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── INTERACTIVE TASK CARDS ────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### ✅ Maintenance Task List — Interactive Checklist")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>Check off tasks as completed. Progress is tracked in the banner above. Tasks sorted by priority.</p>", unsafe_allow_html=True)

        priority_bg={"CRITICAL":("#1E0D11","#E8394A","#4A1820"),"HIGH":("#1C1608","#F5A623","#2E2108"),"MEDIUM":("#061828","#00AEEF","#0C2840"),"LOW":("#0A1C18","#00C896","#0F3828")}

        for t in tasks:
            bg,col,brd=priority_bg[t["priority"]]
            is_done=st.session_state.task_done.get(t["id"],False)
            done_style="opacity:.45;text-decoration:line-through;" if is_done else ""
            check_col,card_col=st.columns([1,15])
            with check_col:
                checked=st.checkbox("",value=is_done,key=f"taskchk_{t['id']}")
                if checked!=is_done:
                    st.session_state.task_done[t["id"]]=checked
                    st.rerun()
            with card_col:
                st.markdown(f"""
                <div style='background:{bg};border:1px solid {brd};border-left:4px solid {col};
                            border-radius:0 10px 10px 0;padding:14px 18px;margin-bottom:0;{done_style}'>
                  <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:7px'>
                    <div style='display:flex;align-items:center;gap:8px'>
                      <span style='font-size:9px;font-weight:800;color:{col};background:{col}22;border:1px solid {col}44;border-radius:5px;padding:2px 8px;letter-spacing:.08em'>{t["priority"]}</span>
                      <span style='font-size:9px;color:#5A6A80;background:#0D1018;border:1px solid #1E2D45;border-radius:5px;padding:2px 8px'>{t["category"]}</span>
                      <span style='font-size:9px;font-weight:700;color:#374A60;font-family:"DM Mono",monospace'>{t["id"]}</span>
                    </div>
                    <div style='display:flex;gap:14px;font-size:10px;color:#5A6A80;flex-wrap:wrap'>
                      <span>📅 <strong style='color:#A8B8CC'>{t["due"].strftime("%d %b %Y")}</strong></span>
                      <span>⏱ <strong style='color:#A8B8CC'>{t["duration_hrs"]} hrs</strong></span>
                      <span>👷 <strong style='color:#A8B8CC'>{t["crew_needed"]} crew</strong></span>
                      <span>💰 <strong style='color:#A8B8CC'>${t["cost"]:,}</strong></span>
                    </div>
                  </div>
                  <div style='font-size:13px;font-weight:600;color:#D6E4F0;margin-bottom:4px'>{("✓ " if is_done else "")}{t["task"]}</div>
                  <div style='font-size:11px;color:#7A8DA0;line-height:1.6;margin-bottom:5px'>{t["desc"]}</div>
                  <div style='font-size:10px;color:#2A3C4E;border-top:1px solid #1A2535;padding-top:5px;margin-top:3px'>⚡ {t["trigger"]}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── CALENDAR VIEW ─────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 📅 Calendar View")
        st.markdown("<p style='font-size:13px;color:#5A6A80;margin-top:-4px;margin-bottom:16px'>Task placement across the planning horizon. Completed tasks shown faded. TODAY highlighted in cyan.</p>", unsafe_allow_html=True)

        from collections import defaultdict

        horizon_start = sched_start_date
        horizon_end   = sched_start_date + timedelta(weeks=horizon_weeks)
        def months_in_range(start,end):
            months=[]; y,m=start.year,start.month
            while (y,m)<=(end.year,end.month):
                months.append((y,m)); m+=1
                if m>12: m=1;y+=1
            return months
        cal_months=months_in_range(horizon_start,horizon_end)
        day_task_map=defaultdict(list)
        for t in tasks:
            day_task_map[(t["due"].year,t["due"].month,t["due"].day)].append(t)

        PCOLORS={"CRITICAL":("#E8394A","#4A1820","#1E0D11"),"HIGH":("#F5A623","#2E2108","#1C1608"),"MEDIUM":("#00AEEF","#0C2840","#061828"),"LOW":("#00C896","#0F3828","#0A1C18")}
        DAY_NAMES=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        today_date=datetime.now().date()

        cal_html="""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#111620;font-family:'DM Sans','Segoe UI',sans-serif;padding:14px;color:#A8B8CC}
.months-wrap{display:flex;flex-direction:column;gap:22px}
.month-title{font-size:13px;font-weight:700;color:#D6E4F0;margin-bottom:10px;display:flex;align-items:center;gap:10px}
.month-title::after{content:'';flex:1;height:1px;background:#1E2D45}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.day-header{text-align:center;font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;padding:3px 0 5px 0}
.day-cell{border-radius:7px;padding:6px 5px 5px 5px;min-height:64px;border:1px solid}
.day-num{font-size:11px;font-weight:600;margin-bottom:3px}
.chip{border-radius:4px;font-size:8px;font-weight:700;padding:2px 4px;margin-top:2px;border:1px solid;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;display:flex;align-items:center;gap:2px}
.chip-dot{width:4px;height:4px;border-radius:50%;flex-shrink:0}
.more-chip{font-size:7px;color:#374A60;margin-top:2px}
.legend{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.leg-item{display:flex;align-items:center;gap:4px;font-size:9px}
.leg-dot{width:8px;height:8px;border-radius:3px}
</style></head><body>
<div class="legend">"""
        for p,(c,b,bg) in PCOLORS.items():
            cal_html+=f'<div class="leg-item"><div class="leg-dot" style="background:{c}"></div><span style="color:#5A6A80">{p}</span></div>'
        cal_html+='<div class="leg-item"><div class="leg-dot" style="background:#00AEEF;border-radius:50%"></div><span style="color:#5A6A80">TODAY</span></div>'
        cal_html+='<div class="leg-item"><div class="leg-dot" style="background:#243048;opacity:.4"></div><span style="color:#374A60">DONE</span></div>'
        cal_html+='</div><div class="months-wrap">'

        for (yr,mo) in cal_months:
            mo_name=calendar.month_name[mo]
            weeks=calendar.monthcalendar(yr,mo)
            cal_html+=f'<div><div class="month-title">{mo_name} {yr}</div><div class="cal-grid">'
            for i,dl in enumerate(DAY_NAMES):
                wknd_col="#1A2535" if dl in ["Sat","Sun"] else "#374A60"
                cal_html+=f'<div class="day-header" style="color:{wknd_col}">{dl}</div>'
            for week in weeks:
                for day in week:
                    if day==0: cal_html+='<div></div>'; continue
                    cell_date=datetime(yr,mo,day).date()
                    is_today=(cell_date==today_date)
                    is_workday=DAY_NAMES[datetime(yr,mo,day).weekday()] in work_days
                    is_past=cell_date<today_date
                    dtasks=day_task_map.get((yr,mo,day),[])
                    if is_today:  bg2,brd2,numcol,numfw="#0A1828","#00AEEF","#00AEEF","800"
                    elif is_past: bg2,brd2,numcol,numfw="#06080E","#0D1520","#1A2535","400"
                    elif not is_workday: bg2,brd2,numcol,numfw="#070A12","#0D1520","#1A2535","400"
                    elif dtasks:
                        top_p=dtasks[0]["priority"]; _,_,tbg=PCOLORS[top_p]
                        bg2,brd2,numcol,numfw=tbg,"#1E2D45","#A8B8CC","600"
                    else: bg2,brd2,numcol,numfw="#0A0E18","#141E2C","#374A60","500"
                    cal_html+=f'<div class="day-cell" style="background:{bg2};border-color:{brd2}"><div class="day-num" style="color:{numcol};font-weight:{numfw}">{day}</div>'
                    for dt in dtasks[:3]:
                        c,b,dbg=PCOLORS[dt["priority"]]
                        is_d=st.session_state.task_done.get(dt["id"],False)
                        cal_html+=(f'<div class="chip" style="background:{dbg};color:{c};border-color:{b};opacity:{0.4 if is_d else 1.0}">'
                                   f'<div class="chip-dot" style="background:{c}"></div>{"✓ " if is_d else ""}{dt["id"]}</div>')
                    if len(dtasks)>3: cal_html+=f'<div class="more-chip">+{len(dtasks)-3}</div>'
                    cal_html+='</div>'
            cal_html+='</div></div>'
        cal_html+='</div></body></html>'
        components.html(cal_html, height=len(cal_months)*285+70, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── WORKLOAD CHART ────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        wl_col, cost_col = st.columns(2)

        with wl_col:
            st.markdown("#### 👷 Crew Workload by Day")
            st.markdown("<p style='font-size:12px;color:#5A6A80;margin-top:-4px;margin-bottom:12px'>Hours of work per scheduled day vs crew capacity.</p>", unsafe_allow_html=True)
            from collections import Counter
            day_hrs = Counter()
            for t in tasks:
                day_hrs[t["due"].strftime("%d %b")] += t["duration_hrs"]
            if day_hrs:
                wl_dates = sorted(day_hrs.keys(), key=lambda x: datetime.strptime(x,"%d %b"))
                wl_vals  = [day_hrs[d] for d in wl_dates]
                capacity = crew_size * hours_per_shift
                wl_cols  = ["#E8394A" if v>capacity else "#00AEEF" for v in wl_vals]
                fig_wl   = go.Figure()
                fig_wl.add_trace(go.Bar(x=wl_dates,y=wl_vals,marker_color=wl_cols,marker_line_width=0,
                                         text=[f"{v:.1f}h" for v in wl_vals],textposition="outside",
                                         textfont=dict(color="#A8B8CC",size=10),hovertemplate="<b>%{x}</b><br>%{y:.1f} hrs<extra></extra>"))
                fig_wl.add_hline(y=capacity,line_dash="dash",line_color="#F5A623",line_width=1.5,
                                  annotation_text=f"Capacity ({capacity}h)",annotation_font_color="#F5A623",annotation_font_size=9)
                fig_wl.update_layout(paper_bgcolor="#111620",plot_bgcolor="#0D1018",height=260,
                                      margin=dict(t=30,b=30,l=10,r=10),
                                      xaxis=dict(gridcolor="#182030",tickfont=dict(color="#A8B8CC",size=10)),
                                      yaxis=dict(title="Work Hours",gridcolor="#182030",tickfont=dict(color="#5A6A80",size=9)),
                                      showlegend=False)
                st.plotly_chart(fig_wl, use_container_width=True)

        with cost_col:
            st.markdown("#### 💰 Cost Breakdown")
            st.markdown("<p style='font-size:12px;color:#5A6A80;margin-top:-4px;margin-bottom:12px'>Planned maintenance cost by category vs unplanned risk.</p>", unsafe_allow_html=True)
            cat_costs = {}
            for t in tasks:
                cat_costs[t["category"]] = cat_costs.get(t["category"],0) + t["cost"]
            cat_costs["Service Fee"] = planned_maint_cost
            palette=["#00AEEF","#00C896","#F5A623","#E8394A","#7B61FF","#5DD4F7","#F8C96A","#F0707A"]
            fig_cost = go.Figure(go.Pie(
                labels=list(cat_costs.keys()),values=list(cat_costs.values()),hole=0.54,
                marker=dict(colors=palette[:len(cat_costs)],line=dict(color="#0B0E14",width=2)),
                textfont=dict(size=10,color="#A8B8CC"),
                hovertemplate="<b>%{label}</b><br>$%{value:,}<br>%{percent}<extra></extra>",
            ))
            fig_cost.update_layout(paper_bgcolor="#111620",height=260,margin=dict(t=10,b=10,l=10,r=10),
                                    legend=dict(font=dict(color="#A8B8CC",size=9),bgcolor="rgba(0,0,0,0)"),
                                    annotations=[dict(text=f"<b>${sum(cat_costs.values()):,}</b>",x=0.5,y=0.5,
                                                      font_size=13,font_color="#D6E4F0",showarrow=False)])
            st.plotly_chart(fig_cost, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── SAVINGS CALLOUT ───────────────────────────────────────────
        if savings > 0:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0A1C18,#0D2820);border:1px solid #00C896;
                        border-radius:10px;padding:16px 22px;margin-bottom:4px;
                        display:flex;align-items:center;justify-content:space-between'>
              <div>
                <div style='font-size:13px;font-weight:700;color:#00C896'>💰 Planned vs Unplanned Cost Analysis</div>
                <div style='font-size:12px;color:#5EEBC8;margin-top:4px'>
                  This planned schedule avoids an estimated
                  <strong style='color:#D6E4F0'>${unplanned_est:,.0f}</strong> in emergency repair costs.
                  Planned cost: <strong style='color:#D6E4F0'>${total_cost:,.0f}</strong>.
                </div>
              </div>
              <div style='text-align:right;flex-shrink:0;padding-left:24px'>
                <div style='font-size:10px;color:#374A60'>Estimated Savings</div>
                <div style='font-size:26px;font-weight:800;color:#00C896;font-family:"DM Mono",monospace'>${savings:,.0f}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── EXPORT ────────────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 📤 Export Schedule")
        def build_schedule_pdf():
            buf=io.BytesIO()
            doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
            ss=getSampleStyleSheet()
            tS=ParagraphStyle("t",parent=ss["Heading1"],fontSize=16,textColor=rl_colors.HexColor("#0B1628"),spaceAfter=4)
            sub=ParagraphStyle("s",parent=ss["Normal"],fontSize=10,textColor=rl_colors.HexColor("#5A6A80"),spaceAfter=14)
            h2S=ParagraphStyle("h2",parent=ss["Heading2"],fontSize=12,textColor=rl_colors.HexColor("#0B1628"),spaceAfter=6)
            bS=ParagraphStyle("b",parent=ss["Normal"],fontSize=9,leading=14,textColor=rl_colors.HexColor("#182030"))
            story=[]
            story.append(Paragraph("Spur Gear Maintenance Schedule",tS))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}  ·  Gear: {gear_type}  ·  Failure Prob: {prob_pct:.1f}%  ·  RUL: {rul_cycles:,.0f} cycles",sub))
            story.append(Paragraph("Gear Status",h2S))
            t_obj=Table([["Parameter","Value","Status"],["Failure Probability",f"{prob_pct:.1f}%",risk_label],["Health Score",f"{health_score*100:.1f}%",rul_label],["RUL (cycles)",f"{rul_cycles:,.0f}",""],["RUL (hours)",f"{rul_hours:.1f} hrs",""]],colWidths=[6*cm,5*cm,5*cm])
            t_obj.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#0B1628")),("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#f8fafc"),rl_colors.white]),("GRID",(0,0),(-1,-1),0.5,rl_colors.HexColor("#e2e8f0")),("PADDING",(0,0),(-1,-1),6)]))
            story.append(t_obj); story.append(Spacer(1,12))
            story.append(Paragraph("Scheduled Tasks",h2S))
            task_data=[["ID","Task","Priority","Due","Duration","Cost"]]
            for t in tasks: task_data.append([t["id"],t["task"][:40],t["priority"],t["due"].strftime("%d %b %Y"),f"{t['duration_hrs']} hrs",f"${t['cost']:,}"])
            t2=Table(task_data,colWidths=[1.2*cm,6.8*cm,2.6*cm,3*cm,2.2*cm,2*cm])
            t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#0B1628")),("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#f8fafc"),rl_colors.white]),("GRID",(0,0),(-1,-1),0.5,rl_colors.HexColor("#e2e8f0")),("PADDING",(0,0),(-1,-1),5)]))
            story.append(t2); story.append(Spacer(1,12))
            story.append(Paragraph("Cost Summary",h2S))
            story.append(Paragraph(f"Total Planned: ${total_cost:,.0f}  ·  Unplanned Risk: ${unplanned_est:,.0f}  ·  Savings: ${savings:,.0f}",bS))
            doc.build(story); buf.seek(0); return buf.read()

        ex_a,ex_b=st.columns(2)
        with ex_a:
            st.download_button(label="⬇  Download Schedule PDF",data=build_schedule_pdf(),
                               file_name=f"maintenance_schedule_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime="application/pdf",use_container_width=True)
        with ex_b:
            csv_df=pd.DataFrame([{"Task ID":t["id"],"Task":t["task"],"Priority":t["priority"],"Category":t["category"],"Due Date":t["due"].strftime("%Y-%m-%d"),"Duration (hrs)":t["duration_hrs"],"Crew Required":t["crew_needed"],"Est. Cost ($)":t["cost"],"Trigger":t["trigger"],"Completed":st.session_state.task_done.get(t["id"],False)} for t in tasks])
            st.download_button(label="⬇  Download Task List CSV",data=csv_df.to_csv(index=False),
                               file_name=f"maintenance_tasks_{datetime.now().strftime('%Y%m%d')}.csv",
                               mime="text/csv",use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    elif not st.session_state.sched_generated:
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#06090F;border:1px dashed #1A2840;border-radius:12px;
                    padding:52px;text-align:center;margin-top:4px'>
          <div style='font-size:36px;margin-bottom:14px'>🗓</div>
          <div style='font-size:14px;font-weight:600;color:#374A60;margin-bottom:8px'>No schedule generated yet</div>
          <div style='font-size:12px;color:#1E2D45;line-height:1.8;max-width:480px;margin:0 auto'>
            Configure crew availability, cost parameters, and planning horizon above,<br>
            then click <strong style='color:#00AEEF'>Generate Maintenance Schedule</strong> to build your prioritised task list.
          </div>
        </div>""", unsafe_allow_html=True)



# =====================================================================
# FLOATING AI COPILOT WIDGET
# Uses components.html so JS runs, but injects into window.parent.document
# so position:fixed is relative to the real page, not the iframe.
# =====================================================================
_groq_key_js   = json.dumps(GROQ_API_KEY)
_sys_prompt_js = json.dumps(_system_prompt)
_prob_str      = f"{prob_pct:.1f}"
_rul_str       = f"{rul_cycles:,.0f}"

_copilot_widget = f"""
<script>
(function() {{
  var pd = window.parent.document;

  // Avoid duplicate injection on Streamlit reruns
  if (pd.getElementById('cp-fab')) {{
    // Update welcome text with fresh data on each rerun
    var wc = pd.getElementById('cp-welcome-txt');
    if (wc) wc.innerHTML = '<strong>Live ✓</strong> &mdash; {_prob_str}% failure prob &middot; {_rul_str} cycles RUL.';
    return;
  }}

  // ── Inject CSS into parent ──────────────────────────────────────
  var style = pd.createElement('style');
  style.textContent = `
    #cp-fab {{
      position:fixed;bottom:28px;right:28px;width:58px;height:58px;
      background:linear-gradient(135deg,#007DB3,#00AEEF);
      border-radius:50%;border:2px solid #5DD4F7;
      cursor:pointer;display:flex;align-items:center;justify-content:center;
      font-size:26px;box-shadow:0 4px 28px rgba(0,174,239,0.65);
      z-index:999999;transition:all 0.2s ease;user-select:none;
      font-family:sans-serif;
    }}
    #cp-fab:hover {{ transform:scale(1.1);box-shadow:0 6px 36px rgba(0,174,239,0.85) }}
    #cp-badge {{
      position:absolute;top:-4px;right:-4px;background:#E8394A;color:#fff;
      border-radius:50%;width:18px;height:18px;font-size:10px;font-weight:700;
      display:none;align-items:center;justify-content:center;
      border:2px solid #0B0E14;pointer-events:none;
    }}
    #cp-panel {{
      position:fixed;bottom:98px;right:28px;width:390px;max-height:560px;
      background:#111620;border:1px solid #243048;border-radius:18px;
      display:none;flex-direction:column;z-index:999998;
      box-shadow:0 16px 52px rgba(0,0,0,0.85);overflow:hidden;
      font-family:'DM Sans',sans-serif;
    }}
    #cp-panel.cp-open {{ display:flex;animation:cpSlide .22s ease }}
    @keyframes cpSlide {{ from{{opacity:0;transform:translateY(16px)}} to{{opacity:1;transform:translateY(0)}} }}
    .cp-hdr {{ background:#0D1018;border-bottom:1px solid #1A2840;padding:11px 14px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0; }}
    .cp-av {{ width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#007DB3,#00AEEF);display:flex;align-items:center;justify-content:center;font-size:15px;border:1.5px solid #5DD4F7;flex-shrink:0; }}
    .cp-hn {{ font-size:13px;font-weight:600;color:#D6E4F0;margin-left:9px }}
    .cp-hs {{ font-size:10px;color:#5A6A80;margin-left:9px;margin-top:1px }}
    .cp-pulse {{ width:8px;height:8px;border-radius:50%;background:#00C896;box-shadow:0 0 6px #00C896;animation:cpP 2s infinite;flex-shrink:0; }}
    @keyframes cpP {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
    .cp-xbtn {{ background:none;border:none;color:#5A6A80;cursor:pointer;font-size:15px;padding:4px 7px;border-radius:6px;margin-left:8px;line-height:1; }}
    .cp-xbtn:hover {{ color:#D6E4F0;background:#182030 }}
    #cp-msgs {{ flex:1;overflow-y:auto;padding:12px 12px 4px;display:flex;flex-direction:column;gap:6px;min-height:0; }}
    #cp-msgs::-webkit-scrollbar {{ width:4px;background:#0B0E14 }}
    #cp-msgs::-webkit-scrollbar-thumb {{ background:#243048;border-radius:2px }}
    #cp-msgs::-webkit-scrollbar-thumb:hover {{ background:#00AEEF }}
    .cp-welcome {{ background:#0A1420;border:1px solid #182030;border-radius:10px;padding:11px 13px;font-size:12px;color:#5A6A80;line-height:1.65; }}
    .cp-welcome strong {{ color:#00AEEF }}
    .cp-wu {{ display:flex;flex-direction:column;align-items:flex-end;gap:2px }}
    .cp-wa {{ display:flex;flex-direction:column;align-items:flex-start;gap:2px }}
    .cp-lbl {{ font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:#374A60 }}
    .cp-lbl-ai {{ color:#00AEEF }}
    .cp-bu {{ background:linear-gradient(135deg,#0F1E35,#182848);color:#7DD4F8;border-radius:13px 13px 3px 13px;padding:8px 12px;max-width:88%;font-size:12.5px;line-height:1.55;border:1px solid #243D60;word-wrap:break-word; }}
    .cp-ba {{ background:#182030;color:#A8B8CC;border-radius:13px 13px 13px 3px;padding:8px 12px;max-width:92%;font-size:12.5px;line-height:1.65;border:1px solid #243048;word-wrap:break-word;white-space:pre-wrap; }}
    .cp-typing {{ background:#182030;border:1px solid #243048;border-radius:13px 13px 13px 3px;padding:10px 13px;display:flex;gap:5px;align-items:center; }}
    .cp-td {{ width:6px;height:6px;border-radius:50%;background:#00AEEF;animation:cpTd 1.2s infinite }}
    .cp-td:nth-child(2){{animation-delay:.2s}}.cp-td:nth-child(3){{animation-delay:.4s}}
    @keyframes cpTd {{ 0%,80%,100%{{transform:translateY(0)}} 40%{{transform:translateY(-6px)}} }}
    #cp-chips {{ padding:5px 12px 7px;display:flex;flex-wrap:wrap;gap:5px;flex-shrink:0; }}
    .cp-chip {{ background:#0D1018;border:1px solid #1A2840;color:#5A6A80;border-radius:20px;padding:4px 10px;font-size:11px;cursor:pointer;transition:all .15s;white-space:nowrap; }}
    .cp-chip:hover {{ border-color:#00AEEF;color:#00AEEF;background:#071420 }}
    #cp-foot {{ padding:9px 11px 8px;border-top:1px solid #182030;background:#0D1018;flex-shrink:0; }}
    .cp-irow {{ display:flex;gap:7px;align-items:flex-end }}
    #cp-inp {{ flex:1;background:#111620;border:1px solid #243048;border-radius:9px;padding:7px 11px;color:#D6E4F0;font-size:12.5px;outline:none;resize:none;font-family:'DM Sans',sans-serif;max-height:76px;overflow-y:auto;transition:border-color .15s;line-height:1.4; }}
    #cp-inp:focus {{ border-color:#00AEEF;box-shadow:0 0 0 2px rgba(0,174,239,.12) }}
    #cp-inp::placeholder {{ color:#3A4A5C }}
    #cp-snd {{ background:linear-gradient(135deg,#007DB3,#00AEEF);border:none;border-radius:8px;width:34px;height:34px;cursor:pointer;color:#fff;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s; }}
    #cp-snd:hover {{ transform:scale(1.07);box-shadow:0 0 14px rgba(0,174,239,.55) }}
    #cp-snd:disabled {{ opacity:.35;cursor:not-allowed;transform:none }}
    .cp-frow {{ display:flex;justify-content:space-between;align-items:center;padding:3px 1px 0 }}
    .cp-hint {{ font-size:10px;color:#2A3A50 }}
    #cp-clr {{ background:none;border:none;color:#2A3A50;font-size:10px;cursor:pointer;text-decoration:underline; }}
    #cp-clr:hover {{ color:#5A6A80 }}
  `;
  pd.head.appendChild(style);

  // ── Inject HTML into parent body ────────────────────────────────
  var wrap = pd.createElement('div');
  wrap.id = 'cp-root';
  wrap.innerHTML = `
    <button id="cp-fab" title="AI Maintenance Copilot">
      🤖<div id="cp-badge">1</div>
    </button>
    <div id="cp-panel">
      <div class="cp-hdr">
        <div style="display:flex;align-items:center">
          <div class="cp-av">🤖</div>
          <div><div class="cp-hn">AI Maintenance Copilot</div><div class="cp-hs">Llama 3.3 · Groq · Live gear data</div></div>
        </div>
        <div style="display:flex;align-items:center">
          <div class="cp-pulse"></div>
          <button class="cp-xbtn" id="cp-xbtn">✕</button>
        </div>
      </div>
      <div id="cp-msgs">
        <div class="cp-welcome" id="cp-welcome-txt">
          <strong>Live ✓</strong> &mdash; {_prob_str}% failure prob &middot; {_rul_str} cycles RUL.<br>
          Ask anything: failure analysis, maintenance, calculations, ISO standards.
        </div>
      </div>
      <div id="cp-chips">
        <div class="cp-chip">Why is this gear failing?</div>
        <div class="cp-chip">What causes gear pitting?</div>
        <div class="cp-chip">Explain SHAP values</div>
        <div class="cp-chip">Power at current RPM</div>
      </div>
      <div id="cp-foot">
        <div class="cp-irow">
          <textarea id="cp-inp" rows="1" placeholder="Ask anything about gear health or engineering…"></textarea>
          <button id="cp-snd">&#10148;</button>
        </div>
        <div class="cp-frow">
          <span class="cp-hint">Enter to send &middot; Shift+Enter for newline</span>
          <button id="cp-clr">clear chat</button>
        </div>
      </div>
    </div>
  `;
  pd.body.appendChild(wrap);

  // ── Wire up logic ───────────────────────────────────────────────
  const GROQ_KEY = {_groq_key_js};
  const SYS      = {_sys_prompt_js};

  var hist = [], busy = false;
  var fab   = pd.getElementById('cp-fab');
  var panel = pd.getElementById('cp-panel');
  var msgs  = pd.getElementById('cp-msgs');
  var inp   = pd.getElementById('cp-inp');
  var snd   = pd.getElementById('cp-snd');
  var clr   = pd.getElementById('cp-clr');
  var chips = pd.getElementById('cp-chips');
  var badge = pd.getElementById('cp-badge');
  var xbtn  = pd.getElementById('cp-xbtn');

  fab.addEventListener('click', function() {{
    panel.classList.toggle('cp-open');
    if (panel.classList.contains('cp-open')) {{
      badge.style.display = 'none';
      setTimeout(function(){{ inp.focus(); }}, 200);
    }}
  }});
  xbtn.addEventListener('click', function() {{ panel.classList.remove('cp-open'); }});

  snd.addEventListener('click', doSend);
  inp.addEventListener('keydown', function(e) {{
    if (e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); doSend(); }}
  }});
  inp.addEventListener('input', function() {{
    inp.style.height = 'auto';
    inp.style.height = Math.min(inp.scrollHeight, 76) + 'px';
  }});
  clr.addEventListener('click', function() {{
    hist = [];
    msgs.innerHTML = '<div class="cp-welcome"><strong>Live ✓</strong> &mdash; {_prob_str}% failure prob &middot; {_rul_str} cycles RUL.</div>';
    chips.style.display = 'flex';
  }});

  var chipEls = chips.querySelectorAll('.cp-chip');
  var chipTexts = ['Why is this gear failing?','What causes gear pitting?','Explain SHAP values','Calculate power at current RPM'];
  chipEls.forEach(function(el, i) {{
    el.addEventListener('click', function() {{
      chips.style.display = 'none';
      var t = chipTexts[i];
      addUser(t); hist.push({{role:'user',content:t}}); callAPI();
    }});
  }});

  function doSend() {{
    var t = inp.value.trim();
    if (!t || busy) return;
    inp.value = ''; inp.style.height = 'auto';
    chips.style.display = 'none';
    addUser(t); hist.push({{role:'user',content:t}}); callAPI();
  }}

  function addUser(t) {{
    var d = pd.createElement('div'); d.className = 'cp-wu';
    d.innerHTML = '<div class="cp-lbl">You</div><div class="cp-bu">' + esc(t) + '</div>';
    msgs.appendChild(d); scrollEnd();
  }}
  function addAI(t) {{
    var d = pd.createElement('div'); d.className = 'cp-wa';
    d.innerHTML = '<div class="cp-lbl cp-lbl-ai">AI Copilot</div><div class="cp-ba">' + esc(t) + '</div>';
    msgs.appendChild(d); scrollEnd();
  }}
  function showTyping() {{
    var d = pd.createElement('div'); d.id = 'cp-typing'; d.className = 'cp-wa';
    d.innerHTML = '<div class="cp-lbl cp-lbl-ai">AI Copilot</div><div class="cp-typing"><div class="cp-td"></div><div class="cp-td"></div><div class="cp-td"></div></div>';
    msgs.appendChild(d); scrollEnd();
  }}
  function removeTyping() {{ var e = pd.getElementById('cp-typing'); if(e) e.remove(); }}
  function scrollEnd() {{ msgs.scrollTop = msgs.scrollHeight; }}
  function esc(s) {{ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}

  async function callAPI() {{
    busy = true; snd.disabled = true; showTyping();
    try {{
      var r = await fetch('https://api.groq.com/openai/v1/chat/completions', {{
        method: 'POST',
        headers: {{'Authorization':'Bearer '+GROQ_KEY,'Content-Type':'application/json'}},
        body: JSON.stringify({{
          model: 'llama-3.3-70b-versatile',
          messages: [{{role:'system',content:SYS}}, ...hist],
          max_tokens: 900, temperature: 0.7
        }})
      }});
      var data = await r.json();
      var reply = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || '⚠ No response.';
      hist.push({{role:'assistant',content:reply}});
      removeTyping(); addAI(reply);
      if (!panel.classList.contains('cp-open')) {{ badge.style.display = 'flex'; }}
    }} catch(e) {{
      removeTyping(); addAI('⚠ Connection error. Check your Groq API key.');
    }}
    busy = false; snd.disabled = false;
  }}
}})();
</script>
"""
components.html(_copilot_widget, height=0, scrolling=False)