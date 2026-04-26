import React from 'react';
import { TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, LineChart, Line, Cell } from 'recharts';

// ── Simulated Engineering Data ─────────────────────────
const SN_DATA = Array.from({ length: 20 }, (_, i) => {
  const cycles = Math.pow(10, 3 + i * 0.35);
  const stress = 800 * Math.pow(cycles, -0.12) + 50 * Math.random();
  return { cycles: Math.round(cycles), stress: Math.round(stress), label: cycles >= 1e6 ? `${(cycles/1e6).toFixed(1)}M` : cycles >= 1e3 ? `${(cycles/1e3).toFixed(0)}K` : String(Math.round(cycles)) };
});

const MTBF_DATA = [
  { type: 'Helical', mtbf: 4200, color: '#1e40af' },
  { type: 'Spur', mtbf: 3800, color: '#0d9488' },
  { type: 'Bevel', mtbf: 3500, color: '#7c3aed' },
  { type: 'Worm', mtbf: 2900, color: '#a3aed0' },
];

const WEIBULL_DATA = Array.from({ length: 30 }, (_, i) => {
  const t = (i + 1) * 200;
  const beta = 2.5, eta = 5000;
  const R = Math.exp(-Math.pow(t / eta, beta));
  return { time: t, reliability: Math.round(R * 10000) / 100, label: `${t}h` };
});

const BATHTUB_DATA = Array.from({ length: 40 }, (_, i) => {
  const t = i * 250;
  const infant = 0.008 * Math.exp(-t / 800);
  const constant = 0.001;
  const wearout = 0.0001 * Math.exp((t - 8000) / 2000);
  const rate = infant + constant + (t > 5000 ? wearout : 0);
  return { time: t, rate: Math.round(rate * 100000) / 100, label: `${t}h` };
});

const FAILURE_MODES = [
  { mode: 'Surface Pitting', percentage: 35, severity: 'High', mttr: '8h', color: '#ee5d50' },
  { mode: 'Tooth Fracture', percentage: 22, severity: 'Critical', mttr: '24h', color: '#dc2626' },
  { mode: 'Wear Fatigue', percentage: 18, severity: 'Medium', mttr: '6h', color: '#ffb547' },
  { mode: 'Thermal Degradation', percentage: 12, severity: 'Medium', mttr: '4h', color: '#f59e0b' },
  { mode: 'Axial Misalignment', percentage: 8, severity: 'Low', mttr: '2h', color: '#0d9488' },
  { mode: 'Lubrication Failure', percentage: 5, severity: 'High', mttr: '3h', color: '#7c3aed' },
];

export default function ReliabilityData() {
  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-banner reliability-banner">
        <div className="page-banner-icon"><TrendingUp size={28} /></div>
        <div>
          <h2>Reliability Data</h2>
          <p>Fatigue Analysis · MTBF Charts · Weibull Distribution · Failure Modes</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="stat-cards" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 24 }}>
        <div className="stat-card"><div className="icon-box blue">📊</div><div className="info"><div className="label">Avg MTBF</div><div className="value">3,850 hrs</div></div></div>
        <div className="stat-card"><div className="icon-box green">✅</div><div className="info"><div className="label">System Reliability</div><div className="value" style={{ color: '#05cd99' }}>94.2%</div></div></div>
        <div className="stat-card"><div className="icon-box amber">⏱</div><div className="info"><div className="label">Avg MTTR</div><div className="value">7.8 hrs</div></div></div>
        <div className="stat-card"><div className="icon-box red">⚠️</div><div className="info"><div className="label">Critical Failures</div><div className="value" style={{ color: '#ee5d50' }}>3 / year</div></div></div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* S-N Curve */}
        <div className="card">
          <div className="card-header"><div className="card-header-icon">📈</div> S-N Fatigue Curve</div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={SN_DATA} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <defs>
                <linearGradient id="snGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1e40af" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#1e40af" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="label" tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Stress (MPa)', angle: -90, position: 'insideLeft', fill: '#a3aed0', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
              <Area type="monotone" dataKey="stress" stroke="#1e40af" strokeWidth={2.5} fill="url(#snGrad)" dot={{ r: 3, fill: '#1e40af', stroke: 'white', strokeWidth: 2 }} />
            </AreaChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#a3aed0', textAlign: 'center', marginTop: 8 }}>Cycles to Failure → Endurance Limit at ~280 MPa</div>
        </div>

        {/* MTBF */}
        <div className="card">
          <div className="card-header"><div className="card-header-icon">📊</div> MTBF by Gear Type</div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={MTBF_DATA} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <XAxis dataKey="type" tick={{ fill: '#a3aed0', fontSize: 12, fontWeight: 600 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
              <Bar dataKey="mtbf" radius={[10, 10, 0, 0]} label={{ position: 'top', fill: '#2b3674', fontSize: 12, fontWeight: 700, formatter: v => `${v} hrs` }}>
                {MTBF_DATA.map((d, i) => <Cell key={i} fill={d.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#a3aed0', textAlign: 'center', marginTop: 8 }}>Mean Time Between Failures (hours of operation)</div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Weibull */}
        <div className="card">
          <div className="card-header"><div className="card-header-icon">📉</div> Weibull Reliability Function</div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={WEIBULL_DATA} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <defs>
                <linearGradient id="weibullGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0d9488" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#0d9488" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="label" tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} domain={[0, 100]} label={{ value: 'R(t) %', angle: -90, position: 'insideLeft', fill: '#a3aed0', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
              <Area type="monotone" dataKey="reliability" stroke="#0d9488" strokeWidth={2.5} fill="url(#weibullGrad)" />
            </AreaChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#a3aed0', textAlign: 'center', marginTop: 8 }}>β = 2.5, η = 5000 hrs — Wear-out Phase</div>
        </div>

        {/* Bathtub */}
        <div className="card">
          <div className="card-header"><div className="card-header-icon">🛁</div> Failure Rate — Bathtub Curve</div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={BATHTUB_DATA} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <XAxis dataKey="label" tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
              <Line type="monotone" dataKey="rate" stroke="#7c3aed" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#a3aed0', textAlign: 'center', marginTop: 8 }}>Infant · Constant · Wear-out failure regions</div>
        </div>
      </div>

      {/* Failure Modes Table */}
      <div className="card">
        <div className="card-header"><div className="card-header-icon">⚠️</div> Failure Mode Analysis</div>
        <table className="data-table">
          <thead>
            <tr><th>Failure Mode</th><th>Occurrence %</th><th>Severity</th><th>MTTR</th><th>Distribution</th></tr>
          </thead>
          <tbody>
            {FAILURE_MODES.map(fm => (
              <tr key={fm.mode}>
                <td style={{ fontWeight: 600, color: '#1b2559' }}>{fm.mode}</td>
                <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: fm.color }}>{fm.percentage}%</td>
                <td><span className={`severity-badge severity-${fm.severity.toLowerCase()}`}>{fm.severity}</span></td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{fm.mttr}</td>
                <td>
                  <div className="sensor-bar-track" style={{ width: '100%' }}>
                    <div className="sensor-bar-fill" style={{ width: `${fm.percentage * 2.5}%`, background: fm.color }} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
