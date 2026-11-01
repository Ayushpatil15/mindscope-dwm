import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { ChartCard, DataTable, ErrorToast } from '../components/ui';
import { Upload, RefreshCw, CheckCircle2 } from 'lucide-react';

export const ETLManagementScreen: React.FC = () => {
  const { data: statusData, loading: statusLoading, refetch: refetchStatus } = useApi<any>('/api/etl/status');
  const { data: versionsData, loading: versionsLoading, refetch: refetchVersions } = useApi<any[]>('/api/etl/versions');
  const { data: historyData, loading: historyLoading, refetch: refetchHistory } = useApi<any[]>('/api/etl/history');

  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);
    setUploadMsg(null);

    try {
      const res = await fetch('/api/etl/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }
      setUploadMsg('Dataset successfully processed, verified, and activated!');
      refetchStatus();
      refetchVersions();
      refetchHistory();
    } catch (err: any) {
      setError(err.message || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  const versionColumns = ['Version #', 'Batch ID', 'Filename', 'Row Count', 'Active', 'Created At'];
  const versionRows = (versionsData || []).map((v) => [
    v.version_number,
    v.batch_id,
    v.source_filename,
    v.row_count?.toLocaleString(),
    v.is_active ? 'YES (Active)' : 'No',
    new Date(v.created_at).toLocaleString(),
  ]);

  const historyColumns = ['Run ID', 'Batch ID', 'Source File', 'Status', 'Extracted', 'Loaded', 'Rejected', 'Started At'];
  const historyRows = (historyData || []).map((h) => [
    h.run_id,
    h.batch_id,
    h.source_file,
    h.status,
    h.rows_extracted,
    h.rows_loaded,
    h.rows_rejected,
    new Date(h.started_at).toLocaleString(),
  ]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onClose={() => setError(null)} />}

      {/* Active Version Status Header */}
      <div
        className="card"
        style={{
          backgroundColor: 'var(--card)',
          borderRadius: '8px',
          border: '1px solid var(--bd)',
          padding: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={18} color="var(--acd)" />
            <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--tx)' }}>
              Active Warehouse Version {statusData?.active_dataset_version || 1}
            </span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--mu)', marginTop: '4px' }}>
            {statusData?.row_count?.toLocaleString() || 5000} Verified Records · SHA-256:{' '}
            <span style={{ fontFamily: 'monospace' }}>{statusData?.sha256_checksum?.slice(0, 16)}...</span>
          </div>
        </div>

        {/* Upload replacement CSV */}
        <div>
          <label
            style={{
              backgroundColor: 'var(--ac)',
              color: '#fff',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: uploading ? 'not-allowed' : 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Upload size={14} /> {uploading ? 'Processing ETL...' : 'Upload CSV & Re-ingest'}
            <input type="file" accept=".csv" onChange={handleFileUpload} disabled={uploading} style={{ display: 'none' }} />
          </label>
        </div>
      </div>

      {uploadMsg && (
        <div style={{ padding: '12px', backgroundColor: '#eef8ef', color: '#3d7849', borderRadius: '6px', fontSize: '13px' }}>
          {uploadMsg}
        </div>
      )}

      {/* Versions Table */}
      <ChartCard
        title="Dataset Versions Catalog"
        subtitle="Version lineage tracking atomic replacement and cache invalidation"
        loading={versionsLoading}
      >
        <DataTable columns={versionColumns} rows={versionRows} maxHeight="240px" />
      </ChartCard>

      {/* ETL Runs Audit History */}
      <ChartCard
        title="ETL Execution Run Audit Logs"
        subtitle="Historical run logs capturing staging balance and rejection counts"
        loading={historyLoading}
      >
        <DataTable columns={historyColumns} rows={historyRows} maxHeight="300px" />
      </ChartCard>
    </div>
  );
};

