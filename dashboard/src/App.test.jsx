import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

// Mock the AuthContext
vi.mock('./context/AuthContext', () => ({
  useAuth: () => ({
    currentUser: { fullName: 'Test User', role: 'Engineer', avatar: 'TU' },
    loading: false,
    isSuperAdmin: false,
    logout: vi.fn(),
  }),
}));

// Mock all page components
vi.mock('./pages/LoginPage', () => ({ default: () => <div>Login Page</div> }));
vi.mock('./pages/MainDashboard', () => ({ default: () => <div>Main Dashboard</div> }));
vi.mock('./pages/DesignParameters', () => ({ default: () => <div>Design Parameters</div> }));
vi.mock('./pages/ReliabilityData', () => ({ default: () => <div>Reliability Data</div> }));
vi.mock('./pages/VibrationPHM', () => ({ default: () => <div>Vibration PHM</div> }));
vi.mock('./pages/ManufacturingQC', () => ({ default: () => <div>Manufacturing QC</div> }));
vi.mock('./pages/StaffDirectory', () => ({ default: () => <div>Staff Directory</div> }));
vi.mock('./pages/ShiftSchedule', () => ({ default: () => <div>Shift Schedule</div> }));
vi.mock('./components/GearScene', () => ({ default: () => <div>3D Gear Animation Scene</div> }));

describe('App - Gear Animation Navigation', () => {
  it('should render GearScene when gear-animation navigation item is clicked', () => {
    render(<App />);

    // Find and click the 3D Gear Animation navigation link
    const gearAnimationLink = screen.getByText('3D Gear Animation');
    fireEvent.click(gearAnimationLink);

    // Verify the GearScene component is rendered
    expect(screen.getByText('3D Gear Animation Scene')).toBeInTheDocument();
  });

  it('should have 3D Gear Animation in sidebar navigation', () => {
    render(<App />);
    
    // Verify the navigation link exists in the sidebar
    expect(screen.getByText('3D Gear Animation')).toBeInTheDocument();
  });
});
