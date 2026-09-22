from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_dashboard_kb() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli tugmalari (rangli fonlar bilan)"""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_action:stats", style="primary"),
            InlineKeyboardButton(text="📢 Xabar tarqatish", callback_data="admin_action:broadcast", style="primary"),
        ],
        [
            InlineKeyboardButton(text="💡 Kitob takliflari", callback_data="admin_action:suggestions", style="primary"),
            InlineKeyboardButton(text="🌐 Web App URL sozlash", callback_data="admin_action:set_url", style="primary"),
        ],
        [
            InlineKeyboardButton(text="📢 Majburiy kanal", callback_data="admin_action:channel", style="primary"),
            InlineKeyboardButton(text="✏️ Matnlarni tahrirlash", callback_data="admin_action:texts", style="primary"),
        ],
        [
            InlineKeyboardButton(text="📥 Foydalanuvchilar (CSV)", callback_data="admin_action:export", style="primary"),
            InlineKeyboardButton(text="🔄 Menyu tugmasini yangilash", callback_data="admin_action:refresh_menu", style="success"),
        ],
        [
            InlineKeyboardButton(text="❌ Yopish", callback_data="admin_action:close", style="danger"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_kb() -> InlineKeyboardMarkup:
    """Jarayonni bekor qilish tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_action:cancel", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_broadcast_confirm_kb() -> InlineKeyboardMarkup:
    """Xabar tarqatishni tasdiqlash tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Barchaga yuborish", callback_data="admin_action:confirm_broadcast", style="success"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_action:cancel", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_channel_manage_kb(has_channel: bool) -> InlineKeyboardMarkup:
    """Majburiy kanal sozlamalari"""
    buttons = [
        [
            InlineKeyboardButton(text="✏️ Yangi kanal kiritish", callback_data="admin_action:set_new_channel", style="primary")
        ]
    ]
    if has_channel:
        buttons.append([
            InlineKeyboardButton(text="🗑 Majburiy obunani o'chirish", callback_data="admin_action:remove_channel", style="danger")
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Boshqaruv paneliga qaytish", callback_data="admin_action:back_to_menu", style="primary")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_texts_manage_kb() -> InlineKeyboardMarkup:
    """Bot matnlarini tahrirlash menyusi"""
    buttons = [
        [
            InlineKeyboardButton(text="ℹ️ 'Biz haqimizda' matni", callback_data="admin_action:edit_about", style="primary")
        ],
        [
            InlineKeyboardButton(text="📞 'Bog'lanish / Yordam' matni", callback_data="admin_action:edit_contact", style="primary")
        ],
        [
            InlineKeyboardButton(text="🔙 Boshqaruv paneliga qaytish", callback_data="admin_action:back_to_menu", style="primary")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_suggestion_admin_kb(suggestion_id: int, status: str = "pending") -> InlineKeyboardMarkup:
    """Yangi kitob taklifi ostidagi admin harakat tugmalari"""
    buttons = []
    if status == "pending":
        buttons.append([
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"suggest_action:accept:{suggestion_id}", style="success"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"suggest_action:reject:{suggestion_id}", style="danger")
        ])
    buttons.append([
        InlineKeyboardButton(text="✍️ Foydalanuvchiga javob yozish", callback_data=f"suggest_action:reply:{suggestion_id}", style="primary")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_suggestions_list_kb(suggestions: list[dict]) -> InlineKeyboardMarkup:
    """Takliflar ro'yxati tugmalari"""
    buttons = []
    for item in suggestions:
        status_icon = "⏳" if item["status"] == "pending" else ("✅" if item["status"] == "accepted" else "❌")
        title = item["book_title"][:22]
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} #{item['id']} {title}",
                callback_data=f"suggest_view:{item['id']}",
                style="primary"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Boshqaruv paneliga qaytish", callback_data="admin_action:back_to_menu", style="primary")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_reply_kb() -> InlineKeyboardMarkup:
    """Foydalanuvchiga javob yozishni bekor qilish tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="suggest_action:cancel_reply", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

