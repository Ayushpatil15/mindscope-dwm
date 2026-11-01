import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { Card, ChartCard, ErrorToast, MetricCards, PageHeader, RangeField } from '../components/ui';
import { AnalyticsChart, ScatterPlot } from '../components/charts';
import { Users } from 'lucide-react';

export const SegmentationScreen: React.FC = () => {
  const [k, setK] = useState<number>(4);
  const { data, loading, error, refetch } = useApi<any>(`/api/analytics/clusters?k=${k}`, [k]);

  const clusterProfiles = data?.clusters || data?.profiles || [];
  const inertia = data?.inertia || 0;
  const silhouette = data?.silhouette || 0;

  const elbow = (data?.elbow || []).map((e: any) => ({
    name: `K=${e.k}`,
    value: Math.round(e.inertia),
  }));

  const rawPts = data?.points || [];
  const pts = rawPts.map((p: any) => {
    if (Array.isArray(p)) {
      return { x: p[0], y: p[1], cluster: p[2] };
    }
    return p;
  });

  const personaNames = ['At-Risk Digital Habit', 'Balanced Achievers', 'Academic Focused', 'Moderate Social', 'Night Owls', 'Casual Browsers'];

  const metrics = {
    'Clusters (K)': k,
    'WCSS Inertia': inertia.toFixed(1),
    'Silhouette Coefficient': silhouette.toFixed(4),
    'Clustered Instances': '5,000 respondents',
    'Algorithm': 'K-Means (Lloyd Euclidean)',
  };

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onRetry={refetch} />}

      <PageHeader
        title="Student Behavioral Segmentation"
        subtitle="Discover distinct student lifestyle and wellbeing cohorts using unsupervised K-Means clustering and PCA projection."
      />

      <Card style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Users size={18} color="var(--acd)" />
          <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--tx)' }}>Clustering Controls</span>
        </div>

        <RangeField
          label="Clusters (K)"
          value={k}
          min={2}
          max={8}
          step={1}
          onChange={setK}
        />
      </Card>

      <MetricCards metrics={metrics} />

      {/* Visualizers Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <ChartCard
          title="Elbow Method (Inertia vs K)"
          subtitle="Within-cluster sum of squares across cluster count evaluations"
          loading={loading}
        >
          <AnalyticsChart type="bar" data={elbow} />
        </ChartCard>

        <ChartCard
          title="Student Clusters (2D PCA Projection)"
          subtitle="Normalized principal component projection colored by cluster assignment"
          loading={loading}
        >
          <ScatterPlot points={pts} />
        </ChartCard>
      </div>

      {/* Profile Cards */}
      <ChartCard
        title={`Identified Behavioral Archetypes (k=${k})`}
        subtitle="Cluster centroids across digital screen hours, sleep habits, and self-reported mental wellbeing"
        loading={loading}
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
          {clusterProfiles.map((c: any, idx: number) => (
            <div
              key={idx}
              style={{
                border: '1px solid var(--bd)',
                borderRadius: '8px',
                padding: '16px',
                backgroundColor: '#fff',
              }}
            >
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--acd)', marginBottom: '8px' }}>
                Cluster {idx}: {personaNames[idx % personaNames.length]}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tx)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f0ebe1', paddingBottom: '3px' }}>
                  <span style={{ color: 'var(--mu)' }}>Population Share:</span>
                  <span style={{ fontWeight: 600 }}>{c.size} students ({((c.size / 5000) * 100).toFixed(1)}%)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f0ebe1', paddingBottom: '3px' }}>
                  <span style={{ color: 'var(--mu)' }}>Screen Usage:</span>
                  <span style={{ fontWeight: 600 }}>{c.Avg_Daily_Usage_Hours} hrs/day</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f0ebe1', paddingBottom: '3px' }}>
                  <span style={{ color: 'var(--mu)' }}>Sleep Duration:</span>
                  <span style={{ fontWeight: 600 }}>{c.Sleep_Hours_Per_Night} hrs/night</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f0ebe1', paddingBottom: '3px' }}>
                  <span style={{ color: 'var(--mu)' }}>Mental Health:</span>
                  <span style={{ fontWeight: 600 }}>{c.Mental_Health_Score} / 10</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--mu)' }}>Dominant Stress:</span>
                  <span style={{ fontWeight: 600 }}>{c.top_stress}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ChartCard>
    </div>
  );
};

export default SegmentationScreen;
