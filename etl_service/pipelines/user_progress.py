"""Pipeline для витрины прогресса пользователей."""

import logging

from etl.base import BasePipeline
from etl.extract.sqlite.users import UserExtractor
from etl.extract.sqlite.weight import WeightExtractor
from etl.load.postgres.users import UserLoader
from etl.registry import view_registry
from etl.transform.users import UserTransformer, merge_user_weight_data
from models import SourceUser, TransformedUserData

logger = logging.getLogger(__name__)


@view_registry.register(name="users")
class UserProgressPipeline(BasePipeline[SourceUser, TransformedUserData]):
    """ETL pipeline для витрины прогресса пользователей.

    Extract:
        - UserExtractor: извлекает пользователей из SQLite
        - WeightExtractor: извлекает записи о весе

    Transform:
        - UserTransformer: рассчитывает progress_score, target_point, lost_weight

    Load:
        - UserLoader: загружает данные в PostgreSQL таблицу users
    """

    def __init__(self) -> None:
        self.user_extractor = UserExtractor()
        self.weight_extractor = WeightExtractor()
        self.transformer = UserTransformer()
        self.loader = UserLoader()

    async def run(self) -> None:
        """Запуск ETL процесса для витрины пользователей."""
        logger.info("Запуск pipeline для витрины users")

        # Подключение к источникам
        await self.user_extractor.connect()
        await self.weight_extractor.connect()
        await self.loader.connect()

        try:
            # Extract
            users = await self.user_extractor.extract()
            weight_records = await self.weight_extractor.extract()

            # Объединение данных перед трансформацией
            merged_data = merge_user_weight_data(users, weight_records)

            # Transform
            transformed_data = await self.transformer.transform(merged_data)

            # Load
            await self.loader.load(transformed_data)

            logger.info(
                "Pipeline завершён: обработано %s пользователей",
                len(transformed_data),
            )

        finally:
            # Отключение
            await self.user_extractor.disconnect()
            await self.weight_extractor.disconnect()
            await self.loader.disconnect()
