"""Главный файл для запуска ETL сервиса."""

import asyncio
import logging
import pathlib
import sys

# Добавляем путь к корню проекта
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from config import etl_settings
from init_tables import init_analytics_tables
from scheduler import run_etl_scheduler

# Настройка уровня логирования
logging.basicConfig(level=getattr(logging, etl_settings.log_min_level.upper()))
logger = logging.getLogger(__name__)


async def main() -> None:
    """Основная функция запуска ETL сервиса."""
    logger.info("Инициализация таблиц витрины данных...")
    await init_analytics_tables()

    logger.info("Запуск планировщика ETL процесса...")
    await run_etl_scheduler()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("ETL сервис остановлен пользователем.")
