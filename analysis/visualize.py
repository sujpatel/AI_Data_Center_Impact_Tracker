
# I generate 5 charts that tell the story of AI data center impact on US energy. Charts 1-3 show the current situation and Charts 4-5 show where it's heading. I use Plotly for Chart 1 because Matplotlib has no built-in US choropleth map.

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sqlalchemy import create_engine
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL

engine = create_engine(DB_URL)
os.makedirs("outputs", exist_ok=True)

HIGH_DC = ["VA", "TX", "CA", "IL", "NY"]
LOW_DC = ["MT", "WY", "VT", "SD", "ND"]

PRIMARY = "steelblue"
SECONDARY = "tomato"
SOURCE_TEXT = "Sources: EIA SEDS, Epoch AI, datacentermap.com"

# Dark theme applied globally so all charts have a consistent look for the submission
plt.style.use("dark_background")
plt.rcParams.update({
    "axes.facecolor": "midnightblue",
    "figure.facecolor": "midnightblue",
    "axes.edgecolor": "slategray",
    "grid.color": "darkslategray",
    "grid.alpha": 0.4,
    "text.color": "lavender",
    "axes.labelcolor": "lavender",
    "xtick.color": "lavender",
    "ytick.color": "lavender",
    "axes.titlesize": 20,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
})

def add_source(fig):
    fig.text(0.99, 0.01, SOURCE_TEXT, ha="right", va="bottom",
             fontsize=8, color="#888899", style="italic")


# Chart 1: US Density Map
import plotly.express as px
import plotly.graph_objects as go

dc_2023 = pd.read_sql("SELECT state, dc_count FROM dc_yearly WHERE year = 2023", engine)

fig1 = px.choropleth(
    dc_2023,
    locations="state",
    locationmode="USA-states",
    color="dc_count",
    scope="usa",
    color_continuous_scale=[[0, "#1e1e2e"], [0.3, "#2a5298"], [1, PRIMARY]],
    title="<b>Data Center Density by State (2023)</b>",
    labels={"dc_count": "Data Centers"},
)


fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor="#1e1e2e",
    plot_bgcolor="#1e1e2e",
    height=500,
    title_font=dict(size=20),
    annotations=[dict(
        text=SOURCE_TEXT, x=1, y=-0.05, xref="paper", yref="paper",
        showarrow=False, font=dict(size=8, color="#888899"), xanchor="right"
    )],
    margin={"r": 0, "t": 60, "l": 0, "b": 40},
)
fig1.write_image("outputs/us_density_map.png")

print("Chart 1 saved: us_density_map.png")


# Chart 2: Wave Price Trend - the divergence between the two lines after 2021 is what the +$6/MMBtu DiD estimate represents visually.
prices = pd.read_sql("SELECT state, year, price_per_mmbtu FROM electricity_prices ORDER BY year", engine)

high_avg = prices[prices["state"].isin(HIGH_DC)].groupby("year")["price_per_mmbtu"].mean()
low_avg = prices[prices["state"].isin(LOW_DC)].groupby("year")["price_per_mmbtu"].mean()

fig, ax = plt.subplots(figsize=(12, 500/96))
ax.plot(high_avg.index, high_avg.values, color=PRIMARY, marker="o", linewidth=2.5,
        markersize=7.2, label="High DC States (VA, TX, CA, IL, NY)")
ax.plot(low_avg.index, low_avg.values, color=SECONDARY, marker="o", linewidth=2.5,
        markersize=7.2, label="Low DC States (MT, WY, VT, SD, ND)")
ax.axvspan(2021.5, 2023.5, color="gold", alpha=0.12, label="AI Boom (2022-2023)")
ax.set_title("Electricity Prices: High vs Low Data Center States (2010-2023)")
ax.set_xlabel("Year")
ax.set_ylabel("Avg Price ($/MMBtu, all sectors)")
ax.legend(fontsize=10)
ax.grid(True)
add_source(fig)
plt.tight_layout()
plt.savefig("outputs/wave_price_trend.png", dpi=120, facecolor=fig.get_facecolor())
plt.close()
print("Chart 2 saved: wave_price_trend.png")


# Chart 3: Emissions Collision - I focus on Indiana because it has a coal-heavy grid and the most planned data centers of any non-wave state (23), making it the clearest example of where emissions and AI infrastructure are heading toward a collision.
in_em = pd.read_sql(
    "SELECT year, co2_million_metric_tons FROM emissions WHERE state = 'IN' ORDER BY year", engine
)
in_dc = pd.read_sql(
    "SELECT year, dc_count FROM dc_yearly WHERE state = 'IN' AND year <= 2023 ORDER BY year", engine
)
state_data = in_em.merge(in_dc, on="year")

in_planned = pd.read_sql("SELECT planned_count FROM announcements WHERE state = 'IN'", engine)

in_planned_val = int(in_planned["planned_count"].iloc[0]) if not in_planned.empty else 0

fig, ax1 = plt.subplots(figsize=(12, 500/96))
ax1.bar(state_data["year"], state_data["co2_million_metric_tons"],
        color=SECONDARY, alpha=0.7, label="CO2 Emissions (MMT)")
ax1.set_xlabel("Year")

ax1.set_ylabel("CO2 Emissions (million metric tons)", color=SECONDARY)
ax1.tick_params(axis="y", labelcolor=SECONDARY)

ax2 = ax1.twinx()

ax2.plot(state_data["year"], state_data["dc_count"], color=PRIMARY, marker="o",
         linewidth=2.5, markersize=7.2, label="Data Center Count")
ax2.set_ylabel("Data Center Count", color=PRIMARY)
ax2.tick_params(axis="y", labelcolor=PRIMARY)
ax1.set_xlim(2009, 2025)
ax2.annotate(f"+{in_planned_val} planned by 2026",
             xy=(2023, state_data["dc_count"].iloc[-1]),
             xytext=(2022, state_data["dc_count"].iloc[-1] * 0.82),
             arrowprops=dict(arrowstyle="->", color=PRIMARY), color=PRIMARY, fontsize=10)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)

ax1.set_title("Indiana: CO2 Emissions vs Data Center Growth (2010-2023)\n(Coal-heavy grid + 23 planned data centers)")

add_source(fig)

plt.tight_layout()
plt.savefig("outputs/emissions_collision.png", dpi=120, facecolor=fig.get_facecolor())
plt.close()

print("Chart 3 saved: emissions_collision.png")


# Chart 4: Forward Prediction - I only show non-wave states since the current wave states are already saturated. The planned count labels above each bar help explain why the model ranks each state the way it does.
predictions = pd.read_csv("outputs/wave_predictions.csv")
emerging = predictions[predictions["is_wave"] == 0].sort_values("wave_probability", ascending=False).head(10)

fig, ax1 = plt.subplots(figsize=(12, 500/96))
x = range(len(emerging))

bars = ax1.bar(x, emerging["wave_probability"], color=PRIMARY, alpha=0.85, label="Wave Probability")

ax1.set_xticks(x)

ax1.set_xticklabels(emerging["state"], fontsize=12)
ax1.set_ylabel("Predicted Wave Probability")
ax1.set_ylim(0, 1)

for bar, val in zip(bars, emerging["planned_count"]):
    if val > 0:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 str(int(val)), ha="center", va="bottom", fontsize=9,
                 color=SECONDARY, fontweight="bold")

ax2 = ax1.twinx()
ax2.plot(x, emerging["planned_count"], color=SECONDARY, marker="o",
         linewidth=2, markersize=7.2, label="Planned Facilities")
ax2.set_ylabel("Planned Facilities", color=SECONDARY)
ax2.tick_params(axis="y", labelcolor=SECONDARY)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=10)
ax1.set_title("Predicted Next-Wave Data Center States (Random Forest)")
add_source(fig)
plt.tight_layout()
plt.savefig("outputs/forward_prediction.png", dpi=120, facecolor=fig.get_facecolor())
plt.close()

print("Chart 4 saved: forward_prediction.png")


# Chart 5: Feature Importance - CO2 and planned capacity dominate, meaning states that already emit a lot and have announced projects are the strongest predictors of future data center concentration.
importance = pd.read_csv("outputs/feature_importance.csv").sort_values("importance")

fig, ax = plt.subplots(figsize=(10, 500/96))
colors = [PRIMARY if i == len(importance) - 1 else "cornflowerblue" for i in range(len(importance))]
ax.barh(importance["feature"], importance["importance"], color=colors)
ax.set_title("Random Forest - What Predicts a Wave State?")

ax.set_xlabel("Feature Importance")
ax.set_ylabel("")
ax.grid(True, axis="x")
add_source(fig)
plt.tight_layout()
plt.savefig("outputs/feature_importance.png", dpi=120, facecolor=fig.get_facecolor())
plt.close()

print("Chart 5 saved: feature_importance.png")
