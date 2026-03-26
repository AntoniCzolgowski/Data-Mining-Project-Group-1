#!/usr/bin/env python3
"""Build MILESTONE_3_CLASSIFICATION.docx — trimmed ~35 page version."""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, 'docs', 'images', 'methods')
OUT = os.path.join(BASE, 'MILESTONE_3_CLASSIFICATION.docx')


def img(name):
    p = os.path.join(FIG, name)
    return p if os.path.exists(p) else None

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(4)
style.paragraph_format.space_before = Pt(2)
for level in range(1, 4):
    doc.styles[f'Heading {level}'].font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(9)
    doc.add_paragraph()


def add_figure(doc, filename, caption, width=Inches(5.8)):
    path = img(filename)
    if not path:
        return
    doc.add_picture(path, width=width)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def bold_para(doc, bold_text, normal_text=''):
    p = doc.add_paragraph()
    p.add_run(bold_text).bold = True
    if normal_text:
        p.add_run(normal_text)
    return p


def takeaway(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run('\u25b6 Takeaway: ')
    r.bold = True
    r.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)
    r.font.size = Pt(10)
    r2 = p.add_run(text)
    r2.font.size = Pt(10)


def method_box(doc, title, text):
    p = doc.add_paragraph()
    r = p.add_run(f'\U0001f4d6 What is {title}? ')
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x2a, 0x6e, 0x2a)
    p.add_run(text).font.size = Pt(10)


# ═══════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('Milestone 3: Classification of Electoral Volatility')
r.bold = True; r.font.size = Pt(26); r.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

s = doc.add_paragraph()
s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run('Predicting County-Level Electoral Instability\nfrom Demographic Census Data')
r.font.size = Pt(14); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()
m = doc.add_paragraph()
m.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = m.add_run('Antoni Czolgowski\n')
r.bold = True; r.font.size = Pt(13)
m.add_run('CSCI 5502 Data Mining \u2014 Spring 2026\nUniversity of Colorado Boulder\nMarch 2026').font.size = Pt(12)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# TOC
# ═══════════════════════════════════════════════════════════════
doc.add_heading('Table of Contents', level=1)
for item in [
    '1. Research Questions & Motivation',
    '2. Dataset & Feature Engineering',
    '3. Data Formatting for Models',
    '4. Classification Models (Random Forest, XGBoost, SVM)',
    '5. Model D \u2014 Demographic Misfit Detector (Logistic Regression)',
    '6. Binary Classification \u2014 High vs Low Volatility',
    '7. Model Comparison & Cross-State Generalization',
    '8. Hypothesis Testing',
    '9. Advanced Analysis \u2014 Deep-Dives',
    '10. Key Findings & Grand Synthesis',
    '11. Appendix',
]:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 1. RESEARCH QUESTIONS  (~1.5 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('1. Research Questions & Motivation', level=1)

p = doc.add_paragraph()
r = p.add_run('Can we predict which U.S. counties will be electorally volatile \u2014 likely to swing between parties \u2014 using only demographic data, without knowing how they voted in the past?')
r.bold = True; r.font.size = Pt(12)

doc.add_paragraph(
    'Electoral volatility determines where campaign resources have the highest return on investment. '
    'We study 250 counties across three battleground states \u2014 Pennsylvania (67), Michigan (83), '
    'and North Carolina (100) \u2014 using American Community Survey census data merged with election '
    'results from 2016, 2020, and 2024.')

doc.add_heading('Hypotheses', level=2)
bold_para(doc, 'H1 \u2014 Wealth-Volatility Inverse: ',
          'Wealthier counties are more electorally stable. Counties in the bottom income quartile '
          'will show higher partisan swing variance than those in the top quartile.')
bold_para(doc, 'H2 \u2014 Diversity Index > Individual Race: ',
          'A composite racial diversity index (Shannon entropy over 4 racial categories) '
          'will outperform any single-race percentage as a volatility predictor. '
          'It\'s racial mixing \u2014 not any single group \u2014 that predicts instability.')

doc.add_heading('Why Classification?', level=2)
doc.add_paragraph(
    'Campaign strategists need to know: "Will this county swing significantly?" '
    'This is a categorization task. We implement classifiers from different families '
    '(ensemble trees, gradient boosting, kernel methods, linear models) to compare approaches.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 2. DATASET  (~2 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('2. Dataset & Feature Engineering', level=1)

doc.add_heading('2.1 Source Data', level=2)
add_table(doc,
    ['File', 'Rows', 'Description'],
    [['master_dataset.csv', '750 (250\u00d73 years)', '39 demographic + election columns'],
     ['master_dataset_scaled.csv', '750', 'Contains race_entropy_norm (diversity index 0\u20131)'],
     ['county_volatility_dimTable.csv', '250', 'Volatility target from margin changes']])

doc.add_heading('2.2 Target Variable', level=2)
doc.add_paragraph(
    'Our target vol_z_abs_sum measures total swing across two election cycles: '
    'the sum of absolute z-scored margin changes from 2016\u21922020 and 2020\u21922024. '
    'Binned into 5-class quintiles (50 each) and binary: High (Q4+Q5, n=100) vs Low (Q1\u2013Q3, n=150).')

doc.add_heading('2.3 Feature Inventory (28 Demographic Features)', level=2)
doc.add_paragraph('All election variables excluded to prevent leakage. Six thematic groups:')
add_table(doc,
    ['Group', 'Features', 'n'],
    [['Race / Ethnicity', 'pct_black, pct_asian, pct_two_or_more_races, pct_hispanic,\npct_non_hispanic_white, race_entropy_norm', '6'],
     ['Urbanization', 'log_total_population, log_population_density,\npct_drive_alone, pct_carpool, pct_public_transit, pct_work_from_home', '6'],
     ['Education', 'pct_hs_or_higher, pct_bachelors_plus', '2'],
     ['Housing', 'log_median_gross_rent, log_median_home_value, pct_owner_occupied', '3'],
     ['Economic', 'log_median_household_income, pct_below_poverty,\npct_income_under_25k, pct_income_50k_100k, unemployment_rate', '5'],
     ['Household / Age', 'median_age, pct_senior_65plus, pct_young_adult_18_24,\npct_foreign_born, pct_family_households, pct_married_couple, pct_living_alone', '7']])

doc.add_heading('2.4 The Diversity Index (race_entropy_norm)', level=2)
doc.add_paragraph(
    'Shannon entropy from 4 racial categories. Score 0 = entirely one race; '
    '1 = perfect split across 4 groups; ~0.55 = no group exceeds ~60%. '
    'Measures mixing, not the share of any particular group. '
    'As we will show, this is the single most important predictor of volatility.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 3. DATA FORMATTING  (~1.5 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('3. Data Formatting for Models', level=1)

doc.add_heading('3.1 Log-Transformation', level=2)
doc.add_paragraph('Five heavy-tailed variables received np.log1p() to compress extreme outliers:')
add_table(doc,
    ['Variable', 'Skewness Before', 'After'],
    [['total_population', '5.82', '0.89'],
     ['population_density', '4.61', '0.34'],
     ['median_household_income', '1.03', '0.72'],
     ['median_home_value', '1.67', '0.81'],
     ['median_gross_rent', '0.98', '0.54']])

doc.add_heading('3.2 Multicollinearity & Scaling', level=2)
doc.add_paragraph(
    'Dropped pct_income_over_100k (r=0.97 with income). '
    'All 28 features standardized to zero mean, unit variance via StandardScaler \u2014 '
    'required for SVM and Logistic Regression, applied to all models for consistency.')

doc.add_heading('3.3 Before-and-After Snapshots', level=2)
add_table(doc,
    ['Stage', 'total_population', 'pct_below_poverty'],
    [['Raw', 'mean=126,437; range [2,144\u20131,603,797]', 'mean=14.8%; range [4.1%\u201335.2%]'],
     ['After log', 'mean=10.8; range [7.7\u201314.3]', '(unchanged)'],
     ['After scale', 'mean=0.0; range [\u22122.6\u20132.9]', 'mean=0.0; range [\u22121.8\u20133.3]']])

doc.add_heading('3.4 Model-Specific Requirements', level=2)
add_table(doc,
    ['Model', 'Needs Numerical?', 'Needs Scaling?', 'Our Approach'],
    [['Random Forest', 'No', 'No', 'Scaling for consistency'],
     ['XGBoost', 'No', 'No', 'Labels 0-indexed'],
     ['SVM', 'Yes', 'Yes', 'StandardScaler required'],
     ['Logistic Regression', 'Yes', 'Yes', 'StandardScaler + balanced weights']])

takeaway(doc, 'Data was log-transformed, de-duplicated, and scaled. '
         'Three snapshots (raw \u2192 log \u2192 scaled) document every transformation step.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 4. CLASSIFICATION MODELS — COMBINED  (~6 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('4. Classification Models', level=1)

doc.add_paragraph(
    'We implemented three classification models from different algorithmic families. '
    'All use nested cross-validation: outer 5-fold for evaluation, inner 3-fold for hyperparameter tuning.')

# --- 4.1 Random Forest ---
doc.add_heading('4.1 Random Forest', level=2)

method_box(doc, 'Random Forest',
    'Imagine 300 analysts each seeing a random subset of data and features, '
    'each building a decision tree (flowchart of yes/no questions). '
    'The final prediction is the majority vote. This "wisdom of crowds" reduces '
    'the chance that any single quirk misleads the prediction.')

bold_para(doc, 'Why chosen: ', 'Non-parametric (no distribution assumptions), captures interactions naturally, '
          'provides feature importance rankings, robust to noise with small n=250.')
bold_para(doc, 'Assumptions: ', 'Some features carry information about volatility; no linearity assumption.')

doc.add_heading('Hyperparameters', level=3)
add_table(doc,
    ['Setting', 'Search Space', 'Best', 'Controls'],
    [['n_estimators', '100\u2013500', '300', 'Number of trees'],
     ['max_depth', '5\u201320, None', '8', 'Tree complexity'],
     ['min_samples_leaf', '3, 5, 10', '5', 'Prevents memorization'],
     ['max_features', 'sqrt, log2, 0.3, 0.5', 'sqrt', 'Diversity among trees'],
     ['class_weight', 'balanced, subsample, none', 'balanced', 'Handles class imbalance']])

doc.add_heading('Results (5-Class)', level=3)
add_table(doc,
    ['Metric', 'Value'],
    [['Accuracy', '0.368'], ['Precision (macro)', '0.369'], ['Recall (macro)', '0.368'],
     ['F1-macro', '0.362'], ['ROC-AUC', '0.803']])

add_table(doc,
    ['Very Stable', 'Stable', 'Moderate', 'Volatile', 'Highly Volatile'],
    [['F1=0.46', 'F1=0.18', 'F1=0.28', 'F1=0.30', 'F1=0.59']])
doc.add_paragraph('37% accuracy may seem low, but random guessing = 20%. The model excels at extremes '
                  '(Highly Volatile F1=0.59, Very Stable F1=0.46) \u2014 the most actionable classes.')

add_figure(doc, 'rf_confusion_matrix.png',
           'Figure 1: RF confusion matrix. Strong diagonal at Q1 and Q5; middle classes show diffuse misclassification.')

doc.add_heading('Feature Importance', level=3)
doc.add_paragraph('Permutation importance (model-agnostic, 30 repeats) ranks race_entropy_norm as #1. '
                  'This is the most reliable importance measure \u2014 it tests how much accuracy drops '
                  'when a feature is randomly shuffled.')

add_figure(doc, 'rf_permutation_importance.png',
           'Figure 2: Permutation importance \u2014 race_entropy_norm (diversity index) is the single most important feature.')

doc.add_paragraph('Challenge: Gini importance overweights continuous features. '
                  'Solution: Used permutation importance as the authoritative ranking.')

# --- 4.2 XGBoost ---
doc.add_heading('4.2 XGBoost', level=2)

method_box(doc, 'XGBoost (Gradient Boosting)',
    'Unlike Random Forest which builds trees independently, XGBoost builds them one at a time \u2014 '
    'each new tree specifically fixes mistakes from the previous ones. Like a student studying '
    'specifically the questions they got wrong. Often produces more accurate predictions for hard cases.')

bold_para(doc, 'Why chosen: ', 'Sequential error correction for hard middle classes; built-in regularization; '
          'SHAP integration for per-county explanations; state-of-the-art on tabular data.')
bold_para(doc, 'Assumptions: ', 'Additive model (prediction = sum of weak learners); regularization prevents overfitting.')

doc.add_heading('Hyperparameters', level=3)
add_table(doc,
    ['Setting', 'Search Space', 'Best', 'Controls'],
    [['n_estimators', '100\u2013500', '300', 'Total learning capacity'],
     ['max_depth', '3\u20138', '5', 'Complexity per tree'],
     ['learning_rate', '0.01\u20130.2', '0.1', 'Step size per tree'],
     ['subsample', '0.6\u20131.0', '0.8', 'Fraction of data per tree'],
     ['colsample_bytree', '0.6\u20131.0', '0.8', 'Fraction of features per tree'],
     ['reg_alpha (L1)', '0\u20131', '0.1', 'Feature selection penalty'],
     ['reg_lambda (L2)', '1\u201310', '5', 'Prediction smoothing']])

doc.add_heading('Results (5-Class)', level=3)
add_table(doc,
    ['Metric', 'Value'],
    [['Accuracy', '0.388 (best overall)'], ['Precision (macro)', '0.396'],
     ['Recall (macro)', '0.383'], ['F1-macro', '0.387 (best overall)'], ['ROC-AUC', '0.783']])

add_figure(doc, 'xgb_confusion_matrix.png',
           'Figure 3: XGBoost confusion matrix. Better middle-class separation, especially Stable (Q2).')

doc.add_heading('SHAP Analysis \u2014 Explaining Predictions', level=3)

method_box(doc, 'SHAP',
    'SHAP calculates how much each feature "pushed" each county\'s prediction toward high or low volatility. '
    'Like an itemized receipt: "+0.85 from high rent, +0.40 from high diversity, \u22120.30 from homeownership." '
    'Based on game theory; mathematically rigorous.')

add_figure(doc, 'xgb_shap_summary.png',
           'Figure 4: SHAP summary. Each dot = one county. Color = feature value (red=high, blue=low). '
           'Housing cost and diversity dominate.')

add_figure(doc, 'xgb_shap_dependence_top5.png',
           'Figure 5: Top 5 SHAP dependence plots. The diversity index shows a clear "step function" '
           '\u2014 volatility jumps once diversity crosses a threshold.')

doc.add_paragraph('Challenge: XGBoost requires 0-indexed labels. Solution: y \u2212 1 before fit, +1 after predict.')

# --- 4.3 SVM ---
doc.add_heading('4.3 SVM (Support Vector Machine)', level=2)

method_box(doc, 'SVM',
    'SVM draws a dividing line between classes and tries to make it as far as possible from '
    'the nearest data points on each side. The "kernel trick" allows the boundary to be curved (RBF) '
    'rather than straight (Linear). Comparing kernels tells us whether the data boundary is simple or complex.')

bold_para(doc, 'Why chosen: ', 'Margin-based learning; kernel comparison as diagnostic tool; '
          'theoretical generalization guarantees.')
bold_para(doc, 'Assumptions: ', 'Linear kernel: boundary is approximately straight. '
          'RBF kernel: similar counties behave similarly. Requires scaled features.')

doc.add_heading('Hyperparameters', level=3)
add_table(doc,
    ['Kernel', 'C', 'Gamma', 'class_weight', 'Best C'],
    [['Linear', '0.01\u2013100', 'N/A', 'balanced', '1'],
     ['RBF', '0.01\u2013100', 'scale, auto, 0.01\u20131', 'balanced', '10']])

doc.add_heading('Kernel Comparison', level=3)
add_table(doc,
    ['Metric', 'Linear', 'RBF'],
    [['Accuracy', '0.368', '0.340'],
     ['F1-macro', '0.364', '0.347'],
     ['ROC-AUC', '0.765', '0.741']])

doc.add_paragraph(
    'Linear > RBF in 5-class: the boundaries between 5 volatility levels are approximately straight. '
    'But this reverses in binary (RBF AUC=0.789 > Linear=0.734) \u2014 the single High/Low boundary '
    'is curved, consistent with the SHAP interaction effects (diversity matters differently by context).')

doc.add_paragraph('Challenge: No built-in feature importance. '
                  'Solution: Used RF/XGBoost for rankings; SVM served as a diagnostic benchmark (kernel comparison).')

takeaway(doc,
    'XGBoost is the best 5-class model (F1=0.387); RF has the best ROC-AUC (0.803). '
    'The diversity index is the #1 feature across all importance measures. '
    'SVM\'s kernel comparison reveals the volatile/stable boundary is moderately nonlinear. '
    'All models excel at extremes (Highly Volatile, Very Stable) and struggle with middle classes.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 5. MISFIT DETECTOR  (~3 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('5. Model D \u2014 Demographic Misfit Detector (Logistic Regression)', level=1)

method_box(doc, 'Logistic Regression',
    'One of the simplest classifiers \u2014 draws a straight line through data to separate groups '
    'and outputs a probability. Here we use it creatively: predict which party a county '
    '"should" vote for based on demographics, then analyze the errors.')

doc.add_heading('Two-Stage Approach', level=2)
doc.add_paragraph('Stage 1: Predict partisan lean from demographics. Accuracy: 89.6%.', style='List Bullet')
doc.add_paragraph('Stage 2: Find "misfits" \u2014 counties where the prediction is confidently wrong. '
                  'If demographics say 96% Republican but it votes Democrat, that\'s a misfit.', style='List Bullet')
doc.add_paragraph('Hypothesis: Misfits are communities in demographic transition, '
                  'and should therefore be more electorally volatile.')

doc.add_heading('Assumptions', level=2)
doc.add_paragraph('Linear decision boundary between D and R counties; P(Dem) is well-calibrated; '
                  'prediction errors capture demographic-political misalignment.')

doc.add_heading('Top 5 Misfits', level=2)
add_table(doc,
    ['County', 'State', 'Model Says', 'Actually', 'Misfit', 'Volatility'],
    [['Leelanau', 'MI', '96% Rep', 'Dem +8%', '0.96', 'Highly Volatile'],
     ['Marquette', 'MI', '96% Rep', 'Dem +9%', '0.96', 'Highly Volatile'],
     ['Nash', 'NC', '95% Dem', 'Rep \u22122%', '0.95', 'Very Stable'],
     ['Lenoir', 'NC', '94% Dem', 'Rep \u22127%', '0.94', 'Stable'],
     ['Cabarrus', 'NC', '87% Dem', 'Rep \u22128%', '0.87', 'Highly Volatile']])

add_figure(doc, 'misfit_scatter.png',
           'Figure 6: P(Dem) vs actual margin. Dot size = volatility. Counties far from diagonal are misfits.')

doc.add_heading('Misfit-Volatility Link', level=2)
add_table(doc,
    ['Finding', 'Test', 'Value'],
    [['Misfits are more volatile', 'Spearman \u03c1', '0.408 (p < 0.001)'],
     ['Misfits don\'t lean one way', 'Pearson r', '\u22120.017 (n.s.)']])

doc.add_heading('Misfit Profiling', level=2)
add_table(doc,
    ['Characteristic', 'Misfits', 'Non-Misfits', 'p-value'],
    [['Racial diversity', '0.567', '0.419', '< 0.0001'],
     ['Bachelor\'s+', '30.9%', '24.7%', '< 0.0001'],
     ['Homeownership', '71.1%', '76.3%', '< 0.0001'],
     ['Median rent', '$1,056', '$932', '< 0.0001'],
     ['Median age', '42.5', '44.5', '0.003']])
doc.add_paragraph('Misfits are younger, more diverse, more educated, higher-rent, and less rooted '
                  '\u2014 communities "in flux."')

doc.add_heading('Two Types of Misfits', level=2)
add_table(doc,
    ['Type', 'Count', 'Avg Volatility', 'Where'],
    [['"Surprise Dem"', '8/30', '0.807 (very high)', 'MI university/resort, PA Scranton'],
     ['"Surprise Rep"', '22/30', '0.383 (moderate)', 'NC rural South']])
doc.add_paragraph('"Surprise Dem" misfits are 2\u00d7 more volatile \u2014 university/resort towns '
                  'voting against their rural demographics are the most unstable counties.')

add_figure(doc, 'deepdive_misfit_by_volatility.png',
           'Figure 7: Misfit proportion rises from 6% (Very Stable) to 34% (Highly Volatile). '
           'Kruskal-Wallis p < 0.000001.')

takeaway(doc, 'Counties that defy demographic expectations are significantly more volatile (\u03c1=0.408). '
         'Misfits are younger, diverse, educated, transient \u2014 communities in transition. '
         '"Surprise Dem" misfits are the most volatile of all.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 6. BINARY CLASSIFICATION  (~3 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('6. Binary Classification \u2014 High vs Low Volatility', level=1)

doc.add_paragraph(
    'The 5-class task (F1~0.39) is limited by middle-class overlap. '
    'Collapsing to binary \u2014 High (Q4+Q5) vs Low (Q1\u2013Q3) \u2014 answers the actionable question: '
    '"Will this county swing significantly?"')

add_table(doc,
    ['Model', 'Accuracy', 'F1', 'Precision', 'Recall', 'AUC'],
    [['Random Forest', '0.780', '0.718', '0.726', '0.690', '0.828'],
     ['XGBoost', '0.748', '0.667', '0.718', '0.610', '0.803'],
     ['SVM (RBF)', '0.760', '0.674', '0.724', '0.630', '0.789'],
     ['Logistic Regression', '0.680', '0.604', '0.598', '0.610', '0.745'],
     ['SVM (Linear)', '0.688', '0.610', '0.610', '0.610', '0.734']])

doc.add_heading('5-Class \u2192 Binary Improvement', level=2)
add_table(doc,
    ['Metric', '5-Class Best', 'Binary Best', 'Improvement'],
    [['F1', '0.387 (XGBoost)', '0.718 (RF)', '+85%'],
     ['AUC', '0.803 (RF)', '0.828 (RF)', '+3%']])
doc.add_paragraph('Simplifying from 5 to 2 classes nearly doubles F1. '
                  'Problem framing matters more than algorithm choice.')

add_figure(doc, 'deepdive_binary_roc_all_models.png',
           'Figure 8: Binary ROC curves. RF (blue) achieves AUC = 0.828.')

doc.add_heading('Bootstrap Confidence Intervals (200 iterations \u00d7 5-fold CV)', level=2)
add_table(doc,
    ['Model', 'F1 [95% CI]', 'AUC [95% CI]', 'Accuracy [95% CI]'],
    [['Random Forest', '0.818 [0.764, 0.872]', '0.918 [0.882, 0.946]', '0.856 [0.816, 0.900]'],
     ['XGBoost', '0.845 [0.789, 0.899]', '0.932 [0.894, 0.966]', '0.880 [0.840, 0.920]']])
doc.add_paragraph('Tight CIs confirm results are robust, not artifacts of a lucky split.')

doc.add_heading('Feature Group Ablation', level=2)
add_table(doc,
    ['Group', 'n', 'F1 without', 'F1 drop', 'F1 alone'],
    [['Race / Ethnicity', '6', '0.626', '+0.092 (biggest)', '0.619 (86%)'],
     ['Urbanization', '6', '0.684', '+0.034', '0.583'],
     ['Education', '2', '0.708', '+0.010', '0.583'],
     ['Housing', '3', '0.712', '+0.006', '0.612'],
     ['Economic', '5', '0.722', '\u22120.004', '0.570'],
     ['Household / Age', '6', '0.728', '\u22120.010', '0.471']])

add_figure(doc, 'deepdive2_feature_ablation.png',
           'Figure 9: Feature ablation (left) and permutation importance with 95% CIs (right).')

takeaway(doc, 'Binary RF achieves F1=0.718 (AUC=0.828). Race/Ethnicity is both the most necessary '
         '(biggest F1 drop when removed) and most sufficient (86% of full alone) feature group. '
         'Economic and age variables are dispensable.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 7. COMPARISON & CROSS-STATE  (~3 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('7. Model Comparison & Cross-State Generalization', level=1)

doc.add_heading('7.1 Full Model Comparison', level=2)

bold_para(doc, '5-Class:')
add_table(doc,
    ['Model', 'Accuracy', 'F1-macro', 'ROC-AUC', 'Best At'],
    [['XGBoost', '0.388', '0.387', '0.783', 'Best overall'],
     ['SVM (Linear)', '0.368', '0.364', '0.765', 'Middle classes'],
     ['Random Forest', '0.368', '0.362', '0.803', 'Best ROC-AUC']])

bold_para(doc, 'Binary (including ensemble attempts):')
add_table(doc,
    ['Model', 'F1', 'AUC', 'Type'],
    [['Random Forest', '0.718', '0.828', 'Best overall'],
     ['Soft Voting', '0.691', '0.826', 'Ensemble (no improvement)'],
     ['XGBoost', '0.667', '0.803', 'Individual'],
     ['SVM (RBF)', '0.663', '0.819', 'Individual'],
     ['Stacking', '0.647', '0.816', 'Ensemble (hurts)'],
     ['Logistic Regression', '0.604', '0.745', 'Individual']])

doc.add_paragraph(
    'Ensembles do not improve on RF. Stacking hurts (F1: 0.718\u21920.647) because the meta-learner '
    'oversmooths with only n=250. The performance ceiling is dataset size, not algorithm sophistication.')

add_figure(doc, 'per_class_f1_heatmap.png',
           'Figure 10: Per-class F1 heatmap. All models excel at extremes, struggle in the middle.')

doc.add_heading('7.2 Cross-State Generalization \u2014 Do Demographics Transfer?', level=2)
doc.add_paragraph('LOSO: Train on 2 states, test on the 3rd. Scaler refit on training states only.')

add_table(doc,
    ['Test State', 'Train States', 'Accuracy', 'F1-macro'],
    [['Michigan', 'PA + NC', '0.205', '0.182'],
     ['North Carolina', 'PA + MI', '0.210', '0.213'],
     ['Pennsylvania', 'MI + NC', '0.209', '0.189'],
     ['', 'Random baseline (1/5)', '0.200', '0.200']])

bold_para(doc, 'Cross-state prediction collapses to random guessing.',
          ' Each state has a fundamentally different volatility signature:')

add_table(doc,
    ['Rank', 'PA (Diversity)', 'MI (Education)', 'NC (Poverty)'],
    [['#1', 'race_entropy_norm', 'pct_bachelors_plus', 'pct_below_poverty'],
     ['#2', 'log_median_gross_rent', 'log_median_gross_rent', 'log_median_gross_rent'],
     ['#3', 'pct_foreign_born', 'pct_work_from_home', 'log_population_density']])
doc.add_paragraph('Only log_median_gross_rent (housing cost) predicts volatility in all 3 states.')

add_figure(doc, 'deepdive_state_feature_importance.png',
           'Figure 11: Per-state feature importance. Dramatically different rankings in each state.')

add_figure(doc, 'loso_confusion_matrices.png',
           'Figure 12: LOSO confusion matrices. All three rotations = near-random.')

add_table(doc,
    ['State', 'n', 'Within-State AUC', 'Within-State F1'],
    [['PA', '67', '0.838', '0.591'],
     ['MI', '83', '0.778', '0.636'],
     ['NC', '100', '0.829', '0.736']])

takeaway(doc, 'Demographics predict volatility well within states (AUC 0.78\u20130.84) but fail across state lines. '
         'National models are fundamentally limited. Housing cost is the only universal predictor. '
         'Ensembles don\'t help at n=250.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 8. HYPOTHESIS TESTING  (~1.5 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('8. Hypothesis Testing', level=1)

doc.add_heading('H1: Wealth-Volatility Inverse \u2014 CONFIRMED', level=2)
add_table(doc,
    ['Evidence', 'Method', 'Result'],
    [['SHAP direction', 'Income SHAP vs Q5', 'r = \u22120.602 (p < 0.0001)'],
     ['Feature importance', 'Poverty rank', 'Top 5 in all models'],
     ['Partial dependence', 'Rent effect', 'Monotonic increase'],
     ['Ablation', 'Economic alone', 'F1 = 0.570 (insufficient alone)']])
doc.add_paragraph('Wealthier counties are more stable. But income alone is insufficient \u2014 '
                  'it interacts with diversity (wealthy diverse suburbs are volatile; wealthy homogeneous exurbs are not).')

doc.add_heading('H2: Diversity Index > Individual Race \u2014 CONFIRMED', level=2)
add_table(doc,
    ['Evidence', 'Method', 'Result'],
    [['Permutation importance', 'RF, 30 repeats', 'race_entropy_norm = #1'],
     ['SHAP importance', 'XGBoost', 'entropy 0.397 > pct_black 0.347'],
     ['PDP range', 'Probability swing', 'entropy = 0.14 (largest)'],
     ['Ablation', 'Race group alone', 'F1 = 0.619 (86% of baseline)'],
     ['Interactions', 'SHAP', 'entropy in 6/10 top interactions'],
     ['Threshold', 'Bootstrap', 'Odds ratio = 7.15\u00d7']])
doc.add_paragraph('Confirmed across 6 independent evidence streams. '
                  'It\'s racial mixing \u2014 not any single group \u2014 that predicts volatility.')

takeaway(doc, 'Both hypotheses confirmed. Wealth \u2192 stability (r=\u22120.602). '
         'Diversity index > all individual race vars (7\u00d7 odds ratio above threshold).')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 9. DEEP-DIVES  (~8 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('9. Advanced Analysis \u2014 Deep-Dives', level=1)

# 9.1 Temporal
doc.add_heading('9.1 Temporal Demographic Shifts (2016 \u2192 2024)', level=2)
doc.add_paragraph('Demographic change over 8 years also predicts volatility:')
add_table(doc,
    ['Change', '\u03c1', 'p-value', 'Meaning'],
    [['\u0394 pct_hispanic', '+0.220', '0.0005', 'Growing Hispanic pop \u2192 more volatile'],
     ['\u0394 median_gross_rent', '+0.209', '0.0009', 'Rising rents \u2192 more volatile'],
     ['\u0394 pct_two_or_more_races', '+0.209', '0.0009', 'Growing multiracial pop \u2192 more volatile'],
     ['\u0394 pct_black', '\u22120.194', '0.0020', 'Growing single group \u2192 less volatile']])
doc.add_paragraph('Diversification predicts volatility; growth of a single group does not.')
add_figure(doc, 'deepdive2_temporal_demographic_shifts.png',
           'Figure 13: Temporal shifts vs volatility. Correlations (left) and top scatter plots (right).')

# 9.2 Trajectories
doc.add_heading('9.2 Election Margin Trajectories', level=2)
add_table(doc,
    ['Trajectory', 'n', 'Mean Vol', '% High Vol', 'Pattern'],
    [['Blue Bounceback', '117 (47%)', '\u22120.17', '34%', 'D in 2020, snapped back 2024'],
     ['Steady Red Drift', '94 (38%)', '+0.39', '50%', 'R in both \u2014 most volatile'],
     ['Steady Blue Drift', '35 (14%)', '\u22120.28', '37%', 'D in both cycles'],
     ['Red Bounceback', '4 (2%)', '\u22121.82', '0%', 'Extremely rare']])
doc.add_paragraph('Blue Bounceback is dominant (47%) \u2014 the 2020 Biden surge was temporary. '
                  'Steady Red Drift is the most volatile (50%). '
                  'NC is different: 49% Steady Red Drift vs 27\u201333% in PA/MI.')
add_figure(doc, 'deepdive2_margin_trajectories.png',
           'Figure 14: Spaghetti trajectories by state. Each line = one county, colored by trajectory type.')

# 9.3 Threshold
doc.add_heading('9.3 The Diversity Threshold', level=2)
add_table(doc,
    ['Metric', 'Value'],
    [['Optimal threshold', 'race_entropy_norm = 0.552'],
     ['95% Bootstrap CI', '[0.397, 0.642]'],
     ['Below: % high vol', '24.4%'],
     ['Above: % high vol', '69.8%'],
     ['Odds ratio', '7.15\u00d7']])
doc.add_paragraph('Counties where no single race exceeds ~60% are 7\u00d7 more likely to be highly volatile. '
                  'P(high vol) jumps from ~20% to ~70% across the threshold \u2014 a switch, not a dial.')
add_figure(doc, 'deepdive2_diversity_threshold.png',
           'Figure 15: Diversity threshold. KDE distributions (left) and rolling probability curve (right).')

# 9.4 PDPs + Nonlinear interactions (combined)
doc.add_heading('9.4 Feature Effects & Interactions', level=2)

method_box(doc, 'Partial Dependence Plots',
    'PDPs show how one feature affects prediction, averaged across all others. '
    '"If we changed just this feature while keeping everything else constant, '
    'how would the predicted volatility change?"')

add_table(doc,
    ['Feature', 'Shape', 'Meaning'],
    [['Diversity index', 'Step function', 'Flat \u2192 jumps at threshold \u2192 plateaus'],
     ['Housing cost', 'Monotonic increase', 'Higher rent = higher P(volatile)'],
     ['Poverty rate', 'Late spike', 'Flat until extreme poverty, then jumps'],
     ['Married-couple %', 'Flat', 'Works only through interactions'],
     ['Bachelor\'s %', 'Slight upward', 'Modest effect at high education'],
     ['Pop. density', 'Uptick at extremes', 'Mostly interaction-driven']])

add_figure(doc, 'deepdive2_partial_dependence.png',
           'Figure 16: PDPs with ICE lines (top), 2D interaction contours (bottom-left), '
           'and PDP-based importance (bottom-right).')

bold_para(doc, 'Diversity \u00d7 Poverty \u2014 The Clearest Interaction:')
add_table(doc,
    ['Quadrant', 'n', 'Mean Vol', '% High Vol', '% Misfits'],
    [['Low Div + Low Poverty', '73', '\u22120.622', '19%', '11%'],
     ['Low Div + High Poverty', '52', '\u22120.669', '23%', '8%'],
     ['High Div + Low Poverty', '52', '+0.407', '60%', '27%'],
     ['High Div + High Poverty', '73', '+0.808', '59%', '33%']])
doc.add_paragraph('Diversity is the switch (triples high-vol rate). Poverty adds magnitude but not probability.')

add_figure(doc, 'deepdive_diversity_poverty_interaction.png',
           'Figure 17: Diversity \u00d7 Poverty quadrant analysis.')

bold_para(doc, 'Education \u00d7 Urbanization:')
add_table(doc,
    ['Quadrant', 'n', '% High Vol'],
    [['Low Ed + Rural', '89', '42%'],
     ['Low Ed + Urban', '36', '19% (least volatile)'],
     ['High Ed + Rural', '36', '33%'],
     ['High Ed + Urban', '89', '49% (most volatile)']])

add_figure(doc, 'deepdive_education_urbanization.png',
           'Figure 18: Education \u00d7 Urbanization. Least volatile = stable working-class cities. '
           'Most volatile = educated suburbs.')

# 9.5 SHAP Case Studies
doc.add_heading('9.5 SHAP Case Studies', level=2)
add_table(doc,
    ['County', 'Archetype', '#1 Driver', 'Story'],
    [['Bucks, PA', 'Suburban swing', 'Rent (+0.85)', '802k votes, 0.1% margin, bellwether'],
     ['Leelanau, MI', 'Misfit', 'Education (+1.50)', 'Rural/white but votes Dem'],
     ['Scotland, NC', 'Diverse-poor', 'Diversity (+1.25)', 'Highest volatility in dataset'],
     ['Philadelphia', 'Counter-example', 'Living alone (\u22120.80)', 'Diverse but STABLE \u2014\nurban density overrides']])
add_figure(doc, 'deepdive_shap_case_studies.png',
           'Figure 19: SHAP waterfall plots for 4 county archetypes.')

# 9.6 Archetypes
doc.add_heading('9.6 SHAP-Based County Archetypes', level=2)
doc.add_paragraph('K-Means on SHAP values (not raw features) reveals 5 functionally distinct county types:')
add_table(doc,
    ['Cluster', 'n', '% High Vol', 'Driver', 'States', 'Archetype'],
    [['0', '35', '100%', 'Diversity (1.54)', 'NC (33/35)', 'NC Diverse Rural'],
     ['1', '47', '0%', 'Small pop (0.82)', 'NC+MI', 'Stable Small'],
     ['2', '33', '91%', 'Immigration (0.66)', 'MI (21/33)', 'MI Working-Class'],
     ['3', '92', '0%', 'Low diversity (1.07)', 'All', 'Stable Core'],
     ['4', '43', '81%', 'Large pop (0.92)', 'PA+NC+MI', 'Suburban Battlegrounds']])
doc.add_paragraph('Near-perfect separation: 100%/0%/91%/0%/81%. '
                  'Cluster 0 is NC-only, Cluster 2 is MI-heavy \u2014 explains why LOSO fails.')
add_figure(doc, 'deepdive2_shap_archetypes.png',
           'Figure 20: SHAP archetypes. PCA projection (top-left), state composition (top-right), '
           'radar charts per cluster (bottom).')

# 9.7 Campaign Priority
doc.add_heading('9.7 Campaign Priority Scoring', level=2)
doc.add_paragraph('priority = 0.30\u00d7volatility + 0.25\u00d7misfit + 0.25\u00d7vote_volume + 0.20\u00d7margin_closeness')
add_table(doc,
    ['#', 'County', 'State', 'Priority', 'Votes', 'Margin', 'Volatility'],
    [['1', 'Bucks', 'PA', '0.650', '802,056', '\u22120.1%', 'Highly Volatile'],
     ['2', 'Lackawanna', 'PA', '0.574', '233,180', '+2.8%', 'Highly Volatile'],
     ['3', 'Cabarrus', 'NC', '0.570', '120,202', '\u22127.7%', 'Highly Volatile'],
     ['4', 'Leelanau', 'MI', '0.566', '17,685', '+7.8%', 'Highly Volatile'],
     ['5', 'Scotland', 'NC', '0.561', '14,626', '\u22126.9%', 'Highly Volatile'],
     ['6', 'Marquette', 'MI', '0.547', '39,009', '+8.7%', 'Highly Volatile'],
     ['7', 'Genesee', 'MI', '0.514', '223,268', '+4.2%', 'Volatile'],
     ['8', 'Monroe', 'PA', '0.492', '171,050', '\u22120.8%', 'Highly Volatile'],
     ['9', 'Isabella', 'MI', '0.492', '30,835', '\u22127.5%', 'Volatile'],
     ['10', 'Grand Traverse', 'MI', '0.484', '62,772', '\u22121.7%', 'Highly Volatile']])
add_figure(doc, 'deepdive_campaign_priority_scatter.png',
           'Figure 21: Campaign priority scatter (volatility \u00d7 misfit, bubble size = votes).')

takeaway(doc, 'Temporal analysis: diversifying counties are becoming more volatile. '
         'Blue Bounceback is the dominant trajectory (47%). '
         'The diversity threshold at 0.55 operates as a 7\u00d7 switch. '
         '5 SHAP archetypes reveal state-specific mechanisms. '
         'Bucks County PA is the #1 priority target nationally.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 10. GRAND SYNTHESIS  (~3 pages)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('10. Key Findings & Grand Synthesis', level=1)

doc.add_heading('The Volatility Formula', level=2)
bold_para(doc, '1. Racial diversity is the necessary condition.',
          ' The #1 predictor. Threshold at 0.55 = 7\u00d7 odds ratio. It\'s mixing, not any single group.')
bold_para(doc, '2. Economic transition is the amplifier.',
          ' Rising rents, poverty, education shifts amplify volatility in diverse counties.')
bold_para(doc, '3. State context is the moderator.',
          ' PA=diversity, MI=education, NC=poverty. National models fail.')

doc.add_heading('What Does NOT Predict Volatility', level=2)
doc.add_paragraph('Poverty alone (low-diversity poor counties are stable)', style='List Bullet')
doc.add_paragraph('Education alone (only with urbanization)', style='List Bullet')
doc.add_paragraph('Cross-state demographics (LOSO F1 = 0.195 = random)', style='List Bullet')
doc.add_paragraph('Swing direction (misfit r = \u22120.017)', style='List Bullet')

add_figure(doc, 'deepdive2_grand_synthesis.png',
           'Figure 22: Grand Synthesis \u2014 the complete story in 6 panels.',
           width=Inches(6.8))

add_figure(doc, 'choropleth_volatility_class.png',
           'Figure 23: Predicted volatility class by county.')

add_figure(doc, 'choropleth_misfit_score.png',
           'Figure 24: Demographic misfit scores. Top 15 misfits highlighted.')

doc.add_heading('Metrics At-a-Glance', level=2)
add_table(doc,
    ['Finding', 'Value'],
    [['Best binary F1', '0.718 (RF)'],
     ['Best 5-class F1', '0.387 (XGBoost)'],
     ['Bootstrap CI (RF)', 'F1: 0.818 [0.764, 0.872]'],
     ['Ensemble ceiling', 'F1 = 0.691 (no gain)'],
     ['Diversity threshold', '0.552 [0.397, 0.642]'],
     ['Diversity odds ratio', '7.15\u00d7'],
     ['Most necessary group', 'Race/Ethnicity (\u0394F1 = +0.092)'],
     ['Top temporal predictor', '\u0394 pct_hispanic (\u03c1 = +0.220)'],
     ['Most volatile trajectory', 'Steady Red Drift (50% high vol)'],
     ['#1 priority county', 'Bucks PA (802k, 0.1% margin)'],
     ['SHAP archetypes', '100%/0%/91%/0%/81% high vol'],
     ['Cross-state transfer', 'F1 = 0.195 (= random)'],
     ['H1 (income)', 'r = \u22120.602 (confirmed)'],
     ['H2 (entropy > race)', '#1 permutation (confirmed)'],
     ['Misfit-volatility', '\u03c1 = 0.408 (p < 0.001)']])

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
# 11. APPENDIX  (~1 page)
# ═══════════════════════════════════════════════════════════════
doc.add_heading('11. Appendix', level=1)

doc.add_heading('Notebooks', level=2)
add_table(doc,
    ['Notebook', 'Cells', 'Description'],
    [['classification_antoni.ipynb', '86', 'Core: RF, XGBoost, SVM, Misfit, LOSO, maps'],
     ['classification_antoni_deepdive.ipynb', '48', 'Deep-dive I: misfits, state models, SHAP, binary, campaigns'],
     ['classification_antoni_deepdive_2.ipynb', '30', 'Deep-dive II: temporal, PDPs, bootstrap, archetypes'],
     ['classification_antoni_deepdive_3.ipynb', '5', 'Grand synthesis figure']])

doc.add_heading('Data Files', level=2)
add_table(doc,
    ['File', 'Description'],
    [['classification_dataset_250.csv', '250 counties, 28 scaled features + targets'],
     ['classification_predictions.csv', 'All model predictions + misfit scores'],
     ['rf_predictions.csv', 'RF predictions for clustering comparison'],
     ['campaign_priority_rankings.csv', '250 counties with priority scores']])

doc.add_heading('Figures (24)', level=2)
figs = [
    ('1', 'RF confusion matrix (5-class)'), ('2', 'RF permutation importance'),
    ('3', 'XGBoost confusion matrix'), ('4', 'SHAP summary'),
    ('5', 'SHAP dependence (top 5)'), ('6', 'Misfit scatter'),
    ('7', 'Misfit by volatility class'), ('8', 'Binary ROC curves'),
    ('9', 'Feature ablation + permutation CIs'), ('10', 'Per-class F1 heatmap'),
    ('11', 'Per-state feature importance'), ('12', 'LOSO confusion matrices'),
    ('13', 'Temporal demographic shifts'), ('14', 'Margin trajectories'),
    ('15', 'Diversity threshold'), ('16', 'Partial dependence plots'),
    ('17', 'Diversity \u00d7 Poverty'), ('18', 'Education \u00d7 Urbanization'),
    ('19', 'SHAP case studies'), ('20', 'SHAP archetypes'),
    ('21', 'Campaign priority scatter'), ('22', 'Grand synthesis (6-panel)'),
    ('23', 'Choropleth: volatility'), ('24', 'Choropleth: misfit')]
add_table(doc, ['#', 'Description'], figs)

# ── Save ──
doc.save(OUT)
print(f'Saved: {OUT}')
