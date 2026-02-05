"""
Тесты для проверки работоспособности бота
"""
import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot
from aiogram.types import Message, User

from bot.handlers.testing import cmd_test
from bot.settings import settings


@pytest.mark.asyncio
async def test_cmd_test():
    """Тест команды /test"""
    # Создаем mock сообщение
    user = User(id=123456789, is_bot=False, first_name="Test", username="testuser")
    message = Message(
        message_id=1,
        date=1234567890,
        chat={"id": 123456789, "type": "private"},
        from_user=user,
        text="/test"
    )
    message.answer = AsyncMock()
    
    # Вызываем команду
    await cmd_test(message)
    
    # Проверяем, что ответ был отправлен
    message.answer.assert_called_once()
    
    # Проверяем содержимое ответа
    response_text = message.answer.call_args[0][0]
    assert "Бот работает!" in response_text
    assert "Режим работы:" in response_text
    assert str(user.id) in response_text
    assert user.first_name in response_text


def test_app_env_setting():
    """Проверяем, что переменная окружения APP_ENV корректно читается"""
    # Устанавливаем тестовое значение
    os.environ["APP_ENV"] = "development"
    
    # Пересоздаем экземпляр настроек, чтобы обновить значение
    from bot.settings import Settings
    test_settings = Settings()
    
    assert test_settings.app_env == "development"
    
    # Возвращаем значение по умолчанию
    del os.environ["APP_ENV"]
    settings.app_env = "production"


if __name__ == "__main__":
    pytest.main([__file__])