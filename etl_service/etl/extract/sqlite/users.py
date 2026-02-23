"""Экстрактор пользователей из SQLite."""

import logging
from decimal import Decimal

from etl.extract.base import BaseSQLiteExtractor
from models import SourceUser

logger = logging.getLogger(__name__)


class UserExtractor(BaseSQLiteExtractor[SourceUser]):
    """Извлечение данных о пользователях из SQLite."""

    async def extract(self) -> list[SourceUser]:
        """Получение пользователей из исходной базы данных."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, username, start_weight, target_weight, height
            FROM users
        """)

        rows = cursor.fetchall()
        users = [
            SourceUser(
                id=row["id"],
                username=row["username"],
                start_weight=Decimal(str(row["start_weight"])) if row["start_weight"] else None,
                target_weight=Decimal(str(row["target_weight"])) if row["target_weight"] else None,
                height=Decimal(str(row["height"])) if row["height"] else None,
            )
            for row in rows
        ]

        logger.info("Извлечено %s пользователей", len(users))
        return users
