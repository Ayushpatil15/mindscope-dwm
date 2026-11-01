import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { Card, ChartCard, DataTable, ErrorToast, MetricCards, PageHeader, RangeField } from '../components/ui';
import { NetworkChart } from '../components/charts';
import { GitFork } from 'lucide-react';

export const MarketBasketScreen: React.FC = () => {
  const [minSupport, setMinSupport] = useState<number>(0.08);
  const [minConfidence, setMinConfidence] = useState<number>(0.5);

  const endpoint = `/api/analytics/associations?min_support=${minSupport}&min_confidence=${minConfidence}&top=25`;
  const { data, loading, error, refetch } = useApi<any>(endpoint, [minSupport, minConfidence]);

  const rules = data?.rules || [];
  const columns = ['Rule #', 'Antecedent (IF)', 'Consequent (THEN)', 'Support', 'Confidence', 'Lift'];
  const rows = rules.map((r: any, idx: number) => [
    `#${idx + 1}`,
    r.antecedent_str || r.if || (Array.isArray(r.antecedents) ? r.antecedents.join(', ') : String(r.antecedents)),
    r.consequent_str || r.then || (Array.isArray(r.consequents) ? r.consequents.join(', ') : String(r.consequents)),
    typeof r.support === 'number' ? r.support.toFixed(3) : r.support,
    typeof r.confidence === 'number' ? `${(r.confidence * 100).toFixed(1)}%` : r.confidence,
    typeof r.lift === 'number' ? r.lift.toFixed(3) : r.lift,
  ]);

  const edges = rules.slice(0, 15).map((r: any) => ({
    source: r.antecedent_str || r.if || 'Antecedent',
    target: r.consequent_str || r.then || 'Consequent',
    lift: typeof r.lift === 'number' ? r.lift : 1.0,
    confidence: typeof r.confidence === 'number' ? r.confidence : 0.5,
  }));

  const maxLift = rules.length > 0 ? Math.max(...rules.map((r: any) => r.lift || 1.0)) : 1.0;

  const metrics = {
    'Total Transactions': data?.n_transactions || 5000,
    'Frequent Itemsets Mined': data?.n_itemsets || 0,
    'Valid Rules Mined': rules.length,
    'Minimum Support': minSupport,
    'Minimum Confidence': minConfidence,
    'Peak Rule Lift': maxLift.toFixed(2),
  };

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onRetry={refetch} />}

      <PageHeader
        title="Behavioral Association Mining"
        subtitle="Discover co-occurring student lifestyle and mental health associations using Apriori downward closure."
      />

      <Card style={{ padding: '16px 20px', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitFork size={18} color="var(--acd)" />
          <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--tx)' }}>Apriori Parameters</span>
        </div>

        <RangeField
          label="Minimum Support"
          value={minSupport}
          min={0.02}
          max={0.25}
          step={0.01}
          onChange={setMinSupport}
        />

        <RangeField
          label="Minimum Confidence"
          value={minConfidence}
          min={0.2}
          max={0.9}
          step={0.05}
          onChange={setMinConfidence}
        />
      </Card>

      <MetricCards metrics={metrics} />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: '20px' }}>
        <ChartCard
          title="Discovered Association Rules"
          subtitle={`Ranked by lift metric (${rows.length} valid rules mined)`}
          loading={loading}
        >
          <DataTable columns={columns} rows={rows} maxHeight="420px" />
        </ChartCard>

        <ChartCard
          title="Behavioral Affinity Network"
          subtitle="Nodes represent lifestyle attributes; edge thickness scaled by lift factor"
        >
          <NetworkChart edges={edges} />
        </ChartCard>
      </div>
    </div>
  );
};

export default MarketBasketScreen;
