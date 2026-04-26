import React from 'react';
import { ClipboardCheck } from 'lucide-react';
import { ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, RadialBarChart, RadialBar } from 'recharts';

const QC_DATA = [
  { parameter: 'Pitch Diameter', target: 72.000, actual: 72.012, tolerance: '±0.025', unit: 'mm' },
  { parameter: 'Module', target: 4.000, actual: 3.998, tolerance: '±0.010', unit: 'mm' },
  { parameter: 'Pressure Angle', target: 20.000, actual: 20.015, tolerance: '±0.050', unit: '°' },
  { parameter: 'Face Width', target: 35.000, actual: 35.045, tolerance: '±0.100', unit: 'mm' },
  { parameter: 'Tooth Thickness', target: 6.283, actual: 6.271, tolerance: '±0.025', unit: 'mm' },
  { parameter: 'Total Runout', target: 0.000, actual: 0.018, tolerance: '≤ 0.030', unit: 'mm' },
  { parameter: 'Backlash', target: 0.150, actual: 0.162, tolerance: '0.10–0.20', unit: 'mm' },
  { parameter: 'Surface Roughness (Ra)', target: 0.800, actual: 0.720, tolerance: '≤ 1.600', unit: 'μm' },
  { parameter: 'Cone Distance', target: 50.912, actual: 50.905, tolerance: '±0.050', unit: 'mm' },
  { parameter: 'Addendum', target: 4.000, actual: 4.008, tolerance: '±0.020', unit: 'mm' },
  { parameter: 'Dedendum', target: 5.000, actual: 4.992, tolerance: '±0.025', unit: 'mm' },
  { parameter: 'Root Fillet Radius', target: 1.200, actual: 1.180, tolerance: '±0.050', unit: 'mm' },
];

function getStatus(param) {
  const dev = Math.abs(param.actual - param.target);
  const tol = param.tolerance;
  if (tol.startsWith('±')) {
    const tolVal = parseFloat(tol.replace('±', ''));
    if (dev <= tolVal * 0.5) return { status: '✅ Pass', color: '#05cd99', score: 100 };
    if (dev <= tolVal) return { status: '✅ Pass', color: '#0d9488', score: 85 };
    return { status: '❌ Fail', color: '#ee5d50', score: 30 };
  }
  if (tol.startsWith('≤')) {
    const max = parseFloat(tol.replace('≤ ', ''));
    if (param.actual <= max * 0.6) return { status: '✅ Pass', color: '#05cd99', score: 100 };
    if (param.actual <= max) return { status: '✅ Pass', color: '#0d9488', score: 85 };
    return { status: '❌ Fail', color: '#ee5d50', score: 30 };
  }
  // Range like 0.10–0.20
  const [lo, hi] = tol.split('–').map(Number);
  if (param.actual >= lo && param.actual <= hi) return { status: '✅ Pass', color: '#05cd99', score: 95 };
  return { status: '❌ Fail', color: '#ee5d50', score: 30 };
}

export default function ManufacturingQC() {
  const enriched = QC_DATA.map(p => ({ ...p, ...getStatus(p) }));
  const passCount = enriched.filter(p => p.status.includes('Pass')).length;
  const overallScore = Math.round(enriched.reduce((s, p) => s + p.score, 0) / enriched.length);
  const gaugeData = [{ value: overallScore, fill: overallScore >= 80 ? '#05cd99' : overallScore >= 60 ? '#ffb547' : '#ee5d50' }];

  const radarData = enriched.slice(0, 8).map(p => ({
    parameter: p.parameter.split(' ')[0],
    accuracy: p.score,
  }));

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-banner qc-banner">
        <div className="page-banner-icon"><ClipboardCheck size={28} /></div>
        <div>
          <h2>Manufacturing QC</h2>
          <p>Tolerance Check · Dimensional Accuracy · AGMA Quality Grade Compliance</p>
        </div>
      </div>

      {/* KPI Row */}
      <div className="stat-cards" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 24 }}>
        <div className="stat-card"><div className="icon-box green">✅</div><div className="info"><div className="label">Parameters Passed</div><div className="value" style={{ color: '#05cd99' }}>{passCount}/{enriched.length}</div></div></div>
        <div className="stat-card"><div className="icon-box red">❌</div><div className="info"><div className="label">Parameters Failed</div><div className="value" style={{ color: '#ee5d50' }}>{enriched.length - passCount}</div></div></div>
        <div className="stat-card"><div className="icon-box blue">📊</div><div className="info"><div className="label">QC Score</div><div className="value">{overallScore}%</div></div></div>
        <div className="stat-card"><div className="icon-box amber">📐</div><div className="info"><div className="label">AGMA Grade</div><div className="value">Q10</div></div></div>
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* QC Gauge */}
        <div className="card" style={{ textAlign: 'center' }}>
          <div className="card-header"><div className="card-header-icon">🎯</div> Overall QC Score</div>
          <ResponsiveContainer width="100%" height={220}>
            <RadialBarChart cx="50%" cy="50%" innerRadius="65%" outerRadius="90%" startAngle={180} endAngle={0} data={gaugeData} barSize={14}>
              <RadialBar background={{ fill: '#f4f7fe' }} dataKey="value" cornerRadius={10} fill={gaugeData[0].fill} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div style={{ marginTop: -50, fontSize: 44, fontWeight: 900, color: '#1b2559' }}>
            {overallScore}<span style={{ fontSize: 16, color: '#a3aed0' }}>%</span>
          </div>
          <div style={{ fontSize: 14, fontWeight: 700, color: overallScore >= 80 ? '#05cd99' : '#ffb547', marginTop: 10 }}>
            {overallScore >= 90 ? 'Excellent' : overallScore >= 80 ? 'Good' : overallScore >= 60 ? 'Acceptable' : 'Needs Review'}
          </div>
        </div>

        {/* Radar Chart */}
        <div className="card">
          <div className="card-header"><div className="card-header-icon">📡</div> Dimensional Accuracy Radar</div>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e9ecf1" />
              <PolarAngleAxis dataKey="parameter" tick={{ fill: '#a3aed0', fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#a3aed0', fontSize: 9 }} />
              <Radar name="Accuracy" dataKey="accuracy" stroke="#1e40af" fill="#1e40af" fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tolerance Check Table */}
      <div className="card">
        <div className="card-header"><div className="card-header-icon">📋</div> Tolerance Check — Target vs Actual</div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Target</th>
                <th>Actual</th>
                <th>Deviation</th>
                <th>Tolerance</th>
                <th>Unit</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {enriched.map(p => {
                const dev = p.actual - p.target;
                return (
                  <tr key={p.parameter}>
                    <td style={{ fontWeight: 600, color: '#1b2559' }}>{p.parameter}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{p.target.toFixed(3)}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 700, color: p.color }}>{p.actual.toFixed(3)}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: Math.abs(dev) > 0.02 ? '#ee5d50' : '#a3aed0' }}>
                      {dev > 0 ? '+' : ''}{dev.toFixed(3)}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{p.tolerance}</td>
                    <td>{p.unit}</td>
                    <td style={{ fontWeight: 700, color: p.color }}>{p.status}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
