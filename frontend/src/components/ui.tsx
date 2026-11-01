import React, { useState } from 'react';
import {
  RotateCcw,
  Play,
  CheckCircle,
  AlertTriangle,
  Info,
  X,
  Copy,
  Check,
  ChevronRight,
  Database,
} from 'lucide-react';

/* ─── Button ─── */
export const Button: React.FC<{
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
  style?: React.CSSProperties;
  className?: string;
  icon?: React.ReactNode;
}> = ({
  children,
  variant = 'secondary',
  size = 'md',
  onClick,
  disabled = false,
  style,
  className = '',
  icon,
}) => {
  const baseClass = `btn btn-${variant} ${className}`;
  const pad = size === 'sm' ? '6px 10px' : size === 'lg' ? '10px 18px' : '8px 14px';
  const fz = size === 'sm' ? '12px' : size === 'lg' ? '14px' : '13px';

  return (
    <button
      className={baseClass}
      onClick={onClick}
      disabled={disabled}
      style={{ padding: pad, fontSize: fz, ...style }}
    >
      {icon && <span style={{ display: 'inline-flex', alignItems: 'center' }}>{icon}</span>}
      {children}
    </button>
  );
};

/* ─── Card ─── */
export const Card: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}> = ({ children, style, className = '' }) => (
  <div
    className={`card ${className}`}
    style={{
      backgroundColor: 'var(--card)',
      border: '1px solid var(--bd)',
      borderRadius: '8px',
      padding: '18px',
      ...style,
    }}
  >
    {children}
  </div>
);

/* ─── DatasetChip ─── */
export const DatasetChip: React.FC<{
  label?: string;
  version?: string;
}> = ({ label = '5,000 Survey Records', version = 'SQLite v1.1.0' }) => (
  <div
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      padding: '4px 10px',
      borderRadius: '16px',
      backgroundColor: 'var(--soft)',
      color: 'var(--acd)',
      fontSize: '11.5px',
      fontWeight: 600,
      border: '1px solid #c9dec9',
    }}
  >
    <CheckCircle size={13} />
    <span>{label}</span>
    <span style={{ color: 'var(--mu)', fontWeight: 400 }}>· {version}</span>
  </div>
);

/* ─── PageHeader ─── */
export const PageHeader: React.FC<{
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
}> = ({ title, subtitle, badge, actions }) => (
  <div
    style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: '20px',
      gap: '16px',
      flexWrap: 'wrap',
    }}
  >
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: 'var(--tx)', letterSpacing: '-0.3px' }}>
          {title}
        </h1>
        {badge}
      </div>
      {subtitle && <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--mu)' }}>{subtitle}</p>}
    </div>
    {actions && <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>{actions}</div>}
  </div>
);

/* ─── KPI Card ─── */
export const KpiCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: string;
}> = ({ title, value, subtitle, icon, trend }) => (
  <div className="metric-card-item">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span className="metric-card-title">{title}</span>
      {icon && <span style={{ color: 'var(--acd)' }}>{icon}</span>}
    </div>
    <div className="metric-card-value">{value}</div>
    {(subtitle || trend) && (
      <div style={{ fontSize: '11px', color: 'var(--mu)', display: 'flex', gap: '6px' }}>
        {trend && <span style={{ color: 'var(--acd)', fontWeight: 600 }}>{trend}</span>}
        {subtitle && <span>{subtitle}</span>}
      </div>
    )}
  </div>
);

/* ─── Chart Card ─── */
export const ChartCard: React.FC<{
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
  style?: React.CSSProperties;
  loading?: boolean;
}> = ({ title, subtitle, children, action, style, loading }) => (
  <div className="chart-card-standalone" style={style}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div>
        <h4 className="chart-header-title">{title}</h4>
        {subtitle && <p style={{ margin: '2px 0 0', fontSize: '11.5px', color: 'var(--mu)' }}>{subtitle}</p>}
      </div>
      {action}
    </div>
    <div style={{ width: '100%', minHeight: '160px' }}>
      {loading ? <Skeleton height="200px" /> : children}
    </div>
  </div>
);

/* ─── Warning Banner ─── */
export const WarningBanner: React.FC<{
  message: string;
  title?: string;
}> = ({ message, title = 'Educational Notice' }) => (
  <div
    style={{
      backgroundColor: 'var(--warn)',
      border: '1px solid #ebd8a0',
      borderRadius: '6px',
      padding: '10px 14px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '10px',
      color: 'var(--warn-tx)',
      fontSize: '12.5px',
      lineHeight: 1.5,
    }}
  >
    <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
    <div>
      <strong style={{ display: 'block', marginBottom: '2px' }}>{title}</strong>
      {message}
    </div>
  </div>
);

/* ─── MetricCards (Grid) ─── */
export const MetricCards: React.FC<{
  metrics: Record<string, string | number>;
}> = ({ metrics }) => (
  <div className="metric-grid">
    {Object.entries(metrics).map(([key, val]) => (
      <div key={key} className="metric-card-item">
        <span className="metric-card-title">{key}</span>
        <span className="metric-card-value">{val}</span>
      </div>
    ))}
  </div>
);

/* ─── ObservationList ─── */
export const ObservationList: React.FC<{
  observations: string[];
}> = ({ observations }) => (
  <ul className="observation-list">
    {observations.map((obs, idx) => (
      <li key={idx} className="observation-item">
        <ChevronRight size={16} color="var(--acd)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <span>{obs}</span>
      </li>
    ))}
  </ul>
);

/* ─── DataTable ─── */
export const DataTable: React.FC<{
  columns: string[];
  rows: (string | number | null | undefined)[][];
  maxHeight?: string;
}> = ({ columns, rows, maxHeight = '400px' }) => {
  if (!rows || rows.length === 0) {
    return <EmptyState message="No table records available." />;
  }

  return (
    <div
      style={{
        width: '100%',
        maxHeight,
        overflowY: 'auto',
        border: '1px solid var(--bd)',
        borderRadius: '6px',
        backgroundColor: '#fff',
      }}
    >
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12.5px' }}>
        <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--card)', zIndex: 1 }}>
          <tr style={{ borderBottom: '1px solid var(--bd)' }}>
            {columns.map((col, idx) => (
              <th
                key={idx}
                style={{
                  padding: '10px 14px',
                  fontWeight: 600,
                  color: 'var(--tx)',
                  whiteSpace: 'nowrap',
                  fontSize: '11.5px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rIdx) => (
            <tr
              key={rIdx}
              style={{
                borderBottom: '1px solid var(--bd)',
                backgroundColor: rIdx % 2 === 0 ? '#fff' : '#fcfaf6',
              }}
            >
              {row.map((cell, cIdx) => (
                <td
                  key={cIdx}
                  style={{
                    padding: '8px 14px',
                    color: 'var(--tx)',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {cell !== null && cell !== undefined ? String(cell) : '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/* ─── Tabs ─── */
export const Tabs: React.FC<{
  tabs: { id: string; label: string; icon?: React.ReactNode }[];
  activeTab: string;
  onChange: (id: string) => void;
}> = ({ tabs, activeTab, onChange }) => (
  <div className="tab-bar">
    {tabs.map((tab) => {
      const isActive = activeTab === tab.id;
      return (
        <button
          key={tab.id}
          className={`tab-btn ${isActive ? 'active' : ''}`}
          onClick={() => onChange(tab.id)}
        >
          {tab.icon && <span>{tab.icon}</span>}
          <span>{tab.label}</span>
        </button>
      );
    })}
  </div>
);

/* ─── Form Select ─── */
export const Select: React.FC<{
  label: string;
  value: string;
  options: string[];
  onChange: (val: string) => void;
}> = ({ label, value, options, onChange }) => (
  <div className="form-group">
    <label className="form-label">{label}</label>
    <select className="form-select" value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  </div>
);

/* ─── Range Field ─── */
export const RangeField: React.FC<{
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (val: number) => void;
}> = ({ label, value, min, max, step = 1, onChange }) => (
  <div className="form-group">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <label className="form-label">{label}</label>
      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--acd)' }}>{value}</span>
    </div>
    <input
      type="range"
      className="form-range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
    />
  </div>
);

/* ─── RunButton ─── */
export const RunButton: React.FC<{
  onClick: () => void;
  loading?: boolean;
  label?: string;
}> = ({ onClick, loading = false, label = 'Run Experiment' }) => (
  <button
    className="btn btn-primary"
    onClick={onClick}
    disabled={loading}
    style={{ width: '100%', padding: '10px 16px' }}
  >
    {loading ? (
      <>
        <span className="spinner" style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%' }} />
        <span>Executing...</span>
      </>
    ) : (
      <>
        <Play size={14} fill="currentColor" />
        <span>{label}</span>
      </>
    )}
  </button>
);

/* ─── Modal ─── */
export const Modal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: 'var(--tx)' }}>{title}</h3>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--mu)', padding: '4px' }}
          >
            <X size={18} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
};

/* ─── Empty State ─── */
export const EmptyState: React.FC<{
  message?: string;
  description?: string;
}> = ({ message = 'No data available', description }) => (
  <div
    style={{
      padding: '40px 20px',
      textAlign: 'center',
      color: 'var(--mu)',
      backgroundColor: 'var(--card)',
      borderRadius: '8px',
      border: '1px dashed var(--bd)',
    }}
  >
    <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--tx)', marginBottom: '4px' }}>{message}</div>
    {description && <div style={{ fontSize: '12px' }}>{description}</div>}
  </div>
);

/* ─── Skeleton ─── */
export const Skeleton: React.FC<{
  height?: string;
  width?: string;
  style?: React.CSSProperties;
}> = ({ height = '20px', width = '100%', style }) => (
  <div
    style={{
      height,
      width,
      backgroundColor: 'var(--bd)',
      borderRadius: '4px',
      animation: 'skeleton-pulse 1.5s infinite ease-in-out',
      ...style,
    }}
  />
);

/* ─── Error Toast ─── */
export const ErrorToast: React.FC<{
  message: string;
  onRetry?: () => void;
  onClose?: () => void;
}> = ({ message, onRetry, onClose }) => (
  <div
    style={{
      backgroundColor: '#fbeae5',
      color: 'var(--err)',
      border: '1px solid #ebd0c8',
      borderRadius: '6px',
      padding: '12px 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: '13px',
      gap: '12px',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <AlertTriangle size={16} />
      <span>{message}</span>
    </div>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            background: 'none',
            border: '1px solid var(--err)',
            color: 'var(--err)',
            borderRadius: '4px',
            padding: '4px 8px',
            fontSize: '11px',
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          Retry
        </button>
      )}
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--err)',
            cursor: 'pointer',
            padding: '2px',
          }}
        >
          <X size={14} />
        </button>
      )}
    </div>
  </div>
);
