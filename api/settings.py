import os
from dotenv import load_dotenv
load_dotenv()

def pick(*keys, default=None):
    for k in keys:
        v = os.getenv(k)
        if v not in (None, ""):
            return v
    return default

DB_HOST     = os.getenv("NEON_HOST",     os.getenv("DB_HOST", "localhost"))
DB_PORT     = int(os.getenv("NEON_PORT", os.getenv("DB_PORT", "5432")))
DB_NAME     = os.getenv("NEON_DATABASE", os.getenv("DB_NAME", "pollution_db"))
DB_USER     = os.getenv("NEON_USER",     os.getenv("DB_USER", "pollution_user"))
DB_PASSWORD = os.getenv("NEON_PASSWORD", os.getenv("DB_PASSWORD", "pollution_pass"))
DB_SSLMODE  = os.getenv("NEON_SSLMODE",  os.getenv("DB_SSLMODE", "require"))