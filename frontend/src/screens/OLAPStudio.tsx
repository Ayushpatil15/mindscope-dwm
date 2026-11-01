import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { ChartCard, DataTable, ErrorToast } from '../components/ui';
import { BarChart } from '../components/charts';
import { Layers, Terminal } from 'lucide-react';

const OPERATIONS = [
  'Roll-up',
  'Drill-down',
  'Slice',
  'Dice',
  'Pivot',
  'Drill-across',
  'Cube',
  'Grouping-sets',
];

const DIMENSIONS = [
  { value: 'academic_level', label: 'Academic Level' },
  { value: 'platform', label: 'Social Platform' },
  { value: 'stress_level', label: 'Stress Level' },
  { value: 'country', label: 'Country' },
  { value: 'gender', label: 'Gender' },
  { value: 'purpose', label: 'Purpose of Use' },
];

const MEASURES = [
  { value: 'mental_health_score', label: 'Mental Health Score' },
  { value: 'avg_daily_usage_hours', label: 'Daily Usage Hours' },
  { value: 'sleep_hours_per_night', label: 'Sleep Hours' },
  { value: 'study_hours', label: 'Study Hours' },
  { value: 'daily_unlocks', label: 'Daily Phone Unlocks' },
];

export const OLAPStudioScreen: React.FC = () => {
  const [op, setOp] = useState<string>('Roll-up');
  const [x, setX] = useState<string>('academic_level');
  const [y, setY] = useState<string>('platform');
  const [measure, setMeasure] = useState<string>('mental_health_score');
  const [agg, setAgg] = useState<string>('AVG');

  const endpoint = `/api/olap/execute?op=${encodeURIComponent(op)}&x=${x}&y=${y}&measure=${measure}&agg=${agg}`;
  const { data, loading, error, refetch } = useApi<any>(endpoint, [op, x, y, measure, agg]);

  const columns = data?.columns || [];
  const rows = data?.rows || [];
  const chartLabels = data?.chart?.labels || [];
  const chartValues = data?.chart?.series?.[0]?.values || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onRetry={refetch} />}

      {/* Control Toolbar */}
      <div
        className="card"
        style={{
          backgroundColor: 'var(--card)',
          borderRadius: '8px',
          border: '1px solid var(--bd)',
          padding: '16px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '16px',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={18} color="var(--acd)" />
          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--tx)' }}>OLAP Studio:</span>
        </div>

        {/* Operation Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--mu)' }}>Operation:</span>
          <select
            value={op}
            onChange={(e) => setOp(e.target.value)}
            style={selectStyle}
          >
            {OPERATIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>

        {/* Primary Dimension */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--mu)' }}>Dim X:</span>
          <select value={x} onChange={(e) => setX(e.target.value)} style={selectStyle}>
            {DIMENSIONS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        {/* Secondary Dimension */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--mu)' }}>Dim Y:</span>
          <select value={y} onChange={(e) => setY(e.target.value)} style={selectStyle}>
            {DIMENSIONS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        {/* Target Measure */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--mu)' }}>Measure:</span>
          <select value={measure} onChange={(e) => setMeasure(e.target.value)} style={selectStyle}>
            {MEASURES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        {/* Aggregation Function */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--mu)' }}>Agg:</span>
          <select value={agg} onChange={(e) => setAgg(e.target.value)} style={selectStyle}>
            <option value="AVG">AVG</option>
            <option value="COUNT">COUNT</option>
            <option value="SUM">SUM</option>
            <option value="MIN">MIN</option>
            <option value="MAX">MAX</option>
          </select>
        </div>
      </div>

      {/* Generated SQL & Educational Insight */}
      {data && (
        <div
          style={{
            backgroundColor: '#2b2a27',
            color: '#f0ece1',
            borderRadius: '8px',
            padding: '16px',
            fontSize: '12px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
              <Terminal size={14} color="var(--ac)" />
              <span>Generated SQL Query (Executed in {data.execution_time_ms} ms)</span>
            </div>
            <span style={{ fontSize: '11px', color: '#a6c5ad' }}>{data.op}</span>
          </div>
          <pre
            style={{
              margin: 0,
              fontFamily: 'Consolas, Monaco, "Courier New", monospace',
              whiteSpace: 'pre-wrap',
              maxHeight: '140px',
              overflowY: 'auto',
              color: '#d4cebe',
            }}
          >
            {data.generated_sql}
          </pre>
          {data.explanation && (
            <div
              style={{
                marginTop: '10px',
                paddingTop: '8px',
                borderTop: '1px solid #42403b',
                color: '#a6a192',
                fontStyle: 'italic',
              }}
            >
              Theory: {data.explanation}
            </div>
          )}
        </div>
      )}

      {/* Visual Projection Chart */}
      <ChartCard
        title={`${op}: Multidimensional Aggregation Chart`}
        subtitle="Visual projection of the active analytical slice"
        loading={loading}
      >
        <BarChart labels={chartLabels} values={chartValues} color="var(--acd)" />
      </ChartCard>

      {/* Tabular Result Grid */}
      <ChartCard
        title="Multidimensional Cross-Tabulation Grid"
        subtitle={`Returned ${rows.length} records`}
        loading={loading}
      >
        <DataTable columns={columns} rows={rows} maxHeight="360px" />
      </ChartCard>
    </div>
  );
};

const selectStyle: React.CSSProperties = {
  padding: '6px 10px',
  borderRadius: '6px',
  border: '1px solid var(--bd)',
  backgroundColor: '#fff',
  fontSize: '12px',
  color: 'var(--tx)',
};

