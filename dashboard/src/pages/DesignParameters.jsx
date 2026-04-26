import React, { useState, useEffect } from 'react';
import { Ruler, Cog, Zap, ChevronDown, ChevronUp } from 'lucide-react';
import * as api from '../api/gearApi';

export default function DesignParameters() {
  const [specs, setSpecs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({ shared: true, pinion: true, gear: true, perf: true });

  useEffect(() => {
    api.getBevelSpecs()
      .then(data => { setSpecs(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading"><span className="spinner" /> Loading Design Parameters...</div>;
  if (!specs) return <div className="card" style={{ color: '#a3aed0' }}>⚠ Could not load bevel gear specifications</div>;

  const toggle = (key) => setExpanded(p => ({ ...p, [key]: !p[key] }));
  const { identification, geometric_data, performance } = specs;

  return (
    <div className="fade-in">
      {/* Header Banner */}
      <div className="page-banner design-banner">
        <div className="page-banner-icon"><Ruler size={28} /></div>
        <div>
          <h2>Design Parameters</h2>
          <p>Bevel Gear — Pinion/Gear 18:18 · AGMA 2003-B97 Compliant</p>
        </div>
      </div>

      {/* Identification Card */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header"><div className="card-header-icon">📋</div> Project Identification</div>
        <div className="design-id-grid">
          {Object.entries(identification).map(([key, val]) => (
            <div key={key} className="design-id-item">
              <span className="design-id-label">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
              <span className="design-id-value">{val}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Gear Mesh Diagram */}
      <div className="card" style={{ marginBottom: 20, textAlign: 'center' }}>
        <div className="card-header"><div className="card-header-icon"><Cog size={18} /></div> Gear Mesh Diagram — 18:18 Miter</div>
        <div className="gear-mesh-diagram">
          <div className="gear-mesh-circle pinion">
            <div className="gear-mesh-label">PINION</div>
            <div className="gear-mesh-teeth">Z = 18</div>
            <div className="gear-mesh-dim">{geometric_data.pinion.outer_pitch_diameter_mm} mm</div>
          </div>
          <div className="gear-mesh-connector">
            <div className="gear-mesh-angle">90°</div>
            <div className="gear-mesh-arrow">⟷</div>
            <div className="gear-mesh-module">m = {geometric_data.shared_dimensions.outer_module_mm}</div>
          </div>
          <div className="gear-mesh-circle gear">
            <div className="gear-mesh-label">GEAR</div>
            <div className="gear-mesh-teeth">Z = 18</div>
            <div className="gear-mesh-dim">{geometric_data.gear.outer_pitch_diameter_mm} mm</div>
          </div>
        </div>
      </div>

      {/* Data Tables */}
      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Shared Dimensions */}
        <div className="card">
          <div className="card-header design-collapse-header" onClick={() => toggle('shared')}>
            <div className="card-header-icon">📐</div>
            Shared Dimensions
            {expanded.shared ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expanded.shared && (
            <table className="data-table">
              <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
              <tbody>
                {Object.entries(geometric_data.shared_dimensions).map(([k, v]) => (
                  <tr key={k}>
                    <td>{k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
                    <td className="design-val">{typeof v === 'number' ? v.toFixed(4) : v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Performance */}
        <div className="card">
          <div className="card-header design-collapse-header" onClick={() => toggle('perf')}>
            <div className="card-header-icon"><Zap size={18} /></div>
            Performance Data
            {expanded.perf ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expanded.perf && (
            <table className="data-table">
              <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
              <tbody>
                {Object.entries(performance).map(([k, v]) => (
                  <tr key={k}>
                    <td>{k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
                    <td className="design-val">{typeof v === 'number' ? v.toFixed(2) : v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="grid-2">
        {/* Pinion */}
        <div className="card">
          <div className="card-header design-collapse-header" onClick={() => toggle('pinion')}>
            <div className="card-header-icon" style={{ background: '#e0f2fe', color: '#0284c7' }}>P</div>
            Pinion Specifications
            {expanded.pinion ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expanded.pinion && (
            <table className="data-table">
              <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
              <tbody>
                {Object.entries(geometric_data.pinion).map(([k, v]) => (
                  <tr key={k}>
                    <td>{k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
                    <td className="design-val">{typeof v === 'number' ? v.toFixed(4) : v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Gear */}
        <div className="card">
          <div className="card-header design-collapse-header" onClick={() => toggle('gear')}>
            <div className="card-header-icon" style={{ background: '#fef3c7', color: '#d97706' }}>G</div>
            Gear Specifications
            {expanded.gear ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expanded.gear && (
            <table className="data-table">
              <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
              <tbody>
                {Object.entries(geometric_data.gear).map(([k, v]) => (
                  <tr key={k}>
                    <td>{k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
                    <td className="design-val">{typeof v === 'number' ? v.toFixed(4) : v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
