import aiosqlite
import logging
from datetime import datetime, date
from bot.config import DB_PATH, DEFAULT_WEB_APP_URL, USE_FIREBASE
from bot.database.firebase_db import (
    is_firebase_available,
    fb_init_db,
    fb_add_or_update_user,
    fb_set_user_blocked,
    fb_get_all_users,
    fb_get_stats,
    fb_get_setting,
    fb_set_setting,
    fb_get_all_users_for_export,
    fb_add_book_suggestion,
    fb_get_book_suggestion,
    fb_update_suggestion_status,
    fb_get_suggestions_stats,
    fb_get_recent_suggestions,
    fb_get_user_suggestions,
    fb_add_support_message,
    fb_get_support_message,
    fb_update_support_status,
)

logger = logging.getLogger(__name__)

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

async def init_db():
    """Ma'lumotlar bazasini initsializatsiya qilish"""
    if is_firebase_available():
        logger.info("🔥 Ma'lumotlar bazasi: Firebase Firestore faol.")
        await fb_init_db()
        return

    logger.warning("⚠️ Firebase kaliti topilmadi. Mahalliy SQLite bazasi ishlatilmoqda.")
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0
            )
        """)

        # Sozlamalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Kitob takliflari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS book_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                book_title TEXT NOT NULL,
                author TEXT,
                note TEXT,
                photo_file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Eski SQLite bazasiga photo_file_id ustunini xavfsiz qo'shish
        try:
            await db.execute("ALTER TABLE book_suggestions ADD COLUMN photo_file_id TEXT")
        except Exception:
            pass

        # Qo'llab-quvvatlash (Support / Murojaat) xabarlari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                message_text TEXT,
                photo_file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Standart sozlamalarni tekshirish va kiritish
        default_settings = [
            ("web_app_url", DEFAULT_WEB_APP_URL),
            ("about_text", DEFAULT_ABOUT_TEXT),
            ("contact_text", DEFAULT_CONTACT_TEXT),
            ("force_channel", ""),
            ("force_channel_title", "")
        ]

        for key, val in default_settings:
            await db.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, val))

        # Agar eski standart matn saqlangan bo'lsa, uni yangisiga yangilash
        async with db.execute("SELECT value FROM settings WHERE key = 'about_text'") as cursor:
            row = await cursor.fetchone()
            if row and ("Dildora Boks" in row[0] or "xush kelibsiz" in row[0] or "loyihasiga xush" in row[0]):
                await db.execute("UPDATE settings SET value = ? WHERE key = 'about_text'", (DEFAULT_ABOUT_TEXT,))

        async with db.execute("SELECT value FROM settings WHERE key = 'contact_text'") as cursor:
            row = await cursor.fetchone()
            if row and ("dildoraboks" in row[0] or "Dildora Boks" in row[0]):
                await db.execute("UPDATE settings SET value = ? WHERE key = 'contact_text'", (DEFAULT_CONTACT_TEXT,))

        await db.commit()

async def add_or_update_user(user_id: int, username: str | None, full_name: str | None) -> bool:
    """Foydalanuvchini bazaga qo'shish yoki ma'lumotlarini yangilash"""
    if is_firebase_available():
        return await fb_add_or_update_user(user_id, username, full_name)

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if row is None:
            await db.execute("""
                INSERT INTO users (user_id, username, full_name, created_at, last_active, is_blocked)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (user_id, username, full_name, now, now))
            await db.commit()
            return True
        else:
            await db.execute("""
                UPDATE users
                SET username = ?, full_name = ?, last_active = ?, is_blocked = 0
                WHERE user_id = ?
            """, (username, full_name, now, user_id))
            await db.commit()
            return False

async def set_user_blocked(user_id: int, is_blocked: bool = True):
    """Foydalanuvchi botni bloklaganini belgilash"""
    if is_firebase_available():
        await fb_set_user_blocked(user_id, is_blocked)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET is_blocked = ? WHERE user_id = ?
        """, (1 if is_blocked else 0, user_id))
        await db.commit()

async def get_all_users(only_active: bool = False) -> list[int]:
    """Barcha foydalanuvchilar ID ro'yxatini olish"""
    if is_firebase_available():
        return await fb_get_all_users(only_active)

    async with aiosqlite.connect(DB_PATH) as db:
        if only_active:
            query = "SELECT user_id FROM users WHERE is_blocked = 0"
        else:
            query = "SELECT user_id FROM users"
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_stats() -> dict:
    """Bot statistikasini olish"""
    if is_firebase_available():
        return await fb_get_stats()

    today_str = date.today().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 0") as cursor:
            active_users = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1") as cursor:
            blocked_users = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{today_str}%",)) as cursor:
            today_users = (await cursor.fetchone())[0]

    return {
        "total_users": total_users,
        "active_users": active_users,
        "blocked_users": blocked_users,
        "today_users": today_users
    }

async def get_setting(key: str, default: str = "") -> str:
    """Sozlama qiymatini olish"""
    if is_firebase_available():
        return await fb_get_setting(key, default)

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row is not None else default

async def set_setting(key: str, value: str):
    """Sozlamani saqlash yoki yangilash"""
    if is_firebase_available():
        await fb_set_setting(key, value)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        await db.commit()

async def get_all_users_for_export() -> list[tuple]:
    """Eksport qilish uchun foydalanuvchilar ro'yxati"""
    if is_firebase_available():
        return await fb_get_all_users_for_export()

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT user_id, username, full_name, created_at, last_active, is_blocked
            FROM users ORDER BY created_at DESC
        """) as cursor:
            return await cursor.fetchall()

async def add_book_suggestion(
    user_id: int,
    username: str | None,
    full_name: str | None,
    book_title: str,
    author: str | None = None,
    note: str | None = None,
    photo_file_id: str | None = None
) -> int:
    """Yangi kitob taklifini saqlash va ID sini qaytarish"""
    if is_firebase_available():
        return await fb_add_book_suggestion(user_id, username, full_name, book_title, author, note, photo_file_id)

    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = await db.execute("""
            INSERT INTO book_suggestions (user_id, username, full_name, book_title, author, note, photo_file_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (user_id, username, full_name, book_title, author, note, photo_file_id, now))
        await db.commit()
        return cursor.lastrowid

async def get_book_suggestion(suggestion_id: int) -> dict | None:
    """Taklif ma'lumotlarini olish"""
    if is_firebase_available():
        return await fb_get_book_suggestion(suggestion_id)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM book_suggestions WHERE id = ?", (suggestion_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_suggestion_status(suggestion_id: int, status: str):
    """Taklif holatini yangilash ('pending', 'accepted', 'rejected')"""
    if is_firebase_available():
        await fb_update_suggestion_status(suggestion_id, status)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE book_suggestions SET status = ? WHERE id = ?", (status, suggestion_id))
        await db.commit()

async def get_suggestions_stats() -> dict:
    """Kitob takliflari statistikasi"""
    if is_firebase_available():
        return await fb_get_suggestions_stats()

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM book_suggestions") as cursor:
            total = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM book_suggestions WHERE status = 'pending'") as cursor:
            pending = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM book_suggestions WHERE status = 'accepted'") as cursor:
            accepted = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM book_suggestions WHERE status = 'rejected'") as cursor:
            rejected = (await cursor.fetchone())[0]
    return {
        "total": total,
        "pending": pending,
        "accepted": accepted,
        "rejected": rejected
    }

async def get_recent_suggestions(limit: int = 10, only_pending: bool = False) -> list[dict]:
    """So'nggi kitob takliflarini olish"""
    if is_firebase_available():
        return await fb_get_recent_suggestions(limit, only_pending)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if only_pending:
            query = "SELECT * FROM book_suggestions WHERE status = 'pending' ORDER BY id DESC LIMIT ?"
        else:
            query = "SELECT * FROM book_suggestions ORDER BY id DESC LIMIT ?"
        async with db.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_user_suggestions(user_id: int) -> list[dict]:
    """Foydalanuvchining o'z kitob takliflari ro'yxatini olish"""
    if is_firebase_available():
        return await fb_get_user_suggestions(user_id)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM book_suggestions WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def add_support_message(
    user_id: int,
    username: str | None,
    full_name: str | None,
    message_text: str,
    photo_file_id: str | None = None
) -> int:
    """Foydalanuvchi murojaatini saqlash va ID sini qaytarish"""
    if is_firebase_available():
        return await fb_add_support_message(user_id, username, full_name, message_text, photo_file_id)

    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = await db.execute("""
            INSERT INTO support_messages (user_id, username, full_name, message_text, photo_file_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (user_id, username, full_name, message_text, photo_file_id, now))
        await db.commit()
        return cursor.lastrowid

async def get_support_message(msg_id: int) -> dict | None:
    """Murojaat ma'lumotlarini olish"""
    if is_firebase_available():
        return await fb_get_support_message(msg_id)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM support_messages WHERE id = ?", (msg_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_support_status(msg_id: int, status: str):
    """Murojaat holatini yangilash ('pending', 'replied')"""
    if is_firebase_available():
        await fb_update_support_status(msg_id, status)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE support_messages SET status = ? WHERE id = ?", (status, msg_id))
        await db.commit()
