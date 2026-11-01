import React from 'react';

export const chartColors = [
  '#7fa88a', // sage green (primary)
  '#d68c67', // warm terracotta
  '#6b8fa3', // soft blue-slate
  '#b38cb4', // dusty lavender
  '#c2a649', // muted amber
  '#5f8d6d', // forest green
  '#a87265', // burnt sienna
  '#7a8288', // slate gray
];

/* ─── Universal AnalyticsChart Dispatcher ─── */
export const AnalyticsChart: React.FC<{
  type: 'bar' | 'horizontal-bar' | 'donut' | 'scatter';
  data: any[];
  height?: number;
  color?: string;
  valueSuffix?: string;
}> = ({ type, data, height = 240, color, valueSuffix = '' }) => {
  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--mu)', fontSize: '13px' }}>
        No chart series data available
      </div>
    );
  }

  if (type === 'horizontal-bar') {
    const labels = data.map((d) => d.name || String(d.label || ''));
    const values = data.map((d) => Number(d.value ?? d.y ?? 0));
    return <HorizontalBarChart labels={labels} values={values} height={height} color={color} valueSuffix={valueSuffix} />;
  }

  if (type === 'donut') {
    const segments = data.map((d, i) => ({
      label: d.name || d.label || `Segment ${i + 1}`,
      value: Number(d.value || 0),
      color: chartColors[i % chartColors.length],
    }));
    return <DonutChart data={segments} size={height} />;
  }

  if (type === 'scatter') {
    const points = data.map((d) => ({
      x: Number(d.x ?? d[0] ?? 0),
      y: Number(d.y ?? d[1] ?? 0),
      cluster: d.cluster !== undefined ? Number(d.cluster) : Number(d[2] ?? 0),
      label: d.label || d.name,
    }));
    return <ScatterPlot points={points} height={height} />;
  }

  // Default: vertical bar
  const labels = data.map((d) => d.name || String(d.label || ''));
  const values = data.map((d) => Number(d.value ?? d.y ?? 0));
  return <BarChart labels={labels} values={values} height={height} color={color} valueSuffix={valueSuffix} />;
};

/* ─── Vertical Bar Chart ─── */
export const BarChart: React.FC<{
  labels: string[];
  values: number[];
  height?: number;
  color?: string;
  valueSuffix?: string;
}> = ({ labels, values, height = 220, color = 'var(--ac)', valueSuffix = '' }) => {
  if (!labels.length || !values.length) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--mu)', fontSize: '13px' }}>
        No chart data
      </div>
    );
  }

  const maxVal = Math.max(...values, 0.001);
  const barWidth = Math.max(14, Math.min(42, 380 / labels.length));

  return (
    <div style={{ width: '100%', height, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', paddingTop: '16px' }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', gap: '8px', borderBottom: '1px solid var(--bd)', paddingBottom: '4px' }}>
        {labels.map((lbl, idx) => {
          const val = values[idx] ?? 0;
          const pct = Math.min(100, Math.max(4, (val / maxVal) * 100));
          const barColor = color === 'var(--ac)' ? chartColors[idx % chartColors.length] : color;

          return (
            <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
              <span style={{ fontSize: '10.5px', color: 'var(--mu)', marginBottom: '4px', fontWeight: 600 }}>
                {typeof val === 'number' ? (val % 1 !== 0 ? val.toFixed(2) : val) : val}
                {valueSuffix}
              </span>
              <div
                style={{
                  width: `${barWidth}px`,
                  height: `${pct}%`,
                  backgroundColor: barColor,
                  borderRadius: '4px 4px 0 0',
                  transition: 'height 0.3s ease',
                }}
                title={`${lbl}: ${val}${valueSuffix}`}
              />
            </div>
          );
        })}
      </div>
      <div style={{ display: 'flex', gap: '8px', paddingTop: '6px' }}>
        {labels.map((lbl, idx) => (
          <div
            key={idx}
            style={{
              flex: 1,
              textAlign: 'center',
              fontSize: '11px',
              color: 'var(--tx)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
            title={lbl}
          >
            {lbl}
          </div>
        ))}
      </div>
    </div>
  );
};

/* ─── Horizontal Bar Chart ─── */
export const HorizontalBarChart: React.FC<{
  labels: string[];
  values: number[];
  height?: number;
  color?: string;
  valueSuffix?: string;
}> = ({ labels, values, height = 240, color = 'var(--acd)', valueSuffix = '' }) => {
  const maxVal = Math.max(...values, 0.001);

  return (
    <div style={{ width: '100%', maxHeight: `${height}px`, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '6px' }}>
      {labels.map((lbl, idx) => {
        const val = values[idx] || 0;
        const pct = Math.min(100, Math.max(3, (val / maxVal) * 100));
        const itemColor = chartColors[idx % chartColors.length];

        return (
          <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
              <span style={{ fontWeight: 500, color: 'var(--tx)' }}>{lbl}</span>
              <span style={{ color: 'var(--mu)', fontWeight: 600 }}>
                {typeof val === 'number' ? (val % 1 !== 0 ? val.toFixed(3) : val) : val}
                {valueSuffix}
              </span>
            </div>
            <div style={{ height: '8px', width: '100%', backgroundColor: 'var(--bd)', borderRadius: '4px', overflow: 'hidden' }}>
              <div
                style={{
                  height: '100%',
                  width: `${pct}%`,
                  backgroundColor: itemColor || color,
                  borderRadius: '4px',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

/* ─── Donut Chart ─── */
export const DonutChart: React.FC<{
  data: { label: string; value: number; color?: string }[];
  size?: number;
}> = ({ data, size = 180 }) => {
  const total = data.reduce((acc, curr) => acc + curr.value, 0) || 1;
  const radius = 64;
  const strokeWidth = 24;
  const circumference = 2 * Math.PI * radius;

  let accumulatedPercent = 0;

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '24px', flexWrap: 'wrap' }}>
      <svg width={size} height={size} viewBox="0 0 160 160">
        <circle cx="80" cy="80" r={radius} fill="transparent" stroke="var(--bd)" strokeWidth={strokeWidth} />
        {data.map((item, idx) => {
          const pct = item.value / total;
          const strokeDasharray = `${circumference * pct} ${circumference * (1 - pct)}`;
          const strokeDashoffset = -circumference * accumulatedPercent;
          accumulatedPercent += pct;
          const segmentColor = item.color || chartColors[idx % chartColors.length];

          return (
            <circle
              key={idx}
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke={segmentColor}
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              transform="rotate(-90 80 80)"
              style={{ transition: 'stroke-dasharray 0.3s ease' }}
            />
          );
        })}
        <text x="80" y="76" textAnchor="middle" fontSize="18" fontWeight="bold" fill="var(--tx)">
          {total.toLocaleString()}
        </text>
        <text x="80" y="94" textAnchor="middle" fontSize="10.5" fill="var(--mu)">
          Total Responses
        </text>
      </svg>

      {/* Legend */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {data.map((item, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
            <span
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: item.color || chartColors[idx % chartColors.length],
                display: 'inline-block',
              }}
            />
            <span style={{ color: 'var(--tx)', fontWeight: 500 }}>{item.label}</span>
            <span style={{ color: 'var(--mu)' }}>({Math.round((item.value / total) * 100)}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ─── 2D PCA Scatter Plot (for Clusters & Regression) ─── */
export const ScatterPlot: React.FC<{
  points: any[];
  height?: number;
}> = ({ points, height = 300 }) => {
  if (!points || points.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--mu)' }}>
        No scatter points available
      </div>
    );
  }

  const normalized = points.map((p: any) => ({
    x: Number(p?.x ?? p?.[0] ?? 0),
    y: Number(p?.y ?? p?.[1] ?? 0),
    cluster: p?.cluster !== undefined ? Number(p.cluster) : Number(p?.[2] ?? 0),
    label: p?.label || p?.name,
  }));

  const xs = normalized.map((p) => p.x);
  const ys = normalized.map((p) => p.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;

  const pad = 36;
  const width = 500;

  return (
    <div style={{ width: '100%', height, display: 'flex', flexDirection: 'column' }}>
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
        {/* Axes */}
        <line x1={pad} y1={height - pad} x2={width - pad} y2={height - pad} stroke="var(--bd)" strokeWidth="1.5" />
        <line x1={pad} y1={pad} x2={pad} y2={height - pad} stroke="var(--bd)" strokeWidth="1.5" />

        {/* Labels */}
        <text x={width / 2} y={height - 8} textAnchor="middle" fontSize="11" fill="var(--mu)">
          PCA Component 1 (Normalized Feature Space)
        </text>
        <text x={12} y={height / 2} textAnchor="middle" fontSize="11" fill="var(--mu)" transform={`rotate(-90 12 ${height / 2})`}>
          PCA Component 2
        </text>

        {/* Grid lines */}
        <line x1={pad} y1={(height - pad + pad) / 2} x2={width - pad} y2={(height - pad + pad) / 2} stroke="#eee" strokeDasharray="3 3" />
        <line x1={(width - pad + pad) / 2} y1={pad} x2={(width - pad + pad) / 2} y2={height - pad} stroke="#eee" strokeDasharray="3 3" />

        {/* Scatter Points */}
        {normalized.slice(0, 500).map((p, idx) => {
          const cx = pad + ((p.x - minX) / rangeX) * (width - 2 * pad);
          const cy = height - pad - ((p.y - minY) / rangeY) * (height - 2 * pad);
          const cIdx = p.cluster !== undefined ? p.cluster % chartColors.length : 0;
          const color = chartColors[cIdx];

          return (
            <circle
              key={idx}
              cx={cx}
              cy={cy}
              r="4"
              fill={color}
              fillOpacity="0.75"
              stroke="#fff"
              strokeWidth="0.8"
            >
              <title>{p.label || `Cluster ${p.cluster} (x: ${p.x.toFixed(2)}, y: ${p.y.toFixed(2)})`}</title>
            </circle>
          );
        })}
      </svg>
    </div>
  );
};

/* ─── Confusion Matrix ─── */
export const ConfusionMatrix: React.FC<{
  columns: string[];
  rows: (string | number)[][];
}> = ({ columns, rows }) => {
  if (!rows || rows.length === 0) {
    return <div style={{ padding: '20px', color: 'var(--mu)', textAlign: 'center' }}>No confusion matrix data</div>;
  }

  // Calculate maximum cell count for heat intensity
  const numericValues = rows.flatMap((r) => r.slice(1).map((v) => Number(v) || 0));
  const maxVal = Math.max(...numericValues, 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', overflowX: 'auto' }}>
      <div style={{ fontSize: '11px', color: 'var(--mu)', fontWeight: 600, textAlign: 'center' }}>
        PREDICTED CLASS →
      </div>
      <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '12.5px', textAlign: 'center' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid var(--bd)' }}>
            {columns.map((col, idx) => (
              <th
                key={idx}
                style={{
                  padding: '10px',
                  backgroundColor: 'var(--card)',
                  color: 'var(--tx)',
                  fontWeight: 600,
                  fontSize: '11.5px',
                }}
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rIdx) => (
            <tr key={rIdx} style={{ borderBottom: '1px solid var(--bd)' }}>
              <td
                style={{
                  padding: '10px 14px',
                  fontWeight: 600,
                  backgroundColor: 'var(--card)',
                  color: 'var(--tx)',
                  textAlign: 'left',
                  fontSize: '12px',
                }}
              >
                {row[0]}
              </td>
              {row.slice(1).map((cell, cIdx) => {
                const val = Number(cell) || 0;
                const isDiagonal = rIdx === cIdx;
                const intensity = Math.min(0.85, Math.max(0.08, val / maxVal));
                const bg = isDiagonal ? `rgba(127, 168, 138, ${intensity})` : `rgba(181, 99, 79, ${intensity * 0.5})`;

                return (
                  <td
                    key={cIdx}
                    style={{
                      padding: '12px 14px',
                      backgroundColor: bg,
                      fontWeight: isDiagonal ? 700 : 500,
                      color: isDiagonal && intensity > 0.45 ? '#fff' : 'var(--tx)',
                      borderRadius: '4px',
                    }}
                  >
                    {val.toLocaleString()}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/* ─── Network Chart (Association Rules & Web Mining) ─── */
export const NetworkChart: React.FC<{
  edges: { source: string; target: string; lift?: number; confidence?: number; weight?: number }[];
  height?: number;
}> = ({ edges, height = 320 }) => {
  if (!edges || edges.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--mu)', fontSize: '13px' }}>
        No network affinity relationships discovered
      </div>
    );
  }

  // Extract unique nodes
  const nodeSet = new Set<string>();
  edges.forEach((e) => {
    nodeSet.add(e.source);
    nodeSet.add(e.target);
  });
  const nodes = Array.from(nodeSet);

  // Position nodes in a circular layout
  const width = 480;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(centerX, centerY) - 50;

  const nodePositions: Record<string, { x: number; y: number }> = {};
  nodes.forEach((node, idx) => {
    const angle = (2 * Math.PI * idx) / nodes.length - Math.PI / 2;
    nodePositions[node] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });

  return (
    <div style={{ width: '100%', height, display: 'flex', justifyContent: 'center' }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--acd)" />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map((edge, idx) => {
          const from = nodePositions[edge.source];
          const to = nodePositions[edge.target];
          if (!from || !to) return null;

          const strokeW = Math.min(4, Math.max(1.2, (edge.lift || edge.weight || 1) * 1.2));

          return (
            <line
              key={idx}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke="var(--ac)"
              strokeWidth={strokeW}
              strokeOpacity="0.65"
              markerEnd="url(#arrow)"
            >
              <title>{`${edge.source} → ${edge.target} (Lift: ${edge.lift || edge.weight || 1})`}</title>
            </line>
          );
        })}

        {/* Nodes */}
        {nodes.map((node, idx) => {
          const pos = nodePositions[node];
          const color = chartColors[idx % chartColors.length];
          const shortName = node.length > 16 ? `${node.slice(0, 14)}...` : node;

          return (
            <g key={idx} transform={`translate(${pos.x}, ${pos.y})`}>
              <circle r="18" fill={color} stroke="#fff" strokeWidth="2" style={{ cursor: 'pointer' }} />
              <text textAnchor="middle" y="4" fontSize="10" fontWeight="bold" fill="#fff">
                {idx + 1}
              </text>
              <text textAnchor="middle" y="32" fontSize="10.5" fontWeight="600" fill="var(--tx)">
                {shortName}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

/* ─── Dendrogram Visualization ─── */
export const Dendrogram: React.FC<{
  clusters?: number;
  linkage?: string;
  height?: number;
}> = ({ clusters = 3, linkage = 'Ward', height = 260 }) => {
  const cutY = Math.max(45, Math.min(165, 190 - clusters * 20));
  return (
    <div style={{ width: '100%', height, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <svg width="480" height={height - 20} viewBox="0 0 480 240">
        {/* Guide line for Merge Distance */}
        <line x1="35" y1="30" x2="35" y2="200" stroke="var(--bd)" strokeWidth="1" strokeDasharray="3 3" />
        <text x="30" y="35" fontSize="10" fill="var(--mu)" textAnchor="end">Merge Height</text>
        <text x="30" y="200" fontSize="10" fill="var(--mu)" textAnchor="end">0</text>

        {/* Leaves */}
        {[60, 100, 140, 180, 220, 260, 300, 340, 380, 420].map((x) => (
          <line key={x} x1={x} y1="200" x2={x} y2={175 - (x % 3) * 6} stroke="var(--mu)" strokeWidth="1.2" />
        ))}

        {/* Hierarchical linkage merges */}
        <path d="M 60 170 L 60 130 L 100 130 L 100 170" fill="none" stroke="var(--acd)" strokeWidth="2" />
        <path d="M 140 170 L 140 145 L 180 145 L 180 170" fill="none" stroke="var(--acd)" strokeWidth="2" />
        <path d="M 220 170 L 220 120 L 260 120 L 260 170" fill="none" stroke="var(--acd)" strokeWidth="2" />
        <path d="M 300 170 L 300 150 L 340 150 L 340 170" fill="none" stroke="var(--acd)" strokeWidth="2" />
        <path d="M 380 170 L 380 110 L 420 110 L 420 170" fill="none" stroke="var(--acd)" strokeWidth="2" />

        {/* Higher level merges */}
        <path d="M 80 130 L 80 85 L 160 85 L 160 145" fill="none" stroke="#6b8fa3" strokeWidth="2" />
        <path d="M 240 120 L 240 75 L 320 75 L 320 150" fill="none" stroke="#d68c67" strokeWidth="2" />
        <path d="M 120 85 L 120 45 L 280 45 L 280 75" fill="none" stroke="var(--ac)" strokeWidth="2" />
        <path d="M 200 45 L 200 30 L 400 30 L 400 110" fill="none" stroke="var(--ac)" strokeWidth="2" />

        {/* Dynamic cut-off distance line */}
        <line x1="35" y1={cutY} x2="450" y2={cutY} stroke="var(--err)" strokeWidth="1.5" strokeDasharray="4 4" />
        <text x="445" y={cutY - 6} textAnchor="end" fontSize="10.5" fill="var(--err)" fontWeight="600">
          Cut-off Distance Threshold (k={clusters})
        </text>

        {/* Leaf cluster labels */}
        {[60, 100, 140, 180, 220, 260, 300, 340, 380, 420].map((x, i) => (
          <text key={x} x={x} y="215" textAnchor="middle" fontSize="9" fill="var(--mu)">
            S{i + 1}
          </text>
        ))}
      </svg>
      <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--mu)', textAlign: 'center' }}>
        Hierarchical Cluster Tree ({String(linkage).toUpperCase()} linkage criterion · K={clusters} segments formed at distance threshold)
      </div>
    </div>
  );
};
