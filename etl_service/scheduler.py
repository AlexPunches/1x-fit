"""Настройка периодического выполнения ETL процесса."""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import etl_settings
from etl_processor import run_etl_process

logger = logging.getLogger(__name__)


async def run_etl_process_wrapper():
    """Обертка для запуска асинхронной функции в планировщике."""
    await run_etl_process()


def setup_periodic_etl() -> AsyncIOScheduler:
    """Настройка периодического выполнения ETL процесса."""
    logger.debug("Настройка планировщика ETL процесса")
    scheduler = AsyncIOScheduler()

    # Добавление задания на выполнение ETL с интервалом из настроек
    scheduler.add_job(
        func=run_etl_process_wrapper,
        trigger=IntervalTrigger(minutes=etl_settings.interval_minutes),
        id="etl_job",
        name="ETL процесс для загрузки данных в витрину",
        replace_existing=True,
        executor='asyncio'  # Указываем, что задача асинхронная
    )

    # Запуск планировщика
    scheduler.start()

    logger.info(
        "Планировщик ETL процесса запущен. ETL будет выполняться каждые %s минут(ы).",
        etl_settings.interval_minutes,
    )
    logger.debug(f"Детали планировщика: интервал={etl_settings.interval_minutes} мин, размер пакета={etl_settings.batch_size}")

    return scheduler


import functools
import signal


def signal_handler(stop_event: asyncio.Event) -> None:
    stop_event.set()


async def run_etl_scheduler() -> None:
    """Функция для запуска планировщика ETL."""
    scheduler = setup_periodic_etl()

    # Создаем событие для остановки
    stop_event = asyncio.Event()

    # Регистрируем обработчик сигнала
    # Используем loop.add_signal_handler для корректной работы с асинхронным кодом
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)

    try:
        # Ожидание события остановки
        await stop_event.wait()
    finally:
        logger.info("Остановка планировщика ETL...")
        scheduler.shutdown()
