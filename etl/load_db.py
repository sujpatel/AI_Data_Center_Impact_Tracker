
# I load the cleaned data centers snapshot into PostgreSQL so load_dc_yearly.py can read the 2025 state totals for interpolation.

import pandas as pd
from sqlalchemy import create_engine
import sys
import os

# I add the project root to the path so I can import config.py from within the etl/ subdirectory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL

engine = create_engine(DB_URL)

df = pd.read_csv("data/data_centers_clean.csv")

# I use replace instead of append so re-running the pipeline doesn't double the row count
df.to_sql("data_centers", engine, if_exists="replace", index=False)

print(f"Loaded {len(df)} rows into data_centers table")
