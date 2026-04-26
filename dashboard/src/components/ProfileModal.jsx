import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, User, Shield, Calendar, FileText, Lock, Check, AlertCircle, Mail, Phone, Building2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function ProfileModal({ isOpen, onClose }) {
  const { currentUser, changePassword, isSuperAdmin } = useAuth();
  const [tab, setTab] = useState('identity');
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' });
  const [pwMsg, setPwMsg] = useState({ type: '', text: '' });

  if (!currentUser) return null;

  const handleChangePw = (e) => {
    e.preventDefault();
    setPwMsg({ type: '', text: '' });
    if (pwForm.newPw !== pwForm.confirm) {
      setPwMsg({ type: 'error', text: 'New passwords do not match' });
      return;
    }
    if (pwForm.newPw.length < 6) {
      setPwMsg({ type: 'error', text: 'Password must be at least 6 characters' });
      return;
    }
    const result = changePassword(currentUser.id, pwForm.current, pwForm.newPw);
    if (result.success) {
      setPwMsg({ type: 'success', text: 'Password changed successfully!' });
      setPwForm({ current: '', newPw: '', confirm: '' });
    } else {
      setPwMsg({ type: 'error', text: result.error });
    }
  };

  const tabs = [
    { id: 'identity', label: 'Identity', icon: User },
    { id: 'personal', label: 'Personal', icon: Calendar },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  const roleColor = isSuperAdmin ? '#1e40af' : '#0d9488';

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="profile-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="profile-panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            {/* Header */}
            <div className="profile-header">
              <div className="profile-header-info">
                <div className="profile-avatar-lg" style={{ background: `linear-gradient(135deg, ${roleColor}, ${roleColor}cc)` }}>
                  {currentUser.avatar}
                </div>
                <div>
                  <h2 className="profile-name">{currentUser.fullName}</h2>
                  <span className="profile-role-badge" style={{ background: `${roleColor}18`, color: roleColor }}>
                    {currentUser.role}
                  </span>
                </div>
              </div>
              <button className="profile-close" onClick={onClose}>
                <X size={20} />
              </button>
            </div>

            {/* Tabs */}
            <div className="profile-tabs">
              {tabs.map(t => (
                <button
                  key={t.id}
                  className={`profile-tab ${tab === t.id ? 'active' : ''}`}
                  onClick={() => setTab(t.id)}
                >
                  <t.icon size={16} />
                  {t.label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="profile-content">
              {tab === 'identity' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="profile-section">
                  <ProfileField icon={User} label="Full Name" value={currentUser.fullName} />
                  <ProfileField icon={Shield} label="Employee ID" value={currentUser.employeeId} />
                  <ProfileField icon={Building2} label="Department" value={currentUser.department} />
                  <ProfileField icon={FileText} label="Designation" value={currentUser.designation} />
                  <ProfileField icon={Mail} label="Email" value={currentUser.email} />
                  <ProfileField icon={Phone} label="Phone" value={currentUser.phone} />
                  <div className="profile-field">
                    <div className="profile-field-label">
                      <Building2 size={15} />
                      Location
                    </div>
                    <div className="profile-field-value">{currentUser.location}</div>
                  </div>
                  <div className="profile-field">
                    <div className="profile-field-label">
                      <Calendar size={15} />
                      Current Shift
                    </div>
                    <div className="profile-field-value">
                      <span className="profile-shift-badge">{currentUser.shift}</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {tab === 'personal' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="profile-section">
                  <ProfileField icon={Calendar} label="Date of Birth" value={currentUser.dob} />
                  <div className="profile-field">
                    <div className="profile-field-label">
                      <FileText size={15} />
                      Profile Description
                    </div>
                    <p className="profile-description">{currentUser.description}</p>
                  </div>
                  <div className="profile-field">
                    <div className="profile-field-label">
                      <Shield size={15} />
                      Access Level
                    </div>
                    <div className="profile-field-value" style={{ color: roleColor, fontWeight: 700 }}>
                      {isSuperAdmin ? '🔑 Full System Access' : '🔧 Standard Access'}
                    </div>
                  </div>
                </motion.div>
              )}

              {tab === 'security' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="profile-section">
                  <h3 className="profile-section-title">
                    <Lock size={18} />
                    Change Password
                  </h3>
                  <form onSubmit={handleChangePw} className="profile-pw-form">
                    <div className="login-field">
                      <label>Current Password</label>
                      <input
                        type="password"
                        value={pwForm.current}
                        onChange={e => setPwForm({ ...pwForm, current: e.target.value })}
                        placeholder="Enter current password"
                        required
                      />
                    </div>
                    <div className="login-field">
                      <label>New Password</label>
                      <input
                        type="password"
                        value={pwForm.newPw}
                        onChange={e => setPwForm({ ...pwForm, newPw: e.target.value })}
                        placeholder="Enter new password"
                        required
                      />
                    </div>
                    <div className="login-field">
                      <label>Confirm New Password</label>
                      <input
                        type="password"
                        value={pwForm.confirm}
                        onChange={e => setPwForm({ ...pwForm, confirm: e.target.value })}
                        placeholder="Confirm new password"
                        required
                      />
                    </div>

                    {pwMsg.text && (
                      <div className={`profile-pw-msg ${pwMsg.type}`}>
                        {pwMsg.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                        {pwMsg.text}
                      </div>
                    )}

                    <button type="submit" className="btn btn-primary btn-full">
                      <Lock size={16} />
                      Update Password
                    </button>
                  </form>
                </motion.div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function ProfileField({ icon: Icon, label, value }) {
  return (
    <div className="profile-field">
      <div className="profile-field-label">
        <Icon size={15} />
        {label}
      </div>
      <div className="profile-field-value">{value}</div>
    </div>
  );
}
