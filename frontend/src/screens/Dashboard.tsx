import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { KpiCard, ChartCard, ErrorToast, Select, Button } from '../components/ui';
import { BarChart, HorizontalBarChart, DonutChart } from '../components/charts';
import { Filter, RotateCcw, Activity, Clock, Moon, BookOpen, Smartphone, Users } from 'lucide-react';

export const DashboardScreen: React.FC = () => {
  const [country, setCountry] = useState<string>('All');
  const [academicLevel, setAcademicLevel] = useState<string>('All');
  const [gender, setGender] = useState<string>('All');

  const { data: filterOpts } = useApi<any>('/api/dashboard/filters');

  // Build query string
  const params = new URLSearchParams();
  if (country !== 'All') params.append('country', country);
  if (academicLevel !== 'All') params.append('academic_level', academicLevel);
  if (gender !== 'All') params.append('gender', gender);
  const qs = params.toString() ? `?${params.toString()}` : '';

  const { data, loading, error, refetch } = useApi<any>(`/api/dashboard/overview${qs}`, [qs]);

  const kpis = data?.kpis;
  const stressDist = data?.stress_distribution || [];
  const platformUsage = data?.platform_usage_breakdown || [];
  const academicSummary = data?.academic_level_summary || [];

  const handleResetFilters = () => {
    setCountry('All');
    setAcademicLevel('All');
    setGender('All');
  };

  const countries = ['All', ...(filterOpts?.countries || [])];
  const levels = ['All', ...(filterOpts?.academic_levels || [])];
  const genders = ['All', ...(filterOpts?.genders || [])];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onRetry={refetch} />}

      {/* Self-Contained Dashboard Filter Bar */}
      <div
        style={{
          backgroundColor: 'var(--card)',
          border: '1px solid var(--bd)',
          borderRadius: '8px',
          padding: '12px 18px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--mu)', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <Filter size={14} color="var(--acd)" />
            Dashboard Filters:
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="form-select"
              style={{ width: 'auto', padding: '6px 10px', fontSize: '12px' }}
            >
              {countries.map((c) => (
                <option key={c} value={c}>
                  Country: {c}
                </option>
              ))}
            </select>

            <select
              value={academicLevel}
              onChange={(e) => setAcademicLevel(e.target.value)}
              className="form-select"
              style={{ width: 'auto', padding: '6px 10px', fontSize: '12px' }}
            >
              {levels.map((l) => (
                <option key={l} value={l}>
                  Level: {l}
                </option>
              ))}
            </select>

            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="form-select"
              style={{ width: 'auto', padding: '6px 10px', fontSize: '12px' }}
            >
              {genders.map((g) => (
                <option key={g} value={g}>
                  Gender: {g}
                </option>
              ))}
            </select>
          </div>
        </div>

        <Button size="sm" onClick={handleResetFilters} icon={<RotateCcw size={13} />}>
          Reset Filters
        </Button>
      </div>

      {/* KPI Ribbon */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '14px' }}>
        <KpiCard
          title="Total Respondents"
          value={kpis?.total_students?.toLocaleString() || '5,000'}
          subtitle="Physical SQLite warehouse grain"
          icon={<Users size={16} />}
        />
        <KpiCard
          title="Avg Mental Health"
          value={kpis ? `${kpis.avg_mental_health_score}/10` : '6.2/10'}
          subtitle="Scale: 1 (Poor) to 10 (Good)"
          icon={<Activity size={16} />}
        />
        <KpiCard
          title="Avg Daily Usage"
          value={kpis ? `${kpis.avg_daily_usage_hours}h` : '4.8h'}
          subtitle="Social media screen time"
          icon={<Clock size={16} />}
        />
        <KpiCard
          title="Avg Sleep Duration"
          value={kpis ? `${kpis.avg_sleep_hours}h` : '6.7h'}
          subtitle="Nightly sleep average"
          icon={<Moon size={16} />}
        />
        <KpiCard
          title="Avg Study Hours"
          value={kpis ? `${kpis.avg_study_hours}h` : '4.2h'}
          subtitle="Academic preparation time"
          icon={<BookOpen size={16} />}
        />
        <KpiCard
          title="Avg Daily Unlocks"
          value={kpis?.avg_daily_unlocks?.toFixed(1) || '82.4'}
          subtitle="Device check frequency"
          icon={<Smartphone size={16} />}
        />
      </div>

      {/* Primary Chart Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        <ChartCard
          title="Stress Level Distribution"
          subtitle="Proportion of students reporting each stress severity level"
        >
          <DonutChart
            data={stressDist.map((item: any) => ({
              label: item.stress_level,
              value: item.count,
            }))}
            size={180}
          />
        </ChartCard>

        <ChartCard
          title="Platform Usage Breakdown"
          subtitle="Average daily usage hours across primary social platforms"
        >
          <HorizontalBarChart
            labels={platformUsage.map((p: any) => p.platform)}
            values={platformUsage.map((p: any) => p.avg_usage_hours)}
            valueSuffix=" hrs"
          />
        </ChartCard>
      </div>

      {/* Secondary Chart Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        <ChartCard
          title="Academic Level Wellbeing"
          subtitle="Average mental health score across educational stages"
        >
          <BarChart
            labels={academicSummary.map((a: any) => a.level)}
            values={academicSummary.map((a: any) => a.avg_mental_score)}
            valueSuffix="/10"
            color="var(--acd)"
          />
        </ChartCard>

        <ChartCard
          title="Platform Population Count"
          subtitle="Total survey respondents per social media platform"
        >
          <BarChart
            labels={platformUsage.slice(0, 6).map((p: any) => p.platform)}
            values={platformUsage.slice(0, 6).map((p: any) => p.students)}
            color="var(--ac)"
          />
        </ChartCard>
      </div>
    </div>
  );
};

export default DashboardScreen;
