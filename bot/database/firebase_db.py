import os
import json
import base64
import logging
import asyncio
from datetime import datetime, date
from pathlib import Path
from google.cloud.firestore_v1.base_query import FieldFilter
import firebase_admin
from firebase_admin import credentials, firestore

from bot.config import (
    BASE_DIR,
    DEFAULT_WEB_APP_URL,
    FIREBASE_KEY_PATH,
    FIREBASE_CREDENTIALS,
    USE_FIREBASE,
)

logger = logging.getLogger(__name__)

# Standart matnlar
DEFAULT_ABOUT_TEXT = (
    "<b>Signal Books haqida</b>\n\n"
    "Signal Books — kitobsevarlar uchun yaratilgan zamonaviy onlayn kutubxona platformasi. "
    "Biz foydalanuvchilarga kitoblarni qulay tarzda topish, o‘qish va bilim olish imkoniyatini taqdim etishni maqsad qilganmiz.\n\n"
    "📖 <b>Bizning maqsadimiz</b>\n\n"
    "Kitobxonlikni rivojlantirish, bilim olishni yanada qulaylashtirish va kitoblarni raqamli muhitda ommalashtirish.\n\n"
    "💡 <b>Bizning imkoniyatlarimiz</b>\n\n"
    "Kitoblarni qulay qidirish.\n\n"
    "Onlayn kitob o‘qish.\n\n"
    "Turli janrdagi kitoblardan foydalanish.\n\n"
    "Foydalanuvchilar uchun sodda va qulay interfeys.\n\n"
    "🤝 <b>Biz bilan bog‘laning</b>\n\n"
    "Savol, taklif yoki mualliflik huquqi bilan bog‘liq murojaatlar uchun Telegram orqali biz bilan bog‘lanishingiz mumkin.\n\n"
    "📲 Telegram: @Signal_Books_bot\n\n"
    "<b>Signal Books — bilim sari bir qadam! 📚</b>"
)

DEFAULT_CONTACT_TEXT = (
    "📞 <b>Qo'llab-quvvatlash va aloqa xizmati:</b>\n\n"
    "Savollar, takliflar yoki buyurtmalar bo'yicha biz bilan bog'laning:\n"
    "👤 Admin / Menejer: @signalbooks_admin\n"
    "📧 Email: info@signalbooks.uz\n"
    "🌐 Veb-sayt: Signal Books Mini App"
)

_firestore_client = None
_firebase_initialized = False
_firebase_attempted = False

def get_firestore_client(force_reload: bool = False):
    """Firebase Firestore mijozini olish yoki initsializatsiya qilish"""
    global _firestore_client, _firebase_initialized, _firebase_attempted

    if _firestore_client is not None and not force_reload:
        return _firestore_client

    if _firebase_attempted and not force_reload and _firestore_client is None:
        return None

    _firebase_attempted = True

    if not USE_FIREBASE:
        logger.info("ℹ️ USE_FIREBASE=false qilib belgilangan.")
        return None

    cred = None

    # 1. Muhit o'zgaruvchisidan JSON yoki Base64 tekshirish
    if FIREBASE_CREDENTIALS:
        try:
            # Oddiy JSON qator
            cred_dict = json.loads(FIREBASE_CREDENTIALS)
            cred = credentials.Certificate(cred_dict)
            logger.info("🔑 Firebase credentials muhit o'zgaruvchisidan (JSON) yuklandi.")
        except Exception:
            try:
                # Base64 shifrlangan JSON
                decoded = base64.b64decode(FIREBASE_CREDENTIALS).decode("utf-8")
                cred_dict = json.loads(decoded)
                cred = credentials.Certificate(cred_dict)
                logger.info("🔑 Firebase credentials muhit o'zgaruvchisidan (Base64) yuklandi.")
            except Exception as e:
                logger.error(f"❌ FIREBASE_CREDENTIALS o'qishda xatolik: {e}")

    # 2. Fayldan tekshirish
    if not cred:
        search_paths = [
            Path(FIREBASE_KEY_PATH) if os.path.isabs(FIREBASE_KEY_PATH) else BASE_DIR / FIREBASE_KEY_PATH,
            BASE_DIR / "serviceAccountKey.json",
            BASE_DIR / "firebase-key.json",
            BASE_DIR / "firebase_credentials.json",
        ]

        # Loyiha papkasidagi har qanday adminsdk yoki signal-books kalitlarini izlash
        search_paths.extend(list(BASE_DIR.glob("*adminsdk*.json")))
        search_paths.extend(list(BASE_DIR.glob("*signal-books*.json")))

        # Downloads papkasini ham avtomatik tekshirish
        try:
            downloads_dir = Path.home() / "Downloads"
            if downloads_dir.exists():
                dl_keys = list(downloads_dir.glob("*signal-books*.json")) + list(downloads_dir.glob("*firebase-adminsdk*.json"))
                for dl_file in dl_keys:
                    # Faylni loyihaga avtomatik ko'chirib olish
                    target = BASE_DIR / "serviceAccountKey.json"
                    if not target.exists() and dl_file.is_file():
                        try:
                            import shutil
                            shutil.copy2(dl_file, target)
                            logger.info(f"📥 Downloads papkasidan {dl_file.name} avtomatik serviceAccountKey.json ga ko'chirildi!")
                            search_paths.insert(0, target)
                        except Exception:
                            search_paths.append(dl_file)
                    else:
                        search_paths.append(dl_file)
        except Exception:
            pass

        for p in search_paths:
            if p and p.exists() and p.is_file():
                try:
                    cred = credentials.Certificate(str(p))
                    logger.info(f"🔑 Firebase kaliti yuklandi: {p.name}")
                    break
                except Exception as e:
                    logger.error(f"❌ Firebase kalit faylini ({p}) o'qishda xatolik: {e}")

    if not cred:
        logger.warning(
            "⚠️ Firebase kaliti (serviceAccountKey.json) topilmadi! "
            "Iltimos, faylni loyiha papkasiga qo'ying yoki FIREBASE_CREDENTIALS o'zgaruvchisini sozlang."
        )
        return None

    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
        _firebase_initialized = True
        logger.info("🔥 Firebase Firestore muvaffaqiyatli ulandi!")
        return _firestore_client
    except Exception as e:
        logger.error(f"❌ Firebase Firestore ulanishida xatolik: {e}")
        return None

def is_firebase_available() -> bool:
    """Firebase sozlamalari mavjudligi va ulanish tekshiruvi"""
    client = get_firestore_client()
    return client is not None

# ==================== SYNC FIRESTORE METHODS ====================

def _sync_init_db(db):
    default_settings = {
        "web_app_url": DEFAULT_WEB_APP_URL,
        "about_text": DEFAULT_ABOUT_TEXT,
        "contact_text": DEFAULT_CONTACT_TEXT,
        "force_channel": "",
        "force_channel_title": "",
    }
    settings_ref = db.collection("settings")
    for key, val in default_settings.items():
        doc_ref = settings_ref.document(key)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({"key": key, "value": val})
        else:
            # Agar eski tekst bo'lsa yangilash
            data = doc.to_dict() or {}
            curr_val = data.get("value", "")
            if key == "about_text" and ("Dildora Boks" in curr_val or "xush kelibsiz" in curr_val or "loyihasiga xush" in curr_val):
                doc_ref.update({"value": DEFAULT_ABOUT_TEXT})
            elif key == "contact_text" and ("dildoraboks" in curr_val or "Dildora Boks" in curr_val):
                doc_ref.update({"value": DEFAULT_CONTACT_TEXT})

def _sync_add_or_update_user(db, user_id: int, username: str | None, full_name: str | None) -> bool:
    user_ref = db.collection("users").document(str(user_id))
    doc = user_ref.get()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not doc.exists:
        user_ref.set({
            "user_id": int(user_id),
            "username": username or "",
            "full_name": full_name or "",
            "created_at": now,
            "last_active": now,
            "is_blocked": 0
        })
        return True
    else:
        user_ref.update({
            "username": username or "",
            "full_name": full_name or "",
            "last_active": now,
            "is_blocked": 0
        })
        return False

def _sync_set_user_blocked(db, user_id: int, is_blocked: bool):
    user_ref = db.collection("users").document(str(user_id))
    doc = user_ref.get()
    if doc.exists:
        user_ref.update({
            "is_blocked": 1 if is_blocked else 0
        })

def _sync_get_all_users(db, only_active: bool) -> list[int]:
    users_ref = db.collection("users")
    if only_active:
        query = users_ref.where(filter=FieldFilter("is_blocked", "==", 0))
    else:
        query = users_ref

    docs = query.stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        uid = d.get("user_id")
        if uid is not None:
            try:
                result.append(int(uid))
                continue
            except (ValueError, TypeError):
                pass
        try:
            result.append(int(doc.id))
        except (ValueError, TypeError):
            pass
    return result

def _sync_get_stats(db) -> dict:
    today_str = date.today().strftime("%Y-%m-%d")
    users_ref = db.collection("users")

    total_users = 0
    active_users = 0
    blocked_users = 0
    today_users = 0

    try:
        total_users = users_ref.count().get()[0][0].value
        active_users = users_ref.where(filter=FieldFilter("is_blocked", "==", 0)).count().get()[0][0].value
        blocked_users = users_ref.where(filter=FieldFilter("is_blocked", "==", 1)).count().get()[0][0].value
        today_users = (
            users_ref.where(filter=FieldFilter("created_at", ">=", f"{today_str} 00:00:00"))
            .where(filter=FieldFilter("created_at", "<=", f"{today_str} 23:59:59"))
            .count().get()[0][0].value
        )
    except Exception:
        docs = list(users_ref.stream())
        total_users = len(docs)
        for doc in docs:
            d = doc.to_dict()
            if d.get("is_blocked") == 1:
                blocked_users += 1
            else:
                active_users += 1

            c_at = str(d.get("created_at", ""))
            if c_at.startswith(today_str):
                today_users += 1

    return {
        "total_users": int(total_users),
        "active_users": int(active_users),
        "blocked_users": int(blocked_users),
        "today_users": int(today_users)
    }

def _sync_get_setting(db, key: str, default: str) -> str:
    doc = db.collection("settings").document(key).get()
    if doc.exists:
        data = doc.to_dict() or {}
        return data.get("value", default)
    return default

def _sync_set_setting(db, key: str, value: str):
    db.collection("settings").document(key).set({
        "key": key,
        "value": value
    }, merge=True)

def _sync_get_all_users_for_export(db) -> list[tuple]:
    users_ref = db.collection("users")
    try:
        docs = users_ref.order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    except Exception:
        docs = users_ref.stream()

    result = []
    for doc in docs:
        d = doc.to_dict()
        uid = d.get("user_id") or doc.id
        result.append((
            uid,
            d.get("username", ""),
            d.get("full_name", ""),
            d.get("created_at", ""),
            d.get("last_active", ""),
            d.get("is_blocked", 0)
        ))
    return result

@firestore.transactional
def _increment_suggestion_id(transaction, counter_ref):
    snapshot = counter_ref.get(transaction=transaction)
    current_id = 0
    if snapshot.exists:
        current_id = snapshot.to_dict().get("last_id", 0)
    new_id = current_id + 1
    transaction.set(counter_ref, {"last_id": new_id}, merge=True)
    return new_id

def _sync_add_book_suggestion(
    db,
    user_id: int,
    username: str | None,
    full_name: str | None,
    book_title: str,
    author: str | None,
    note: str | None,
    photo_file_id: str | None = None
) -> int:
    counter_ref = db.collection("counters").document("suggestions")
    transaction = db.transaction()
    new_id = _increment_suggestion_id(transaction, counter_ref)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_ref = db.collection("book_suggestions").document(str(new_id))
    doc_ref.set({
        "id": new_id,
        "user_id": int(user_id),
        "username": username or "",
        "full_name": full_name or "",
        "book_title": book_title,
        "author": author or "",
        "note": note or "",
        "photo_file_id": photo_file_id or "",
        "status": "pending",
        "created_at": now
    })
    return new_id


def _sync_get_book_suggestion(db, suggestion_id: int) -> dict | None:
    doc = db.collection("book_suggestions").document(str(suggestion_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = int(suggestion_id)
        return data
    return None

def _sync_update_suggestion_status(db, suggestion_id: int, status: str):
    db.collection("book_suggestions").document(str(suggestion_id)).update({
        "status": status
    })

def _sync_get_suggestions_stats(db) -> dict:
    coll = db.collection("book_suggestions")
    total = 0
    pending = 0
    accepted = 0
    rejected = 0

    try:
        total = coll.count().get()[0][0].value
        pending = coll.where(filter=FieldFilter("status", "==", "pending")).count().get()[0][0].value
        accepted = coll.where(filter=FieldFilter("status", "==", "accepted")).count().get()[0][0].value
        rejected = coll.where(filter=FieldFilter("status", "==", "rejected")).count().get()[0][0].value
    except Exception:
        docs = list(coll.stream())
        total = len(docs)
        for doc in docs:
            d = doc.to_dict()
            s = d.get("status")
            if s == "pending":
                pending += 1
            elif s == "accepted":
                accepted += 1
            elif s == "rejected":
                rejected += 1

    return {
        "total": int(total),
        "pending": int(pending),
        "accepted": int(accepted),
        "rejected": int(rejected)
    }

def _sync_get_recent_suggestions(db, limit: int, only_pending: bool) -> list[dict]:
    coll = db.collection("book_suggestions")
    try:
        if only_pending:
            query = coll.where(filter=FieldFilter("status", "==", "pending")).order_by("id", direction=firestore.Query.DESCENDING).limit(limit)
        else:
            query = coll.order_by("id", direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    except Exception:
        if only_pending:
            docs = coll.where(filter=FieldFilter("status", "==", "pending")).stream()
        else:
            docs = coll.stream()
        items = [doc.to_dict() for doc in docs]
        items.sort(key=lambda x: x.get("id", 0), reverse=True)
        return items[:limit]

def _sync_get_user_suggestions(db, user_id: int) -> list[dict]:
    coll = db.collection("book_suggestions")
    try:
        docs = coll.where(filter=FieldFilter("user_id", "==", int(user_id))).stream()
        items = [doc.to_dict() for doc in docs]
        items.sort(key=lambda x: x.get("id", 0), reverse=True)
        return items
    except Exception as e:
        logger.error(f"Foydalanuvchi takliflarini olishda xatolik: {e}")
        return []

@firestore.transactional
def _increment_support_id(transaction, counter_ref):
    snapshot = counter_ref.get(transaction=transaction)
    current_id = 0
    if snapshot.exists:
        current_id = snapshot.to_dict().get("last_id", 0)
    new_id = current_id + 1
    transaction.set(counter_ref, {"last_id": new_id}, merge=True)
    return new_id

def _sync_add_support_message(
    db,
    user_id: int,
    username: str | None,
    full_name: str | None,
    message_text: str,
    photo_file_id: str | None = None
) -> int:
    counter_ref = db.collection("counters").document("support")
    transaction = db.transaction()
    new_id = _increment_support_id(transaction, counter_ref)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_ref = db.collection("support_messages").document(str(new_id))
    doc_ref.set({
        "id": new_id,
        "user_id": int(user_id),
        "username": username or "",
        "full_name": full_name or "",
        "message_text": message_text or "",
        "photo_file_id": photo_file_id or "",
        "status": "pending",
        "created_at": now
    })
    return new_id

def _sync_get_support_message(db, msg_id: int) -> dict | None:
    doc = db.collection("support_messages").document(str(msg_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = int(msg_id)
        return data
    return None

def _sync_update_support_status(db, msg_id: int, status: str):
    db.collection("support_messages").document(str(msg_id)).update({
        "status": status
    })

# ==================== ASYNC EXPORTED API ====================

async def fb_init_db():
    db = get_firestore_client()
    if db:
        await asyncio.to_thread(_sync_init_db, db)

async def fb_add_or_update_user(user_id: int, username: str | None, full_name: str | None) -> bool:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_add_or_update_user, db, user_id, username, full_name)

async def fb_set_user_blocked(user_id: int, is_blocked: bool = True):
    db = get_firestore_client()
    await asyncio.to_thread(_sync_set_user_blocked, db, user_id, is_blocked)

async def fb_get_all_users(only_active: bool = False) -> list[int]:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_all_users, db, only_active)

async def fb_get_stats() -> dict:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_stats, db)

async def fb_get_setting(key: str, default: str = "") -> str:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_setting, db, key, default)

async def fb_set_setting(key: str, value: str):
    db = get_firestore_client()
    await asyncio.to_thread(_sync_set_setting, db, key, value)

async def fb_get_all_users_for_export() -> list[tuple]:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_all_users_for_export, db)

async def fb_add_book_suggestion(
    user_id: int,
    username: str | None,
    full_name: str | None,
    book_title: str,
    author: str | None = None,
    note: str | None = None,
    photo_file_id: str | None = None
) -> int:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_add_book_suggestion, db, user_id, username, full_name, book_title, author, note, photo_file_id)

async def fb_get_book_suggestion(suggestion_id: int) -> dict | None:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_book_suggestion, db, suggestion_id)

async def fb_update_suggestion_status(suggestion_id: int, status: str):
    db = get_firestore_client()
    await asyncio.to_thread(_sync_update_suggestion_status, db, suggestion_id, status)

async def fb_get_suggestions_stats() -> dict:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_suggestions_stats, db)

async def fb_get_recent_suggestions(limit: int = 10, only_pending: bool = False) -> list[dict]:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_recent_suggestions, db, limit, only_pending)

async def fb_get_user_suggestions(user_id: int) -> list[dict]:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_user_suggestions, db, user_id)

async def fb_add_support_message(
    user_id: int,
    username: str | None,
    full_name: str | None,
    message_text: str,
    photo_file_id: str | None = None
) -> int:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_add_support_message, db, user_id, username, full_name, message_text, photo_file_id)

async def fb_get_support_message(msg_id: int) -> dict | None:
    db = get_firestore_client()
    return await asyncio.to_thread(_sync_get_support_message, db, msg_id)

async def fb_update_support_status(msg_id: int, status: str):
    db = get_firestore_client()
    await asyncio.to_thread(_sync_update_support_status, db, msg_id, status)

