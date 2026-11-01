import React from 'react';
import {
  LayoutDashboard,
  Search,
  BarChart3,
  Network,
  Users,
  Target,
  Lightbulb,
  Sparkles,
  Database,
  CheckCircle,
} from 'lucide-react';
import { useApi } from '../hooks/useApi';

interface AppShellProps {
  activeScreen: string;
  onNavigate: (screen: string) => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ activeScreen, onNavigate, children }) => {
  const { data: etlStatus } = useApi<any>('/api/etl/status');

  const analyticsNav = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: <LayoutDashboard size={16} /> },
    { id: 'exploration', label: 'Data Exploration', icon: <Search size={16} /> },
    { id: 'sales', label: 'Wellbeing Analysis', icon: <BarChart3 size={16} /> },
    { id: 'market-basket', label: 'Market Basket', icon: <Network size={16} /> },
    { id: 'segmentation', label: 'Student Segmentation', icon: <Users size={16} /> },
    { id: 'predict', label: 'Predictive Modeling', icon: <Target size={16} /> },
    { id: 'insights', label: 'Insights', icon: <Lightbulb size={16} /> },
  ];

  const experimentsNav = [
    { id: 'lab-1', num: 1, label: 'Lab 1 — Data Warehouse Design' },
    { id: 'lab-2', num: 2, label: 'Lab 2 — OLAP Operations' },
    { id: 'lab-3', num: 3, label: 'Lab 3 — Data Visualization' },
    { id: 'lab-4', num: 4, label: 'Lab 4 — Linear Regression' },
    { id: 'lab-5', num: 5, label: 'Lab 5 — Decision Tree Induction' },
    { id: 'lab-6', num: 6, label: 'Lab 6 — Naive Bayes Classification' },
    { id: 'lab-7', num: 7, label: 'Lab 7 — K-Means Clustering' },
    { id: 'lab-8', num: 8, label: 'Lab 8 — Agglomerative Clustering' },
    { id: 'lab-9', num: 9, label: 'Lab 9 — Apriori Association Rules' },
    { id: 'lab-10', num: 10, label: 'Lab 10 — Integrated Mining Pipeline' },
  ];

  const getScreenTitle = () => {
    const aItem = analyticsNav.find((n) => n.id === activeScreen);
    if (aItem) return aItem.label;
    const eItem = experimentsNav.find((e) => e.id === activeScreen);
    if (eItem) return eItem.label;
    return 'Student DWM Analytics';
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg)' }}>
      {/* Sidebar Navigation */}
      <aside
        style={{
          width: '270px',
          backgroundColor: '#fbf8f1',
          borderRight: '1px solid var(--bd)',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}
      >
        {/* Brand Header */}
        <div
          style={{
            padding: '18px 20px',
            borderBottom: '1px solid var(--bd)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: 'var(--acd)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              fontSize: '16px',
              flexShrink: 0,
            }}
          >
            D
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--tx)', letterSpacing: '-0.2px' }}>
              Student DWM
            </div>
            <div style={{ fontSize: '11px', color: 'var(--mu)' }}>Analytics & Laboratory Suite</div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ padding: '16px 10px', display: 'flex', flexDirection: 'column', flex: 1, overflowY: 'auto' }}>
          {/* ANALYTICS SECTION */}
          <div className="nav-group">
            <span className="nav-label">Analytics</span>
            {analyticsNav.map((item) => {
              const isActive = activeScreen === item.id;
              return (
                <button
                  key={item.id}
                  className={`sidebar-nav-btn ${isActive ? 'active' : ''}`}
                  onClick={() => onNavigate(item.id)}
                >
                  <span style={{ color: isActive ? 'var(--acd)' : 'var(--mu)', display: 'inline-flex' }}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* EXPERIMENTS SECTION */}
          <div className="nav-group" style={{ marginTop: '10px' }}>
            <span className="nav-label">Academic Experiments</span>
            {experimentsNav.map((lab) => {
              const isActive = activeScreen === lab.id;
              return (
                <button
                  key={lab.id}
                  className={`sidebar-nav-btn ${isActive ? 'active' : ''}`}
                  onClick={() => onNavigate(lab.id)}
                >
                  <span className="lab-dot">{lab.num}</span>
                  <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {lab.label}
                  </span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Footer info */}
        <div style={{ padding: '14px 18px', borderTop: '1px solid var(--bd)', fontSize: '11px', color: 'var(--mu)' }}>
          SQLite Star Schema · v1.1.0
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Topbar */}
        <header
          style={{
            height: '60px',
            backgroundColor: '#fff',
            borderBottom: '1px solid var(--bd)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
          }}
        >
          <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--tx)' }}>
            {getScreenTitle()}
          </div>

          {/* Dataset Status Chip */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: '16px',
              backgroundColor: 'var(--soft)',
              color: 'var(--acd)',
              fontSize: '12px',
              fontWeight: 600,
              border: '1px solid #c9dec9',
            }}
          >
            <CheckCircle size={14} />
            <span>
              {etlStatus?.row_count?.toLocaleString() || '5,000'} respondents · Active v{etlStatus?.active_dataset_version || 1}
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppShell;
