"""Настройка периодического выполнения ETL процесса."""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from etl_service.config import etl_settings
from etl_service.etl_processor import run_etl_process

logger = logging.getLogger(__name__)


def setup_periodic_etl() -> AsyncIOScheduler:
    """Настройка периодического выполнения ETL процесса."""
    scheduler = AsyncIOScheduler()

    # Добавление задания на выполнение ETL с интервалом из настроек
    scheduler.add_job(
        func=lambda: asyncio.create_task(run_etl_process()),
        trigger=IntervalTrigger(minutes=etl_settings.interval_minutes),
        id="etl_job",
        name="ETL процесс для загрузки данных в витрину",
        replace_existing=True,
    )

    # Запуск планировщика
    scheduler.start()

    logger.info(
        "Планировщик ETL процесса запущен. ETL будет выполняться каждые %s минут(ы).",
        etl_settings.interval_minutes,
    )

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
    signal.signal(signal.SIGINT, functools.partial(signal_handler, stop_event))
    signal.signal(signal.SIGTERM, functools.partial(signal_handler, stop_event))

    try:
        # Ожидание события остановки
        await stop_event.wait()
    finally:
        logger.info("Остановка планировщика ETL...")
        scheduler.shutdown()
