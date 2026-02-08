"""Конфигурация ETL сервиса."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ETLSettings(BaseSettings):
    """Конфигурация ETL процесса."""

    # Размер пакета для обработки данных
    batch_size: int = Field(default=1000, description="Размер пакета для обработки данных")

    # Интервал выполнения ETL в минутах
    interval_minutes: int = Field(default=3, description="Интервал выполнения ETL в минутах")

    class Config:
        env_prefix = "ETL_"


# Глобальный экземпляр настроек
etl_settings = ETLSettings()
