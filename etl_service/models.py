"""Модели данных для ETL процесса."""

import dataclasses
import decimal
from datetime import date


@dataclasses.dataclass
class SourceUser:
    """Пользователь из исходной БД SQLite."""

    id: int
    username: str
    start_weight: decimal.Decimal | None
    target_weight: decimal.Decimal | None
    height: decimal.Decimal | None


@dataclasses.dataclass
class SourceWeightRecord:
    """Запись о весе из исходной БД SQLite."""

    user_id: int
    weight: decimal.Decimal
    record_date: date


@dataclasses.dataclass
class ExtractedUserData:
    """Данные пользователя после этапа Extract."""

    id: int
    nickname: str
    start_weight: decimal.Decimal
    target_weight: decimal.Decimal
    height: decimal.Decimal
    current_weight: decimal.Decimal | None  # Может быть None, если нет записей о весе


@dataclasses.dataclass
class TransformedUserData:
    """Данные пользователя после этапа Transform (для витрины)."""

    id: int
    nickname: str
    current_point: decimal.Decimal  # Текущий прогресс в уе
    target_point: decimal.Decimal   # Целевой прогресс в уе
    lost_weight: decimal.Decimal    # Сброшенные кг


__all__ = [
    "ExtractedUserData",
    "SourceUser",
    "SourceWeightRecord",
    "TransformedUserData",
]
