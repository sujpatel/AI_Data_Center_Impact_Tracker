
# I load the planned data center count by state into PostgreSQL. This is forward-looking data from early 2026 that I use as a feature in the random forest to help predict which states are likely to become the next major data center hubs.

import pandas as pd
import sys
import os
from sqlalchemy import create_engine

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL

df = pd.read_csv("data/announcements.csv")

# I keep only state and planned_count since the other columns in the CSV aren't used in the analysis
df = df[["state", "planned_count"]].dropna()
df["planned_count"] = pd.to_numeric(df["planned_count"], errors="coerce")
df = df.dropna(subset=["planned_count"])
df["planned_count"] = df["planned_count"].astype(int)

engine = create_engine(DB_URL)
df.to_sql("announcements", engine, if_exists="replace", index=False)
print(f"Loaded {len(df)} rows into announcements ({df['state'].nunique()} states, {df['planned_count'].sum()} total planned)")
