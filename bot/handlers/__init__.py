from aiogram import Router


def setup_handlers(dp: Router) -> None:
    """Функция для регистрации всех обработчиков."""
    from . import daily_polls, notifications, progress, registration, testing  # noqa: PLC0415

    # Создание роутеров
    registration_router = registration.router
    daily_polls_router = daily_polls.router
    progress_router = progress.router
    notifications_router = notifications.router
    testing_router = testing.router

    # Включение роутеров в диспетчер
    dp.include_router(registration_router)
    dp.include_router(daily_polls_router)
    dp.include_router(progress_router)
    dp.include_router(notifications_router)
    dp.include_router(testing_router)
