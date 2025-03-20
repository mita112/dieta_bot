import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

LOGS_DIR = DATA_DIR / "logs"
LOGS_SETTINGS_PATH = LOGS_DIR / "logs_settings.yaml"


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATA_DIR / 'users_data', exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

BOT_TOKEN = "ваш_токен_бота"
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "ваш_пароль"
DB_NAME = "nutrition_bot"
