import { test, expect } from '@playwright/test';
import * as path from 'path';

const SCREENSHOT_DIR = path.resolve(process.cwd(), '../screenshots');

test.describe('Student DWM Milestone 4.1 Parity & Reconstruction E2E Suite', () => {

  test('1. Navigation Parity — Full 7 Analytics Destinations & 10 Experiments', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 7 Core Analytics Destinations
    const expectedAnalytics = [
      'Executive Dashboard',
      'Data Exploration',
      'Wellbeing Analysis',
      'Market Basket',
      'Student Segmentation',
      'Predictive Modeling',
      'Insights'
    ];
    for (const name of expectedAnalytics) {
      await expect(page.getByRole('button', { name })).toBeVisible();
    }

    // 10 Educational Labs with Aligned Syllabus
    const expectedLabs = [
      'Lab 1 — Data Warehouse Design',
      'Lab 2 — OLAP Operations',
      'Lab 3 — Data Visualization',
      'Lab 4 — Linear Regression',
      'Lab 5 — Decision Tree Induction',
      'Lab 6 — Naive Bayes Classification',
      'Lab 7 — K-Means Clustering',
      'Lab 8 — Agglomerative Clustering',
      'Lab 9 — Apriori Association Rules',
      'Lab 10 — Integrated Mining Pipeline'
    ];
    for (const name of expectedLabs) {
      await expect(page.getByRole('button', { name })).toBeVisible();
    }
  });

  test('2. Executive Dashboard — Metrics & Distribution Charts', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Total Respondents')).toBeVisible();
    await expect(page.locator('.metric-card-value').filter({ hasText: '5,000' }).first()).toBeVisible();
    await expect(page.getByText('Avg Mental Health')).toBeVisible();

    await expect(page.getByText('Stress Level Distribution')).toBeVisible();
    await expect(page.getByText('Platform Usage Breakdown')).toBeVisible();
    await expect(page.getByText('Academic Level Wellbeing')).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '1_dashboard.png'), fullPage: true });
  });

  test('3. Data Exploration — DMart Parity Overview, Filters, Statistics & SQL Lab', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Data Exploration' }).click();
    await page.waitForTimeout(600);

    // Verify Overview KPI Cards
    await expect(page.getByText('Rows', { exact: true })).toBeVisible();
    await expect(page.getByText('5,000').first()).toBeVisible();
    await expect(page.getByText('Columns', { exact: true })).toBeVisible();
    await expect(page.getByText('13').first()).toBeVisible();
    await expect(page.getByText('Missing values')).toBeVisible();
    await expect(page.getByText('Duplicate rows')).toBeVisible();

    // Verify Schema Data Types and Descriptive Statistics
    await expect(page.getByRole('heading', { name: 'Schema Data Types' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Descriptive Statistics' })).toBeVisible();

    // Verify Download CSV button
    await expect(page.getByRole('button', { name: /Download CSV/i })).toBeVisible();

    // Verify SQL Query Lab
    await expect(page.getByText('Interactive SQL Query Lab')).toBeVisible();
    const runBtn = page.getByRole('button', { name: /Run Query/i });
    await expect(runBtn).toBeVisible();

    await runBtn.click();
    await page.waitForTimeout(1000);

    await expect(page.getByText(/Executed in/i)).toBeVisible();
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '2_data_exploration.png'), fullPage: true });
  });

  test('4. Wellbeing Analysis & OLAP Studio', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Wellbeing Analysis' }).click();
    await page.waitForTimeout(500);

    await expect(page.getByText('OLAP Studio:')).toBeVisible();
    await expect(page.getByText('Operation:')).toBeVisible();
    await expect(page.getByText('Multidimensional Cross-Tabulation Grid')).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '3_olap_studio.png'), fullPage: true });
  });

  test('5. Market Basket Screen — Apriori Affinity Network', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Market Basket' }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByText('Behavioral Association Mining')).toBeVisible();
    await expect(page.getByText('Apriori Parameters')).toBeVisible();
    await expect(page.getByText('Frequent Itemsets Mined')).toBeVisible();
    await expect(page.getByText('Discovered Association Rules')).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '4_market_basket.png'), fullPage: true });
  });

  test('6. Student Segmentation Screen — K-Means 2D PCA & Centroids', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Student Segmentation' }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByText('Student Behavioral Segmentation')).toBeVisible();
    await expect(page.getByText('Clustering Controls')).toBeVisible();
    await expect(page.getByText('Silhouette Coefficient')).toBeVisible();
    await expect(page.locator('circle').first()).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '5_segmentation.png'), fullPage: true });
  });

  test('7. Predictive Modeling & Ensemble Uncertainty (AC-22)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Predictive Modeling' }).click();
    await page.waitForTimeout(500);

    await expect(page.getByText('Student Profile & Digital Habit Inputs')).toBeVisible();

    const predictBtn = page.getByRole('button', { name: /Predict Wellbeing Score/i });
    await expect(predictBtn).toBeVisible();
    await predictBtn.click();
    await page.waitForTimeout(1000);

    // Verify AC-22 ensemble spread disclosure
    await expect(page.getByText('10th Percentile', { exact: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('90th Percentile', { exact: true })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Ensemble disagreement range/i)).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '6_predictive_modeling.png'), fullPage: true });
  });

  test('8. Automated Insights Screen', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Insights' }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByText('Student Population Insights')).toBeVisible();
    await expect(page.getByText('Evidence-based university counseling actions')).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '7_insights.png'), fullPage: true });
  });

  test('9. Lab 1 — Data Warehouse Design (Star, Snowflake, Constellation)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: /Lab 1 — Data Warehouse/i }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByRole('heading', { name: 'Data Warehouse Design' })).toBeVisible();
    await page.getByRole('button', { name: 'Charts' }).click();
    await page.waitForTimeout(500);

    await expect(page.getByRole('button', { name: 'Star Schema' })).toBeVisible();
    await expect(page.locator('text').filter({ hasText: 'fact_survey_response' }).first()).toBeVisible();

    // Switch to Snowflake Schema
    await page.getByRole('button', { name: 'Snowflake Schema' }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText('dim_gender')).toBeVisible();

    // Switch to Fact Constellation Schema
    await page.getByRole('button', { name: 'Fact Constellation Schema' }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText('fact_lifestyle', { exact: true })).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '8_lab_1_schema.png'), fullPage: true });
  });

  test('10. Lab 2 — OLAP Dynamic Parameter Execution & Stale Result Banner', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: /Lab 2 — OLAP/i }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByRole('heading', { name: 'OLAP Operations' })).toBeVisible();

    // Change Dimension from academic_level to country to trigger modified state
    const dimSelect = page.locator('select').nth(1);
    await dimSelect.selectOption('country');
    await page.waitForTimeout(300);

    // Verify Stale Warning Banner appears
    await expect(page.getByText(/Configuration Modified/i)).toBeVisible();

    // Click Run Experiment
    await page.getByRole('button', { name: 'Run Experiment' }).click();
    await page.waitForTimeout(1000);

    // Stale banner disappears
    await expect(page.getByText(/Configuration Modified/i)).not.toBeVisible();

    // Verify exact metric alias and dimension in Result Grid
    await expect(page.getByText(/OLAP Roll-up Result Grid/i)).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'country' })).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '12_lab_2_olap_parameter_parity.png'), fullPage: true });
  });

  test('11. Lab 8 — Agglomerative Hierarchical Clustering (Dendrogram & Full Cohort)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: /Lab 8 — Agglomerative/i }).click();
    await page.waitForTimeout(1200);

    await expect(page.getByRole('heading', { name: 'Agglomerative Clustering' })).toBeVisible({ timeout: 15000 });

    // Verify Result tab has rich institutional profile table
    await expect(page.getByText(/Agglomerative Cluster Centroids & Institutional Profile/i)).toBeVisible();
    await expect(page.getByText('Institutional Interpretation').first()).toBeVisible();

    // Switch to Charts tab to view Dendrogram
    await page.getByRole('button', { name: 'Charts' }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByText(/Hierarchical Clustering Dendrogram/i)).toBeVisible();
    await expect(page.getByText(/Cut-off Distance Threshold/i)).toBeVisible();

    // Switch to Metrics tab
    await page.getByRole('button', { name: 'Metrics' }).click();
    await page.waitForTimeout(500);
    await expect(page.getByText('ARI vs K-Means')).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '9_lab_8_dendrogram.png'), fullPage: true });
  });

  test('12. Lab 9 — Apriori Association Rules (Network Affinity)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: /Lab 9 — Apriori/i }).click();
    await page.waitForTimeout(1200);

    await expect(page.getByRole('heading', { name: 'Apriori', exact: true })).toBeVisible({ timeout: 15000 });

    // Switch to Charts tab
    await page.getByRole('button', { name: 'Charts' }).click();
    await page.waitForTimeout(1000);

    await expect(page.getByText(/Behavioral Association Affinity Network Graph/i)).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_lab_9_apriori.png'), fullPage: true });
  });

  test('13. Lab 10 — Integrated Data Mining Pipeline (Scoped Stepper & Conditional Classifier)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: /Lab 10 — Integrated Mining/i }).click();
    await page.waitForTimeout(1200);

    await expect(page.getByRole('heading', { name: 'Lab 10: Integrated Data Mining Pipeline' })).toBeVisible({ timeout: 15000 });

    // Verify classifier dropdown is disabled in Preprocess step
    await expect(page.getByText('(Enabled in Step 2: Classify)')).toBeVisible();

    // Verify Preprocess table
    await expect(page.getByText(/Stage 1: Equal-Frequency Quantile Discretization/i)).toBeVisible();

    // Click Stepper Step 2: Classify
    await page.getByText('2. Classify').click();
    await page.waitForTimeout(1500);

    // Verify Supervised classification metrics or table
    await expect(page.getByText(/Stage 2: Supervised Classifier Comparison/i)).toBeVisible();

    // Click Stepper Step 3: Cluster
    await page.getByText('3. Cluster').click();
    await page.waitForTimeout(1500);
    await expect(page.getByText(/Stage 3: Unsupervised Segmentation/i)).toBeVisible();

    // Click Stepper Step 4: Associate
    await page.getByText('4. Associate').click();
    await page.waitForTimeout(1500);
    await expect(page.getByText(/Stage 4: Association Rule Mining/i)).toBeVisible();

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '11_lab_10_pipeline.png'), fullPage: true });
  });

});
