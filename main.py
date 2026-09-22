import asyncio
import logging
import sys
import os
import aiohttp
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
    return web.Response(text="Signal Books Bot is RUNNING 24/7! 🚀", content_type="text/plain")

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

async def keep_alive_task():
    """Serverlarni (Render, Koyeb, Hugging Face) uxlab qolishdan saqlovchi fon vazifasi"""
    await asyncio.sleep(30)
    server_url = (
        os.getenv("SERVER_URL")
        or os.getenv("RENDER_EXTERNAL_URL")
        or (f"https://{os.getenv('SPACE_HOST')}" if os.getenv("SPACE_HOST") else None)
    )
    if not server_url:
        logger.info("ℹ️ Server URL belgilanmagan, keep-alive ping o'tkazib yuborildi.")
        return

    url = f"{server_url.rstrip('/')}/health"
    logger.info(f"🔄 Keep-alive tizimi faollashtirildi: {url}")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        logger.info("💓 Keep-alive ping muvaffaqiyatli (Bot faol)")
        except Exception as e:
            logger.debug(f"Keep-alive ping: {e}")
        # Har 10 daqiqada ping yuborib serverni uyg'oq ushlab turadi
        await asyncio.sleep(600)

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
            "DIQQAT! BOT_TOKEN ko'rsatilmagan!\n"
            "!" * 60
        )
        return

    # Proxy mavjud bo'lsa
    proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy") or os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    session = AiohttpSession(proxy=proxy) if proxy else None

    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewarelarni ulash
    dp.message.outer_middleware(DatabaseMiddleware())
    dp.callback_query.outer_middleware(DatabaseMiddleware())

    # Routerlarni ulash
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Startup hodisasini ro'yxatdan o'tkazish
    dp.startup.register(on_startup)

    # Healthcheck serverni ishga tushirish (Render, Koyeb, Docker uchun)
    port_env = os.getenv("PORT", "8000")
    if port_env and port_env.isdigit():
        try:
            await start_web_server(int(port_env))
        except Exception as e:
            logger.warning(f"Healthcheck serverni ishga tushirishda xatolik: {e}")

    # Uxlab qolishdan saqlovchi keep-alive taskni orqa fonda yoqish
    asyncio.create_task(keep_alive_task())

    # Cheksiz qayta ulanish sikli (Internet uzilsa ham bot o'chmaydi)
    while True:
        try:
            logger.info("Eski yangilanishlar o'chirilmoqda va bot tayyorlanmoqda...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"⚠️ Telegram ulanish xatoligi: {e}. 5 soniyadan so'ng qayta ulanadi...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
            break
        except (KeyboardInterrupt, SystemExit):
            logger.info("Dastur to'xtatildi.")
            break
        except Exception as e:
            logger.critical(f"Kutilmagan xatolik yuz berdi: {e}. Qayta ishga tushirilmoqda...")
            import time
            time.sleep(5)
