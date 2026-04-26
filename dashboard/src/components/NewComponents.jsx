import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
         AreaChart, Area, LineChart, Line, PieChart, Pie } from 'recharts';
import * as api from '../api/gearApi';
import { ProfessionalPDFReport } from './ProfessionalPDFReport';

// Re-export the professional PDF report as ReportPDFButton
export { ProfessionalPDFReport as ReportPDFButton };

// ═══════════════════════════════════════════════════════════
// LIME Chart — Fetches LIME for any gear type
// ═══════════════════════════════════════════════════════════
export function LimeChart({ sensors, gearType }) {
  const [limeData, setLimeData] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [predicted, setPredicted] = useState('');

  const fetchLime = async () => {
    setLoading(true);
    try {
      let res;
      if (gearType === 'Spur') {
        res = await api.getLimeSpur({
          speed: sensors.load, torque: sensors.torque,
          vib: sensors.vib, temp: sensors.temp,
          shock: sensors.wear, noise: sensors.lube * 100
        });
      } else if (gearType === 'Bevel') {
        res = await api.getLimeBevel({
          load: sensors.load, torque: sensors.torque,
          vib: sensors.vib, temp: sensors.temp,
          wear: sensors.wear, lube: sensors.lube,
          eff: sensors.eff, cycles: sensors.cycles
        });
      } else {
        res = await api.getLime({
          load: sensors.load, torque: sensors.torque,
          vib: sensors.vib, temp: sensors.temp,
          wear: sensors.wear, lube: sensors.lube,
          eff: sensors.eff, cycles: sensors.cycles
        });
      }
      setLimeData(res.lime_results || []);
      setPredicted(res.predicted_class || '');
    } catch (e) {
      setLimeData([]);
    }
    setLoading(false);
  };

  useEffect(() => { fetchLime(); }, [sensors, gearType]);

  const chartData = (limeData || []).map(d => ({
    rule: d.rule.length > 32 ? d.rule.slice(0, 30) + '…' : d.rule,
    fullRule: d.rule,
    weight: Math.round(d.weight * 10000) / 10000,
  }));

  return (
    <div>
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#a3aed0' }}>⏳ Computing LIME...</div>
      ) : chartData.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#a3aed0' }}>No LIME data available</div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 80, top: 10, bottom: 10 }}>
              <XAxis type="number" tick={{ fill: '#a3aed0', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="rule" tick={{ fill: '#2b3674', fontSize: 11, fontWeight: 600 }} width={180} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }}
                formatter={(v, n, p) => [v, p.payload.fullRule]} />
              <Bar dataKey="weight" radius={[0, 8, 8, 0]} barSize={28}
                label={{ position: 'right', fill: '#2b3674', fontSize: 11, fontWeight: 600, formatter: v => v > 0 ? `+${v}` : v }}>
                {chartData.map((d, i) => <Cell key={i} fill={d.weight > 0 ? '#ee5d50' : '#05cd99'} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 12, color: '#a3aed0', marginTop: 12, textAlign: 'center', fontWeight: 600 }}>
            🟢 Conditions favoring healthy operation | 🔴 Conditions pushing toward fault · Predicted: <strong style={{ color: '#2b3674' }}>{predicted}</strong>
          </div>
        </>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// RUL Section — Visual RUL indicator with progress bar
// ═══════════════════════════════════════════════════════════
export function RULSection({ rul, dailyCycles, fault, healthScore }) {
  const daysLeft   = Math.floor(rul / dailyCycles);
  const shiftsLeft = Math.floor(rul / (dailyCycles / 3));
  const hoursLeft  = Math.floor((rul / dailyCycles) * 24);
  const maxRUL     = 100000;
  const pct        = Math.min(100, (rul / maxRUL) * 100);

  const barColor = pct > 60 ? '#05cd99' : pct > 30 ? '#ffb547' : '#ee5d50';
  const urgency  = fault === 'Major Fault' || fault === 'Failure'
    ? { text: 'CRITICAL — Schedule Emergency Maintenance', color: '#ee5d50', bg: '#fef1f0' }
    : fault === 'Minor Fault'
    ? { text: 'CAUTION — Plan Maintenance This Week', color: '#ffb547', bg: '#fff8eb' }
    : { text: 'NORMAL — Continue Operations', color: '#05cd99', bg: '#e6faf5' };

  return (
    <div className="rul-section card" style={{ marginTop: 20 }}>
      <div className="card-header"><div className="card-header-icon">🔮</div> Remaining Useful Life (RUL)</div>
      <div className="rul-grid">
        <div className="rul-metric">
          <div className="rul-metric-value" style={{ color: barColor }}>{rul.toLocaleString()}</div>
          <div className="rul-metric-label">Cycles Remaining</div>
        </div>
        <div className="rul-metric">
          <div className="rul-metric-value" style={{ color: '#422afb' }}>{daysLeft}</div>
          <div className="rul-metric-label">Days</div>
        </div>
        <div className="rul-metric">
          <div className="rul-metric-value" style={{ color: '#7551ff' }}>{shiftsLeft}</div>
          <div className="rul-metric-label">Shifts</div>
        </div>
        <div className="rul-metric">
          <div className="rul-metric-value" style={{ color: '#a78bfa' }}>{hoursLeft.toLocaleString()}</div>
          <div className="rul-metric-label">Hours</div>
        </div>
      </div>
      <div className="rul-bar-track">
        <div className="rul-bar-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${barColor}88, ${barColor})` }} />
      </div>
      <div className="rul-urgency" style={{ background: urgency.bg, color: urgency.color }}>
        {urgency.text}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Floating AI Copilot Widget
// ═══════════════════════════════════════════════════════════
export function FloatingCopilot({ sensorValues, gearId, gearType, fault, conf, score }) {
  const [open, setOpen]       = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput]     = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const suggestions = [
    '🔍 Why did this fault happen?',
    '⚡ What action should I take?',
    '🧪 Root cause analysis',
    '⏱ How long until failure?'
  ];

  const send = async (q) => {
    const question = q || input;
    if (!question.trim()) return;
    const newMsgs = [...messages, { role: 'user', content: question }];
    setMessages(newMsgs); setInput(''); setLoading(true);
    try {
      const res = await api.chat(question, gearId, sensorValues, history);
      setMessages([...newMsgs, { role: 'ai', content: res.response }]);
      setHistory([...history, { role: 'user', content: question }, { role: 'assistant', content: res.response }]);
    } catch (e) {
      setMessages([...newMsgs, { role: 'ai', content: `⚠️ Error: ${e.message}` }]);
    }
    setLoading(false);
  };

  return (
    <>
      {/* Floating Button */}
      {!open && (
        <button className="copilot-fab" onClick={() => setOpen(true)} title="Open AI Copilot">
          <span className="copilot-fab-icon">🤖</span>
          <span className="copilot-fab-pulse" />
          <span className="copilot-fab-glow" />
        </button>
      )}

      {/* Chat Panel */}
      {open && (
        <div className="copilot-panel">
          <div className="copilot-panel-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div className="copilot-avatar">
                <span>🤖</span>
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, color: '#1b2559' }}>GearMind AI Copilot</div>
                <div style={{ fontSize: 10, color: '#a3aed0', marginTop: 2 }}>
                  {gearId} · {gearType} · LLaMA 3.3 70B
                </div>
              </div>
            </div>
            <button className="copilot-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="copilot-messages">
            {messages.length === 0 ? (
              <div className="copilot-empty">
                <div className="copilot-empty-icon">🤖</div>
                <div style={{ fontWeight: 700, color: '#1b2559', fontSize: 15, marginBottom: 6 }}>
                  GearMind AI Ready
                </div>
                <div style={{ fontSize: 12, color: '#a3aed0', marginBottom: 20 }}>
                  {fault} · {(conf * 100).toFixed(0)}% confidence · Health: {score}/100
                </div>
                <div className="copilot-suggestions">
                  {suggestions.map(q => (
                    <button key={q} className="copilot-suggestion-btn" onClick={() => send(q)}>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            ) : messages.map((m, i) => (
              <div key={i} className={`copilot-msg ${m.role}`}>
                <div className="copilot-msg-avatar">
                  {m.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="copilot-msg-bubble">
                  <div className="copilot-msg-meta">{m.role === 'user' ? 'YOU' : 'AI ASSISTANT'}</div>
                  <div className="copilot-msg-text">{m.content}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="copilot-msg ai">
                <div className="copilot-msg-avatar">🤖</div>
                <div className="copilot-msg-bubble">
                  <div className="copilot-typing">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="copilot-input-area">
            <textarea 
              value={input} 
              onChange={e => setInput(e.target.value)}
              placeholder={`Ask about ${gearId}...`} 
              rows={2}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }} 
            />
            <div style={{ display: 'flex', gap: 8 }}>
              <button 
                className="btn btn-primary" 
                style={{ flex: 1, fontSize: 12, padding: '10px 0', borderRadius: 10 }} 
                onClick={() => send()}
                disabled={!input.trim()}
              >
                Send ↑
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ fontSize: 12, padding: '10px 14px', borderRadius: 10 }} 
                onClick={() => { setMessages([]); setHistory([]); }}
                title="Clear chat"
              >
                🗑
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ═══════════════════════════════════════════════════════════
// Enhanced History Dashboard
// ═══════════════════════════════════════════════════════════
export function HistoryDashboard({ gearType }) {
  const [histData, setHistData] = useState([]);
  const [loaded, setLoaded]     = useState(false);
  const [search, setSearch]     = useState('');
  const [sensorType, setSensorType] = useState('health');

  useEffect(() => {
    api.getHistory().then(r => { setHistData(r.history || []); setLoaded(true); }).catch(() => setLoaded(true));
  }, []);

  if (!loaded) return <div style={{ color: '#a3aed0' }}>Loading...</div>;
  if (histData.length === 0) return <div className="card" style={{ background: '#fff8eb', color: '#ffb547', fontWeight: 600 }}>⚠ No data yet. Adjust any slider — readings are saved automatically.</div>;

  const filtered = histData.filter(r =>
    (!search || JSON.stringify(r).toLowerCase().includes(search.toLowerCase())) &&
    r.gear_type === gearType
  );

  const faultCounts = filtered.reduce((a, r) => { a[r.fault_label] = (a[r.fault_label] || 0) + 1; return a; }, {});
  const pieData     = Object.entries(faultCounts).map(([k, v]) => ({ name: k, value: v }));
  const pieColors   = { 'No Fault': '#05cd99', 'Minor Fault': '#ffb547', 'Major Fault': '#ee5d50', 'No Failure': '#05cd99', 'Failure': '#ee5d50' };
  
  // Map database columns to display values based on gear type
  const plotData = [...filtered].reverse().slice(-50).map((r, i) => {
    if (gearType === 'Spur') {
      return {
        no: i + 1, health: r.health_score, rul: r.rul_cycles,
        speed: r.load_kn, torque: r.torque_nm, vib: r.vibration,
        temp: r.temperature, shock: r.wear, noise: r.lubrication,
      };
    } else if (gearType === 'Worm') {
      return {
        no: i + 1, health: r.health_score, rul: r.rul_cycles,
        rpm: r.load_kn, in_torque: r.torque_nm, oil_temp: r.temperature,
        ax_vib: r.vibration, rad_vib: r.wear, eff: r.efficiency,
      };
    } else {
      return {
        no: i + 1, health: r.health_score, rul: r.rul_cycles,
        vib: r.vibration, temp: r.temperature, wear: r.wear,
        lube: r.lubrication, eff: r.efficiency,
      };
    }
  });

  // Define sensor chart configurations based on gear type
  const sensorChartConfig = gearType === 'Spur' ? {
    health: { dataKey: 'health', name: 'Health Score', color: '#422afb', yDomain: [0, 105] },
    speed: { dataKey: 'speed', name: 'Speed (RPM)', color: '#3b82f6', yDomain: [0, 'auto'] },
    torque: { dataKey: 'torque', name: 'Torque (Nm)', color: '#8b5cf6', yDomain: [0, 'auto'] },
    vib: { dataKey: 'vib', name: 'Vibration (mm/s)', color: '#ee5d50', yDomain: [0, 'auto'] },
    temp: { dataKey: 'temp', name: 'Temperature (°C)', color: '#ffb547', yDomain: [0, 'auto'] },
    shock: { dataKey: 'shock', name: 'Shock Load (g)', color: '#ef4444', yDomain: [0, 'auto'] },
    noise: { dataKey: 'noise', name: 'Noise (dB)', color: '#a78bfa', yDomain: [0, 'auto'] },
  } : gearType === 'Worm' ? {
    health: { dataKey: 'health', name: 'Health Score', color: '#422afb', yDomain: [0, 105] },
    rpm: { dataKey: 'rpm', name: 'Worm RPM', color: '#3b82f6', yDomain: [0, 'auto'] },
    in_torque: { dataKey: 'in_torque', name: 'Input Torque (Nm)', color: '#8b5cf6', yDomain: [0, 'auto'] },
    oil_temp: { dataKey: 'oil_temp', name: 'Oil Temp (°C)', color: '#ffb547', yDomain: [0, 'auto'] },
    ax_vib: { dataKey: 'ax_vib', name: 'Axial Vib', color: '#ee5d50', yDomain: [0, 'auto'] },
    rad_vib: { dataKey: 'rad_vib', name: 'Radial Vib', color: '#ef4444', yDomain: [0, 'auto'] },
    eff: { dataKey: 'eff', name: 'Efficiency (%)', color: '#10b981', yDomain: [70, 100] },
  } : {
    health: { dataKey: 'health', name: 'Health Score', color: '#422afb', yDomain: [0, 105] },
    vib: { dataKey: 'vib', name: 'Vibration (mm/s)', color: '#ee5d50', yDomain: [0, 'auto'] },
    temp: { dataKey: 'temp', name: 'Temperature (°C)', color: '#ffb547', yDomain: [0, 'auto'] },
    wear: { dataKey: 'wear', name: 'Wear (mm)', color: '#a78bfa', yDomain: [0, 'auto'] },
    lube: { dataKey: 'lube', name: 'Lubrication Index', color: '#05cd99', yDomain: [0, 1] },
    eff: { dataKey: 'eff', name: 'Efficiency (%)', color: '#10b981', yDomain: [70, 100] },
  };

  const readingsVsFaultData = Object.entries(faultCounts).map(([fault, count]) => ({
    fault: fault.replace('No Fault', 'No Fault').replace('Minor Fault', 'Minor').replace('Major Fault', 'Major'),
    count: count,
    color: pieColors[fault] || '#3965ff'
  }));

  const currentChart = sensorChartConfig[sensorType];

  return (
    <div className="fade-in">
      <div className="section-title">📈 Historical Data & Trends — {gearType} Gear</div>

      <div className="stat-cards" style={{ gridTemplateColumns: 'repeat(4,1fr)', marginBottom: 24 }}>
        <StatCard label="Total Readings" value={filtered.length} icon="blue" />
        <StatCard label="Major Faults"   value={faultCounts['Major Fault'] || faultCounts['Failure'] || 0} icon="red" color="#ee5d50" />
        <StatCard label="Avg Health"     value={`${Math.round(filtered.reduce((a, r) => a + (r.health_score || 0), 0) / Math.max(filtered.length, 1))}/100`} icon="green" />
        <StatCard label="Avg RUL"        value={Math.round(filtered.reduce((a, r) => a + (r.rul_cycles || 0), 0) / Math.max(filtered.length, 1)).toLocaleString()} icon="purple" />
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div><div className="card-header-icon">📈</div> Sensor Trends Over Time</div>
          <select 
            value={sensorType} 
            onChange={e => setSensorType(e.target.value)}
            className="sensor-dropdown"
          >
            <option value="health">Health Score</option>
            {gearType === 'Spur' ? (
              <>
                <option value="speed">Speed (RPM)</option>
                <option value="torque">Torque (Nm)</option>
                <option value="vib">Vibration</option>
                <option value="temp">Temperature</option>
                <option value="shock">Shock Load</option>
                <option value="noise">Noise</option>
              </>
            ) : gearType === 'Worm' ? (
              <>
                <option value="rpm">Worm RPM</option>
                <option value="in_torque">Input Torque</option>
                <option value="oil_temp">Oil Temperature</option>
                <option value="ax_vib">Axial Vibration</option>
                <option value="rad_vib">Radial Vibration</option>
                <option value="eff">Efficiency</option>
              </>
            ) : (
              <>
                <option value="vib">Vibration</option>
                <option value="temp">Temperature</option>
                <option value="wear">Wear</option>
                <option value="lube">Lubrication</option>
                <option value="eff">Efficiency</option>
              </>
            )}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={plotData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
            <defs>
              <linearGradient id={`${sensorType}Grad`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={currentChart.color} stopOpacity={0.15} />
                <stop offset="95%" stopColor={currentChart.color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="no" tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Reading Number', position: 'insideBottom', offset: -5, fill: '#a3aed0', fontSize: 11 }} />
            <YAxis domain={currentChart.yDomain} tick={{ fill: '#a3aed0', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: currentChart.name, angle: -90, position: 'insideLeft', fill: '#a3aed0', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: 'white', border: 'none', borderRadius: 16, boxShadow: '0 18px 40px rgba(112,144,176,0.12)' }} />
            <Area 
              type="monotone" 
              dataKey={currentChart.dataKey} 
              name={currentChart.name}
              stroke={currentChart.color} 
              strokeWidth={3} 
              fill={`url(#${sensorType}Grad)`} 
              dot={{ r: 3, fill: currentChart.color, strokeWidth: 2, stroke: 'white' }} 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📋 Full Operation Log</span>
          <input className="history-search-input" value={search} onChange={e => setSearch(e.target.value)} placeholder="🔍 Filter logs..." />
        </div>
        <div style={{ maxHeight: 400, overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr><th>Time</th><th>Type</th><th>Unit</th><th>Fault</th><th>Health</th><th>RUL</th><th>Operator</th><th>Shift</th></tr>
            </thead>
            <tbody>
              {filtered.slice(0, 50).map((r, i) => (
                <tr key={i}>
                  <td style={{ fontSize: 10 }}>{r.timestamp}</td>
                  <td>{r.gear_type}</td>
                  <td>{r.gear_unit}</td>
                  <td style={{ color: pieColors[r.fault_label] || '#2b3674', fontWeight: 600 }}>{r.fault_label}</td>
                  <td style={{ fontWeight: 700 }}>{r.health_score}</td>
                  <td style={{ fontSize: 11 }}>{(r.rul_cycles || 0).toLocaleString()}</td>
                  <td style={{ fontSize: 11 }}>{r.operator_name || '—'}</td>
                  <td style={{ fontSize: 11 }}>{r.shift || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* CSV Download Button */}
      <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center' }}>
        <button 
          onClick={() => downloadFailureLogCSV(filtered, gearType)}
          style={{
            background: 'linear-gradient(135deg, #05cd99 0%, #00b383 100%)',
            padding: '14px 32px',
            fontSize: '15px',
            fontWeight: 700,
            borderRadius: '12px',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(5, 205, 153, 0.3)',
            transition: 'all 0.3s ease',
          }}
          onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
        >
          📊 Download Failure Log (CSV)
        </button>
      </div>
    </div>
  );
}

// CSV Download Function for Failure Log
function downloadFailureLogCSV(historyData, gearType) {
  if (!historyData || historyData.length === 0) {
    alert('No data available to download');
    return;
  }
  
  // Create CSV content with all relevant fields
  const headers = ['Timestamp', 'Gear Type', 'Unit ID', 'Fault Type', 'Confidence (%)', 'Health Score', 'RUL (cycles)', 'Operator', 'Shift'];
  const csvRows = [
    headers.join(','),
    ...historyData.map(row => 
      `${row.timestamp || ''},${row.gear_type || ''},${row.gear_unit || ''},${row.fault_label || ''},${((row.confidence || 0) * 100).toFixed(1)},${row.health_score || 0},${row.rul_cycles || 0},${row.operator_name || 'N/A'},${row.shift || 'N/A'}`
    )
  ];
  
  const csvContent = csvRows.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `GearMind_FailureLog_${gearType}_${Date.now()}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function StatCard({ label, value, color, icon }) {
  const iconColors = { blue: 'blue', green: 'green', red: 'red', amber: 'amber', purple: 'purple' };
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
