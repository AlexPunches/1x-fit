"""Настройка периодического выполнения ETL процесса."""

import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import etl_settings
from pipelines.user_progress import UserProgressPipeline

logger = logging.getLogger(__name__)


async def run_etl_pipeline() -> None:
    """Функция для запуска ETL pipeline."""
    logger.info("Запуск ETL pipeline")
    pipeline = UserProgressPipeline()
    await pipeline.run()


def setup_periodic_etl() -> AsyncIOScheduler:
    """Настройка периодического выполнения ETL процесса."""
    logger.debug("Настройка планировщика ETL процесса")
    scheduler = AsyncIOScheduler()

    # Запуск планировщика
    scheduler.start()

    # Добавление задания на выполнение ETL с интервалом из настроек
    scheduler.add_job(
        func=run_etl_pipeline,
        trigger=IntervalTrigger(minutes=etl_settings.interval_minutes),
        id="etl_job",
        name="ETL процесс для загрузки данных в витрину",
        replace_existing=True,
    )

    logger.info("Планировщик ETL запущен. ETL будет выполняться каждые %s минут(ы).", etl_settings.interval_minutes)
    return scheduler


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
