"""Главный файл для запуска ETL сервиса."""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

from etl_service.init_tables import init_analytics_tables
from etl_service.scheduler import run_etl_scheduler

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
