from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from settings import settings

router = Router()


@router.message(Command("test"))
async def cmd_test(message: Message) -> None:
    """Тестовая команда для проверки работоспособности бота."""
    env_status = "разработки" if settings.app_env.lower() == "development" else "продакшена"

    user_id = message.from_user.id if message.from_user and message.from_user.id is not None else 0
    full_name = message.from_user.full_name if message.from_user and message.from_user.full_name is not None else "Unknown"

    response_text = (
        f"✅ Бот работает!\n"
        f"🔧 Режим работы: {env_status}\n"
        f"🤖 Телеграм ID: {user_id}\n"
        f"👤 Имя пользователя: {full_name}"
    )

    await message.answer(response_text)
