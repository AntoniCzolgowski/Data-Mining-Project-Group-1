import pandas as pd
import numpy as np

scaled = "../data/processed/master_dataset_scaled.csv"
scaled_df = pd.read_csv(scaled)
df_piv = scaled_df.copy()

# remove irrelevant cols
df_piv = df_piv[["county_fips", "state", "county_name", "election_year", "dem_votes", "rep_votes", "total_votes", "dem_pct", "rep_pct", "dem_margin"]]

# pivot
df_piv = (
    df_piv 
      .pivot(index=["county_fips", "county_name"], columns="election_year", values="dem_margin")
      .rename(columns=lambda y: f"dem_margin_{int(y)}")
      .reset_index()
)

# get directional volatility index
df_piv["d_16_20"] = df_piv["dem_margin_2020"] - df_piv["dem_margin_2016"]
df_piv["d_20_24"] = df_piv["dem_margin_2024"] - df_piv["dem_margin_2020"]
df_piv["swing_dir_score"] = df_piv["d_16_20"] * df_piv["d_20_24"] * 10000

# abs swing each cycle
df_piv["swing_mag_16_20"] = df_piv["d_16_20"].abs()
df_piv["swing_mag_20_24"] = df_piv["d_20_24"].abs()

# z scores for magnitude of swing each cycle
mean_16_20 = df_piv["swing_mag_16_20"].mean()
sd_16_20 = df_piv["swing_mag_16_20"].std()

mean_20_24 = df_piv["swing_mag_20_24"].mean()
sd_20_24 = df_piv["swing_mag_20_24"].std()

# change vs average change by election
df_piv["z_swing_mag_16_20"] = (df_piv["swing_mag_16_20"] - mean_16_20) / sd_16_20
df_piv["z_swing_mag_20_24"] = (df_piv["swing_mag_20_24"] - mean_20_24) / sd_20_24

# change vs average change in total
df_piv["vol_z_abs_sum"] = df_piv["z_swing_mag_16_20"] + df_piv["z_swing_mag_20_24"]

# euclidean distance 
df_piv["vol_z_euc"] = np.sqrt(df_piv["z_swing_mag_16_20"]**2 + df_piv["z_swing_mag_20_24"]**2)

path = "../data/processed/county_volatility_dimTable.csv"
df_piv.to_csv(path, index=False)