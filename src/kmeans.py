import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

# load fips and county names
df = pd.read_csv(
    "data/processed/classification_dataset_250.csv",
    dtype={"county_fips": str}
)

print("All columns:")
print(df.columns.tolist())

# exclude fields 
exclude_cols = [
    "county_fips",
    "county_name",
    "state",
    "vol_quintile_num",
    "vol_z_abs_sum",
    "vol_binary",
    "vol_class"
]
exclude_cols = [col for col in exclude_cols if col in df.columns]

# get rid of qualatative / non numeric 
cleaned_df = df.drop(columns=exclude_cols, errors="ignore").select_dtypes(include="number")


print("Features used:")
print(cleaned_df.columns.tolist())

# compare candidate k vals
print("\nK comparison:")
rows = []
cleaned_vals = cleaned_df.values

for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=25)
    labels = km.fit_predict(cleaned_vals)

    centers = km.cluster_centers_
    dists = ((cleaned_vals - centers[labels]) ** 2).sum(axis=1)
    cluster_counts = pd.Series(labels).value_counts()

    rows.append({
        "k": k,
        "silhouette": silhouette_score(cleaned_df, labels),
        "davies_bouldin": davies_bouldin_score(cleaned_df, labels),
        "min_cluster_size": cluster_counts.min(),
        "max_cluster_size": cluster_counts.max()
    })

results = pd.DataFrame(rows)
print(results)

# decided model
final_k = 5
kmeans = KMeans(n_clusters=final_k, random_state=42, n_init=30)
labels = kmeans.fit_predict(cleaned_df)
df["kmeans_cluster_label"] = labels

# export 
output = df[["county_fips", "county_name", "kmeans_cluster_label"]].copy()
output.to_csv("data/processed/kmeans_clusters.csv", index=False)
print(pd.crosstab(df["kmeans_cluster_label"], df["vol_quintile_num"]))

# cluster summary means using raw 2024 values from master_dataset
master_df = pd.read_csv("data/processed/master_dataset.csv", dtype={"county_fips": str})
master_2024 = master_df[master_df["election_year"] == 2024].copy()

map_cols = {
    "median_age": "median_age",
    "pct_black": "pct_black",
    "pct_asian": "pct_asian",
    "pct_two_or_more_races": "pct_two_or_more_races",
    "pct_hispanic": "pct_hispanic",
    "pct_hs_or_higher": "pct_hs_or_higher",
    "pct_bachelors_plus": "pct_bachelors_plus",
    "pct_below_poverty": "pct_below_poverty",
    "pct_income_under_25k": "pct_income_under_25k",
    "pct_income_50k_100k": "pct_income_50k_100k",
    "unemployment_rate": "unemployment_rate",
    "pct_owner_occupied": "pct_owner_occupied",
    "pct_drive_alone": "pct_drive_alone",
    "pct_carpool": "pct_carpool",
    "pct_public_transit": "pct_public_transit",
    "pct_work_from_home": "pct_work_from_home",
    "pct_family_households": "pct_family_households",
    "pct_married_couple": "pct_married_couple",
    "pct_living_alone": "pct_living_alone",
    "pct_senior_65plus": "pct_senior_65plus",
    "pct_young_adult_18_24": "pct_young_adult_18_24",
    "pct_foreign_born": "pct_foreign_born",
    "log_total_population": "total_population",
    "log_population_density": "population_density",
    "log_median_household_income": "median_household_income",
    "log_median_home_value": "median_home_value",
    "log_median_gross_rent": "median_gross_rent"
}

raw_cols = [map_cols[f] for f in map_cols if map_cols[f] in master_2024.columns]
summary_df = df[["county_fips", "kmeans_cluster_label", "vol_quintile_num", "vol_z_abs_sum"]].merge(
    master_2024[["county_fips"] + raw_cols], on="county_fips", how="left"
)
cluster_summary = summary_df.drop(columns=["county_fips"]).select_dtypes(include="number").groupby("kmeans_cluster_label").mean().reset_index()
cluster_summary.to_csv("data/processed/kmeans_cluster_means.csv", index=False)
print("Saved cluster summary means to data/processed/kmeans_cluster_means.csv")
