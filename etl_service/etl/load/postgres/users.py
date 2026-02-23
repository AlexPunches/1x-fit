"""Лоадер для загрузки данных пользователей в PostgreSQL."""

import logging

from etl.load.base import BasePostgresLoader
from models import TransformedUserData

logger = logging.getLogger(__name__)


class UserLoader(BasePostgresLoader[TransformedUserData]):
    """Загрузка данных пользователей в PostgreSQL."""

    async def load(self, data: list[TransformedUserData]) -> None:
        """Загрузка данных пользователей в витрину.

        Использует ON CONFLICT для обновления существующих записей.
        """
        if not data:
            logger.debug("Нет данных для загрузки")
            return

        # Подготовка данных для вставки
        values = [
            (
                user.id,
                user.nickname,
                user.current_point,
                user.target_point,
                user.lost_weight,
            )
            for user in data
        ]

        await self.connection.executemany(
            """
            INSERT INTO users (id, nickname, current_point, target_point, lost_weight)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO UPDATE SET
                nickname = EXCLUDED.nickname,
                current_point = EXCLUDED.current_point,
                target_point = EXCLUDED.target_point,
                lost_weight = EXCLUDED.lost_weight
            """,
            values,
        )

        logger.info("Загружено %s пользователей в витрину", len(data))
