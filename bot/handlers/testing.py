import utils.messages as msg
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

    response_text = msg.TEST_RESPONSE_SSS.format(env_status, user_id, full_name)
    await message.answer(response_text)
