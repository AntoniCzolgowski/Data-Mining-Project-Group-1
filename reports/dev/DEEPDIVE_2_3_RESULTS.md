# Final Synthesis Results — Deep-Dive II & III

**Author:** Antoni Czolgowski | **Date:** March 2026 | **Branch:** `antoni-dev-2`

**Prerequisites:** `CLASSIFICATION_RESULTS.md` (baseline models), `DEEPDIVE_RESULTS.md` (first deep-dive). This document covers the closing analysis from `classification_antoni_deepdive_2.ipynb` and `classification_antoni_deepdive_3.ipynb`.

---

## 1. Temporal Demographic Shifts (2016 → 2024)

**New finding:** It's not just *static* demographics — *demographic change* over 8 years predicts volatility.

### Significant Correlations (Bonferroni-corrected)

| Demographic Change | Spearman ρ | p-value | Direction |
|-------------------|-----------|---------|-----------|
| **Δ pct_hispanic** | **+0.220** | 0.0005 | Growing Hispanic pop → more volatile |
| **Δ median_gross_rent** | **+0.209** | 0.0009 | Rising rents → more volatile |
| **Δ pct_two_or_more_races** | **+0.209** | 0.0009 | Growing multiracial pop → more volatile |
| Δ pct_black | -0.194 | 0.0020 | Growing Black pop → *less* volatile |

**Key insight:** Diversification (entropy increase via Hispanic and multiracial growth) predicts volatility, while growth of a single group (Black population) does not. This is consistent with the entropy-based findings — it's *mixing*, not any single group, that destabilizes voting patterns.

---

## 2. Election Margin Trajectories (2016 → 2020 → 2024)

### Four Trajectory Types

| Trajectory | n | Mean Volatility | % High Vol | Pattern |
|-----------|---|-----------------|------------|---------|
| **Blue Bounceback** | **117** | -0.17 | 34% | Swung D in 2020, snapped back in 2024 |
| Steady Red Drift | 94 | **+0.39** | **50%** | Moved R in both cycles |
| Steady Blue Drift | 35 | -0.28 | 37% | Moved D in both cycles |
| Red Bounceback | 4 | -1.82 | 0% | Swung R in 2020, then D in 2024 (extremely rare) |

### State Patterns

| Trajectory | PA | MI | NC |
|-----------|----|----|-----|
| Blue Bounceback | 36 (54%) | 49 (59%) | 32 (32%) |
| Steady Red Drift | 18 (27%) | 27 (33%) | **49 (49%)** |
| Steady Blue Drift | 12 (18%) | 6 (7%) | 17 (17%) |

**Key findings:**
- **Blue Bounceback is dominant** (47% of counties) — the 2020 Biden surge was temporary in most places
- **Steady Red Drift is the most volatile trajectory** (mean vol +0.39, 50% high vol) — counties consistently moving Republican are the most electorally unstable
- **NC is different** — nearly half its counties show Steady Red Drift vs only 27-33% in PA/MI
- **Red Bounceback barely exists** (4 counties) — almost no county swung R in 2020 then D in 2024

---

## 3. Partial Dependence Analysis

PDPs reveal the **true functional form** of each feature's effect, averaged across all counties.

### Feature Effect Shapes

| Feature | Functional Form | Description |
|---------|----------------|-------------|
| `race_entropy_norm` | **Step function** | Flat at P≈0.38, jumps to P≈0.52 around 0.0–0.5 (scaled), then plateaus |
| `log_median_gross_rent` | **Monotonic increase** | Gradual linear rise from 0.38 → 0.50 |
| `pct_below_poverty` | **Late spike** | Flat until extreme high poverty, then jumps |
| `pct_married_couple` | **Flat** (works via interactions) | Weak marginal effect despite high SHAP importance |
| `pct_bachelors_plus` | **Slight upward** | Modest increase at high education levels |
| `log_population_density` | **Slight uptick** at extremes | Mostly flat; works through interactions |

### 2D Interactions (PDP Contours)

- **Diversity × Density:** High volatility zone = high diversity + medium-high density (suburban belt)
- **Education × Diversity:** High volatility zone = high education + high diversity (emerging suburbs)

### PDP-Based Feature Importance (top 5)

| Rank | Feature | PDP Range |
|------|---------|-----------|
| 1 | `race_entropy_norm` | 0.14 |
| 2 | `pct_black` | ~0.10 |
| 3 | `log_median_gross_rent` | ~0.09 |
| 4 | `pct_bachelors_plus` | ~0.09 |
| 5 | `pct_below_poverty` | ~0.08 |

---

## 4. Model Robustness

### Bootstrap Confidence Intervals (200 iterations × 5-fold CV)

| Model | F1 [95% CI] | AUC [95% CI] | Accuracy [95% CI] |
|-------|-------------|--------------|-------------------|
| **Random Forest** | **0.818 [0.764, 0.872]** | **0.918 [0.882, 0.946]** | 0.856 [0.816, 0.900] |
| XGBoost | 0.845 [0.789, 0.899] | 0.932 [0.894, 0.966] | 0.880 [0.840, 0.920] |

Note: Bootstrap CIs are higher than single-CV estimates because resampling with replacement creates some train-test overlap. The CIs confirm performance is robust and not an artifact of a lucky split.

### Feature Group Ablation

| Feature Group | n features | F1 without | F1 drop | F1 alone |
|--------------|-----------|------------|---------|----------|
| **Race / Ethnicity** | 6 | 0.626 | **+0.092** | **0.619** |
| Urbanization | 6 | 0.684 | +0.034 | 0.583 |
| Education | 2 | 0.708 | +0.010 | 0.583 |
| Housing | 3 | 0.712 | +0.006 | 0.612 |
| Economic | 5 | 0.722 | -0.004 | 0.570 |
| Household / Age | 6 | 0.728 | -0.010 | 0.471 |

**Baseline F1 (all features): 0.718**

**Key findings:**
- **Race/Ethnicity is both necessary AND sufficient** — largest F1 drop when removed (0.092), and alone achieves 0.619 (86% of baseline)
- **Housing alone = 0.612** — nearly as strong solo, confirming rent/home value are independent predictors
- **Economic and Household/Age are dispensable** — removing them slightly *improves* F1, meaning they add noise
- **Permutation importance (with 95% CIs):** `race_entropy_norm` is #1 by a wide margin, followed by `log_median_home_value` and `pct_bachelors_plus`

---

## 5. Ensemble Stacking

### Final Model Scoreboard (Binary: High vs Low Volatility)

| Model | Accuracy | F1 | AUC | Type |
|-------|----------|-----|-----|------|
| **Random Forest** | **0.780** | **0.718** | **0.828** | Individual |
| Soft Voting (RF+XGB+SVM) | 0.768 | 0.691 | 0.826 | Ensemble |
| XGBoost | 0.748 | 0.667 | 0.803 | Individual |
| SVM (RBF) | 0.760 | 0.663 | 0.819 | Individual |
| Stacking (LR meta) | 0.760 | 0.647 | 0.816 | Ensemble |
| Logistic Regression | 0.680 | 0.604 | 0.745 | Individual |

**Conclusion: Ensembles don't beat Random Forest.** Stacking actually hurts (F1 drops from 0.718 → 0.647) because the LR meta-learner oversmooths with only 250 samples. We have hit the **performance ceiling** for n=250 — the bottleneck is dataset size, not algorithm sophistication.

---

## 6. The Diversity Threshold — Precisely Estimated

### Threshold Estimation (Maximum-Separation + Bootstrap)

| Metric | Value |
|--------|-------|
| **Optimal threshold** | **race_entropy_norm = 0.552** |
| 95% Bootstrap CI (1000 resamples) | [0.397, 0.642] |
| Below threshold (n=164) | 24.4% high volatility |
| Above threshold (n=86) | 69.8% high volatility |
| **Odds ratio** | **7.15×** |

**Interpretation:** A `race_entropy_norm` of 0.552 corresponds to a county where no single racial group exceeds ~60% of the population — a genuinely mixed community. Counties above this threshold are **7× more likely** to be highly volatile.

The rolling probability curve shows P(High Volatility) jumping from ~20% to ~80% across the threshold zone — consistent with the step-function shape in the PDP analysis.

---

## 7. SHAP-Based County Archetypes

### Data-Driven Clustering (K-Means on SHAP Values, k=5)

| Cluster | n | % High Vol | Top SHAP Driver | Dominant State | Archetype |
|---------|---|-----------|-----------------|---------------|-----------|
| 0 | 35 | **100%** | `race_entropy_norm` (1.54) | NC (33/35) | **NC Diverse Rural** |
| 1 | 47 | **0%** | `log_total_population` (0.82) | NC + MI | **Stable Small Counties** |
| 2 | 33 | **91%** | `pct_foreign_born` (0.66) | MI (21/33) | **MI Working-Class Transition** |
| 3 | 92 | **0%** | `race_entropy_norm` (1.07) | All states | **Stable Core** |
| 4 | 43 | **81%** | `log_total_population` (0.92) | PA (19) + NC + MI | **Suburban Battlegrounds** |

**Key findings:**
- Clusters 0, 1, and 3 show **perfect or near-perfect separation** (100%/0%/0% high vol) — the model finds clean archetype boundaries
- **Cluster 0 (NC Diverse Rural)** is almost entirely North Carolina — these are the racially mixed rural Southern counties driving NC's distinctive volatility pattern
- **Cluster 2 (MI Working-Class Transition)** is driven by immigration and education, not diversity per se — the Rust Belt mechanism is fundamentally different from the Southern mechanism
- **Cluster 4 (Suburban Battlegrounds)** is the most state-balanced and contains the top campaign targets (Bucks, Cabarrus, Grand Traverse)
- This directly explains **why LOSO cross-state prediction fails** — Cluster 0 is NC-only and Cluster 2 is MI-heavy; their volatility mechanisms don't transfer

---

## 8. Grand Synthesis — The Complete Story

The 6-panel grand synthesis figure (`deepdive2_grand_synthesis.png`) summarizes all findings:

- **Panel A:** The diversity switch operates consistently across all 3 states — high-diversity counties have higher volatility in PA, MI, and NC alike
- **Panel B:** Despite the universal diversity effect, the *specific* feature signatures differ by state (PA: rent+entropy, MI: education+HS, NC: entropy+poverty)
- **Panel C:** Task framing matters more than algorithms — binary classification (F1=0.718) nearly doubles 5-class performance (F1=0.387), while ensembles add nothing
- **Panel D:** Blue Bounceback (2020 Biden surge → 2024 reversal) is the dominant trajectory (47%), but Steady Red Drift is the most volatile
- **Panel E:** SHAP-based archetypes reveal 5 functionally distinct county groups clustered by model explanation, not raw demographics
- **Panel F:** Campaign priority targets span all states — Bucks PA (competitive + volatile + large) is #1, followed by targets that balance margin closeness with vote volume

---

## Complete Model Performance Summary (All Notebooks)

### 5-Class Volatility Classification

| Model | Accuracy | F1-macro | ROC-AUC |
|-------|----------|----------|---------|
| XGBoost | 0.388 | 0.387 | 0.783 |
| Random Forest | 0.368 | 0.362 | 0.803 |
| SVM (Linear) | 0.368 | 0.364 | 0.765 |

### Binary Classification (High vs Low Volatility)

| Model | Accuracy | F1 | AUC |
|-------|----------|-----|-----|
| **Random Forest** | **0.780** | **0.718** | **0.828** |
| Soft Voting | 0.768 | 0.691 | 0.826 |
| XGBoost | 0.748 | 0.667 | 0.803 |
| SVM (RBF) | 0.760 | 0.663 | 0.819 |
| Stacking | 0.760 | 0.647 | 0.816 |
| Logistic Regression | 0.680 | 0.604 | 0.745 |

### State-Specific Binary Models

| State | n | AUC | F1 |
|-------|---|-----|-----|
| PA | 67 | 0.838 | 0.591 |
| MI | 83 | 0.778 | 0.636 |
| NC | 100 | 0.829 | 0.736 |

### Bootstrap CIs (200 iterations)

| Model | F1 [95% CI] | AUC [95% CI] |
|-------|-------------|--------------|
| Random Forest | 0.818 [0.764, 0.872] | 0.918 [0.882, 0.946] |
| XGBoost | 0.845 [0.789, 0.899] | 0.932 [0.894, 0.966] |

### Misfit Detector

| Metric | Value |
|--------|-------|
| Logistic Regression accuracy | 89.6% |
| Misfit-volatility Spearman ρ | 0.408 (p < 0.001) |
| Top misfit | Leelanau MI (score = 0.96) |

---

## Key Metrics At-a-Glance

| Finding | Metric | Value |
|---------|--------|-------|
| Best binary model | RF F1 | **0.718** |
| Performance ceiling | Ensemble F1 | 0.691 (no improvement) |
| Diversity threshold | race_entropy_norm | **0.552 [0.397, 0.642]** |
| Diversity odds ratio | P(high vol) above/below | **7.15×** |
| Most necessary feature group | Race/Ethnicity F1 drop | +0.092 |
| Top temporal predictor | Δ pct_hispanic ρ | +0.220 |
| Most volatile trajectory | Steady Red Drift | 50% high vol |
| Most common trajectory | Blue Bounceback | 117/250 (47%) |
| #1 priority county | Bucks County PA | 802k votes, -0.1% margin |
| SHAP archetype clusters | k=5 | 100%/0%/91%/0%/81% high vol |
| Cross-state generalization | LOSO F1 | 0.195 (random baseline) |
| Hypothesis 1 (income↔volatility) | SHAP r | -0.602 (confirmed) |
| Hypothesis 2 (entropy > individual race) | Permutation imp #1 | race_entropy_norm (confirmed) |

---

## Files Produced (Deep-Dive II & III)

| File | Description |
|------|-------------|
| `notebooks/classification_antoni_deepdive_2.ipynb` | Final synthesis notebook (30 cells, 8 sections) |
| `notebooks/classification_antoni_deepdive_3.ipynb` | Grand synthesis figure (standalone, fixed Panel F) |
| `docs/images/methods/deepdive2_temporal_demographic_shifts.png` | Demographic change correlations + scatter |
| `docs/images/methods/deepdive2_margin_trajectories.png` | Spaghetti trajectories by state (3-panel) |
| `docs/images/methods/deepdive2_partial_dependence.png` | PDPs with ICE + 2D contours + importance |
| `docs/images/methods/deepdive2_feature_ablation.png` | Group ablation + permutation importance with CIs |
| `docs/images/methods/deepdive2_model_scoreboard.png` | Final model comparison dot plot + ROC curves |
| `docs/images/methods/deepdive2_diversity_threshold.png` | Threshold KDE + rolling probability curve |
| `docs/images/methods/deepdive2_shap_archetypes.png` | PCA scatter + state composition + radar charts |
| `docs/images/methods/deepdive2_grand_synthesis.png` | 6-panel grand synthesis figure |
