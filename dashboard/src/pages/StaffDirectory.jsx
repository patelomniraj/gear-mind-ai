import React, { useState } from 'react';
import { Users, Plus, Pencil, Trash2, Search, X, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const DEPARTMENTS = ['Engineering Management', 'Helical Gear Module', 'Spur Gear Module', 'Bevel Gear Module', 'Quality Control', 'Vibration & PHM', 'Operations', 'AI & Data Science'];
const ROLES = ['Super Admin', 'Senior Gear Engineer', 'Maintenance Technician', 'Quality Inspector', 'PHM Analyst', 'Bevel Gear Specialist', 'Shift Supervisor', 'ML Engineer', 'Junior Engineer'];
const SHIFTS = ['Morning', 'Afternoon', 'Night'];
const LOCATIONS = ['Control Room', 'Gear Line A', 'Gear Line B', 'Gear Line C', 'Testing Bay', 'Monitoring Center', 'Data Lab'];

const EMPTY_FORM = {
  fullName: '', username: '', password: '', employeeId: '', role: ROLES[1],
  department: DEPARTMENTS[1], designation: '', dob: '', phone: '', email: '',
  description: '', shift: 'Morning', location: LOCATIONS[0]
};

export default function StaffDirectory() {
  const { users, addUser, removeUser, updateUser } = useAuth();
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const filtered = users.filter(u =>
    u.fullName.toLowerCase().includes(search.toLowerCase()) ||
    u.employeeId.toLowerCase().includes(search.toLowerCase()) ||
    u.role.toLowerCase().includes(search.toLowerCase()) ||
    u.department.toLowerCase().includes(search.toLowerCase())
  );

  const openAdd = () => {
    setEditId(null);
    setForm({ ...EMPTY_FORM, employeeId: `EMP-${String(users.length + 1).padStart(3, '0')}` });
    setShowForm(true);
  };

  const openEdit = (user) => {
    setEditId(user.id);
    setForm({
      fullName: user.fullName, username: user.username, password: user.password,
      employeeId: user.employeeId, role: user.role, department: user.department,
      designation: user.designation || '', dob: user.dob || '', phone: user.phone || '',
      email: user.email || '', description: user.description || '',
      shift: user.shift || 'Morning', location: user.location || 'Control Room',
    });
    setShowForm(true);
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (editId) {
      updateUser(editId, form);
    } else {
      addUser(form);
    }
    setShowForm(false);
    setForm(EMPTY_FORM);
    setEditId(null);
  };

  const handleDelete = (userId) => {
    removeUser(userId);
    setDeleteConfirm(null);
  };

  const shiftColors = { Morning: '#f59e0b', Afternoon: '#0d9488', Night: '#6366f1' };

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-banner staff-banner">
        <div className="page-banner-icon"><Users size={28} /></div>
        <div>
          <h2>Staff Directory</h2>
          <p>Manage workers, roles, departments, and shift assignments</p>
        </div>
      </div>

      {/* Toolbar */}
      <div className="staff-toolbar">
        <div className="staff-search-wrap">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search by name, ID, role, department..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="staff-search"
          />
        </div>
        <button className="btn btn-primary" onClick={openAdd}>
          <Plus size={16} /> Add Worker
        </button>
      </div>

      {/* Table */}
      <div className="card">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>ID</th>
                <th>Role</th>
                <th>Department</th>
                <th>Shift</th>
                <th>Location</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(u => (
                <tr key={u.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div className="staff-avatar" style={{
                        background: u.role === 'Super Admin'
                          ? 'linear-gradient(135deg, #1e40af, #3b82f6)'
                          : 'linear-gradient(135deg, #0d9488, #14b8a6)'
                      }}>{u.avatar}</div>
                      <div>
                        <div style={{ fontWeight: 600, color: '#1b2559' }}>{u.fullName}</div>
                        <div style={{ fontSize: 11, color: '#a3aed0' }}>{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{u.employeeId}</td>
                  <td><span className="staff-role-badge">{u.role}</span></td>
                  <td style={{ fontSize: 12 }}>{u.department}</td>
                  <td>
                    <span className="staff-shift-badge" style={{ background: `${shiftColors[u.shift]}18`, color: shiftColors[u.shift] }}>
                      {u.shift === 'Morning' ? '🌅' : u.shift === 'Afternoon' ? '🌤' : '🌙'} {u.shift}
                    </span>
                  </td>
                  <td style={{ fontSize: 12 }}>{u.location}</td>
                  <td>
                    <span className={`staff-status ${u.status === 'Active' ? 'active' : 'inactive'}`}>
                      {u.status}
                    </span>
                  </td>
                  <td>
                    <div className="staff-actions">
                      <button className="staff-action-btn edit" onClick={() => openEdit(u)} title="Edit">
                        <Pencil size={14} />
                      </button>
                      {u.role !== 'Super Admin' && (
                        <button className="staff-action-btn delete" onClick={() => setDeleteConfirm(u.id)} title="Delete">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ padding: '12px 0', fontSize: 12, color: '#a3aed0' }}>
          Showing {filtered.length} of {users.length} workers
        </div>
      </div>

      {/* Add/Edit Modal */}
      <AnimatePresence>
        {showForm && (
          <motion.div 
            className="modal-backdrop" 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0 }}
            onClick={() => setShowForm(false)}
          >
            <motion.div 
              className="modal-panel" 
              initial={{ opacity: 0, scale: 0.95, y: 20 }} 
              animate={{ opacity: 1, scale: 1, y: 0 }} 
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>{editId ? 'Edit Worker' : 'Add New Worker'}</h3>
                <button onClick={() => setShowForm(false)}><X size={20} /></button>
              </div>
              <form onSubmit={handleSave} className="modal-form">
                <div className="modal-form-grid">
                  <div className="login-field"><label>Full Name *</label><input required value={form.fullName} onChange={e => setForm({ ...form, fullName: e.target.value })} /></div>
                  <div className="login-field"><label>Username *</label><input required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} /></div>
                  <div className="login-field"><label>Password *</label><input required type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} /></div>
                  <div className="login-field"><label>Employee ID</label><input value={form.employeeId} onChange={e => setForm({ ...form, employeeId: e.target.value })} /></div>
                  <div className="login-field"><label>Role</label><select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>{ROLES.map(r => <option key={r}>{r}</option>)}</select></div>
                  <div className="login-field"><label>Department</label><select value={form.department} onChange={e => setForm({ ...form, department: e.target.value })}>{DEPARTMENTS.map(d => <option key={d}>{d}</option>)}</select></div>
                  <div className="login-field"><label>Designation</label><input value={form.designation} onChange={e => setForm({ ...form, designation: e.target.value })} /></div>
                  <div className="login-field"><label>Date of Birth</label><input type="date" value={form.dob} onChange={e => setForm({ ...form, dob: e.target.value })} /></div>
                  <div className="login-field"><label>Phone</label><input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} /></div>
                  <div className="login-field"><label>Email</label><input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></div>
                  <div className="login-field"><label>Shift</label><select value={form.shift} onChange={e => setForm({ ...form, shift: e.target.value })}>{SHIFTS.map(s => <option key={s}>{s}</option>)}</select></div>
                  <div className="login-field"><label>Location</label><select value={form.location} onChange={e => setForm({ ...form, location: e.target.value })}>{LOCATIONS.map(l => <option key={l}>{l}</option>)}</select></div>
                </div>
                <div className="login-field" style={{ marginTop: 12 }}><label>Description</label><textarea rows={2} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} /></div>
                <div className="modal-form-actions">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary"><Check size={16} /> {editId ? 'Update' : 'Add Worker'}</button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirm */}
      <AnimatePresence>
        {deleteConfirm && (
          <motion.div 
            className="modal-backdrop" 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0 }}
            onClick={() => setDeleteConfirm(null)}
          >
            <motion.div 
              className="modal-panel modal-sm" 
              initial={{ opacity: 0, scale: 0.95, y: 20 }} 
              animate={{ opacity: 1, scale: 1, y: 0 }} 
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header"><h3>Confirm Delete</h3></div>
              <p style={{ color: '#a3aed0', margin: '16px 0' }}>Are you sure you want to remove this worker? This action cannot be undone.</p>
              <div className="modal-form-actions">
                <button className="btn btn-secondary" onClick={() => setDeleteConfirm(null)}>Cancel</button>
                <button className="btn btn-danger" onClick={() => handleDelete(deleteConfirm)}><Trash2 size={16} /> Delete</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
