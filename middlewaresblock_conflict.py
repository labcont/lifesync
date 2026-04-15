import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

USER_INPUT_LOCK = {}  # FSM блок
LOCKED_USERS = set()  # ГЛОБАЛЬНЫЙ блок


class BlockConflictMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id

            # ✅ разрешаем фото ВСЕГДА
            if event.photo:
                return await handler(event, data)

            # ✅ разрешаем если есть FSM состояние
            state = data.get("state")
            if state:
                current = await state.get_state()
                if current:
                    return await handler(event, data)

            # ✅ FAQ пропуск
            if event.text and "FAQ" in event.text:
                return await handler(event, data)

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if not user_id:
            return await handler(event, data)

        now = time.time()

        # 🔥 глобальный блок
        if user_id in LOCKED_USERS:
            if isinstance(event, Message):
                await event.answer("⛔ Заверши текущее действие")
                return
            else:
                return await handler(event, data)

        # 🔥 FSM блок (только текст)
        if isinstance(event, Message) and user_id in USER_INPUT_LOCK:
            if now - USER_INPUT_LOCK[user_id] < 30:
                await event.answer("⛔ Заверши текущее действие")
                return
            else:
                USER_INPUT_LOCK.pop(user_id, None)

        return await handler(event, data)