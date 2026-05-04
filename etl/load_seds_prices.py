# I load electricity prices from EIA SEDS using MSN code ESTCD, which is the all-sectors retail price in $/MMBtu. I use all-sectors rather than residential because data centers are industrial consumers. SEDS stores years as columns so I melt to long format for SQL compatibility.

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

df = pd.read_csv("data/pr_all.csv")

# I filter to just US states because the SEDS file also includes census regions and national totals I don't want
df = df[(df["MSN"] == "ESTCD") & (df["State"].isin(US_STATES))]

# I start at 2010 because that's when hyperscale data center growth accelerated, and 2023 is the last complete year in SEDS
year_cols = [str(y) for y in range(2010, 2024)]
df = df.melt(id_vars=["State"], value_vars=year_cols, var_name="year", value_name="price_per_mmbtu")
df.columns = ["state", "year", "price_per_mmbtu"]

df["year"] = df["year"].astype(int)
df["price_per_mmbtu"] = pd.to_numeric(df["price_per_mmbtu"], errors="coerce")
df = df.dropna(subset=["price_per_mmbtu"])

engine = create_engine(DB_URL)
df.to_sql("electricity_prices", engine, if_exists="replace", index=False)

print(f"Loaded {len(df)} rows into electricity_prices ({df['state'].nunique()} states, {df['year'].min()}–{df['year'].max()})")
