import React, { useState } from 'react';
import {
  Database,
  Layers,
  Key,
  Info,
  CheckCircle2,
  Table,
  Sparkles,
  ChevronRight,
  Code2,
} from 'lucide-react';
import { Button } from './ui';

export interface ColumnDef {
  name: string;
  type: string;
  isPk?: boolean;
  isFk?: boolean;
  references?: string;
  isMeasure?: boolean;
}

export interface TableNode {
  id: string;
  name: string;
  classification: 'fact' | 'dimension' | 'conformed_dim' | 'normalized_dim';
  role: string;
  x: number;
  y: number;
  width: number;
  height: number;
  columns: ColumnDef[];
}

export interface RelationshipDef {
  id: string;
  fromTable: string;
  fromColumn: string;
  toTable: string;
  toColumn: string;
  cardinality: string;
  type: 'dim_to_fact' | 'outrigger' | 'conformed';
}

export interface SchemaArchitecture {
  id: string;
  name: string;
  subtitle: string;
  badge: string;
  summary: string;
  advantages: string[];
  tradeoffs: string[];
  canvasWidth: number;
  canvasHeight: number;
  tables: TableNode[];
  relationships: RelationshipDef[];
}

export const SCHEMA_CONFIGS: Record<string, SchemaArchitecture> = {
  'Star Schema': {
    id: 'star',
    name: 'Star Schema',
    subtitle: 'Single central fact table surrounded by denormalized dimension tables',
    badge: 'Denormalized · Single-Hop Joins · Optimized Analytical Reads',
    summary:
      'The operational dimensional standard for Student DWM. Central fact_survey_response stores 5,000 granular student survey transactions, joining directly to dimension tables without multi-hop overhead.',
    advantages: [
      'Fastest analytical read performance with minimal join complexity.',
      'Optimal compatibility with SQL-backed OLAP cubes, slice, and dice.',
      'Simpler conceptual model for academic exploration and reporting.',
    ],
    tradeoffs: [
      'Denormalized attributes in dimensions increase minor storage footprint.',
      'Attribute updates require updates across all occurrences within the dimension.',
    ],
    canvasWidth: 920,
    canvasHeight: 520,
    tables: [
      {
        id: 'fact_survey_response',
        name: 'fact_survey_response',
        classification: 'fact',
        role: 'Central operational fact table (Grain: 1 survey response)',
        x: 330,
        y: 130,
        width: 260,
        height: 250,
        columns: [
          { name: 'survey_key', type: 'INTEGER', isPk: true },
          { name: 'respondent_key', type: 'INTEGER', isFk: true, references: 'dim_respondent.respondent_key' },
          { name: 'academic_key', type: 'INTEGER', isFk: true, references: 'dim_academic.academic_key' },
          { name: 'country_key', type: 'INTEGER', isFk: true, references: 'dim_country.country_key' },
          { name: 'platform_key', type: 'INTEGER', isFk: true, references: 'dim_platform.platform_key' },
          { name: 'purpose_key', type: 'INTEGER', isFk: true, references: 'dim_purpose.purpose_key' },
          { name: 'stress_key', type: 'INTEGER', isFk: true, references: 'dim_stress.stress_key' },
          { name: 'mental_health_score', type: 'REAL', isMeasure: true },
          { name: 'avg_daily_usage_hours', type: 'REAL', isMeasure: true },
          { name: 'daily_unlocks', type: 'INTEGER', isMeasure: true },
        ],
      },
      {
        id: 'dim_respondent',
        name: 'dim_respondent',
        classification: 'dimension',
        role: 'Student demographic profile',
        x: 30,
        y: 30,
        width: 220,
        height: 140,
        columns: [
          { name: 'respondent_key', type: 'INTEGER', isPk: true },
          { name: 'age', type: 'INTEGER' },
          { name: 'gender_key', type: 'INTEGER' },
          { name: 'academic_key', type: 'INTEGER' },
        ],
      },
      {
        id: 'dim_platform',
        name: 'dim_platform',
        classification: 'dimension',
        role: 'Social media platform context',
        x: 670,
        y: 30,
        width: 220,
        height: 130,
        columns: [
          { name: 'platform_key', type: 'INTEGER', isPk: true },
          { name: 'platform_name', type: 'TEXT' },
          { name: 'platform_category', type: 'TEXT' },
        ],
      },
      {
        id: 'dim_country',
        name: 'dim_country',
        classification: 'dimension',
        role: 'Geographical origin',
        x: 30,
        y: 340,
        width: 220,
        height: 130,
        columns: [
          { name: 'country_key', type: 'INTEGER', isPk: true },
          { name: 'country_name', type: 'TEXT' },
          { name: 'region', type: 'TEXT' },
        ],
      },
      {
        id: 'dim_stress',
        name: 'dim_stress',
        classification: 'dimension',
        role: 'Psychological stress level category',
        x: 670,
        y: 340,
        width: 220,
        height: 130,
        columns: [
          { name: 'stress_key', type: 'INTEGER', isPk: true },
          { name: 'stress_level', type: 'TEXT' },
          { name: 'stress_rank', type: 'INTEGER' },
        ],
      },
      {
        id: 'dim_academic',
        name: 'dim_academic',
        classification: 'dimension',
        role: 'Educational stage',
        x: 350,
        y: 10,
        width: 220,
        height: 100,
        columns: [
          { name: 'academic_key', type: 'INTEGER', isPk: true },
          { name: 'academic_level', type: 'TEXT' },
        ],
      },
    ],
    relationships: [
      { id: 'r1', fromTable: 'dim_respondent', fromColumn: 'respondent_key', toTable: 'fact_survey_response', toColumn: 'respondent_key', cardinality: '1:N', type: 'dim_to_fact' },
      { id: 'r2', fromTable: 'dim_platform', fromColumn: 'platform_key', toTable: 'fact_survey_response', toColumn: 'platform_key', cardinality: '1:N', type: 'dim_to_fact' },
      { id: 'r3', fromTable: 'dim_country', fromColumn: 'country_key', toTable: 'fact_survey_response', toColumn: 'country_key', cardinality: '1:N', type: 'dim_to_fact' },
      { id: 'r4', fromTable: 'dim_stress', fromColumn: 'stress_key', toTable: 'fact_survey_response', toColumn: 'stress_key', cardinality: '1:N', type: 'dim_to_fact' },
      { id: 'r5', fromTable: 'dim_academic', fromColumn: 'academic_key', toTable: 'fact_survey_response', toColumn: 'academic_key', cardinality: '1:N', type: 'dim_to_fact' },
    ],
  },

  'Snowflake Schema': {
    id: 'snowflake',
    name: 'Snowflake Schema',
    subtitle: 'Normalized dimension hierarchies reducing categorical redundancy',
    badge: 'Normalized · Third Normal Form (3NF) Dimensions · Multi-Hop Joins',
    summary:
      'Normalized variation where Dim_Respondent is decomposed into Dim_Gender and Dim_Academic outriggers, eliminating repetitive textual attributes at the expense of additional join hops.',
    advantages: [
      'Eliminates duplicate storage of repeated categorical labels across student profiles.',
      'Enforces referential integrity at every sub-level of the dimensional hierarchy.',
    ],
    tradeoffs: [
      'Multi-hop joins (Fact → Dim_Respondent → Dim_Academic) increase OLAP query latency.',
      'Complex query syntax for end-user SQL self-service exploration.',
    ],
    canvasWidth: 920,
    canvasHeight: 520,
    tables: [
      {
        id: 'fact_survey_response',
        name: 'fact_survey_response',
        classification: 'fact',
        role: 'Central operational fact table',
        x: 340,
        y: 160,
        width: 240,
        height: 220,
        columns: [
          { name: 'survey_key', type: 'INTEGER', isPk: true },
          { name: 'respondent_key', type: 'INTEGER', isFk: true, references: 'dim_respondent.respondent_key' },
          { name: 'country_key', type: 'INTEGER', isFk: true, references: 'dim_country.country_key' },
          { name: 'platform_key', type: 'INTEGER', isFk: true, references: 'dim_platform.platform_key' },
          { name: 'mental_health_score', type: 'REAL', isMeasure: true },
          { name: 'avg_daily_usage_hours', type: 'REAL', isMeasure: true },
        ],
      },
      {
        id: 'dim_respondent',
        name: 'dim_respondent',
        classification: 'dimension',
        role: 'Normalized student profile with outrigger FKs',
        x: 60,
        y: 120,
        width: 210,
        height: 140,
        columns: [
          { name: 'respondent_key', type: 'INTEGER', isPk: true },
          { name: 'age', type: 'INTEGER' },
          { name: 'gender_key', type: 'INTEGER', isFk: true, references: 'dim_gender.gender_key' },
          { name: 'academic_key', type: 'INTEGER', isFk: true, references: 'dim_academic.academic_key' },
        ],
      },
      {
        id: 'dim_gender',
        name: 'dim_gender',
        classification: 'normalized_dim',
        role: 'Outrigger dimension: Gender taxonomy',
        x: 30,
        y: 10,
        width: 180,
        height: 90,
        columns: [
          { name: 'gender_key', type: 'INTEGER', isPk: true },
          { name: 'gender_name', type: 'TEXT' },
        ],
      },
      {
        id: 'dim_academic',
        name: 'dim_academic',
        classification: 'normalized_dim',
        role: 'Outrigger dimension: Academic tier',
        x: 30,
        y: 330,
        width: 190,
        height: 100,
        columns: [
          { name: 'academic_key', type: 'INTEGER', isPk: true },
          { name: 'academic_level', type: 'TEXT' },
          { name: 'tier_level', type: 'TEXT' },
        ],
      },
      {
        id: 'dim_platform',
        name: 'dim_platform',
        classification: 'dimension',
        role: 'Platform entity',
        x: 660,
        y: 120,
        width: 210,
        height: 110,
        columns: [
          { name: 'platform_key', type: 'INTEGER', isPk: true },
          { name: 'platform_name', type: 'TEXT' },
        ],
      },
      {
        id: 'dim_country',
        name: 'dim_country',
        classification: 'dimension',
        role: 'Geographical origin',
        x: 660,
        y: 300,
        width: 210,
        height: 110,
        columns: [
          { name: 'country_key', type: 'INTEGER', isPk: true },
          { name: 'country_name', type: 'TEXT' },
        ],
      },
    ],
    relationships: [
      { id: 's1', fromTable: 'dim_gender', fromColumn: 'gender_key', toTable: 'dim_respondent', toColumn: 'gender_key', cardinality: '1:N', type: 'outrigger' },
      { id: 's2', fromTable: 'dim_academic', fromColumn: 'academic_key', toTable: 'dim_respondent', toColumn: 'academic_key', cardinality: '1:N', type: 'outrigger' },
      { id: 's3', fromTable: 'dim_respondent', fromColumn: 'respondent_key', toTable: 'fact_survey_response', toColumn: 'respondent_key', cardinality: '1:N', type: 'dim_to_fact' },
      { id: 's4', fromTable: 'dim_platform', fromColumn: 'platform_key', toTable: 'fact_survey_response', toColumn: 'platform_key', cardinality: '1:N', type: 'dim_to_fact' },
      { id: 's5', fromTable: 'dim_country', fromColumn: 'country_key', toTable: 'fact_survey_response', toColumn: 'country_key', cardinality: '1:N', type: 'dim_to_fact' },
    ],
  },

  'Fact Constellation Schema': {
    id: 'constellation',
    name: 'Fact Constellation (Galaxy Schema)',
    subtitle: 'Multiple distinct business process fact tables sharing conformed dimensions',
    badge: 'Dual Business Processes · Conformed Dimensions · Cross-Process Analytics',
    summary:
      'Enterprise architecture incorporating two distinct fact tables: fact_survey_response (digital usage) and fact_lifestyle (study, exercise, sleep habits). Both facts share conformed dimensions dim_respondent and dim_country.',
    advantages: [
      'Decouples distinct business process measurements with different measurement frequencies.',
      'Conformed dimensions guarantee drill-across compatibility across usage and lifestyle domains.',
    ],
    tradeoffs: [
      'Requires drill-across queries with outer joins when reconciling both facts together.',
      'Slightly higher warehouse modeling governance overhead.',
    ],
    canvasWidth: 920,
    canvasHeight: 520,
    tables: [
      {
        id: 'fact_survey_response',
        name: 'fact_survey_response',
        classification: 'fact',
        role: 'Process 1: Social media digital engagement',
        x: 120,
        y: 160,
        width: 240,
        height: 200,
        columns: [
          { name: 'survey_key', type: 'INTEGER', isPk: true },
          { name: 'respondent_key', type: 'INTEGER', isFk: true, references: 'dim_respondent.respondent_key' },
          { name: 'country_key', type: 'INTEGER', isFk: true, references: 'dim_country.country_key' },
          { name: 'platform_key', type: 'INTEGER', isFk: true, references: 'dim_platform.platform_key' },
          { name: 'mental_health_score', type: 'REAL', isMeasure: true },
          { name: 'avg_daily_usage_hours', type: 'REAL', isMeasure: true },
        ],
      },
      {
        id: 'fact_lifestyle',
        name: 'fact_lifestyle',
        classification: 'fact',
        role: 'Process 2: Academic study & physical habits',
        x: 560,
        y: 160,
        width: 240,
        height: 200,
        columns: [
          { name: 'lifestyle_key', type: 'INTEGER', isPk: true },
          { name: 'respondent_key', type: 'INTEGER', isFk: true, references: 'dim_respondent.respondent_key' },
          { name: 'country_key', type: 'INTEGER', isFk: true, references: 'dim_country.country_key' },
          { name: 'study_hours', type: 'REAL', isMeasure: true },
          { name: 'physical_activity_hours', type: 'REAL', isMeasure: true },
          { name: 'sleep_hours_per_night', type: 'REAL', isMeasure: true },
        ],
      },
      {
        id: 'dim_respondent',
        name: 'dim_respondent',
        classification: 'conformed_dim',
        role: 'Conformed dimension shared by both facts',
        x: 350,
        y: 20,
        width: 220,
        height: 110,
        columns: [
          { name: 'respondent_key', type: 'INTEGER', isPk: true },
          { name: 'age', type: 'INTEGER' },
          { name: 'gender_key', type: 'INTEGER' },
        ],
      },
      {
        id: 'dim_country',
        name: 'dim_country',
        classification: 'conformed_dim',
        role: 'Conformed dimension shared by both facts',
        x: 350,
        y: 390,
        width: 220,
        height: 100,
        columns: [
          { name: 'country_key', type: 'INTEGER', isPk: true },
          { name: 'country_name', type: 'TEXT' },
        ],
      },
    ],
    relationships: [
      { id: 'c1', fromTable: 'dim_respondent', fromColumn: 'respondent_key', toTable: 'fact_survey_response', toColumn: 'respondent_key', cardinality: '1:N', type: 'conformed' },
      { id: 'c2', fromTable: 'dim_respondent', fromColumn: 'respondent_key', toTable: 'fact_lifestyle', toColumn: 'respondent_key', cardinality: '1:N', type: 'conformed' },
      { id: 'c3', fromTable: 'dim_country', fromColumn: 'country_key', toTable: 'fact_survey_response', toColumn: 'country_key', cardinality: '1:N', type: 'conformed' },
      { id: 'c4', fromTable: 'dim_country', fromColumn: 'country_key', toTable: 'fact_lifestyle', toColumn: 'country_key', cardinality: '1:N', type: 'conformed' },
    ],
  },
};

export const SchemaDiagram: React.FC<{
  selectedSchema?: string;
  onSelectSchema?: (schema: string) => void;
  executedSql?: string;
}> = ({ selectedSchema = 'Star Schema', onSelectSchema, executedSql }) => {
  const [activeSchemaKey, setActiveSchemaKey] = useState<string>(selectedSchema);
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);

  const currentArch = SCHEMA_CONFIGS[activeSchemaKey] || SCHEMA_CONFIGS['Star Schema'];

  const handleSchemaChange = (schemaKey: string) => {
    setActiveSchemaKey(schemaKey);
    setSelectedTableId(null);
    if (onSelectSchema) onSelectSchema(schemaKey);
  };

  const selectedTable = currentArch.tables.find((t) => t.id === selectedTableId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Schema Model Selector */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          backgroundColor: 'var(--card)',
          border: '1px solid var(--bd)',
          borderRadius: '8px',
          padding: '12px 16px',
        }}
      >
        <div style={{ display: 'flex', gap: '8px' }}>
          {Object.keys(SCHEMA_CONFIGS).map((key) => (
            <Button
              key={key}
              variant={activeSchemaKey === key ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => handleSchemaChange(key)}
            >
              <Database size={13} />
              <span>{key}</span>
            </Button>
          ))}
        </div>
        <div
          style={{
            fontSize: '11.5px',
            color: 'var(--acd)',
            fontWeight: 600,
            backgroundColor: 'var(--soft)',
            padding: '4px 10px',
            borderRadius: '12px',
          }}
        >
          {currentArch.badge}
        </div>
      </div>

      {/* SVG Canvas */}
      <div
        style={{
          width: '100%',
          overflowX: 'auto',
          backgroundColor: '#fbf9f4',
          border: '1px solid var(--bd)',
          borderRadius: '8px',
          padding: '20px',
        }}
      >
        <svg
          width={currentArch.canvasWidth}
          height={currentArch.canvasHeight}
          viewBox={`0 0 ${currentArch.canvasWidth} ${currentArch.canvasHeight}`}
          style={{ display: 'block', margin: '0 auto' }}
        >
          <defs>
            <marker id="marker-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--mu)" />
            </marker>
          </defs>

          {/* Relationship connecting lines */}
          {currentArch.relationships.map((rel) => {
            const from = currentArch.tables.find((t) => t.id === rel.fromTable);
            const to = currentArch.tables.find((t) => t.id === rel.toTable);
            if (!from || !to) return null;

            const x1 = from.x + from.width / 2;
            const y1 = from.y + from.height / 2;
            const x2 = to.x + to.width / 2;
            const y2 = to.y + to.height / 2;

            const isHighlighted = selectedTableId === rel.fromTable || selectedTableId === rel.toTable;
            const strokeColor = isHighlighted ? 'var(--acd)' : 'var(--bd)';
            const strokeWidth = isHighlighted ? 2.5 : 1.5;

            return (
              <g key={rel.id}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={rel.type === 'outrigger' ? '4 4' : 'none'}
                  markerEnd="url(#marker-arrow)"
                />
                <circle cx={(x1 + x2) / 2} cy={(y1 + y2) / 2} r="10" fill="#fff" stroke={strokeColor} strokeWidth="1.5" />
                <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 + 3} textAnchor="middle" fontSize="9" fontWeight="bold" fill="var(--mu)">
                  1:N
                </text>
              </g>
            );
          })}

          {/* Tables */}
          {currentArch.tables.map((tbl) => {
            const isFact = tbl.classification === 'fact';
            const isSelected = selectedTableId === tbl.id;
            const headerBg = isFact ? 'var(--acd)' : tbl.classification === 'conformed_dim' ? '#6b8fa3' : '#b0a894';

            return (
              <g
                key={tbl.id}
                transform={`translate(${tbl.x}, ${tbl.y})`}
                onClick={() => setSelectedTableId(tbl.id === selectedTableId ? null : tbl.id)}
                style={{ cursor: 'pointer' }}
              >
                {/* Table box shadow & border */}
                <rect
                  width={tbl.width}
                  height={tbl.height}
                  rx="6"
                  fill="#fff"
                  stroke={isSelected ? 'var(--acd)' : 'var(--bd)'}
                  strokeWidth={isSelected ? 2.5 : 1}
                  filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.04))"
                />

                {/* Table Header */}
                <rect width={tbl.width} height="32" rx="6" fill={headerBg} />
                <rect y="26" width={tbl.width} height="6" fill={headerBg} />
                <text x="12" y="20" fill="#fff" fontSize="12" fontWeight="bold">
                  {tbl.name}
                </text>
                <text x={tbl.width - 12} y="20" textAnchor="end" fill="#fff" fontSize="9.5" opacity="0.85">
                  {isFact ? 'FACT' : 'DIM'}
                </text>

                {/* Columns List */}
                {tbl.columns.slice(0, 7).map((col, cIdx) => (
                  <g key={cIdx} transform={`translate(10, ${48 + cIdx * 20})`}>
                    {col.isPk && (
                      <circle cx="5" cy="-4" r="3" fill="#c2a649" />
                    )}
                    {col.isFk && (
                      <circle cx="5" cy="-4" r="3" fill="#6b8fa3" />
                    )}
                    {col.isMeasure && (
                      <circle cx="5" cy="-4" r="3" fill="var(--acd)" />
                    )}
                    <text x="16" y="0" fontSize="11" fill="var(--tx)">
                      {col.name}
                    </text>
                    <text x={tbl.width - 24} y="0" textAnchor="end" fontSize="9.5" fill="var(--mu)">
                      {col.type}
                    </text>
                  </g>
                ))}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Table Inspector */}
      {selectedTable && (
        <div
          style={{
            backgroundColor: 'var(--card)',
            border: '1px solid var(--bd)',
            borderRadius: '8px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4 style={{ margin: 0, fontSize: '14px', fontWeight: 700, color: 'var(--tx)' }}>
              Entity Inspector: {selectedTable.name}
            </h4>
            <span style={{ fontSize: '11px', color: 'var(--mu)' }}>{selectedTable.role}</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {selectedTable.columns.map((c, i) => (
              <span
                key={i}
                style={{
                  fontSize: '11.5px',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  backgroundColor: c.isPk ? '#fcf3cf' : c.isFk ? '#ebf5fb' : c.isMeasure ? 'var(--soft)' : '#fff',
                  border: '1px solid var(--bd)',
                  color: 'var(--tx)',
                }}
              >
                {c.isPk && '🔑 '}
                {c.isFk && '🔗 '}
                {c.isMeasure && '📊 '}
                {c.name} ({c.type})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Architectural Overview & Tradeoffs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="chart-card-standalone">
          <h4 className="chart-header-title">Architectural Advantages</h4>
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12.5px', color: 'var(--tx)', lineHeight: 1.6 }}>
            {currentArch.advantages.map((adv, i) => (
              <li key={i}>{adv}</li>
            ))}
          </ul>
        </div>
        <div className="chart-card-standalone">
          <h4 className="chart-header-title">Design Tradeoffs</h4>
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12.5px', color: 'var(--tx)', lineHeight: 1.6 }}>
            {currentArch.tradeoffs.map((trd, i) => (
              <li key={i}>{trd}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SchemaDiagram;

