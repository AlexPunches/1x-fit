"""Конфигурация ETL сервиса."""
import logging
import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings


class ETLSettings(BaseSettings):
    """Конфигурация ETL процесса."""

    base_path: pathlib.Path = pathlib.Path(__file__).parent.absolute()
    database_path: pathlib.Path = base_path / "../data/database.db"

    # Размер пакета для обработки данных
    batch_size: int = Field(1000, description="Размер пакета для обработки данных")

    # Интервал выполнения ETL в минутах
    interval_minutes: int = Field(3, description="Интервал выполнения ETL в минутах")

    # Минимальный уровень логирования
    log_min_level: str = Field("INFO", description="Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    # Anal DB
    anal_postgres_db: str | None = None
    anal_postgres_user: str | None = None
    anal_postgres_password: str | None = None
    anal_postgres_port: str | None = None
    anal_postgres_host: str | None = None

    class Config:
        env_prefix = "ETL_"


# Глобальный экземпляр настроек
etl_settings = ETLSettings()


def setup_logging() -> None:
    """Настройка формата и уровня логирования."""
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(filename)s:%(lineno)d"
    logging.basicConfig(level=getattr(logging, etl_settings.log_min_level.upper()), format=log_format)


# Автоматическая настройка логирования при импорте модуля
setup_logging()


__all__ = [
    "etl_settings",
]
