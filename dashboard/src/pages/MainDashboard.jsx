import React, { useState, useEffect } from 'react';
import {
  StatCard, GearHealthGauge, FaultCountdown, FaultProbabilityBar,
  SensorStatus, CostImpact, ShapChart, ModelComparison,
  WhatIfOptimizer, LimeChart, RULSection,
  ReportPDFButton, FloatingCopilot, HistoryDashboard
} from '../components/DashboardComponents';
import * as api from '../api/gearApi';
import { useAuth } from '../context/AuthContext';
import GearScene from '../components/GearScene';
import { useGearStore } from '../store/gearStore';

const TABS = [
  { id: 'health',    label: '🎯  Gear Health' },
  { id: 'xai',      label: '🔍  SHAP + LIME' },
  { id: 'history',  label: '📈  Trends & History' },
  { id: 'optimizer',label: '🔧  What-If Optimizer' },
  { id: '3d',       label: '🎬  3D Animation' },
  { id: 'cost',     label: '💰  Cost Impact' },
  { id: 'models',   label: '📊  Model Comparison' },
];

const DEFAULT_SENSORS = {
  load: 48.0, torque: 201.6, vib: 2.3, temp: 72.0,
  wear: 0.20, lube: 0.82, eff: 96.8, cycles: 18000
};

const GEAR_ICONS = { Helical: '⚙️', Spur: '🔧', Bevel: '🔩', Worm: '🌀' };

const HELICAL_SLIDERS = [
  { key: 'load',   label: 'Load (kN)',             min: 10,  max: 120,   step: 0.5,  unit: 'kN' },
  { key: 'torque', label: 'Torque (Nm)',            min: 50,  max: 600,   step: 1,    unit: 'Nm' },
  { key: 'vib',   label: 'Vibration RMS (mm/s)',   min: 0.5, max: 30,    step: 0.1,  unit: 'mm/s' },
  { key: 'temp',  label: 'Temperature (°C)',       min: 40,  max: 150,   step: 0.5,  unit: '°C' },
  { key: 'wear',  label: 'Wear (mm)',              min: 0,   max: 4,     step: 0.01, unit: 'mm' },
  { key: 'lube',  label: 'Lubrication Index',      min: 0.05,max: 1,     step: 0.01, unit: '' },
  { key: 'eff',   label: 'Efficiency (%)',         min: 70,  max: 99,    step: 0.1,  unit: '%' },
  { key: 'cycles',label: 'Cycles in Use',          min: 0,   max: 100000,step: 100,  unit: '' },
];

const SPUR_SLIDERS = [
  { key: 'load',   label: 'Speed (RPM)',           min: 500,  max: 3000,  step: 10,   unit: 'RPM' },
  { key: 'torque', label: 'Torque (Nm)',           min: 50,   max: 500,   step: 1,    unit: 'Nm' },
  { key: 'vib',    label: 'Vibration (mm/s)',      min: 0.5,  max: 20,    step: 0.1,  unit: 'mm/s' },
  { key: 'temp',   label: 'Temperature (°C)',      min: 40,   max: 120,   step: 0.5,  unit: '°C' },
  { key: 'wear',   label: 'Shock Load (g)',        min: 0,    max: 5,     step: 0.1,  unit: 'g' },
  { key: 'lube',   label: 'Noise (dB)',            min: 50,   max: 95,    step: 0.5,  unit: 'dB' },
];

const WORM_SLIDERS = [
  { key: 'rpm',        label: 'Worm RPM',              min: 500,  max: 4000,  step: 10,   unit: 'RPM' },
  { key: 'in_torque',  label: 'Input Torque (Nm)',     min: 15,   max: 120,   step: 0.5,  unit: 'Nm' },
  { key: 'out_torque', label: 'Output Torque (Nm)',    min: 400,  max: 3500,  step: 10,   unit: 'Nm' },
  { key: 'current',    label: 'Motor Current (A)',     min: 10,   max: 35,    step: 0.1,  unit: 'A' },
  { key: 'oil_temp',   label: 'Oil Temperature (°C)',  min: 30,   max: 160,   step: 1,    unit: '°C' },
  { key: 'amb_temp',   label: 'Ambient Temp (°C)',     min: 10,   max: 40,    step: 0.5,  unit: '°C' },
  { key: 'ax_vib',     label: 'Axial Vibration',       min: 2,    max: 8,     step: 0.1,  unit: 'mm/s' },
  { key: 'rad_vib',    label: 'Radial Vibration',      min: 0.5,  max: 3,     step: 0.1,  unit: 'mm/s' },
  { key: 'cu_ppm',     label: 'Copper PPM',            min: 10,   max: 150,   step: 1,    unit: 'ppm' },
  { key: 'fe_ppm',     label: 'Iron PPM',              min: 5,    max: 40,    step: 1,    unit: 'ppm' },
  { key: 'eff',        label: 'Efficiency (%)',        min: 70,   max: 90,    step: 0.1,  unit: '%' },
  { key: 'friction',   label: 'Friction Coefficient',  min: 0.02, max: 0.07,  step: 0.001, unit: '' },
  { key: 'backlash',   label: 'Backlash (mm)',         min: 0.05, max: 0.20,  step: 0.001, unit: 'mm' },
];

function calcHealthScore(pred, gc) {
  if (!pred || !gc) return 100;
  // If backend already computed health_score, use it
  if (pred.health_score !== undefined) return pred.health_score;
  let score = 100;
  const v = pred.sensor_values || {};
  score -= Math.min(30, Math.max(0, ((v['Vibration RMS (mm/s)'] || 0) - gc.vib_limit) * 5));
  score -= Math.min(20, Math.max(0, ((v['Temperature (°C)'] || 0) - gc.temp_limit) * 0.8));
  score -= Math.min(25, Math.max(0, ((v['Wear (mm)'] || 0) - gc.wear_limit) * 30));
  score -= Math.min(20, Math.max(0, (gc.lube_limit - (v['Lubrication Index'] || 1)) * 40));
  score -= Math.min(10, Math.max(0, (gc.eff_limit - (v['Efficiency (%)'] || 99)) * 0.8));
  if (pred.fault_label === 'Major Fault' || pred.fault_label === 'Failure') score = Math.min(score, 25);
  else if (pred.fault_label === 'Minor Fault') score = Math.min(score, 65);
  return Math.max(0, Math.round(score));
}

export default function MainDashboard() {
  const { currentUser } = useAuth();
  const [gearType,    setGearType]    = useState('Helical');
  const [sensors,     setSensors]     = useState(DEFAULT_SENSORS);
  const [activeTab,   setActiveTab]   = useState('health');
  const [prediction,  setPrediction]  = useState(null);
  const [gearConfigs, setGearConfigs] = useState(null);
  const [compData,    setCompData]    = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [showSliders, setShowSliders] = useState(false);

  // Zustand store for 3D scene
  const setActiveGear = useGearStore((state) => state.setActiveGear);
  const updateSensors = useGearStore((state) => state.updateSensors);

  // Use actual logged-in user from AuthContext
  const user = currentUser ? {
    name: currentUser.fullName,
    role: currentUser.role,
    shift: currentUser.shift
  } : { name: 'Operator', role: 'Operator', shift: 'Day' };

  useEffect(() => {
    Promise.all([api.getGearConfigs(), api.getModels()])
      .then(([gc, mc]) => { setGearConfigs(gc); setCompData(mc); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  // Sync gear type with 3D scene
  useEffect(() => {
    setActiveGear(gearType);
  }, [gearType, setActiveGear]);

  // Sync sensors with 3D scene
  useEffect(() => {
    if (prediction) {
      const healthScore = calcHealthScore(prediction, gearConfigs?.[gearType] || {});
      updateSensors({
        rpm:         sensors.rpm || sensors.load || 1200,
        vibration:   sensors.vib || sensors.ax_vib || 2.3,
        health:      healthScore >= 70 ? 'normal' : healthScore >= 40 ? 'warning' : 'critical',
        temperature: sensors.temp || sensors.oil_temp || 72,
      });
    }
  }, [sensors, prediction, gearType, gearConfigs, updateSensors]);

  // When gear type changes, load preset values from first unit
  useEffect(() => {
    if (!gearConfigs || !gearConfigs[gearType]) return;
    const units    = gearConfigs[gearType].units;
    const firstKey = Object.keys(units)[0];
    const p        = units[firstKey];
    // Spur uses speed/shock/noise, map to slider keys
    if (gearType === 'Spur') {
      setSensors({
        load: p.speed || 1200, torque: p.torque || 180,
        vib: p.vib || 3.2,    temp: p.temp || 70,
        wear: p.shock || 1.2, lube: p.noise ? p.noise / 100 : 0.62,
        eff: 94.5,            cycles: 22000
      });
    } else if (gearType === 'Worm') {
      // Worm gear - proper 13 features mapping
      setSensors({
        rpm: p.rpm || 1321,
        in_torque: p.in_torque || 86.8,
        out_torque: p.out_torque || 2951,
        current: p.current || 26.0,
        oil_temp: p.oil_temp || 56.5,
        amb_temp: p.amb_temp || 24.6,
        ax_vib: p.ax_vib || 5.2,
        rad_vib: p.rad_vib || 2.3,
        cu_ppm: p.cu_ppm || 25,
        fe_ppm: p.fe_ppm || 9,
        eff: p.eff || 85.0,
        friction: p.friction || 0.031,
        backlash: p.backlash || 0.115
      });
    } else {
      setSensors({ load: p.load, torque: p.torque, vib: p.vib, temp: p.temp, wear: p.wear, lube: p.lube, eff: p.eff, cycles: p.cycles });
    }
  }, [gearType, gearConfigs]);

  // Debounced predict on sensor change
  useEffect(() => {
    const timer = setTimeout(() => {
      // For Spur, convert slider values to proper API format
      if (gearType === 'Spur') {
        const spurPayload = {
          speed: sensors.load,    // Speed RPM
          torque: sensors.torque, // Torque Nm
          vib: sensors.vib,       // Vibration mm/s
          temp: sensors.temp,     // Temperature C
          shock: sensors.wear,    // Shock Load g
          noise: sensors.lube * 100, // Noise dB (slider is 0-1, API expects 50-95)
        };
        api.predictSpur(spurPayload).then(setPrediction).catch(console.error);
      } else if (gearType === 'Worm') {
        // For Worm, send proper worm gear payload with fallback defaults
        const wormPayload = {
          rpm: sensors.rpm ?? 1321,
          in_torque: sensors.in_torque ?? 86.8,
          out_torque: sensors.out_torque ?? 2951,
          current: sensors.current ?? 26.0,
          oil_temp: sensors.oil_temp ?? 56.5,
          amb_temp: sensors.amb_temp ?? 24.6,
          ax_vib: sensors.ax_vib ?? 5.2,
          rad_vib: sensors.rad_vib ?? 2.3,
          cu_ppm: sensors.cu_ppm ?? 25,
          fe_ppm: sensors.fe_ppm ?? 9,
          eff: sensors.eff ?? 85.0,
          friction: sensors.friction ?? 0.031,
          backlash: sensors.backlash ?? 0.115,
        };
        console.log('Worm payload:', wormPayload); // Debug log
        api.predict(wormPayload, gearType).then(setPrediction).catch(console.error);
      } else {
        api.predict(sensors, gearType).then(setPrediction).catch(console.error);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [sensors, gearType]);

  // Auto-log to history on each prediction
  useEffect(() => {
    if (!prediction || !gearConfigs) return;
    const gc      = gearConfigs[gearType];
    const hs      = calcHealthScore(prediction, gc);
    const unitKeys = Object.keys(gc.units || {});
    const gearName = unitKeys[0]?.split(' ')[0] || 'GR-01';
    api.logHistory({
      gear_type: gearType, gear_unit: gearName,
      fault_label: prediction.fault_label, confidence: prediction.confidence,
      health_score: hs, rul_cycles: prediction.rul_cycles,
      sensor_values: prediction.sensor_values,
      operator_name: user.name || 'Unknown',
      shift: user.shift || 'Day',
      role: user.role || 'Operator',
    }).catch(() => {});
  }, [prediction]);

  if (loading) return <div className="page-loading"><span className="spinner" /> Loading Dashboard...</div>;

  const gc          = gearConfigs?.[gearType] || {};
  const fault       = prediction?.fault_label || 'Loading...';
  const conf        = prediction?.confidence  || 0;
  const rul         = prediction?.rul_cycles  || 0;
  const healthScore = calcHealthScore(prediction, gc);
  const unitKeys    = Object.keys(gc.units || {});
  const gearName    = unitKeys[0]?.split(' ')[0] || 'GR-01';
  const sensorValues = prediction?.sensor_values || {};
  const currentSliders = gearType === 'Spur' ? SPUR_SLIDERS : gearType === 'Worm' ? WORM_SLIDERS : HELICAL_SLIDERS;

  return (
    <div className="fade-in">
      {/* ── Gear Selector + Sensor Toggle ─────────────────── */}
      <div className="dashboard-controls">
        <div className="gear-selector">
          {['Helical', 'Spur', 'Bevel', 'Worm'].map(g => (
            <button
              key={g}
              className={`gear-sel-btn ${g === gearType ? 'active' : ''}`}
              onClick={() => setGearType(g)}
            >
              <span className="gear-sel-icon">{GEAR_ICONS[g]}</span>
              <span>{g}</span>
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span style={{ fontSize: 12, color: '#a3aed0', fontWeight: 600 }}>
            👤 {user.name} · {user.shift} Shift
          </span>
          <button className="btn btn-secondary" onClick={() => setShowSliders(!showSliders)}>
            {showSliders ? '▲ Hide Sensors' : '▼ Show Sensors'}
          </button>
        </div>
      </div>

      {/* ── Sensor Sliders ─────────────────────────────────── */}
      {showSliders && (
        <div className="card sensor-panel fade-in">
          <div className="sensor-grid">
            {currentSliders.map(s => (
              <div className="slider-group" key={s.key}>
                <div className="slider-label">
                  <span>{s.label}</span>
                  <span className="slider-value">{(sensors[s.key] !== undefined ? sensors[s.key] : s.min).toFixed(s.step < 0.01 ? 3 : s.step < 0.1 ? 2 : s.step < 1 ? 1 : 0)}{s.unit}</span>
                </div>
                <input type="range" min={s.min} max={s.max} step={s.step}
                  value={sensors[s.key] !== undefined ? sensors[s.key] : s.min}
                  onChange={e => setSensors(prev => ({ ...prev, [s.key]: parseFloat(e.target.value) }))} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── KPI Row ────────────────────────────────────────── */}
      <div className="stat-cards">
        <StatCard label="Confidence"  value={`${(conf * 100).toFixed(1)}%`} icon="blue" />
        <StatCard label="Fault Class" value={fault}
          color={fault === 'Major Fault' || fault === 'Failure' ? '#ee5d50' : fault === 'Minor Fault' ? '#ffb547' : '#05cd99'}
          icon={fault === 'No Fault' || fault === 'No Failure' ? 'green' : 'red'} />
        <StatCard label="RUL (cycles)"  value={rul.toLocaleString()} icon="purple" />
        <StatCard label="RUL (shifts)"  value={Math.floor(rul / 400).toLocaleString()} icon="amber" />
        <StatCard label="Health Score"  value={`${healthScore}/100`}
          color={healthScore >= 70 ? '#05cd99' : healthScore >= 40 ? '#ffb547' : '#ee5d50'}
          icon={healthScore >= 70 ? 'green' : 'red'} />
      </div>

      {/* ── Tab Navigation ─────────────────────────────────── */}
      <div className="tab-bar">
        {TABS.map(t => (
          <button key={t.id} className={`tab-btn ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Tab: Gear Health ───────────────────────────────── */}
      {activeTab === 'health' && (
        <div className="fade-in">
          <div className="grid-3">
            <GearHealthGauge score={healthScore} fault={fault} gearName={gearName} />
            <FaultCountdown  rul={rul} fault={fault} dailyCycles={gc.daily_cycles || 8000} />
            <div className="card">
              <FaultProbabilityBar probs={prediction?.class_probs || {}} />
              <div style={{ marginTop: 16 }}>
                <SensorStatus sensors={sensors} gearConfig={gc} gearType={gearType} />
              </div>
            </div>
          </div>

          {/* RUL Section + PDF button */}
          <RULSection
            rul={rul}
            dailyCycles={gc.daily_cycles || 8000}
            fault={fault}
            healthScore={healthScore}
          />

          <div className="pdf-button-container">
            <ReportPDFButton
              sensorValues={sensorValues}
              gearId={gearName}
              gearType={gearType}
              prediction={prediction}
              healthScore={healthScore}
              gearConfig={gc}
              user={user}
            />
          </div>
        </div>
      )}

      {/* ── Tab: SHAP + LIME ─────────────────────────────── */}
      {activeTab === 'xai' && (
        <div className="fade-in">
          {/* SHAP Section */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="xai-section-header">
              <div className="xai-section-icon">🔍</div>
              <div>
                <div className="xai-section-title">SHAP — SHapley Additive exPlanations</div>
                <div className="xai-section-desc">
                  Uses game theory to calculate each feature's contribution to the prediction.
                  <span style={{ color: '#ee5d50', fontWeight: 700 }}> Positive values</span> push toward fault,
                  <span style={{ color: '#05cd99', fontWeight: 700 }}> negative values</span> push toward healthy.
                </div>
              </div>
            </div>
            <ShapChart shapValues={prediction?.shap_values} gearName={gearName} gearType={gearType} fault={fault} />
            <div className="xai-explanation">
              <div className="xai-explanation-title">📖 Understanding SHAP Values</div>
              <div className="xai-explanation-text">
                SHAP (SHapley Additive exPlanations) values show how much each sensor reading contributes to the fault prediction. 
                Features with <strong style={{ color: '#ee5d50' }}>positive values (red bars)</strong> increase the likelihood of a fault, 
                while <strong style={{ color: '#05cd99' }}>negative values (green bars)</strong> indicate protective factors that reduce fault risk. 
                The magnitude shows the strength of influence — larger bars mean stronger impact on the prediction.
              </div>
            </div>
          </div>

          {/* LIME Section */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="xai-section-header">
              <div className="xai-section-icon">📋</div>
              <div>
                <div className="xai-section-title">LIME — Local Interpretable Model-agnostic Explanations</div>
                <div className="xai-section-desc">
                  Fits a simple model around your input to explain which conditions most influenced this prediction.
                  Higher weight = stronger influence on the current output.
                </div>
              </div>
            </div>
            <LimeChart sensors={sensors} gearType={gearType} />
            <div className="xai-explanation">
              <div className="xai-explanation-title">📖 Understanding LIME Results</div>
              <div className="xai-explanation-text">
                LIME creates a local approximation of the model's behavior around your specific input. 
                Each rule shows a condition (e.g., "Vibration &gt; 5.2") and its weight. 
                <strong style={{ color: '#ee5d50' }}>Positive weights (red)</strong> indicate conditions that push toward fault classification, 
                while <strong style={{ color: '#05cd99' }}>negative weights (green)</strong> suggest conditions favoring healthy operation. 
                LIME is particularly useful for understanding complex non-linear model decisions in human-readable terms.
              </div>
            </div>
          </div>

          {/* Maintenance Techniques Section - Only show when fault detected */}
          {(fault === 'Minor Fault' || fault === 'Major Fault' || fault === 'Failure') && (
            <div className="card maintenance-techniques">
              <div className="card-header">
                <div className="card-header-icon">🔧</div> 
                Recommended Maintenance Techniques — {fault} Detected
              </div>
              
              {/* Show appropriate maintenance card based on fault severity */}
              <div className="maintenance-grid">
                {fault === 'Minor Fault' && (
                  <div className="maintenance-card">
                    <div className="maintenance-card-header" style={{ background: '#fff8eb', color: '#ffb547' }}>
                      <span className="maintenance-icon">⚠️</span>
                      <span className="maintenance-title">Corrective Maintenance Required</span>
                    </div>
                    <div className="maintenance-card-body">
                      <div className="maintenance-item">
                        <strong>Current Status:</strong> Health score {healthScore}/100 — Minor Fault detected
                      </div>
                      <div className="maintenance-item">
                        <strong>Immediate Actions:</strong>
                        <ul>
                          <li>Reduce operating load by 15-20%</li>
                          <li>Inspect and replenish lubrication system</li>
                          <li>Check for misalignment or mounting issues</li>
                          <li>Increase monitoring frequency to every shift</li>
                        </ul>
                      </div>
                      <div className="maintenance-item">
                        <strong>Schedule:</strong> Plan maintenance within 1-2 weeks
                      </div>
                      <div className="maintenance-item">
                        <strong>Expected Downtime:</strong> 4-8 hours
                      </div>
                    </div>
                  </div>
                )}

                {(fault === 'Major Fault' || fault === 'Failure') && (
                  <div className="maintenance-card">
                    <div className="maintenance-card-header" style={{ background: '#fef1f0', color: '#ee5d50' }}>
                      <span className="maintenance-icon">🔴</span>
                      <span className="maintenance-title">Emergency Maintenance Required</span>
                    </div>
                    <div className="maintenance-card-body">
                      <div className="maintenance-item">
                        <strong>Current Status:</strong> Health score {healthScore}/100 — {fault} detected
                      </div>
                      <div className="maintenance-item">
                        <strong>Critical Actions:</strong>
                        <ul>
                          <li><strong style={{ color: '#ee5d50' }}>IMMEDIATE SHUTDOWN REQUIRED</strong> — Stop operation now</li>
                          <li>Full gear inspection and damage assessment</li>
                          <li>Replace worn or damaged components</li>
                          <li>Check bearing condition and alignment</li>
                          <li>Verify shaft integrity and coupling</li>
                          <li>Complete lubrication system overhaul</li>
                          <li>Post-repair testing before restart</li>
                        </ul>
                      </div>
                      <div className="maintenance-item">
                        <strong>Schedule:</strong> <span style={{ color: '#ee5d50', fontWeight: 700 }}>IMMEDIATE — Do not delay</span>
                      </div>
                      <div className="maintenance-item">
                        <strong>Expected Downtime:</strong> 1-3 days
                      </div>
                    </div>
                  </div>
                )}

                {/* Root Cause Analysis - Always show when fault detected */}
                <div className="maintenance-card">
                  <div className="maintenance-card-header" style={{ background: '#ece5ff', color: '#7c3aed' }}>
                    <span className="maintenance-icon">🔬</span>
                    <span className="maintenance-title">Root Cause Analysis</span>
                  </div>
                  <div className="maintenance-card-body">
                    <div className="maintenance-item">
                      <strong>Investigation Steps:</strong>
                      <ul>
                        <li>Review SHAP analysis above for primary contributors</li>
                        <li>Identify top 3 features with highest SHAP values</li>
                        <li>Check historical trends for patterns</li>
                        <li>Verify operating conditions vs. design specs</li>
                        <li>Inspect for external factors (contamination, overload)</li>
                        <li>Document findings and update maintenance plan</li>
                      </ul>
                    </div>
                    <div className="maintenance-item">
                      <strong>Goal:</strong> Prevent recurrence and extend gear life
                    </div>
                  </div>
                </div>

                {/* SHAP-based Recommendations */}
                {prediction?.shap_values && (
                  <div className="maintenance-card">
                    <div className="maintenance-card-header" style={{ background: '#e0f2fe', color: '#0369a1' }}>
                      <span className="maintenance-icon">📊</span>
                      <span className="maintenance-title">AI-Driven Insights</span>
                    </div>
                    <div className="maintenance-card-body">
                      <div className="maintenance-item">
                        <strong>Top Contributing Factors:</strong>
                        <ul>
                          {Object.entries(prediction.shap_values)
                            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                            .slice(0, 3)
                            .map(([feature, value]) => (
                              <li key={feature}>
                                <strong style={{ color: value > 0 ? '#ee5d50' : '#05cd99' }}>
                                  {feature}
                                </strong>: {value > 0 ? 'Increasing' : 'Decreasing'} fault risk 
                                (impact: {Math.abs(value).toFixed(4)})
                              </li>
                            ))}
                        </ul>
                      </div>
                      <div className="maintenance-item">
                        <strong>Recommendation:</strong> Focus maintenance efforts on addressing the parameters listed above for maximum effectiveness.
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="maintenance-footer">
                <div className="maintenance-footer-icon">💡</div>
                <div className="maintenance-footer-text">
                  <strong>Pro Tip:</strong> Use the SHAP and LIME insights above to identify which parameters are driving the fault. 
                  The AI-Driven Insights card shows the top 3 contributing factors based on your current sensor readings.
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Trends & History ─────────────────────────── */}
      {activeTab === 'history' && (
        <HistoryDashboard gearType={gearType} />
      )}

      {/* ── Tab: Optimizer ───────────────────────────────── */}
      {activeTab === 'optimizer' && (
        <WhatIfOptimizer sensors={sensors} sensorValues={sensorValues} prediction={prediction} gearConfig={gc} />
      )}

      {/* ── Tab: 3D Animation ─────────────────────────────── */}
      {activeTab === '3d' && (
        <div className="fade-in">
          <div className="card" style={{ padding: 0, height: '600px', overflow: 'hidden', marginBottom: 16 }}>
            <GearScene />
          </div>
          
          {/* Gear Type Insights - Side by Side Layout */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-header">
              <div className="card-header-icon">📚</div>
              {gearType} Gear - Technical Insights
            </div>
            <div className="gear-insights-grid">
              {gearType === 'Spur' && (
                <>
                  <div className="insight-box">
                    <div className="insight-box-icon">🔧</div>
                    <div className="insight-box-title">Design</div>
                    <div className="insight-box-text">
                      Straight teeth parallel to gear axis. Simplest gear type with 95-98% efficiency. 
                      Teeth engage suddenly causing noise at high speeds.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">⚡</div>
                    <div className="insight-box-title">Performance</div>
                    <div className="insight-box-text">
                      <strong>Pros:</strong> High efficiency, simple, low cost.<br/>
                      <strong>Cons:</strong> Noisy, shock loads, parallel shafts only.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">🏭</div>
                    <div className="insight-box-title">Applications</div>
                    <div className="insight-box-text">
                      Washing machines, dryers, construction equipment, fuel pumps, mills, 
                      rack systems, industrial machinery.
                    </div>
                  </div>
                </>
              )}
              
              {gearType === 'Helical' && (
                <>
                  <div className="insight-box">
                    <div className="insight-box-icon">🔧</div>
                    <div className="insight-box-title">Design</div>
                    <div className="insight-box-text">
                      Teeth cut at 15-30° helix angle. Gradual engagement for smoother operation. 
                      Creates axial thrust requiring thrust bearings.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">⚡</div>
                    <div className="insight-box-title">Performance</div>
                    <div className="insight-box-text">
                      <strong>Pros:</strong> Quieter, smoother, higher load capacity.<br/>
                      <strong>Cons:</strong> Axial thrust, complex, 94-96% efficiency.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">🏭</div>
                    <div className="insight-box-title">Applications</div>
                    <div className="insight-box-text">
                      Automotive transmissions, heavy-duty gearboxes, conveyors, elevators, 
                      compressors, high-speed systems.
                    </div>
                  </div>
                </>
              )}
              
              {gearType === 'Bevel' && (
                <>
                  <div className="insight-box">
                    <div className="insight-box-icon">🔧</div>
                    <div className="insight-box-title">Design</div>
                    <div className="insight-box-text">
                      Cone-shaped with tapered teeth. Transmits power between intersecting shafts 
                      at 90° angles. Requires precise alignment.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">⚡</div>
                    <div className="insight-box-title">Performance</div>
                    <div className="insight-box-text">
                      <strong>Pros:</strong> Right-angle transmission, compact design.<br/>
                      <strong>Cons:</strong> Complex manufacturing, precise alignment needed.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">🏭</div>
                    <div className="insight-box-title">Applications</div>
                    <div className="insight-box-text">
                      Automotive differentials, hand drills, marine propulsion, printing presses, 
                      cooling towers, 90° drives.
                    </div>
                  </div>
                </>
              )}
              
              {gearType === 'Worm' && (
                <>
                  <div className="insight-box">
                    <div className="insight-box-icon">🔧</div>
                    <div className="insight-box-title">Design</div>
                    <div className="insight-box-text">
                      Screw-like worm meshes with wheel. High reduction ratios (20:1 to 300:1). 
                      Self-locking: worm drives wheel, but not reverse.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">⚡</div>
                    <div className="insight-box-title">Performance</div>
                    <div className="insight-box-text">
                      <strong>Pros:</strong> High ratios, compact, self-locking, quiet.<br/>
                      <strong>Cons:</strong> Lower efficiency (40-90%), heat generation.
                    </div>
                  </div>
                  <div className="insight-box">
                    <div className="insight-box-icon">🏭</div>
                    <div className="insight-box-title">Applications</div>
                    <div className="insight-box-text">
                      Elevators (safety), conveyors, tuning instruments, gate operators, 
                      packaging machinery, high-reduction systems.
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
          
          {/* 3D Controls */}
          <div className="card">
            <div className="card-header">
              <div className="card-header-icon">🎬</div>
              3D Animation Controls
            </div>
            <div style={{ marginTop: 12, color: '#a3aed0', fontSize: 14 }}>
              <div style={{ marginBottom: 8 }}>
                <strong>🖱️ Mouse Controls:</strong>
              </div>
              <ul style={{ marginLeft: 20, lineHeight: 1.8 }}>
                <li><strong>Left Click + Drag:</strong> Rotate camera around gear</li>
                <li><strong>Scroll Wheel:</strong> Zoom in/out (min: 3, max: 12 units)</li>
                <li><strong>Right Click + Drag:</strong> Pan disabled for stability</li>
              </ul>
              <div style={{ marginTop: 12, marginBottom: 8 }}>
                <strong>⚙️ Animation Features:</strong>
              </div>
              <ul style={{ marginLeft: 20, lineHeight: 1.8 }}>
                <li>Real-time gear rotation based on current RPM sensor value</li>
                <li>Vibration effects visualized through gear wobble</li>
                <li>Health-based color coding (green = healthy, red = fault)</li>
                <li>Factory environment with atmospheric particles</li>
                <li>Smooth transitions when switching gear types</li>
              </ul>
              <div style={{ marginTop: 12, padding: 12, background: 'rgba(5, 205, 153, 0.1)', borderRadius: 8, border: '1px solid rgba(5, 205, 153, 0.3)' }}>
                <strong style={{ color: '#05cd99' }}>💡 Tip:</strong> Use the gear selector above to switch between Helical, Spur, Bevel, and Worm gears. The 3D scene will smoothly transition to show the selected gear type.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab: Cost Impact ─────────────────────────────── */}
      {activeTab === 'cost' && (
        <CostImpact gearConfig={gc} gearType={gearType} gearName={gearName} rul={rul} fault={fault} />
      )}

      {/* ── Tab: Model Comparison ────────────────────────── */}
      {activeTab === 'models' && (
        <ModelComparison compData={compData} />
      )}

      {/* ── Floating AI Copilot Widget (persists across all tabs) ── */}
      <FloatingCopilot
        sensorValues={sensorValues}
        gearId={gearName}
        gearType={gearType}
        fault={fault}
        conf={conf}
        score={healthScore}
      />
    </div>
  );
}
