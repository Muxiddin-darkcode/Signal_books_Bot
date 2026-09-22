import os
from pathlib import Path
from dotenv import load_dotenv

# Loyihaning asosiy papkasi
BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini yuklash
load_dotenv(BASE_DIR / ".env")

# Asosiy sozlamalar
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin IDlarini list qilib olish
_admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS = []
if _admin_ids_raw:
    for item in _admin_ids_raw.replace(" ", "").split(","):
        if item.isdigit():
            ADMIN_IDS.append(int(item))

# Standart Web App URL
DEFAULT_WEB_APP_URL = os.getenv("WEB_APP_URL", "https://t.me").strip()

# Baza fayli yo'li
DB_PATH = BASE_DIR / "signal_books.db"
