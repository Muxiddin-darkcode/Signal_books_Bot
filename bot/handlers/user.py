from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, MenuButtonWebApp, WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from bot.database.db import get_setting, add_or_update_user, add_book_suggestion
from bot.config import DEFAULT_WEB_APP_URL, ADMIN_IDS
from bot.states.user_states import BookSuggestionStates
from bot.keyboards.user_kb import (
    get_main_keyboard,
    get_web_app_inline_kb,
    get_share_inline_kb,
    get_subscription_check_kb,
    get_suggestion_skip_kb,
    get_cancel_suggestion_kb,
)
from bot.keyboards.admin_kb import get_suggestion_admin_kb
from bot.utils.setup_bot import is_user_subscribed

user_router = Router(name="user_router")

async def send_welcome_content(message: Message, bot: Bot, user_id: int):
    """Foydalanuvchiga xush kelibsiz xabari va Web App tugmalarini yuborish"""
    web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
    
    # Foydalanuvchiga chat pastidagi Web App tugmasini ham biriktirish
    if web_app_url and web_app_url.startswith("https://"):
        try:
            await bot.set_chat_menu_button(
                chat_id=user_id,
                menu_button=MenuButtonWebApp(
                    text="Open",
                    web_app=WebAppInfo(url=web_app_url)
                )
            )
        except Exception:
            pass

    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "📖 <b>Signal Books</b> rasmiy botiga xush kelibsiz!\n\n"
        "Bu yerda siz eng sara kitoblarni topishingiz, mutolaa qilishingiz "
        "va buyurtma berishingiz mumkin.\n\n"
        "👇 <b>Saytni ochish uchun quyidagi 'Signal Books (Saytni ochish)' tugmasini bosing:</b>"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(web_app_url)
    )
    await message.answer(
        "💡 <i>Web ilovani to'g'ridan-to'g'ri ochish uchun bosing:</i>",
        reply_markup=get_web_app_inline_kb(web_app_url)
    )

@user_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user_id = message.from_user.id
    
    # Foydalanuvchini bazaga qo'shish
    try:
        await add_or_update_user(
            user_id=user_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
    except Exception:
        pass
    
    # Majburiy kanal tekshiruvi
    force_channel = await get_setting("force_channel", "")
    if force_channel:
        is_sub = await is_user_subscribed(bot, user_id, force_channel)
        if not is_sub:
            channel_link = force_channel if force_channel.startswith("https://") else f"https://t.me/{force_channel.lstrip('@')}"
            await message.answer(
                "⚠️ <b>Botdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling!</b>\n\n"
                "Kanalga a'zo bo'lgach, quyidagi <b>'Obunani tekshirish'</b> tugmasini bosing:",
                reply_markup=get_subscription_check_kb(channel_link)
            )
            return

    await send_welcome_content(message, bot, user_id)

@user_router.callback_query(F.data == "check_subscription")
async def callback_check_subscription(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    force_channel = await get_setting("force_channel", "")
    is_sub = await is_user_subscribed(bot, user_id, force_channel)
    
    if is_sub:
        await call.message.delete()
        await call.answer("✅ Obuna tasdiqlandi! Xush kelibsiz.", show_alert=False)
        await send_welcome_content(call.message, bot, user_id)
    else:
        await call.answer(
            "❌ Siz hali kanalga a'zo bo'lmadingiz!\nIltimos, avval kanalga a'zo bo'ling.",
            show_alert=True
        )

@user_router.message(Command("app"))
async def cmd_app(message: Message):
    """Tezkor Web App chaqirish buyrug'i"""
    web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
    await message.answer(
        "📚 <b>Signal Books Mini App</b>\n\n"
        "Saytni ochish uchun pastdagi tugmani bosing:",
        reply_markup=get_web_app_inline_kb(web_app_url)
    )

@user_router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam bo'limi"""
    help_text = (
        "ℹ️ <b>Signal Books boti bo'yicha yordam:</b>\n\n"
        "• <b>📚 Signal Books (Saytni ochish)</b> - Telegram ichida to'liq saytni ochadi.\n"
        "• <b>ℹ️ Biz haqimizda</b> - Loyiha haqida batafsil ma'lumot.\n"
        "• <b>📞 Bog'lanish / Yordam</b> - Savollar yoki muammolar bo'yicha ma'muriyat bilan bog'lanish.\n"
        "• <b>🔗 Do'stlarga ulashish</b> - Botni tanishlar va kitobsevarlarga yuborish.\n\n"
        "<i>Eslatma: Chatning pastki chap qismidagi 'Signal Books' menyu tugmasidan ham saytni istalgan vaqt ochishingiz mumkin.</i>"
    )
    await message.answer(help_text)

@user_router.message(F.text.contains("Biz haqimizda"))
async def btn_about(message: Message):
    about_text = await get_setting("about_text")
    web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
    await message.answer(
        about_text,
        reply_markup=get_web_app_inline_kb(web_app_url)
    )

@user_router.message(F.text.contains("Bog'lanish"))
async def btn_contact(message: Message):
    contact_text = await get_setting("contact_text")
    await message.answer(contact_text)

@user_router.message(F.text.contains("Do'stlarga ulashish"))
async def btn_share(message: Message, bot: Bot):
    bot_info = await bot.get_me()
    await message.answer(
        "📚 <b>Signal Books</b> botini do'stlaringizga ham ulashing va ular bilan birga eng yaxshi kitoblardan bahramand bo'ling!",
        reply_markup=get_share_inline_kb(bot_info.username or "")
    )

# --- Kitob taklif qilish FSM bo'limi ---

@user_router.message(F.text.contains("Kitob taklif qilish"))
async def btn_suggest_book_start(message: Message, state: FSMContext):
    """Foydalanuvchi kitob taklif qilishni boshlaganda"""
    await state.clear()
    await state.set_state(BookSuggestionStates.waiting_for_title)
    text = (
        "💡 <b>Kitob taklif qilish</b>\n\n"
        "Siz Signal Books javonlarida qaysi kitobni ko'rishni xohlaysiz?\n\n"
        "<b>1-qadam:</b> Iltimos, <b>kitob nomini</b> kiriting:"
    )
    await message.answer(text, reply_markup=get_cancel_suggestion_kb())

@user_router.callback_query(F.data == "cancel_suggestion")
async def callback_cancel_suggestion(call: CallbackQuery, state: FSMContext):
    """Jarayonni bekor qilish"""
    await state.clear()
    await call.message.edit_text("❌ Kitob taklif qilish bekor qilindi.")
    await call.answer("Bekor qilindi")

@user_router.message(BookSuggestionStates.waiting_for_title)
async def process_suggest_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer(
            "⚠️ Iltimos, kitob nomini matn ko'rinishida yozing:",
            reply_markup=get_cancel_suggestion_kb()
        )
        return

    await state.update_data(book_title=title)
    await state.set_state(BookSuggestionStates.waiting_for_author)
    text = (
        f"📖 Kitob nomi: <b>{title}</b>\n\n"
        "<b>2-qadam:</b> Kitob <b>muallifi</b> kim?\n"
        "<i>(Agar muallifini bilmasangiz, 'O'tkazib yuborish' tugmasini bosing):</i>"
    )
    await message.answer(text, reply_markup=get_suggestion_skip_kb())

@user_router.callback_query(F.data == "skip_suggestion_step", BookSuggestionStates.waiting_for_author)
async def skip_suggest_author(call: CallbackQuery, state: FSMContext):
    await state.update_data(author=None)
    await state.set_state(BookSuggestionStates.waiting_for_note)
    await call.message.edit_text(
        "📝 <b>3-qadam:</b> Ushbu kitob haqida qo'shimcha izoh yoki tavsif bormi?\n"
        "<i>(Masalan: O'zbek tilidagi tarjimasi kerak, yoki 'O'tkazib yuborish' tugmasini bosing):</i>",
        reply_markup=get_suggestion_skip_kb()
    )
    await call.answer()

@user_router.message(BookSuggestionStates.waiting_for_author)
async def process_suggest_author(message: Message, state: FSMContext):
    author = (message.text or "").strip()
    await state.update_data(author=author)
    await state.set_state(BookSuggestionStates.waiting_for_note)
    await message.answer(
        f"✍️ Muallif: <b>{author}</b>\n\n"
        "<b>3-qadam:</b> Ushbu kitob haqida qo'shimcha izoh yoki tavsif bormi?\n"
        "<i>(Masalan: Qaysi nashriyot yoki til, yoki 'O'tkazib yuborish' tugmasini bosing):</i>",
        reply_markup=get_suggestion_skip_kb()
    )

async def _finish_book_suggestion(user_id: int, user_data: dict, bot: Bot, from_user):
    book_title = user_data.get("book_title", "")
    author = user_data.get("author") or "Ko'rsatilmadi"
    note = user_data.get("note") or "Mavjud emas"

    # Bazaga yozish
    suggestion_id = await add_book_suggestion(
        user_id=user_id,
        username=from_user.username,
        full_name=from_user.full_name,
        book_title=book_title,
        author=author if author != "Ko'rsatilmadi" else None,
        note=note if note != "Mavjud emas" else None
    )

    # Foydalanuvchiga tasdiq xabari
    user_response = (
        "✅ <b>Rahmat! Sizning kitob taklifingiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📖 <b>Kitob:</b> {book_title}\n"
        f"✍️ <b>Muallif:</b> {author}\n"
        f"📝 <b>Izoh:</b> {note}\n\n"
        "Tez orada ma'muriyatimiz taklifingizni ko'rib chiqadi va sizga natija haqida xabar beradi. 📚"
    )

    # Adminlarga bildirishnoma yuborish
    username_str = f"@{from_user.username}" if from_user.username else "mavjud emas"
    admin_notification = (
        f"💡 <b>Yangi kitob taklifi!</b> (#{suggestion_id})\n\n"
        f"👤 <b>Foydalanuvchi:</b> {from_user.full_name} ({username_str})\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📖 <b>Kitob nomi:</b> {book_title}\n"
        f"✍️ <b>Muallif:</b> {author}\n"
        f"📝 <b>Izoh:</b> {note}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_notification,
                reply_markup=get_suggestion_admin_kb(suggestion_id, status="pending")
            )
        except Exception:
            pass

    return user_response

@user_router.callback_query(F.data == "skip_suggestion_step", BookSuggestionStates.waiting_for_note)
async def skip_suggest_note(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    data["note"] = None
    await state.clear()
    response_text = await _finish_book_suggestion(call.from_user.id, data, bot, call.from_user)
    await call.message.edit_text(response_text)
    await call.answer("Taklif qabul qilindi!")

@user_router.message(BookSuggestionStates.waiting_for_note)
async def process_suggest_note(message: Message, state: FSMContext, bot: Bot):
    note = (message.text or "").strip()
    data = await state.get_data()
    data["note"] = note
    await state.clear()
    response_text = await _finish_book_suggestion(message.from_user.id, data, bot, message.from_user)
    await message.answer(response_text)

