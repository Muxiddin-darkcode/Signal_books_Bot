from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from bot.database.db import add_or_update_user

class DatabaseMiddleware(BaseMiddleware):
    """
    Har bir kelgan xabar va callback_query dan foydalanuvchini
    aniqlab, ma'lumotlar bazasiga avtomatik qo'shish / yangilash middleware'i.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user and not user.is_bot:
            try:
                await add_or_update_user(
                    user_id=user.id,
                    username=user.username,
                    full_name=user.full_name
                )
            except Exception as e:
                # Middleware xatoligi botni to'xtatmasligi uchun log qilish kifoya
                pass

        return await handler(event, data)
