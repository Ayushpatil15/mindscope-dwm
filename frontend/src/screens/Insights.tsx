import React from 'react';
import { useApi } from '../hooks/useApi';
import { Button, Card, ErrorToast, PageHeader } from '../components/ui';
import { AlertCircle, CheckCircle2, Lightbulb, RefreshCw, Sparkles, TrendingUp } from 'lucide-react';

interface InsightItem {
  title: string;
  sentence: string;
  metric: string;
  tone: 'positive' | 'attention' | 'neutral';
}

interface InsightsData {
  insights: InsightItem[];
  recommendations: string[];
}

export const InsightsScreen: React.FC = () => {
  const { data, loading, error, refetch } = useApi<InsightsData>('/api/insights');

  const icons = {
    positive: TrendingUp,
    attention: AlertCircle,
    neutral: Sparkles,
  };

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onRetry={refetch} />}

      <PageHeader
        title="Student Population Insights"
        subtitle="Empirical patterns and actionable student counseling recommendations synthesized from live dimensional warehouse measures."
        actions={
          <Button variant="secondary" onClick={refetch}>
            <RefreshCw size={15} style={{ marginRight: 6 }} />
            Recompute signals
          </Button>
        }
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.8fr) minmax(0, 1.2fr)', gap: '24px' }}>
        {/* Insight Signal Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {(data?.insights || []).map((insight, idx) => {
            const Icon = icons[insight.tone] || Sparkles;
            const iconBg = insight.tone === 'positive' ? '#e2f0d9' : insight.tone === 'attention' ? '#fde2e2' : 'var(--soft)';
            const iconCol = insight.tone === 'positive' ? 'var(--acd)' : insight.tone === 'attention' ? '#c0392b' : 'var(--tx)';

            return (
              <Card key={idx} style={{ padding: '18px 20px', display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '8px',
                    backgroundColor: iconBg,
                    color: iconCol,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Icon size={20} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 700, color: 'var(--tx)' }}>{insight.title}</h3>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '3px 8px',
                        borderRadius: '12px',
                        backgroundColor: 'var(--soft)',
                        color: 'var(--acd)',
                        fontWeight: 600,
                      }}
                    >
                      {insight.metric}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: '13px', color: 'var(--tx)', lineHeight: 1.5 }}>{insight.sentence}</p>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Prioritized Actionable Recommendations */}
        <Card style={{ padding: '22px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '8px',
                backgroundColor: 'var(--soft)',
                color: 'var(--acd)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Lightbulb size={18} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 700, color: 'var(--tx)' }}>Recommendations</h3>
              <p style={{ margin: 0, fontSize: '11px', color: 'var(--mu)' }}>Evidence-based university counseling actions</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {(data?.recommendations || []).map((rec, idx) => (
              <label
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px',
                  fontSize: '13px',
                  color: 'var(--tx)',
                  lineHeight: 1.5,
                  cursor: 'pointer',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  border: '1px solid #f0ebe1',
                  backgroundColor: '#faf8f5',
                }}
              >
                <input type="checkbox" defaultChecked={idx < 2} style={{ marginTop: '3px' }} />
                <span>{rec}</span>
              </label>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default InsightsScreen;
