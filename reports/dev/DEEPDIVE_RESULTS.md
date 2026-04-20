# Deep-Dive Analysis Results — Milestone 3 Extended

**Author:** Antoni Czolgowski | **Date:** March 2026 | **Branch:** `antoni-dev-2`

**Prerequisite:** `CLASSIFICATION_RESULTS.md` covers the baseline models (RF, XGBoost, SVM, Misfit Detector). This document extends those findings.

---

## 1. Why Demographic Misfits Are Volatile

**Core question:** Counties that "defy" their demographic predictions — do they also show more electoral volatility?

### Misfit Profiling

Misfits defined as counties with misfit score > 80th percentile (threshold = 0.179). Out of 250 counties: **50 misfits, 200 non-misfits.**

| Demographic | Misfits | Non-Misfits | p-value |
|-------------|---------|-------------|---------|
| Owner-occupied housing | 71.1% | 76.3% | < 0.0001 |
| Bachelor's degree+ | 30.9% | 24.7% | < 0.0001 |
| Racial diversity (entropy) | 0.567 | 0.419 | < 0.0001 |
| Median gross rent | $1,056 | $932 | < 0.0001 |
| % Black | 16.1% | 8.6% | 0.0001 |
| Median age | 42.5 | 44.5 | 0.003 |

**Key insight:** Misfits are younger, more diverse, more educated, more urban, and more transient (lower homeownership). They are places where the electorate is demographically "in flux."

### Two Types of Misfits

| Type | Count (top 30) | Avg Volatility | Where |
|------|----------------|----------------|-------|
| **Surprise Dem** (demographics say Rep, votes Dem) | 8 | **0.807** | MI Upper Peninsula, PA Scranton area |
| **Surprise Rep** (demographics say Dem, votes Rep) | 22 | 0.383 | NC rural South |

**"Surprise Dem" misfits are 2x more volatile** than "Surprise Rep" — university towns and resort communities (Leelanau, Marquette, Lackawanna) that vote against their rural/white demographics are the most electorally unstable counties in the dataset.

### Volatility-Misfit Gradient

Proportion of misfits by volatility class:

| Very Stable | Stable | Moderate | Volatile | Highly Volatile |
|:-----------:|:------:|:--------:|:--------:|:---------------:|
| 6% | 8% | 24% | 28% | **34%** |

Kruskal-Wallis H = 41.54, p < 0.000001. The relationship is monotonic — higher volatility classes contain progressively more misfits.

---

## 2. State-Specific Models — Why Demographics Don't Transfer

**Setup:** Binary XGBoost (High vs Low volatility) trained separately within each state. 5-fold stratified CV.

### Performance

| State | n | AUC | F1 | Top Feature |
|-------|---|-----|----|----|
| PA | 67 | **0.838** | 0.591 (±0.31) | `race_entropy_norm` |
| MI | 83 | 0.778 | 0.636 (±0.16) | `pct_bachelors_plus` |
| NC | 100 | 0.829 | **0.736** (±0.12) | `pct_below_poverty` |

### Each State Has a Different "Volatility Signature"

| PA — Diversity-driven | MI — Education-driven | NC — Poverty-driven |
|-----------------------|----------------------|---------------------|
| 1. `race_entropy_norm` | 1. `pct_bachelors_plus` | 1. `pct_below_poverty` |
| 2. `log_median_gross_rent` | 2. `log_median_gross_rent` | 2. `log_median_gross_rent` |
| 3. `pct_foreign_born` | 3. `pct_work_from_home` | 3. `log_population_density` |
| 4. `pct_two_or_more_races` | 4. `log_median_home_value` | 4. `log_median_home_value` |
| 5. `log_median_household_income` | 5. `pct_senior_65plus` | 5. `pct_bachelors_plus` |

**The only universal predictor: `log_median_gross_rent`** — housing cost appears in every state's top 5. Everything else is state-specific, which directly explains why the LOSO cross-state experiment collapsed to random baseline (F1 = 0.195).

**Implication:** National-level demographic models of electoral behavior are fundamentally limited. The same demographic profile produces different political outcomes depending on state-level political culture, historical voting patterns, and local issues.

---

## 3. SHAP Feature Interactions

**Method:** SHAP interaction values from binary XGBoost (High/Low volatility), computed on all 250 counties.

### Top 6 Interactions

| Rank | Feature Pair | Interaction Strength | Interpretation |
|------|-------------|---------------------|----------------|
| 1 | `race_entropy_norm` × `log_population_density` | **0.133** | Diversity predicts volatility most strongly in urban/suburban areas |
| 2 | `pct_bachelors_plus` × `race_entropy_norm` | 0.091 | Educated + diverse = "emerging suburban" — amplified volatility |
| 3 | `log_total_population` × `log_population_density` | 0.078 | Urban-suburban-rural gradient captures county "type" |
| 4 | `race_entropy_norm` × `log_total_population` | 0.069 | Diversity in large counties matters more |
| 5 | `pct_hs_or_higher` × `race_entropy_norm` | 0.057 | Education × diversity — lower-education diverse areas especially volatile |
| 6 | `pct_foreign_born` × `race_entropy_norm` | 0.052 | Immigration-driven diversity has additional volatility signal |

**`race_entropy_norm` appears in 6 of the top 10 interactions.** It is the "hub" feature — its predictive power is amplified or dampened by urbanization, education, and immigration context. This means racial diversity alone doesn't cause volatility; it's diversity **in combination with** other demographic shifts (urbanization, education sorting) that destabilizes voting patterns.

---

## 4. Binary Classification — High vs Low Volatility

**Setup:** Collapsed 5 quintiles → binary (Q4+Q5 = High, Q1-Q3 = Low). 100 High, 150 Low. 5-fold stratified CV with hyperparameter tuning.

### Model Comparison

| Model | Accuracy | F1 | Precision | Recall | AUC |
|-------|----------|-----|-----------|--------|-----|
| **Random Forest** | **0.772** | **0.708** | 0.726 | 0.690 | **0.827** |
| XGBoost | 0.748 | 0.660 | 0.718 | 0.610 | 0.814 |
| SVM (RBF) | 0.756 | 0.674 | 0.724 | 0.630 | 0.789 |
| Logistic Regression | 0.680 | 0.604 | 0.598 | 0.610 | 0.745 |
| SVM (Linear) | 0.688 | 0.610 | 0.610 | 0.610 | 0.734 |

**Key comparison to 5-class results:**
- Best F1 improved from 0.387 (5-class XGBoost) → **0.708** (binary RF) — nearly doubled
- Best AUC improved from 0.803 → **0.827**
- The middle classes (Q2, Q3) were the primary source of confusion

**SVM kernel flip:** In 5-class, Linear > RBF. In binary, **RBF > Linear** (AUC 0.789 vs 0.734). The High/Low boundary is moderately nonlinear, consistent with the interaction effects found in Section 3.

---

## 5. Campaign Priority Scoring

**Purpose:** Translate analytical findings into actionable resource allocation for campaign strategists.

### Scoring Formula

```
priority = 0.30 × volatility_norm + 0.25 × misfit_norm + 0.25 × vote_volume_norm + 0.20 × margin_closeness_norm
```

Weights reflect campaign logic: volatility (will it swing?) + misfit (is it unpredictable?) + votes (does it matter?) + margin (is it competitive?).

### Top 10 Priority Counties

| Rank | County | State | Priority | Votes | Margin | Volatility Class |
|------|--------|-------|----------|-------|--------|------------------|
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

### State-Level Insights

- **PA:** Bucks County is the #1 target nationally — 800k votes, 0.1% margin, highly volatile. The Philadelphia suburban collar (Bucks, Chester, Montgomery) plus Lehigh Valley (Northampton, Lehigh) are the decisive battleground.
- **MI:** Split between small misfit-driven targets (Leelanau, Marquette — university/resort towns) and large population centers (Macomb, Oakland, Kent). The misfit counties are "early warning" indicators; the population centers deliver the votes.
- **NC:** Cabarrus stands out as the only high-population NC priority. The rest are small rural misfits (Scotland, Nash, Lenoir) — diagnostic of broader Southern realignment patterns but less electorally decisive individually.

---

## 6. Nonlinear Deep-Dives

### 6a. Rent and Volatility — U-Shaped Relationship

Linear correlation is modest (Pearson r = 0.220, Spearman rho = 0.228, both p < 0.001), but the true relationship is **nonlinear**:

- **Low-rent counties** (Q1, <$750): mixed volatility, mostly stable
- **Mid-rent counties** (Q2-Q3, $750-$1100): lowest volatility — the stable suburban core
- **High-rent counties** (Q4, >$1100): most volatile — these are the fast-changing urban fringe and gentrifying areas

The highest-rent counties are overrepresented in *both* the most volatile and most stable quintiles — a U-shape. SHAP dependence plots confirm this nonlinearity.

### 6b. Diversity × Poverty — The Dominant Interaction

| Quadrant | n | Mean Volatility | % High Volatility | % Misfits |
|----------|---|-----------------|-------------------|-----------|
| Low Diversity / Low Poverty | 73 | -0.622 | 19% | 11% |
| Low Diversity / High Poverty | 52 | -0.669 | 23% | 8% |
| **High Diversity / Low Poverty** | **52** | **+0.407** | **60%** | **27%** |
| **High Diversity / High Poverty** | **73** | **+0.808** | **59%** | **33%** |

**This is the clearest finding in the entire analysis:**
- **Diversity is the switch.** Crossing the diversity threshold triples the rate of high volatility (20% → 60%), regardless of poverty level.
- **Poverty adds magnitude but not probability.** High-diversity counties are equally likely to be volatile whether rich or poor, but the *degree* of volatility is higher in poorer diverse counties (mean vol 0.81 vs 0.41).
- The misfit rate follows the same pattern — diverse counties are 3x more likely to be misfits.

### 6c. Education × Urbanization — Volatile at Both Extremes

| Quadrant | n | Mean Volatility | % High Volatility |
|----------|---|-----------------|-------------------|
| Low Education / Rural | 89 | +0.048 | **42%** |
| Low Education / Urban/Suburban | 36 | -0.288 | 19% |
| High Education / Rural | 36 | -0.272 | 33% |
| **High Education / Urban/Suburban** | **89** | **+0.178** | **49%** |

The most volatile quadrants are the **extremes**: low-education rural counties and high-education urban/suburban counties. The *least* volatile are low-education urban (19%) — stable working-class cities with established voting patterns. This suggests volatility is driven by **demographic transition**, not by any single demographic level.

### 6d. SHAP Case Studies — Four Archetypes of Volatility

| County | Archetype | #1 SHAP Driver | Key Insight |
|--------|-----------|----------------|-------------|
| **Bucks, PA** | Suburban swing | `log_median_gross_rent` (+0.85) | High housing cost in large suburban county — classic bellwether |
| **Leelanau, MI** | Demographic misfit | `pct_bachelors_plus` (+1.50) | Highly educated but rural/white — votes Dem against expectations |
| **Scotland, NC** | Diverse-poor rural | `race_entropy_norm` (+1.25) | Highest volatility in dataset — driven by diversity + poverty |
| **Philadelphia, PA** | Urban extreme | `pct_living_alone` (-0.80) | Dense, diverse, but *stable* — solo-living urbanites are consistent voters |

Philadelphia is the critical counter-example: it's extremely diverse and has high poverty, yet it's electorally stable. The SHAP waterfall reveals why — very high `pct_living_alone` and `pct_owner_occupied` (negative) pull it toward stability. Urban density creates voting consistency that overrides the diversity-volatility signal.

---

## Synthesis: What Makes a County Volatile?

### The Volatility Formula (Qualitative)

Electoral volatility emerges from the **interaction** of three factors:

1. **Racial/ethnic diversity** (necessary condition) — `race_entropy_norm` is the #1 predictor and the "hub" feature in interaction analysis. Low-diversity counties are almost never highly volatile.

2. **Economic transition** — captured by `log_median_gross_rent`, `pct_below_poverty`, `pct_bachelors_plus`. Counties where housing costs are rising, education levels are shifting, or poverty is persistent show higher volatility.

3. **Context** (moderating condition) — the same demographics produce different outcomes depending on:
   - **State** (PA: diversity-driven, MI: education-driven, NC: poverty-driven)
   - **Urbanization** (diversity matters more in suburban than rural areas)
   - **Household structure** (married-couple households → stability; living-alone → stability in dense urban areas only)

### What Does NOT Predict Volatility

- **Poverty alone** — Low-diversity poor counties are among the most stable
- **Education alone** — High education predicts volatility only when combined with urbanization
- **Demographics from other states** — Cross-state models fail completely (F1 drops to random baseline)
- **Swing direction** — Misfit score does not correlate with whether a county swings left or right (r = -0.017)

---

## Files Produced (Deep-Dive)

| File | Description |
|------|-------------|
| `notebooks/classification_antoni_deepdive.ipynb` | Deep-dive analysis notebook (30+ code cells) |
| `data/processed/campaign_priority_rankings.csv` | 250 counties with priority scores + all components |
| `docs/images/methods/deepdive_misfit_by_volatility.png` | Misfit score boxplots by volatility class |
| `docs/images/methods/deepdive_state_feature_importance.png` | Per-state top 15 features (3-panel) |
| `docs/images/methods/deepdive_state_roc_curves.png` | State-specific vs pooled ROC curves |
| `docs/images/methods/deepdive_shap_binary_summary.png` | SHAP summary — binary High/Low |
| `docs/images/methods/deepdive_shap_interactions.png` | Top 6 SHAP interaction scatter plots |
| `docs/images/methods/deepdive_interaction_heatmap.png` | 12×12 interaction strength heatmap |
| `docs/images/methods/deepdive_binary_roc_all_models.png` | 5-model ROC comparison (binary) |
| `docs/images/methods/deepdive_binary_confusion_matrices.png` | 5-model confusion matrices |
| `docs/images/methods/deepdive_campaign_priority_scatter.png` | Campaign priority scatter (volatility × misfit) |
| `docs/images/methods/deepdive_rent_volatility.png` | Rent vs volatility (3-panel deep-dive) |
| `docs/images/methods/deepdive_diversity_poverty_interaction.png` | Diversity × poverty quadrant analysis |
| `docs/images/methods/deepdive_education_urbanization.png` | Education × urbanization quadrant analysis |
| `docs/images/methods/deepdive_shap_case_studies.png` | SHAP waterfall — 4 county archetypes |
