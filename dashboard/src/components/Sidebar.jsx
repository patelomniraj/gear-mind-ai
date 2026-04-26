import React from 'react';
import {
  LayoutDashboard, Ruler, TrendingUp, Activity, ClipboardCheck,
  Users, CalendarDays, LogOut, Cog, ChevronRight, Settings
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Main Dashboard', icon: LayoutDashboard, adminOnly: false },
  { id: 'design', label: 'Design Parameters', icon: Ruler, adminOnly: false },
  { id: 'reliability', label: 'Reliability Data', icon: TrendingUp, adminOnly: false },
  { id: 'vibration', label: 'Vibration / PHM', icon: Activity, adminOnly: false },
  { id: 'manufacturing', label: 'Manufacturing QC', icon: ClipboardCheck, adminOnly: false },
  { id: 'divider', label: '', icon: null, adminOnly: true },
  { id: 'staff', label: 'Staff Directory', icon: Users, adminOnly: true },
  { id: 'shifts', label: 'Shift Schedule', icon: CalendarDays, adminOnly: true },
];

export default function Sidebar({ activePage, setActivePage }) {
  const { currentUser, logout, isSuperAdmin } = useAuth();

  return (
    <div className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <h1><Cog size={24} className="sidebar-cog" /> Elecon</h1>
        <div className="subtitle">GEAR MANAGEMENT SYSTEM</div>
      </div>

      {/* User Card */}
      <div className="sidebar-user-card">
        <div className="sidebar-user-avatar" style={{
          background: isSuperAdmin
            ? 'linear-gradient(135deg, #1e40af, #3b82f6)'
            : 'linear-gradient(135deg, #0d9488, #14b8a6)'
        }}>
          {currentUser?.avatar || 'U'}
        </div>
        <div className="sidebar-user-info">
          <div className="sidebar-user-name">{currentUser?.fullName || 'User'}</div>
          <div className="sidebar-user-role">{currentUser?.role || 'Worker'}</div>
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-nav-label">NAVIGATION</div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.filter(item => !item.adminOnly || isSuperAdmin).map(item => {
          if (item.id === 'divider') {
            return <div key="divider" className="sidebar-divider"><span>ADMIN TOOLS</span></div>;
          }
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {isActive && <ChevronRight size={16} className="sidebar-nav-arrow" />}
            </button>
          );
        })}
      </nav>

      {/* System Info Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-system-info">
          <div className="sidebar-system-title">System Info</div>
          ML: GBM · XGBoost · RF · LR · SVM<br/>
          XAI: SHAP · LIME · Isolation Forest<br/>
          LLM: Groq · LLaMA 3.3 70B<br/>
          Tracking: MLflow · v4.0
        </div>
        <button className="sidebar-logout" onClick={logout}>
          <LogOut size={16} />
          Sign Out
        </button>
      </div>
    </div>
  );
}
