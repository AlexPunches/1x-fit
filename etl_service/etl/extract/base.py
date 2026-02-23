"""Базовый класс для SQLite экстракторов."""

import logging
import sqlite3
from abc import abstractmethod

from config import etl_settings
from etl.base import BaseExtractor

logger = logging.getLogger(__name__)

CONNECTION_NOT_ESTABLISHED_MSG = (
    "Соединение не установлено. Вызовите connect() сначала."
)


class BaseSQLiteExtractor(BaseExtractor):
    """Базовый класс для извлечения данных из SQLite."""

    def __init__(self) -> None:
        self._connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError(CONNECTION_NOT_ESTABLISHED_MSG)
        return self._connection

    async def connect(self) -> None:
        """Подключение к SQLite базе."""
        self._connection = sqlite3.connect(etl_settings.database_path)
        self._connection.row_factory = sqlite3.Row

    async def disconnect(self) -> None:
        """Отключение от SQLite базы."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @abstractmethod
    async def extract(self) -> list:
        """Извлечение данных из SQLite."""
