import React, { useState, useEffect, useCallback } from 'react';
import {
  RotateCcw,
  Search,
  Download,
  Database,
  Columns3,
  Eraser,
  Copy,
  Play,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { apiFetch } from '../api/client';
import { useApi } from '../hooks/useApi';
import { AnalyticsChart } from '../components/charts';
import {
  Button,
  Card,
  ChartCard,
  DataTable,
  ErrorToast,
  KpiCard,
  PageHeader,
  Select,
  Skeleton,
} from '../components/ui';

interface ExplorationData {
  overview: {
    rows: string;
    columns: number;
    missing: number;
    duplicates: number;
  };
  previewRows: Record<string, any>[];
  dataTypes: { column: string; type: string; non_null: string }[];
  statistics: { metric: string; mean: number; std: number; min: number; median: number; max: number }[];
  distributions: {
    usageHist: { name: string; value: number }[];
    sleepHist: { name: string; value: number }[];
    scoreHist: { name: string; value: number }[];
    platformWellbeing: { name: string; value: number }[];
  };
}

const SAMPLE_QUERIES = [
  {
    name: 'Platform Wellbeing Averages',
    sql: 'SELECT p.platform_name, COUNT(*) AS students, ROUND(AVG(f.mental_health_score), 2) AS avg_score, ROUND(AVG(f.avg_daily_usage_hours), 2) AS avg_usage FROM fact_survey_response f JOIN dim_platform p ON f.platform_key = p.platform_key GROUP BY p.platform_name ORDER BY avg_score DESC;',
  },
  {
    name: 'Top 10 Stress Counts by Country',
    sql: 'SELECT c.country_name, COUNT(*) AS students, ROUND(AVG(f.mental_health_score), 2) AS avg_score FROM fact_survey_response f JOIN dim_country c ON f.country_key = c.country_key GROUP BY c.country_name ORDER BY students DESC LIMIT 10;',
  },
  {
    name: 'Fact Conformed Join (Dual Grain)',
    sql: 'SELECT a.academic_level, COUNT(*) AS students, ROUND(AVG(f.avg_daily_usage_hours), 2) AS screen_hrs, ROUND(AVG(l.sleep_hours_per_night), 2) AS sleep_hrs, ROUND(AVG(l.study_hours), 2) AS study_hrs FROM fact_survey_response f JOIN fact_lifestyle l ON f.version_id = l.version_id AND f.source_row_id = l.source_row_id JOIN dim_academic a ON f.academic_key = a.academic_key GROUP BY a.academic_level;',
  },
];

export const DataExplorationScreen: React.FC = () => {
  const { data, loading, error, refetch } = useApi<ExplorationData>('/api/exploration');

  // Filter state for records query
  const [filterPlatform, setFilterPlatform] = useState('All platforms');
  const [filterAcademic, setFilterAcademic] = useState('All academic levels');
  const [filterStress, setFilterStress] = useState('All stress levels');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const [filteredRows, setFilteredRows] = useState<Record<string, any>[]>([]);
  const [totalMatches, setTotalMatches] = useState<number | null>(null);
  const [queryLoading, setQueryLoading] = useState(false);

  // SQL Query Lab state
  const [sql, setSql] = useState<string>(SAMPLE_QUERIES[0].sql);
  const [queryResult, setQueryResult] = useState<any>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [sqlError, setSqlError] = useState<string | null>(null);

  const fetchRecords = useCallback(async () => {
    setQueryLoading(true);
    try {
      const res = await apiFetch<any>('/api/exploration/query', {
        method: 'POST',
        body: JSON.stringify({
          platform: filterPlatform !== 'All platforms' ? filterPlatform : undefined,
          academic_level: filterAcademic !== 'All academic levels' ? filterAcademic : undefined,
          stress_level: filterStress !== 'All stress levels' ? filterStress : undefined,
          search: searchTerm.trim() || undefined,
          page,
          page_size: pageSize,
        }),
      });
      setFilteredRows(res.records || []);
      setTotalMatches(res.total_records ?? null);
    } catch {
      if (data?.previewRows) setFilteredRows(data.previewRows.slice((page - 1) * pageSize, page * pageSize));
    } finally {
      setQueryLoading(false);
    }
  }, [filterPlatform, filterAcademic, filterStress, searchTerm, page, data]);

  useEffect(() => {
    if (data?.previewRows) {
      if (
        filterPlatform === 'All platforms' &&
        filterAcademic === 'All academic levels' &&
        filterStress === 'All stress levels' &&
        !searchTerm.trim()
      ) {
        setFilteredRows(data.previewRows.slice((page - 1) * pageSize, page * pageSize));
        setTotalMatches(5000);
      } else {
        fetchRecords();
      }
    }
  }, [fetchRecords, data, filterPlatform, filterAcademic, filterStress, searchTerm, page]);

  function resetFilters() {
    setFilterPlatform('All platforms');
    setFilterAcademic('All academic levels');
    setFilterStress('All stress levels');
    setSearchTerm('');
    setPage(1);
  }

  const handleDownloadCsv = () => {
    if (!filteredRows || filteredRows.length === 0) return;
    const cols = Object.keys(filteredRows[0]);
    const csvContent = [
      cols.join(','),
      ...filteredRows.map((r) => cols.map((c) => JSON.stringify(r[c] ?? '')).join(',')),
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `student_survey_records_page_${page}.csv`);
    link.click();
  };

  const handleRunQuery = async () => {
    setRunning(true);
    setSqlError(null);
    try {
      const res = await apiFetch<any>('/api/warehouse/query', {
        method: 'POST',
        body: JSON.stringify({ sql, limit: 100 }),
      });
      setQueryResult(res);
    } catch (err: any) {
      setSqlError(err.message || 'Query execution failed.');
    } finally {
      setRunning(false);
    }
  };

  if (loading && !data) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <PageHeader
          title="Data exploration"
          subtitle="Inspect structure, quality, distributions and descriptive statistics."
        />
        <Skeleton height="300px" />
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <ErrorToast message={error || 'Failed to load exploration data'} onRetry={refetch} />
      </div>
    );
  }

  const recordCols =
    filteredRows.length > 0
      ? Object.keys(filteredRows[0])
      : [
          'Respondent_ID',
          'Age',
          'Gender',
          'Country',
          'Academic_Level',
          'Most_Used_Platform',
          'Daily_Usage_Hours',
          'Daily_Unlocks',
          'Sleep_Hours',
          'Study_Hours',
          'Mental_Health_Score',
          'Stress_Level',
        ];

  const recordRows = filteredRows.map((r) => recordCols.map((c) => r[c]));

  const dataTypesCols = ['Column', 'Data Type', 'Non-Null Count'];
  const dataTypesRows = data.dataTypes.map((d) => [d.column, d.type, d.non_null]);

  const statsCols = ['Metric', 'Mean', 'Std Dev', 'Min', 'Median', 'Max'];
  const statsRows = data.statistics.map((s) => [s.metric, s.mean, s.std, s.min, s.median, s.max]);

  const totalPages = Math.max(1, Math.ceil((totalMatches || 5000) / pageSize));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <PageHeader
        title="Data exploration"
        subtitle="Inspect structure, quality, distributions and descriptive statistics across 5,000 student survey responses."
        actions={
          <Button variant="secondary" onClick={refetch}>
            <RotateCcw size={14} style={{ marginRight: 6 }} />
            Refresh data
          </Button>
        }
      />

      {/* KPI Overview Grid */}
      <div className="overview-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
        <KpiCard
          title="Rows"
          value={data.overview.rows}
          subtitle="Complete survey respondent records"
          icon={<Database size={18} />}
        />
        <KpiCard
          title="Columns"
          value={data.overview.columns}
          subtitle="6 dimensions · 5 continuous metrics"
          icon={<Columns3 size={18} />}
        />
        <KpiCard
          title="Missing values"
          value={data.overview.missing}
          subtitle="100% complete · Zero imputation required"
          icon={<Eraser size={18} />}
        />
        <KpiCard
          title="Duplicate rows"
          value={data.overview.duplicates}
          subtitle="Preserved survey respondent signatures"
          icon={<Copy size={18} />}
        />
      </div>

      {/* Filter Card */}
      <Card style={{ padding: '16px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '14px', alignItems: 'flex-end' }}>
          <div style={{ flex: '1 1 220px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--tx)', marginBottom: '6px' }}>
              Search respondent, country or platform
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="e.g. India, Instagram, Undergraduate..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(1);
                }}
                style={{
                  width: '100%',
                  padding: '8px 10px 8px 32px',
                  borderRadius: '6px',
                  border: '1px solid var(--bd)',
                  fontSize: '13px',
                  backgroundColor: '#fff',
                  boxSizing: 'border-box',
                }}
              />
              <Search size={15} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--mu)' }} />
            </div>
          </div>

          <div style={{ minWidth: '170px' }}>
            <Select
              label="Platform"
              value={filterPlatform}
              options={['All platforms', 'Instagram', 'TikTok', 'YouTube', 'Twitter/X', 'Reddit', 'Facebook']}
              onChange={(v) => {
                setFilterPlatform(v);
                setPage(1);
              }}
            />
          </div>

          <div style={{ minWidth: '170px' }}>
            <Select
              label="Academic Level"
              value={filterAcademic}
              options={['All academic levels', 'Undergraduate', 'Graduate', 'High School', 'Doctorate']}
              onChange={(v) => {
                setFilterAcademic(v);
                setPage(1);
              }}
            />
          </div>

          <div style={{ minWidth: '170px' }}>
            <Select
              label="Stress Level"
              value={filterStress}
              options={['All stress levels', 'Low', 'Medium', 'High', 'Very High']}
              onChange={(v) => {
                setFilterStress(v);
                setPage(1);
              }}
            />
          </div>

          {(filterPlatform !== 'All platforms' ||
            filterAcademic !== 'All academic levels' ||
            filterStress !== 'All stress levels' ||
            searchTerm) && (
            <Button variant="secondary" onClick={resetFilters}>
              <RotateCcw size={14} style={{ marginRight: 4 }} />
              Reset
            </Button>
          )}
        </div>
      </Card>

      {/* Dataset Records Table Card */}
      <ChartCard
        title={`Dataset records ${totalMatches !== null ? `(${totalMatches.toLocaleString()} matches)` : '(Sample)'}`}
        subtitle="Interactive view of student survey respondent records joined across dimension and lifestyle facts"
        action={
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Button variant="outline" size="sm" onClick={handleDownloadCsv}>
              <Download size={13} style={{ marginRight: 5 }} />
              Download CSV
            </Button>
          </div>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {queryLoading ? (
            <Skeleton height="240px" />
          ) : (
            <DataTable columns={recordCols} rows={recordRows} maxHeight="340px" />
          )}

          {/* Pagination Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '6px' }}>
            <span style={{ fontSize: '12px', color: 'var(--mu)' }}>
              Showing page <strong>{page}</strong> of <strong>{totalPages}</strong> ({totalMatches ?? 5000} total rows)
            </span>
            <div style={{ display: 'flex', gap: '6px' }}>
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft size={14} /> Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                Next <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        </div>
      </ChartCard>

      {/* Schema & Descriptive Statistics Side-by-Side */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '16px' }}>
        <ChartCard title="Schema Data Types" subtitle="Physical column attributes and non-null guarantees">
          <DataTable columns={dataTypesCols} rows={dataTypesRows} maxHeight="320px" />
        </ChartCard>

        <ChartCard title="Descriptive Statistics" subtitle="Empirical moments for continuous behavioral features">
          <DataTable columns={statsCols} rows={statsRows} maxHeight="320px" />
        </ChartCard>
      </div>

      {/* Continuous Feature Distributions Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <ChartCard title="Daily screen time distribution" subtitle="Frequency by daily usage hours range">
          <AnalyticsChart type="bar" data={data.distributions.usageHist} height={200} color="#7fa88a" />
        </ChartCard>

        <ChartCard title="Sleep duration distribution" subtitle="Frequency by nightly sleep hours range">
          <AnalyticsChart type="bar" data={data.distributions.sleepHist} height={200} color="#6b8fa3" />
        </ChartCard>

        <ChartCard title="Mental health score distribution" subtitle="Frequency by wellbeing score range">
          <AnalyticsChart type="bar" data={data.distributions.scoreHist} height={200} color="#d68c67" />
        </ChartCard>
      </div>

      {/* Platform Wellbeing Breakdown Chart */}
      <ChartCard
        title="Platform wellbeing comparison"
        subtitle="Mean Mental Health Score observed across major social media platforms"
      >
        <AnalyticsChart type="bar" data={data.distributions.platformWellbeing} height={220} color="#5f8d6d" />
      </ChartCard>

      {/* Interactive SQL Query Lab (Secondary Section) */}
      <ChartCard
        title="Interactive SQL Query Lab"
        subtitle="Execute secure, read-only analytical queries against the SQLite warehouse"
        action={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--acd)' }}>
            <ShieldCheck size={16} />
            <span>SQLite Authorizer & Query-Only Protected</span>
          </div>
        }
      >
        {sqlError && <ErrorToast message={sqlError} onClose={() => setSqlError(null)} onRetry={handleRunQuery} />}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--mu)', fontWeight: 600 }}>Sample Templates:</span>
            {SAMPLE_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => setSql(q.sql)}
                style={{
                  padding: '4px 10px',
                  fontSize: '11px',
                  borderRadius: '12px',
                  border: '1px solid var(--bd)',
                  backgroundColor: 'var(--soft)',
                  color: 'var(--acd)',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                {q.name}
              </button>
            ))}
          </div>

          <textarea
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            rows={4}
            style={{
              width: '100%',
              fontFamily: 'Consolas, Monaco, "Courier New", monospace',
              fontSize: '13px',
              padding: '12px',
              borderRadius: '6px',
              border: '1px solid var(--bd)',
              backgroundColor: '#faf8f5',
              color: 'var(--tx)',
              boxSizing: 'border-box',
              resize: 'vertical',
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              onClick={handleRunQuery}
              disabled={running}
              style={{
                backgroundColor: 'var(--ac)',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: running ? 'not-allowed' : 'pointer',
              }}
            >
              <Play size={14} /> {running ? 'Executing...' : 'Run Query'}
            </button>

            {queryResult && (
              <span style={{ fontSize: '12px', color: 'var(--mu)' }}>
                Executed in <strong>{queryResult.execution_time_ms} ms</strong> · {queryResult.row_count} rows returned
                {queryResult.is_truncated && ' (truncated at 100)'}
              </span>
            )}
          </div>

          {queryResult && (
            <div style={{ marginTop: '12px' }}>
              <DataTable columns={queryResult.columns} rows={queryResult.rows} maxHeight="300px" />
            </div>
          )}
        </div>
      </ChartCard>
    </div>
  );
};
export default DataExplorationScreen;
