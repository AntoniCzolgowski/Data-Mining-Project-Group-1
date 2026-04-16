"""
Enhanced Democratic Priority Score
===================================
Integrates regression, clustering, classification, and temporal analysis
into a 6-component composite score for Democratic campaign resource allocation.

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
from adjustText import adjust_text
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

# -- Configuration ----------------------------------------------------------
RANDOM_STATE = 42
BASE = '../data/processed'
FIG_DIR = '../docs/images/methods'
GEOJSON_URL = 'https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/US-counties.geojson'

STATE_FIPS = {'PA': '42', 'MI': '26', 'NC': '37'}
STATE_NAMES = {'PA': 'Pennsylvania', 'MI': 'Michigan', 'NC': 'North Carolina'}

# Weights for 6 sub-scores (sum = 1.0)
W_PERSUADABILITY = 0.20
W_ELECTORAL_WEIGHT = 0.20
W_COMPETITIVENESS = 0.20
W_PREDICTED_VOL = 0.20
W_DEM_OPPORTUNITY = 0.10
W_MISFIT = 0.10

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

# Map back to county_fips
rf_probs = pd.DataFrame({
    'county_fips': clf_df['county_fips'].values,
    'p_high_vol': p_high_vol
})
df = df.merge(rf_probs, on='county_fips', how='left')

print(f"   RF P(high vol) range: [{p_high_vol.min():.3f}, {p_high_vol.max():.3f}]")
print(f"   RF mean P(high vol): {p_high_vol.mean():.3f}")

# -- 3. Compute 6 Sub-Scores ----------------------------------------------
print("[3/7] Computing 6 sub-scores...")

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

# --- S2: Electoral Weight Score (0.20) ---
log_votes = np.log1p(df['total_votes_2024'].values)
df['S_electoral_weight'] = scaler.fit_transform(log_votes.reshape(-1, 1)).ravel()

# --- S3: Competitiveness Score (0.20) ---
# Exponential decay: exp(-|margin| / tau), tau=10 percentage points
tau = 10.0
df['S_competitiveness'] = np.exp(-np.abs(df['dem_margin_2024_pp'].values) / tau)

# --- S4: Predicted Volatility Score (0.20) ---
# Already 0-1 from RF predict_proba
df['S_volatility_predicted'] = df['p_high_vol']

# --- S5: Democratic Opportunity Score (0.10) ---
# Positive d_20_24 = shifted toward Democrats in most recent cycle
# Positive d_16_20 = shifted toward Democrats 2016->2020
raw_opportunity = 0.65 * df['d_20_24'].values + 0.35 * df['d_16_20'].values
df['S_dem_opportunity'] = scaler.fit_transform(raw_opportunity.reshape(-1, 1)).ravel()

# --- S6: Demographic Misfit Score (0.10) ---
# Direction-adjusted: boost "Surprise Dem" misfits (2x more volatile empirically)
adjusted_misfit = df['misfit_score'].copy()
# Surprise Dem: model says Rep (p_dem < 0.5) but county voted Dem (margin > 0)
surprise_dem = (df['p_dem'] < 0.5) & (df['dem_margin_2024_pp'] > 0)
# Surprise Rep: model says Dem (p_dem > 0.5) but county voted Rep (margin < 0)
surprise_rep = (df['p_dem'] > 0.5) & (df['dem_margin_2024_pp'] < 0)

adjusted_misfit[surprise_dem] *= 1.3
adjusted_misfit[surprise_rep] *= 0.7

df['S_misfit'] = scaler.fit_transform(adjusted_misfit.values.reshape(-1, 1)).ravel()

# Print sub-score statistics
for col in ['S_persuadability', 'S_electoral_weight', 'S_competitiveness',
            'S_volatility_predicted', 'S_dem_opportunity', 'S_misfit']:
    vals = df[col]
    print(f"   {col:25s}: mean={vals.mean():.3f}, min={vals.min():.3f}, max={vals.max():.3f}")

# -- 4. Combine into Final Composite Score ---------------------------------
print("[4/7] Computing final Democratic Priority Score...")

df['DPS'] = (
    W_PERSUADABILITY * df['S_persuadability'] +
    W_ELECTORAL_WEIGHT * df['S_electoral_weight'] +
    W_COMPETITIVENESS * df['S_competitiveness'] +
    W_PREDICTED_VOL * df['S_volatility_predicted'] +
    W_DEM_OPPORTUNITY * df['S_dem_opportunity'] +
    W_MISFIT * df['S_misfit']
)

print(f"   DPS range: [{df['DPS'].min():.4f}, {df['DPS'].max():.4f}]")
print(f"   DPS mean: {df['DPS'].mean():.4f}, median: {df['DPS'].median():.4f}")

# -- 5. Generate Rankings -------------------------------------------------
print("[5/7] Generating rankings...")

# Clean county name for display (remove " County")
df['county_short'] = df['county_name'].str.replace(' County', '', regex=False)

# --- Top 10 Overall ---
top10 = df.nlargest(10, 'DPS')
print("\n" + "=" * 120)
print("TOP 10 DEMOCRATIC PRIORITY COUNTIES (OVERALL)")
print("=" * 120)
header = f"{'Rank':<5} {'County':<22} {'ST':<4} {'DPS':>6} | {'Persuad':>7} {'ElecWt':>7} {'Compet':>7} {'PredVol':>7} {'DemOpp':>7} {'Misfit':>7} | {'Margin':>8} {'Votes':>10} {'VolClass':<16}"
print(header)
print("-" * 120)
for i, (_, row) in enumerate(top10.iterrows(), 1):
    print(f"{i:<5} {row['county_short']:<22} {row['state']:<4} {row['DPS']:>6.3f} | "
          f"{row['S_persuadability']:>7.3f} {row['S_electoral_weight']:>7.3f} "
          f"{row['S_competitiveness']:>7.3f} {row['S_volatility_predicted']:>7.3f} "
          f"{row['S_dem_opportunity']:>7.3f} {row['S_misfit']:>7.3f} | "
          f"{row['dem_margin_2024_pp']:>+7.1f}% {row['total_votes_2024']:>10,.0f} "
          f"{row['volatility_class']:<16}")

# --- Top 5 per State ---
for state_abbr in ['PA', 'MI', 'NC']:
    state_df = df[df['state'] == state_abbr].nlargest(5, 'DPS')
    print(f"\n{'-' * 120}")
    print(f"TOP 5 -- {STATE_NAMES[state_abbr]} ({state_abbr})")
    print("-" * 120)
    print(header)
    print("-" * 120)
    for i, (_, row) in enumerate(state_df.iterrows(), 1):
        print(f"{i:<5} {row['county_short']:<22} {row['state']:<4} {row['DPS']:>6.3f} | "
              f"{row['S_persuadability']:>7.3f} {row['S_electoral_weight']:>7.3f} "
              f"{row['S_competitiveness']:>7.3f} {row['S_volatility_predicted']:>7.3f} "
              f"{row['S_dem_opportunity']:>7.3f} {row['S_misfit']:>7.3f} | "
              f"{row['dem_margin_2024_pp']:>+7.1f}% {row['total_votes_2024']:>10,.0f} "
              f"{row['volatility_class']:<16}")

# --- Old vs New comparison ---
df['new_rank'] = df['DPS'].rank(ascending=False).astype(int)
df['old_rank'] = df['old_priority_score'].rank(ascending=False).astype(int)
df['rank_change'] = df['old_rank'] - df['new_rank']  # positive = moved up

print(f"\n{'-' * 80}")
print("BIGGEST RANK CHANGES (Old -> New)")
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
print(f"   Top 10 volatility classes: {top10['volatility_class'].value_counts().to_dict()}")
print(f"   Score distribution: skewness = {df['DPS'].skew():.3f}")

# -- 6. Save Enhanced Rankings ---------------------------------------------
print("\n[6/7] Saving enhanced rankings...")

output_cols = [
    'county_fips', 'state', 'county_name', 'population_2024',
    'total_votes_2024', 'dem_margin_2024_pp',
    'S_persuadability', 'S_electoral_weight', 'S_competitiveness',
    'S_volatility_predicted', 'S_dem_opportunity', 'S_misfit',
    'DPS', 'old_priority_score', 'volatility_class',
    'race_entropy_raw', 'kmeans_cluster_label', 'new_rank', 'old_rank', 'rank_change'
]

output = df[output_cols].sort_values('DPS', ascending=False)
output.to_csv(f'{BASE}/enhanced_priority_rankings.csv', index=False)
print(f"   Saved: {BASE}/enhanced_priority_rankings.csv ({output.shape})")

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

# -- MAP 1: Three-State Choropleth (all counties by DPS) ------------------
print("   Creating Map 1: Three-state choropleth...")

fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.suptitle('Democratic Priority Score by County (2024 Demographics)\nEnhanced Model: 6-Component Composite | 0 = Low Priority, 1 = High Priority',
             fontsize=14, fontweight='bold', y=0.98)

vmax = df['DPS'].quantile(0.98)  # clip top 2% for better color range

for idx, (abbr, ax) in enumerate(zip(['PA', 'MI', 'NC'], axes)):
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    state_data.plot(
        column='DPS', ax=ax, cmap='YlOrRd',
        vmin=0, vmax=vmax,
        edgecolor='gray', linewidth=0.3,
        missing_kwds={'color': 'lightgray'}
    )

    # State outline
    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    ax.set_title(STATE_NAMES[abbr], fontsize=13, fontweight='bold')
    ax.axis('off')

# Shared colorbar
sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=0, vmax=vmax))
sm.set_array([])
cbar = fig.colorbar(sm, ax=axes, orientation='vertical', fraction=0.02, pad=0.02)
cbar.set_label('Democratic Priority Score', fontsize=11)

plt.tight_layout(rect=[0, 0, 0.95, 0.93])
plt.savefig(f'{FIG_DIR}/enhanced_priority_3state_choropleth.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("   OK Saved enhanced_priority_3state_choropleth.png")

# -- MAP 2: Top 10 Highlight Map ------------------------------------------
print("   Creating Map 2: Top 10 highlight...")

top10_fips = set(top10['county_fips'].values)
top10_min = top10['DPS'].min()
top10_max = top10['DPS'].max()

fig, axes = plt.subplots(1, 3, figsize=(22, 7))
fig.suptitle('Top 10 Democratic Priority Counties Across Swing States\nHighest-Value Targets for Campaign Resource Allocation',
             fontsize=14, fontweight='bold', y=0.98)

for idx, (abbr, ax) in enumerate(zip(['PA', 'MI', 'NC'], axes)):
    state_data = get_state_geo(abbr)
    if len(state_data) == 0:
        continue

    # All counties in light gray
    state_data.plot(ax=ax, color='#f0f0f0', edgecolor='#cccccc', linewidth=0.3)

    # State outline
    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=1.5)

    # Highlight top-10 counties
    top10_state = state_data[state_data['county_fips'].isin(top10_fips)]
    if len(top10_state) > 0:
        top10_state.plot(
            column='DPS', ax=ax, cmap='YlOrRd',
            vmin=top10_min, vmax=top10_max,
            edgecolor='black', linewidth=1.8,
            missing_kwds={'color': 'lightgray'}
        )

        # Label top-10 counties
        texts = []
        for _, row in top10_state.iterrows():
            centroid = row.geometry.centroid
            rank = int(row['new_rank'])
            label = f"#{rank} {row['county_short']}"
            txt = ax.annotate(
                label,
                xy=(centroid.x, centroid.y),
                fontsize=7.5, fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='gray', alpha=0.9),
                path_effects=[pe.withStroke(linewidth=2, foreground='white')]
            )
            texts.append(txt)

    ax.set_title(STATE_NAMES[abbr], fontsize=13, fontweight='bold')
    ax.axis('off')

# Colorbar for top-10 scale
sm2 = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=top10_min, vmax=top10_max))
sm2.set_array([])
cbar2 = fig.colorbar(sm2, ax=axes, orientation='vertical', fraction=0.02, pad=0.02)
cbar2.set_label('Priority Score (Top 10 relative scale)', fontsize=11)

plt.tight_layout(rect=[0, 0, 0.95, 0.93])
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

    state_top5 = df[df['state'] == abbr].nlargest(5, 'DPS')
    top5_fips = set(state_top5['county_fips'].values)

    figw = 14 if abbr == 'MI' else 12
    fig, ax = plt.subplots(1, 1, figsize=(figw, 9))

    # All counties shaded by DPS
    state_vmax = state_data['DPS'].max()
    state_data.plot(
        column='DPS', ax=ax, cmap='YlOrRd',
        vmin=0, vmax=state_vmax,
        edgecolor='gray', linewidth=0.4,
        missing_kwds={'color': 'lightgray'}
    )

    # State outline
    if abbr in state_outlines:
        state_outlines[abbr].boundary.plot(ax=ax, edgecolor='black', linewidth=2)

    # Highlight top-5 with thick borders
    top5_geo = state_data[state_data['county_fips'].isin(top5_fips)]
    if len(top5_geo) > 0:
        top5_geo.boundary.plot(ax=ax, edgecolor='black', linewidth=2.5)

    # Annotate top 5
    texts = []
    for _, row in state_top5.iterrows():
        # Find geometry from geo_merged
        geo_row = geo_merged[geo_merged['county_fips'] == row['county_fips']]
        if len(geo_row) == 0:
            continue
        centroid = geo_row.geometry.values[0].centroid
        state_rank = int(row.name) if isinstance(row.name, (int, np.integer)) else 0

        # Get rank within state
        state_sorted = df[df['state'] == abbr].sort_values('DPS', ascending=False)
        state_rank_num = state_sorted.index.get_loc(row.name) + 1 if row.name in state_sorted.index else 0

        label = f"#{state_rank_num} {row['county_short']}\nDPS: {row['DPS']:.3f} | Margin: {row['dem_margin_2024_pp']:+.1f}%"

        txt = ax.annotate(
            label,
            xy=(centroid.x, centroid.y),
            fontsize=9, fontweight='bold',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#333333',
                      alpha=0.92, linewidth=1.5),
            path_effects=[pe.withStroke(linewidth=2, foreground='white')]
        )
        texts.append(txt)

    # Try to adjust text positions
    try:
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='->', color='#333333', lw=1.2))
    except Exception:
        pass  # fallback: labels stay at centroids

    ax.set_title(f'{STATE_NAMES[abbr]}: Top 5 Democratic Priority Counties\nEnhanced Composite Score -- Campaign Resource Targeting',
                 fontsize=14, fontweight='bold')
    ax.axis('off')

    # Colorbar
    sm3 = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mcolors.Normalize(vmin=0, vmax=state_vmax))
    sm3.set_array([])
    cbar3 = fig.colorbar(sm3, ax=ax, orientation='vertical', fraction=0.025, pad=0.02, shrink=0.8)
    cbar3.set_label('Democratic Priority Score', fontsize=11)

    plt.tight_layout()
    plt.savefig(f'{FIG_DIR}/enhanced_priority_{abbr}_top5.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   OK Saved enhanced_priority_{abbr}_top5.png")

print("\n" + "=" * 70)
print("ALL DONE -- Enhanced Democratic Priority Score complete.")
print(f"   Rankings: {BASE}/enhanced_priority_rankings.csv")
print(f"   Maps: {FIG_DIR}/enhanced_priority_*.png (5 files)")
print("=" * 70)
