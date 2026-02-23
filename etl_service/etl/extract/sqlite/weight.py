"""Экстрактор записей о весе из SQLite."""

import logging
from datetime import date
from decimal import Decimal

from etl.extract.base import BaseSQLiteExtractor
from models import SourceWeightRecord

logger = logging.getLogger(__name__)


class WeightExtractor(BaseSQLiteExtractor[SourceWeightRecord]):
    """Извлечение данных о весе пользователей из SQLite."""

    async def extract(self) -> list[SourceWeightRecord]:
        """Получение записей о весе из исходной базы данных."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT user_id, weight, record_date
            FROM weight_records
            ORDER BY user_id, record_date
        """)

        rows = cursor.fetchall()
        records = []

        for row in rows:
            record_date_str = row["record_date"]
            # Извлекаем дату из строки timestamp
            if " " in record_date_str:
                record_date_str = record_date_str.split()[0]

            records.append(
                SourceWeightRecord(
                    user_id=row["user_id"],
                    weight=Decimal(str(row["weight"])),
                    record_date=date.fromisoformat(record_date_str),
                ),
            )

        logger.info("Извлечено %s записей о весе", len(records))
        return records
