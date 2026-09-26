import os
import sys
import sqlite3
from pathlib import Path

# Loyiha papkasini sys.path ga qo'shish
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Windows konsolida UTF-8 ni ta'minlash
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from bot.config import DB_PATH
from bot.database.firebase_db import get_firestore_client, is_firebase_available

def run_migration():
    print("=" * 60)
    print("🚀 Signal Books — SQLite'dan Firebase Firestore'ga ma'lumotlarni ko'chirish")
    print("=" * 60)

    # 1. Firebase ulanishini tekshirish
    if not is_firebase_available():
        print("\n❌ XATOLIK: Firebase Firestore'ga ulanib bo'lmadi!")
        print("Iltimos, quyidagilarni tekshiring:")
        print("1. Firebase Console'dan 'serviceAccountKey.json' faylini yuklab olib, loyiha asosiy papkasiga qo'ying.")
        print("2. Yoki .env faylida FIREBASE_KEY_PATH yoki FIREBASE_CREDENTIALS o'zgaruvchilarini to'g'ri ko'rsating.")
        print("=" * 60)
        sys.exit(1)

    db = get_firestore_client()
    print("✅ Firebase Firestore muvaffaqiyatli ulandi!\n")

    # 2. SQLite faylini tekshirish
    if not DB_PATH.exists():
        print(f"⚠️ SQLite bazasi fayli topilmadi: {DB_PATH}")
        print("Yangi bo'sh Firebase bazasi bilan ishlash davom ettiriladi.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- 3. Foydalanuvchilarni ko'chirish ---
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"👥 SQLite'dan topilgan foydalanuvchilar: {len(users)} ta")

        users_ref = db.collection("users")
        migrated_users = 0
        for u in users:
            uid = str(u["user_id"])
            users_ref.document(uid).set({
                "user_id": int(u["user_id"]),
                "username": u["username"] or "",
                "full_name": u["full_name"] or "",
                "created_at": u["created_at"] or "",
                "last_active": u["last_active"] or "",
                "is_blocked": int(u["is_blocked"] or 0)
            }, merge=True)
            migrated_users += 1

        print(f"✅ Firebase'ga ko'chirildi: {migrated_users} ta foydalanuvchi.")
    except Exception as e:
        print(f"⚠️ Foydalanuvchilarni ko'chirishda xatolik: {e}")

    # --- 4. Sozlamalarni ko'chirish ---
    try:
        cursor.execute("SELECT * FROM settings")
        settings = cursor.fetchall()
        print(f"\n⚙️ SQLite'dan topilgan sozlamalar: {len(settings)} ta")

        settings_ref = db.collection("settings")
        migrated_settings = 0
        for s in settings:
            key = s["key"]
            val = s["value"]
            settings_ref.document(key).set({
                "key": key,
                "value": val
            }, merge=True)
            migrated_settings += 1

        print(f"✅ Firebase'ga ko'chirildi: {migrated_settings} ta sozlama.")
    except Exception as e:
        print(f"⚠️ Sozlamalarni ko'chirishda xatolik: {e}")

    # --- 5. Kitob takliflarini ko'chirish ---
    try:
        cursor.execute("SELECT * FROM book_suggestions")
        suggestions = cursor.fetchall()
        print(f"\n💡 SQLite'dan topilgan kitob takliflari: {len(suggestions)} ta")

        suggestions_ref = db.collection("book_suggestions")
        max_id = 0
        migrated_suggestions = 0
        for sug in suggestions:
            s_id = int(sug["id"])
            if s_id > max_id:
                max_id = s_id

            suggestions_ref.document(str(s_id)).set({
                "id": s_id,
                "user_id": int(sug["user_id"]),
                "username": sug["username"] or "",
                "full_name": sug["full_name"] or "",
                "book_title": sug["book_title"] or "",
                "author": sug["author"] or "",
                "note": sug["note"] or "",
                "photo_file_id": (sug["photo_file_id"] if "photo_file_id" in sug.keys() else "") or "",
                "status": sug["status"] or "pending",
                "created_at": sug["created_at"] or ""
            }, merge=True)
            migrated_suggestions += 1

        # Counter ni yangilash
        if max_id > 0:
            db.collection("counters").document("suggestions").set({
                "last_id": max_id
            }, merge=True)

        print(f"✅ Firebase'ga ko'chirildi: {migrated_suggestions} ta taklif (So'nggi ID: {max_id}).")
    except Exception as e:
        print(f"⚠️ Kitob takliflarini ko'chirishda xatolik: {e}")

    # --- 6. Murojaatlarni (support) ko'chirish ---
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='support_messages'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM support_messages")
            support_msgs = cursor.fetchall()
            print(f"\n📩 SQLite'dan topilgan murojaatlar: {len(support_msgs)} ta")

            support_ref = db.collection("support_messages")
            max_sup_id = 0
            migrated_support = 0
            for sup in support_msgs:
                s_id = int(sup["id"])
                if s_id > max_sup_id:
                    max_sup_id = s_id

                support_ref.document(str(s_id)).set({
                    "id": s_id,
                    "user_id": int(sup["user_id"]),
                    "username": sup["username"] or "",
                    "full_name": sup["full_name"] or "",
                    "message_text": sup["message_text"] or "",
                    "photo_file_id": (sup["photo_file_id"] if "photo_file_id" in sup.keys() else "") or "",
                    "status": sup["status"] or "pending",
                    "created_at": sup["created_at"] or ""
                }, merge=True)
                migrated_support += 1

            if max_sup_id > 0:
                db.collection("counters").document("support").set({
                    "last_id": max_sup_id
                }, merge=True)

            print(f"✅ Firebase'ga ko'chirildi: {migrated_support} ta murojaat.")
    except Exception as e:
        print(f"⚠️ Murojaatlarni ko'chirishda xatolik: {e}")

    conn.close()

    print("\n" + "=" * 60)
    print("🎉 MIGRATSIYA MUVAFFAQIYATLI YAKUNLANDI!")
    print("Barcha ma'lumotlar Firebase Firestore'ga o'tkazildi.")
    print("=" * 60)

if __name__ == "__main__":
    run_migration()
