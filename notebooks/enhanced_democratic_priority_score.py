"""
Enhanced Democratic Priority Score
===================================
Integrates regression, clustering, classification, and temporal analysis
into a 5-component composite score for Democratic campaign resource allocation.

Author: Antoni Czolgowski
Date: April 2026
Project: Swing State Election Analysis (PA, MI, NC)
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
import warnings
warnings.filterwarnings('ignore')

# -- Configuration ----------------------------------------------------------
RANDOM_STATE = 42
BASE = '../data/processed'
FIG_DIR = '../docs/images/methods'
GEOJSON_URL = 'https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/US-counties.geojson'

STATE_FIPS = {'PA': '42', 'MI': '26', 'NC': '37'}
STATE_NAMES = {'PA': 'Pennsylvania', 'MI': 'Michigan', 'NC': 'North Carolina'}
STATE_OOF_FOLDS = {'PA': 4, 'MI': 5, 'NC': 5}

# Weights for 5 sub-scores (sum = 1.0)
# Competitiveness has been removed; remaining weights preserve the
# original balance after renormalizing the prior 0.80 total.
W_PERSUADABILITY = 0.25
W_ELECTORAL_WEIGHT = 0.25
W_PREDICTED_VOL = 0.25
W_DEM_OPPORTUNITY = 0.125
W_MISFIT = 0.125

# Persuasion-target score weights (sum = 1.0)
# Keep this intentionally simple and interpretable:
# persuadability, within-state vote importance, and predicted volatility.
W_PS_PERSUADABILITY = 0.50
W_PS_ELECTORAL_WEIGHT = 0.20
W_PS_PREDICTED_VOL = 0.30

# -- 1. Load & Merge All Data ----------------------------------------------
print("=" * 70)
print("ENHANCED DEMOCRATIC PRIORITY SCORE")
print("=" * 70)
print("\n[1/7] Loading data...")

# Raw master dataset (2024) -- has dem_margin in percentage points, total_votes
raw = pd.read_csv(f'{BASE}/master_dataset.csv', dtype={'county_fips': str})
raw_2024 = raw[raw['election_year'] == 2024][
    ['county_fips', 'state', 'county_name', 'total_population',
     'total_votes', 'dem_margin', 'dem_pct', 'rep_pct']
].copy()
raw_2024.rename(columns={
    'total_votes': 'total_votes_2024',
    'dem_margin': 'dem_margin_2024_pp',
    'total_population': 'population_2024'
}, inplace=True)

# Scaled dataset (2024) -- has raw race_entropy_norm (0-1)
scaled = pd.read_csv(f'{BASE}/master_dataset_scaled.csv', dtype={'county_fips': str})
scaled_2024 = scaled[scaled['election_year'] == 2024][
    ['county_fips', 'race_entropy_norm']
].copy()
scaled_2024.rename(columns={'race_entropy_norm': 'race_entropy_raw'}, inplace=True)

# Classification dataset -- 28 scaled features + vol_binary + vol_quintile
clf_df = pd.read_csv(f'{BASE}/classification_dataset_250.csv', dtype={'county_fips': str})

# Volatility dim table -- swing directions, magnitudes
dim = pd.read_csv(f'{BASE}/county_volatility_dimTable.csv', dtype={'county_fips': str})
dim_cols = dim[['county_fips', 'd_16_20', 'd_20_24', 'vol_z_abs_sum']].copy()

# K-Means clusters (drop county_name to avoid merge conflicts)
kmeans = pd.read_csv(f'{BASE}/kmeans_clusters.csv', dtype={'county_fips': str})
kmeans = kmeans[['county_fips', 'kmeans_cluster_label']].copy()

# Classification predictions -- p_dem, misfit_score (only needed cols)
preds = pd.read_csv(f'{BASE}/classification_predictions.csv', dtype={'county_fips': str})
preds_cols = preds[['county_fips', 'p_dem', 'misfit_score']].copy()

# Old priority scores (for comparison, only needed cols)
old_priority = pd.read_csv(f'{BASE}/campaign_priority_rankings.csv', dtype={'county_fips': str})
old_priority_cols = old_priority[['county_fips', 'priority_score', 'volatility_class']].copy()
old_priority_cols.rename(columns={'priority_score': 'old_priority_score'}, inplace=True)

# Merge everything on county_fips
df = raw_2024.copy()
df = df.merge(scaled_2024, on='county_fips', how='left')
df = df.merge(dim_cols, on='county_fips', how='left')
df = df.merge(kmeans, on='county_fips', how='left')
df = df.merge(preds_cols, on='county_fips', how='left')
df = df.merge(old_priority_cols, on='county_fips', how='left')

print(f"   Merged dataset: {df.shape[0]} counties, {df.shape[1]} columns")
assert df.shape[0] == 250, f"Expected 250 counties, got {df.shape[0]}"

# -- 2. Compute RF Predicted Volatility ------------------------------------
print("[2/7] Training Random Forest for predicted volatility...")

EXCLUDE_COLS = ['county_fips', 'state', 'county_name',
                'volatility_class', 'vol_quintile_num', 'vol_binary', 'vol_z_abs_sum']
FEATURE_COLS = [c for c in clf_df.columns if c not in EXCLUDE_COLS]

X = clf_df[FEATURE_COLS].values
y_binary = clf_df['vol_binary'].values

rf = RandomForestClassifier(
    n_estimators=500, max_depth=8, min_samples_leaf=5,
    random_state=RANDOM_STATE, n_jobs=-1
)
rf.fit(X, y_binary)
p_high_vol = rf.predict_proba(X)[:, 1]

# State-specific out-of-fold RF probabilities for persuasion. Each county is
# scored by a model trained on the other folds from its own state, so the
# prediction is no longer in-sample for that county.
state_rf_parts = []
for state_abbr, state_clf in clf_df.groupby('state', sort=False):
    X_state = state_clf[FEATURE_COLS].values
    y_state = state_clf['vol_binary'].values
    class_counts = pd.Series(y_state).value_counts()
    max_valid_folds = int(class_counts.min())
    requested_folds = STATE_OOF_FOLDS.get(state_abbr, 5)
    n_splits = max(2, min(requested_folds, max_valid_folds))

    if len(np.unique(y_state)) < 2:
        p_high_vol_state = np.full(len(state_clf), y_state[0], dtype=float)
    else:
        p_high_vol_state = np.zeros(len(state_clf), dtype=float)
        state_cv = StratifiedKFold(
            n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE
        )
        for train_idx, test_idx in state_cv.split(X_state, y_state):
            state_rf = RandomForestClassifier(
                n_estimators=500, max_depth=8, min_samples_leaf=5,
                random_state=RANDOM_STATE, n_jobs=-1
            )
            state_rf.fit(X_state[train_idx], y_state[train_idx])
            p_high_vol_state[test_idx] = state_rf.predict_proba(X_state[test_idx])[:, 1]

    print(
        f"      {state_abbr}: state OOF folds={n_splits}, "
        f"count={len(state_clf)}, high_vol={int(y_state.sum())}"
    )

    state_rf_parts.append(pd.DataFrame({
        'county_fips': state_clf['county_fips'].values,
        'p_high_vol_state_rf': p_high_vol_state
    }))

state_rf_probs = pd.concat(state_rf_parts, ignore_index=True)

# Map back to county_fips
rf_probs = pd.DataFrame({
    'county_fips': clf_df['county_fips'].values,
    'p_high_vol': p_high_vol
})
rf_probs = rf_probs.merge(state_rf_probs, on='county_fips', how='left')
df = df.merge(rf_probs, on='county_fips', how='left')

print(f"   RF P(high vol) range: [{p_high_vol.min():.3f}, {p_high_vol.max():.3f}]")
print(f"   RF mean P(high vol): {p_high_vol.mean():.3f}")
print(
    "   State-OOF RF P(high vol) range: "
    f"[{df['p_high_vol_state_rf'].min():.3f}, {df['p_high_vol_state_rf'].max():.3f}]"
)
print(f"   State-OOF RF mean P(high vol): {df['p_high_vol_state_rf'].mean():.3f}")
for state_abbr in ['PA', 'MI', 'NC']:
    state_mask = df['state'] == state_abbr
    pooled_mean = df.loc[state_mask, 'p_high_vol'].mean()
    state_mean = df.loc[state_mask, 'p_high_vol_state_rf'].mean()
    print(
        f"      {state_abbr}: pooled mean={pooled_mean:.3f}, "
        f"state-OOF mean={state_mean:.3f}"
    )

# -- 3. Compute Component Scores -------------------------------------------
print("[3/7] Computing score components...")

scaler = MinMaxScaler()

# --- S1: Persuadability Score (0.20) ---
# Soft sigmoid on diversity threshold at 0.552
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

diversity_signal = sigmoid((df['race_entropy_raw'].values - 0.552) * 10)

# K-Means cluster volatility rates (from cluster_means analysis)
# Cluster: mean vol_quintile -> convert to % high volatility estimate
# Cluster 2 (Poor&Diverse): vol_quintile=4.61 -> ~86% high vol
# Cluster 4 (Educated Urban): vol_quintile=3.69 -> ~73% high vol
# Cluster 0 (High-Diversity Urban): vol_quintile=3.21 -> ~62% high vol
# Cluster 1 (Affluent Stable): vol_quintile=3.0 -> ~49% high vol
# Cluster 3 (Rural Stable): vol_quintile=2.44 -> ~26% high vol
cluster_vol_rates = {2: 0.86, 4: 0.73, 0: 0.62, 1: 0.49, 3: 0.26}
cluster_vol = df['kmeans_cluster_label'].map(cluster_vol_rates).values
# Normalize cluster volatility rates to 0-1
cluster_vol_norm = (cluster_vol - 0.26) / (0.86 - 0.26)

df['S_persuadability'] = 0.60 * diversity_signal + 0.40 * cluster_vol_norm

# --- S2: Electoral Weight Score (0.25) ---
# Share of each state's vote pool captured by the county,
# softened with a square-root transform, then scaled within-state
# to keep this component on a 0-1 range.
state_total_votes = df.groupby('state')['total_votes_2024'].transform('sum')
state_vote_share = df['total_votes_2024'] / state_total_votes
state_vote_share_sqrt = np.sqrt(state_vote_share)
state_min_share = state_vote_share_sqrt.groupby(df['state']).transform('min')
state_max_share = state_vote_share_sqrt.groupby(df['state']).transform('max')
state_share_range = state_max_share - state_min_share
df['S_electoral_weight'] = np.where(
    state_share_range > 0,
    (state_vote_share_sqrt - state_min_share) / state_share_range,
    0.0
)

# --- S3: Predicted Volatility Score (0.25) ---
# Already 0-1 from RF predict_proba
df['S_volatility_predicted'] = df['p_high_vol']
df['S_volatility_predicted_state_rf'] = df['p_high_vol_state_rf']

# --- S4: Uncertainty Score (Persuasion only) ---
# Peaks when the classifier is maximally unsure around p_dem = 0.5.
df['S_uncertainty'] = np.clip(1 - 2 * np.abs(df['p_dem'].values - 0.5), 0, 1)

# --- S5: Democratic Opportunity Score (0.125) ---
# Positive d_20_24 = shifted toward Democrats in most recent cycle
# Positive d_16_20 = shifted toward Democrats 2016->2020
raw_opportunity = 0.65 * df['d_20_24'].values + 0.35 * df['d_16_20'].values
df['S_dem_opportunity'] = scaler.fit_transform(raw_opportunity.reshape(-1, 1)).ravel()

# --- S6: Demographic Misfit Score (0.125) ---
# Direction-adjusted: boost "Surprise Dem" misfits (2x more volatile empirically)
adjusted_misfit = df['misfit_score'].copy()
# Surprise Dem: model says Rep (p_dem < 0.5) but county voted Dem (margin > 0)
surprise_dem = (df['p_dem'] < 0.5) & (df['dem_margin_2024_pp'] > 0)
# Surprise Rep: model says Dem (p_dem > 0.5) but county voted Rep (margin < 0)
surprise_rep = (df['p_dem'] > 0.5) & (df['dem_margin_2024_pp'] < 0)

adjusted_misfit[surprise_dem] *= 1.3
adjusted_misfit[surprise_rep] *= 0.7

df['S_misfit'] = scaler.fit_transform(adjusted_misfit.values.reshape(-1, 1)).ravel()

# Print component statistics
for col in ['S_persuadability', 'S_electoral_weight', 'S_volatility_predicted',
            'S_volatility_predicted_state_rf', 'S_uncertainty',
            'S_dem_opportunity', 'S_misfit']:
    vals = df[col]
    print(f"   {col:25s}: mean={vals.mean():.3f}, min={vals.min():.3f}, max={vals.max():.3f}")

# -- 4. Combine into Final Scores ------------------------------------------
print("[4/7] Computing final scores...")

df['DPS'] = (
    W_PERSUADABILITY * df['S_persuadability'] +
    W_ELECTORAL_WEIGHT * df['S_electoral_weight'] +
    W_PREDICTED_VOL * df['S_volatility_predicted'] +
    W_DEM_OPPORTUNITY * df['S_dem_opportunity'] +
    W_MISFIT * df['S_misfit']
)

print(f"   DPS range: [{df['DPS'].min():.4f}, {df['DPS'].max():.4f}]")
print(f"   DPS mean: {df['DPS'].mean():.4f}, median: {df['DPS'].median():.4f}")

df['DPS_state_rf'] = (
    W_PERSUADABILITY * df['S_persuadability'] +
    W_ELECTORAL_WEIGHT * df['S_electoral_weight'] +
    W_PREDICTED_VOL * df['S_volatility_predicted_state_rf'] +
    W_DEM_OPPORTUNITY * df['S_dem_opportunity'] +
    W_MISFIT * df['S_misfit']
)

print(f"   DPS_state_rf range: [{df['DPS_state_rf'].min():.4f}, {df['DPS_state_rf'].max():.4f}]")
print(f"   DPS_state_rf mean: {df['DPS_state_rf'].mean():.4f}, median: {df['DPS_state_rf'].median():.4f}")

df['PersuasionScore'] = (
    W_PS_PERSUADABILITY * df['S_persuadability'] +
    W_PS_ELECTORAL_WEIGHT * df['S_electoral_weight'] +
    W_PS_PREDICTED_VOL * df['S_volatility_predicted_state_rf']
)

print(f"   PersuasionScore range: [{df['PersuasionScore'].min():.4f}, {df['PersuasionScore'].max():.4f}]")
print(f"   PersuasionScore mean: {df['PersuasionScore'].mean():.4f}, median: {df['PersuasionScore'].median():.4f}")

df['PersuasionScore_pooled'] = (
    W_PS_PERSUADABILITY * df['S_persuadability'] +
    W_PS_ELECTORAL_WEIGHT * df['S_electoral_weight'] +
    W_PS_PREDICTED_VOL * df['S_volatility_predicted']
)

print(
    "   PersuasionScore_pooled range: "
    f"[{df['PersuasionScore_pooled'].min():.4f}, {df['PersuasionScore_pooled'].max():.4f}]"
)
print(
    "   PersuasionScore_pooled mean: "
    f"{df['PersuasionScore_pooled'].mean():.4f}, "
    f"median: {df['PersuasionScore_pooled'].median():.4f}"
)

# -- 5. Generate Rankings -------------------------------------------------
print("[5/7] Generating rankings...")

# Clean county name for display (remove " County")
df['county_short'] = df['county_name'].str.replace(' County', '', regex=False)

# State-specific rankings
df['new_rank'] = df.groupby('state')['DPS'].rank(method='first', ascending=False).astype(int)
df['old_rank'] = df.groupby('state')['old_priority_score'].rank(method='first', ascending=False).astype(int)
df['rank_change'] = df['old_rank'] - df['new_rank']  # positive = moved up within-state
df['persuasion_rank'] = df.groupby('state')['PersuasionScore'].rank(method='first', ascending=False).astype(int)
df['new_rank_state_rf'] = df.groupby('state')['DPS_state_rf'].rank(method='first', ascending=False).astype(int)
df['persuasion_rank_pooled'] = df.groupby('state')['PersuasionScore_pooled'].rank(
    method='first', ascending=False
).astype(int)
df['dps_rank_shift_state_rf'] = df['new_rank'] - df['new_rank_state_rf']
df['persuasion_rank_shift_pooled'] = df['persuasion_rank_pooled'] - df['persuasion_rank']

state_counts = df.groupby('state')['county_fips'].transform('count')
df['state_priority_pct'] = np.where(
    state_counts > 1,
    1 - (df['new_rank'] - 1) / (state_counts - 1),
    1.0
)
df['state_persuasion_pct'] = np.where(
    state_counts > 1,
    1 - (df['persuasion_rank'] - 1) / (state_counts - 1),
    1.0
)

header = f"{'Rank':<5} {'County':<22} {'ST':<4} {'DPS':>6} | {'Persuad':>7} {'ElecWt':>7} {'PredVol':>7} {'DemOpp':>7} {'Misfit':>7} | {'Margin':>8} {'Votes':>10} {'VolClass':<16}"

# --- Top 5 per State ---
for state_abbr in ['PA', 'MI', 'NC']:
    state_df = df[df['state'] == state_abbr].sort_values('new_rank').head(5)
    print("\n" + "=" * 120)
    print(f"TOP 5 DEMOCRATIC PRIORITY COUNTIES -- {STATE_NAMES[state_abbr]} ({state_abbr})")
    print("-" * 120)
    print(header)
    print("-" * 120)
    for _, row in state_df.iterrows():
        print(f"{int(row['new_rank']):<5} {row['county_short']:<22} {row['state']:<4} {row['DPS']:>6.3f} | "
              f"{row['S_persuadability']:>7.3f} {row['S_electoral_weight']:>7.3f} "
              f"{row['S_volatility_predicted']:>7.3f} "
              f"{row['S_dem_opportunity']:>7.3f} {row['S_misfit']:>7.3f} | "
              f"{row['dem_margin_2024_pp']:>+7.1f}% {row['total_votes_2024']:>10,.0f} "
              f"{row['volatility_class']:<16}")

pers_header = (
    f"{'Rank':<5} {'County':<22} {'ST':<4} {'PS':>6} | "
    f"{'Persuad':>7} {'ElecWt':>7} {'PredVol':>7} | "
    f"{'D-Margin':>9} {'Votes':>10} {'VolClass':<16}"
)

# --- Top 5 Persuasion Targets per State ---
for state_abbr in ['PA', 'MI', 'NC']:
    state_df = df[df['state'] == state_abbr].sort_values('persuasion_rank').head(5)
    print("\n" + "=" * 120)
    print(f"TOP 5 PERSUASION TARGETS -- {STATE_NAMES[state_abbr]} ({state_abbr})")
    print("-" * 120)
    print(pers_header)
    print("-" * 120)
    for _, row in state_df.iterrows():
        print(f"{int(row['persuasion_rank']):<5} {row['county_short']:<22} {row['state']:<4} {row['PersuasionScore']:>6.3f} | "
              f"{row['S_persuadability']:>7.3f} {row['S_electoral_weight']:>7.3f} "
              f"{row['S_volatility_predicted']:>7.3f} | "
              f"{row['dem_margin_2024_pp']:>+9.1f}% {row['total_votes_2024']:>10,.0f} "
              f"{row['volatility_class']:<16}")

# --- Old vs New comparison ---
print(f"\n{'-' * 80}")
print("BIGGEST WITHIN-STATE RANK CHANGES (Old -> New)")
print("-" * 80)
movers = df.nlargest(10, 'rank_change')[['county_short', 'state', 'old_rank', 'new_rank', 'rank_change', 'DPS', 'old_priority_score']]
print(f"{'County':<22} {'ST':<4} {'Old#':>5} {'New#':>5} {'Chng':>5} {'NewDPS':>7} {'OldDPS':>7}")
for _, row in movers.iterrows():
    print(f"{row['county_short']:<22} {row['state']:<4} {row['old_rank']:>5} {row['new_rank']:>5} "
          f"{row['rank_change']:>+5} {row['DPS']:>7.3f} {row['old_priority_score']:>7.3f}")

# --- Validation ---
print(f"\n{'-' * 80}")
print("VALIDATION")
print("-" * 80)
corr = df['DPS'].corr(df['old_priority_score'])
print(f"   Pearson correlation (old vs new): r = {corr:.3f}")
pers_corr = df['DPS'].corr(df['PersuasionScore'])
print(f"   DPS vs PersuasionScore correlation: r = {pers_corr:.3f}")
for state_abbr in ['PA', 'MI', 'NC']:
    state_top5 = df[df['state'] == state_abbr].sort_values('new_rank').head(5)
    print(f"   {state_abbr} top-5 volatility classes: {state_top5['volatility_class'].value_counts().to_dict()}")
print(f"   Score distribution: skewness = {df['DPS'].skew():.3f}")

# -- 6. Save Enhanced Rankings ---------------------------------------------
print("\n[6/7] Saving enhanced rankings...")

output_cols = [
    'county_fips', 'state', 'county_name', 'population_2024',
    'total_votes_2024', 'dem_margin_2024_pp',
    'p_high_vol', 'p_high_vol_state_rf',
    'S_persuadability', 'S_electoral_weight', 'S_volatility_predicted',
    'S_volatility_predicted_state_rf',
    'S_uncertainty', 'S_dem_opportunity', 'S_misfit',
    'DPS', 'DPS_state_rf', 'PersuasionScore', 'PersuasionScore_pooled',
    'state_priority_pct', 'state_persuasion_pct',
    'old_priority_score', 'volatility_class', 'race_entropy_raw',
    'kmeans_cluster_label', 'new_rank', 'new_rank_state_rf',
    'persuasion_rank', 'persuasion_rank_pooled',
    'dps_rank_shift_state_rf', 'persuasion_rank_shift_pooled',
    'old_rank', 'rank_change'
]

output = df[output_cols].copy()
output['state_sort'] = pd.Categorical(output['state'], categories=['PA', 'MI', 'NC'], ordered=True)
output = output.sort_values(['state_sort', 'new_rank']).drop(columns='state_sort')
output.to_csv(f'{BASE}/enhanced_priority_rankings.csv', index=False)
print(f"   Saved: {BASE}/enhanced_priority_rankings.csv ({output.shape})")

persuasion_output_cols = [
    'county_fips', 'state', 'county_name', 'population_2024',
    'total_votes_2024', 'dem_margin_2024_pp',
    'p_high_vol', 'p_high_vol_state_rf',
    'S_persuadability', 'S_electoral_weight',
    'S_volatility_predicted', 'S_volatility_predicted_state_rf',
    'PersuasionScore', 'PersuasionScore_pooled',
    'state_persuasion_pct', 'persuasion_rank', 'persuasion_rank_pooled',
    'persuasion_rank_shift_pooled',
    'DPS', 'DPS_state_rf', 'state_priority_pct', 'new_rank', 'new_rank_state_rf',
    'dps_rank_shift_state_rf',
    'old_priority_score', 'volatility_class',
    'race_entropy_raw', 'kmeans_cluster_label'
]

persuasion_output = df[persuasion_output_cols].copy()
persuasion_output['state_sort'] = pd.Categorical(
    persuasion_output['state'], categories=['PA', 'MI', 'NC'], ordered=True
)
persuasion_output = persuasion_output.sort_values(
    ['state_sort', 'persuasion_rank']
).drop(columns='state_sort')
persuasion_output.to_csv(f'{BASE}/enhanced_persuasion_rankings.csv', index=False)
print(f"   Saved: {BASE}/enhanced_persuasion_rankings.csv ({persuasion_output.shape})")

# -- 7. Visualizations ----------------------------------------------------
print("\n[7/7] Creating visualizations...")

# Load GeoJSON
print("   Loading county boundaries...")
geo = gpd.read_file(GEOJSON_URL)
geo['id'] = geo['id'].astype(str).str.zfill(5)

# Merge with our data
geo_merged = geo.merge(df, left_on='id', right_on='county_fips', how='inner')
print(f"   Merged {len(geo_merged)} counties with geometry")

# Helper: filter by state
def get_state_geo(state_abbr):
    fips_prefix = STATE_FIPS[state_abbr]
    return geo_merged[geo_merged['county_fips'].str[:2] == fips_prefix].copy()

# State outlines (dissolved boundaries)
state_outlines = {}
for abbr in ['PA', 'MI', 'NC']:
    sg = get_state_geo(abbr)
    if len(sg) > 0:
        state_outlines[abbr] = sg.dissolve()

# -- MAP 1: Three-State Choropleth (within-state priority percentile) -----
print("   Creating Map 1: Three-state choropleth...")

fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.subplots_adjust(left=0.03, right=0.88, top=0.96, bottom=0.05, wspace=0.04)

for idx, (abbr, ax) in enumerate(zip(['PA', 'MI', 'NC'], axes)):
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    state_data.plot(
        column='state_priority_pct', ax=ax, cmap='YlOrRd',
        vmin=0, vmax=1,
        edgecolor='gray', linewidth=0.3,
        missing_kwds={'color': 'lightgray'}
    )

    # State outline
    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    ax.axis('off')

# Shared colorbar
sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=0, vmax=1))
sm.set_array([])
cax = fig.add_axes([0.895, 0.18, 0.014, 0.60])
cbar = fig.colorbar(sm, cax=cax, orientation='vertical')
cbar.set_label('Within-State Priority Percentile', fontsize=11)

plt.savefig(f'{FIG_DIR}/enhanced_priority_3state_choropleth.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("   OK Saved enhanced_priority_3state_choropleth.png")

# -- MAP 2: State Top-5 Highlight Map -------------------------------------
# Retain the legacy filename for compatibility with downstream report code.
print("   Creating Map 2: state top-5 highlight...")

fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.subplots_adjust(left=0.03, right=0.88, top=0.96, bottom=0.05, wspace=0.04)

for idx, (abbr, ax) in enumerate(zip(['PA', 'MI', 'NC'], axes)):
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    # All counties in light gray
    state_data.plot(ax=ax, color='#f0f0f0', edgecolor='#cccccc', linewidth=0.3)

    # State outline
    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    # Highlight top-5 counties in each state
    top5_state = state_data[state_data['new_rank'] <= 5]
    if len(top5_state) > 0:
        top5_state.plot(
            column='new_rank', ax=ax, cmap='YlOrRd_r',
            vmin=1, vmax=5,
            edgecolor='black', linewidth=2.4,
            missing_kwds={'color': 'lightgray'}
        )
        top5_state.boundary.plot(ax=ax, edgecolor='white', linewidth=3.8)
        top5_state.boundary.plot(ax=ax, edgecolor='black', linewidth=2.6)

        # Label top-5 counties with within-state rank
        texts = []
        for _, row in top5_state.iterrows():
            centroid = row.geometry.centroid
            label = f"#{int(row['new_rank'])} {row['county_short']}"
            txt = ax.annotate(
                label,
                xy=(centroid.x, centroid.y),
                fontsize=8.5, fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='gray', alpha=0.9),
                path_effects=[pe.withStroke(linewidth=2, foreground='white')]
            )
            texts.append(txt)

    ax.axis('off')

# Colorbar for top-5 rank scale
sm2 = plt.cm.ScalarMappable(cmap='YlOrRd_r', norm=mcolors.Normalize(vmin=1, vmax=5))
sm2.set_array([])
cax2 = fig.add_axes([0.895, 0.18, 0.014, 0.60])
cbar2 = fig.colorbar(sm2, cax=cax2, orientation='vertical')
cbar2.set_label('Within-State Rank (1 = highest priority)', fontsize=11)
plt.savefig(f'{FIG_DIR}/enhanced_priority_top10_highlight.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("   OK Saved enhanced_priority_top10_highlight.png")

# -- MAPS 3-5: Individual State Maps with Top 5 --------------------------
print("   Creating Maps 3-5: Individual state maps...")

for abbr in ['PA', 'MI', 'NC']:
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    state_top5 = df[df['state'] == abbr].sort_values('new_rank').head(5)
    top5_fips = set(state_top5['county_fips'].values)

    figw = 16 if abbr == 'MI' else 14
    fig, ax = plt.subplots(1, 1, figsize=(figw, 10))
    fig.subplots_adjust(left=0.04, right=0.82, top=0.97, bottom=0.04)

    # All counties shaded by within-state priority percentile
    state_data.plot(
        column='state_priority_pct', ax=ax, cmap='YlOrRd',
        vmin=0, vmax=1,
        edgecolor='gray', linewidth=0.4,
        missing_kwds={'color': 'lightgray'}
    )

    xmin, ymin, xmax, ymax = state_data.total_bounds
    xpad = (xmax - xmin) * 0.12
    ypad = (ymax - ymin) * 0.12
    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)

    # State outline
    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=2)

    # Highlight top-5 with thick borders
    top5_geo = state_data[state_data['county_fips'].isin(top5_fips)]
    if len(top5_geo) > 0:
        top5_geo.boundary.plot(ax=ax, edgecolor='white', linewidth=4.8)
        top5_geo.boundary.plot(ax=ax, edgecolor='black', linewidth=3.4)

    # Annotate top 5 with callout arrows to make county targets clearer
    state_label_offsets = {
        'PA': {
            'Philadelphia': (110, 30),
            'Montgomery': (185, 110),
            'Delaware': (135, -175),
            'Allegheny': (-220, -60),
            'Chester': (-85, -145),
        },
        'MI': {
            'Oakland': (190, 120),
            'Wayne': (-150, -15),
            'Kent': (-80, 145),
            'Macomb': (190, -55),
            'Washtenaw': (-140, -115),
        },
        'NC': {
            'Wake': (110, 150),
            'Mecklenburg': (-220, 115),
            'Cabarrus': (80, 95),
            'Durham': (-235, -105),
            'Lenoir': (150, -35),
        },
    }
    for _, row in state_top5.iterrows():
        # Find geometry from geo_merged
        geo_row = geo_merged[geo_merged['county_fips'] == row['county_fips']]
        if len(geo_row) == 0:
            continue
        centroid = geo_row.geometry.values[0].centroid
        state_rank_num = int(row['new_rank'])
        county_key = row['county_short']
        dx, dy = state_label_offsets.get(abbr, {}).get(county_key, (0, 0))
        label = f"#{state_rank_num} {row['county_short']}\nDPS: {row['DPS']:.3f} | D-Margin: {row['dem_margin_2024_pp']:+.1f}%"

        ax.annotate(
            label,
            xy=(centroid.x, centroid.y),
            xytext=(dx, dy),
            textcoords='offset points',
            fontsize=14, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#333333',
                      alpha=0.92, linewidth=1.5),
            arrowprops=dict(
                arrowstyle='-|>',
                color='#222222',
                lw=2.0,
                mutation_scale=16,
                shrinkA=3,
                shrinkB=3
            ),
            annotation_clip=False,
            path_effects=[pe.withStroke(linewidth=2, foreground='white')]
        )
    ax.axis('off')

    # Keep the legend only on the North Carolina state map.
    if abbr == 'NC':
        sm3 = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=0, vmax=1))
        sm3.set_array([])
        cax3 = fig.add_axes([0.885, 0.24, 0.014, 0.48])
        cbar3 = fig.colorbar(sm3, cax=cax3, orientation='vertical')
        cbar3.set_label('Within-State Priority Percentile', fontsize=11)

    plt.savefig(f'{FIG_DIR}/enhanced_priority_{abbr}_top5.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   OK Saved enhanced_priority_{abbr}_top5.png")

# -- MAPS 6-10: PersuasionScore Visualizations ----------------------------
print("   Creating PersuasionScore maps...")

# Map 6: Three-state persuasion choropleth
fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.subplots_adjust(left=0.03, right=0.88, top=0.96, bottom=0.05, wspace=0.04)

for idx, (abbr, ax) in enumerate(zip(['PA', 'MI', 'NC'], axes)):
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    state_data.plot(
        column='state_persuasion_pct', ax=ax, cmap='YlOrRd',
        vmin=0, vmax=1,
        edgecolor='gray', linewidth=0.3,
        missing_kwds={'color': 'lightgray'}
    )

    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    ax.axis('off')

sm_p = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=0, vmax=1))
sm_p.set_array([])
cax_p = fig.add_axes([0.895, 0.18, 0.014, 0.60])
cbar_p = fig.colorbar(sm_p, cax=cax_p, orientation='vertical')
cbar_p.set_label('Within-State Persuasion Percentile', fontsize=11)

plt.savefig(f'{FIG_DIR}/enhanced_persuasion_3state_choropleth.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("   OK Saved enhanced_persuasion_3state_choropleth.png")

# Map 7: Three-state top-5 persuasion highlight
fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.subplots_adjust(left=0.03, right=0.88, top=0.96, bottom=0.05, wspace=0.04)

for idx, (abbr, ax) in enumerate(zip(['PA', 'MI', 'NC'], axes)):
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    state_data.plot(ax=ax, color='#f0f0f0', edgecolor='#cccccc', linewidth=0.3)

    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    top5_state = state_data[state_data['persuasion_rank'] <= 5]
    if len(top5_state) > 0:
        top5_state.plot(
            column='persuasion_rank', ax=ax, cmap='YlOrRd_r',
            vmin=1, vmax=5,
            edgecolor='black', linewidth=2.4,
            missing_kwds={'color': 'lightgray'}
        )
        top5_state.boundary.plot(ax=ax, edgecolor='white', linewidth=3.8)
        top5_state.boundary.plot(ax=ax, edgecolor='black', linewidth=2.6)

        for _, row in top5_state.iterrows():
            centroid = row.geometry.centroid
            label = f"#{int(row['persuasion_rank'])} {row['county_short']}"
            ax.annotate(
                label,
                xy=(centroid.x, centroid.y),
                fontsize=8.5, fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='gray', alpha=0.9),
                path_effects=[pe.withStroke(linewidth=2, foreground='white')]
            )

    ax.axis('off')

sm2_p = plt.cm.ScalarMappable(cmap='YlOrRd_r', norm=mcolors.Normalize(vmin=1, vmax=5))
sm2_p.set_array([])
cax2_p = fig.add_axes([0.895, 0.18, 0.014, 0.60])
cbar2_p = fig.colorbar(sm2_p, cax=cax2_p, orientation='vertical')
cbar2_p.set_label('Within-State Persuasion Rank (1 = highest)', fontsize=11)
plt.savefig(f'{FIG_DIR}/enhanced_persuasion_top5_highlight.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("   OK Saved enhanced_persuasion_top5_highlight.png")

# Maps 8-10: Individual state persuasion maps
for abbr in ['PA', 'MI', 'NC']:
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    state_top5 = df[df['state'] == abbr].sort_values('persuasion_rank').head(5)
    top5_fips = set(state_top5['county_fips'].values)

    figw = 16 if abbr == 'MI' else 14
    fig, ax = plt.subplots(1, 1, figsize=(figw, 10))
    fig.subplots_adjust(left=0.04, right=0.82, top=0.97, bottom=0.04)

    state_data.plot(
        column='state_persuasion_pct', ax=ax, cmap='YlOrRd',
        vmin=0, vmax=1,
        edgecolor='gray', linewidth=0.4,
        missing_kwds={'color': 'lightgray'}
    )

    xmin, ymin, xmax, ymax = state_data.total_bounds
    xpad = (xmax - xmin) * 0.12
    ypad = (ymax - ymin) * 0.12
    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)

    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=2)

    top5_geo = state_data[state_data['county_fips'].isin(top5_fips)]
    if len(top5_geo) > 0:
        top5_geo.boundary.plot(ax=ax, edgecolor='white', linewidth=4.8)
        top5_geo.boundary.plot(ax=ax, edgecolor='black', linewidth=3.4)

    persuasion_label_offsets = {
        'PA': {
            'Philadelphia': (110, 35),
            'Delaware': (85, -110),
            'Allegheny': (-140, 120),
            'Montgomery': (190, 110),
            'Lehigh': (-90, 155),
        },
        'MI': {
            'Oakland': (210, 150),
            'Wayne': (215, 35),
            'Washtenaw': (-80, 155),
            'Ingham': (20, -140),
            'Kent': (-170, -75),
        },
        'NC': {
            'Wake': (130, 120),
            'Mecklenburg': (-170, -115),
            'Lenoir': (110, -145),
            'Halifax': (-70, 170),
            'Richmond': (-180, 95),
        },
    }
    for _, row in state_top5.iterrows():
        geo_row = geo_merged[geo_merged['county_fips'] == row['county_fips']]
        if len(geo_row) == 0:
            continue
        centroid = geo_row.geometry.values[0].centroid
        state_rank_num = int(row['persuasion_rank'])
        county_key = row['county_short']
        dx, dy = persuasion_label_offsets.get(abbr, {}).get(county_key, (0, 0))
        label = f"#{state_rank_num} {row['county_short']}\nPS: {row['PersuasionScore']:.3f} | D-Margin: {row['dem_margin_2024_pp']:+.1f}%"

        ax.annotate(
            label,
            xy=(centroid.x, centroid.y),
            xytext=(dx, dy),
            textcoords='offset points',
            fontsize=14, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#333333',
                      alpha=0.92, linewidth=1.5),
            arrowprops=dict(
                arrowstyle='-|>',
                color='#222222',
                lw=2.0,
                mutation_scale=16,
                shrinkA=3,
                shrinkB=3
            ),
            annotation_clip=False,
            path_effects=[pe.withStroke(linewidth=2, foreground='white')]
        )
    ax.axis('off')

    if abbr == 'NC':
        sm3_p = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=0, vmax=1))
        sm3_p.set_array([])
        cax3_p = fig.add_axes([0.885, 0.24, 0.014, 0.48])
        cbar3_p = fig.colorbar(sm3_p, cax=cax3_p, orientation='vertical')
        cbar3_p.set_label('Priority Percentile', fontsize=12)

    plt.savefig(f'{FIG_DIR}/enhanced_persuasion_{abbr}_top5.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   OK Saved enhanced_persuasion_{abbr}_top5.png")

print("\n" + "=" * 70)
print("ALL DONE -- Enhanced Democratic Priority Score complete.")
print(f"   Rankings: {BASE}/enhanced_priority_rankings.csv")
print(f"   DPS maps: {FIG_DIR}/enhanced_priority_*.png (5 files)")
print(f"   Persuasion maps: {FIG_DIR}/enhanced_persuasion_*.png (5 files)")
print("=" * 70)
