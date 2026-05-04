
# I extract the US state from raw scraped address strings. The addresses are inconsistent so I use two passes: first a regex that matches the 2-letter state code in standard US postal format, then a dictionary fallback for addresses that spell out the full state name.

import pandas as pd

# Fallback dictionary for addresses that spell out the full state name instead of abbreviating it
STATE_MAP = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}

df = pd.read_csv("data/data_centers.csv")
df.columns = ["operator", "name", "address"]

# The regex matches the 2-letter state code that sits between the city and zip code in standard US postal format
df["state"] = df["address"].str.extract(r",\s([A-Z]{2})\s*\d*,\s*USA")

# I only apply the dictionary to rows the regex missed to avoid incorrectly overwriting valid matches
for full, abbr in STATE_MAP.items():
    mask = df["state"].isna() & df["address"].str.contains(full, na=False)
    df.loc[mask, "state"] = abbr

df["city"] = df["address"].str.extract(r"^(.*?),")

# I drop rows with no state since they can't be used in any state-level analysis
df = df[["name", "operator", "city", "state"]]
df = df.dropna(subset=["state"])

print(df.head(10))
print(f"Total rows: {len(df)}")

# Save cleaned data for load_db.py to pick up
df.to_csv("data/data_centers_clean.csv", index=False)
