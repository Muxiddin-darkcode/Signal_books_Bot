import logging
from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    MenuButtonWebApp,
    WebAppInfo,
)

logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    """Bot menyusi uchun buyruqlarni sozlash"""
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish / Yangilash"),
        BotCommand(command="app", description="📚 Signal Books saytini ochish"),
        BotCommand(command="help", description="ℹ️ Yordam va ma'lumot"),
        BotCommand(command="admin", description="⚙️ Boshqaruv paneli (Faqat adminlar uchun)"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

async def set_global_menu_button(bot: Bot, web_app_url: str):
    """Telegram chatining pastki chap burchagiga Web App tugmasini o'rnatish"""
    try:
        if web_app_url and web_app_url.startswith("https://"):
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="Signal Books",
                    web_app=WebAppInfo(url=web_app_url)
                )
            )
            logger.info(f"Global MenuButtonWebApp muvaffaqiyatli o'rnatildi: {web_app_url}")
    except Exception as e:
        logger.warning(f"Menu button o'rnatishda xatolik (URL to'g'riligini tekshiring): {e}")

async def is_user_subscribed(bot: Bot, user_id: int, channel: str) -> bool:
    """Foydalanuvchi kanalga a'zo ekanligini tekshirish"""
    if not channel:
        return True
    try:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if chat_member.status in ["creator", "administrator", "member", "restricted"]:
            return True
        return False
    except Exception as e:
        logger.error(f"Kanal a'zoligini tekshirishda xatolik: {e}")
        # Agar kanal topilmasa yoki bot kanalda admin bo'lmasa, user bloklanmasligi uchun True beramiz
        return True
