import React, { useState } from 'react';
import { apiFetch } from '../api/client';
import { ChartCard, ErrorToast } from '../components/ui';
import { Sparkles, Brain, Info } from 'lucide-react';

export const PredictionScreen: React.FC = () => {
  const [formData, setFormData] = useState({
    age: 21,
    gender: 'Male',
    country: 'India',
    academic_level: 'Undergraduate',
    most_used_platform: 'Instagram',
    purpose_of_use: 'Entertainment',
    avg_daily_usage_hours: 5.0,
    daily_unlocks: 150,
    study_hours: 3.0,
    physical_activity_hours: 1.5,
    sleep_hours_per_night: 7.0,
    stress_level: 'Medium',
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: string, val: any) => {
    setFormData((prev) => ({ ...prev, [field]: val }));
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch<any>('/api/predict/score', {
        method: 'POST',
        body: JSON.stringify(formData),
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {error && <ErrorToast message={error} onClose={() => setError(null)} />}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {/* Form Inputs */}
        <ChartCard
          title="Student Profile & Digital Habit Inputs"
          subtitle="Configure respondent demographic and lifestyle factors for model inference"
        >
          <form onSubmit={handlePredict} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={labelStyle}>Age</label>
                <input
                  type="number"
                  min={10}
                  max={100}
                  value={formData.age}
                  onChange={(e) => handleChange('age', parseInt(e.target.value) || 21)}
                  style={inputStyle}
                />
              </div>

              <div>
                <label style={labelStyle}>Gender</label>
                <select value={formData.gender} onChange={(e) => handleChange('gender', e.target.value)} style={inputStyle}>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Academic Level</label>
                <select value={formData.academic_level} onChange={(e) => handleChange('academic_level', e.target.value)} style={inputStyle}>
                  <option value="High School">High School</option>
                  <option value="Undergraduate">Undergraduate</option>
                  <option value="Graduate">Graduate</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Primary Platform</label>
                <select value={formData.most_used_platform} onChange={(e) => handleChange('most_used_platform', e.target.value)} style={inputStyle}>
                  <option value="Instagram">Instagram</option>
                  <option value="TikTok">TikTok</option>
                  <option value="YouTube">YouTube</option>
                  <option value="LinkedIn">LinkedIn</option>
                  <option value="Twitter">Twitter</option>
                  <option value="WhatsApp">WhatsApp</option>
                  <option value="Facebook">Facebook</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Purpose of Use</label>
                <select value={formData.purpose_of_use} onChange={(e) => handleChange('purpose_of_use', e.target.value)} style={inputStyle}>
                  <option value="Entertainment">Entertainment</option>
                  <option value="Education">Education</option>
                  <option value="Networking">Networking</option>
                  <option value="News">News</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Stress Level</label>
                <select value={formData.stress_level} onChange={(e) => handleChange('stress_level', e.target.value)} style={inputStyle}>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Very High">Very High</option>
                </select>
              </div>

              <div>
                <label style={labelStyle}>Screen Usage (hrs/day)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="24"
                  value={formData.avg_daily_usage_hours}
                  onChange={(e) => handleChange('avg_daily_usage_hours', parseFloat(e.target.value) || 0)}
                  style={inputStyle}
                />
              </div>

              <div>
                <label style={labelStyle}>Sleep Hours/Night</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="24"
                  value={formData.sleep_hours_per_night}
                  onChange={(e) => handleChange('sleep_hours_per_night', parseFloat(e.target.value) || 0)}
                  style={inputStyle}
                />
              </div>

              <div>
                <label style={labelStyle}>Study Hours/Day</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="24"
                  value={formData.study_hours}
                  onChange={(e) => handleChange('study_hours', parseFloat(e.target.value) || 0)}
                  style={inputStyle}
                />
              </div>

              <div>
                <label style={labelStyle}>Daily Phone Unlocks</label>
                <input
                  type="number"
                  min="0"
                  max="500"
                  value={formData.daily_unlocks}
                  onChange={(e) => handleChange('daily_unlocks', parseInt(e.target.value) || 0)}
                  style={inputStyle}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: '8px',
                backgroundColor: 'var(--ac)',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 18px',
                fontSize: '14px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              <Sparkles size={16} /> {loading ? 'Estimating Score...' : 'Predict Wellbeing Score'}
            </button>
          </form>
        </ChartCard>

        {/* Prediction Results & Ensemble Uncertainty Card */}
        <ChartCard
          title="Model Prediction & Ensemble Spread"
          subtitle="Trained over 5,000 physical survey respondents via 200-tree Random Forest"
        >
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div
                style={{
                  backgroundColor: 'var(--soft)',
                  borderRadius: '8px',
                  padding: '24px',
                  textAlign: 'center',
                }}
              >
                <span style={{ fontSize: '13px', color: 'var(--acd)', fontWeight: 600 }}>
                  Projected Mental Health Score
                </span>
                <div style={{ fontSize: '48px', fontWeight: 800, color: 'var(--tx)', marginTop: '4px' }}>
                  {result.predicted_score.toFixed(2)}
                  <span style={{ fontSize: '20px', color: 'var(--mu)', fontWeight: 400 }}> / 10</span>
                </div>
                <div style={{ fontSize: '14px', color: 'var(--tx)', marginTop: '8px', fontWeight: 500 }}>
                  {result.interpretation}
                </div>
              </div>

              {/* Ensemble Disagreement / Uncertainty Spread (AC-22) */}
              <div
                style={{
                  border: '1px solid var(--bd)',
                  borderRadius: '8px',
                  padding: '16px',
                  backgroundColor: '#fff',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Brain size={16} color="var(--acd)" />
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--tx)' }}>
                    Random Forest Ensemble Tree Spread
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-around', margin: '14px 0' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--mu)' }}>10th Percentile</div>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--tx)' }}>
                      {result.ensemble_tree_spread.tree_percentile_10.toFixed(2)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--mu)' }}>Ensemble Mean</div>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--acd)' }}>
                      {result.predicted_score.toFixed(2)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--mu)' }}>90th Percentile</div>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--tx)' }}>
                      {result.ensemble_tree_spread.tree_percentile_90.toFixed(2)}
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '8px',
                    fontSize: '11px',
                    color: 'var(--mu)',
                    borderTop: '1px solid var(--bd)',
                    paddingTop: '10px',
                    lineHeight: '1.4',
                  }}
                >
                  <Info size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{result.ensemble_tree_spread.metric_description}</span>
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{
                height: '300px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--mu)',
                gap: '8px',
              }}
            >
              <Sparkles size={32} strokeWidth={1.5} />
              <span>Configure attributes on the left and submit to view prediction.</span>
            </div>
          )}
        </ChartCard>
      </div>
    </div>
  );
};

const labelStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  color: 'var(--mu)',
  marginBottom: '4px',
  display: 'block',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  borderRadius: '6px',
  border: '1px solid var(--bd)',
  backgroundColor: '#fff',
  fontSize: '13px',
  color: 'var(--tx)',
  boxSizing: 'border-box',
};

