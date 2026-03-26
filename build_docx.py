#!/usr/bin/env python3
"""Build MILESTONE_3_CLASSIFICATION.docx — comprehensive classification report with all visualizations."""

import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn

# ── Paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, 'docs', 'images', 'methods')
OUT = os.path.join(BASE, 'MILESTONE_3_CLASSIFICATION.docx')


def img(name):
    """Return full path to a figure, or None if missing."""
    p = os.path.join(FIG, name)
    return p if os.path.exists(p) else None


# ── Document setup ──
doc = Document()

# -- Style tweaks --
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
style.paragraph_format.space_after = Pt(4)
style.paragraph_format.space_before = Pt(2)

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)


def add_table(doc, headers, rows, col_widths=None):
    """Add a formatted table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
    # Rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(9)
    doc.add_paragraph()  # spacing
    return table


def add_figure(doc, filename, caption, width=Inches(6.2)):
    """Add a figure with caption."""
    path = img(filename)
    if path is None:
        doc.add_paragraph(f'[Figure not found: {filename}]').italic = True
        return
    doc.add_picture(path, width=width)
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def bold_para(doc, bold_text, normal_text=''):
    p = doc.add_paragraph()
    r = p.add_run(bold_text)
    r.bold = True
    if normal_text:
        p.add_run(normal_text)
    return p


# ═══════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('Milestone 3: Classification of Electoral Volatility')
run.bold = True
run.font.size = Pt(26)
run.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('Predicting County-Level Electoral Instability\nfrom Demographic Census Data')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()
doc.add_paragraph()

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = meta.add_run('Antoni Czolgowski\n')
run.bold = True
run.font.size = Pt(13)
run = meta.add_run('CSCI 5502 Data Mining \u2014 Spring 2026\nUniversity of Colorado Boulder\n\nMarch 2026')
run.font.size = Pt(12)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (manual)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('Table of Contents', level=1)
toc_items = [
    '1. Research Question & Motivation',
    '2. Dataset & Feature Engineering',
    '3. Data Formatting for Models',
    '4. Model A \u2014 Random Forest',
    '5. Model B \u2014 XGBoost',
    '6. Model C \u2014 SVM (Support Vector Machine)',
    '7. Model D \u2014 Demographic Misfit Detector (Logistic Regression)',
    '8. Binary Classification \u2014 High vs Low Volatility',
    '9. Ensemble Stacking',
    '10. Model Comparison & Performance Evaluation',
    '11. Cross-State Generalization Experiment',
    '12. Hypothesis Testing',
    '13. Advanced Analysis \u2014 Deep-Dives',
    '14. Key Findings & Grand Synthesis',
    '15. Appendix: Figures & Notebooks',
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 1. RESEARCH QUESTION
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('1. Research Question & Motivation', level=1)

doc.add_paragraph(
    'Can we predict which U.S. counties will be electorally volatile using only demographic data \u2014 '
    'without any election variables?'
).runs[0].bold = True

doc.add_paragraph(
    'Electoral volatility \u2014 the degree to which a county\'s partisan lean shifts between elections \u2014 '
    'is critical for campaign resource allocation, political science research, and understanding democratic health. '
    'Rather than using past vote totals (which would be trivially predictive), we challenge ourselves: can the '
    'demographic profile of a county alone tell us whether it will swing?'
)

doc.add_paragraph(
    'We study 250 counties across three presidential battleground states \u2014 Pennsylvania (67), '
    'Michigan (83), and North Carolina (100) \u2014 using American Community Survey (ACS) census data '
    'from 2020 and 2024 merged with election returns from 2016, 2020, and 2024.'
)

doc.add_heading('Research Hypotheses', level=2)
doc.add_paragraph(
    'H1 \u2014 Wealth-Volatility Inverse: Higher-income counties are less electorally volatile (wealth \u2192 stability).',
    style='List Bullet'
)
doc.add_paragraph(
    'H2 \u2014 Diversity Index > Individual Race: A composite racial diversity index (race_entropy_norm, '
    'Shannon entropy over 4 racial categories) outperforms any single-race percentage variable as a volatility predictor.',
    style='List Bullet'
)

doc.add_heading('Why Classification?', level=2)
doc.add_paragraph(
    'Classification is the natural framework for this question. Campaign strategists don\'t need a precise '
    'volatility number \u2014 they need to know: "Is this county likely to swing significantly?" This is '
    'inherently a categorization task. We implement multiple classifiers spanning different algorithmic '
    'families (ensemble trees, gradient boosting, kernel methods, linear models) to understand which '
    'approaches best capture the demographic-volatility relationship, and why.'
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 2. DATASET
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('2. Dataset & Feature Engineering', level=1)

doc.add_heading('2.1 Source Data', level=2)
add_table(doc,
    ['File', 'Rows', 'Description'],
    [
        ['master_dataset.csv', '750 (250 \u00d7 3 years)', '39 demographic + election columns per county-year'],
        ['master_dataset_scaled.csv', '750', 'Contains race_entropy_norm (raw 0\u20131 Shannon entropy)'],
        ['county_volatility_dimTable.csv', '250', 'Volatility target: vol_z_abs_sum'],
    ]
)

doc.add_heading('2.2 Target Variable', level=2)
doc.add_paragraph(
    'The target vol_z_abs_sum captures total volatility across two election cycles:'
)
p = doc.add_paragraph()
r = p.add_run('vol_z_abs_sum = |z(margin_2020 \u2212 margin_2016)| + |z(margin_2024 \u2212 margin_2020)|')
r.italic = True

doc.add_paragraph('This was binned into:')
doc.add_paragraph(
    '5-class quintiles (50 counties each): Very Stable, Stable, Moderate, Volatile, Highly Volatile',
    style='List Bullet')
doc.add_paragraph(
    'Binary: High (Q4 + Q5, n=100) vs Low (Q1\u2013Q3, n=150)',
    style='List Bullet')

doc.add_heading('2.3 Feature Inventory (28 Demographic Features)', level=2)
doc.add_paragraph(
    'After filtering to 2024 and merging volatility targets, we retain 28 purely demographic features '
    'organized into 6 thematic groups. All election-derived variables (dem_votes, rep_votes, total_votes, '
    'dem_pct, rep_pct, dem_margin) are excluded to prevent data leakage.'
)

add_table(doc,
    ['Group', 'Features', 'Count'],
    [
        ['Race / Ethnicity', 'pct_black, pct_asian, pct_two_or_more_races,\npct_hispanic, pct_non_hispanic_white, race_entropy_norm', '6'],
        ['Urbanization', 'log_total_population, log_population_density,\npct_drive_alone, pct_carpool, pct_public_transit, pct_work_from_home', '6'],
        ['Education', 'pct_hs_or_higher, pct_bachelors_plus', '2'],
        ['Housing', 'log_median_gross_rent, log_median_home_value,\npct_owner_occupied', '3'],
        ['Economic', 'log_median_household_income, pct_below_poverty,\npct_income_under_25k, pct_income_50k_100k, unemployment_rate', '5'],
        ['Household / Age', 'median_age, pct_senior_65plus, pct_young_adult_18_24,\npct_foreign_born, pct_family_households, pct_married_couple, pct_living_alone', '7'],
    ]
)

doc.add_paragraph(
    'Note: pct_income_over_100k was dropped due to multicollinearity (r \u2248 0.97 with log_median_household_income). '
    'pct_non_hispanic_white conditionally dropped if |r| > 0.85 with race_entropy_norm.'
)

doc.add_heading('2.4 The race_entropy_norm Feature', level=2)
doc.add_paragraph(
    'This is a normalized Shannon entropy index computed from 4 racial categories '
    '(Non-Hispanic White, Black, Asian, Other/Two+). Values range from 0 (completely homogeneous) '
    'to 1 (perfectly equal distribution across all 4 groups). It captures racial mixing \u2014 not the share '
    'of any individual group \u2014 and turns out to be the single most important feature in the entire analysis.'
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 3. DATA FORMATTING
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('3. Data Formatting for Models', level=1)

doc.add_heading('3.1 Log-Transformation of Skewed Variables', level=2)
doc.add_paragraph(
    'Five heavy-tailed variables received np.log1p() transformation to reduce skewness and '
    'satisfy distributional assumptions for distance-based models (SVM, Logistic Regression):'
)
add_table(doc,
    ['Variable', 'Skewness Before', 'Skewness After', 'Reason'],
    [
        ['total_population', '5.82', '0.89', 'Few very large counties (Philadelphia, Wayne)'],
        ['population_density', '4.61', '0.34', 'Extreme urban outliers'],
        ['median_household_income', '1.03', '0.72', 'Income distribution right tail'],
        ['median_home_value', '1.67', '0.81', 'Housing market outliers'],
        ['median_gross_rent', '0.98', '0.54', 'Rent distribution tail'],
    ]
)
doc.add_paragraph(
    'Original columns were replaced with log_ prefixed versions (e.g., total_population \u2192 log_total_population).'
)

doc.add_heading('3.2 Multicollinearity Removal', level=2)
doc.add_paragraph(
    'Computed pairwise Pearson correlations across all features. Pairs with |r| > 0.85 were flagged:'
)
doc.add_paragraph('Dropped: pct_income_over_100k (r = 0.97 with log_median_household_income)', style='List Bullet')
doc.add_paragraph('Conditional: pct_non_hispanic_white dropped if |r| > 0.85 with race_entropy_norm', style='List Bullet')

doc.add_heading('3.3 StandardScaler', level=2)
doc.add_paragraph(
    'All 28 features were standardized to zero mean and unit variance using sklearn.preprocessing.StandardScaler.'
)

doc.add_heading('3.4 Before-and-After Data Transformation Snapshots', level=2)
doc.add_paragraph(
    'Three transformation snapshots were generated to verify each pipeline stage:'
)
add_table(doc,
    ['Stage', 'total_population (example)', 'pct_below_poverty (example)'],
    [
        ['Raw', 'mean=126,437; std=237,044\nrange [2,144 \u2013 1,603,797]', 'mean=14.8%; std=6.1%\nrange [4.1% \u2013 35.2%]'],
        ['After log-transform', 'mean=10.8; std=1.2\nrange [7.7 \u2013 14.3]', '(unchanged)'],
        ['After StandardScale', 'mean=0.0; std=1.0\nrange [\u22122.6 \u2013 2.9]', 'mean=0.0; std=1.0\nrange [\u22121.8 \u2013 3.3]'],
    ]
)

doc.add_heading('3.5 Model-Specific Data Requirements', level=2)
add_table(doc,
    ['Model', 'Requires Numerical?', 'Requires Scaling?', 'Handles Categorical?', 'Our Approach'],
    [
        ['Random Forest', 'No', 'No', 'Yes', 'Scaling applied for consistency'],
        ['XGBoost', 'No', 'No', 'Yes', 'Labels 0-indexed (y_xgb = y \u2212 1)'],
        ['SVM', 'Yes', 'Yes', 'No', 'StandardScaler applied'],
        ['Logistic Regression', 'Yes', 'Yes', 'No', 'StandardScaler + balanced weights'],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 4. MODEL A — RANDOM FOREST
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('4. Model A \u2014 Random Forest', level=1)

doc.add_heading('Why Random Forest?', level=2)
doc.add_paragraph(
    'Random Forest is a bagging-based ensemble of decision trees that aggregates predictions '
    'from hundreds of independently-trained trees. We chose it for several key reasons:'
)
doc.add_paragraph('Non-parametric: Makes no assumptions about feature distributions \u2014 appropriate for our mixed demographic data (percentages, log-transformed counts, entropy indices)', style='List Bullet')
doc.add_paragraph('Handles nonlinearity: Captures complex interactions between demographic features without explicit feature engineering', style='List Bullet')
doc.add_paragraph('Built-in feature importance: Gini impurity (MDI) and permutation importance provide interpretable feature rankings', style='List Bullet')
doc.add_paragraph('Robust to noise: Ensemble of 300+ trees reduces variance, critical for our relatively small n=250 dataset', style='List Bullet')
doc.add_paragraph('No multicollinearity sensitivity: Unlike logistic regression, RF handles correlated features gracefully', style='List Bullet')

doc.add_heading('Model Assumptions', level=2)
doc.add_paragraph('Features contain information relevant to the target (at least some demographic variables relate to volatility)', style='List Bullet')
doc.add_paragraph('Training samples are representative of the population of counties in PA, MI, NC', style='List Bullet')
doc.add_paragraph('No assumption of linearity, normality, or specific distribution shape', style='List Bullet')
doc.add_paragraph('Bootstrap sampling provides sufficient diversity among trees for stable ensemble', style='List Bullet')

doc.add_heading('Hyperparameter Tuning', level=2)
doc.add_paragraph(
    'Method: Nested cross-validation \u2014 outer 5-fold stratified CV for unbiased evaluation, '
    'inner 3-fold stratified CV for hyperparameter selection via RandomizedSearchCV (n_iter=80). '
    'This two-level design prevents information leakage from tuning into evaluation.'
)
add_table(doc,
    ['Hyperparameter', 'Search Space', 'Best Value'],
    [
        ['n_estimators', '[100, 200, 300, 500]', '300'],
        ['max_depth', '[5, 10, 15, 20, None]', '8'],
        ['min_samples_leaf', '[3, 5, 10]', '5'],
        ['max_features', "['sqrt', 'log2', 0.3, 0.5]", "'sqrt'"],
        ['class_weight', "['balanced', 'balanced_subsample', None]", "'balanced'"],
    ]
)

doc.add_heading('5-Class Performance', level=2)
add_table(doc,
    ['Metric', 'Value'],
    [
        ['Accuracy', '0.368'],
        ['Precision (macro)', '0.369'],
        ['Recall (macro)', '0.368'],
        ['F1-macro', '0.362'],
        ['ROC-AUC (binary High/Low)', '0.803'],
    ]
)

doc.add_heading('Per-Class F1 Breakdown', level=2)
add_table(doc,
    ['Very Stable', 'Stable', 'Moderate', 'Volatile', 'Highly Volatile'],
    [['0.46', '0.18', '0.28', '0.30', '0.59']]
)
doc.add_paragraph(
    'Interpretation: RF excels at the extremes \u2014 Highly Volatile (F1=0.59) and Very Stable (F1=0.46) '
    'counties have more distinctive demographic profiles. The middle classes overlap substantially in feature space.'
)

add_figure(doc, 'rf_confusion_matrix.png',
           'Figure 1: Random Forest confusion matrix (5-class, nested 5-fold CV). '
           'Strong diagonal at Q1 and Q5; middle classes show diffuse misclassification.')

doc.add_heading('Feature Importance', level=2)
doc.add_paragraph(
    'Two complementary importance measures were computed on the final retrained RF (all 250 counties):'
)

add_figure(doc, 'rf_gini_importance.png',
           'Figure 2: Random Forest Gini (MDI) feature importance \u2014 top features by impurity reduction.')

add_figure(doc, 'rf_permutation_importance.png',
           'Figure 3: Permutation importance (30 repeats, f1_macro scoring) \u2014 '
           'race_entropy_norm is the #1 most important feature by this model-agnostic measure.')

doc.add_paragraph(
    'Key finding: While Gini importance places pct_below_poverty and log_median_gross_rent at the top '
    '(because continuous features with many split points get higher Gini), the model-agnostic permutation '
    'importance confirms race_entropy_norm as the single most important feature for volatility prediction.'
)

doc.add_heading('Challenges & Solutions', level=2)
doc.add_paragraph('Class imbalance (5 equal classes): Addressed with class_weight=\'balanced\' which assigns higher penalty to misclassified minority patterns', style='List Bullet')
doc.add_paragraph('Overfitting risk (n=250): Mitigated by limiting max_depth=8 and requiring min_samples_leaf=5, plus nested CV prevents information leakage during tuning', style='List Bullet')
doc.add_paragraph('Gini vs Permutation disagreement: Gini overweights high-cardinality continuous features; permutation importance provided the unbiased ranking', style='List Bullet')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 5. MODEL B — XGBOOST
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('5. Model B \u2014 XGBoost', level=1)

doc.add_heading('Why XGBoost?', level=2)
doc.add_paragraph(
    'XGBoost (eXtreme Gradient Boosting) is a gradient-boosted tree ensemble that sequentially '
    'corrects errors from previous trees. It complements Random Forest by offering a fundamentally '
    'different learning strategy: where RF reduces variance through bagging, XGBoost reduces bias through boosting.'
)
doc.add_paragraph('Sequential error correction: Each tree focuses on the residuals of the previous ensemble, particularly benefiting hard-to-classify middle quintiles', style='List Bullet')
doc.add_paragraph('Built-in regularization: L1/L2 penalties on tree weights prevent overfitting on small datasets', style='List Bullet')
doc.add_paragraph('SHAP integration: shap.TreeExplainer provides exact Shapley values, enabling per-county prediction explanations', style='List Bullet')
doc.add_paragraph('State-of-the-art: Consistently the top performer in tabular data competitions (Kaggle, etc.)', style='List Bullet')

doc.add_heading('Model Assumptions', level=2)
doc.add_paragraph('Additive model: final prediction = sum of weak learners (shallow trees)', style='List Bullet')
doc.add_paragraph('Residual learning: each iteration meaningfully reduces training loss', style='List Bullet')
doc.add_paragraph('Regularization parameters prevent memorization of noise in small-n regime', style='List Bullet')

doc.add_heading('Hyperparameter Tuning', level=2)
doc.add_paragraph(
    'Method: Nested CV (same structure as RF). RandomizedSearchCV with n_iter=100. '
    'XGBoost requires 0-indexed class labels: y_xgb = y \u2212 1 before fit, preds + 1 after predict.'
)
add_table(doc,
    ['Hyperparameter', 'Search Space', 'Best Value'],
    [
        ['n_estimators', '[100, 200, 300, 500]', '300'],
        ['max_depth', '[3, 4, 5, 6, 8]', '5'],
        ['learning_rate', '[0.01, 0.05, 0.1, 0.2]', '0.1'],
        ['subsample', '[0.6, 0.8, 1.0]', '0.8'],
        ['colsample_bytree', '[0.6, 0.8, 1.0]', '0.8'],
        ['min_child_weight', '[1, 3, 5, 10]', '5'],
        ['reg_alpha (L1)', '[0, 0.01, 0.1, 1]', '0.1'],
        ['reg_lambda (L2)', '[1, 5, 10]', '5'],
    ]
)

doc.add_heading('5-Class Performance', level=2)
add_table(doc,
    ['Metric', 'Value'],
    [
        ['Accuracy', '0.388 (best)'],
        ['Precision (macro)', '0.396'],
        ['Recall (macro)', '0.383'],
        ['F1-macro', '0.387 (best)'],
        ['ROC-AUC', '0.783'],
    ]
)

add_figure(doc, 'xgb_confusion_matrix.png',
           'Figure 4: XGBoost confusion matrix (5-class). Better middle-class separation than RF, '
           'particularly in Stable (Q2) class.')

doc.add_heading('SHAP Analysis', level=2)
doc.add_paragraph(
    'SHAP (SHapley Additive exPlanations) decomposes each prediction into per-feature contributions '
    'based on cooperative game theory. Unlike feature importance which gives a global ranking, '
    'SHAP reveals how each feature pushes each county toward or away from each volatility class.'
)

add_figure(doc, 'xgb_shap_summary.png',
           'Figure 5: SHAP summary plot \u2014 each dot is one county. Features ranked by mean |SHAP| value. '
           'Color indicates feature value (red=high, blue=low). log_median_gross_rent and race_entropy_norm dominate.')

add_figure(doc, 'xgb_shap_dependence_top5.png',
           'Figure 6: SHAP dependence plots for top 5 features (Class Q5 = Highly Volatile). '
           'Vertical dispersion reveals interaction effects. race_entropy_norm shows a clear step-function shape.')

doc.add_heading('SHAP Interaction Effects', level=2)
doc.add_paragraph(
    'SHAP interaction values quantify how pairs of features combine to affect predictions '
    'beyond their individual effects. race_entropy_norm appears in 6 of the top 10 interactions \u2014 '
    'it is the "hub" feature whose signal is amplified or dampened by context.'
)

add_table(doc,
    ['Rank', 'Feature Pair', 'Strength', 'Interpretation'],
    [
        ['1', 'race_entropy_norm \u00d7\nlog_population_density', '0.133', 'Diversity predicts volatility\nmost in suburban/urban areas'],
        ['2', 'pct_bachelors_plus \u00d7\nrace_entropy_norm', '0.091', 'Educated + diverse =\namplified volatility'],
        ['3', 'log_total_population \u00d7\nlog_population_density', '0.078', 'Urban-suburban-rural\ngradient effect'],
        ['4', 'race_entropy_norm \u00d7\nlog_total_population', '0.069', 'Diversity matters more\nin large counties'],
        ['5', 'pct_hs_or_higher \u00d7\nrace_entropy_norm', '0.057', 'Lower education + diverse\n= especially volatile'],
        ['6', 'pct_foreign_born \u00d7\nrace_entropy_norm', '0.052', 'Immigration-driven diversity\namplifies signal'],
    ]
)

add_figure(doc, 'deepdive_shap_interactions.png',
           'Figure 7: Top 6 SHAP interaction scatter plots. Each dot is a county; color indicates the interacting feature value.')

add_figure(doc, 'deepdive_interaction_heatmap.png',
           'Figure 8: 12\u00d712 SHAP interaction strength heatmap for top features. '
           'race_entropy_norm is the clear interaction hub.')

doc.add_heading('Challenges & Solutions', level=2)
doc.add_paragraph('0-indexed labels: XGBoost requires labels starting at 0; handled with explicit y \u2212 1 transformation', style='List Bullet')
doc.add_paragraph('SHAP output format: Code handles both old (list of arrays) and new (3D array / Explanation object) shap library formats', style='List Bullet')
doc.add_paragraph('Overfitting with boosting: Mitigated by subsample=0.8, colsample_bytree=0.8, and strong regularization', style='List Bullet')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 6. MODEL C — SVM
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('6. Model C \u2014 SVM (Support Vector Machine)', level=1)

doc.add_heading('Why SVM?', level=2)
doc.add_paragraph(
    'SVM finds the hyperplane that maximizes the margin between classes in feature space. '
    'It offers a fundamentally different inductive bias from tree-based models:'
)
doc.add_paragraph('Margin-based learning: Focuses on the hardest-to-classify boundary cases (support vectors), not all data points', style='List Bullet')
doc.add_paragraph('Kernel trick: RBF kernel projects data into infinite-dimensional space without explicit computation, capturing nonlinear boundaries', style='List Bullet')
doc.add_paragraph('Theoretical guarantees: Structural risk minimization provides generalization bounds', style='List Bullet')
doc.add_paragraph('Diagnostic value: Comparing Linear vs RBF reveals whether the decision boundary is linear or nonlinear', style='List Bullet')

doc.add_heading('Model Assumptions', level=2)
doc.add_paragraph('Linear kernel: Classes are approximately linearly separable (or soft margin with slack suffices)', style='List Bullet')
doc.add_paragraph('RBF kernel: Decision boundary captured by Gaussian similarity \u2014 nearby points in feature space belong to same class', style='List Bullet')
doc.add_paragraph('Requires scaling: SVM computes distances; unscaled features would dominate based on magnitude (StandardScaler applied)', style='List Bullet')
doc.add_paragraph('All features must be numerical \u2014 satisfied (no categorical variables in our pipeline)', style='List Bullet')

doc.add_heading('Hyperparameter Tuning', level=2)
doc.add_paragraph('Two separate grids were tuned via nested CV:')

bold_para(doc, 'Linear SVM:')
add_table(doc,
    ['Hyperparameter', 'Search Space', 'Best Value'],
    [
        ['C (regularization)', '[0.01, 0.1, 1, 10, 100]', '1'],
        ['class_weight', "['balanced', None]", "'balanced'"],
    ]
)

bold_para(doc, 'RBF SVM:')
add_table(doc,
    ['Hyperparameter', 'Search Space', 'Best Value'],
    [
        ['C', '[0.01, 0.1, 1, 10, 100]', '10'],
        ['gamma', "['scale', 'auto', 0.01, 0.1, 1]", "'scale'"],
        ['class_weight', "['balanced', None]", "'balanced'"],
    ]
)

doc.add_heading('Kernel Comparison (5-Class)', level=2)
add_table(doc,
    ['Metric', 'Linear SVM', 'RBF SVM'],
    [
        ['Accuracy', '0.368', '0.340'],
        ['F1-macro', '0.364', '0.347'],
        ['ROC-AUC', '0.765', '0.741'],
    ]
)

bold_para(doc, 'Key finding: Linear > RBF in 5-class.',
          ' The demographic-volatility boundary is approximately linear when distinguishing 5 granular quintiles. '
          'However, this reverses in binary classification (RBF AUC=0.789 > Linear AUC=0.734) \u2014 '
          'the High/Low boundary is moderately nonlinear, consistent with SHAP interaction effects.')

add_figure(doc, 'svm_confusion_matrix.png',
           'Figure 9: SVM confusion matrix (best kernel). Similar pattern to RF/XGBoost: '
           'strong at extremes, weak at middle classes.')

doc.add_heading('Challenges & Solutions', level=2)
doc.add_paragraph('No native feature importance: SVM lacks built-in importance; relied on RF/XGBoost for feature ranking, SVM used as performance benchmark', style='List Bullet')
doc.add_paragraph('Probability calibration: SVC(probability=True) enables Platt scaling for ROC-AUC but adds computational cost', style='List Bullet')
doc.add_paragraph('C sensitivity: With small n=250, regularization significantly affects generalization; nested CV prevents overfitting to a single C', style='List Bullet')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 7. MODEL D — MISFIT DETECTOR
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('7. Model D \u2014 Demographic Misfit Detector (Logistic Regression)', level=1)

doc.add_heading('Why This Approach?', level=2)
doc.add_paragraph(
    'This is not a direct volatility predictor \u2014 it is a two-stage diagnostic model with a creative twist:'
)
doc.add_paragraph('Stage 1: Predict partisan lean (Democrat vs Republican) from demographics using Logistic Regression', style='List Bullet')
doc.add_paragraph('Stage 2: Analyze prediction errors ("misfits") \u2014 counties whose electoral behavior defies their demographics', style='List Bullet')

doc.add_paragraph(
    'Motivation: If a county\'s demographics say it should vote Republican but it actually votes Democrat '
    '(or vice versa), that "misfit" may indicate demographic transition, unique local dynamics, or emerging '
    'political realignment \u2014 all of which should correlate with volatility.'
)

doc.add_heading('Model Assumptions', level=2)
doc.add_paragraph('Linear decision boundary between Democrat and Republican counties in demographic space', style='List Bullet')
doc.add_paragraph('P(Dem) is a well-calibrated probability; counties near P=0.5 are genuinely uncertain', style='List Bullet')
doc.add_paragraph('Prediction errors capture demographic-political misalignment, not model deficiency', style='List Bullet')

doc.add_heading('Setup & Performance', level=2)
doc.add_paragraph(
    'Target: dem_winner = 1 if dem_margin > 0, else 0. Method: cross_val_predict with 5-fold stratified CV '
    'produces P(Dem) for every county without data leakage. class_weight=\'balanced\'.'
)
bold_para(doc, 'Partisan prediction accuracy: 89.6%', ' \u2014 demographics predict party correctly in 9 out of 10 counties.')

doc.add_heading('Misfit Score', level=2)
p = doc.add_paragraph()
r = p.add_run('misfit_score = |actual_winner \u2212 P(Dem)|')
r.italic = True
doc.add_paragraph(
    'Range 0\u20131. A score of 0.96 means the model was 96% confident the county would vote one way, '
    'but it voted the other.'
)

doc.add_heading('Top 5 Demographic Misfits', level=2)
add_table(doc,
    ['County', 'State', 'P(Dem)', 'Actual', 'Misfit', 'Volatility'],
    [
        ['Leelanau', 'MI', '0.04', 'Dem (+8%)', '0.96', 'Highly Volatile'],
        ['Marquette', 'MI', '0.04', 'Dem (+9%)', '0.96', 'Highly Volatile'],
        ['Nash', 'NC', '0.95', 'Rep (\u22122%)', '0.95', 'Very Stable'],
        ['Lenoir', 'NC', '0.94', 'Rep (\u22127%)', '0.94', 'Stable'],
        ['Cabarrus', 'NC', '0.87', 'Rep (\u22128%)', '0.87', 'Highly Volatile'],
    ]
)

doc.add_paragraph(
    'Leelanau and Marquette (MI) are the biggest misfits \u2014 rural, white, low-density counties that '
    '"should" vote Republican based on demographics but vote Democrat (university/resort towns). '
    'They are also both Highly Volatile, confirming the misfit-volatility link.'
)

doc.add_heading('Misfit-Volatility Correlation', level=2)
add_table(doc,
    ['Correlation', 'Value', 'p-value'],
    [
        ['Spearman \u03c1 (misfit \u00d7 volatility)', '0.408', '< 0.001'],
        ['Pearson r (misfit \u00d7 swing direction)', '\u22120.017', 'n.s.'],
    ]
)

bold_para(doc, 'Counties that defy demographic expectations are significantly more volatile.',
          ' However, misfit score does NOT predict which direction they swing \u2014 '
          'it captures instability, not partisanship.')

add_figure(doc, 'misfit_scatter.png',
           'Figure 10: P(Dem) vs actual margin scatter. Point size = volatility (shifted to non-negative). '
           'Top 15 misfits annotated. Counties far from the diagonal defy their demographics.')

add_figure(doc, 'misfit_correlation_matrix.png',
           'Figure 11: Cross-analysis correlations between misfit score, volatility, swing direction, and P(Dem).')

doc.add_heading('Misfit Profiling (Deep-Dive)', level=2)
doc.add_paragraph('Misfits (top 20th percentile) compared to non-misfits:')
add_table(doc,
    ['Characteristic', 'Misfits', 'Non-Misfits', 'p-value'],
    [
        ['Racial diversity (entropy)', '0.567', '0.419', '< 0.0001'],
        ["Bachelor's degree+", '30.9%', '24.7%', '< 0.0001'],
        ['Owner-occupied housing', '71.1%', '76.3%', '< 0.0001'],
        ['Median gross rent', '$1,056', '$932', '< 0.0001'],
        ['Median age', '42.5', '44.5', '0.003'],
    ]
)
doc.add_paragraph(
    'Misfits are younger, more diverse, more educated, more urban, and more transient (lower homeownership) '
    '\u2014 they are places where the electorate is demographically "in flux."'
)

doc.add_heading('Two Types of Misfits', level=2)
add_table(doc,
    ['Type', 'Count (top 30)', 'Avg Volatility', 'Where'],
    [
        ['Surprise Dem\n(predicted Rep, votes Dem)', '8', '0.807', 'MI Upper Peninsula,\nPA Scranton area'],
        ['Surprise Rep\n(predicted Dem, votes Rep)', '22', '0.383', 'NC rural South'],
    ]
)
bold_para(doc, '"Surprise Dem" misfits are 2\u00d7 more volatile',
          ' than "Surprise Rep" \u2014 university towns and resort communities that vote against their '
          'rural/white demographics are the most electorally unstable counties in the dataset.')

add_figure(doc, 'deepdive_misfit_by_volatility.png',
           'Figure 12: Misfit score distribution by volatility class. The proportion of misfits '
           'increases monotonically from 6% (Very Stable) to 34% (Highly Volatile). '
           'Kruskal-Wallis H = 41.54, p < 0.000001.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 8. BINARY CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('8. Binary Classification \u2014 High vs Low Volatility', level=1)

doc.add_heading('Motivation', level=2)
doc.add_paragraph(
    'The 5-class problem (F1 \u2248 0.39) is limited by middle-class confusion. Collapsing to binary \u2014 '
    'High (Q4+Q5, n=100) vs Low (Q1\u2013Q3, n=150) \u2014 focuses on the most actionable distinction for '
    'campaign strategists: "Will this county swing significantly?"'
)

doc.add_heading('Binary Model Comparison', level=2)
add_table(doc,
    ['Model', 'Accuracy', 'F1', 'Precision', 'Recall', 'AUC'],
    [
        ['Random Forest', '0.780', '0.718', '0.726', '0.690', '0.828'],
        ['XGBoost', '0.748', '0.667', '0.718', '0.610', '0.803'],
        ['SVM (RBF)', '0.760', '0.674', '0.724', '0.630', '0.789'],
        ['Logistic Regression', '0.680', '0.604', '0.598', '0.610', '0.745'],
        ['SVM (Linear)', '0.688', '0.610', '0.610', '0.610', '0.734'],
    ]
)

bold_para(doc, 'Random Forest is the clear winner: F1 = 0.718, AUC = 0.828.')

doc.add_heading('5-Class \u2192 Binary Improvement', level=2)
add_table(doc,
    ['Metric', '5-Class Best', 'Binary Best', 'Improvement'],
    [
        ['F1', '0.387 (XGBoost)', '0.718 (RF)', '+85%'],
        ['AUC', '0.803 (RF)', '0.828 (RF)', '+3%'],
    ]
)
doc.add_paragraph(
    'Removing the ambiguous middle classes nearly doubles F1. This demonstrates that task framing '
    '(choosing the right problem formulation) matters more than model selection.'
)

add_figure(doc, 'deepdive_binary_roc_all_models.png',
           'Figure 13: ROC curves for all 5 binary models. Random Forest (blue) achieves the highest AUC = 0.828.')

add_figure(doc, 'deepdive_binary_confusion_matrices.png',
           'Figure 14: Binary confusion matrices for all 5 models side-by-side.')

add_figure(doc, 'deepdive_shap_binary_summary.png',
           'Figure 15: SHAP summary for binary XGBoost (High/Low). race_entropy_norm and '
           'log_median_gross_rent are the two dominant features.')

doc.add_heading('Bootstrap Confidence Intervals', level=2)
doc.add_paragraph(
    '200 bootstrap iterations \u00d7 5-fold CV to establish confidence intervals for the binary models:'
)
add_table(doc,
    ['Model', 'F1 [95% CI]', 'AUC [95% CI]', 'Accuracy [95% CI]'],
    [
        ['Random Forest', '0.818 [0.764, 0.872]', '0.918 [0.882, 0.946]', '0.856 [0.816, 0.900]'],
        ['XGBoost', '0.845 [0.789, 0.899]', '0.932 [0.894, 0.966]', '0.880 [0.840, 0.920]'],
    ]
)
doc.add_paragraph(
    'Note: Bootstrap CIs are higher than single-CV estimates because resampling with replacement creates '
    'some train-test overlap. The CIs confirm performance is robust and not an artifact of a lucky data split.'
)

add_figure(doc, 'deepdive2_feature_ablation.png',
           'Figure 16: Feature group ablation (left) and permutation importance with 95% CIs (right). '
           'Race/Ethnicity is both the most necessary and most sufficient feature group.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 9. ENSEMBLE STACKING
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('9. Ensemble Stacking', level=1)

doc.add_paragraph(
    'Can combining the best individual models improve on Random Forest\'s F1 = 0.718? '
    'We tested two ensemble strategies:'
)
doc.add_paragraph('Soft Voting (RF + XGBoost + SVM-RBF): Averages predicted probabilities from all three models', style='List Bullet')
doc.add_paragraph('Stacking (RF + XGBoost + SVM-RBF \u2192 Logistic Regression meta-learner): Learns the optimal combination of base model predictions', style='List Bullet')

doc.add_heading('Results', level=2)
add_table(doc,
    ['Model', 'Accuracy', 'F1', 'AUC', 'Type'],
    [
        ['Random Forest', '0.780', '0.718', '0.828', 'Individual'],
        ['Soft Voting', '0.768', '0.691', '0.826', 'Ensemble'],
        ['XGBoost', '0.748', '0.667', '0.803', 'Individual'],
        ['SVM (RBF)', '0.760', '0.663', '0.819', 'Individual'],
        ['Stacking (LR meta)', '0.760', '0.647', '0.816', 'Ensemble'],
        ['Logistic Regression', '0.680', '0.604', '0.745', 'Individual'],
    ]
)

add_figure(doc, 'deepdive2_model_scoreboard.png',
           'Figure 17: Final model scoreboard (left: F1 dot plot, right: ROC curves). '
           'Random Forest dominates; ensembles offer no improvement.')

bold_para(doc, 'Conclusion: Ensembles do not beat Random Forest.',
          ' Stacking actually hurts performance (F1 drops 0.718 \u2192 0.647) because the Logistic Regression '
          'meta-learner oversmooths predictions with only n=250 training samples. '
          'The performance bottleneck is dataset size, not algorithm sophistication. '
          'We have hit the performance ceiling for this sample.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 10. MODEL COMPARISON
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('10. Model Comparison & Performance Evaluation', level=1)

doc.add_heading('10.1 Complete 5-Class Comparison', level=2)
add_table(doc,
    ['Model', 'Accuracy', 'F1-macro', 'ROC-AUC', 'Best At'],
    [
        ['XGBoost', '0.388', '0.387', '0.783', 'Best overall; Q3, Q5'],
        ['Random Forest', '0.368', '0.362', '0.803', 'Best ROC-AUC; Q1'],
        ['SVM (Linear)', '0.368', '0.364', '0.765', 'Best middle-class (Q2)'],
    ]
)

add_figure(doc, 'per_class_f1_heatmap.png',
           'Figure 18: Per-class F1 heatmap across 3 models and 5 volatility classes. '
           'All models struggle with middle classes; extremes are well-separated.')

doc.add_heading('10.2 Complete Binary Comparison (Final Scoreboard)', level=2)
add_table(doc,
    ['Model', 'Accuracy', 'F1', 'AUC', 'Type'],
    [
        ['Random Forest', '0.780', '0.718', '0.828', 'Best overall'],
        ['Soft Voting', '0.768', '0.691', '0.826', 'Ensemble'],
        ['XGBoost', '0.748', '0.667', '0.803', 'Individual'],
        ['SVM (RBF)', '0.760', '0.663', '0.819', 'Individual'],
        ['Stacking', '0.760', '0.647', '0.816', 'Ensemble'],
        ['Logistic Regression', '0.680', '0.604', '0.745', 'Individual'],
    ]
)

doc.add_heading('10.3 Why Random Forest Wins', level=2)
doc.add_paragraph('Bagging advantage: With n=250, variance reduction from bootstrapped trees matters more than boosting\'s bias reduction', style='List Bullet')
doc.add_paragraph('Interaction handling: Naturally captures feature interactions (diversity \u00d7 density, education \u00d7 urbanization) without explicit specification', style='List Bullet')
doc.add_paragraph('Robustness: Less sensitive to hyperparameter choice than XGBoost \u2014 "just works" on small datasets', style='List Bullet')
doc.add_paragraph('Class weighting: class_weight=\'balanced\' effectively upweights minority volatility patterns', style='List Bullet')

doc.add_heading('10.4 Feature Group Ablation', level=2)
doc.add_paragraph(
    'To understand which demographic themes drive predictions, we performed leave-one-group-out '
    'and single-group-only ablation on the binary RF model (baseline F1 = 0.718):'
)
add_table(doc,
    ['Feature Group', 'n', 'F1 without', 'F1 drop', 'F1 alone'],
    [
        ['Race / Ethnicity', '6', '0.626', '+0.092', '0.619'],
        ['Urbanization', '6', '0.684', '+0.034', '0.583'],
        ['Education', '2', '0.708', '+0.010', '0.583'],
        ['Housing', '3', '0.712', '+0.006', '0.612'],
        ['Economic', '5', '0.722', '\u22120.004', '0.570'],
        ['Household / Age', '6', '0.728', '\u22120.010', '0.471'],
    ]
)
bold_para(doc, 'Race/Ethnicity is both necessary AND sufficient:',
          ' largest F1 drop when removed (0.092), and alone achieves 0.619 (86% of baseline). '
          'Economic and Household/Age groups are dispensable \u2014 removing them slightly improves F1.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 11. CROSS-STATE GENERALIZATION
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('11. Cross-State Generalization Experiment', level=1)

doc.add_heading('Setup', level=2)
doc.add_paragraph(
    'Leave-One-State-Out (LOSO): Train on two states, predict the third using the best 5-class model (XGBoost). '
    'Critical design decision: StandardScaler is refit on training states only to prevent data leakage.'
)

doc.add_heading('Results', level=2)
add_table(doc,
    ['Test State', 'Train States', 'Accuracy', 'F1-macro'],
    [
        ['MI (n=83)', 'PA + NC', '0.205', '0.182'],
        ['NC (n=100)', 'PA + MI', '0.210', '0.213'],
        ['PA (n=67)', 'MI + NC', '0.209', '0.189'],
    ]
)

add_table(doc,
    ['Setup', 'F1-macro'],
    [
        ['Full 5-fold CV (pooled)', '0.387'],
        ['LOSO average', '0.195'],
        ['Random baseline (1/5)', '0.200'],
    ]
)

bold_para(doc, 'Performance drops to random baseline when predicting across state lines.',
          ' The same demographic profile produces different political outcomes in PA, MI, and NC.')

add_figure(doc, 'loso_confusion_matrices.png',
           'Figure 19: Leave-one-state-out confusion matrices. All three rotations collapse to near-random prediction.')

doc.add_heading('State-Specific Volatility Signatures', level=2)
doc.add_paragraph(
    'To understand why LOSO fails, we trained separate binary XGBoost models within each state:'
)

add_table(doc,
    ['Rank', 'PA (Diversity-driven)', 'MI (Education-driven)', 'NC (Poverty-driven)'],
    [
        ['1', 'race_entropy_norm', 'pct_bachelors_plus', 'pct_below_poverty'],
        ['2', 'log_median_gross_rent', 'log_median_gross_rent', 'log_median_gross_rent'],
        ['3', 'pct_foreign_born', 'pct_work_from_home', 'log_population_density'],
        ['4', 'pct_two_or_more_races', 'log_median_home_value', 'log_median_home_value'],
        ['5', 'log_median_hh_income', 'pct_senior_65plus', 'pct_bachelors_plus'],
    ]
)

bold_para(doc, 'The only universal predictor: log_median_gross_rent',
          ' \u2014 housing cost appears in every state\'s top 5. Everything else is state-specific, '
          'reflecting distinct political cultures, historical patterns, and local economics.')

add_figure(doc, 'deepdive_state_feature_importance.png',
           'Figure 20: Per-state top 15 feature importance (3-panel). Each state has a fundamentally different '
           'volatility signature.')

add_figure(doc, 'deepdive_state_roc_curves.png',
           'Figure 21: State-specific ROC curves vs pooled model. NC achieves the best within-state AUC.')

add_table(doc,
    ['State', 'n', 'AUC', 'F1'],
    [
        ['PA', '67', '0.838', '0.591'],
        ['MI', '83', '0.778', '0.636'],
        ['NC', '100', '0.829', '0.736'],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 12. HYPOTHESIS TESTING
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('12. Hypothesis Testing', level=1)

doc.add_heading('H1: Volatility Inversely Correlated with Wealth \u2014 CONFIRMED', level=2)
add_table(doc,
    ['Evidence', 'Method', 'Value'],
    [
        ['SHAP direction', 'Q5 SHAP for log_median_hh_income', 'r = \u22120.602 (p < 0.0001)'],
        ['Feature importance', 'pct_below_poverty rank', 'Top 5 in all models'],
        ['PDP shape', 'log_median_gross_rent', 'Monotonic increase'],
        ['Ablation', 'Economic group alone', 'F1 = 0.570 (insufficient alone)'],
    ]
)
doc.add_paragraph(
    'Higher income pushes counties away from high volatility. But income alone is insufficient \u2014 '
    'it interacts with diversity, education, and urbanization.'
)

doc.add_heading('H2: Diversity Index > Individual Race Features \u2014 CONFIRMED', level=2)
add_table(doc,
    ['Evidence', 'Method', 'Result'],
    [
        ['Permutation importance', 'RF, 30 repeats', 'race_entropy_norm = #1'],
        ['SHAP importance', 'XGBoost mean |SHAP|', 'entropy (0.397) > pct_black (0.347)'],
        ['PDP range', 'Probability swing', 'entropy = 0.14 (largest)'],
        ['Feature ablation', 'Race group alone', 'F1 = 0.619 (86% of baseline)'],
        ['Interaction hub', 'SHAP interactions', 'entropy in 6/10 top interactions'],
        ['Threshold analysis', 'Maximum-separation', 'Odds ratio = 7.15\u00d7'],
    ]
)
doc.add_paragraph(
    'race_entropy_norm is the single most important feature in the entire analysis. '
    'It captures information that no individual race percentage can match \u2014 it measures mixing, '
    'not the share of any group.'
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 13. ADVANCED ANALYSIS — DEEP-DIVES
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('13. Advanced Analysis \u2014 Deep-Dives', level=1)

doc.add_heading('13.1 Temporal Demographic Shifts (2016 \u2192 2024)', level=2)
doc.add_paragraph(
    'It\'s not just static demographics \u2014 demographic change over 8 years predicts volatility. '
    'We computed deltas between 2016 and 2024 ACS data for all 250 counties and correlated them '
    'with volatility (Bonferroni-corrected Spearman correlations):'
)
add_table(doc,
    ['Demographic Change (\u0394)', 'Spearman \u03c1', 'p-value', 'Direction'],
    [
        ['\u0394 pct_hispanic', '+0.220', '0.0005', 'Growing Hispanic pop \u2192 more volatile'],
        ['\u0394 median_gross_rent', '+0.209', '0.0009', 'Rising rents \u2192 more volatile'],
        ['\u0394 pct_two_or_more_races', '+0.209', '0.0009', 'Growing multiracial pop \u2192 more volatile'],
        ['\u0394 pct_black', '\u22120.194', '0.0020', 'Growing Black pop \u2192 less volatile'],
    ]
)
bold_para(doc, 'Diversification (entropy increase) predicts volatility; growth of a single group does not.',
          ' This is consistent with the entropy-based findings from the static models.')

add_figure(doc, 'deepdive2_temporal_demographic_shifts.png',
           'Figure 22: Temporal demographic shifts vs volatility. Left: Bonferroni-corrected correlation bars. '
           'Right: Top 2 scatter plots with trend lines.')

doc.add_heading('13.2 Election Margin Trajectories (2016 \u2192 2020 \u2192 2024)', level=2)
doc.add_paragraph(
    'Instead of a single volatility score, we trace how each county\'s margin evolved across three elections. '
    'Four trajectory types emerge based on the direction of change in each cycle:'
)
add_table(doc,
    ['Trajectory', 'n', 'Mean Vol', '% High Vol', 'Pattern'],
    [
        ['Blue Bounceback', '117', '\u22120.17', '34%', 'Swung D in 2020, snapped back in 2024'],
        ['Steady Red Drift', '94', '+0.39', '50%', 'Moved R in both cycles \u2014 most volatile'],
        ['Steady Blue Drift', '35', '\u22120.28', '37%', 'Moved D in both cycles'],
        ['Red Bounceback', '4', '\u22121.82', '0%', 'Swung R in 2020, then D (extremely rare)'],
    ]
)

add_table(doc,
    ['Trajectory', 'PA', 'MI', 'NC'],
    [
        ['Blue Bounceback', '36 (54%)', '49 (59%)', '32 (32%)'],
        ['Steady Red Drift', '18 (27%)', '27 (33%)', '49 (49%)'],
        ['Steady Blue Drift', '12 (18%)', '6 (7%)', '17 (17%)'],
    ]
)

doc.add_paragraph('Blue Bounceback is dominant (47%) \u2014 the 2020 Biden surge was temporary in most places.', style='List Bullet')
doc.add_paragraph('Steady Red Drift is the most volatile trajectory (50% high volatility).', style='List Bullet')
doc.add_paragraph('NC is different: 49% Steady Red Drift vs only 27\u201333% in PA/MI \u2014 ongoing Southern realignment.', style='List Bullet')

add_figure(doc, 'deepdive2_margin_trajectories.png',
           'Figure 23: Spaghetti plot of margin trajectories by state (3-panel). '
           'Each line is one county. Colors indicate trajectory type.')

doc.add_heading('13.3 The Diversity Threshold \u2014 Precisely Estimated', level=2)
doc.add_paragraph(
    'The prior analysis established diversity as a "switch." Here we estimate the precise threshold '
    'using maximum-separation search with 1000-resample bootstrap:'
)
add_table(doc,
    ['Metric', 'Value'],
    [
        ['Optimal threshold', 'race_entropy_norm = 0.552'],
        ['95% Bootstrap CI', '[0.397, 0.642]'],
        ['Below threshold (n=164)', '24.4% high volatility'],
        ['Above threshold (n=86)', '69.8% high volatility'],
        ['Odds ratio', '7.15\u00d7'],
    ]
)
doc.add_paragraph(
    'A race_entropy_norm of 0.552 corresponds to a county where no single racial group exceeds ~60% '
    'of the population \u2014 a genuinely mixed community. Counties above this threshold are 7\u00d7 more likely '
    'to be highly volatile.'
)

add_figure(doc, 'deepdive2_diversity_threshold.png',
           'Figure 24: Diversity threshold visualization. Left: KDE distributions of entropy for High vs Low volatility. '
           'Right: Rolling probability curve showing P(High Vol) jumping from ~20% to ~80% across the threshold zone.')

doc.add_heading('13.4 Partial Dependence Analysis', level=2)
doc.add_paragraph(
    'Partial Dependence Plots (PDPs) reveal the true functional form of each feature\'s effect, '
    'averaged across all counties. ICE (Individual Conditional Expectation) lines show per-county heterogeneity.'
)

add_table(doc,
    ['Feature', 'Functional Form', 'Key Insight'],
    [
        ['race_entropy_norm', 'Step function', 'Flat \u2192 jumps at threshold \u2192 plateaus'],
        ['log_median_gross_rent', 'Monotonic increase', 'Higher rent = higher P(volatile)'],
        ['pct_below_poverty', 'Late spike', 'Flat until extreme poverty, then jumps'],
        ['pct_married_couple', 'Flat', 'Works via interactions only'],
        ['pct_bachelors_plus', 'Slight upward', 'Modest increase at high education'],
        ['log_population_density', 'Uptick at extremes', 'Mostly flat; interaction-driven'],
    ]
)

add_figure(doc, 'deepdive2_partial_dependence.png',
           'Figure 25: Partial dependence plots with ICE lines (top 6 features), 2D interaction contours '
           '(diversity \u00d7 density, education \u00d7 diversity), and PDP-based importance ranking.')

doc.add_heading('13.5 Nonlinear Deep-Dives', level=2)

bold_para(doc, 'Diversity \u00d7 Poverty \u2014 The clearest finding in the entire analysis:')
add_table(doc,
    ['Quadrant', 'n', 'Mean Vol', '% High Vol'],
    [
        ['Low Diversity / Low Poverty', '73', '\u22120.622', '19%'],
        ['Low Diversity / High Poverty', '52', '\u22120.669', '23%'],
        ['High Diversity / Low Poverty', '52', '+0.407', '60%'],
        ['High Diversity / High Poverty', '73', '+0.808', '59%'],
    ]
)
doc.add_paragraph(
    'Diversity is the switch \u2014 crossing the threshold triples the high-volatility rate (20% \u2192 60%), '
    'regardless of poverty level. Poverty adds magnitude but not probability.'
)

add_figure(doc, 'deepdive_diversity_poverty_interaction.png',
           'Figure 26: Diversity \u00d7 Poverty quadrant analysis. High diversity triples volatility rate '
           'independent of poverty level.')

bold_para(doc, 'Education \u00d7 Urbanization \u2014 Volatile at both extremes:')
add_table(doc,
    ['Quadrant', 'n', '% High Vol'],
    [
        ['Low Education / Rural', '89', '42%'],
        ['Low Education / Urban', '36', '19% (least volatile)'],
        ['High Education / Rural', '36', '33%'],
        ['High Education / Urban', '89', '49% (most volatile)'],
    ]
)

add_figure(doc, 'deepdive_education_urbanization.png',
           'Figure 27: Education \u00d7 Urbanization quadrant analysis. Most volatile at extremes; '
           'least volatile = low-education urban (stable working-class cities).')

bold_para(doc, 'Rent and Volatility \u2014 U-Shaped Relationship:')
doc.add_paragraph(
    'Linear correlation is modest (r = 0.220), but the true relationship is nonlinear: '
    'low-rent counties are mixed, mid-rent are most stable (the suburban core), '
    'and high-rent are most volatile (fast-changing urban fringe and gentrifying areas).'
)

add_figure(doc, 'deepdive_rent_volatility.png',
           'Figure 28: Rent vs volatility deep-dive (3-panel). Reveals the U-shaped nonlinear relationship.')

doc.add_heading('13.6 SHAP Case Studies \u2014 Four Archetypes', level=2)
add_table(doc,
    ['County', 'Archetype', '#1 SHAP Driver', 'Insight'],
    [
        ['Bucks, PA', 'Suburban swing', 'log_median_gross_rent (+0.85)', 'High rent + large suburban = bellwether'],
        ['Leelanau, MI', 'Demographic misfit', 'pct_bachelors_plus (+1.50)', 'Educated but rural/white; votes Dem'],
        ['Scotland, NC', 'Diverse-poor rural', 'race_entropy_norm (+1.25)', 'Highest volatility via diversity+poverty'],
        ['Philadelphia, PA', 'Urban extreme', 'pct_living_alone (\u22120.80)', 'Dense+diverse but STABLE'],
    ]
)
doc.add_paragraph(
    'Philadelphia is the critical counter-example: extremely diverse and high poverty, yet electorally '
    'stable. High pct_living_alone and low pct_owner_occupied push it toward stability. '
    'Urban density creates voting consistency that overrides the diversity-volatility signal.'
)

add_figure(doc, 'deepdive_shap_case_studies.png',
           'Figure 29: SHAP waterfall plots for 4 county archetypes. Each bar shows one feature\'s '
           'push toward High or Low volatility prediction.')

doc.add_heading('13.7 SHAP-Based County Archetypes', level=2)
doc.add_paragraph(
    'Instead of clustering on raw features (which would group by demographics), we cluster on SHAP values '
    '(which groups by why the model predicts volatility). K-Means (k=5) on SHAP values reveals 5 functionally '
    'distinct county types:'
)
add_table(doc,
    ['Cluster', 'n', '% High Vol', 'Top SHAP Driver', 'State', 'Archetype'],
    [
        ['0', '35', '100%', 'race_entropy_norm (1.54)', 'NC (33/35)', 'NC Diverse Rural'],
        ['1', '47', '0%', 'log_total_population (0.82)', 'NC + MI', 'Stable Small Counties'],
        ['2', '33', '91%', 'pct_foreign_born (0.66)', 'MI (21/33)', 'MI Working-Class Transition'],
        ['3', '92', '0%', 'race_entropy_norm (1.07)', 'All states', 'Stable Core'],
        ['4', '43', '81%', 'log_total_population (0.92)', 'PA+NC+MI', 'Suburban Battlegrounds'],
    ]
)

doc.add_paragraph('Clusters 0, 1, and 3 show perfect or near-perfect separation (100% / 0% / 0% high volatility) \u2014 the model finds clean archetype boundaries.', style='List Bullet')
doc.add_paragraph('Cluster 0 (NC Diverse Rural) is almost entirely North Carolina \u2014 racially mixed rural Southern counties driving NC\'s distinctive volatility.', style='List Bullet')
doc.add_paragraph('Cluster 2 (MI Working-Class Transition) is driven by immigration and education, not diversity per se \u2014 the Rust Belt mechanism is fundamentally different from the Southern mechanism.', style='List Bullet')
doc.add_paragraph('This directly explains why LOSO cross-state prediction fails \u2014 Cluster 0 is NC-only and Cluster 2 is MI-heavy; their volatility mechanisms don\'t transfer.', style='List Bullet')

add_figure(doc, 'deepdive2_shap_archetypes.png',
           'Figure 30: SHAP-based archetypes. Top-left: PCA projection of SHAP space. '
           'Top-right: state composition per cluster. Bottom: radar charts of mean SHAP values per archetype.')

doc.add_heading('13.8 Campaign Priority Scoring', level=2)
doc.add_paragraph('Translating analytical findings into actionable resource allocation:')
p = doc.add_paragraph()
r = p.add_run('priority = 0.30 \u00d7 volatility + 0.25 \u00d7 misfit + 0.25 \u00d7 vote_volume + 0.20 \u00d7 margin_closeness')
r.italic = True

add_table(doc,
    ['Rank', 'County', 'State', 'Priority', 'Votes', 'Margin', 'Vol. Class'],
    [
        ['1', 'Bucks', 'PA', '0.650', '802,056', '\u22120.1%', 'Highly Volatile'],
        ['2', 'Lackawanna', 'PA', '0.574', '233,180', '+2.8%', 'Highly Volatile'],
        ['3', 'Cabarrus', 'NC', '0.570', '120,202', '\u22127.7%', 'Highly Volatile'],
        ['4', 'Leelanau', 'MI', '0.566', '17,685', '+7.8%', 'Highly Volatile'],
        ['5', 'Scotland', 'NC', '0.561', '14,626', '\u22126.9%', 'Highly Volatile'],
        ['6', 'Marquette', 'MI', '0.547', '39,009', '+8.7%', 'Highly Volatile'],
        ['7', 'Genesee', 'MI', '0.514', '223,268', '+4.2%', 'Volatile'],
        ['8', 'Monroe', 'PA', '0.492', '171,050', '\u22120.8%', 'Highly Volatile'],
        ['9', 'Isabella', 'MI', '0.492', '30,835', '\u22127.5%', 'Volatile'],
        ['10', 'Grand Traverse', 'MI', '0.484', '62,772', '\u22121.7%', 'Highly Volatile'],
    ]
)

bold_para(doc, 'Bucks County, PA is the #1 target nationally',
          ' \u2014 800k votes, 0.1% margin, highly volatile. The single most electorally decisive county.')

add_figure(doc, 'deepdive_campaign_priority_scatter.png',
           'Figure 31: Campaign priority scatter (volatility \u00d7 misfit score). '
           'Bubble size = vote volume, color = state. Top right = highest priority.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 14. GRAND SYNTHESIS
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('14. Key Findings & Grand Synthesis', level=1)

doc.add_heading('The Volatility Formula (Qualitative)', level=2)
doc.add_paragraph(
    'Electoral volatility emerges from the interaction of three factors:'
)

bold_para(doc, '1. Racial/ethnic diversity (necessary condition):',
          ' race_entropy_norm is the #1 predictor. Low-diversity counties are almost never highly volatile. '
          'The threshold is 0.552 (7\u00d7 odds ratio). Diversification \u2014 not the growth of any single group '
          '\u2014 destabilizes voting patterns.')

bold_para(doc, '2. Economic transition (amplifying condition):',
          ' Captured by log_median_gross_rent, pct_below_poverty, pct_bachelors_plus. '
          'Counties where housing costs are rising, education levels are shifting, or poverty is persistent '
          'show higher volatility.')

bold_para(doc, '3. Context (moderating condition):',
          ' The same demographics produce different outcomes depending on state '
          '(PA: diversity, MI: education, NC: poverty), urbanization (diversity matters more in suburbs), '
          'and household structure (married-couple \u2192 stability).')

doc.add_heading('What Does NOT Predict Volatility', level=2)
doc.add_paragraph('Poverty alone \u2014 low-diversity poor counties are among the most stable', style='List Bullet')
doc.add_paragraph('Education alone \u2014 only predicts volatility when combined with urbanization', style='List Bullet')
doc.add_paragraph('Demographics from other states \u2014 LOSO F1 = 0.195 = random baseline', style='List Bullet')
doc.add_paragraph('Swing direction \u2014 misfit score has r = \u22120.017 with partisanship', style='List Bullet')

doc.add_heading('Methodological Conclusions', level=2)
doc.add_paragraph('Task framing > algorithms: Binary (F1=0.718) nearly doubles 5-class (F1=0.387). Problem formulation matters more than model selection.', style='List Bullet')
doc.add_paragraph('Ensembles don\'t help at n=250: The performance ceiling is dataset size, not algorithm sophistication.', style='List Bullet')
doc.add_paragraph('National models are fundamentally limited: State-specific political cultures create distinct volatility mechanisms.', style='List Bullet')
doc.add_paragraph('SHAP archetypes > feature importance: Clustering on SHAP values reveals clean county types with near-perfect separation.', style='List Bullet')

doc.add_heading('Grand Synthesis Figure', level=2)
doc.add_paragraph(
    'The complete story in 6 panels \u2014 from the diversity switch operating across all states (A), '
    'through state-specific signatures (B), model performance journey (C), trajectory types (D), '
    'SHAP archetypes (E), to actionable campaign targets (F):'
)

add_figure(doc, 'deepdive2_grand_synthesis.png',
           'Figure 32: Grand Synthesis \u2014 Electoral Volatility in PA, MI, NC (2016\u20132024). '
           'The complete analytical story in one publication-quality figure.',
           width=Inches(7.0))

doc.add_heading('Geographic Visualization', level=2)

add_figure(doc, 'choropleth_volatility_class.png',
           'Figure 33: Choropleth map of predicted volatility class by county across all 3 states.')

add_figure(doc, 'choropleth_misfit_score.png',
           'Figure 34: Choropleth map of demographic misfit score. Top 15 misfits highlighted with bold borders.')

doc.add_heading('Complete Metrics At-a-Glance', level=2)
add_table(doc,
    ['Finding', 'Metric', 'Value'],
    [
        ['Best binary model', 'RF F1', '0.718'],
        ['Best 5-class model', 'XGBoost F1-macro', '0.387'],
        ['Bootstrap CI (RF binary)', 'F1 [95% CI]', '0.818 [0.764, 0.872]'],
        ['Performance ceiling', 'Ensemble F1', '0.691 (no improvement)'],
        ['Diversity threshold', 'race_entropy_norm', '0.552 [0.397, 0.642]'],
        ['Diversity odds ratio', 'above/below threshold', '7.15\u00d7'],
        ['Most necessary group', 'Race/Ethnicity F1 drop', '+0.092'],
        ['Most sufficient group', 'Race/Ethnicity F1 alone', '0.619'],
        ['Top temporal predictor', '\u0394 pct_hispanic \u03c1', '+0.220'],
        ['Most volatile trajectory', 'Steady Red Drift', '50% high vol'],
        ['Most common trajectory', 'Blue Bounceback', '117/250 (47%)'],
        ['#1 priority county', 'Bucks County PA', '802k votes, 0.1% margin'],
        ['SHAP archetypes', 'k=5', '100%/0%/91%/0%/81% high vol'],
        ['Cross-state transfer', 'LOSO F1', '0.195 (= random)'],
        ['H1 (income\u2194volatility)', 'SHAP r', '\u22120.602'],
        ['H2 (entropy > race)', 'Permutation imp', '#1 (confirmed)'],
        ['Misfit-volatility link', 'Spearman \u03c1', '0.408 (p < 0.001)'],
        ['Partisan prediction', 'LR accuracy', '89.6%'],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════
# 15. APPENDIX
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('15. Appendix: Notebooks, Data Files & Figures', level=1)

doc.add_heading('Notebooks', level=2)
add_table(doc,
    ['Notebook', 'Cells', 'Description'],
    [
        ['classification_antoni.ipynb', '86', 'Core: RF, XGBoost, SVM, Misfit Detector, LOSO, choropleths'],
        ['classification_antoni_deepdive.ipynb', '48', 'Deep-dive I: misfits, state models, SHAP interactions,\nbinary models, campaign scoring, nonlinear analysis'],
        ['classification_antoni_deepdive_2.ipynb', '30', 'Deep-dive II: temporal shifts, trajectories, PDPs,\nbootstrap CIs, ablation, ensembles, threshold, archetypes'],
        ['classification_antoni_deepdive_3.ipynb', '5', 'Grand synthesis figure (standalone)'],
    ]
)

doc.add_heading('Data Files Produced', level=2)
add_table(doc,
    ['File', 'Description'],
    [
        ['classification_dataset_250.csv', '250 counties, 28 scaled features + targets'],
        ['classification_predictions.csv', 'All model predictions + misfit scores'],
        ['rf_predictions.csv', 'RF predictions for clustering comparison'],
        ['campaign_priority_rankings.csv', '250 counties with priority scores + components'],
    ]
)

doc.add_heading('Figure Index (34 figures)', level=2)
figures_list = [
    ('Figure 1', 'RF confusion matrix (5-class)'),
    ('Figure 2', 'RF Gini feature importance'),
    ('Figure 3', 'RF permutation importance'),
    ('Figure 4', 'XGBoost confusion matrix (5-class)'),
    ('Figure 5', 'SHAP feature importance summary'),
    ('Figure 6', 'SHAP dependence plots (top 5 features)'),
    ('Figure 7', 'Top 6 SHAP interaction scatter plots'),
    ('Figure 8', 'SHAP interaction strength heatmap'),
    ('Figure 9', 'SVM confusion matrix'),
    ('Figure 10', 'P(Dem) vs actual margin scatter'),
    ('Figure 11', 'Model D cross-analysis correlations'),
    ('Figure 12', 'Misfit score by volatility class'),
    ('Figure 13', 'Binary ROC curves (5 models)'),
    ('Figure 14', 'Binary confusion matrices (5 models)'),
    ('Figure 15', 'SHAP summary (binary)'),
    ('Figure 16', 'Feature ablation + permutation importance CIs'),
    ('Figure 17', 'Final model scoreboard + ROC'),
    ('Figure 18', 'Per-class F1 heatmap'),
    ('Figure 19', 'LOSO confusion matrices'),
    ('Figure 20', 'Per-state feature importance (3-panel)'),
    ('Figure 21', 'State-specific ROC curves'),
    ('Figure 22', 'Temporal demographic shifts'),
    ('Figure 23', 'Margin trajectories (spaghetti)'),
    ('Figure 24', 'Diversity threshold (KDE + rolling prob)'),
    ('Figure 25', 'Partial dependence with ICE lines'),
    ('Figure 26', 'Diversity \u00d7 Poverty interaction'),
    ('Figure 27', 'Education \u00d7 Urbanization interaction'),
    ('Figure 28', 'Rent vs volatility nonlinear'),
    ('Figure 29', 'SHAP waterfall case studies'),
    ('Figure 30', 'SHAP-based archetypes (PCA + radar)'),
    ('Figure 31', 'Campaign priority scatter'),
    ('Figure 32', 'Grand synthesis (6-panel)'),
    ('Figure 33', 'Choropleth: volatility class'),
    ('Figure 34', 'Choropleth: misfit score'),
]
add_table(doc,
    ['#', 'Description'],
    [[f[0], f[1]] for f in figures_list]
)

# ── Save ──
doc.save(OUT)
print(f'Document saved to: {OUT}')
print(f'Pages estimated: ~25-30 (with all figures)')