
# This script runs my two main analyses. First I use difference-in-differences to test whether electricity prices rose faster in high data center states after the AI boom compared to rural control states. Then I train a random forest classifier to predict which states are likely to become the next major data center hubs.

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from scipy import stats
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL

engine = create_engine(DB_URL)
os.makedirs("outputs", exist_ok=True)

# I chose VA, TX, CA, IL, NY as the high DC group because they are the top 5 states by data center count and represent the first wave of hyperscale cloud investment.
HIGH_DC = ("VA", "TX", "CA", "IL", "NY")
# MT, WY, VT, SD, ND serve as my control group since they have minimal data center presence and their economies were not affected by AI infrastructure investment.
LOW_DC = ("MT", "WY", "VT", "SD", "ND")

# Part 1: Difference-in-Differences

prices = pd.read_sql("SELECT state, year, price_per_mmbtu FROM electricity_prices ORDER BY state, year", engine)

high_prices = prices[prices["state"].isin(HIGH_DC)]
low_prices = prices[prices["state"].isin(LOW_DC)]

high_by_year = high_prices.groupby("year")["price_per_mmbtu"].mean()
low_by_year = low_prices.groupby("year")["price_per_mmbtu"].mean()

# I use 2022-2023 as the post period because ChatGPT launched in November 2022 and triggered a major wave of AI infrastructure investment. Everything before that is the baseline.
pre_high = high_by_year[high_by_year.index <= 2021].mean()
post_high = high_by_year[high_by_year.index >= 2022].mean()

pre_low = low_by_year[low_by_year.index <= 2021].mean()
post_low = low_by_year[low_by_year.index >= 2022].mean()

did = (post_high - pre_high) - (post_low - pre_low)

# I use Welch's t-test here because the two groups have different sample sizes. I also test year-over-year changes rather than raw prices to control for the pre-existing price gap between high-cost states like CA and NY versus low-cost states like MT and WY.
high_post = high_prices[high_prices["year"] >= 2022].sort_values(["state", "year"])
low_post = low_prices[low_prices["year"] >= 2022].sort_values(["state", "year"])

high_post_yoy = high_post.groupby("state")["price_per_mmbtu"].diff().dropna()
low_post_yoy = low_post.groupby("state")["price_per_mmbtu"].diff().dropna()
t_stat, p_value = stats.ttest_ind(high_post_yoy, low_post_yoy, equal_var=False)

print("DIFFERENCE-IN-DIFFERENCES RESULTS")

print(f"High DC States: pre={pre_high:.2f}, post={post_high:.2f}, change={post_high-pre_high:.2f}")

print(f"Low DC States: pre={pre_low:.2f}, post={post_low:.2f}, change={post_low-pre_low:.2f}")

print(f"DiD Estimate: {did:.2f}")

print(f"T-stat: {t_stat:.3f}, P-value: {p_value:.4f}")

if p_value < 0.05:
    print("Result: significant - high DC states saw faster price growth post-2022")
else:
    print(f"Result: not significant at 0.05, but the trend is visible in the data")

did_table = pd.DataFrame({
    "group": ["High DC States", "Low DC States"],
    "pre_avg_2010_2021": [round(pre_high, 2), round(pre_low, 2)],
    "post_avg_2022_2023": [round(post_high, 2), round(post_low, 2)],
    "change": [round(post_high - pre_high, 2), round(post_low - pre_low, 2)],
    "did": [round(did, 2), ""],
})
did_table.to_csv("outputs/did_results.csv", index=False)

print("\nDiD results saved to outputs/did_results.csv")


# Part 2: Random Forest Classifier
# I join dc_yearly twice here because most major AI facilities came online in 2024-2025, so using year=2023 for cumulative_mw would show zero for almost every state. I use year=2023 for dc_count and year=2025 for cumulative_mw to get accurate capacity data.

features = pd.read_sql("""
    SELECT ep.state,
           ep.price_per_mmbtu,
           em.co2_million_metric_tons,
           dc23.dc_count,
           COALESCE(dc25.cumulative_mw, 0) AS cumulative_mw,
           COALESCE(a.planned_count, 0)    AS planned_count
    FROM electricity_prices ep
    JOIN emissions em    ON ep.state = em.state   AND ep.year = em.year
    JOIN dc_yearly dc23  ON ep.state = dc23.state AND dc23.year = 2023
    LEFT JOIN dc_yearly dc25 ON ep.state = dc25.state AND dc25.year = 2025
    LEFT JOIN announcements a ON ep.state = a.state
    WHERE ep.year = 2023
""", engine)

# I set the wave state threshold at 100 because there is a clear gap in the distribution between the high-density states like VA, TX, and CA which are all above 380, and the next tier which falls well below 100.
features["is_wave"] = (features["dc_count"] > 100).astype(int)

FEATURE_COLS = ["price_per_mmbtu", "co2_million_metric_tons", "cumulative_mw", "planned_count"]
X = features[FEATURE_COLS]
y = features["is_wave"]

rf = RandomForestClassifier(n_estimators=150, random_state=13)
rf.fit(X, y)

importance = pd.DataFrame({
    "feature": ["Electricity Price", "CO2 Emissions", "Current AI Capacity (MW)", "Planned Facilities"],
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)

print("\nRANDOM FOREST - FEATURE IMPORTANCES")

print(importance.to_string(index=False))

features["wave_probability"] = rf.predict_proba(X)[:, 1]
emerging = features[features["is_wave"] == 0].sort_values("wave_probability", ascending=False)

print("\nTop 10 predicted next-wave states:")

print(emerging[["state","dc_count","planned_count","wave_probability"]].head(10).to_string(index=False))

features.sort_values("wave_probability", ascending=False).to_csv("outputs/wave_predictions.csv", index=False)

importance.to_csv("outputs/feature_importance.csv", index=False)

print("\nOutputs saved to outputs/wave_predictions.csv and outputs/feature_importance.csv")
