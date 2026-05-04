# config.py
# Single source of truth for DB credentials so no script hardcodes a password.
# python-dotenv loads .env at runtime, keeping secrets out of version control.

import os
from dotenv import load_dotenv

load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "datacenter_tracker",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
}

# SQLAlchemy expects a connection URL string, not a dict, so we build it here once.
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
