import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import Sidebar from './components/Sidebar';
import ProfileModal from './components/ProfileModal';
import MainDashboard from './pages/MainDashboard';
import DesignParameters from './pages/DesignParameters';
import ReliabilityData from './pages/ReliabilityData';
import VibrationPHM from './pages/VibrationPHM';
import ManufacturingQC from './pages/ManufacturingQC';
import StaffDirectory from './pages/StaffDirectory';
import ShiftSchedule from './pages/ShiftSchedule';
import { Search, Menu, X } from 'lucide-react';

const PAGE_TITLES = {
  dashboard: 'Main Dashboard',
  design: 'Design Parameters',
  reliability: 'Reliability Data',
  vibration: 'Vibration / PHM',
  manufacturing: 'Manufacturing QC',
  staff: 'Staff Directory',
  shifts: 'Shift Schedule',
};

export default function App() {
  const { currentUser, loading, isSuperAdmin } = useAuth();
  const [activePage, setActivePage] = useState('dashboard');
  const [profileOpen, setProfileOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  if (loading) return <div className="loading"><div className="spinner" /> Loading Elecon...</div>;
  if (!currentUser) return <LoginPage />;

  // Search functionality
  const handleSearch = (query) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    const results = [];
    const lowerQuery = query.toLowerCase();

    // Search in pages
    const pages = [
      { id: 'dashboard', title: 'Main Dashboard', keywords: ['dashboard', 'health', 'gear', 'prediction', 'fault', 'rul', '3d', 'animation'] },
      { id: 'design', title: 'Design Parameters', keywords: ['design', 'parameters', 'specifications', 'helical', 'spur', 'bevel'] },
      { id: 'reliability', title: 'Reliability Data', keywords: ['reliability', 'mtbf', 'failure', 'analysis'] },
      { id: 'vibration', title: 'Vibration / PHM', keywords: ['vibration', 'phm', 'predictive', 'maintenance', 'spectral'] },
      { id: 'manufacturing', title: 'Manufacturing QC', keywords: ['manufacturing', 'quality', 'control', 'qc', 'inspection'] },
      { id: 'staff', title: 'Staff Directory', keywords: ['staff', 'workers', 'employees', 'directory', 'team'] },
      { id: 'shifts', title: 'Shift Schedule', keywords: ['shift', 'schedule', 'roster', 'calendar'] },
    ];

    pages.forEach(page => {
      if (page.title.toLowerCase().includes(lowerQuery) || 
          page.keywords.some(k => k.includes(lowerQuery))) {
        results.push({ type: 'page', ...page });
      }
    });

    // Search in features
    const features = [
      { title: 'SHAP Analysis', page: 'dashboard', keywords: ['shap', 'explainability', 'xai', 'feature importance'] },
      { title: 'LIME Explanations', page: 'dashboard', keywords: ['lime', 'local', 'interpretable', 'explanation'] },
      { title: 'What-If Optimizer', page: 'dashboard', keywords: ['optimizer', 'what-if', 'optimization', 'differential evolution'] },
      { title: '3D Gear Animation', page: 'dashboard', keywords: ['3d', 'animation', 'gear', 'visualization', 'three', 'threejs'] },
      { title: 'Cost Impact Analysis', page: 'dashboard', keywords: ['cost', 'financial', 'impact', 'savings'] },
      { title: 'Model Comparison', page: 'dashboard', keywords: ['model', 'comparison', 'accuracy', 'performance'] },
      { title: 'Trends & History', page: 'dashboard', keywords: ['trends', 'history', 'historical', 'logs'] },
      { title: 'Gear Health Gauge', page: 'dashboard', keywords: ['health', 'gauge', 'score', 'status'] },
      { title: 'RUL Prediction', page: 'dashboard', keywords: ['rul', 'remaining', 'useful', 'life', 'cycles'] },
    ];

    features.forEach(feature => {
      if (feature.title.toLowerCase().includes(lowerQuery) || 
          feature.keywords.some(k => k.includes(lowerQuery))) {
        results.push({ type: 'feature', ...feature });
      }
    });

    setSearchResults(results);
    setShowSearchResults(true);
  };

  const navigateToResult = (result) => {
    setActivePage(result.page || result.id);
    setShowSearchResults(false);
    setSearchQuery('');
    setSidebarOpen(false);
  };

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': return <MainDashboard />;
      case 'design': return <DesignParameters />;
      case 'reliability': return <ReliabilityData />;
      case 'vibration': return <VibrationPHM />;
      case 'manufacturing': return <ManufacturingQC />;
      case 'staff': return isSuperAdmin ? <StaffDirectory /> : <MainDashboard />;
      case 'shifts': return isSuperAdmin ? <ShiftSchedule /> : <MainDashboard />;
      default: return <MainDashboard />;
    }
  };

  return (
    <div className="app-layout">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      <div className={`sidebar ${sidebarOpen ? 'sidebar-mobile-open' : ''}`}>
        <Sidebar activePage={activePage} setActivePage={(p) => { setActivePage(p); setSidebarOpen(false); }} />
      </div>

      <div className="main-content">
        {/* Top Header */}
        <div className="top-header">
          <div className="top-header-left">
            <button className="mobile-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
              {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
            <div>
              <div className="breadcrumb">Pages / {PAGE_TITLES[activePage]}</div>
              <h1>{PAGE_TITLES[activePage]}</h1>
            </div>
          </div>
          <div className="header-right">
            <div className="header-search-wrap">
              <Search size={16} />
              <input 
                type="text" 
                className="header-search" 
                placeholder="Search pages, features..." 
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                onFocus={() => searchQuery && setShowSearchResults(true)}
              />
              {showSearchResults && searchResults.length > 0 && (
                <div className="search-results-dropdown">
                  {searchResults.map((result, idx) => (
                    <div 
                      key={idx} 
                      className="search-result-item"
                      onClick={() => navigateToResult(result)}
                    >
                      <div className="search-result-icon">
                        {result.type === 'page' ? '📄' : '⚡'}
                      </div>
                      <div className="search-result-content">
                        <div className="search-result-title">{result.title}</div>
                        <div className="search-result-type">
                          {result.type === 'page' ? 'Page' : 'Feature'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="header-user-section" onClick={() => setProfileOpen(true)}>
              <div className="header-avatar" style={{
                background: isSuperAdmin
                  ? 'linear-gradient(135deg, #1e40af, #3b82f6)'
                  : 'linear-gradient(135deg, #0d9488, #14b8a6)'
              }}>
                {currentUser.avatar}
              </div>
              <div className="header-user-info">
                <div className="header-user-name">{currentUser.fullName}</div>
                <div className="header-user-role">{currentUser.role}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        {renderPage()}

        {/* Footer */}
        <div className="footer">
          ⚙ Elecon v4.0 · Gear Management System · Elecon Engineering Works Pvt. Ltd., Anand, Gujarat
        </div>
      </div>

      {/* Profile Modal */}
      <ProfileModal isOpen={profileOpen} onClose={() => setProfileOpen(false)} />
    </div>
  );
}
