
# I build dc_yearly with one row per state per year. For dc_count I interpolate linearly from 20% of the 2025 total in 2010 to 100% in 2025 because datacentermap.com has no timestamps. For cumulative_mw I use Epoch AI's timeline data which has exact operational dates for 35 major AI facilities.

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL
from sqlalchemy import create_engine

YEARS = list(range(2010, 2026))

# Part 1: Interpolated dc_count per state per year

dc = pd.read_csv("data/data_centers_clean.csv")
state_counts_2025 = dc.groupby("state").size().reset_index(name="count_2025")

rows = []
for _, row in state_counts_2025.iterrows():
    for year in YEARS:
        # frac goes from 0.20 (2010) to 1.00 (2025) - models the ramp-up in data center construction
        frac = 0.20 + (0.80 * (year - 2010) / (2025 - 2010))
        rows.append({"state": row["state"], "year": year, "dc_count": round(row["count_2025"] * frac, 1)})

dc_yearly = pd.DataFrame(rows)

# Part 2: Cumulative operational MW per state per year from major AI facilities
# I map facilities to states manually because the names don't reliably encode the state - something like "OpenAI Stargate Abilene" requires knowing that Abilene is in Texas.
FACILITY_STATE = {
    "STACK Infrastructure NVA02": "VA",
    "Microsoft Goodyear": "AZ",
    "Google Omaha": "NE",
    "Meta Temple": "TX",
    "QTS Richmond": "VA",
    "Meta Prometheus": "IL",
    "Google Council Bluffs (East)": "IA",
    "Meta Kuna": "ID",
    "Stream Phoenix": "AZ",
    "Microsoft Fairwater Atlanta": "GA",
    "Microsoft Fairwater Wisconsin": "WI",
    "Amazon Madison Mega Site": "WI",
    "Vantage TX1": "TX",
    "Anthropic-Amazon New Carlisle": "IN",
    "Amazon Ridgeland": "MS",
    "Google New Albany": "OH",
    "xAI Colossus 1": "TN",
    "Google Cedar Rapids": "IA",
    "OpenAI Stargate Abilene": "TX",
    "Google Pryor (North)": "OK",
    "Alibaba Zhangbei": None, # China - excluded
    "Fluidstack Lake Mariner": "NY",
    "Meta Hyperion": "TX",
    "QTS Cedar Rapids": "IA",
    "xAI Colossus 2": "TN",
    "Goodnight": "TX",
    "Coreweave Helios": "NJ",
    "OpenAI Stargate UAE": None, # UAE - excluded
    "OpenAI Stargate Shackelford": "TX",
    "OpenAI Stargate Milam": "TX",
    "OpenAI Stargate New Mexico": "NM",
    "OpenAI Stargate Lordstown": "OH",
    "Crusoe Abilene Expansion": "TX",
    "OpenAI Stargate Michigan": "MI",
    "OpenAI Stargate Wisconsin": "WI",
}

tl = pd.read_csv("data/data_center_timelines.csv")
tl["Date"] = pd.to_datetime(tl["Date"], errors="coerce")
tl["year"] = tl["Date"].dt.year
tl["Power (MW)"] = pd.to_numeric(tl["Power (MW)"], errors="coerce")
tl["Buildings operational"] = pd.to_numeric(tl["Buildings operational"], errors="coerce").fillna(0)
tl["state"] = tl["Data center"].map(FACILITY_STATE)

# I drop non-US facilities and rows with no MW value since I can't include them in the capacity sum
tl = tl[tl["state"].notna() & tl["Power (MW)"].notna()]

# Each facility has multiple rows as buildings come online, so I take the max MW seen up to each year so capacity only ever increases and never drops.
mw_rows = []
for year in YEARS:
    # Buildings operational is 0 for planned or under-construction entries so I skip those
    op = tl[(tl["Buildings operational"] > 0) & (tl["year"] <= year)]
    if op.empty:
        continue
    per_facility = op.groupby(["state", "Data center"])["Power (MW)"].max()
    per_state = per_facility.groupby("state").sum().reset_index()
    per_state.columns = ["state", "cumulative_mw"]
    per_state["year"] = year
    mw_rows.append(per_state)

cumulative_mw = pd.concat(mw_rows, ignore_index=True) if mw_rows else pd.DataFrame(columns=["state", "cumulative_mw", "year"])

# Merge interpolated counts with cumulative MW
dc_yearly = dc_yearly.merge(cumulative_mw[["state", "year", "cumulative_mw"]], on=["state", "year"], how="left")

engine = create_engine(DB_URL)
dc_yearly.to_sql("dc_yearly", engine, if_exists="replace", index=False)

print(f"Loaded {len(dc_yearly)} rows into dc_yearly ({dc_yearly['state'].nunique()} states, {min(YEARS)}-{max(YEARS)})")

print(f"  Cumulative MW data for {cumulative_mw['state'].nunique()} states from timelines")
