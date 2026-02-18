from aiogram import Router


def setup_handlers(dp: Router) -> None:
    """Функция для регистрации всех обработчиков."""
    from . import daily_polls, notifications, registration  # noqa: PLC0415

    # Создание роутеров
    registration_router = registration.router
    daily_polls_router = daily_polls.router
    notifications_router = notifications.router

    # Включение роутеров в диспетчер
    dp.include_router(registration_router)
    dp.include_router(daily_polls_router)
    dp.include_router(notifications_router)
