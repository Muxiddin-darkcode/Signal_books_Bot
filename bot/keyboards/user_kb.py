from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

def get_main_keyboard(web_app_url: str) -> ReplyKeyboardMarkup:
    """Foydalanuvchi uchun asosiy reply tugmalar (rangli fonli)"""
    keyboard = [
        [
            KeyboardButton(
                text="📚 Signal Books (Saytni ochish)",
                web_app=WebAppInfo(url=web_app_url),
                style="success"  # Yashil rangli fon
            )
        ],
        [
            KeyboardButton(
                text="💡 Kitob taklif qilish",
                style="primary"  # Ko'k rangli fon
            ),
            KeyboardButton(
                text="🔗 Do'stlarga ulashish",
                style="primary"  # Ko'k rangli fon
            )
        ],
        [
            KeyboardButton(
                text="ℹ️ Biz haqimizda",
                style="primary"  # Ko'k rangli fon
            ),
            KeyboardButton(
                text="📞 Bog'lanish / Yordam",
                style="primary"  # Ko'k rangli fon
            )
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    )

def get_web_app_inline_kb(web_app_url: str) -> InlineKeyboardMarkup:
    """Xabarlar ostiga qo'yiladigan inline Web App tugmasi (rangli fonli)"""
    buttons = [
        [
            InlineKeyboardButton(
                text="🚀 Signal Books Mini App",
                web_app=WebAppInfo(url=web_app_url),
                style="success"  # Yashil rangli fon
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 Brauzerda ochish",
                url=web_app_url,
                style="primary"  # Ko'k rangli fon
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_share_inline_kb(bot_username: str) -> InlineKeyboardMarkup:
    """Do'stlarga ulashish uchun inline tugma"""
    share_text = "Signal Books - Eng sara kitoblar va qulay xaridlar platformasi! Telegram Web App orqali foydalaning:"
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}&text={share_text}"
    buttons = [
        [
            InlineKeyboardButton(
                text="↗️ Do'stlarga yuborish",
                url=share_url,
                style="primary"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subscription_check_kb(channel_url: str) -> InlineKeyboardMarkup:
    """Majburiy a'zolik kanali va tekshirish tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(
                text="📢 Kanalga a'zo bo'lish",
                url=channel_url,
                style="primary"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Obunani tekshirish",
                callback_data="check_subscription",
                style="success"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_suggestion_skip_kb() -> InlineKeyboardMarkup:
    """Kitob taklifida o'tkazib yuborish va bekor qilish tugmalari"""
    buttons = [
        [
            InlineKeyboardButton(text="➡️ O'tkazib yuborish", callback_data="skip_suggestion_step", style="primary"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_suggestion", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_suggestion_kb() -> InlineKeyboardMarkup:
    """Kitob taklifini bekor qilish tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_suggestion", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

