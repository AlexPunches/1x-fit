# Основной файл запуска бота

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from database.models import init_db
from handlers import setup_handlers
from handlers.notifications import scheduler
from settings import settings
import utils.messages as msg


async def on_startup(app: web.Application) -> None:
    # Инициализация базы данных
    init_db()

    # Запуск планировщика уведомлений
    scheduler.start_scheduler()


async def on_cleanup(app: web.Application) -> None:
    # Остановка планировщика уведомлений
    scheduler.stop_scheduler()


async def main() -> None:
    # Настройка логирования
    logging.basicConfig(level=getattr(logging, settings.log_min_level.upper(), logging.INFO))

    # Инициализация логгера
    logger = logging.getLogger(__name__)

    # Инициализация бота
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Инициализация диспетчера
    dp = Dispatcher()

    # Настройка обработчиков
    setup_handlers(dp)

    # Проверяем режим работы: development или production
    if settings.app_env.lower() == "development":
        # Режим разработки - запуск с polling
        logger.info(msg.BOT_STARTUP_DEV_MODE)

        # Инициализация базы данных
        init_db()

        # Запуск планировщика уведомлений
        scheduler.start_scheduler()

        try:
            await dp.start_polling(bot)
        finally:
            # Остановка планировщика при завершении работы
            scheduler.stop_scheduler()
    else:
        # Режим продакшн - запуск с webhook
        # Получение webhook URL из настроек
        webhook_url = settings.webhook_url

        # Установка webhook
        # Если используется самоподписной сертификат, нужно передать его в Telegram
        # см. инструкции в nginx/ssl_setup_instructions.md
        await bot.set_webhook(webhook_url)

        # Настройка веб-приложения
        app = web.Application()

        # Регистрация обработчика запросов
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )

        # Регистрация маршрута для вебхука
        webhook_requests_handler.register(app, path="/webhook")

        # Настройка приложения
        setup_application(app, dp, bot=bot)

        # Добавление функций запуска и остановки
        app.on_startup.append(on_startup)
        app.on_cleanup.append(on_cleanup)

        # Получение хоста и порта из настроек
        host = settings.host
        port = settings.port

        # Запуск веб-сервера
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(msg.BOT_STARTED_ON_HOST_PORT_SS, host, port)

        # Бесконечный цикл
        try:
            await asyncio.sleep(float("inf"))
        except (KeyboardInterrupt, SystemExit):
            logger.warning(msg.SHUTTING_DOWN)
        finally:
            # Остановка планировщика при завершении работы
            scheduler.stop_scheduler()
            await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
