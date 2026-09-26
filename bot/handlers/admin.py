import asyncio
import csv
import io
import time
from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramBadRequest

from bot.config import ADMIN_IDS, DEFAULT_WEB_APP_URL
from bot.database.db import (
    get_stats,
    get_setting,
    set_setting,
    get_all_users,
    set_user_blocked,
    get_all_users_for_export,
    get_book_suggestion,
    update_suggestion_status,
    get_suggestions_stats,
    get_recent_suggestions,
    get_support_message,
    update_support_status,
)
from bot.keyboards.admin_kb import (
    get_admin_dashboard_kb,
    get_cancel_kb,
    get_broadcast_confirm_kb,
    get_channel_manage_kb,
    get_texts_manage_kb,
    get_suggestion_admin_kb,
    get_suggestions_list_kb,
    get_cancel_reply_kb,
    get_cancel_support_reply_kb,
)
from bot.keyboards.user_kb import get_web_app_inline_kb
from bot.states.admin_states import AdminStates
from bot.utils.setup_bot import set_global_menu_button

admin_router = Router(name="admin_router")

# Faqat adminlar uchun filtr
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def get_dashboard_text() -> str:
    stats = await get_stats()
    s_stats = await get_suggestions_stats()
    web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
    force_channel = await get_setting("force_channel", "O'rnatilmagan")
    if not force_channel:
        force_channel = "O'rnatilmagan"

    return (
        "👑 <b>Signal Books — Admin Boshqaruv Paneli</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']} ta\n"
        f"🟢 <b>Faol a'zolar:</b> {stats['active_users']} ta\n"
        f"🚫 <b>Bloklaganlar:</b> {stats['blocked_users']} ta\n"
        f"📅 <b>Bugun yangi qo'shilganlar:</b> {stats['today_users']} ta\n\n"
        f"💡 <b>Kitob takliflari:</b> {s_stats['total']} ta (⏳ {s_stats['pending']} ta kutilmoqda)\n\n"
        f"🌐 <b>Joriy Web App URL:</b>\n<code>{web_app_url}</code>\n\n"
        f"📢 <b>Majburiy kanal:</b> {force_channel}\n\n"
        "<i>Quyidagi tugmalar orqali kerakli bo'limni tanlang:</i>"
    )

# --- Admin Panel Asosiy Buyruq ---
@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ <i>Kechirasiz, ushbu buyruq faqat bot adminlari uchun.</i>")
        return

    await state.clear()
    text = await get_dashboard_text()
    await message.answer(text, reply_markup=get_admin_dashboard_kb())

# --- Callback Actionlar ---
@admin_router.callback_query(F.data.startswith("admin_action:"))
async def handle_admin_actions(call: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)
        return

    action = call.data.split(":")[1]

    if action == "stats":
        stats = await get_stats()
        web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
        text = (
            "📊 <b>Bot Statistikasi:</b>\n\n"
            f"• Jami a'zolar: <b>{stats['total_users']}</b> ta\n"
            f"• Faol (bloklamagan): <b>{stats['active_users']}</b> ta\n"
            f"• Bloklagan foydalanuvchilar: <b>{stats['blocked_users']}</b> ta\n"
            f"• Bugun tashrif buyurganlar: <b>{stats['today_users']}</b> ta\n\n"
            f"🌐 Web App URL: <code>{web_app_url}</code>"
        )
        try:
            await call.message.edit_text(text, reply_markup=get_admin_dashboard_kb())
        except TelegramBadRequest:
            pass
        await call.answer("Statistika yangilandi")

    elif action == "suggestions":
        s_stats = await get_suggestions_stats()
        recent = await get_recent_suggestions(limit=8)
        text = (
            "💡 <b>Kitob takliflari bo'limi</b>\n\n"
            f"• Jami takliflar: <b>{s_stats['total']}</b> ta\n"
            f"• ⏳ Kutilayotganlar: <b>{s_stats['pending']}</b> ta\n"
            f"• ✅ Qabul qilinganlar: <b>{s_stats['accepted']}</b> ta\n"
            f"• ❌ Rad etilganlar: <b>{s_stats['rejected']}</b> ta\n\n"
            "<i>So'nggi takliflarni ko'rish va boshqarish uchun quyidagi ro'yxatdan tanlang:</i>"
        )
        await call.message.edit_text(text, reply_markup=get_suggestions_list_kb(recent))
        await call.answer()

    elif action == "set_url":
        current_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
        await state.set_state(AdminStates.waiting_for_web_app_url)
        await call.message.edit_text(
            f"🌐 <b>Web App sayt havolasini o'zgartirish</b>\n\n"
            f"Hozirgi havola:\n<code>{current_url}</code>\n\n"
            "Iltimos, yangi sayt havolasini yuboring (<b>https://</b> bilan boshlanishi shart):",
            reply_markup=get_cancel_kb()
        )
        await call.answer()

    elif action == "broadcast":
        await state.set_state(AdminStates.waiting_for_broadcast_message)
        await call.message.edit_text(
            "📢 <b>Barcha foydalanuvchilarga xabar tarqatish</b>\n\n"
            "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring.\n"
            "<i>(Oddiy matn, rasm, video, havola yoki formatlangan xabar yuborishingiz mumkin):</i>",
            reply_markup=get_cancel_kb()
        )
        await call.answer()

    elif action == "channel":
        current_channel = await get_setting("force_channel", "")
        has_channel = bool(current_channel)
        status = f"<code>{current_channel}</code>" if has_channel else "O'rnatilmagan (O'chiq)"
        await call.message.edit_text(
            f"📢 <b>Majburiy a'zolik kanali sozlamalari</b>\n\n"
            f"Hozirgi kanal: {status}\n\n"
            "Agar kanal ulasangiz, foydalanuvchi kanalga a'zo bo'lmaguncha botdan foydalana olmaydi.\n"
            "<i>(Eslatma: Bot ushbu kanalda administrator bo'lishi shart!)</i>",
            reply_markup=get_channel_manage_kb(has_channel)
        )
        await call.answer()

    elif action == "set_new_channel":
        await state.set_state(AdminStates.waiting_for_channel)
        await call.message.edit_text(
            "📢 <b>Yangi kanalni belgilash</b>\n\n"
            "Kanal username'ini (masalan: <code>@signalbooks</code>) yoki kanal ID raqamini yuboring:\n\n"
            "<i>(Eslatma: Bot kanalda admin bo'lishi kerak!)</i>",
            reply_markup=get_cancel_kb()
        )
        await call.answer()

    elif action == "remove_channel":
        await set_setting("force_channel", "")
        await call.message.edit_text(
            "✅ Majburiy obuna kanali o'chirildi! Endi hamma botdan to'g'ridan-to'g'ri foydalana oladi.",
            reply_markup=get_admin_dashboard_kb()
        )
        await call.answer("Kanal o'chirildi")

    elif action == "texts":
        await call.message.edit_text(
            "✏️ <b>Bot matnlarini tahrirlash</b>\n\n"
            "Qaysi bo'lim matnini o'zgartirmoqchisiz?",
            reply_markup=get_texts_manage_kb()
        )
        await call.answer()

    elif action == "edit_about":
        current_about = await get_setting("about_text")
        await state.set_state(AdminStates.waiting_for_about_text)
        await call.message.edit_text(
            f"ℹ️ <b>'Biz haqimizda' matnini o'zgartirish</b>\n\n"
            f"Hozirgi matn:\n\n{current_about}\n\n"
            "Yangi matnni yuboring:",
            reply_markup=get_cancel_kb()
        )
        await call.answer()

    elif action == "edit_contact":
        current_contact = await get_setting("contact_text")
        await state.set_state(AdminStates.waiting_for_contact_text)
        await call.message.edit_text(
            f"📞 <b>'Bog'lanish / Yordam' matnini o'zgartirish</b>\n\n"
            f"Hozirgi matn:\n\n{current_contact}\n\n"
            "Yangi ma'lumotlarni yuboring:",
            reply_markup=get_cancel_kb()
        )
        await call.answer()

    elif action == "export":
        users_data = await get_all_users_for_export()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["User ID", "Username", "Full Name", "Created At", "Last Active", "Is Blocked"])
        for row in users_data:
            writer.writerow(row)
        
        file_bytes = output.getvalue().encode("utf-8-sig")
        doc = BufferedInputFile(file_bytes, filename=f"signal_books_users_{int(time.time())}.csv")
        await call.message.answer_document(
            doc,
            caption=f"👥 <b>Foydalanuvchilar bazasi eksport qilindi.</b>\nJami: {len(users_data)} ta foydalanuvchi."
        )
        await call.answer("Fayl yuborildi")

    elif action == "refresh_menu":
        web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
        await set_global_menu_button(bot, web_app_url)
        await call.answer("✅ Menyu tugmasi yangilandi!", show_alert=True)

    elif action == "preview_broadcast":
        data = await state.get_data()
        from_chat_id = data.get("from_chat_id")
        message_id = data.get("message_id")
        if not from_chat_id or not message_id:
            await call.answer("⚠️ Yuboriladigan xabar topilmadi!", show_alert=True)
            return

        try:
            await bot.copy_message(
                chat_id=call.from_user.id,
                from_chat_id=from_chat_id,
                message_id=message_id
            )
            await call.answer("✅ Sinov xabari profilingizga yuborildi!", show_alert=True)
        except Exception as e:
            await call.answer(f"Xatolik: {e}", show_alert=True)

    elif action in ("confirm_broadcast", "confirm_broadcast_webapp"):
        with_webapp = (action == "confirm_broadcast_webapp")
        data = await state.get_data()
        from_chat_id = data.get("from_chat_id")
        message_id = data.get("message_id")
        await state.clear()

        if not from_chat_id or not message_id:
            await call.message.edit_text(
                "❌ Xatolik: yuboriladigan xabar topilmadi. Qaytadan urinib ko'ring.",
                reply_markup=get_admin_dashboard_kb()
            )
            return

        extra_kb = None
        if with_webapp:
            web_app_url = await get_setting("web_app_url", DEFAULT_WEB_APP_URL)
            extra_kb = get_web_app_inline_kb(web_app_url)

        await call.message.edit_text("🚀 <b>Xabar tarqatish boshlandi...</b>\nIltimos kuting.")

        users = await get_all_users()
        total_users = len(users)

        if total_users == 0:
            await call.message.edit_text(
                "⚠️ Bazada hali foydalanuvchilar yo'q!",
                reply_markup=get_admin_dashboard_kb()
            )
            return

        sent_count = 0
        blocked_count = 0
        start_time = time.time()

        for user_id in users:
            try:
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id,
                    reply_markup=extra_kb
                )
                sent_count += 1
                await asyncio.sleep(0.04)  # Telegram flood limitiga tushmaslik uchun
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                try:
                    await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=from_chat_id,
                        message_id=message_id,
                        reply_markup=extra_kb
                    )
                    sent_count += 1
                except Exception:
                    pass
            except TelegramForbiddenError:
                blocked_count += 1
                await set_user_blocked(user_id, True)
            except Exception:
                pass

        duration = round(time.time() - start_time, 2)
        btn_info = " (Mini App tugmasi bilan)" if with_webapp else ""
        report = (
            f"✅ <b>Xabar tarqatish yakunlandi!</b>{btn_info}\n\n"
            f"👥 <b>Jami foydalanuvchilar:</b> {total_users} ta\n"
            f"📥 <b>Yetkazildi:</b> {sent_count} ta\n"
            f"🚫 <b>Botni bloklaganlar:</b> {blocked_count} ta\n"
            f"⏱ <b>Sarflangan vaqt:</b> {duration} soniya"
        )
        await call.message.answer(report, reply_markup=get_admin_dashboard_kb())
        await call.answer("Xabar yuborildi")

    elif action == "cancel":
        await state.clear()
        text = await get_dashboard_text()
        await call.message.edit_text(text, reply_markup=get_admin_dashboard_kb())
        await call.answer("Amal bekor qilindi")

    elif action == "back_to_menu":
        await state.clear()
        text = await get_dashboard_text()
        await call.message.edit_text(text, reply_markup=get_admin_dashboard_kb())
        await call.answer()

    elif action == "close":
        await state.clear()
        await call.message.delete()
        await call.answer()

# --- FSM Handlerlar ---

# 1. Yangi Web App URL kiritilganda
@admin_router.message(AdminStates.waiting_for_web_app_url)
async def process_new_url(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    url = (message.text or "").strip()
    if not url.startswith("https://"):
        await message.answer(
            "⚠️ <b>Xatolik!</b> Sayt havolasi albatta <code>https://</code> bilan boshlanishi kerak.\n"
            "Iltimos, to'g'ri havolani yuboring:",
            reply_markup=get_cancel_kb()
        )
        return

    await set_setting("web_app_url", url)
    await set_global_menu_button(bot, url)
    await state.clear()

    await message.answer(
        f"✅ <b>Web App havolasi muvaffaqiyatli yangilandi!</b>\n\n"
        f"Yangi havola: <code>{url}</code>\n"
        "Barcha foydalanuvchilar va menyu tugmalari yangi havolaga o'tkazildi.",
        reply_markup=get_admin_dashboard_kb()
    )

# 2. Yangi kanal kiritilganda
@admin_router.message(AdminStates.waiting_for_channel)
async def process_new_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    channel = (message.text or "").strip()
    if not (channel.startswith("@") or channel.startswith("-100")):
        channel = f"@{channel}"

    await set_setting("force_channel", channel)
    await state.clear()
    await message.answer(
        f"✅ <b>Majburiy kanal belgilandi:</b> <code>{channel}</code>\n\n"
        "<i>Eslatma: Bot ushbu kanalda administrator ekanligiga ishonch hosil qiling!</i>",
        reply_markup=get_admin_dashboard_kb()
    )

# 3. Biz haqimizda matni
@admin_router.message(AdminStates.waiting_for_about_text)
async def process_about_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    new_text = message.html_text or message.text
    await set_setting("about_text", new_text)
    await state.clear()
    await message.answer(
        "✅ <b>'Biz haqimizda' matni muvaffaqiyatli yangilandi!</b>",
        reply_markup=get_admin_dashboard_kb()
    )

# 4. Bog'lanish matni
@admin_router.message(AdminStates.waiting_for_contact_text)
async def process_contact_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    new_text = message.html_text or message.text
    await set_setting("contact_text", new_text)
    await state.clear()
    await message.answer(
        "✅ <b>'Bog'lanish / Yordam' matni muvaffaqiyatli yangilandi!</b>",
        reply_markup=get_admin_dashboard_kb()
    )

# 5. Xabar tarqatish: xabar qabul qilish
@admin_router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    await state.set_state(AdminStates.confirm_broadcast)

    await message.reply(
        "👆 <b>Xabar qabul qilindi!</b>\n\n"
        "Uni barcha faol foydalanuvchilarga tarqatishni tasdiqlaysizmi?",
        reply_markup=get_broadcast_confirm_kb()
    )

# --- Kitob takliflarini ko'rish va boshqarish ---

@admin_router.callback_query(F.data.startswith("suggest_view:"))
async def handle_suggest_view(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)
        return
    suggestion_id = int(call.data.split(":")[1])
    item = await get_book_suggestion(suggestion_id)
    if not item:
        await call.answer("Taklif topilmadi!", show_alert=True)
        return

    status_labels = {
        "pending": "⏳ Ko'rib chiqilmoqda",
        "accepted": "✅ Qabul qilingan",
        "rejected": "❌ Rad etilgan"
    }
    status_str = status_labels.get(item["status"], item["status"])
    user_str = f"@{item['username']}" if item["username"] else "mavjud emas"
    author_str = item["author"] if item["author"] else "Ko'rsatilmadi"
    note_str = item["note"] if item["note"] else "Mavjud emas"

    text = (
        f"💡 <b>Kitob taklifi #{item['id']}</b>\n\n"
        f"📖 <b>Kitob:</b> {item['book_title']}\n"
        f"✍️ <b>Muallif:</b> {author_str}\n"
        f"📝 <b>Izoh:</b> {note_str}\n\n"
        f"👤 <b>Foydalanuvchi:</b> {item['full_name']} ({user_str})\n"
        f"🆔 <b>ID:</b> <code>{item['user_id']}</code>\n"
        f"📅 <b>Vaqt:</b> {item['created_at']}\n"
        f"📊 <b>Holat:</b> {status_str}"
    )

    photo_file_id = item.get("photo_file_id")
    if photo_file_id:
        try:
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo_file_id,
                caption=text,
                reply_markup=get_suggestion_admin_kb(suggestion_id, status=item["status"])
            )
            await call.answer()
            return
        except Exception:
            pass

    await call.message.edit_text(
        text,
        reply_markup=get_suggestion_admin_kb(suggestion_id, status=item["status"])
    )
    await call.answer()

@admin_router.callback_query(F.data.startswith("suggest_action:accept:"))
async def handle_suggest_accept(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)
        return
    suggestion_id = int(call.data.split(":")[2])
    item = await get_book_suggestion(suggestion_id)
    if not item:
        await call.answer("Taklif topilmadi!", show_alert=True)
        return

    await update_suggestion_status(suggestion_id, "accepted")

    # Foydalanuvchiga bildirishnoma yuborish
    try:
        await bot.send_message(
            chat_id=item["user_id"],
            text=(
                "🎉 <b>Ajoyib xushxabar!</b>\n\n"
                f"Siz taklif qilgan <b>«{item['book_title']}»</b> kitobi ma'muriyatimiz tomonidan qabul qilindi "
                "va tez orada <b>Signal Books</b> do'konimizga qo'shiladi! 📚\n\n"
                "Biz bilan ekanligingizdan mamnunmiz!"
            )
        )
    except Exception:
        pass

    await call.answer("✅ Taklif qabul qilindi!", show_alert=False)
    updated_text = (
        call.message.html_text + "\n\n"
        f"<i>✅ Ushbu taklif admin ({call.from_user.first_name}) tomonidan qabul qilindi va foydalanuvchiga xabar yetkazildi.</i>"
    )
    await call.message.edit_text(
        updated_text,
        reply_markup=get_suggestion_admin_kb(suggestion_id, status="accepted")
    )

@admin_router.callback_query(F.data.startswith("suggest_action:reject:"))
async def handle_suggest_reject(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)
        return
    suggestion_id = int(call.data.split(":")[2])
    item = await get_book_suggestion(suggestion_id)
    if not item:
        await call.answer("Taklif topilmadi!", show_alert=True)
        return

    await update_suggestion_status(suggestion_id, "rejected")

    # Foydalanuvchiga bildirishnoma yuborish
    try:
        await bot.send_message(
            chat_id=item["user_id"],
            text=(
                "ℹ️ <b>Kitob taklifingiz bo'yicha ma'lumot:</b>\n\n"
                f"Siz taklif qilgan <b>«{item['book_title']}»</b> kitobi mutaxassislarimiz tomonidan ko'rib chiqildi. "
                "Afsuski, ayni paytda ushbu kitobni do'konga qo'shish imkoni bo'lmadi.\n\n"
                "Boshqa qiziqarli kitob takliflaringizni kutib qolamiz!"
            )
        )
    except Exception:
        pass

    await call.answer("❌ Taklif rad etildi", show_alert=False)
    updated_text = (
        call.message.html_text + "\n\n"
        f"<i>❌ Ushbu taklif admin ({call.from_user.first_name}) tomonidan rad etildi va foydalanuvchiga ma'lum qilindi.</i>"
    )
    await call.message.edit_text(
        updated_text,
        reply_markup=get_suggestion_admin_kb(suggestion_id, status="rejected")
    )

@admin_router.callback_query(F.data.startswith("suggest_action:reply:"))
async def handle_suggest_reply_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)
        return
    suggestion_id = int(call.data.split(":")[2])
    item = await get_book_suggestion(suggestion_id)
    if not item:
        await call.answer("Taklif topilmadi!", show_alert=True)
        return

    await state.update_data(
        reply_suggestion_id=suggestion_id,
        reply_user_id=item["user_id"],
        book_title=item["book_title"]
    )
    await state.set_state(AdminStates.waiting_for_suggestion_reply)

    user_str = f"@{item['username']}" if item["username"] else item["full_name"]
    await call.message.answer(
        f"✍️ <b>Foydalanuvchiga javob yozish:</b> {user_str}\n"
        f"Kitob: <b>«{item['book_title']}»</b>\n\n"
        "Foydalanuvchiga yubormoqchi bo'lgan xabaringizni yozib yuboring:",
        reply_markup=get_cancel_reply_kb()
    )
    await call.answer()

@admin_router.callback_query(F.data == "suggest_action:cancel_reply")
async def handle_cancel_reply(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.answer("Javob yozish bekor qilindi")

@admin_router.message(AdminStates.waiting_for_suggestion_reply)
async def process_send_suggestion_reply(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    user_id = data.get("reply_user_id")
    book_title = data.get("book_title", "")
    await state.clear()

    if not user_id:
        await message.answer(
            "❌ Xatolik: foydalanuvchi ma'lumotlari topilmadi.",
            reply_markup=get_admin_dashboard_kb()
        )
        return

    reply_text = message.html_text or message.text

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"📩 <b>Signal Books ma'muriyatidan javob</b> (Taklifingiz: «{book_title}»):\n\n"
                f"{reply_text}"
            )
        )
        await message.answer(
            f"✅ Xabar foydalanuvchiga (ID: <code>{user_id}</code>) muvaffaqiyatli yetkazildi!",
            reply_markup=get_admin_dashboard_kb()
        )
    except Exception as e:
        await message.answer(
            f"❌ Xabarni yuborib bo'lmadi (Foydalanuvchi botni bloklagan bo'lishi mumkin).\nXatolik: {e}",
            reply_markup=get_admin_dashboard_kb()
        )

# --- Murojaat / Support xabarlariga javob yozish ---

@admin_router.callback_query(F.data.startswith("support_action:reply:"))
async def handle_support_reply_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Siz admin emassiz!", show_alert=True)
        return
    msg_id = int(call.data.split(":")[2])
    item = await get_support_message(msg_id)
    if not item:
        await call.answer("Murojaat topilmadi!", show_alert=True)
        return

    await state.update_data(
        reply_support_id=msg_id,
        reply_user_id=item["user_id"]
    )
    await state.set_state(AdminStates.waiting_for_support_reply)

    user_str = f"@{item['username']}" if item["username"] else item["full_name"]
    await call.message.answer(
        f"✍️ <b>Foydalanuvchiga javob yozish:</b> {user_str} (ID: <code>{item['user_id']}</code>)\n\n"
        "Foydalanuvchiga yubormoqchi bo'lgan xabaringizni yozib yuboring:",
        reply_markup=get_cancel_support_reply_kb()
    )
    await call.answer()

@admin_router.callback_query(F.data == "support_action:cancel_reply")
async def handle_cancel_support_reply(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.answer("Javob yozish bekor qilindi")

@admin_router.message(AdminStates.waiting_for_support_reply)
async def process_send_support_reply(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    user_id = data.get("reply_user_id")
    msg_id = data.get("reply_support_id")
    await state.clear()

    if not user_id:
        await message.answer(
            "❌ Xatolik: foydalanuvchi ma'lumotlari topilmadi.",
            reply_markup=get_admin_dashboard_kb()
        )
        return

    reply_text = message.html_text or message.text

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "📩 <b>Signal Books ma'muriyatidan javob:</b>\n\n"
                f"{reply_text}"
            )
        )
        if msg_id:
            await update_support_status(msg_id, "replied")

        await message.answer(
            f"✅ Javob foydalanuvchiga (ID: <code>{user_id}</code>) muvaffaqiyatli yetkazildi!",
            reply_markup=get_admin_dashboard_kb()
        )
    except Exception as e:
        await message.answer(
            f"❌ Xabarni yuborib bo'lmadi (Foydalanuvchi botni bloklagan bo'lishi mumkin).\nXatolik: {e}",
            reply_markup=get_admin_dashboard_kb()
        )

