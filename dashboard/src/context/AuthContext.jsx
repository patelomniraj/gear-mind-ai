import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// ── Default Users Store ──────────────────────────────────
const DEFAULT_USERS = [
  {
    id: 'USR-001', username: 'ompatel', password: '1234567890',
    fullName: 'Om Patel', employeeId: 'EMP-001', role: 'Super Admin',
    department: 'Engineering Management', designation: 'Chief Engineer',
    dob: '1998-07-15', phone: '+91 98765 43210', email: 'om.patel@prognos.in',
    description: 'Lead systems architect overseeing all gear predictive maintenance modules. 8+ years of experience in industrial IoT and machine learning applications.',
    avatar: 'OP', shift: 'Morning', location: 'Control Room', status: 'Active',
  },
  {
    id: 'USR-002', username: 'isha', password: 'isha1234',
    fullName: 'Isha Patel', employeeId: 'EMP-002', role: 'Senior Gear Engineer',
    department: 'Helical Gear Module', designation: 'Senior Engineer',
    dob: '1999-03-22', phone: '+91 98765 43211', email: 'isha.patel@prognos.in',
    description: 'Specialist in helical gear analysis and vibration diagnostics. Responsible for gear health monitoring on Line A.',
    avatar: 'IP', shift: 'Morning', location: 'Gear Line A', status: 'Active',
  },
  {
    id: 'USR-003', username: 'rajesh', password: 'rajesh1234',
    fullName: 'Rajesh Kumar', employeeId: 'EMP-003', role: 'Maintenance Technician',
    department: 'Spur Gear Module', designation: 'Technician III',
    dob: '1995-11-08', phone: '+91 98765 43212', email: 'rajesh.kumar@prognos.in',
    description: 'Experienced maintenance technician specializing in spur gear overhauls and preventive maintenance scheduling.',
    avatar: 'RK', shift: 'Afternoon', location: 'Gear Line B', status: 'Active',
  },
  {
    id: 'USR-004', username: 'priya', password: 'priya1234',
    fullName: 'Priya Sharma', employeeId: 'EMP-004', role: 'Quality Inspector',
    department: 'Quality Control', designation: 'QC Lead',
    dob: '1997-06-30', phone: '+91 98765 43213', email: 'priya.sharma@prognos.in',
    description: 'Quality control specialist with expertise in dimensional inspection, AGMA tolerances, and manufacturing QC processes.',
    avatar: 'PS', shift: 'Morning', location: 'Testing Bay', status: 'Active',
  },
  {
    id: 'USR-005', username: 'arjun', password: 'arjun1234',
    fullName: 'Arjun Mehta', employeeId: 'EMP-005', role: 'PHM Analyst',
    department: 'Vibration & PHM', designation: 'Data Analyst',
    dob: '2000-01-14', phone: '+91 98765 43214', email: 'arjun.mehta@prognos.in',
    description: 'Prognostics & Health Management analyst. Focuses on vibration spectral analysis and failure prediction models.',
    avatar: 'AM', shift: 'Night', location: 'Monitoring Center', status: 'Active',
  },
  {
    id: 'USR-006', username: 'sneha', password: 'sneha1234',
    fullName: 'Sneha Desai', employeeId: 'EMP-006', role: 'Bevel Gear Specialist',
    department: 'Bevel Gear Module', designation: 'Engineer',
    dob: '1998-09-05', phone: '+91 98765 43215', email: 'sneha.desai@prognos.in',
    description: 'Bevel gear specialist handling AGMA 2003-B97 compliance. Manages right-angle drive testing protocols.',
    avatar: 'SD', shift: 'Afternoon', location: 'Gear Line C', status: 'Active',
  },
  {
    id: 'USR-007', username: 'vikram', password: 'vikram1234',
    fullName: 'Vikram Singh', employeeId: 'EMP-007', role: 'Shift Supervisor',
    department: 'Operations', designation: 'Shift Lead',
    dob: '1993-12-20', phone: '+91 98765 43216', email: 'vikram.singh@prognos.in',
    description: 'Night shift supervisor responsible for monitoring all gear lines during 22:00–06:00 operations.',
    avatar: 'VS', shift: 'Night', location: 'Control Room', status: 'Active',
  },
  {
    id: 'USR-008', username: 'ananya', password: 'ananya1234',
    fullName: 'Ananya Reddy', employeeId: 'EMP-008', role: 'ML Engineer',
    department: 'AI & Data Science', designation: 'Junior Engineer',
    dob: '2001-04-18', phone: '+91 98765 43217', email: 'ananya.reddy@prognos.in',
    description: 'Machine learning engineer working on model training, SHAP/LIME interpretability, and anomaly detection algorithms.',
    avatar: 'AR', shift: 'Morning', location: 'Data Lab', status: 'Active',
  },
];

function getStoredUsers() {
  try {
    const stored = localStorage.getItem('prognos_users');
    if (stored) return JSON.parse(stored);
  } catch {}
  return DEFAULT_USERS;
}

function storeUsers(users) {
  localStorage.setItem('prognos_users', JSON.stringify(users));
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [users, setUsers] = useState(getStoredUsers);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const session = localStorage.getItem('prognos_session');
      if (session) {
        const parsed = JSON.parse(session);
        const u = getStoredUsers().find(u => u.id === parsed.id);
        if (u) setCurrentUser(u);
      }
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    storeUsers(users);
  }, [users]);

  const login = (username, password) => {
    const user = users.find(u => u.username === username && u.password === password);
    if (!user) return { success: false, error: 'Invalid username or password' };
    setCurrentUser(user);
    localStorage.setItem('prognos_session', JSON.stringify({ id: user.id }));
    return { success: true };
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('prognos_session');
  };

  const updateUser = (userId, updates) => {
    setUsers(prev => {
      const next = prev.map(u => u.id === userId ? { ...u, ...updates } : u);
      if (currentUser?.id === userId) {
        const updated = next.find(u => u.id === userId);
        setCurrentUser(updated);
        localStorage.setItem('prognos_session', JSON.stringify({ id: updated.id }));
      }
      return next;
    });
  };

  const addUser = (user) => {
    const newUser = {
      ...user,
      id: 'USR-' + String(users.length + 1).padStart(3, '0'),
      avatar: user.fullName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2),
      status: 'Active',
    };
    setUsers(prev => [...prev, newUser]);
    return newUser;
  };

  const removeUser = (userId) => {
    setUsers(prev => prev.filter(u => u.id !== userId));
  };

  const changePassword = (userId, currentPw, newPw) => {
    const user = users.find(u => u.id === userId);
    if (!user) return { success: false, error: 'User not found' };
    if (user.password !== currentPw) return { success: false, error: 'Current password is incorrect' };
    updateUser(userId, { password: newPw });
    return { success: true };
  };

  const isSuperAdmin = currentUser?.role === 'Super Admin';

  return (
    <AuthContext.Provider value={{
      currentUser, users, loading, login, logout,
      updateUser, addUser, removeUser, changePassword, isSuperAdmin,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
