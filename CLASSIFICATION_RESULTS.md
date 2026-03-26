# Classification Results Summary — Milestone 3

**Author:** Antoni Czolgowski | **Date:** March 2026 | **Branch:** `antoni-dev-2`

---

## Dataset

- **250 counties** across PA (67), MI (83), NC (100)
- **28 demographic features** (after log-transforms, multicollinearity drops)
- **Target:** `vol_z_abs_sum` binned into 5 quintiles (50 counties each)
- **No election variables** used as predictors (leakage prevention)

---

## Model Performance (5-Class Volatility Prediction)

| Model | Accuracy | F1-macro | ROC-AUC (binary) | Best at |
|-------|----------|----------|-------------------|---------|
| **XGBoost** | **0.388** | **0.387** | 0.783 | Q3, Q5 — best overall |
| Random Forest | 0.368 | 0.362 | **0.803** | Q1 — best ROC-AUC |
| SVM (Linear) | 0.368 | 0.364 | 0.765 | Q2 — best middle-class separation |
| Logistic (Misfit) | 0.896 | 0.827 | — | Different task: partisan prediction |

**Per-class pattern:** All models best at extremes (Q5: F1=0.57-0.59, Q1: F1=0.42-0.46), weakest at middle classes (Q2: F1=0.18-0.37). This is expected — extreme volatility counties have more distinctive demographic profiles.

---

## Key Findings

### Hypothesis 1: Volatility inversely correlated with wealth — SUPPORTED
- SHAP: `log_median_household_income` vs Q5 SHAP: r = -0.602 (p < 0.0001)
- Higher income pushes counties away from high volatility class
- `pct_below_poverty` is a top-5 predictor across all models

### Hypothesis 2: Racial Diversity Index > individual race features — SUPPORTED
- `race_entropy_norm` ranks **#1 in permutation importance** (RF) and **#2 in SHAP** (XGBoost)
- Beats every individual race variable: entropy mean|SHAP| = 0.397 vs pct_black = 0.347
- Consistent across both RF (Gini + permutation) and XGBoost (SHAP)

### Top Predictors of Electoral Volatility

| Rank | Feature | Why it matters |
|------|---------|----------------|
| 1 | `log_median_gross_rent` | Housing cost — strongest SHAP signal; nonlinear relationship |
| 2 | `race_entropy_norm` | Racial diversity index — higher diversity → higher volatility |
| 3 | `pct_married_couple` | Household structure — married-couple households → stability |
| 4 | `pct_below_poverty` | Poverty rate — top Gini importance; strong poverty→volatility link |
| 5 | `pct_two_or_more_races` | Multiracial population — closely tied to entropy |

### SVM Kernel Comparison: Linear > RBF
- Linear SVM slightly outperforms RBF (F1: 0.364 vs 0.347)
- Implication: the demographic-volatility boundary is approximately **linear** in feature space

---

## Cross-State Generalization — Demographics Do NOT Generalize

| Test State | Train States | Accuracy | F1-macro |
|------------|-------------|----------|----------|
| MI (n=83) | PA + NC | 0.205 | 0.182 |
| NC (n=100) | PA + MI | 0.210 | 0.213 |
| PA (n=67) | MI + NC | 0.209 | 0.189 |

- **Full-CV F1: 0.387 → LOSO avg F1: 0.195** (gap = 0.19)
- Performance drops to **random baseline** (~20%) when predicting across state lines
- **Conclusion:** The same demographics predict volatility differently in each state. State-specific political culture, local issues, and voter registration patterns dominate.

---

## Model D — Demographic Misfit Detector

**Concept:** Predict partisan lean from demographics (LogReg, 89.6% accuracy), then identify counties where prediction errors are largest — "demographic misfits."

### Top 5 Misfits

| County | State | P(Dem) | Actual | Misfit Score | Volatility |
|--------|-------|--------|--------|-------------|------------|
| Leelanau | MI | 0.04 | Dem (+8%) | 0.96 | Highly Volatile |
| Marquette | MI | 0.04 | Dem (+9%) | 0.96 | Highly Volatile |
| Nash | NC | 0.95 | Rep (-2%) | 0.95 | Very Stable |
| Lenoir | NC | 0.94 | Rep (-7%) | 0.94 | Stable |
| Cabarrus | NC | 0.87 | Rep (-8%) | 0.87 | Highly Volatile |

### Cross-Analysis
- **Misfit score correlates with volatility:** Spearman rho = 0.408 (p < 0.001)
- Counties that defy demographic expectations tend to be more electorally volatile
- Misfit score does NOT correlate with swing direction (r = -0.017, n.s.)

### Geographic Patterns
- **NC has the most misfits** — rural Southern counties with mixed demographics voting unexpectedly
- **MI misfits** cluster in Upper Peninsula / northern resort & university towns
- **PA has fewest misfits** — demographics predict voting behavior well in PA

---

## Files Produced

| File | Description |
|------|-------------|
| `notebooks/classification_antoni.ipynb` | Full analysis notebook (43 code cells) |
| `data/processed/classification_dataset_250.csv` | 250 counties, 28 scaled features + targets |
| `data/processed/classification_predictions.csv` | All model predictions + misfit scores |
| `data/processed/rf_predictions.csv` | RF predictions for Sam's clustering comparison |
| `docs/images/methods/choropleth_volatility_class.png` | Predicted volatility map (3 states) |
| `docs/images/methods/choropleth_misfit_score.png` | Misfit score map (3 states) |
| `docs/images/methods/rf_confusion_matrix.png` | RF confusion matrix |
| `docs/images/methods/xgb_confusion_matrix.png` | XGBoost confusion matrix |
| `docs/images/methods/xgb_shap_summary.png` | SHAP feature importance |
| `docs/images/methods/xgb_shap_dependence_top5.png` | SHAP dependence plots |
| `docs/images/methods/per_class_f1_heatmap.png` | Per-class F1 comparison |
| `docs/images/methods/loso_confusion_matrices.png` | Leave-one-state-out results |
| `docs/images/methods/misfit_correlation_matrix.png` | Model D cross-analysis |
| `docs/images/methods/misfit_scatter.png` | P(Dem) vs actual margin scatter |

---

## For Sam — Clustering Comparison

Sam should run k-means on the **same 28 demographic features** from `classification_dataset_250.csv` and return `county_fips, kmeans_cluster_label`. Antoni will compute Adjusted Rand Index to measure alignment between unsupervised clusters and supervised volatility quintiles.
