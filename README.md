# AI Data Center Impact Tracker

Analyzes the effect of AI-driven data center growth on electricity prices and CO2 emissions across US states using EIA SEDS data, difference-in-differences analysis, and a Random Forest classifier.

# Project Structure 
```
AI_Data_Center_Impact_Tracker/
├── run_all.py
├── config.py
├── requirements.txt
├── README.md
├── schema.sql
├── .env
├── .gitignore
├── data/
│   ├── announcements.csv
│   ├── co2_all.csv
│   ├── data_center_timelines.csv
│   ├── data_centers_clean.csv
│   ├── data_centers.csv
│   └── pr_all.csv
├── etl/
│   ├── clean_data.py
│   ├── load_announcements.py
│   ├── load_db.py
│   ├── load_dc_yearly.py
│   ├── load_seds_co2.py
│   └── load_seds_prices.py
├── analysis/
│   ├── models.py
│   └── visualize.py
└── outputs/
    ├── did_results.csv
    ├── emissions_collision.png
    ├── feature_importance.csv
    ├── feature_importance.png
    ├── forward_prediction.png
    ├── us_density_map.png
    ├── wave_predictions.csv
    └── wave_price_trend.png
```

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment variables**

Create a `.env` file in the project root:
```
DB_PASSWORD=your_postgres_password
EIA_API_KEY=your_eia_api_key
```

**3. Create the PostgreSQL database**
```bash
psql -U postgres -c "CREATE DATABASE datacenter_tracker;"
```

## Usage

```bash
python run_all.py
```

This runs the full pipeline in order: ETL scripts load all data into PostgreSQL, `models.py` runs the statistical analysis and saves CSVs to `outputs/`, and `visualize.py` generates all 5 charts as PNGs in `outputs/`.


## Data Sources

- **EIA SEDS** - Annual state electricity prices and CO2 emissions (2010-2023): https://www.eia.gov/state/seds/
- **Epoch AI** - Operational dates and MW capacity for 35 major AI data centers: https://epoch.ai
- **datacentermap.com** - Data center locations by state (scraped, cleaned): https://www.datacentermap.com


## Key Findings

**Electricity prices:** States with high data center density (VA, TX, CA, IL, NY) saw electricity prices rise $6.28/MMBtu more than rural control states (MT, WY, VT, SD, ND) after the AI boom began in 2022, a difference-in-differences estimate consistent with increased industrial demand.

**Emissions risk:** Indiana has a coal-heavy grid and 23 planned data center facilities as of 2026, making it the state most exposed to rising emissions from AI infrastructure growth.

**Next-wave states:** The Random Forest model predicts Indiana, Pennsylvania, Louisiana, and Tennessee as the most likely next-wave data center hubs, driven primarily by CO2 emissions profile and planned facility announcements.
