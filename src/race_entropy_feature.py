import pandas as pd
import numpy as np

file_nonscaled = "../data/processed/master_dataset.csv"
nonscaled_df = pd.read_csv(file_nonscaled)
df_ns = nonscaled_df.copy()

race_cols = df_ns[["pct_non_hispanic_white", "pct_black", "pct_asian"]]

# find other to get full distribution
race_cols["pct_other"] = (100 - race_cols["pct_non_hispanic_white"] - race_cols["pct_black"] - race_cols["pct_asian"])

# normalize to get proportions
race_cols = race_cols / 100.0

# pseudo zero for log
pseudo_zero = .00000001

# shannon entropy index
race_entropy = -(race_cols.clip(lower=pseudo_zero) * np.log(race_cols.clip(lower=pseudo_zero))).sum(axis=1)

# normalize from 0-1
race_entropy_norm = race_entropy / np.log(race_cols.shape[1])

df_ns["race_entropy"] = race_entropy
df_ns["race_entropy_norm"] = race_entropy_norm
 
# condense table for merge with scaled
entropy_cols = df_ns[["county_fips", "election_year","race_entropy_norm"]].copy()

# merge with scaled dataset
file_scaled = "../data/processed/master_dataset_scaled.csv"
master_scaled = pd.read_csv(file_scaled)

master_scaled = master_scaled.merge(
    entropy_cols,
    on=["county_fips", "election_year"],
    how="left",
    validate="one_to_one"
)

path = "../data/processed/master_dataset_scaled.csv"
master_scaled.to_csv(path, index=False)