import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  RotateCcw,
  Sparkles,
  BarChart3,
  Table as TableIcon,
  Activity,
  FileText,
  Code2,
  Copy,
  Check,
  CheckCircle,
  AlertCircle,
  Layers,
} from 'lucide-react';
import {
  Button,
  Card,
  PageHeader,
  DatasetChip,
  MetricCards,
  ObservationList,
  DataTable,
  Tabs,
  Select,
  RangeField,
  RunButton,
  Modal,
  EmptyState,
  Skeleton,
  ErrorToast,
  WarningBanner,
} from './ui';
import {
  AnalyticsChart,
  ConfusionMatrix,
  NetworkChart,
  ScatterPlot,
  Dendrogram,
} from './charts';
import SchemaDiagram from './SchemaDiagram';
import InteractiveDecisionTree from './InteractiveDecisionTree';

export type Param =
  | { type: 'select'; key: string; label: string; options: string[]; initial: string }
  | { type: 'range'; key: string; label: string; min: number; max: number; step?: number; initial: number }
  | { type: 'number'; key: string; label: string; initial: number };

export interface LabConfig {
  number: number;
  title: string;
  subtitle?: string;
  description?: string;
  dataset: string;
  theory: string;
  params: Param[];
  special?: 'schema' | 'tree' | 'confusion' | 'cluster' | 'dendrogram' | 'network' | 'pipeline';
}

export const LabRunner: React.FC<{
  config: LabConfig;
}> = ({ config }) => {
  // Initialize parameters state
  const initParams = () => {
    const p: Record<string, any> = {};
    config.params.forEach((param) => {
      p[param.key] = param.initial;
    });
    return p;
  };

  const [params, setParams] = useState<Record<string, any>>(initParams);
  const [effectiveParams, setEffectiveParams] = useState<Record<string, any>>(initParams);
  const [activeTab, setActiveTab] = useState<string>('result');
  const [theoryOpen, setTheoryOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Check if current parameters differ from the last executed run
  const isStale = React.useMemo(() => {
    if (!result || !effectiveParams) return false;
    return Object.keys(params).some(
      (k) => String(params[k] ?? '') !== String(effectiveParams[k] ?? '')
    );
  }, [params, effectiveParams, result]);

  // Re-initialize when lab config changes
  useEffect(() => {
    const initial = initParams();
    setParams(initial);
    setEffectiveParams(initial);
    setActiveTab('result');
    runExperiment(initial);
  }, [config.number]);

  const handleParamChange = (key: string, val: any) => {
    setParams((prev) => ({ ...prev, [key]: val }));
  };

  const handleResetParams = () => {
    const initial = initParams();
    setParams(initial);
    setEffectiveParams(initial);
    runExperiment(initial);
  };

  const runExperiment = async (currentParams = params) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/labs/${config.number}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ params: currentParams }),
      });

      if (!res.ok) {
        let msg = `Server error ${res.status}`;
        try {
          const errData = await res.json();
          if (errData?.detail) msg = String(errData.detail);
        } catch {}
        throw new Error(msg);
      }

      const data = await res.json();
      setResult(data);
      setEffectiveParams({ ...currentParams });
    } catch (err: any) {
      setError(err?.message || 'Failed to execute laboratory experiment.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    if (!result?.sql) return;
    navigator.clipboard.writeText(result.sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs = [
    { id: 'result', label: 'Result', icon: <TableIcon size={14} /> },
    { id: 'charts', label: 'Charts', icon: <BarChart3 size={14} /> },
    { id: 'metrics', label: 'Metrics', icon: <Activity size={14} /> },
    { id: 'observation', label: 'Observation', icon: <FileText size={14} /> },
    { id: 'sql', label: 'SQL / Code', icon: <Code2 size={14} /> },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Experiment Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '16px',
          borderBottom: '1px solid var(--bd)',
          paddingBottom: '16px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <span
              style={{
                backgroundColor: 'var(--acd)',
                color: '#fff',
                fontSize: '11px',
                fontWeight: 800,
                padding: '3px 8px',
                borderRadius: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Lab {config.number}
            </span>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: 'var(--tx)', letterSpacing: '-0.2px' }}>
              {config.title}
            </h1>
          </div>
          {config.subtitle && (
            <p style={{ margin: '0 0 6px', fontSize: '13px', color: 'var(--mu)', fontWeight: 500 }}>
              {config.subtitle}
            </p>
          )}
          {config.description && (
            <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--tx)', maxWidth: '850px', lineHeight: 1.5 }}>
              {config.description}
            </p>
          )}
        </div>

        {/* Header Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <DatasetChip label={config.dataset} />
          <Button
            size="sm"
            onClick={() => setTheoryOpen(true)}
            icon={<BookOpen size={13} />}
          >
            Theory & Guidelines
          </Button>
          <Button
            size="sm"
            onClick={handleResetParams}
            icon={<RotateCcw size={13} />}
          >
            Reset
          </Button>
        </div>
      </div>

      {error && <ErrorToast message={error} onRetry={() => runExperiment()} />}

      {/* Main Runner Layout: Left Parameters Panel, Right Workspace */}
      <div className="lab-runner-layout">
        {/* Dedicated Parameters Panel */}
        <aside className="lab-params-panel">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--tx)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Experiment Parameters
            </span>
            <span
              style={{ cursor: 'pointer', display: 'inline-flex' }}
              title="Reset Parameters"
              onClick={handleResetParams}
            >
              <RotateCcw size={13} color="var(--mu)" />
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {config.params.map((p) => {
              if (p.type === 'select') {
                const isLab10Classifier = config.number === 10 && p.key === 'classifier';
                const isClassifyStep = (params['step'] || 'Preprocess').toLowerCase() === 'classify';
                if (isLab10Classifier && !isClassifyStep) {
                  return (
                    <div key={p.key} className="form-group" style={{ opacity: 0.6 }}>
                      <label className="form-label">{p.label}</label>
                      <select className="form-select" disabled value={params[p.key] || p.initial}>
                        {p.options.map((opt) => (
                          <option key={opt} value={opt}>
                            {opt}
                          </option>
                        ))}
                      </select>
                      <span style={{ fontSize: '11px', color: 'var(--mu)', marginTop: '2px', display: 'block' }}>
                        (Enabled in Step 2: Classify)
                      </span>
                    </div>
                  );
                }
                return (
                  <Select
                    key={p.key}
                    label={p.label}
                    value={params[p.key] || p.initial}
                    options={p.options}
                    onChange={(val) => handleParamChange(p.key, val)}
                  />
                );
              }
              if (p.type === 'range') {
                return (
                  <RangeField
                    key={p.key}
                    label={p.label}
                    value={params[p.key] ?? p.initial}
                    min={p.min}
                    max={p.max}
                    step={p.step}
                    onChange={(val) => handleParamChange(p.key, val)}
                  />
                );
              }
              return null;
            })}
          </div>

          <div style={{ marginTop: '6px' }}>
            <RunButton onClick={() => runExperiment()} loading={loading} />
          </div>

          {result?.meta && (
            <div style={{ fontSize: '11px', color: 'var(--mu)', borderTop: '1px solid var(--bd)', paddingTop: '10px' }}>
              <div>Execution Time: {result.meta.runtime_ms} ms</div>
              <div>Rows Ingested: {result.meta.rows_used?.toLocaleString() || 5000}</div>
            </div>
          )}
        </aside>

        {/* Results Workspace */}
        <main className="lab-results-panel">
          {/* Stale Parameters Warning Banner */}
          {isStale && (
            <div style={{ marginBottom: '14px' }}>
              <WarningBanner
                title="Configuration Modified"
                message="Current workspace view reflects the previous run (effective parameters). Click 'Run Experiment' to re-execute with your new settings."
              />
            </div>
          )}

          {/* Navigation Tabs */}
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <Skeleton height="120px" />
              <Skeleton height="280px" />
            </div>
          ) : !result ? (
            <EmptyState message="Click 'Run Experiment' to compute laboratory results." />
          ) : (
            <>
              {/* TAB 1: RESULT (Default - Primary Tabular Results) */}
              {activeTab === 'result' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {/* Pipeline Stepper (For Lab 10) */}
                  {config.special === 'pipeline' && (
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(4, 1fr)',
                        gap: '10px',
                      }}
                    >
                      {[
                        { key: 'Preprocess', label: '1. Preprocess', desc: 'Discretization & Audit' },
                        { key: 'Classify', label: '2. Classify', desc: '10-Fold CV Modeling' },
                        { key: 'Cluster', label: '3. Cluster', desc: 'K-Means Profiling' },
                        { key: 'Associate', label: '4. Associate', desc: 'Apriori Rule Mining' },
                      ].map((s) => {
                        const active = (params['step'] || 'Preprocess').toLowerCase() === s.key.toLowerCase();
                        return (
                          <div
                            key={s.key}
                            onClick={() => {
                              handleParamChange('step', s.key);
                              runExperiment({ ...params, step: s.key });
                            }}
                            style={{
                              padding: '12px 14px',
                              borderRadius: '8px',
                              border: active ? '2px solid var(--acd)' : '1px solid var(--bd)',
                              backgroundColor: active ? 'rgba(74, 107, 85, 0.08)' : '#fff',
                              cursor: 'pointer',
                              transition: 'all 0.15s ease',
                            }}
                          >
                            <div style={{ fontWeight: 700, fontSize: '13px', color: active ? 'var(--acd)' : 'var(--tx)' }}>
                              {s.label}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--mu)', marginTop: '2px' }}>{s.desc}</div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Top Summary Metrics */}
                  {result.metrics && Object.keys(result.metrics).length > 0 && (
                    <MetricCards metrics={result.metrics} />
                  )}

                  {/* Primary Data Tables */}
                  {result.tables && result.tables.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      {result.tables.map((table: any, idx: number) => (
                        <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--tx)' }}>
                            {table.name}
                          </span>
                          <DataTable columns={table.columns} rows={table.rows} maxHeight="420px" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <EmptyState message="No result tables generated for this configuration." />
                  )}
                </div>
              )}

              {/* TAB 2: CHARTS (Dedicated Visualizations & Specialized Visualizers) */}
              {activeTab === 'charts' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {/* Specialized Visualizer by Lab Special */}
                  {config.special === 'schema' && (
                    <SchemaDiagram
                      selectedSchema={params['schema'] || 'Star Schema'}
                      onSelectSchema={(schema) => {
                        handleParamChange('schema', schema);
                        runExperiment({ ...params, schema });
                      }}
                      executedSql={result.sql}
                    />
                  )}

                  {config.special === 'tree' && result.tree_data && (
                    <InteractiveDecisionTree treeData={result.tree_data} />
                  )}

                  {config.special === 'confusion' && (result.tables?.[1] || result.tables?.[0]) && (
                    <Card>
                      <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>Supervised Confusion Matrix</h4>
                      <ConfusionMatrix
                        columns={(result.tables[1] || result.tables[0]).columns}
                        rows={(result.tables[1] || result.tables[0]).rows}
                      />
                    </Card>
                  )}

                  {config.special === 'cluster' && result.points && (
                    <Card>
                      <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>
                        2D PCA Cluster Scatter Projection (k={params['k'] || 3})
                      </h4>
                      <ScatterPlot points={result.points} height={320} />
                    </Card>
                  )}

                  {config.special === 'dendrogram' && (
                    <Card>
                      <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>
                        Hierarchical Clustering Dendrogram ({String(params['linkage'] || 'Ward')} Linkage)
                      </h4>
                      <Dendrogram
                        clusters={Number(params['clusters'] || 3)}
                        linkage={String(params['linkage'] || 'Ward')}
                      />
                    </Card>
                  )}

                  {config.special === 'network' && (
                    <Card>
                      <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>
                        Behavioral Association Affinity Network Graph (Apriori)
                      </h4>
                      <NetworkChart
                        edges={
                          (result.network_edges && result.network_edges.length > 0)
                            ? result.network_edges
                            : (result.charts?.[0]?.series || result.rules || [])
                                .filter((s: any) => s.source && s.target)
                                .map((s: any) => ({
                                  source: String(s.source),
                                  target: String(s.target),
                                  lift: Number(s.lift || 1),
                                  confidence: Number(s.confidence || 0.5),
                                }))
                        }
                        height={340}
                      />
                    </Card>
                  )}

                  {config.special === 'pipeline' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {(params['step'] || 'Preprocess').toLowerCase() === 'classify' && (
                        <>
                          {(params['classifier'] || 'Decision Tree') === 'Decision Tree' && result.tree_data && (
                            <InteractiveDecisionTree treeData={result.tree_data} />
                          )}
                          {((params['classifier'] || 'Decision Tree') === 'Naive Bayes' || !result.tree_data) && result.tables?.[1] && (
                            <Card>
                              <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>Supervised Confusion Matrix</h4>
                              <ConfusionMatrix columns={result.tables[1].columns} rows={result.tables[1].rows} />
                            </Card>
                          )}
                        </>
                      )}

                      {(params['step'] || 'Preprocess').toLowerCase() === 'cluster' && result.points && (
                        <Card>
                          <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>K-Means 2D PCA Cluster Projection</h4>
                          <ScatterPlot points={result.points} height={320} />
                        </Card>
                      )}

                      {(params['step'] || 'Preprocess').toLowerCase() === 'associate' && (
                        <Card>
                          <h4 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600 }}>Apriori Behavioral Rule Network</h4>
                          <NetworkChart
                            edges={
                              (result.network_edges && result.network_edges.length > 0)
                                ? result.network_edges
                                : (result.charts?.[0]?.series || result.rules || [])
                                    .filter((s: any) => s.source && s.target)
                                    .map((s: any) => ({
                                      source: String(s.source),
                                      target: String(s.target),
                                      lift: Number(s.lift || 1),
                                      confidence: Number(s.confidence || 0.5),
                                    }))
                            }
                            height={340}
                          />
                        </Card>
                      )}
                    </div>
                  )}

                  {/* Standard Result Charts */}
                  {result.charts && result.charts.length > 0 && (
                    <div className="lab-charts-grid">
                      {result.charts.map((chart: any, idx: number) => (
                        <div key={idx} className="chart-card-standalone">
                          <h4 className="chart-header-title">{chart.title}</h4>
                          <AnalyticsChart type={chart.type || 'bar'} data={chart.series} height={260} />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: METRICS */}
              {activeTab === 'metrics' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {result.metrics && Object.keys(result.metrics).length > 0 ? (
                    <MetricCards metrics={result.metrics} />
                  ) : (
                    <EmptyState message="No performance metrics computed." />
                  )}
                </div>
              )}

              {/* TAB 4: OBSERVATION */}
              {activeTab === 'observation' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {result.observations && result.observations.length > 0 ? (
                    <ObservationList observations={result.observations} />
                  ) : (
                    <EmptyState message="No academic observations recorded." />
                  )}
                </div>
              )}

              {/* TAB 5: SQL / CODE (Strictly Opt-in) */}
              {activeTab === 'sql' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12.5px', color: 'var(--mu)', fontWeight: 500 }}>
                      Executed SQL / Python Computational Algorithm:
                    </span>
                    <Button size="sm" onClick={handleCopyCode} icon={copied ? <Check size={13} /> : <Copy size={13} />}>
                      {copied ? 'Copied' : 'Copy Code'}
                    </Button>
                  </div>
                  <pre className="code-block-container">
                    <code>{result.sql || '-- No specific SQL statement logged for this experiment.'}</code>
                  </pre>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* Theory & Guidelines Modal */}
      <Modal
        isOpen={theoryOpen}
        onClose={() => setTheoryOpen(false)}
        title={`Academic Theory & Guidelines: Lab ${config.number} — ${config.title}`}
      >
        <div style={{ whiteSpace: 'pre-line' }}>{config.theory}</div>
      </Modal>
    </div>
  );
};

export default LabRunner;
