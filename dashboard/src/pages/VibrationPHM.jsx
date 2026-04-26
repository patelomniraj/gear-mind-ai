import React, { useState } from 'react';
import { Activity } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, AreaChart, Area } from 'recharts';

// ── Gear Mesh Frequency Waveform (monotone) ───────────
const MESH_FREQ = 585; // Hz for 18-tooth at 1950 RPM
const TIME_DOMAIN = Array.from({ length: 200 }, (_, i) => {
  const t = i * 0.0002;
  const signal = 2.0 * Math.sin(2 * Math.PI * MESH_FREQ * t)
    + 0.8 * Math.sin(2 * Math.PI * MESH_FREQ * 2 * t)
    + 0.3 * Math.sin(2 * Math.PI * MESH_FREQ * 3 * t)
    + 0.4 * Math.sin(2 * Math.PI * 120 * t)
    + (Math.random() - 0.5) * 0.3;
  return { time: Math.round(t * 10000) / 10, amplitude: Math.round(signal * 1000) / 1000, label: `${(t * 1000).toFixed(1)}ms` };
});

// ── FFT Spectral Data ─────────────────────────────────
const FFT_DATA = [
  { freq: 60, magnitude: 0.15, label: '60 Hz', note: 'Motor' },
  { freq: 120, magnitude: 0.35, label: '120 Hz', note: '2× Line' },
  { freq: 292, magnitude: 0.22, label: '292 Hz', note: '1/2× GMF' },
  { freq: 585, magnitude: 2.80, label: '585 Hz', note: '1× GMF' },
  { freq: 1170, magnitude: 1.45, label: '1170 Hz', note: '2× GMF' },
  { freq: 1755, magnitude: 0.65, label: '1755 Hz', note: '3× GMF' },
  { freq: 2340, magnitude: 0.28, label: '2340 Hz', note: '4× GMF' },
  { freq: 2925, magnitude: 0.12, label: '2925 Hz', note: '5× GMF' },
];

// ── PHM Status Data ───────────────────────────────────
const PHM_STATUS = [
  { indicator: 'RMS Velocity', value: 2.3, limit: 6.0, unit: 'mm/s', status: 'Normal' },
  { indicator: 'Peak Acceleration', value: 4.8, limit: 12.0, unit: 'g', status: 'Normal' },
  { indicator: 'Crest Factor', value: 3.2, limit: 6.0, unit: '', status: 'Normal' },
  { indicator: 'Kurtosis', value: 3.8, limit: 5.0, unit: '', status: 'Watch' },
  { indicator: 'Sideband Energy', value: 0.45, limit: 1.0, unit: 'g²', status: 'Normal' },
  { indicator: 'Envelope RMS', value: 1.2, limit: 3.0, unit: 'mm/s', status: 'Normal' },
];

// ── Failure Prediction Timeline ───────────────────────
const PREDICTION_TIMELINE = Array.from({ length: 12 }, (_, i) => {
  const month = i + 1;
  const health = Math.max(20, 95 - i * 2.5 - Math.random() * 5);
  const prob = Math.min(90, 5 + i * 3.5 + Math.random() * 8);
  return { month: `M${month}`, health: Math.round(health * 10) / 10, failProb: Math.round(prob * 10) / 10 };
});

export default function VibrationPHM() {
  const [viewMode, setViewMode] = useState('time');

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-banner vibration-banner">
        <div className="page-banner-icon"><Activity size={28} /></div>
        <div>
          <h2>Vibration / PHM</h2>
          <p>Spectral Analysis · Gear Mesh Waves · Failure Prediction</p>
        </div>
      </div>

      {/* PHM Status Cards */}
      <div className="phm-status-grid" style={{ marginBottom: 20 }}>
        {PHM_STATUS.map(p => {
          const pct = (p.value / p.limit) * 100;
          const color = pct > 80 ? '#ee5d50' : pct > 60 ? '#ffb547' : '#05cd99';
          return (
            <div key={p.indicator} className="card phm-card">
              <div className="phm-card-header">
                <span className="phm-indicator">{p.indicator}</span>
                <span className={`phm-status-badge phm-${p.status.toLowerCase()}`}>{p.status}</span>
              </div>
              <div className="phm-value" style={{ color }}>{p.value} <span className="phm-unit">{p.unit}</span></div>
              <div className="sensor-bar-track">
                <div className="sensor-bar-fill" style={{ width: `${Math.min(100, pct)}%`, background: `linear-gradient(90deg, ${color}88, ${color})` }} />
              </div>
              <div className="phm-limit">Limit: {p.limit} {p.unit}</div>
            </div>
          );
        })}
      </div>

      {/* Time/Frequency Toggle */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div className="card-header" style={{ marginBottom: 0 }}><div className="card-header-icon">🌊</div> Gear Mesh Vibration Signal</div>
          <div className="toggle-group">
            <button className={`toggle-btn ${viewMode === 'time' ? 'active' : ''}`} onClick={() => setViewMode('time')}>Time Domain</button>
            <button className={`toggle-btn ${viewMode === 'freq' ? 'active' : ''}`} onClick={() => setViewMode('freq')}>Frequency (FFT)</button>
          </div>
        </div>

        {viewMode === 'time' ? (
          <>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={TIME_DOMAIN} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                <XAxis dataKey="label" tick={{ fill: '#a3aed0', fontSize: 9 }} axisLine={false} tickLine={false} interval={19} />
                <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Amplitude (mm/s)', angle: -90, position: 'insideLeft', fill: '#a3aed0', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
                <Line type="monotone" dataKey="amplitude" stroke="#1e40af" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div style={{ fontSize: 11, color: '#a3aed0', textAlign: 'center', marginTop: 8 }}>
              Gear Mesh Frequency: {MESH_FREQ} Hz (18 teeth × 1950 RPM ÷ 60)
            </div>
          </>
        ) : (
          <>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={FFT_DATA} margin={{ top: 10, right: 30, left: 10, bottom: 30 }}>
                <defs>
                  <linearGradient id="fftGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="label" tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Magnitude (g)', angle: -90, position: 'insideLeft', fill: '#a3aed0', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }}
                  formatter={(v, n, p) => [`${v} g — ${p.payload.note}`, 'Magnitude']} />
                <Area type="monotone" dataKey="magnitude" stroke="#7c3aed" strokeWidth={2.5} fill="url(#fftGrad)" dot={{ r: 5, fill: '#7c3aed', stroke: 'white', strokeWidth: 2 }} />
              </AreaChart>
            </ResponsiveContainer>
            <div style={{ fontSize: 11, color: '#a3aed0', textAlign: 'center', marginTop: 8 }}>
              1× GMF dominant at 585 Hz · 2× harmonic present · No significant sidebands
            </div>
          </>
        )}
      </div>

      {/* Failure Prediction Timeline */}
      <div className="card">
        <div className="card-header"><div className="card-header-icon">🔮</div> Failure Prediction — 12 Month Horizon</div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={PREDICTION_TIMELINE} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
            <XAxis dataKey="month" tick={{ fill: '#a3aed0', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} domain={[0, 100]} />
            <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
            <Line type="monotone" dataKey="health" stroke="#0d9488" strokeWidth={2.5} name="Health %" dot={{ r: 4, fill: '#0d9488', stroke: 'white', strokeWidth: 2 }} />
            <Line type="monotone" dataKey="failProb" stroke="#ee5d50" strokeWidth={2.5} name="Failure %" strokeDasharray="5 5" dot={{ r: 4, fill: '#ee5d50', stroke: 'white', strokeWidth: 2 }} />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 32, marginTop: 12, fontSize: 12, fontWeight: 600 }}>
          <span style={{ color: '#0d9488' }}>━━ Health Score</span>
          <span style={{ color: '#ee5d50' }}>╌╌ Failure Probability</span>
        </div>
      </div>
    </div>
  );
}
