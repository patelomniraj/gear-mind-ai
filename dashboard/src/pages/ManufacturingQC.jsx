import React, { useState } from 'react';
import { ClipboardCheck } from 'lucide-react';
import { ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, RadialBarChart, RadialBar } from 'recharts';

const GEAR_ICONS = { Helical: '⚙️', Spur: '🔧', Bevel: '🔩', Worm: '🌀' };

// ═══════════════════════════════════════════════════════════
// QC DATA PER GEAR TYPE — Realistic inspection parameters
// ═══════════════════════════════════════════════════════════

const QC_DATA_BY_GEAR = {
  Helical: {
    agmaGrade: 'Q10',
    standard: 'AGMA 2001-D04',
    data: [
      { parameter: 'Pitch Diameter',         target: 128.000, actual: 128.018, tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Normal Module',          target: 4.000,   actual: 3.997,  tolerance: '±0.010', unit: 'mm' },
      { parameter: 'Helix Angle',            target: 20.000,  actual: 20.035, tolerance: '±0.050', unit: '°' },
      { parameter: 'Pressure Angle',         target: 14.500,  actual: 14.510, tolerance: '±0.050', unit: '°' },
      { parameter: 'Face Width',             target: 50.000,  actual: 50.062, tolerance: '±0.100', unit: 'mm' },
      { parameter: 'Tooth Thickness',        target: 6.283,   actual: 6.271,  tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Total Runout (Fr)',      target: 0.000,   actual: 0.015,  tolerance: '≤ 0.030', unit: 'mm' },
      { parameter: 'Profile Error (fα)',     target: 0.000,   actual: 0.008,  tolerance: '≤ 0.014', unit: 'mm' },
      { parameter: 'Lead Error (fβ)',        target: 0.000,   actual: 0.007,  tolerance: '≤ 0.012', unit: 'mm' },
      { parameter: 'Backlash',               target: 0.150,   actual: 0.162,  tolerance: '0.10–0.20', unit: 'mm' },
      { parameter: 'Surface Roughness (Ra)', target: 0.800,   actual: 0.720,  tolerance: '≤ 1.600', unit: 'μm' },
      { parameter: 'Addendum',               target: 4.000,   actual: 4.008,  tolerance: '±0.020', unit: 'mm' },
      { parameter: 'Dedendum',               target: 5.000,   actual: 4.992,  tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Root Fillet Radius',     target: 1.200,   actual: 1.185,  tolerance: '±0.050', unit: 'mm' },
      { parameter: 'Axial Pitch',            target: 34.413,  actual: 34.420, tolerance: '±0.030', unit: 'mm' },
    ],
  },

  Spur: {
    agmaGrade: 'Q8',
    standard: 'AGMA 2015-1-A01',
    data: [
      { parameter: 'Pitch Diameter',         target: 140.000, actual: 140.025, tolerance: '±0.030', unit: 'mm' },
      { parameter: 'Module',                 target: 5.000,   actual: 4.998,   tolerance: '±0.010', unit: 'mm' },
      { parameter: 'Pressure Angle',         target: 20.000,  actual: 20.022,  tolerance: '±0.050', unit: '°' },
      { parameter: 'Face Width',             target: 50.000,  actual: 50.078,  tolerance: '±0.100', unit: 'mm' },
      { parameter: 'Number of Teeth',        target: 28.000,  actual: 28.000,  tolerance: '±0.000', unit: '' },
      { parameter: 'Tooth Thickness',        target: 7.854,   actual: 7.841,   tolerance: '±0.030', unit: 'mm' },
      { parameter: 'Total Runout (Fr)',      target: 0.000,   actual: 0.022,   tolerance: '≤ 0.035', unit: 'mm' },
      { parameter: 'Profile Error (fα)',     target: 0.000,   actual: 0.011,   tolerance: '≤ 0.018', unit: 'mm' },
      { parameter: 'Pitch Error (fp)',       target: 0.000,   actual: 0.009,   tolerance: '≤ 0.016', unit: 'mm' },
      { parameter: 'Backlash',               target: 0.180,   actual: 0.195,   tolerance: '0.12–0.25', unit: 'mm' },
      { parameter: 'Surface Roughness (Ra)', target: 1.200,   actual: 1.050,   tolerance: '≤ 1.600', unit: 'μm' },
      { parameter: 'Addendum',               target: 5.000,   actual: 5.012,   tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Dedendum',               target: 6.250,   actual: 6.238,   tolerance: '±0.030', unit: 'mm' },
      { parameter: 'Root Fillet Radius',     target: 1.500,   actual: 1.488,   tolerance: '±0.050', unit: 'mm' },
      { parameter: 'Tip Diameter',           target: 150.000, actual: 150.024, tolerance: '±0.040', unit: 'mm' },
    ],
  },

  Bevel: {
    agmaGrade: 'Q9',
    standard: 'AGMA 2003-B97',
    data: [
      { parameter: 'Pitch Diameter',         target: 72.000,  actual: 72.012,  tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Module',                 target: 4.000,   actual: 3.998,   tolerance: '±0.010', unit: 'mm' },
      { parameter: 'Pressure Angle',         target: 20.000,  actual: 20.015,  tolerance: '±0.050', unit: '°' },
      { parameter: 'Shaft Angle',            target: 90.000,  actual: 89.985,  tolerance: '±0.030', unit: '°' },
      { parameter: 'Face Width',             target: 35.000,  actual: 35.045,  tolerance: '±0.100', unit: 'mm' },
      { parameter: 'Cone Distance',          target: 50.912,  actual: 50.905,  tolerance: '±0.050', unit: 'mm' },
      { parameter: 'Pitch Cone Angle',       target: 45.000,  actual: 45.018,  tolerance: '±0.030', unit: '°' },
      { parameter: 'Total Runout (Fr)',      target: 0.000,   actual: 0.018,   tolerance: '≤ 0.030', unit: 'mm' },
      { parameter: 'Profile Error (fα)',     target: 0.000,   actual: 0.009,   tolerance: '≤ 0.016', unit: 'mm' },
      { parameter: 'Backlash',               target: 0.150,   actual: 0.162,   tolerance: '0.10–0.20', unit: 'mm' },
      { parameter: 'Surface Roughness (Ra)', target: 0.800,   actual: 0.720,   tolerance: '≤ 1.600', unit: 'μm' },
      { parameter: 'Addendum',               target: 4.000,   actual: 4.008,   tolerance: '±0.020', unit: 'mm' },
      { parameter: 'Dedendum',               target: 5.000,   actual: 4.992,   tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Root Fillet Radius',     target: 1.200,   actual: 1.180,   tolerance: '±0.050', unit: 'mm' },
      { parameter: 'Mounting Distance',      target: 82.500,  actual: 82.530,  tolerance: '±0.050', unit: 'mm' },
    ],
  },

  Worm: {
    agmaGrade: 'Q7',
    standard: 'AGMA 6022-C93',
    data: [
      { parameter: 'Worm Pitch Diameter',    target: 40.000,  actual: 40.015,  tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Wheel Pitch Diameter',   target: 120.000, actual: 119.978, tolerance: '±0.030', unit: 'mm' },
      { parameter: 'Lead Angle',             target: 5.200,   actual: 5.215,   tolerance: '±0.030', unit: '°' },
      { parameter: 'Axial Pitch (Worm)',     target: 11.424,  actual: 11.430,  tolerance: '±0.020', unit: 'mm' },
      { parameter: 'Number of Threads',      target: 2.000,   actual: 2.000,   tolerance: '±0.000', unit: '' },
      { parameter: 'Wheel Teeth',            target: 60.000,  actual: 60.000,  tolerance: '±0.000', unit: '' },
      { parameter: 'Center Distance',        target: 80.000,  actual: 80.025,  tolerance: '±0.040', unit: 'mm' },
      { parameter: 'Worm Thread Thickness',  target: 5.712,   actual: 5.698,   tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Wheel Tooth Thickness',  target: 5.712,   actual: 5.725,   tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Total Runout (Fr)',      target: 0.000,   actual: 0.020,   tolerance: '≤ 0.035', unit: 'mm' },
      { parameter: 'Lead Error (fβ)',        target: 0.000,   actual: 0.010,   tolerance: '≤ 0.015', unit: 'mm' },
      { parameter: 'Backlash',               target: 0.200,   actual: 0.218,   tolerance: '0.12–0.28', unit: 'mm' },
      { parameter: 'Surface Roughness (Ra)', target: 0.400,   actual: 0.380,   tolerance: '≤ 0.800', unit: 'μm' },
      { parameter: 'Worm Root Diameter',     target: 30.000,  actual: 29.985,  tolerance: '±0.025', unit: 'mm' },
      { parameter: 'Gear Ratio',             target: 30.000,  actual: 30.000,  tolerance: '±0.000', unit: ':1' },
    ],
  },
};

// ═══════════════════════════════════════════════════════════

function getStatus(param) {
  const dev = Math.abs(param.actual - param.target);
  const tol = param.tolerance;
  if (tol.startsWith('±')) {
    const tolVal = parseFloat(tol.replace('±', ''));
    if (tolVal === 0) return { status: '✅ Pass', color: '#05cd99', score: 100 };
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

const GEAR_COLORS = {
  Helical: '#2563eb',
  Spur: '#10b981',
  Bevel: '#a78bfa',
  Worm: '#f59e0b',
};

export default function ManufacturingQC() {
  const [gearType, setGearType] = useState('Helical');

  const currentQC = QC_DATA_BY_GEAR[gearType];
  const enriched = currentQC.data.map(p => ({ ...p, ...getStatus(p) }));
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
          <p>Tolerance Check · Dimensional Accuracy · {currentQC.standard} Compliance</p>
        </div>
      </div>

      {/* ── Gear Type Selector ──────────────────────────────── */}
      <div className="dashboard-controls" style={{ marginBottom: 20 }}>
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
      </div>

      {/* KPI Row */}
      <div className="stat-cards" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 24 }}>
        <div className="stat-card"><div className="icon-box green">✅</div><div className="info"><div className="label">Parameters Passed</div><div className="value" style={{ color: '#05cd99' }}>{passCount}/{enriched.length}</div></div></div>
        <div className="stat-card"><div className="icon-box red">❌</div><div className="info"><div className="label">Parameters Failed</div><div className="value" style={{ color: '#ee5d50' }}>{enriched.length - passCount}</div></div></div>
        <div className="stat-card"><div className="icon-box blue">📊</div><div className="info"><div className="label">QC Score</div><div className="value">{overallScore}%</div></div></div>
        <div className="stat-card"><div className="icon-box amber">📐</div><div className="info"><div className="label">AGMA Grade</div><div className="value">{currentQC.agmaGrade}</div></div></div>
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* QC Gauge */}
        <div className="card" style={{ textAlign: 'center' }}>
          <div className="card-header"><div className="card-header-icon">🎯</div> Overall QC Score — {gearType} Gear</div>
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
          <div className="card-header"><div className="card-header-icon">📡</div> Dimensional Accuracy Radar — {gearType}</div>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e9ecf1" />
              <PolarAngleAxis dataKey="parameter" tick={{ fill: '#a3aed0', fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#a3aed0', fontSize: 9 }} />
              <Radar name="Accuracy" dataKey="accuracy" stroke={GEAR_COLORS[gearType]} fill={GEAR_COLORS[gearType]} fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tolerance Check Table */}
      <div className="card">
        <div className="card-header"><div className="card-header-icon">📋</div> Tolerance Check — {gearType} Gear ({currentQC.standard})</div>
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

      {/* Gear-Specific Notes */}
      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-header">
          <div className="card-header-icon">{GEAR_ICONS[gearType]}</div>
          {gearType} Gear — Inspection Notes
        </div>
        <div style={{ padding: '8px 0', color: '#68769a', fontSize: 13, lineHeight: 1.8 }}>
          {gearType === 'Helical' && (
            <>
              <p><strong>Standard:</strong> AGMA 2001-D04 · Helix Angle: 20° · Module: 4 · Teeth: 32 · Pressure Angle: 14.5°</p>
              <p><strong>Key Checks:</strong> Helix angle accuracy is critical — deviation affects axial thrust and bearing loads. Profile and lead errors must stay within AGMA Q10 tolerances for smooth, quiet operation. Axial pitch measured at 3 locations along face width.</p>
              <p><strong>Material:</strong> 20MnCr5 case-hardened steel · Surface hardness: 58-62 HRC · Core hardness: 30-38 HRC</p>
            </>
          )}
          {gearType === 'Spur' && (
            <>
              <p><strong>Standard:</strong> AGMA 2015-1-A01 · Module: 5 · Teeth: 28 · Pressure Angle: 20° · Face Width: 50mm</p>
              <p><strong>Key Checks:</strong> Pitch error directly affects noise and vibration at speed. Profile error governs load distribution across tooth face. Tip diameter checked at 4 angular positions for concentricity.</p>
              <p><strong>Material:</strong> EN36B carburizing steel · Surface hardness: 56-60 HRC · Core hardness: 28-35 HRC</p>
            </>
          )}
          {gearType === 'Bevel' && (
            <>
              <p><strong>Standard:</strong> AGMA 2003-B97 · Shaft Angle: 90° · Module: 4 · Teeth: 18 · Pressure Angle: 20°</p>
              <p><strong>Key Checks:</strong> Mounting distance is critical — ±0.05mm tolerance ensures proper tooth contact pattern. Cone distance verified via contact pattern test (blue check). Shaft angle checked with precision sine bar.</p>
              <p><strong>Material:</strong> SAE 8620 case-hardened steel · Surface hardness: 58-62 HRC · Lapping compound: 600-grit</p>
            </>
          )}
          {gearType === 'Worm' && (
            <>
              <p><strong>Standard:</strong> AGMA 6022-C93 · Ratio: 30:1 · Lead Angle: 5.2° · Worm Threads: 2 · Wheel Teeth: 60</p>
              <p><strong>Key Checks:</strong> Worm surface finish is critical for efficiency — Ra ≤ 0.8μm required. Center distance controls backlash and contact pattern. Lead error on worm directly affects gear ratio accuracy. Wheel teeth checked for proper throat form.</p>
              <p><strong>Material:</strong> Worm: EN24 hardened steel (55-60 HRC) · Wheel: Phosphor Bronze (CuSn12) · Lubrication: EP 460 synthetic oil</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
