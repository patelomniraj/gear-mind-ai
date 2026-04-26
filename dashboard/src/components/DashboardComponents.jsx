import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar,
         AreaChart, Area, PieChart, Pie, Cell, RadarChart, Radar,
         PolarGrid, PolarAngleAxis, PolarRadiusAxis, LineChart, Line, Legend } from 'recharts';
import * as api from '../api/gearApi';

// Re-export new components
export { LimeChart, RULSection, ReportPDFButton, FloatingCopilot, HistoryDashboard } from './NewComponents';

// ── StatCard (Horizon Style with Icon) ──────────────────
export function StatCard({ label, value, color, icon }) {
  const iconColors = { blue:'blue', green:'green', red:'red', amber:'amber', purple:'purple' };
  const ic = iconColors[icon] || 'blue';
  return (
    <div className="stat-card">
      <div className={`icon-box ${ic}`}>{icon === 'green' ? '✅' : icon === 'red' ? '⚠️' : icon === 'amber' ? '⏱' : icon === 'purple' ? '💜' : '📊'}</div>
      <div className="info">
        <div className="label">{label}</div>
        <div className="value" style={color ? { color } : {}}>{value}</div>
      </div>
    </div>
  );
}

// ── GearHealthGauge ─────────────────────────────────────
export function GearHealthGauge({ score, fault, gearName }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [displayScore, setDisplayScore] = useState(0);
  const color = score >= 70 ? '#05cd99' : score >= 40 ? '#ffb547' : '#ee5d50';
  const statusText = score >= 70 ? 'EXCELLENT' : score >= 40 ? 'CAUTION' : 'CRITICAL';
  const statusIcon = score >= 70 ? '✓' : score >= 40 ? '⚠' : '✕';
  const data = [{ value: animatedScore, fill: color }];
  
  useEffect(() => {
    let start = animatedScore;
    const end = score;
    const duration = 1500;
    const startTime = Date.now();
    
    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const current = start + (end - start) * easeOutQuart;
      setAnimatedScore(Math.round(current));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [score]);

  // Separate counter animation for display
  useEffect(() => {
    let start = displayScore;
    const end = score;
    const duration = 1200;
    const startTime = Date.now();
    
    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * easeOutCubic;
      setDisplayScore(Math.round(current));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [score]);
  
  return (
    <div className="card health-gauge-card">
      <div className="card-header"><div className="card-header-icon">🎯</div> Gear Health Gauge</div>
      <div style={{ textAlign: 'center', position: 'relative', padding: '20px 0' }}>
        <ResponsiveContainer width="100%" height={240}>
          <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="85%"
            startAngle={180} endAngle={0} data={data} barSize={20}>
            <defs>
              <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#422afb" />
                <stop offset="50%" stopColor="#7551ff" />
                <stop offset="100%" stopColor={color} />
              </linearGradient>
              <filter id="gaugeShadow">
                <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.25"/>
              </filter>
              <filter id="gaugeGlow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <RadialBar 
              background={{ fill: '#f4f7fe' }} 
              dataKey="value" 
              cornerRadius={12} 
              fill="url(#gaugeGrad)"
              filter="url(#gaugeShadow)"
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="gauge-center-content">
          <div className="gauge-status-badge" style={{ 
            background: `${color}15`, 
            color: color,
            border: `2px solid ${color}40`
          }}>
            <span className="gauge-status-icon">{statusIcon}</span>
            <span className="gauge-status-text">{statusText}</span>
          </div>
          <div className="gauge-score-display" style={{ color: color }}>
            {displayScore}
          </div>
          <div className="gauge-score-label">Health Score</div>
          <div className="gauge-pulse" style={{ background: `${color}22`, borderColor: `${color}40` }} />
          <div className="gauge-glow" style={{ background: `radial-gradient(circle, ${color}20 0%, transparent 70%)` }} />
        </div>
        <div style={{ fontSize: 15, fontWeight: 700, color: '#1b2559', marginTop: 16 }}>{gearName}</div>
        <div style={{ fontSize: 13, color: '#a3aed0', marginTop: 4 }}>{fault}</div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 24, fontSize: 11, fontWeight: 600, marginTop: 16, paddingTop: 16, borderTop: '1px solid #f4f7fe' }}>
        <span style={{ color: '#ee5d50' }}>● Critical (0-39)</span>
        <span style={{ color: '#ffb547' }}>● Warning (40-69)</span>
        <span style={{ color: '#05cd99' }}>● Safe (70-100)</span>
      </div>
    </div>
  );
}

// ── FaultCountdown ──────────────────────────────────────
export function FaultCountdown({ rul, fault, dailyCycles }) {
  const daysLeft = rul / dailyCycles;
  const days = Math.floor(daysLeft);
  const hours = Math.floor((daysLeft % 1) * 24);
  const cfg = fault === 'Major Fault'
    ? { color: '#ee5d50', bg: '#fef1f0', text: '⚠️ IMMEDIATE ACTION', pulse: 'red', action: 'Stop gear. Schedule emergency maintenance.' }
    : fault === 'Minor Fault'
    ? { color: '#ffb547', bg: '#fff8eb', text: '⚠️ SCHEDULE MAINTENANCE', pulse: 'amber', action: 'Plan maintenance within this week.' }
    : { color: '#05cd99', bg: '#e6faf5', text: '✅ OPERATING NORMALLY', pulse: 'green', action: 'Continue operation. Next check at scheduled interval.' };

  return (
    <div className="card">
      <div className="card-header"><div className="card-header-icon">⏱</div> Fault Countdown</div>
      <div className="countdown-box" style={{ background: cfg.bg }}>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: 2, color: cfg.color }}>ESTIMATED TIME TO MAJOR FAULT</div>
        <div className="countdown-digits">
          <div className="countdown-unit">
            <div className="countdown-number" style={{ color: cfg.color }}>{String(days).padStart(3, '0')}</div>
            <div className="countdown-label">DAYS</div>
          </div>
          <div style={{ fontSize: 36, color: cfg.color, alignSelf: 'center', fontWeight: 300 }}>:</div>
          <div className="countdown-unit">
            <div className="countdown-number" style={{ color: cfg.color }}>{String(hours).padStart(2, '0')}</div>
            <div className="countdown-label">HOURS</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 10 }}>
          <div className={`pulse-dot ${cfg.pulse}`} />
          <span style={{ fontSize: 13, fontWeight: 700, color: cfg.color }}>{cfg.text}</span>
        </div>
        <div style={{ fontSize: 12, color: '#a3aed0' }}>{cfg.action}</div>
        <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid #e9ecf1', fontSize: 11, color: '#a3aed0' }}>
          {rul.toLocaleString()} cycles ÷ {dailyCycles.toLocaleString()} daily
        </div>
      </div>
    </div>
  );
}

// ── FaultProbabilityBar ─────────────────────────────────
export function FaultProbabilityBar({ probs }) {
  const colors = { 'No Fault': '#05cd99', 'Minor Fault': '#ffb547', 'Major Fault': '#ee5d50' };
  const data = Object.entries(probs).map(([k, v]) => ({ name: k, value: Math.round(v * 1000) / 10 }));
  return (
    <div>
      <div className="card-header" style={{fontSize:14}}>Fault Probability</div>
      <ResponsiveContainer width="100%" height={130}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 50, top: 5, bottom: 5 }}>
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis type="category" dataKey="name" tick={{ fill: '#a3aed0', fontSize: 12, fontWeight: 500 }} width={95} />
          <Bar dataKey="value" radius={[0, 8, 8, 0]} label={{ position: 'right', fill: '#2b3674', fontSize: 12, fontWeight: 700, formatter: v => `${v}%` }}>
            {data.map((d, i) => <Cell key={i} fill={colors[d.name] || '#3965ff'} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// ── SensorStatus ────────────────────────────────────────
export function SensorStatus({ sensors, gearConfig, gearType }) {
  // Define checks based on gear type
  let checks = [];
  
  if (gearType === 'Worm') {
    // Worm gear has 13 different sensors
    checks = [
      { name: 'Oil Temperature', val: sensors.oil_temp, limit: 120, unit: '°C', inv: false },
      { name: 'Axial Vibration', val: sensors.ax_vib, limit: 6.0, unit: 'mm/s', inv: false },
      { name: 'Radial Vibration', val: sensors.rad_vib, limit: 3.0, unit: 'mm/s', inv: false },
      { name: 'Copper PPM', val: sensors.cu_ppm, limit: 100, unit: 'ppm', inv: false },
      { name: 'Iron PPM', val: sensors.fe_ppm, limit: 20, unit: 'ppm', inv: false },
      { name: 'Friction Coeff', val: sensors.friction, limit: 0.06, unit: '', inv: false },
      { name: 'Efficiency', val: sensors.eff, limit: 75, unit: '%', inv: true },
    ];
  } else if (gearType === 'Spur') {
    // Spur gear has 6 sensors
    checks = [
      { name: 'Speed', val: sensors.load, limit: 2500, unit: 'RPM', inv: false },
      { name: 'Vibration', val: sensors.vib, limit: 8.0, unit: 'mm/s', inv: false },
      { name: 'Temperature', val: sensors.temp, limit: 90, unit: '°C', inv: false },
      { name: 'Shock Load', val: sensors.wear, limit: 4.0, unit: 'g', inv: false },
      { name: 'Noise', val: sensors.lube * 100, limit: 85, unit: 'dB', inv: false },
    ];
  } else {
    // Helical and Bevel use standard sensors
    checks = [
      { name: 'Vibration', val: sensors.vib, limit: gearConfig.vib_limit, unit: 'mm/s', inv: false },
      { name: 'Temperature', val: sensors.temp, limit: gearConfig.temp_limit, unit: '°C', inv: false },
      { name: 'Wear', val: sensors.wear, limit: gearConfig.wear_limit, unit: 'mm', inv: false },
      { name: 'Lubrication', val: sensors.lube, limit: gearConfig.lube_limit, unit: '', inv: true },
      { name: 'Efficiency', val: sensors.eff, limit: gearConfig.eff_limit, unit: '%', inv: true },
    ];
  }
  
  return (
    <div>
      <div className="card-header" style={{fontSize:14}}>Sensor Status</div>
      {checks.map(c => {
        // Handle undefined values gracefully
        if (c.val === undefined || c.val === null) return null;
        
        const isBad = c.inv ? c.val < c.limit : c.val > c.limit;
        const pct = Math.min(100, (c.val / c.limit) * 100);
        const color = isBad ? '#ee5d50' : '#05cd99';
        return (
          <div key={c.name} className={`sensor-card ${isBad ? 'bad' : ''}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontSize: 13, color: '#2b3674', fontWeight: 600 }}>{isBad ? '🔴' : '🟢'} {c.name}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color, fontFamily: 'var(--font-mono)' }}>{c.val.toFixed(2)}{c.unit}</span>
            </div>
            <div className="sensor-bar-track">
              <div className="sensor-bar-fill" style={{ width: `${Math.min(100, Math.abs(pct))}%`, background: `linear-gradient(90deg,${color}88,${color})` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ChatCopilot replaced by FloatingCopilot in NewComponents.jsx

// ── CostImpact ──────────────────────────────────────────
export function CostImpact({ gearConfig, gearType, gearName, rul, fault }) {
  const { repair_cost, overhaul_cost, failure_cost, daily_cycles } = gearConfig;
  const saved = failure_cost - repair_cost;
  const daysLeft = Math.floor(rul / daily_cycles);
  const costData = [
    { name: 'Preventive', value: repair_cost, color: '#05cd99' },
    { name: 'Delayed', value: overhaul_cost, color: '#ffb547' },
    { name: 'Failure', value: failure_cost, color: '#ee5d50' },
  ];

  return (
    <div className="fade-in">
      <div className="section-title">💰 Maintenance Cost Impact</div>
      <div className="grid-3" style={{ marginBottom: 24 }}>
        {[
          { title: '✅ Preventive', sub: 'Act Now', cost: repair_cost, color: '#05cd99', bg: '#e6faf5', dt: '4-6 hours', prod: 'Minimal', risk: 'Low' },
          { title: '⚠️ Delayed', sub: 'Wait 1 Month', cost: overhaul_cost, color: '#ffb547', bg: '#fff8eb', dt: '1-2 days', prod: 'Significant', risk: 'Medium-High' },
          { title: '🔴 Failure', sub: 'No Maintenance', cost: failure_cost, color: '#ee5d50', bg: '#fef1f0', dt: '5-7 days', prod: 'Severe', risk: 'Critical' },
        ].map(c => (
          <div key={c.title} className="cost-card card" style={{ background: c.bg }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: c.color, marginBottom: 16 }}>{c.title}<br/><span style={{ fontSize: 11, color: '#a3aed0' }}>{c.sub}</span></div>
            <div className="cost-value" style={{ color: c.color }}>₹{c.cost.toLocaleString()}</div>
            <div style={{ marginTop: 20 }}>
              {[['Downtime', c.dt], ['Production', c.prod], ['Risk', c.risk]].map(([l, v]) => (
                <div key={l} className="cost-row"><span style={{ color: '#a3aed0' }}>{l}</span><span style={{ color: c.color, fontWeight: 600 }}>{v}</span></div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ background: 'linear-gradient(135deg,#e6faf5,#f0fdf8)', textAlign: 'center', marginBottom: 24 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#05cd99', letterSpacing: 1, marginBottom: 12 }}>💰 TOTAL SAVINGS</div>
        <div style={{ fontSize: 52, fontWeight: 900, color: '#05cd99' }}>₹{saved.toLocaleString()}</div>
        <div style={{ fontSize: 14, color: '#a3aed0', marginTop: 8 }}>Saved per gear unit by catching faults early</div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 48, marginTop: 28 }}>
          {[[Math.floor(rul / (daily_cycles / 8)) + 'h', 'Downtime Prevented', '#422afb'],
            [rul.toLocaleString(), 'Remaining Cycles', '#7551ff'],
            [daysLeft + 'd', 'Days to Act', '#ffb547']].map(([v, l, c]) => (
            <div key={l} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: c }}>{v}</div>
              <div style={{ fontSize: 12, color: '#a3aed0' }}>{l}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-header-icon">📊</div> Cost Comparison</div>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={costData} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
            <XAxis dataKey="name" tick={{ fill: '#a3aed0', fontSize: 13, fontWeight: 600 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#a3aed0', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
            <Tooltip formatter={v => `₹${v.toLocaleString()}`} contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
            <Bar dataKey="value" radius={[10, 10, 0, 0]} label={{ position: 'top', fill: '#2b3674', fontSize: 12, fontWeight: 700, formatter: v => `₹${v.toLocaleString()}` }}>
              {costData.map((d, i) => <Cell key={i} fill={d.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ── ShapChart ────────────────────────────────────────────
export function ShapChart({ shapValues, gearName, gearType, fault }) {
  if (!shapValues || Object.keys(shapValues).length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#a3aed0' }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#2b3674', marginBottom: 8 }}>
          SHAP Analysis Unavailable
        </div>
        <div style={{ fontSize: 12, lineHeight: 1.6 }}>
          {gearType === 'Spur' && 'Spur gear SHAP artifacts may not be loaded.'}
          {gearType === 'Bevel' && 'Bevel gear SHAP artifacts may not be loaded.'}
          {gearType === 'Helical' && 'Helical gear SHAP artifacts may not be loaded.'}
          <br />
          Check backend console for SHAP loading status.
        </div>
      </div>
    );
  }
  const data = Object.entries(shapValues).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])).map(([k, v]) => ({ feature: k, value: Math.round(v * 10000) / 10000 }));
  return (
    <div>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 80, top: 10, bottom: 10 }}>
          <XAxis type="number" tick={{ fill: '#a3aed0', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="feature" tick={{ fill: '#2b3674', fontSize: 12, fontWeight: 600 }} width={160} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
          <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={28} label={{ position: 'right', fill: '#2b3674', fontSize: 11, fontWeight: 600, formatter: v => v > 0 ? `+${v}` : v }}>
            {data.map((d, i) => <Cell key={i} fill={d.value > 0 ? '#ee5d50' : '#05cd99'} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, color: '#a3aed0', marginTop: 12, textAlign: 'center', fontWeight: 600 }}>
        🟢 Protective factors (reduce fault risk) | 🔴 Risk factors (increase fault likelihood)
      </div>
    </div>
  );
}

// ── ModelComparison ──────────────────────────────────────
export function ModelComparison({ compData }) {
  const [selectedGear, setSelectedGear] = useState('Overall');
  const [comparisonData, setComparisonData] = useState(null);
  const [viewMode, setViewMode] = useState('table'); // 'table', 'radar', 'insights'
  const [selectedMetric, setSelectedMetric] = useState('auc'); // For highlighting in table
  
  useEffect(() => {
    // Fetch structured comparison data
    fetch('http://localhost:8000/api/models/comparison')
      .then(res => res.json())
      .then(data => setComparisonData(data))
      .catch(console.error);
  }, []);
  
  if (!comparisonData) {
    return <div className="card"><p style={{color:'#a3aed0'}}>Loading model data...</p></div>;
  }
  
  // Prepare data based on selection
  let models = [];
  let chartData = [];
  let radarData = [];
  let overallStats = null;
  
  if (selectedGear === 'Overall') {
    // Show overall comparison across all gear types
    overallStats = comparisonData.overall;
    
    // Create models array from all gear types
    Object.entries(comparisonData.gear_types || {}).forEach(([gearType, gearModels]) => {
      Object.entries(gearModels).forEach(([modelName, metrics]) => {
        models.push({
          name: `${gearType} - ${modelName}`,
          gearType,
          modelName,
          ...metrics
        });
      });
    });
    
    models.sort((a, b) => (b.auc || 0) - (a.auc || 0));
    chartData = models.slice(0, 10).map(m => ({
      name: m.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM'),
      Accuracy: +((m.accuracy || 0) * 100).toFixed(1),
      F1: +((m.f1 || 0) * 100).toFixed(1),
      AUC: +((m.auc || 0) * 100).toFixed(1),
      CV: +((m.cv_mean || 0) * 100).toFixed(1)
    }));
    
    // Radar chart data for top 5 models
    radarData = models.slice(0, 5).map(m => ({
      model: m.modelName.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM'),
      Accuracy: +((m.accuracy || 0) * 100).toFixed(1),
      F1: +((m.f1 || 0) * 100).toFixed(1),
      AUC: +((m.auc || 0) * 100).toFixed(1),
      CV: +((m.cv_mean || 0) * 100).toFixed(1)
    }));
  } else {
    // Show specific gear type comparison
    const gearModels = comparisonData.gear_types?.[selectedGear] || {};
    models = Object.entries(gearModels)
      .map(([name, m]) => ({ name, modelName: name, gearType: selectedGear, ...m }))
      .sort((a, b) => (b.auc || 0) - (a.auc || 0));
    
    chartData = models.map(m => ({
      name: m.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM'),
      Accuracy: +((m.accuracy || 0) * 100).toFixed(1),
      F1: +((m.f1 || 0) * 100).toFixed(1),
      AUC: +((m.auc || 0) * 100).toFixed(1),
      CV: +((m.cv_mean || 0) * 100).toFixed(1)
    }));
    
    // Radar chart data for all models in this gear
    radarData = models.map(m => ({
      model: m.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM'),
      Accuracy: +((m.accuracy || 0) * 100).toFixed(1),
      F1: +((m.f1 || 0) * 100).toFixed(1),
      AUC: +((m.auc || 0) * 100).toFixed(1),
      CV: +((m.cv_mean || 0) * 100).toFixed(1)
    }));
  }
  
  // Calculate performance grades
  const getGrade = (value) => {
    if (value >= 0.95) return { grade: 'A+', color: '#05cd99', bg: '#e6faf5' };
    if (value >= 0.90) return { grade: 'A', color: '#05cd99', bg: '#e6faf5' };
    if (value >= 0.85) return { grade: 'B+', color: '#7551ff', bg: '#ece5ff' };
    if (value >= 0.80) return { grade: 'B', color: '#ffb547', bg: '#fff8eb' };
    if (value >= 0.75) return { grade: 'C+', color: '#ffb547', bg: '#fff8eb' };
    return { grade: 'C', color: '#ee5d50', bg: '#fef1f0' };
  };

  // Calculate model rankings and insights
  const modelInsights = models.length > 0 ? {
    bestAccuracy: [...models].sort((a, b) => (b.accuracy || 0) - (a.accuracy || 0))[0],
    bestF1: [...models].sort((a, b) => (b.f1 || 0) - (a.f1 || 0))[0],
    bestAuc: [...models].sort((a, b) => (b.auc || 0) - (a.auc || 0))[0],
    mostConsistent: [...models].sort((a, b) => (a.cv_std || 1) - (b.cv_std || 1))[0],
    avgAccuracy: models.reduce((sum, m) => sum + (m.accuracy || 0), 0) / models.length,
    avgF1: models.reduce((sum, m) => sum + (m.f1 || 0), 0) / models.length,
    avgAuc: models.reduce((sum, m) => sum + (m.auc || 0), 0) / models.length,
  } : null;

  return (
    <div className="fade-in">
      <div className="section-title">🏆 Advanced Model Performance Analysis</div>
      
      {/* Enhanced Controls */}
      <div className="card" style={{ marginBottom: 24, padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#2b3674' }}>Gear Type:</span>
            <select 
              value={selectedGear}
              onChange={(e) => setSelectedGear(e.target.value)}
              style={{
                padding: '8px 16px',
                borderRadius: 8,
                border: '1px solid #e0e5f2',
                background: 'white',
                fontSize: 13,
                fontWeight: 600,
                color: '#2b3674',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="Overall">🌐 Overall Comparison (All Gears)</option>
              <option value="Helical">⚙️ Helical Gear</option>
              <option value="Spur">🔧 Spur Gear</option>
              <option value="Bevel">🔩 Bevel Gear</option>
              <option value="Worm">🌀 Worm Gear</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', gap: 8 }}>
            <button 
              onClick={() => setViewMode('table')}
              style={{
                padding: '8px 16px',
                borderRadius: 8,
                border: viewMode === 'table' ? '2px solid #422afb' : '1px solid #e0e5f2',
                background: viewMode === 'table' ? 'linear-gradient(135deg, #422afb 0%, #7551ff 100%)' : 'white',
                color: viewMode === 'table' ? 'white' : '#a3aed0',
                fontSize: 13,
                fontWeight: 700,
                cursor: 'pointer',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxShadow: viewMode === 'table' ? '0 4px 12px rgba(66, 42, 251, 0.3)' : 'none'
              }}
            >
              📋 Table View
            </button>
            <button 
              onClick={() => setViewMode('radar')}
              style={{
                padding: '8px 16px',
                borderRadius: 8,
                border: viewMode === 'radar' ? '2px solid #422afb' : '1px solid #e0e5f2',
                background: viewMode === 'radar' ? 'linear-gradient(135deg, #422afb 0%, #7551ff 100%)' : 'white',
                color: viewMode === 'radar' ? 'white' : '#a3aed0',
                fontSize: 13,
                fontWeight: 700,
                cursor: 'pointer',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxShadow: viewMode === 'radar' ? '0 4px 12px rgba(66, 42, 251, 0.3)' : 'none'
              }}
            >
              🎯 Radar View
            </button>
            <button 
              onClick={() => setViewMode('insights')}
              style={{
                padding: '8px 16px',
                borderRadius: 8,
                border: viewMode === 'insights' ? '2px solid #422afb' : '1px solid #e0e5f2',
                background: viewMode === 'insights' ? 'linear-gradient(135deg, #422afb 0%, #7551ff 100%)' : 'white',
                color: viewMode === 'insights' ? 'white' : '#a3aed0',
                fontSize: 13,
                fontWeight: 700,
                cursor: 'pointer',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxShadow: viewMode === 'insights' ? '0 4px 12px rgba(66, 42, 251, 0.3)' : 'none'
              }}
            >
              💡 Insights View
            </button>
          </div>
        </div>
      </div>
      
      {/* Overall Statistics Card */}
      {selectedGear === 'Overall' && overallStats && (
        <div className="card" style={{ marginBottom: 24, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <div style={{ padding: '24px', color: 'white' }}>
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>🏆</span> Overall System Performance
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16 }}>
              <div>
                <div style={{ fontSize: 11, opacity: 0.9, marginBottom: 4 }}>Total Gear Types</div>
                <div style={{ fontSize: 28, fontWeight: 800 }}>{overallStats.total_gear_types}</div>
              </div>
              <div>
                <div style={{ fontSize: 11, opacity: 0.9, marginBottom: 4 }}>Total Models</div>
                <div style={{ fontSize: 28, fontWeight: 800 }}>{overallStats.total_models}</div>
              </div>
              <div>
                <div style={{ fontSize: 11, opacity: 0.9, marginBottom: 4 }}>Avg Accuracy</div>
                <div style={{ fontSize: 28, fontWeight: 800 }}>{(overallStats.avg_accuracy * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div style={{ fontSize: 11, opacity: 0.9, marginBottom: 4 }}>Avg F1 Score</div>
                <div style={{ fontSize: 28, fontWeight: 800 }}>{(overallStats.avg_f1 * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div style={{ fontSize: 11, opacity: 0.9, marginBottom: 4 }}>Avg AUC</div>
                <div style={{ fontSize: 28, fontWeight: 800 }}>{(overallStats.avg_auc * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div style={{ fontSize: 11, opacity: 0.9, marginBottom: 4 }}>Best AUC</div>
                <div style={{ fontSize: 28, fontWeight: 800 }}>{(overallStats.best_auc * 100).toFixed(1)}%</div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Performance Grade Cards */}
      {selectedGear !== 'Overall' && models.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 24 }}>
          {models.slice(0, 3).map((m, i) => {
            const grade = getGrade(m.auc || 0);
            return (
              <div key={m.name} className="card" style={{ background: grade.bg, border: `2px solid ${grade.color}20`, position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: -20, right: -20, width: 100, height: 100, background: `${grade.color}10`, borderRadius: '50%' }} />
                <div style={{ padding: '20px', position: 'relative' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: '#a3aed0', letterSpacing: 1 }}>
                      {i === 0 ? '🏆 BEST' : i === 1 ? '🥈 SECOND' : '🥉 THIRD'}
                    </span>
                    <span style={{ fontSize: 24, fontWeight: 800, color: grade.color }}>{grade.grade}</span>
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#1b2559', marginBottom: 6 }}>
                    {m.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM')}
                  </div>
                  <div style={{ fontSize: 11, color: '#a3aed0', marginBottom: 16 }}>
                    {selectedGear} Gear
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <div style={{ fontSize: 10, color: '#a3aed0', marginBottom: 4 }}>Accuracy</div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: grade.color }}>{((m.accuracy || 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 10, color: '#a3aed0', marginBottom: 4 }}>AUC</div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: grade.color }}>{((m.auc || 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 10, color: '#a3aed0', marginBottom: 4 }}>F1 Score</div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: grade.color }}>{((m.f1 || 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 10, color: '#a3aed0', marginBottom: 4 }}>CV Mean</div>
                      <div style={{ fontSize: 16, fontWeight: 700, color: grade.color }}>{((m.cv_mean || 0) * 100).toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {/* Radar Chart View */}
      {viewMode === 'radar' && radarData.length > 0 && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <div className="card-header-icon">🎯</div>
            Multi-Dimensional Performance Radar
          </div>
          <ResponsiveContainer width="100%" height={500}>
            <RadarChart data={radarData.length > 0 ? [
              { metric: 'Accuracy', ...Object.fromEntries(radarData.map(m => [m.model, m.Accuracy])) },
              { metric: 'F1 Score', ...Object.fromEntries(radarData.map(m => [m.model, m.F1])) },
              { metric: 'AUC', ...Object.fromEntries(radarData.map(m => [m.model, m.AUC])) },
              { metric: 'CV Mean', ...Object.fromEntries(radarData.map(m => [m.model, m.CV])) }
            ] : []}>
              <PolarGrid stroke="#e0e5f2" strokeWidth={2} />
              <PolarAngleAxis dataKey="metric" tick={{ fill: '#2b3674', fontSize: 13, fontWeight: 700 }} />
              <PolarRadiusAxis angle={90} domain={[70, 100]} tick={{ fill: '#a3aed0', fontSize: 11 }} />
              {radarData.slice(0, 5).map((m, i) => (
                <Radar
                  key={m.model}
                  name={m.model}
                  dataKey={m.model}
                  stroke={['#422afb', '#05cd99', '#ffb547', '#ee5d50', '#7551ff'][i]}
                  fill={['#422afb', '#05cd99', '#ffb547', '#ee5d50', '#7551ff'][i]}
                  fillOpacity={0.25}
                  strokeWidth={3}
                />
              ))}
              <Legend wrapperStyle={{ paddingTop: 20 }} />
              <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)', padding: '12px 16px' }} />
            </RadarChart>
          </ResponsiveContainer>
          <div style={{ padding: '20px', fontSize: 13, color: '#2b3674', textAlign: 'center', background: '#f4f7fe', borderRadius: 12, margin: '0 20px 20px' }}>
            <strong>Radar Analysis:</strong> Larger area indicates better overall performance. Models closer to the outer edge excel across all metrics.
          </div>
        </div>
      )}
      
      {/* Insights View */}
      {viewMode === 'insights' && modelInsights && (
        <div className="fade-in">
          {/* Top Performers Grid */}
          <div className="grid-3" style={{ marginBottom: 24 }}>
            {/* Best Overall (AUC) */}
            <div className="card" style={{ background: 'linear-gradient(135deg, #05cd99 0%, #00b383 100%)', color: 'white', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: -30, right: -30, width: 150, height: 150, background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }} />
              <div style={{ padding: '24px', position: 'relative' }}>
                <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, opacity: 0.9, letterSpacing: 1 }}>🏆 BEST OVERALL (AUC)</div>
                <div style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
                  {modelInsights.bestAuc?.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM')}
                </div>
                <div style={{ fontSize: 12, opacity: 0.9, marginBottom: 16 }}>
                  {selectedGear === 'Overall' ? modelInsights.bestAuc?.gearType + ' Gear' : selectedGear + ' Gear'}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <div style={{ fontSize: 10, opacity: 0.8 }}>AUC</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>{((modelInsights.bestAuc?.auc || 0) * 100).toFixed(2)}%</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 10, opacity: 0.8 }}>Accuracy</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>{((modelInsights.bestAuc?.accuracy || 0) * 100).toFixed(2)}%</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Most Consistent */}
            <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: -30, right: -30, width: 150, height: 150, background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }} />
              <div style={{ padding: '24px', position: 'relative' }}>
                <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, opacity: 0.9, letterSpacing: 1 }}>🎯 MOST CONSISTENT</div>
                <div style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
                  {modelInsights.mostConsistent?.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM')}
                </div>
                <div style={{ fontSize: 12, opacity: 0.9, marginBottom: 16 }}>
                  Lowest Variance
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <div style={{ fontSize: 10, opacity: 0.8 }}>CV Std</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>{(modelInsights.mostConsistent?.cv_std || 0).toFixed(4)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 10, opacity: 0.8 }}>CV Mean</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>{((modelInsights.mostConsistent?.cv_mean || 0) * 100).toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Best F1 Score */}
            <div className="card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: -30, right: -30, width: 150, height: 150, background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }} />
              <div style={{ padding: '24px', position: 'relative' }}>
                <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, opacity: 0.9, letterSpacing: 1 }}>⚖️ BEST BALANCE (F1)</div>
                <div style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
                  {modelInsights.bestF1?.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM')}
                </div>
                <div style={{ fontSize: 12, opacity: 0.9, marginBottom: 16 }}>
                  Best Precision-Recall
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <div style={{ fontSize: 10, opacity: 0.8 }}>F1 Score</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>{((modelInsights.bestF1?.f1 || 0) * 100).toFixed(2)}%</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 10, opacity: 0.8 }}>Accuracy</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>{((modelInsights.bestF1?.accuracy || 0) * 100).toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Analysis */}
          <div className="grid-2" style={{ marginBottom: 24 }}>
            {/* Performance Distribution */}
            <div className="card">
              <div className="card-header">
                <div className="card-header-icon">📊</div>
                Performance Distribution by Grade
              </div>
              <div style={{ padding: '20px' }}>
                {['A+ (≥95%)', 'A (90-95%)', 'B+ (85-90%)', 'B (80-85%)', 'C+ (75-80%)', 'C (<75%)'].map((grade, i) => {
                  const ranges = [[0.95, 1], [0.90, 0.95], [0.85, 0.90], [0.80, 0.85], [0.75, 0.80], [0, 0.75]];
                  const count = models.filter(m => m.auc >= ranges[i][0] && m.auc < ranges[i][1]).length;
                  const percentage = (count / models.length) * 100;
                  const colors = ['#05cd99', '#05cd99', '#7551ff', '#ffb547', '#ffb547', '#ee5d50'];
                  return (
                    <div key={grade} style={{ marginBottom: 16 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontSize: 13, fontWeight: 700, color: '#2b3674' }}>{grade}</span>
                        <span style={{ fontSize: 13, fontWeight: 700, color: colors[i] }}>{count} models ({percentage.toFixed(0)}%)</span>
                      </div>
                      <div style={{ height: 10, background: '#f4f7fe', borderRadius: 6, overflow: 'hidden' }}>
                        <div style={{ 
                          width: `${percentage}%`, 
                          height: '100%', 
                          background: `linear-gradient(90deg, ${colors[i]}, ${colors[i]}dd)`,
                          transition: 'width 0.5s ease',
                          borderRadius: 6
                        }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Average Performance Metrics */}
            <div className="card">
              <div className="card-header">
                <div className="card-header-icon">📈</div>
                Average Performance Metrics
              </div>
              <div style={{ padding: '20px' }}>
                {[
                  { label: 'Average Accuracy', value: modelInsights.avgAccuracy, color: '#422afb', icon: '🎯' },
                  { label: 'Average F1 Score', value: modelInsights.avgF1, color: '#05cd99', icon: '⚖️' },
                  { label: 'Average AUC', value: modelInsights.avgAuc, color: '#ffb547', icon: '📊' }
                ].map(metric => (
                  <div key={metric.label} style={{ marginBottom: 20 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: '#2b3674' }}>
                        {metric.icon} {metric.label}
                      </span>
                      <span style={{ fontSize: 18, fontWeight: 800, color: metric.color }}>
                        {(metric.value * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div style={{ height: 8, background: '#f4f7fe', borderRadius: 4, overflow: 'hidden' }}>
                      <div style={{ 
                        width: `${metric.value * 100}%`, 
                        height: '100%', 
                        background: `linear-gradient(90deg, ${metric.color}, ${metric.color}dd)`,
                        borderRadius: 4
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <div className="card-header-icon">💡</div>
              AI-Powered Recommendations
            </div>
            <div style={{ padding: '24px' }}>
              <div className="grid-2" style={{ gap: 20 }}>
                <div style={{ padding: '20px', background: 'linear-gradient(135deg, #e6faf5 0%, #f0fdf8 100%)', borderRadius: 12, border: '2px solid #05cd9930' }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#05cd99', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 20 }}>✅</span> Recommended for Production
                  </div>
                  <div style={{ fontSize: 13, color: '#2b3674', lineHeight: 1.7, marginBottom: 12 }}>
                    <strong>{modelInsights.bestAuc?.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM')}</strong> demonstrates exceptional performance with {((modelInsights.bestAuc?.auc || 0) * 100).toFixed(2)}% AUC.
                  </div>
                  <div style={{ fontSize: 12, color: '#a3aed0', lineHeight: 1.6 }}>
                    This model shows excellent generalization with CV std of {(modelInsights.bestAuc?.cv_std || 0).toFixed(4)}, making it highly reliable for production deployment.
                  </div>
                </div>
                
                <div style={{ padding: '20px', background: 'linear-gradient(135deg, #fff8eb 0%, #fffbf0 100%)', borderRadius: 12, border: '2px solid #ffb54730' }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#ffb547', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 20 }}>⚠️</span> Consider for Improvement
                  </div>
                  <div style={{ fontSize: 13, color: '#2b3674', lineHeight: 1.7, marginBottom: 12 }}>
                    {models[models.length - 1]?.name.replace('Gradient Boosting', 'GBM').replace('Logistic Regression', 'LR').replace('SVM (RBF)', 'SVM')} shows lower performance at {((models[models.length - 1]?.auc || 0) * 100).toFixed(2)}% AUC.
                  </div>
                  <div style={{ fontSize: 12, color: '#a3aed0', lineHeight: 1.6 }}>
                    Consider hyperparameter tuning, feature engineering, or ensemble methods to improve performance.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Enhanced Model Comparison Table */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-header-icon">📋</div>
          {selectedGear === 'Overall' ? `Top 10 Models Across All Gear Types` : `${selectedGear} Gear - All Models`}
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ minWidth: 60 }}>Rank</th>
                <th style={{ minWidth: 180 }}>Model</th>
                {selectedGear === 'Overall' && <th style={{ minWidth: 120 }}>Gear Type</th>}
                <th style={{ minWidth: 100 }}>Accuracy</th>
                <th style={{ minWidth: 100 }}>F1 Score</th>
                <th style={{ minWidth: 100 }}>AUC</th>
                <th style={{ minWidth: 100 }}>CV Mean</th>
                <th style={{ minWidth: 100 }}>CV Std</th>
                <th style={{ minWidth: 80 }}>Grade</th>
              </tr>
            </thead>
            <tbody>
              {models.slice(0, selectedGear === 'Overall' ? 10 : models.length).map((m, i) => {
                const grade = getGrade(m.auc || 0);
                return (
                  <tr key={m.name} style={{ 
                    background: i < 3 ? `${grade.color}08` : 'transparent',
                    transition: 'all 0.2s ease'
                  }}>
                    <td style={{ fontWeight: 700, fontSize: 14 }}>
                      {i === 0 && <span style={{ fontSize: 18 }}>🏆</span>}
                      {i === 1 && <span style={{ fontSize: 18 }}>🥈</span>}
                      {i === 2 && <span style={{ fontSize: 18 }}>🥉</span>}
                      {i > 2 && <span style={{ color: '#a3aed0' }}>{i + 1}</span>}
                    </td>
                    <td style={{ fontWeight: 700, color: '#1b2559', fontSize: 13 }}>
                      {selectedGear === 'Overall' ? m.name.split(' - ')[1] : m.name}
                    </td>
                    {selectedGear === 'Overall' && (
                      <td style={{ fontSize: 12, fontWeight: 600 }}>
                        {m.gearType === 'Helical' && <span style={{ color: '#2563eb' }}>⚙️ Helical</span>}
                        {m.gearType === 'Spur' && <span style={{ color: '#10b981' }}>🔧 Spur</span>}
                        {m.gearType === 'Bevel' && <span style={{ color: '#a78bfa' }}>🔩 Bevel</span>}
                        {m.gearType === 'Worm' && <span style={{ color: '#f59e0b' }}>🌀 Worm</span>}
                      </td>
                    )}
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{((m.accuracy || 0) * 100).toFixed(2)}%</span>
                        <div style={{ flex: 1, height: 4, background: '#f4f7fe', borderRadius: 2, overflow: 'hidden', minWidth: 40 }}>
                          <div style={{ width: `${(m.accuracy || 0) * 100}%`, height: '100%', background: '#422afb', borderRadius: 2 }} />
                        </div>
                      </div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{((m.f1 || 0) * 100).toFixed(2)}%</span>
                        <div style={{ flex: 1, height: 4, background: '#f4f7fe', borderRadius: 2, overflow: 'hidden', minWidth: 40 }}>
                          <div style={{ width: `${(m.f1 || 0) * 100}%`, height: '100%', background: '#05cd99', borderRadius: 2 }} />
                        </div>
                      </div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: i === 0 ? '#05cd99' : '#2b3674' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{((m.auc || 0) * 100).toFixed(2)}%</span>
                        <div style={{ flex: 1, height: 4, background: '#f4f7fe', borderRadius: 2, overflow: 'hidden', minWidth: 40 }}>
                          <div style={{ width: `${(m.auc || 0) * 100}%`, height: '100%', background: '#ffb547', borderRadius: 2 }} />
                        </div>
                      </div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: '#2b3674' }}>
                      {((m.cv_mean || 0) * 100).toFixed(2)}%
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: '#a3aed0' }}>
                      {(m.cv_std || 0).toFixed(4)}
                    </td>
                    <td>
                      <span style={{
                        padding: '6px 12px',
                        borderRadius: 8,
                        fontSize: 12,
                        fontWeight: 700,
                        background: grade.bg,
                        color: grade.color,
                        border: `2px solid ${grade.color}40`,
                        display: 'inline-block'
                      }}>
                        {grade.grade}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Metrics Comparison Chart */}
      <div className="card">
        <div className="card-header">
          <div className="card-header-icon">📊</div>
          Metrics Comparison Chart
        </div>
        <ResponsiveContainer width="100%" height={selectedGear === 'Overall' ? 400 : 300}>
          <BarChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 60 }}>
            <XAxis 
              dataKey="name" 
              tick={{ fill: '#a3aed0', fontSize: 10 }} 
              axisLine={false} 
              tickLine={false}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              domain={[70, 101]} 
              tick={{ fill: '#a3aed0', fontSize: 10 }} 
              axisLine={false} 
              tickLine={false} 
            />
            <Tooltip 
              contentStyle={{ 
                background: 'white', 
                border: 'none', 
                borderRadius: 16, 
                boxShadow: '0 18px 40px rgba(112,144,176,0.12)' 
              }} 
            />
            <Legend />
            <Bar dataKey="Accuracy" fill="#422afb" radius={[8, 8, 0, 0]} />
            <Bar dataKey="F1" fill="#05cd99" radius={[8, 8, 0, 0]} />
            <Bar dataKey="AUC" fill="#ffb547" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ReportGenerator replaced by ReportPDFButton in NewComponents.jsx
// HistoryDashboard enhanced version in NewComponents.jsx

// ── WhatIfOptimizer ─────────────────────────────────────
export function WhatIfOptimizer({ sensors, sensorValues, prediction, gearConfig }) {
  const [locks, setLocks] = useState({});
  const [target, setTarget] = useState(80);  // Changed to health score (80% = good target)
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Detect gear type from prediction or sensorValues
  const gearType = prediction?.gear_type || 'Helical';
  
  // Define features and units based on gear type
  const FEATURE_CONFIGS = {
    Helical: {
      features: ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)', 'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use'],
      units: ['kN', 'Nm', 'mm/s', '°C', 'mm', '', '%', 'cycles'],
      values: [sensors.load, sensors.torque, sensors.vib, sensors.temp, sensors.wear, sensors.lube, sensors.eff, sensors.cycles]
    },
    Spur: {
      features: ['Speed_RPM', 'Torque_Nm', 'Vibration_mm_s', 'Temperature_C', 'Shock_Load_g', 'Noise_dB'],
      units: ['RPM', 'Nm', 'mm/s', '°C', 'g', 'dB'],
      values: [sensors.load, sensors.torque, sensors.vib, sensors.temp, sensors.wear, sensors.lube * 100]
    },
    Bevel: {
      features: ['Load (kN)', 'Torque (Nm)', 'Vibration RMS (mm/s)', 'Temperature (°C)', 'Wear (mm)', 'Lubrication Index', 'Efficiency (%)', 'Cycles in Use'],
      units: ['kN', 'Nm', 'mm/s', '°C', 'mm', '', '%', 'cycles'],
      values: [sensors.load, sensors.torque, sensors.vib, sensors.temp, sensors.wear, sensors.lube, sensors.eff, sensors.cycles]
    },
    Worm: {
      features: ['Worm_RPM', 'Input_Torque', 'Output_Torque', 'Motor_Current', 'Oil_Temp', 'Ambient_Temp', 'Axial_Vib', 'Radial_Vib', 'Cu_PPM', 'Fe_PPM', 'Efficiency_Calc', 'Friction_Coeff', 'Backlash'],
      units: ['RPM', 'Nm', 'Nm', 'A', '°C', '°C', 'mm/s', 'mm/s', 'ppm', 'ppm', '%', '', 'mm'],
      values: [sensors.rpm, sensors.in_torque, sensors.out_torque, sensors.current, sensors.oil_temp, sensors.amb_temp, sensors.ax_vib, sensors.rad_vib, sensors.cu_ppm, sensors.fe_ppm, sensors.eff, sensors.friction, sensors.backlash]
    }
  };
  
  const config = FEATURE_CONFIGS[gearType] || FEATURE_CONFIGS.Helical;
  const FEATURE_COLS = config.features;
  const units = config.units;
  const vals = config.values;

  const runOptimizer = async () => {
    setLoading(true);
    setResult(null); // Clear previous results
    try { 
      // Convert health score to failure probability for backend (inverse relationship)
      const targetFailureProbability = 100 - target;
      
      // Add gear_type to sensor values so backend can detect it
      const sensorValuesWithType = { ...sensorValues, gear_type: gearType };
      
      const res = await api.optimize(sensorValuesWithType, locks, targetFailureProbability); 
      setResult(res); 
    }
    catch (e) { 
      console.error('Optimizer error:', e);
      setResult({ error: e.response?.data?.detail || e.message || 'Optimization failed. Try reducing locked parameters or adjusting target.' }); 
    }
    setLoading(false);
  };

  return (
    <div className="fade-in">
      <div className="card" style={{ background: 'linear-gradient(135deg,#ece5ff,#f4f7fe)', marginBottom: 20 }}>
        <div style={{ fontSize: 18, fontWeight: 800, color: '#1b2559', marginBottom: 6 }}>🔧 What-If Optimizer — {gearType} Gear</div>
        <div style={{ fontSize: 14, color: '#a3aed0' }}>Lock parameters you cannot change. Optimizer uses <strong style={{ color: '#422afb' }}>Differential Evolution</strong> to find safe operating points.</div>
      </div>
      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="card">
          <div className="slider-group">
            <div className="slider-label"><span>Target Health Score (%)</span><span className="slider-value">{target}%</span></div>
            <input type="range" min={50} max={95} step={5} value={target} onChange={e => setTarget(+e.target.value)} />
          </div>
        </div>
        <div className="card">
          <div style={{ fontSize: 13, fontWeight: 700, color: '#1b2559', marginBottom: 10 }}>Parameter Locks</div>
          <div className="grid-4">
            {FEATURE_COLS.map((f, i) => (
              <label key={f} className="lock-toggle">
                <input type="checkbox" checked={locks[f] || false} onChange={e => setLocks({ ...locks, [f]: e.target.checked })} />
                {f.split(/[_\s]/)[0]}
              </label>
            ))}
          </div>
        </div>
      </div>
      <button className="btn btn-primary btn-full" onClick={runOptimizer} disabled={loading} style={{ marginBottom: 20 }}>
        {loading ? '⏳ Optimizing... (10-20 seconds)' : '⚡ Find Safe Operating Point'}
      </button>
      {loading && (
        <div className="card fade-in" style={{ background: '#e0f2fe', color: '#0369a1', fontWeight: 600, marginBottom: 20, textAlign: 'center' }}>
          🔄 Running optimization algorithm... This typically takes 10-20 seconds.
          <div style={{ fontSize: 12, marginTop: 8, color: '#0284c7' }}>
            Computing sensitivity analysis and finding optimal parameters...
          </div>
        </div>
      )}
      {result && result.error && (
        <div className="card fade-in" style={{ background: '#fef1f0', color: '#ee5d50', fontWeight: 600 }}>
          ❌ Error: {result.error}
        </div>
      )}
      {result && !result.error && (
        <div className="fade-in">
          <div className="card">
            <div className="card-header">{result.achieved ? '✅ Target Achieved' : '⚠️ Best Reachable Point'}</div>
            <div className="stat-cards" style={{ gridTemplateColumns: 'repeat(4,1fr)' }}>
              <StatCard label="Before" value={`${(100 - result.before_probability)?.toFixed(1)}%`} icon="red" />
              <StatCard label="After" value={`${(100 - result.optimized_probability)?.toFixed(1)}%`} icon="green" color="#05cd99" />
              <StatCard label="Improvement" value={`+${result.reduction?.toFixed(1)}pp`} icon="blue" color="#422afb" />
              <StatCard label="Target" value={`${target}%`} icon="amber" />
            </div>
          </div>

          {/* Sensitivity Analysis */}
          {result.sensitivity && result.sensitivity.length > 0 && (
            <div className="card" style={{ marginTop: 20 }}>
              <div className="card-header"><div className="card-header-icon">📊</div> Parameter Sensitivity Analysis</div>
              <div style={{ fontSize: 13, color: '#a3aed0', marginBottom: 16 }}>
                How much does health score change when each parameter is nudged ±5% of its range? 
                High-leverage parameters are the most effective levers.
              </div>
              {result.sensitivity.slice(0, 5).map((s, idx) => {
                const barWidth = Math.min(100, (s.leverage / Math.max(...result.sensitivity.map(x => x.leverage))) * 100);
                const color = s.locked ? '#a3aed0' : (s.leverage > 5 ? '#ee5d50' : s.leverage > 2 ? '#ffb547' : '#05cd99');
                return (
                  <div key={s.feature} style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: '#2b3674' }}>
                        {idx === 0 ? '🔥 ' : ''}{s.label} {s.locked ? '🔒' : ''}
                      </span>
                      <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color }}>
                        {s.leverage.toFixed(2)}pp leverage
                      </span>
                    </div>
                    <div style={{ background: '#f4f7fe', borderRadius: 4, height: 8, overflow: 'hidden' }}>
                      <div style={{ width: `${barWidth}%`, height: '100%', background: color, borderRadius: 4 }} />
                    </div>
                  </div>
                );
              })}
              {result.sensitivity[0] && !result.sensitivity[0].locked && (
                <div style={{ marginTop: 16, padding: 12, background: '#fff8eb', borderLeft: '3px solid #ffb547', borderRadius: '0 8px 8px 0', fontSize: 13, color: '#8b5a00' }}>
                  ⚡ <strong>{result.sensitivity[0].label}</strong> is the most influential parameter — 
                  a ±5% change shifts health score by up to <strong>{result.sensitivity[0].leverage.toFixed(2)} percentage points</strong>.
                </div>
              )}
            </div>
          )}

          {/* Recommended Changes */}
          {result.changes && result.changes.length > 0 && (
            <div className="card" style={{ marginTop: 20 }}>
              <div className="card-header"><div className="card-header-icon">🔧</div> Recommended Parameter Changes</div>
              <div style={{ fontSize: 13, color: '#a3aed0', marginBottom: 16 }}>
                Minimum adjustments to reach the safe operating zone. Parameters sorted by magnitude of change.
              </div>
              {result.changes
                .sort((a, b) => a.locked ? 1 : b.locked ? -1 : Math.abs(b.delta) - Math.abs(a.delta))
                .map(ch => {
                  if (ch.locked) {
                    return (
                      <div key={ch.feature} style={{ padding: '10px 16px', borderLeft: '3px solid #a3aed0', margin: '4px 0', fontSize: 14, color: '#a3aed0', borderRadius: '0 8px 8px 0', background: '#f4f7fe' }}>
                        🔒 <strong>{ch.label}</strong> — fixed at <strong>{ch.before.toFixed(2)} {ch.unit}</strong> (locked)
                      </div>
                    );
                  }
                  if (Math.abs(ch.delta) < 0.01) {
                    return (
                      <div key={ch.feature} style={{ padding: '10px 16px', borderLeft: '3px solid #e9ecf1', margin: '4px 0', fontSize: 14, color: '#a3aed0', borderRadius: '0 8px 8px 0', background: '#f4f7fe' }}>
                        ➖ <strong>{ch.label}</strong> — no change needed · stays at <strong>{ch.before.toFixed(2)} {ch.unit}</strong>
                      </div>
                    );
                  }
                  const color = ch.delta < 0 ? '#05cd99' : '#ee5d50';
                  const bg = ch.delta < 0 ? '#e6faf5' : '#fef1f0';
                  const arrow = ch.delta < 0 ? '⬇' : '⬆';
                  const action = ch.delta < 0 ? 'reduce' : 'increase';
                  return (
                    <div key={ch.feature} style={{ padding: '10px 16px', borderLeft: `3px solid ${color}`, margin: '4px 0', fontSize: 14, color, borderRadius: '0 8px 8px 0', background: bg }}>
                      {arrow} <strong style={{ color: '#1b2559' }}>{ch.label}</strong> — {action} from{' '}
                      <strong>{ch.before.toFixed(2)} → {ch.after.toFixed(2)} {ch.unit}</strong>
                      {' '}· change by <strong>{Math.abs(ch.delta).toFixed(2)} {ch.unit}</strong>
                      {' '}<span style={{ color: '#a3aed0' }}>({ch.pct_range.toFixed(1)}% of range)</span>
                    </div>
                  );
                })}
            </div>
          )}

          {/* Before/After Comparison */}
          {result.changes && result.changes.length > 0 && (
            <div className="card" style={{ marginTop: 20 }}>
              <div className="card-header"><div className="card-header-icon">📊</div> Before vs After — Parameter Comparison</div>
              <div style={{ fontSize: 13, color: '#a3aed0', marginBottom: 16 }}>
                Bar fill shows where each parameter sits within its operating range. Values beyond 75% enter the danger zone.
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#2b3674', marginBottom: 12 }}>
                    Before — {(100 - result.before_probability).toFixed(1)}% health
                  </div>
                  {result.changes.map(ch => {
                    const norm = ch.normalized_before;
                    const barColor = norm < 0.4 ? '#05cd99' : norm < 0.65 ? '#ffb547' : '#ee5d50';
                    return (
                      <div key={ch.feature} style={{ marginBottom: 12 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                          <span style={{ fontSize: 13, color: '#a3aed0', fontWeight: 500 }}>{ch.label}</span>
                          <span style={{ fontSize: 13, fontWeight: 600, color: '#2b3674', fontFamily: 'var(--font-mono)' }}>
                            {ch.before.toFixed(1)} {ch.unit}
                          </span>
                        </div>
                        <div style={{ background: '#f4f7fe', borderRadius: 4, height: 7, overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(norm * 100, 100)}%`, height: '100%', background: barColor, borderRadius: 4 }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#05cd99', marginBottom: 12 }}>
                    After — {(100 - result.optimized_probability).toFixed(1)}% health
                  </div>
                  {result.changes.map(ch => {
                    const norm = ch.normalized_after;
                    const barColor = norm < 0.4 ? '#05cd99' : norm < 0.65 ? '#ffb547' : '#ee5d50';
                    return (
                      <div key={ch.feature} style={{ marginBottom: 12 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                          <span style={{ fontSize: 13, color: '#a3aed0', fontWeight: 500 }}>{ch.label}</span>
                          <span style={{ fontSize: 13, fontWeight: 600, color: '#2b3674', fontFamily: 'var(--font-mono)' }}>
                            {ch.after.toFixed(1)} {ch.unit}
                          </span>
                        </div>
                        <div style={{ background: '#f4f7fe', borderRadius: 4, height: 7, overflow: 'hidden' }}>
                          <div style={{ width: `${Math.min(norm * 100, 100)}%`, height: '100%', background: barColor, borderRadius: 4 }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
