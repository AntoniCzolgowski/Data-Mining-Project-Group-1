import pandas as pd

file = "../data/raw/countypres_2000-2024.csv"
raw_df = pd.read_csv(file)
df = raw_df.copy()

df = df.loc[
    (df["year"] >= 2016) # filter irrelevant years
    & (df["county_fips"].notna()) # remove fip nas
    & (df["mode"].fillna("").str.strip().str.lower() == "total") # dont break out by voting method
    & (pd.to_numeric(df["candidatevotes"], errors="coerce").fillna(0)) # remove zero votes and non-numeric values
].copy()

df.drop(columns=["version", "totalvotes", 'office', 'state_po', 'mode'], errors="ignore", inplace=True)
df["candidatevotes"] = pd.to_numeric(df["candidatevotes"], errors="coerce").astype("Int64") # coerce to numeric and set errors to nan
df["county_fips"] = pd.to_numeric(df["county_fips"], errors="coerce").astype("Int64")