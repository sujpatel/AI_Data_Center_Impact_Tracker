# run_all.py
# Runs the full pipeline in dependency order: ETL must finish before analysis,
# and models.py must run before visualize.py because it produces the CSVs Charts 4 and 5 read.
# Usage: python run_all.py

import subprocess
import sys

scripts = [
    "etl/load_db.py",
    "etl/load_seds_prices.py",
    "etl/load_seds_co2.py",
    "etl/load_dc_yearly.py",
    "etl/load_announcements.py",
    "analysis/models.py",
    "analysis/visualize.py",
]

for script in scripts:
    print(f"\n{'='*50}\nRunning {script}\n{'='*50}")
    result = subprocess.run([sys.executable, script], check=True)

print("\nAll done. Open outputs/*.png to view charts.")
