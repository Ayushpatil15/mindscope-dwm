import React from 'react';
import LabRunner, { type LabConfig } from '../components/LabRunner';

export const LAB_CONFIGS: Record<number, LabConfig> = {
  1: {
    number: 1,
    title: 'Data Warehouse Design',
    subtitle: 'Dimensional Modeling: Star, Snowflake & Fact Constellation Schemas',
    description:
      'Design, compare, and execute live analytical queries across Star, Snowflake, and Fact Constellation dimensional architectures backed by the persistent SQLite data warehouse.',
    dataset: 'SQLite Warehouse (5,000 verified student records)',
    special: 'schema',
    theory: `1. Core Dimensional Modeling Concepts:
• Fact Tables: Store numeric, additive, or semi-additive measurements resulting from business events (e.g. fact_survey_response mental_health_score, avg_daily_usage_hours; fact_lifestyle study_hours, sleep_hours). They possess foreign keys pointing to dimension tables.
• Dimension Tables: Provide rich descriptive context ('who, what, where, when, and why') that filter, group, and slice facts (dim_respondent, dim_academic, dim_country, dim_platform, dim_purpose, dim_stress).
• Primary Keys (PK) & Foreign Keys (FK): Dimensions define unique integer surrogate Primary Keys. Fact tables declare matching Foreign Keys, creating strict referential integrity.
• Cardinality (1 : N): Every dimension row associates with zero, one, or many fact records, whereas each fact record refers back to exactly one dimension row.

2. Star Schema Architecture:
• Definition: One central fact table surrounded directly by denormalized dimension tables.
• Joins: Single-hop direct joins between fact_survey_response and each dimension.
• Advantages: Maximum read speed, simple SQL join paths, minimal join overhead in OLAP tools.
• Tradeoffs: Attribute denormalization causes minor dimensional data redundancy.

3. Snowflake Schema Architecture:
• Definition: A normalized variation where selected dimension tables are decomposed into 3NF sub-tables.
• Joins: Multi-hop joins (fact_survey_response → dim_respondent → dim_gender / dim_academic).
• Advantages: Eliminates attribute redundancy and prevents update anomalies in dimensional hierarchies.
• Tradeoffs: Additional JOIN operations increase query latency.

4. Fact Constellation (Galaxy Schema):
• Definition: Multiple fact tables sharing conformed dimensions across distinct business processes.
• Joins: fact_survey_response and fact_lifestyle share conformed dimensions (dim_respondent, dim_country, dim_academic), enabling cross-process drill-across operations.
• Advantages: Models complex multi-process domains without forcing disparate grains into a single monolithic fact table.`,
    params: [
      {
        type: 'select',
        key: 'schema',
        label: 'Dimensional Schema Model',
        options: ['Star Schema', 'Snowflake Schema', 'Fact Constellation Schema'],
        initial: 'Star Schema',
      },
      {
        type: 'select',
        key: 'query',
        label: 'Analytical SQL Target',
        options: ['Platform-wise Mental Health', 'Academic Level vs Sleep', 'Country-wise Lifestyle Measures'],
        initial: 'Platform-wise Mental Health',
      },
    ],
  },

  2: {
    number: 2,
    title: 'OLAP Operations',
    subtitle: 'Multidimensional Aggregation: Roll-up, Drill-down, Slice, Dice, Pivot & CUBE',
    description:
      'Execute parameterized multi-dimensional SQL OLAP queries directly against the SQLite warehouse. Aggregate wellbeing measures across academic tiers, social media platforms, and geographic regions.',
    dataset: 'SQLite OLAP Engine',
    theory: `1. Core OLAP Operations:
• Roll-up: Aggregates granular metrics to higher summary levels (e.g. from specific platforms to platform categories).
• Drill-down: Increases dimensional granularity, revealing fine-grained distributions.
• Slice: Fixes one dimension to a single constant value (e.g. stress_level = 'High') to examine a 2D hyperplane.
• Dice: Defines a subcube by applying range filters across two or more dimensions simultaneously.
• Pivot: Transposes dimension attributes across orthogonal axes for cross-tabulation.
• CUBE & GROUPING SETS: Computes simultaneous aggregates across all 2^N dimensional power-set combinations.
• Drill-across: Queries across multiple fact tables (fact_survey_response and fact_lifestyle) sharing conformed dimensions.`,
    params: [
      {
        type: 'select',
        key: 'operation',
        label: 'OLAP Operation',
        options: ['Roll-up', 'Drill-down', 'Slice', 'Dice', 'Pivot', 'CUBE', 'GROUPING SETS', 'Drill-across'],
        initial: 'Roll-up',
      },
      {
        type: 'select',
        key: 'dimension',
        label: 'Primary Dimension',
        options: ['academic_level', 'platform', 'country', 'gender', 'stress_level'],
        initial: 'academic_level',
      },
      {
        type: 'select',
        key: 'measure',
        label: 'Target Measure',
        options: ['sleep_hours_per_night', 'mental_health_score', 'avg_daily_usage_hours', 'study_hours', 'daily_unlocks'],
        initial: 'sleep_hours_per_night',
      },
      {
        type: 'select',
        key: 'aggregator',
        label: 'Aggregate Function',
        options: ['AVG', 'SUM', 'MIN', 'MAX', 'COUNT'],
        initial: 'AVG',
      },
    ],
  },

  3: {
    number: 3,
    title: 'Data Visualization',
    subtitle: 'Visual Encodings, Distribution Profiling & Variance Analysis',
    description:
      'Map student behavioral dimensions to visual encodings for comparative distribution analysis, grouped variance, and outlier detection.',
    dataset: '5,000 Student Records',
    theory: `1. Visual Encodings:
• Bar Charts: Optimal for discrete categorical comparison with baseline at zero.
• Histograms: Continuous frequency partitioning into equal-width bins for skewness evaluation.
• Boxplots: Robust 5-number summary (Min, Q1, Median, Q3, Max) with IQR outlier boundaries (1.5 × IQR).
• Scatter Plots: Bivariate continuous co-variation revealing positive/negative linear and non-linear associations.
• Line Charts: Trend progressions across ordered dimensional tiers.`,
    params: [
      {
        type: 'select',
        key: 'chart',
        label: 'Chart Type',
        options: ['Bar', 'Pie', 'Line', 'Histogram', 'Box', 'Scatter', 'Heatmap'],
        initial: 'Bar',
      },
      {
        type: 'select',
        key: 'x',
        label: 'X Dimension Column',
        options: ['academic_level', 'platform', 'country', 'gender', 'stress_level'],
        initial: 'academic_level',
      },
      {
        type: 'select',
        key: 'y',
        label: 'Y Measure Column',
        options: ['mental_health_score', 'avg_daily_usage_hours', 'sleep_hours_per_night'],
        initial: 'mental_health_score',
      },
    ],
  },

  4: {
    number: 4,
    title: 'Linear Regression',
    subtitle: 'Predictive Modeling of Continuous Mental Health Score & Residual Analysis',
    description:
      'Evaluate linear and multiple regression models predicting student mental wellbeing scores. Analyze slope coefficients, residuals, MAE, RMSE, and explanatory power (R²).',
    dataset: '5,000 Ingested Records',
    theory: `1. Linear Regression Fundamentals:
• Equation: y = β₀ + β₁·x₁ + ... + β_k·x_k + ε, where y is Mental_Health_Score.
• Ordinary Least Squares (OLS) minimizes residual sum of squares: ∑(y_i - ŷ_i)².
• Negative coefficient confirms that each additional hour of social media reduces mental health by approximately 0.32 points.

2. Model Diagnostics:
• R² (Coefficient of Determination): Proportion of variance explained by the model.
• MAE (Mean Absolute Error) & RMSE (Root Mean Squared Error): Measure average magnitude of prediction errors.`,
    params: [
      {
        type: 'select',
        key: 'type',
        label: 'Regression Architecture',
        options: ['Simple', 'Multiple'],
        initial: 'Multiple',
      },
      {
        type: 'range',
        key: 'test',
        label: 'Holdout Test Split Ratio',
        min: 0.1,
        max: 0.4,
        step: 0.05,
        initial: 0.2,
      },
    ],
  },

  5: {
    number: 5,
    title: 'Attribute Relevance + Decision Tree',
    subtitle: 'Mutual Information Attribute Ranking & Interactive Tree Induction',
    description:
      'Measure dependency between attributes and mental wellbeing using Mutual Information, then recursively train an interactive decision tree classifier.',
    dataset: '4,000 Train / 1,000 Test Records',
    special: 'tree',
    theory: `1. Decision Tree Splitting Criteria:
• Mutual Information: Quantifies information shared between each feature and the target class: I(X; Y) = ∑∑ p(x,y) log(p(x,y) / (p(x)p(y))).
• Information Gain / Entropy: Gain(D, A) = Entropy(D) - ∑((|D_v| / |D|) · Entropy(D_v)).
• Recursive Partitioning: At each internal node, the feature and split threshold yielding maximum impurity reduction is selected.

2. Tree Pruning & Regularization:
• Maximum Depth constraints prevent excessive leaf branching and guard against training variance overfitting.`,
    params: [
      {
        type: 'range',
        key: 'depth',
        label: 'Maximum Tree Depth',
        min: 2,
        max: 8,
        step: 1,
        initial: 4,
      },
    ],
  },

  6: {
    number: 6,
    title: 'Naive Bayes',
    subtitle: 'Probabilistic Classification & Multi-Algorithm Benchmarks',
    description:
      'Train a Gaussian Naive Bayes classifier on student behavioral indicators. Inspect class prior probabilities, confusion matrix heatmaps, and compare against Tree, Forest, and Logistic baselines.',
    dataset: 'Stratified 80/20 Holdout Split',
    special: 'confusion',
    theory: `1. Naive Bayes Probabilistic Foundations:
• Bayes Theorem: P(C | X) = [P(C) · ∏ P(x_i | C)] / P(X).
• Conditional Independence Assumption: Assumes features x_i are conditionally independent given class C.
• Gaussian Likelihood: Continuous features are modeled via normal distribution: P(x_i | C) = (1 / √(2πσ_c²)) exp(-(x_i - μ_c)² / (2σ_c²)).

2. Evaluation Metrics:
• Precision = TP / (TP + FP)
• Recall = TP / (TP + FN)
• Macro F1-Score = harmonic mean of precision and recall averaged unweighted across all classes.`,
    params: [
      {
        type: 'range',
        key: 'test',
        label: 'Holdout Test Split Ratio',
        min: 0.1,
        max: 0.4,
        step: 0.05,
        initial: 0.2,
      },
    ],
  },

  7: {
    number: 7,
    title: 'K-Means (Student DWM)',
    subtitle: 'Unsupervised Behavioral Partitioning via K-Means & PCA Projection',
    description:
      'Partition student lifestyle and digital habits into k clusters by minimizing within-cluster inertia. Visualize 2D PCA cluster projections and inspect centroid profiles.',
    dataset: '5,000 Standardized Student Profiles',
    special: 'cluster',
    theory: `1. K-Means Algorithm:
• Objective: Minimizes within-cluster sum of squares (Inertia): ∑∑||x - μ_k||².
• Centroid Initialization: Uses k-means++ to seed centroids far apart, speeding convergence.
• Convergence: Alternates between assignment step (nearest centroid) and update step (mean recalculation).

2. Cluster Validation:
• Silhouette Score: s = (b - a) / max(a, b), ranging from -1 to +1. High scores confirm dense, well-separated clusters.
• PCA Projection: Projects 5-dimensional standardized space onto 2 principal orthogonal axes for visual inspection.`,
    params: [
      {
        type: 'range',
        key: 'k',
        label: 'Number of Clusters (k)',
        min: 2,
        max: 8,
        step: 1,
        initial: 3,
      },
    ],
  },

  8: {
    number: 8,
    title: 'Agglomerative Clustering',
    subtitle: 'Bottom-Up Hierarchical Clustering with Linkage Criteria & Dendrogram',
    description:
      'Build a bottom-up hierarchical clustering tree on student lifestyle attributes. Compare Ward, Complete, Average, and Single linkage criteria, inspect the dendrogram, and evaluate Adjusted Rand Index (ARI) against K-Means.',
    dataset: '5,000 Student Profiles',
    special: 'dendrogram',
    theory: `1. Agglomerative Hierarchical Clustering:
• Bottom-Up Merge: Begins with N single-element clusters and iteratively merges the closest pair.
• Linkage Criteria:
  - Ward: Minimizes total within-cluster variance increase (leads to compact, spherical clusters).
  - Complete: Maximum pairwise distance between elements in two clusters.
  - Average: Average pairwise distance between all elements.
  - Single: Minimum pairwise distance (susceptible to chaining artifacts).

2. Dendrogram & Validation:
• Dendrogram: Visual tree illustrating merge distances; horizontal cutting yields k discrete clusters.
• Adjusted Rand Index (ARI): Measures partition similarity between Hierarchical and K-Means clustering (-1 to +1, where 1.0 represents identical cluster labels).`,
    params: [
      {
        type: 'select',
        key: 'linkage',
        label: 'Linkage Criterion',
        options: ['Ward', 'Complete', 'Average', 'Single'],
        initial: 'Ward',
      },
      {
        type: 'range',
        key: 'clusters',
        label: 'Number of Clusters (k)',
        min: 2,
        max: 8,
        step: 1,
        initial: 3,
      },
    ],
  },

  9: {
    number: 9,
    title: 'Apriori',
    subtitle: 'Frequent Itemsets, Association Rules & Behavior Affinity Network',
    description:
      'Mine frequent itemsets and high-lift association rules using downward closure. Discover strong directional patterns linking platform selection, screen time tiers, and elevated stress levels.',
    dataset: '5,000 Discretized Student Transactions',
    special: 'network',
    theory: `1. Apriori Principle:
• Downward Closure Property: Any subset of a frequent itemset must also be frequent.
• Support: P(A ∩ B) = Count(A ∩ B) / N.
• Confidence: P(B | A) = Support(A ∪ B) / Support(A).
• Lift: P(A ∩ B) / (P(A) · P(B)). Lift > 1 indicates positive dependence; Lift = 1 indicates independence.

2. Association Network Graphs:
• Nodes represent behavioral items (e.g. Platform=Instagram, Usage=High, Sleep=Low).
• Directed edges represent rules with stroke width weighted by Lift factor.`,
    params: [
      {
        type: 'range',
        key: 'support',
        label: 'Minimum Support Threshold',
        min: 0.05,
        max: 0.3,
        step: 0.05,
        initial: 0.1,
      },
      {
        type: 'range',
        key: 'confidence',
        label: 'Minimum Confidence Threshold',
        min: 0.4,
        max: 0.9,
        step: 0.05,
        initial: 0.6,
      },
    ],
  },

  10: {
    number: 10,
    title: 'Lab 10: Integrated Data Mining Pipeline',
    subtitle: 'End-to-End CRISP-DM Workflow: Preprocess -> Classify -> Cluster -> Associate',
    description:
      'This laboratory executes a configurable end-to-end data mining workflow on the student mental health dataset, spanning empirical data preprocessing, comparative supervised classification, unsupervised cluster partitioning, and transactional association rule discovery.',
    dataset: '5,000 Student Records',
    special: 'pipeline',
    theory: `1. CRISP-DM Architectural Synthesis:
• Stage 1 (Preprocessing): Discretizes continuous numerical features into equal-frequency quantiles ('Low', 'Mid', 'High') and audits missing values.
• Stage 2 (Supervised Classification): Executes 10-fold stratified cross-validation comparing Decision Tree with Gaussian Naive Bayes.
• Stage 3 (Unsupervised Clustering): Generates K-Means centroid profiles characterizing student lifestyle segments.
• Stage 4 (Association Rule Mining): Extracts actionable IF-THEN behavioral implications with Lift > 1.2.`,
    params: [
      {
        type: 'select',
        key: 'step',
        label: 'Pipeline Step',
        options: ['Preprocess', 'Classify', 'Cluster', 'Associate'],
        initial: 'Preprocess',
      },
      {
        type: 'select',
        key: 'classifier',
        label: 'Classification Algorithm',
        options: ['Decision Tree', 'Naive Bayes'],
        initial: 'Decision Tree',
      },
    ],
  },
};

export const LabPageScreen: React.FC<{
  labNumber?: number;
}> = ({ labNumber = 1 }) => {
  const config = LAB_CONFIGS[labNumber] || LAB_CONFIGS[1];
  return <LabRunner key={config.number} config={config} />;
};

export default LabPageScreen;
