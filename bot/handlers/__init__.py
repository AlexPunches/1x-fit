# bot/handlers/__init__.py

from aiogram import Router


def setup_handlers(dp):
    """Функция для регистрации всех обработчиков"""
    from . import registration, daily_polls, progress, notifications

    # Создание роутеров
    registration_router = registration.router
    daily_polls_router = daily_polls.router
    progress_router = progress.router
    notifications_router = notifications.router

    # Включение роутеров в диспетчер
    dp.include_router(registration_router)
    dp.include_router(daily_polls_router)
    dp.include_router(progress_router)
    dp.include_router(notifications_router)