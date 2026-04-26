import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

// Mock the AuthContext
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    currentUser: { fullName: 'Test User', role: 'Engineer', avatar: 'TU' },
    loading: false,
    isSuperAdmin: false,
    logout: vi.fn(),
  }),
}));

// Mock all page components
vi.mock('../pages/LoginPage', () => ({ default: () => <div>Login Page</div> }));
vi.mock('../pages/MainDashboard', () => ({ default: () => <div>Main Dashboard</div> }));
vi.mock('../pages/DesignParameters', () => ({ default: () => <div>Design Parameters</div> }));
vi.mock('../pages/ReliabilityData', () => ({ default: () => <div>Reliability Data</div> }));
vi.mock('../pages/VibrationPHM', () => ({ default: () => <div>Vibration PHM</div> }));
vi.mock('../pages/ManufacturingQC', () => ({ default: () => <div>Manufacturing QC</div> }));
vi.mock('../pages/StaffDirectory', () => ({ default: () => <div>Staff Directory</div> }));
vi.mock('../pages/ShiftSchedule', () => ({ default: () => <div>Shift Schedule</div> }));

// Mock GearScene component with a test identifier
vi.mock('./GearScene', () => ({ 
  default: () => <div data-testid="gear-scene-component">3D Gear Animation Scene</div> 
}));

/**
 * Integration tests for dashboard navigation to 3D Gear Animation page
 * 
 * **Validates: Requirements 13.1**
 * 
 * These tests verify that:
 * 1. The '/gear-animation' route correctly renders the GearScene component
 * 2. The sidebar navigation link successfully navigates to the gear animation page
 */
describe('Dashboard Navigation - 3D Gear Animation Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Test: Route renders GearScene component
   * 
   * Verifies that when the gear-animation route is active,
   * the GearScene component is rendered in the main content area.
   */
  it('should render GearScene component when gear-animation route is active', () => {
    render(<App />);

    // Navigate to gear animation page via sidebar
    const gearAnimationLink = screen.getByText('3D Gear Animation');
    fireEvent.click(gearAnimationLink);

    // Verify the GearScene component is rendered
    const gearScene = screen.getByTestId('gear-scene-component');
    expect(gearScene).toBeInTheDocument();
    expect(gearScene).toHaveTextContent('3D Gear Animation Scene');
  });

  /**
   * Test: Sidebar link navigates to gear animation page
   * 
   * Verifies that clicking the "3D Gear Animation" link in the sidebar
   * successfully navigates to the gear animation page and updates the page title.
   */
  it('should navigate to gear animation page when sidebar link is clicked', () => {
    render(<App />);

    // Find and click the 3D Gear Animation navigation link
    const gearAnimationLink = screen.getByText('3D Gear Animation');
    expect(gearAnimationLink).toBeInTheDocument();
    
    fireEvent.click(gearAnimationLink);

    // Verify navigation occurred
    expect(screen.getByTestId('gear-scene-component')).toBeInTheDocument();
    
    // Verify page title updated in breadcrumb
    expect(screen.getByText(/Pages \/ 3D Gear Animation/)).toBeInTheDocument();
  });

  /**
   * Test: Sidebar link is visible and accessible
   * 
   * Verifies that the 3D Gear Animation navigation link exists
   * in the sidebar and is accessible to users.
   */
  it('should have 3D Gear Animation link visible in sidebar navigation', () => {
    render(<App />);
    
    // Verify the navigation link exists in the sidebar
    const gearAnimationLink = screen.getByText('3D Gear Animation');
    expect(gearAnimationLink).toBeInTheDocument();
    
    // Verify it's a clickable button
    expect(gearAnimationLink.closest('button')).toBeInTheDocument();
  });

  /**
   * Test: Navigation maintains state
   * 
   * Verifies that navigating away from and back to the gear animation
   * page works correctly.
   */
  it('should maintain navigation state when switching between pages', () => {
    render(<App />);

    // Navigate to gear animation
    const gearAnimationLink = screen.getByRole('button', { name: /3D Gear Animation/i });
    fireEvent.click(gearAnimationLink);
    expect(screen.getByTestId('gear-scene-component')).toBeInTheDocument();

    // Navigate to another page
    const designLink = screen.getByRole('button', { name: /Design Parameters/i });
    fireEvent.click(designLink);
    expect(screen.getByText(/Pages \/ Design Parameters/)).toBeInTheDocument();
    expect(screen.queryByTestId('gear-scene-component')).not.toBeInTheDocument();

    // Navigate back to gear animation
    fireEvent.click(gearAnimationLink);
    expect(screen.getByTestId('gear-scene-component')).toBeInTheDocument();
  });

  /**
   * Test: Page title updates correctly
   * 
   * Verifies that the page title in the header updates to
   * "3D Gear Animation" when navigating to the gear animation page.
   */
  it('should update page title to "3D Gear Animation" when navigating to gear page', () => {
    render(<App />);

    // Navigate to gear animation page
    const gearAnimationLink = screen.getByText('3D Gear Animation');
    fireEvent.click(gearAnimationLink);

    // Verify page title is updated in the header
    const pageTitles = screen.getAllByText('3D Gear Animation');
    expect(pageTitles.length).toBeGreaterThan(0);
    
    // Verify breadcrumb shows correct page
    expect(screen.getByText(/Pages \/ 3D Gear Animation/)).toBeInTheDocument();
  });
});
