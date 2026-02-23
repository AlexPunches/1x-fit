"""Базовый класс для PostgreSQL лоадеров."""

import logging
from abc import abstractmethod
from typing import TypeVar

import asyncpg

from config import etl_settings

logger = logging.getLogger(__name__)

TransformData = TypeVar("TransformData")

CONNECTION_NOT_ESTABLISHED_MSG = (
    "Соединение не установлено. Вызовите connect() сначала."
)
ANALYTIC_DB_NOT_CONFIGURED_MSG = "Не задана строка подключения к аналитической БД"


class BasePostgresLoader[TransformData]:
    """Базовый класс для загрузки данных в PostgreSQL."""

    def __init__(self) -> None:
        self._connection: asyncpg.Connection | None = None

    @property
    def connection(self) -> asyncpg.Connection:
        if self._connection is None:
            raise RuntimeError(CONNECTION_NOT_ESTABLISHED_MSG)
        return self._connection

    async def connect(self) -> None:
        """Подключение к PostgreSQL базе."""
        if not etl_settings.anal_postgres_db:
            raise ValueError(ANALYTIC_DB_NOT_CONFIGURED_MSG)

        logger.info(
            "Подключение к PostgreSQL: host=%s, port=%s, database=%s",
            etl_settings.anal_postgres_host or "localhost",
            etl_settings.anal_postgres_port or 5432,
            etl_settings.anal_postgres_db,
        )

        try:
            self._connection = await asyncpg.connect(
                host=etl_settings.anal_postgres_host or "localhost",
                port=etl_settings.anal_postgres_port or 5432,
                user=etl_settings.anal_postgres_user,
                password=etl_settings.anal_postgres_password,
                database=etl_settings.anal_postgres_db,
            )
            logger.info("Успешное подключение к PostgreSQL")
        except Exception:
            logger.exception("Ошибка подключения к PostgreSQL")
            raise

    async def disconnect(self) -> None:
        """Отключение от PostgreSQL базы."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.debug("Соединение с PostgreSQL закрыто")

    @abstractmethod
    async def load(self, data: list[TransformData]) -> None:
        """Загрузка данных в PostgreSQL."""
