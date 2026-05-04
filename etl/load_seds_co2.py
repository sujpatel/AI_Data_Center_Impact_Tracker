# I use MSN code TETCE which is total energy-related CO2 across all sectors, not just electricity, because I want to capture the full emissions profile of coal-heavy states like Indiana before data centers even arrive.

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL
from sqlalchemy import create_engine

US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC"
}

df = pd.read_csv("data/co2_all.csv")

# Same state filter as load_seds_prices.py - exclude census regions and US aggregate rows
df = df[(df["MSN"] == "TETCE") & (df["State"].isin(US_STATES))]

year_cols = [str(y) for y in range(2010, 2024)]

df = df.melt(id_vars=["State"], value_vars=year_cols, var_name="year", value_name="co2_million_metric_tons")

df.columns = ["state", "year", "co2_million_metric_tons"]

df["year"] = df["year"].astype(int)
df["co2_million_metric_tons"] = pd.to_numeric(df["co2_million_metric_tons"], errors="coerce")
df = df.dropna(subset=["co2_million_metric_tons"])

engine = create_engine(DB_URL)
df.to_sql("emissions", engine, if_exists="replace", index=False)

print(f"Loaded {len(df)} rows into emissions ({df['state'].nunique()} states, {df['year'].min()} – {df['year'].max()})")
