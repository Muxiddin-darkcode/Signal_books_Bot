import asyncio
import logging
import sys
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, DEFAULT_WEB_APP_URL, ADMIN_IDS
from bot.database.db import init_db, get_setting
from bot.middlewares.db_middleware import DatabaseMiddleware
from bot.handlers.user import user_router
from bot.handlers.admin import admin_router
from bot.utils.setup_bot import set_bot_commands, set_global_menu_button

# Windows konsoli uchun UTF-8 sozlamasi
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

async def handle_ping(request):
    return web.Response(text="Signal Books Bot is RUNNING! 🚀", content_type="text/plain")

async def start_web_server(port: int):
    """Serverlar (Hugging Face, Koyeb, Render) uchun kichik veb endpoint"""
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.getLogger(__name__).info(f"🌐 Healthcheck web-server {port}-portda ishga tushdi.")


# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan amallar"""
    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await init_db()

    # Buyruqlar menyusini sozlash
    await set_bot_commands(bot)

    # Global menyu Web App tugmasini sozlash
    web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
    await set_global_menu_button(bot, web_app_url)

    bot_info = await bot.get_me()
    logger.info("=" * 50)
    logger.info(f"🚀 Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    logger.info(f"👑 Admin IDlar: {ADMIN_IDS}")
    logger.info(f"🌐 Web App URL: {web_app_url}")
    logger.info("=" * 50)

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "!" * 60 + "\n"
            "DIQQAT! .env faylida BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, .env faylini ochib, @BotFather dan olgan bot tokeningizni kiriting.\n"
            "!" * 60
        )
        return

    # Proxy mavjud bo'lsa (masalan PythonAnywhere bepul rejasida)
    proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy") or os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    session = AiohttpSession(proxy=proxy) if proxy else None

    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewarelarni ulash (foydalanuvchilarni avtomatik bazaga yozish uchun)
    dp.message.outer_middleware(DatabaseMiddleware())
    dp.callback_query.outer_middleware(DatabaseMiddleware())

    # Routerlarni ulash
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Startup hodisasini ro'yxatdan o'tkazish
    dp.startup.register(on_startup)

    # Server muhitida (PORT bo'lganda) healthcheck serverni ishga tushirish
    port_env = os.getenv("PORT")
    if port_env and port_env.isdigit():
        try:
            await start_web_server(int(port_env))
        except Exception as e:
            logger.warning(f"Healthcheck serverni ishga tushirishda xatolik: {e}")

    # Eski xabarlarni tashlab yuborish va pollingni boshlash
    logger.info("Eski yangilanishlar o'chirilmoqda va bot tayyorlanmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
