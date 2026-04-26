import React, { useState, useEffect } from 'react';
import { CalendarDays, GripVertical, Clock, MapPin } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SHIFTS = [
  { id: 'morning', label: 'Morning', time: '06:00 – 14:00', icon: '🌅', color: '#f59e0b', bg: '#fef3c7' },
  { id: 'afternoon', label: 'Afternoon', time: '14:00 – 22:00', icon: '🌤', color: '#0d9488', bg: '#ccfbf1' },
  { id: 'night', label: 'Night', time: '22:00 – 06:00', icon: '🌙', color: '#6366f1', bg: '#e0e7ff' },
];

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const LOCATIONS = ['Gear Line A', 'Gear Line B', 'Gear Line C', 'Testing Bay', 'Control Room', 'Monitoring Center', 'Data Lab'];

function generateSchedule(users) {
  const workers = users.filter(u => u.role !== 'Super Admin');
  const schedule = {};
  DAYS.forEach((day, dayIdx) => {
    schedule[day] = {};
    SHIFTS.forEach((shift, shiftIdx) => {
      // Auto-rotate: each worker shifts forward every day
      const assigned = workers.filter((_, workerIdx) => {
        const rotation = (workerIdx + dayIdx) % 3;
        return rotation === shiftIdx;
      });
      schedule[day][shift.id] = assigned.map(w => ({
        id: w.id,
        name: w.fullName,
        avatar: w.avatar,
        role: w.role,
        location: LOCATIONS[(workers.indexOf(w)) % LOCATIONS.length],
      }));
    });
  });
  return schedule;
}

export default function ShiftSchedule() {
  const { users } = useAuth();
  const [schedule, setSchedule] = useState({});
  const [view, setView] = useState('calendar'); // 'calendar' or 'gantt'
  const [dragItem, setDragItem] = useState(null);

  useEffect(() => {
    setSchedule(generateSchedule(users));
  }, [users]);

  // Drag & Drop handlers
  const handleDragStart = (day, shiftId, worker) => {
    setDragItem({ day, shiftId, worker });
  };

  const handleDrop = (targetDay, targetShiftId) => {
    if (!dragItem) return;
    const { day: srcDay, shiftId: srcShift, worker } = dragItem;
    if (srcDay === targetDay && srcShift === targetShiftId) return;

    setSchedule(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      // Remove from source
      next[srcDay][srcShift] = next[srcDay][srcShift].filter(w => w.id !== worker.id);
      // Add to target
      next[targetDay][targetShiftId] = [...(next[targetDay][targetShiftId] || []), worker];
      return next;
    });
    setDragItem(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('shift-drop-active');
  };

  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove('shift-drop-active');
  };

  const handleDropWrap = (e, day, shiftId) => {
    e.preventDefault();
    e.currentTarget.classList.remove('shift-drop-active');
    handleDrop(day, shiftId);
  };

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-banner shift-banner">
        <div className="page-banner-icon"><CalendarDays size={28} /></div>
        <div>
          <h2>Shift Schedule</h2>
          <p>3-Shift Rotation · Drag & Drop to Swap Workers · Auto-Generated Timetable</p>
        </div>
      </div>

      {/* Shift Legend */}
      <div className="shift-legend">
        {SHIFTS.map(s => (
          <div key={s.id} className="shift-legend-item" style={{ background: s.bg, borderLeft: `3px solid ${s.color}` }}>
            <span className="shift-legend-icon">{s.icon}</span>
            <div>
              <div style={{ fontWeight: 700, color: s.color, fontSize: 13 }}>{s.label}</div>
              <div style={{ fontSize: 11, color: '#a3aed0' }}><Clock size={11} /> {s.time}</div>
            </div>
          </div>
        ))}
      </div>

      {/* View Toggle */}
      <div style={{ marginBottom: 16 }}>
        <div className="toggle-group">
          <button className={`toggle-btn ${view === 'calendar' ? 'active' : ''}`} onClick={() => setView('calendar')}>📅 Calendar View</button>
          <button className={`toggle-btn ${view === 'gantt' ? 'active' : ''}`} onClick={() => setView('gantt')}>📊 Gantt View</button>
        </div>
      </div>

      {/* Calendar View */}
      {view === 'calendar' && (
        <div className="shift-calendar">
          {/* Day Headers */}
          <div className="shift-cal-header">
            <div className="shift-cal-corner">Shift / Day</div>
            {DAYS.map(d => (
              <div key={d} className="shift-cal-day-header">{d.slice(0, 3)}</div>
            ))}
          </div>

          {/* Shift Rows */}
          {SHIFTS.map(shift => (
            <div key={shift.id} className="shift-cal-row">
              <div className="shift-cal-label" style={{ background: shift.bg, color: shift.color }}>
                <span>{shift.icon}</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 12 }}>{shift.label}</div>
                  <div style={{ fontSize: 10, opacity: 0.8 }}>{shift.time}</div>
                </div>
              </div>
              {DAYS.map(day => {
                const workers = schedule[day]?.[shift.id] || [];
                return (
                  <div
                    key={day}
                    className="shift-cal-cell"
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={e => handleDropWrap(e, day, shift.id)}
                  >
                    {workers.map(w => (
                      <div
                        key={w.id}
                        className="shift-worker-chip"
                        draggable
                        onDragStart={() => handleDragStart(day, shift.id, w)}
                        style={{ borderLeftColor: shift.color }}
                      >
                        <GripVertical size={12} className="shift-grip" />
                        <div className="shift-worker-avatar" style={{ background: `${shift.color}30`, color: shift.color }}>{w.avatar}</div>
                        <div className="shift-worker-info">
                          <div className="shift-worker-name">{w.name}</div>
                          <div className="shift-worker-loc"><MapPin size={9} /> {w.location}</div>
                        </div>
                      </div>
                    ))}
                    {workers.length === 0 && (
                      <div className="shift-empty">—</div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}

      {/* Gantt View */}
      {view === 'gantt' && (
        <div className="card">
          <div className="card-header"><div className="card-header-icon">📊</div> Weekly Gantt Chart</div>
          <div className="gantt-container">
            {/* Time axis */}
            <div className="gantt-header">
              <div className="gantt-label-col">Worker</div>
              {DAYS.map(d => (
                <div key={d} className="gantt-day-col">{d.slice(0, 3)}</div>
              ))}
            </div>
            {/* Worker rows */}
            {users.filter(u => u.role !== 'Super Admin').map(worker => (
              <div key={worker.id} className="gantt-row">
                <div className="gantt-worker-label">
                  <div className="shift-worker-avatar" style={{ background: '#e0e7ff', color: '#6366f1', minWidth: 28, height: 28, fontSize: 10 }}>{worker.avatar}</div>
                  <span>{worker.fullName.split(' ')[0]}</span>
                </div>
                {DAYS.map(day => {
                  const shiftForDay = SHIFTS.find(s => {
                    const workers = schedule[day]?.[s.id] || [];
                    return workers.some(w => w.id === worker.id);
                  });
                  return (
                    <div key={day} className="gantt-cell">
                      {shiftForDay ? (
                        <div className="gantt-bar" style={{ background: `linear-gradient(135deg, ${shiftForDay.color}22, ${shiftForDay.color}44)`, borderLeft: `3px solid ${shiftForDay.color}` }}>
                          <span style={{ color: shiftForDay.color, fontWeight: 700, fontSize: 11 }}>{shiftForDay.icon} {shiftForDay.label}</span>
                        </div>
                      ) : (
                        <div className="gantt-empty">off</div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
