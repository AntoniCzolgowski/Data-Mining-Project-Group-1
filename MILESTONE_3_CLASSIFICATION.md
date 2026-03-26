# Milestone 3 — Classification of Electoral Volatility

**Author:** Antoni Czolgowski | **Course:** CSCI 5502 Data Mining | **Spring 2026**

---

## Table of Contents

1. [Research Question & Motivation](#1-research-question--motivation)
2. [Dataset & Feature Engineering](#2-dataset--feature-engineering)
3. [Data Formatting for Models](#3-data-formatting-for-models)
4. [Model A — Random Forest](#4-model-a--random-forest)
5. [Model B — XGBoost](#5-model-b--xgboost)
6. [Model C — SVM (Support Vector Machine)](#6-model-c--svm-support-vector-machine)
7. [Model D — Demographic Misfit Detector (Logistic Regression)](#7-model-d--demographic-misfit-detector-logistic-regression)
8. [Binary Classification — High vs Low Volatility](#8-binary-classification--high-vs-low-volatility)
9. [Ensemble Stacking](#9-ensemble-stacking)
10. [Model Comparison & Performance Evaluation](#10-model-comparison--performance-evaluation)
11. [Cross-State Generalization Experiment](#11-cross-state-generalization-experiment)
12. [Hypothesis Testing](#12-hypothesis-testing)
13. [Advanced Analysis — Deep-Dives](#13-advanced-analysis--deep-dives)
14. [Key Findings & Conclusions](#14-key-findings--conclusions)
15. [Figures & Notebooks Produced](#15-figures--notebooks-produced)

---

## 1. Research Question & Motivation

**Can we predict which U.S. counties will be electorally volatile using only demographic data — without any election variables?**

Electoral volatility — the degree to which a county's partisan lean shifts between elections — is critical for campaign resource allocation, political science research, and understanding democratic health. Rather than using past vote totals (which would be trivially predictive), we challenge ourselves: can the *demographic profile* of a county alone tell us whether it will swing?

We study **250 counties** across three presidential battleground states — **Pennsylvania (67)**, **Michigan (83)**, and **North Carolina (100)** — using ACS census data from 2020 and 2024 merged with election returns from 2016, 2020, and 2024.

### Research Hypotheses

1. **H1 — Wealth-Volatility Inverse:** Higher-income counties are less electorally volatile (wealth → stability).
2. **H2 — Diversity Index > Individual Race:** A composite racial diversity index (`race_entropy_norm`, Shannon entropy over 4 racial categories) outperforms any single-race percentage variable as a volatility predictor.

---

## 2. Dataset & Feature Engineering

### 2.1 Source Data

| File | Rows | Description |
|------|------|-------------|
| `master_dataset.csv` | 750 (250 × 3 years) | 39 demographic + election columns per county-year |
| `master_dataset_scaled.csv` | 750 | Contains `race_entropy_norm` (raw 0–1 Shannon entropy) |
| `county_volatility_dimTable.csv` | 250 | Volatility target: `vol_z_abs_sum` (sum of absolute z-scored margin swings across 2016→2020→2024) |

### 2.2 Feature Inventory (28 Demographic Features)

After filtering to 2024 and merging volatility targets, we retain 28 purely demographic features organized into 6 thematic groups:

| Group | Features | Count |
|-------|----------|-------|
| **Race / Ethnicity** | `pct_black`, `pct_asian`, `pct_two_or_more_races`, `pct_hispanic`, `pct_non_hispanic_white`, `race_entropy_norm` | 6 |
| **Urbanization** | `log_total_population`, `log_population_density`, `pct_drive_alone`, `pct_carpool`, `pct_public_transit`, `pct_work_from_home` | 6 |
| **Education** | `pct_hs_or_higher`, `pct_bachelors_plus` | 2 |
| **Housing** | `log_median_gross_rent`, `log_median_home_value`, `pct_owner_occupied` | 3 |
| **Economic** | `log_median_household_income`, `pct_below_poverty`, `pct_income_under_25k`, `pct_income_50k_100k`, `unemployment_rate` | 5 |
| **Household / Age** | `median_age`, `pct_senior_65plus`, `pct_young_adult_18_24`, `pct_foreign_born`, `pct_family_households`, `pct_married_couple`, `pct_living_alone` | 7* |

*Note: `pct_income_over_100k` was dropped due to multicollinearity (r ≈ 0.97 with `log_median_household_income`). `pct_non_hispanic_white` conditionally dropped if |r| > 0.85 with `race_entropy_norm`.*

### 2.3 Target Variable

The target `vol_z_abs_sum` captures total volatility across two election cycles:

```
vol_z_abs_sum = |z(margin_2020 - margin_2016)| + |z(margin_2024 - margin_2020)|
```

This was binned into:
- **5-class quintiles** (50 counties each): Very Stable, Stable, Moderate, Volatile, Highly Volatile
- **Binary** (for advanced models): High (Q4 + Q5, n=100) vs Low (Q1–Q3, n=150)

### 2.4 Leakage Prevention

All election-derived variables (`dem_votes`, `rep_votes`, `total_votes`, `dem_pct`, `rep_pct`, `dem_margin`) are **excluded** from features. Only demographic census variables are used as predictors. The volatility target is derived from election data but does not appear among features.

---

## 3. Data Formatting for Models

### 3.1 Log-Transformation of Skewed Variables

Five heavy-tailed variables received `np.log1p()` transformation to reduce skewness:

| Variable | Skewness Before | Skewness After | Reason |
|----------|:-:|:-:|--------|
| `total_population` | 5.82 | 0.89 | Right-skewed (few very large counties) |
| `population_density` | 4.61 | 0.34 | Extreme urban outliers |
| `median_household_income` | 1.03 | 0.72 | Income distribution tail |
| `median_home_value` | 1.67 | 0.81 | Housing market outliers |
| `median_gross_rent` | 0.98 | 0.54 | Rent distribution tail |

Original columns were replaced with `log_` prefixed versions (e.g., `total_population` → `log_total_population`).

### 3.2 Multicollinearity Removal

Computed pairwise Pearson correlations; dropped features with |r| > 0.85:
- **Dropped:** `pct_income_over_100k` (r = 0.97 with `log_median_household_income`)
- **Conditional:** `pct_non_hispanic_white` dropped if |r| > 0.85 with `race_entropy_norm`

This reduced the feature set from ~29 to **28 features**.

### 3.3 StandardScaler

All 28 features were standardized to zero mean and unit variance using `sklearn.preprocessing.StandardScaler`. This is **required** for:
- **SVM** — distance-based algorithm; unscaled features would dominate based on magnitude
- **Logistic Regression** — convergence and coefficient interpretability
- **Beneficial for:** Random Forest and XGBoost (not required, but ensures fair comparison)

### 3.4 Before-and-After Data Transformation Snapshots

Three transformation snapshots were generated in the notebook:

| Stage | Example: `total_population` | Example: `pct_below_poverty` |
|-------|:--:|:--:|
| **Raw** | mean=126,437; std=237,044; range [2,144 – 1,603,797] | mean=14.8%; std=6.1%; range [4.1% – 35.2%] |
| **After log-transform** | mean=10.8; std=1.2; range [7.7 – 14.3] | (unchanged) |
| **After StandardScale** | mean=0.0; std=1.0; range [-2.6 – 2.9] | mean=0.0; std=1.0; range [-1.8 – 3.3] |

### 3.5 Model-Specific Data Requirements

| Model | Requires Numerical? | Requires Scaling? | Handles Categorical? | Our Approach |
|-------|:---:|:---:|:---:|------|
| Random Forest | No | No | Yes | All features are numerical; scaling applied for consistency |
| XGBoost | No | No | Yes | Labels 0-indexed (`y_xgb = y - 1`); scaling applied for consistency |
| SVM | **Yes** | **Yes** | No | StandardScaler applied; all features already numerical |
| Logistic Regression | **Yes** | **Yes** | No | StandardScaler applied; balanced class weights |

---

## 4. Model A — Random Forest

### Why Random Forest?

- **Non-parametric:** Makes no assumptions about feature distributions — appropriate for our mixed demographic data (percentages, log-transformed counts, entropy indices)
- **Handles nonlinearity:** Can capture complex interactions between demographic features without explicit feature engineering
- **Built-in feature importance:** Gini impurity and permutation importance provide interpretable rankings
- **Robust to noise:** Ensemble of 100+ decision trees reduces variance from our relatively small n=250 dataset
- **No multicollinearity sensitivity:** Unlike logistic regression, RF is robust to correlated features

### Model Assumptions

- Features are informative (at least some demographic variables relate to volatility)
- Training samples are representative of the population
- No assumption of linearity or specific distribution shape
- Assumes bootstrap sampling provides sufficient diversity among trees

### Hyperparameter Tuning

**Method:** Nested cross-validation — outer 5-fold stratified CV for evaluation, inner 3-fold stratified CV for hyperparameter selection via `RandomizedSearchCV` (n_iter=80).

| Hyperparameter | Search Space | Best Value |
|---------------|-------------|-----------|
| `n_estimators` | [100, 200, 300, 500] | 300 |
| `max_depth` | [5, 10, 15, 20, None] | 8 |
| `min_samples_leaf` | [3, 5, 10] | 5 |
| `max_features` | ['sqrt', 'log2', 0.3, 0.5] | 'sqrt' |
| `class_weight` | ['balanced', 'balanced_subsample', None] | 'balanced' |

### 5-Class Performance

| Metric | Value |
|--------|-------|
| Accuracy | 0.368 |
| Precision (macro) | 0.369 |
| Recall (macro) | 0.368 |
| **F1-macro** | **0.362** |
| ROC-AUC (binary High/Low) | **0.803** |

### Per-Class F1 Breakdown

| Very Stable | Stable | Moderate | Volatile | Highly Volatile |
|:-----------:|:------:|:--------:|:--------:|:---------------:|
| 0.46 | 0.18 | 0.28 | 0.30 | 0.59 |

**Interpretation:** RF excels at the extremes — Highly Volatile (F1=0.59) and Very Stable (F1=0.46) counties have more distinctive demographic profiles. The middle classes (Stable, Moderate, Volatile) are harder to separate because their demographics overlap substantially.

### Feature Importance

**Gini (MDI) Importance — Top 10:**

| Rank | Feature | Gini Importance |
|------|---------|:-:|
| 1 | `pct_below_poverty` | 0.065 |
| 2 | `log_median_gross_rent` | 0.063 |
| 3 | `race_entropy_norm` | 0.058 |
| 4 | `pct_married_couple` | 0.055 |
| 5 | `log_median_household_income` | 0.050 |
| 6 | `pct_bachelors_plus` | 0.048 |
| 7 | `pct_two_or_more_races` | 0.045 |
| 8 | `median_age` | 0.042 |
| 9 | `pct_owner_occupied` | 0.041 |
| 10 | `pct_hispanic` | 0.039 |

**Permutation Importance — Top 5** (30 repeats, scoring=f1_macro):

| Rank | Feature | Mean Importance |
|------|---------|:-:|
| 1 | **`race_entropy_norm`** | **#1** |
| 2 | `pct_below_poverty` | #2 |
| 3 | `log_median_gross_rent` | #3 |
| 4 | `pct_married_couple` | #4 |
| 5 | `pct_bachelors_plus` | #5 |

### Challenges & Solutions

- **Class imbalance (5-class):** Addressed with `class_weight='balanced'` which assigns higher penalty to minority classes
- **Overfitting risk (n=250):** Mitigated by limiting `max_depth=8` and requiring `min_samples_leaf=5`, plus nested CV prevents information leakage during tuning
- **Gini vs Permutation disagreement:** Gini overweights high-cardinality continuous features; permutation importance (which is model-agnostic) confirmed `race_entropy_norm` as #1

---

## 5. Model B — XGBoost

### Why XGBoost?

- **Gradient boosting:** Sequentially corrects errors from previous trees — complementary to RF's bagging approach
- **Regularization built-in:** L1/L2 penalties on tree weights help prevent overfitting on small datasets
- **SHAP integration:** `shap.TreeExplainer` provides exact Shapley values for XGBoost, enabling per-county explanations
- **Handles class imbalance:** `scale_pos_weight` parameter and custom objectives
- **State-of-the-art:** Consistently top performer in tabular data competitions

### Model Assumptions

- Boosting improves on residuals from prior iterations
- Features contain sufficient signal (at least weakly informative)
- Sequential additive model assumption: final prediction = sum of weak learners
- Regularization parameters prevent the model from memorizing noise

### Hyperparameter Tuning

**Method:** Nested CV (same structure as RF). `RandomizedSearchCV` with n_iter=100.

| Hyperparameter | Search Space | Best Value |
|---------------|-------------|-----------|
| `n_estimators` | [100, 200, 300, 500] | 300 |
| `max_depth` | [3, 4, 5, 6, 8] | 5 |
| `learning_rate` | [0.01, 0.05, 0.1, 0.2] | 0.1 |
| `subsample` | [0.6, 0.8, 1.0] | 0.8 |
| `colsample_bytree` | [0.6, 0.8, 1.0] | 0.8 |
| `min_child_weight` | [1, 3, 5, 10] | 5 |
| `reg_alpha` | [0, 0.01, 0.1, 1] | 0.1 |
| `reg_lambda` | [1, 5, 10] | 5 |

**Note:** XGBoost requires 0-indexed class labels. We used `y_xgb = y - 1` before fitting and `preds + 1` after prediction.

### 5-Class Performance

| Metric | Value |
|--------|-------|
| Accuracy | **0.388** |
| Precision (macro) | 0.396 |
| Recall (macro) | 0.383 |
| **F1-macro** | **0.387** |
| ROC-AUC (binary High/Low) | 0.783 |

### Per-Class F1 Breakdown

| Very Stable | Stable | Moderate | Volatile | Highly Volatile |
|:-----------:|:------:|:--------:|:--------:|:---------------:|
| 0.42 | 0.37 | 0.30 | 0.28 | 0.57 |

**Interpretation:** XGBoost achieves the **best overall F1-macro (0.387)** in the 5-class task. It particularly outperforms RF on the Stable class (0.37 vs 0.18), suggesting boosting better separates the adjacent classes.

### SHAP Analysis

SHAP (SHapley Additive exPlanations) values decompose each prediction into per-feature contributions.

**SHAP Feature Importance — Top 10** (mean |SHAP| across all counties):

| Rank | Feature | Mean |SHAP| |
|------|---------|:-:|
| 1 | `log_median_gross_rent` | 0.412 |
| 2 | `race_entropy_norm` | 0.397 |
| 3 | `pct_married_couple` | 0.351 |
| 4 | `pct_below_poverty` | 0.329 |
| 5 | `pct_two_or_more_races` | 0.301 |
| 6 | `pct_bachelors_plus` | 0.285 |
| 7 | `log_population_density` | 0.264 |
| 8 | `pct_owner_occupied` | 0.241 |
| 9 | `log_total_population` | 0.230 |
| 10 | `pct_hispanic` | 0.218 |

### SHAP Interaction Effects (from Deep-Dive)

| Rank | Feature Pair | Interaction Strength | Interpretation |
|------|-------------|:-:|------|
| 1 | `race_entropy_norm` × `log_population_density` | **0.133** | Diversity predicts volatility most in suburban/urban areas |
| 2 | `pct_bachelors_plus` × `race_entropy_norm` | 0.091 | Educated + diverse = amplified volatility |
| 3 | `log_total_population` × `log_population_density` | 0.078 | Urban-suburban-rural gradient |
| 4 | `race_entropy_norm` × `log_total_population` | 0.069 | Diversity in large counties matters more |
| 5 | `pct_hs_or_higher` × `race_entropy_norm` | 0.057 | Lower education + diverse = especially volatile |
| 6 | `pct_foreign_born` × `race_entropy_norm` | 0.052 | Immigration-driven diversity amplifies signal |

**`race_entropy_norm` appears in 6 of the top 10 interactions** — it is the "hub" feature whose predictive power is amplified or dampened by urbanization, education, and immigration context.

### Challenges & Solutions

- **0-indexed labels:** XGBoost requires labels starting at 0; handled with explicit `y_xgb = y - 1` transformation
- **SHAP output format:** Newer shap (≥0.42) returns 3D arrays or `Explanation` objects for multiclass; code handles both `list[ndarray]` and `(n, features, classes)` formats
- **Overfitting with boosting:** Mitigated by `subsample=0.8`, `colsample_bytree=0.8`, and regularization (`reg_alpha=0.1`, `reg_lambda=5`)

---

## 6. Model C — SVM (Support Vector Machine)

### Why SVM?

- **Margin-based:** Finds the hyperplane that maximizes separation between volatility classes — good for moderate-dimensional data (28 features)
- **Kernel trick:** Can capture nonlinear decision boundaries (RBF kernel) without explicit feature mapping
- **Theoretically principled:** Structural risk minimization provides generalization guarantees
- **Kernel comparison:** Testing Linear vs RBF reveals whether the demographic-volatility boundary is approximately linear or requires nonlinear modeling

### Model Assumptions

- **Linear kernel:** Assumes classes are approximately linearly separable in feature space (or that soft margin with slack variables suffices)
- **RBF kernel:** Assumes the decision boundary can be captured by Gaussian similarity — data points close in feature space should belong to the same class
- **Requires scaling:** SVM computes distances between data points; features must be on the same scale (StandardScaler applied)
- **All features must be numerical** — satisfied by our pipeline (no categorical variables)

### Hyperparameter Tuning

**Method:** Nested CV. Two separate grids for Linear and RBF kernels.

**Linear SVM:**

| Hyperparameter | Search Space | Best Value |
|---------------|-------------|-----------|
| `C` | [0.01, 0.1, 1, 10, 100] | 1 |
| `class_weight` | ['balanced', None] | 'balanced' |

**RBF SVM:**

| Hyperparameter | Search Space | Best Value |
|---------------|-------------|-----------|
| `C` | [0.01, 0.1, 1, 10, 100] | 10 |
| `gamma` | ['scale', 'auto', 0.01, 0.1, 1] | 'scale' |
| `class_weight` | ['balanced', None] | 'balanced' |

### 5-Class Performance — Kernel Comparison

| Metric | Linear SVM | RBF SVM |
|--------|:-:|:-:|
| Accuracy | **0.368** | 0.340 |
| Precision (macro) | 0.375 | 0.349 |
| Recall (macro) | 0.368 | 0.340 |
| F1-macro | **0.364** | 0.347 |
| ROC-AUC | **0.765** | 0.741 |

**Key finding: Linear > RBF in the 5-class task.** This implies the demographic-volatility boundary is approximately linear in 28-dimensional feature space when distinguishing 5 granular classes.

**However, in binary classification (High vs Low), this reverses:** RBF SVM (F1=0.674, AUC=0.789) outperforms Linear SVM (F1=0.610, AUC=0.734). The High/Low boundary is moderately nonlinear, consistent with the interaction effects found in SHAP analysis.

### Challenges & Solutions

- **No native feature importance:** SVM lacks built-in importance; we relied on RF/XGBoost for feature ranking and used SVM primarily as a performance benchmark
- **Probability calibration:** `SVC(probability=True)` enables Platt scaling for ROC-AUC computation, but adds computational cost
- **Sensitivity to C:** With small n=250, the regularization parameter C significantly affects generalization; nested CV prevents overfitting to a single C value

---

## 7. Model D — Demographic Misfit Detector (Logistic Regression)

### Why Logistic Regression + Residual Analysis?

This is not a direct volatility predictor — it is a **two-stage diagnostic model:**
1. Predict partisan lean (Democrat vs Republican) from demographics
2. Analyze prediction errors to identify counties whose electoral behavior *defies* their demographics

**Motivation:** If a county's demographics say it should vote Republican but it actually votes Democrat (or vice versa), that "misfit" may indicate demographic transition, unique local dynamics, or emerging political realignment — all of which should correlate with volatility.

### Model Assumptions

- **Linear decision boundary** between Democrat and Republican counties in demographic space
- **P(Dem)** is a well-calibrated probability — counties near P=0.5 are genuinely uncertain
- **Residuals are informative** — prediction errors capture demographic-political misalignment, not model deficiency

### Setup

- **Target:** `dem_winner = 1 if dem_margin > 0 else 0` (binary partisan outcome)
- **Features:** Same 28 scaled demographic features
- **Method:** `cross_val_predict(method='predict_proba')` with 5-fold stratified CV produces P(Dem) for every county without data leakage
- **Class weighting:** `class_weight='balanced'` (since Democrat counties are the minority class)

### Performance (Partisan Prediction)

| Metric | Value |
|--------|-------|
| Accuracy | **89.6%** |
| Interpretation | Demographics predict party correctly in 9/10 counties |

### Misfit Score Computation

```
misfit_score = |actual_winner - P(Dem)|
```

Range 0–1. A score of 0.96 means the model was 96% confident the county would vote one way, but it voted the other.

### Top 5 Demographic Misfits

| County | State | P(Dem) | Actual | Misfit Score | Volatility Class |
|--------|:---:|:-:|------|:-:|------|
| **Leelanau** | MI | 0.04 | Dem (+8%) | **0.96** | Highly Volatile |
| **Marquette** | MI | 0.04 | Dem (+9%) | **0.96** | Highly Volatile |
| Nash | NC | 0.95 | Rep (-2%) | 0.95 | Very Stable |
| Lenoir | NC | 0.94 | Rep (-7%) | 0.94 | Stable |
| Cabarrus | NC | 0.87 | Rep (-8%) | 0.87 | Highly Volatile |

**Leelanau and Marquette (MI)** are the biggest misfits — rural, white, low-density counties that "should" vote Republican based on demographics but vote Democrat. They are also both Highly Volatile, confirming the misfit-volatility link.

### Misfit-Volatility Correlation

| Correlation | Value | p-value |
|------------|:-:|:-:|
| Spearman ρ (misfit × volatility) | **0.408** | < 0.001 |
| Pearson r (misfit × swing direction) | -0.017 | n.s. |

**Counties that defy demographic expectations are significantly more volatile.** However, misfit score does NOT predict *which direction* they swing — it captures instability, not partisanship.

### Misfit Profiling (Deep-Dive)

Misfits (top 20%) compared to non-misfits:

| Characteristic | Misfits | Non-Misfits | p-value |
|---------------|:-:|:-:|:-:|
| Racial diversity (entropy) | 0.567 | 0.419 | < 0.0001 |
| Bachelor's degree+ | 30.9% | 24.7% | < 0.0001 |
| Owner-occupied housing | 71.1% | 76.3% | < 0.0001 |
| Median gross rent | $1,056 | $932 | < 0.0001 |
| Median age | 42.5 | 44.5 | 0.003 |

**Misfits are younger, more diverse, more educated, more urban, and more transient** — they are places where the electorate is demographically "in flux."

### Two Types of Misfits

| Type | Count | Avg Volatility | Where |
|------|:-:|:-:|------|
| **Surprise Dem** (predicted Rep, votes Dem) | 8 of top 30 | **0.807** | MI Upper Peninsula, PA Scranton area |
| **Surprise Rep** (predicted Dem, votes Rep) | 22 of top 30 | 0.383 | NC rural South |

**"Surprise Dem" misfits are 2× more volatile** — university towns and resort communities that vote against their rural/white demographics are the most electorally unstable counties in the dataset.

### Challenges & Solutions

- **Different task than Models A–C:** Model D predicts partisanship, not volatility directly; the volatility signal comes from residual analysis
- **Interpretation requires care:** High misfit score means "demographics predict wrong," which could reflect model limitation or genuine political uniqueness — SHAP case studies confirmed the latter

---

## 8. Binary Classification — High vs Low Volatility

### Motivation

The 5-class problem (F1 ≈ 0.39) is limited by middle-class confusion. Collapsing to binary — **High** (Q4+Q5, n=100) vs **Low** (Q1–Q3, n=150) — focuses on the most actionable distinction: "Will this county swing significantly?"

### Model Comparison (Binary)

| Model | Accuracy | F1 | Precision | Recall | AUC |
|-------|:-:|:-:|:-:|:-:|:-:|
| **Random Forest** | **0.780** | **0.718** | 0.726 | 0.690 | **0.828** |
| XGBoost | 0.748 | 0.667 | 0.718 | 0.610 | 0.803 |
| SVM (RBF) | 0.760 | 0.674 | 0.724 | 0.630 | 0.789 |
| Logistic Regression | 0.680 | 0.604 | 0.598 | 0.610 | 0.745 |
| SVM (Linear) | 0.688 | 0.610 | 0.610 | 0.610 | 0.734 |

**Random Forest is the clear winner** in binary classification — F1=0.718 vs next-best XGBoost at 0.667.

### Key Comparison: 5-Class → Binary

| Metric | 5-Class Best | Binary Best | Improvement |
|--------|:-:|:-:|:-:|
| F1 | 0.387 (XGBoost) | **0.718 (RF)** | **+85%** |
| AUC | 0.803 (RF) | **0.828 (RF)** | +3% |

The middle classes (Stable, Moderate) were the primary source of confusion — removing this ambiguity nearly **doubles** F1.

### SVM Kernel Flip

| Task | Better Kernel | AUC |
|------|:---:|:-:|
| 5-class | Linear | 0.765 |
| Binary | **RBF** | **0.789** |

In binary mode, RBF overtakes Linear — the High/Low decision boundary is moderately nonlinear, consistent with the interaction effects identified in SHAP analysis.

### Bootstrap Confidence Intervals (200 iterations × 5-fold CV)

| Model | F1 [95% CI] | AUC [95% CI] | Accuracy [95% CI] |
|-------|:-:|:-:|:-:|
| **Random Forest** | **0.818 [0.764, 0.872]** | **0.918 [0.882, 0.946]** | 0.856 [0.816, 0.900] |
| XGBoost | 0.845 [0.789, 0.899] | 0.932 [0.894, 0.966] | 0.880 [0.840, 0.920] |

Bootstrap CIs are higher than single-CV estimates because resampling with replacement creates some train-test overlap. The CIs confirm performance is **robust and not an artifact of a lucky split**.

---

## 9. Ensemble Stacking

### Motivation

Can combining models improve on the best individual? We tested:

1. **Soft Voting** (RF + XGBoost + SVM-RBF) — averages predicted probabilities
2. **Stacking** (RF + XGBoost + SVM-RBF → Logistic Regression meta-learner) — learns optimal combination

### Results

| Model | Accuracy | F1 | AUC | Type |
|-------|:-:|:-:|:-:|------|
| **Random Forest** | **0.780** | **0.718** | **0.828** | Individual |
| Soft Voting (RF+XGB+SVM) | 0.768 | 0.691 | 0.826 | Ensemble |
| XGBoost | 0.748 | 0.667 | 0.803 | Individual |
| SVM (RBF) | 0.760 | 0.663 | 0.819 | Individual |
| Stacking (LR meta) | 0.760 | 0.647 | 0.816 | Ensemble |
| Logistic Regression | 0.680 | 0.604 | 0.745 | Individual |

### Conclusion

**Ensembles do not beat Random Forest.** Stacking actually *hurts* performance (F1 drops from 0.718 → 0.647) because the Logistic Regression meta-learner oversmooths predictions with only n=250 training samples. The performance bottleneck is **dataset size**, not algorithm sophistication. We have hit the performance ceiling for this sample.

---

## 10. Model Comparison & Performance Evaluation

### 10.1 Complete 5-Class Comparison

| Model | Accuracy | F1-macro | ROC-AUC | Best At |
|-------|:-:|:-:|:-:|------|
| **XGBoost** | **0.388** | **0.387** | 0.783 | Best overall 5-class; best at Q3, Q5 |
| Random Forest | 0.368 | 0.362 | **0.803** | Best ROC-AUC; best at Q1 |
| SVM (Linear) | 0.368 | 0.364 | 0.765 | Best middle-class separation (Q2) |

### 10.2 Complete Binary Comparison (Final Scoreboard)

| Model | Accuracy | F1 | AUC | Type |
|-------|:-:|:-:|:-:|------|
| **Random Forest** | **0.780** | **0.718** | **0.828** | **Best overall** |
| Soft Voting | 0.768 | 0.691 | 0.826 | Ensemble |
| XGBoost | 0.748 | 0.667 | 0.803 | Individual |
| SVM (RBF) | 0.760 | 0.663 | 0.819 | Individual |
| Stacking | 0.760 | 0.647 | 0.816 | Ensemble |
| Logistic Regression | 0.680 | 0.604 | 0.745 | Individual |

### 10.3 Why Random Forest Wins

1. **Bagging advantage:** With n=250, the variance reduction from bootstrapped tree ensembles matters more than boosting's bias reduction
2. **Interaction handling:** RF naturally captures feature interactions (diversity × density, education × urbanization) without explicit specification
3. **Robustness:** RF is less sensitive to hyperparameter choice than XGBoost — it "just works" on small datasets
4. **Class weighting:** `class_weight='balanced'` effectively upweights minority volatility classes

### 10.4 Why XGBoost is Best for 5-Class

1. **Sequential error correction:** Boosting focuses on hard-to-classify middle quintiles where RF struggles
2. **Fine-grained boundaries:** Gradient boosting can find subtle boundaries between adjacent classes
3. **But:** The advantage disappears in binary mode where the boundary is cleaner

### 10.5 Feature Group Ablation — What Matters Most?

| Feature Group | n features | F1 without | F1 drop | F1 alone |
|--------------|:-:|:-:|:-:|:-:|
| **Race / Ethnicity** | 6 | 0.626 | **+0.092** | **0.619** |
| Urbanization | 6 | 0.684 | +0.034 | 0.583 |
| Education | 2 | 0.708 | +0.010 | 0.583 |
| Housing | 3 | 0.712 | +0.006 | 0.612 |
| Economic | 5 | 0.722 | -0.004 | 0.570 |
| Household / Age | 6 | 0.728 | -0.010 | 0.471 |

**Baseline F1 (all features): 0.718**

- **Race/Ethnicity is both necessary AND sufficient** — largest F1 drop when removed (0.092), and alone achieves 0.619 (86% of baseline)
- **Housing alone = 0.612** — nearly as strong solo, confirming rent/home value are independent predictors
- **Economic and Household/Age are dispensable** — removing them slightly *improves* F1, meaning they add noise

---

## 11. Cross-State Generalization Experiment

### Setup

**Leave-One-State-Out (LOSO):** Train on two states, predict the third. Uses the best 5-class model (XGBoost). Critical: StandardScaler is **refit on training states only** to prevent data leakage.

### Results

| Test State | Train States | Accuracy | F1-macro |
|:----------:|:-----------:|:-:|:-:|
| MI (n=83) | PA + NC | 0.205 | 0.182 |
| NC (n=100) | PA + MI | 0.210 | 0.213 |
| PA (n=67) | MI + NC | 0.209 | 0.189 |

### Comparison

| Setup | F1-macro |
|-------|:-:|
| Full 5-fold CV (all states pooled) | 0.387 |
| LOSO average | **0.195** |
| Random baseline (1/5 classes) | 0.200 |

**Performance drops to random baseline when predicting across state lines.** The same demographic profile produces different political outcomes in PA, MI, and NC.

### State-Specific Volatility Signatures (from Deep-Dive)

| PA — Diversity-driven | MI — Education-driven | NC — Poverty-driven |
|:---:|:---:|:---:|
| 1. `race_entropy_norm` | 1. `pct_bachelors_plus` | 1. `pct_below_poverty` |
| 2. `log_median_gross_rent` | 2. `log_median_gross_rent` | 2. `log_median_gross_rent` |
| 3. `pct_foreign_born` | 3. `pct_work_from_home` | 3. `log_population_density` |

**The only universal predictor across all three states: `log_median_gross_rent`** (housing cost). Everything else is state-specific, reflecting distinct political cultures, historical voting patterns, and local economic conditions.

### State-Specific Binary Model Performance

| State | n | AUC | F1 |
|:-----:|:-:|:-:|:-:|
| PA | 67 | 0.838 | 0.591 |
| MI | 83 | 0.778 | 0.636 |
| NC | 100 | **0.829** | **0.736** |

NC achieves the best state-specific F1 — its volatility is most tightly coupled to demographics (poverty-driven mechanism is consistent across the state).

---

## 12. Hypothesis Testing

### H1: Volatility Inversely Correlated with Wealth — CONFIRMED

| Evidence | Method | Value |
|----------|--------|:-:|
| SHAP direction | Q5 SHAP values for `log_median_household_income` | r = **-0.602** (p < 0.0001) |
| Feature importance | `pct_below_poverty` in top 5 all models | Consistent positive association |
| PDP shape | `log_median_gross_rent` | Monotonic increase: higher rent → higher volatility probability |
| Ablation | Economic group alone | F1 = 0.570 (weakest solo group → income alone is insufficient) |

**Higher income pushes counties away from high volatility.** But income alone is not sufficient — it interacts with diversity, education, and urbanization.

### H2: Diversity Index > Individual Race Features — CONFIRMED

| Evidence | Method | Entropy vs Best Individual |
|----------|--------|:-:|
| Permutation importance (RF) | 30 repeats, f1_macro scoring | `race_entropy_norm` = **#1** |
| SHAP importance (XGBoost) | Mean |SHAP| | entropy = 0.397 vs `pct_black` = 0.347 |
| Partial dependence range | PDP range (probability swing) | entropy = **0.14** (largest of all features) |
| Feature ablation | Race group alone F1 | **0.619** (86% of baseline with just 6 race features) |
| Interaction hub | SHAP interactions | entropy in **6 of top 10** interactions |
| Threshold analysis | Maximum-separation + bootstrap | Threshold = 0.552; odds ratio = **7.15×** |

**`race_entropy_norm` is the single most important feature** in the entire analysis. It captures information that no individual race percentage can match — it measures *mixing*, not the share of any group.

---

## 13. Advanced Analysis — Deep-Dives

### 13.1 Temporal Demographic Shifts (2016 → 2024)

**Finding:** It's not just *static* demographics — *demographic change* over 8 years predicts volatility.

| Demographic Change (Δ) | Spearman ρ | p-value (Bonferroni) | Direction |
|------------------------|:-:|:-:|------|
| **Δ pct_hispanic** | **+0.220** | 0.0005 | Growing Hispanic pop → more volatile |
| **Δ median_gross_rent** | **+0.209** | 0.0009 | Rising rents → more volatile |
| **Δ pct_two_or_more_races** | **+0.209** | 0.0009 | Growing multiracial pop → more volatile |
| Δ pct_black | -0.194 | 0.0020 | Growing Black pop → less volatile |

**Diversification (entropy increase) predicts volatility; growth of a single group does not.** This is consistent with the entropy-based findings.

### 13.2 Election Margin Trajectories (2016 → 2020 → 2024)

Four trajectory types classified by margin change direction across two cycles:

| Trajectory | n | Mean Volatility | % High Volatility | Pattern |
|-----------|:-:|:-:|:-:|------|
| **Blue Bounceback** | **117** | -0.17 | 34% | Swung D in 2020, snapped back in 2024 |
| Steady Red Drift | 94 | **+0.39** | **50%** | Moved R in both cycles — most volatile |
| Steady Blue Drift | 35 | -0.28 | 37% | Moved D in both cycles |
| Red Bounceback | 4 | -1.82 | 0% | Swung R in 2020, then D in 2024 — extremely rare |

**Blue Bounceback is dominant** (47%) — the 2020 Biden surge was temporary in most places. **Steady Red Drift is the most volatile** trajectory (50% high volatility).

**NC is different:** 49% of NC counties show Steady Red Drift vs only 27% (PA) and 33% (MI), reflecting ongoing Southern realignment.

### 13.3 The Diversity Threshold — Precisely Estimated

| Metric | Value |
|--------|:-:|
| **Optimal threshold** | **`race_entropy_norm` = 0.552** |
| 95% Bootstrap CI (1000 resamples) | [0.397, 0.642] |
| Below threshold: % high volatility | 24.4% |
| Above threshold: % high volatility | 69.8% |
| **Odds ratio** | **7.15×** |

A `race_entropy_norm` of 0.552 corresponds to a county where no single racial group exceeds ~60% of the population. Counties above this threshold are **7× more likely** to be highly volatile.

The PDP analysis confirms a **step-function** shape: volatility probability jumps from ~20% to ~80% across the threshold zone.

### 13.4 Partial Dependence Analysis

| Feature | Functional Form | Key Insight |
|---------|:-:|------|
| `race_entropy_norm` | **Step function** | Flat → jumps at threshold → plateaus |
| `log_median_gross_rent` | **Monotonic increase** | Higher rent = higher volatility probability |
| `pct_below_poverty` | **Late spike** | Flat until extreme poverty, then jumps |
| `pct_married_couple` | **Flat** | Works via interactions only, not marginal effect |
| `pct_bachelors_plus` | **Slight upward** | Modest increase at high education |
| `log_population_density` | **Uptick at extremes** | Mostly flat; works through interactions |

**2D Interaction Contours:**
- **Diversity × Density:** High volatility zone = high diversity + medium-high density (suburban belt)
- **Education × Diversity:** High volatility zone = high education + high diversity (emerging suburbs)

### 13.5 Nonlinear Deep-Dives

**Diversity × Poverty Interaction — The clearest finding:**

| Quadrant | n | Mean Vol | % High Vol |
|----------|:-:|:-:|:-:|
| Low Diversity / Low Poverty | 73 | -0.622 | 19% |
| Low Diversity / High Poverty | 52 | -0.669 | 23% |
| **High Diversity / Low Poverty** | 52 | **+0.407** | **60%** |
| **High Diversity / High Poverty** | 73 | **+0.808** | **59%** |

**Diversity is the switch** — crossing the diversity threshold triples high-volatility rate (20% → 60%) regardless of poverty. Poverty adds *magnitude* but not *probability*.

**Education × Urbanization — Volatile at both extremes:**

| Quadrant | n | % High Vol |
|----------|:-:|:-:|
| Low Education / Rural | 89 | **42%** |
| Low Education / Urban | 36 | 19% |
| High Education / Rural | 36 | 33% |
| **High Education / Urban** | 89 | **49%** |

The most volatile quadrants are the extremes. The least volatile: low-education urban counties (stable working-class cities with established voting patterns).

### 13.6 SHAP-Based County Archetypes

K-Means clustering on SHAP values (not raw features) reveals 5 functionally distinct county types:

| Cluster | n | % High Vol | Top SHAP Driver | Dominant State | Archetype |
|:-:|:-:|:-:|------|:-:|------|
| 0 | 35 | **100%** | `race_entropy_norm` (1.54) | NC (33/35) | **NC Diverse Rural** |
| 1 | 47 | **0%** | `log_total_population` (0.82) | NC + MI | **Stable Small Counties** |
| 2 | 33 | **91%** | `pct_foreign_born` (0.66) | MI (21/33) | **MI Working-Class Transition** |
| 3 | 92 | **0%** | `race_entropy_norm` (1.07) | All states | **Stable Core** |
| 4 | 43 | **81%** | `log_total_population` (0.92) | PA + NC + MI | **Suburban Battlegrounds** |

**Clusters 0, 1, and 3 show perfect or near-perfect separation** (100% / 0% / 0% high volatility). The model finds clean archetype boundaries in SHAP space.

**This explains why LOSO cross-state prediction fails:** Cluster 0 is almost entirely NC (33/35) and Cluster 2 is MI-heavy (21/33). Their volatility mechanisms are state-specific and don't transfer.

### 13.7 Campaign Priority Scoring

**Formula:**
```
priority = 0.30 × volatility_norm + 0.25 × misfit_norm + 0.25 × vote_volume_norm + 0.20 × margin_closeness_norm
```

**Top 10 Campaign Priority Counties:**

| Rank | County | State | Priority | Total Votes | Margin | Vol. Class |
|:-:|------|:-:|:-:|:-:|:-:|------|
| 1 | **Bucks** | PA | **0.650** | 802,056 | -0.1% | Highly Volatile |
| 2 | Lackawanna | PA | 0.574 | 233,180 | +2.8% | Highly Volatile |
| 3 | Cabarrus | NC | 0.570 | 120,202 | -7.7% | Highly Volatile |
| 4 | Leelanau | MI | 0.566 | 17,685 | +7.8% | Highly Volatile |
| 5 | Scotland | NC | 0.561 | 14,626 | -6.9% | Highly Volatile |
| 6 | Marquette | MI | 0.547 | 39,009 | +8.7% | Highly Volatile |
| 7 | Genesee | MI | 0.514 | 223,268 | +4.2% | Volatile |
| 8 | Monroe | PA | 0.492 | 171,050 | -0.8% | Highly Volatile |
| 9 | Isabella | MI | 0.492 | 30,835 | -7.5% | Volatile |
| 10 | Grand Traverse | MI | 0.484 | 62,772 | -1.7% | Highly Volatile |

**Bucks County, PA** is the #1 target nationally — 800k votes, 0.1% margin, highly volatile. It is the single most electorally decisive county in the three-state dataset.

### 13.8 SHAP Case Studies — Four Archetypes

| County | Archetype | #1 SHAP Driver | Insight |
|--------|------|------|------|
| **Bucks, PA** | Suburban swing | `log_median_gross_rent` (+0.85) | High housing cost in large suburban county = classic bellwether |
| **Leelanau, MI** | Demographic misfit | `pct_bachelors_plus` (+1.50) | Highly educated but rural/white — votes Dem against expectations |
| **Scotland, NC** | Diverse-poor rural | `race_entropy_norm` (+1.25) | Highest volatility — driven by diversity + poverty |
| **Philadelphia, PA** | Urban extreme | `pct_living_alone` (-0.80) | Dense, diverse, but *stable* — solo-living urbanites are consistent voters |

Philadelphia is the critical **counter-example:** extremely diverse and high poverty, yet electorally stable. High `pct_living_alone` and low `pct_owner_occupied` push it toward stability. Urban density creates voting consistency that overrides the diversity-volatility signal.

---

## 14. Key Findings & Conclusions

### The Volatility Formula (Qualitative)

Electoral volatility emerges from the **interaction** of three factors:

1. **Racial/ethnic diversity** (necessary condition) — `race_entropy_norm` is the #1 predictor. Low-diversity counties are almost never highly volatile. The threshold is 0.552 (7× odds ratio).

2. **Economic transition** — captured by `log_median_gross_rent`, `pct_below_poverty`, `pct_bachelors_plus`. Counties where housing costs are rising, education levels are shifting, or poverty is persistent show higher volatility.

3. **Context** (moderating condition) — the same demographics produce different outcomes depending on:
   - **State** (PA: diversity-driven, MI: education-driven, NC: poverty-driven)
   - **Urbanization** (diversity matters more in suburban than rural areas)
   - **Household structure** (married-couple → stability; living-alone → stability in dense urban only)

### What Does NOT Predict Volatility

- **Poverty alone** — low-diversity poor counties are among the most stable
- **Education alone** — only predicts volatility when combined with urbanization
- **Demographics from other states** — cross-state models fail (LOSO F1 = 0.195 ≈ random)
- **Swing direction** — misfit score does not predict left/right (r = -0.017)

### Methodological Conclusions

- **Task framing > algorithms:** Binary classification (F1=0.718) nearly doubles 5-class (F1=0.387). Choosing the right problem formulation matters more than model selection.
- **Ensembles don't help at n=250:** The performance ceiling is dataset size, not algorithm sophistication.
- **National models are fundamentally limited:** State-specific political cultures create distinct volatility mechanisms that don't transfer.
- **SHAP archetypes > feature importance:** Clustering on SHAP values reveals 5 clean county types with near-perfect volatility separation — a richer understanding than any single feature ranking.

### Complete Metrics At-a-Glance

| Finding | Metric | Value |
|---------|--------|:-:|
| Best binary model | RF F1 | **0.718** |
| Best 5-class model | XGBoost F1-macro | **0.387** |
| Bootstrap CI (RF binary) | F1 [95% CI] | 0.818 [0.764, 0.872] |
| Performance ceiling | Ensemble F1 | 0.691 (no improvement) |
| Diversity threshold | `race_entropy_norm` | **0.552 [0.397, 0.642]** |
| Diversity odds ratio | above/below threshold | **7.15×** |
| Most necessary feature group | Race/Ethnicity F1 drop | +0.092 |
| Most sufficient feature group | Race/Ethnicity F1 alone | 0.619 |
| Top temporal predictor | Δ pct_hispanic ρ | +0.220 |
| Most volatile trajectory | Steady Red Drift | 50% high vol |
| Most common trajectory | Blue Bounceback | 117/250 (47%) |
| #1 priority county | Bucks County PA | 802k votes, 0.1% margin |
| SHAP archetype clusters | k=5 | 100%/0%/91%/0%/81% high vol |
| Cross-state generalization | LOSO F1 | 0.195 (= random) |
| H1 (income ↔ volatility) | SHAP correlation | r = -0.602 |
| H2 (entropy > individual race) | Permutation importance | #1 (confirmed) |
| Misfit-volatility link | Spearman ρ | 0.408 (p < 0.001) |
| Partisan prediction accuracy | Logistic Regression | 89.6% |

---

## 15. Figures & Notebooks Produced

### Notebooks

| Notebook | Cells | Description |
|----------|:-:|------|
| `classification_antoni.ipynb` | 86 | Core classification: RF, XGBoost, SVM, Misfit Detector, LOSO, choropleths |
| `classification_antoni_deepdive.ipynb` | 48 | Deep-dive I: misfit profiling, state models, SHAP interactions, binary models, campaign scoring, nonlinear analysis |
| `classification_antoni_deepdive_2.ipynb` | 30 | Deep-dive II: temporal shifts, trajectories, PDPs, bootstrap CIs, ablation, ensembles, threshold estimation, SHAP archetypes |
| `classification_antoni_deepdive_3.ipynb` | 5 | Grand synthesis figure (standalone fix for 6-panel visualization) |

### Data Files

| File | Description |
|------|------|
| `data/processed/classification_dataset_250.csv` | 250 counties, 28 scaled features + targets |
| `data/processed/classification_predictions.csv` | All model predictions + misfit scores |
| `data/processed/rf_predictions.csv` | RF predictions for Sam's clustering comparison |
| `data/processed/campaign_priority_rankings.csv` | 250 counties with priority scores + all components |

### Figures (34 total)

**Core Classification:**
- `rf_confusion_matrix.png` — Random Forest confusion matrix (5-class)
- `rf_gini_importance.png` — RF Gini feature importance bar chart
- `rf_permutation_importance.png` — RF permutation importance bar chart
- `xgb_confusion_matrix.png` — XGBoost confusion matrix (5-class)
- `xgb_shap_summary.png` — SHAP feature importance summary
- `xgb_shap_dependence_top5.png` — SHAP dependence plots for top 5 features
- `svm_confusion_matrix.png` — SVM confusion matrix
- `misfit_correlation_matrix.png` — Model D cross-analysis correlations
- `misfit_scatter.png` — P(Dem) vs actual margin scatter plot
- `loso_confusion_matrices.png` — Leave-one-state-out confusion matrices (3 panels)
- `per_class_f1_heatmap.png` — Per-class F1 comparison across 3 models
- `choropleth_volatility_class.png` — Predicted volatility map (3 states)
- `choropleth_misfit_score.png` — Misfit score map (3 states)

**Deep-Dive I:**
- `deepdive_misfit_by_volatility.png` — Misfit score boxplots by volatility class
- `deepdive_state_feature_importance.png` — Per-state top 15 features (3 panels)
- `deepdive_state_roc_curves.png` — State-specific vs pooled ROC curves
- `deepdive_shap_binary_summary.png` — SHAP summary for binary classification
- `deepdive_shap_interactions.png` — Top 6 SHAP interaction scatter plots
- `deepdive_interaction_heatmap.png` — 12×12 interaction strength heatmap
- `deepdive_binary_roc_all_models.png` — 5-model binary ROC comparison
- `deepdive_binary_confusion_matrices.png` — 5-model binary confusion matrices
- `deepdive_campaign_priority_scatter.png` — Campaign priority scatter (volatility × misfit)
- `deepdive_rent_volatility.png` — Rent vs volatility nonlinear analysis (3 panels)
- `deepdive_diversity_poverty_interaction.png` — Diversity × poverty quadrant analysis
- `deepdive_education_urbanization.png` — Education × urbanization quadrant analysis
- `deepdive_shap_case_studies.png` — SHAP waterfall for 4 county archetypes

**Deep-Dive II & III:**
- `deepdive2_temporal_demographic_shifts.png` — Demographic change correlations + scatter
- `deepdive2_margin_trajectories.png` — Spaghetti trajectories by state (3 panels)
- `deepdive2_partial_dependence.png` — PDPs with ICE + 2D contours + importance
- `deepdive2_feature_ablation.png` — Group ablation + permutation importance with CIs
- `deepdive2_model_scoreboard.png` — Final model comparison dot plot + ROC curves
- `deepdive2_diversity_threshold.png` — Threshold KDE + rolling probability curve
- `deepdive2_shap_archetypes.png` — PCA scatter + state composition + radar charts
- `deepdive2_grand_synthesis.png` — 6-panel grand synthesis figure

---

*All figures saved to `docs/images/methods/`. All notebooks on branch `antoni-dev-2`.*