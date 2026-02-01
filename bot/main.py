# Основной файл запуска бота

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN
from handlers import setup_handlers
from database.models import init_db
from handlers.notifications import scheduler


async def on_startup(app: web.Application):
    # Инициализация базы данных
    init_db()

    # Запуск планировщика уведомлений
    asyncio.create_task(scheduler.start_scheduler())


async def on_cleanup(app: web.Application):
    # Остановка планировщика уведомлений
    scheduler.stop_scheduler()


async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    # Инициализация бота
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Инициализация диспетчера
    dp = Dispatcher()

    # Настройка обработчиков
    setup_handlers(dp)

    # Получение webhook URL из переменной окружения или использование стандартного
    webhook_url = os.getenv('WEBHOOK_URL')

    # Установка webhook
    # Если используется самоподписной сертификат, нужно передать его в Telegram
    # см. инструкции в nginx/ssl_setup_instructions.md
    await bot.set_webhook(webhook_url)

    # Настройка веб-приложения
    app = web.Application()

    # Регистрация обработчика запросов
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )

    # Регистрация маршрута для вебхука
    webhook_requests_handler.register(app, path="/webhook")

    # Настройка приложения
    setup_application(app, dp, bot=bot)

    # Добавление функций запуска и остановки
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Получение хоста и порта из переменных окружения
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))

    # Запуск веб-сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logging.info(f"Бот запущен на {host}:{port}")
    logging.info("Кэширование Docker-слоев ускоряет повторные сборки")

    # Бесконечный цикл
    try:
        await asyncio.sleep(float('inf'))
    except (KeyboardInterrupt, SystemExit):
        logging.warning("Shutting down...")
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())