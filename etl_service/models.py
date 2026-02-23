"""Модели данных для ETL процесса."""

import dataclasses
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003

__all__ = [
    "ExtractedUserData",
    "SourceUser",
    "SourceWeightRecord",
    "TransformedUserData",
]


@dataclasses.dataclass
class SourceUser:
    """Пользователь из исходной БД SQLite."""

    id: int
    username: str
    start_weight: Decimal | None
    target_weight: Decimal | None
    height: Decimal | None


@dataclasses.dataclass
class SourceWeightRecord:
    """Запись о весе из исходной БД SQLite."""

    user_id: int
    weight: Decimal
    record_date: date


@dataclasses.dataclass
class ExtractedUserData:
    """Данные пользователя после этапа Extract."""

    id: int
    nickname: str
    start_weight: Decimal
    target_weight: Decimal
    height: Decimal
    current_weight: Decimal | None


@dataclasses.dataclass
class TransformedUserData:
    """Данные пользователя после этапа Transform (для витрины)."""

    id: int
    nickname: str
    current_point: Decimal
    target_point: Decimal
    lost_weight: Decimal
