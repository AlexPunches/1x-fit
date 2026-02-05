from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from settings import settings

router = Router()


@router.message(Command("test"))
async def cmd_test(message: Message):
    """Тестовая команда для проверки работоспособности бота
    """
    env_status = "разработки" if settings.app_env.lower() == "development" else "продакшена"

    response_text = (
        f"✅ Бот работает!\n"
        f"🔧 Режим работы: {env_status}\n"
        f"🤖 Телеграм ID: {message.from_user.id}\n"
        f"👤 Имя пользователя: {message.from_user.full_name}"
    )

    await message.answer(response_text)
