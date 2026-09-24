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

# Baza fayli yo'li (SQLite zaxira uchun)
DB_PATH = BASE_DIR / "signal_books.db"

# Firebase sozlamalari
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "signal-books").strip()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "").strip()
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "").strip()
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "").strip()

# 1) Fayl yo'li (masalan, serviceAccountKey.json yoki firebase-key.json)
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "serviceAccountKey.json").strip()

# 2) Muhit o'zgaruvchisi orqali JSON matn yoki Base64 (Render / Koyeb / Vercel uchun qulay)
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "").strip()

# Firebase'dan foydalanish holati (true/false)
USE_FIREBASE = os.getenv("USE_FIREBASE", "true").strip().lower() in ("true", "1", "yes")

