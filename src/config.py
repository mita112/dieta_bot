import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

LOGS_DIR = DATA_DIR / "logs"
LOGS_SETTINGS_PATH = LOGS_DIR / "logs_settings.yaml"


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATA_DIR / 'users_data', exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

BOT_TOKEN = ""
DB_HOST = ""
DB_USER = ""
DB_PASSWORD = ""
DB_NAME = ""