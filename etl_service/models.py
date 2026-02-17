"""Модели данных для витрины аналитики."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class User:
    """Модель пользователя."""

    id: int
    nickname: str | None


@dataclass
class Activity:
    """Модель типа активности."""

    id: int
    name: str
    unit: str
    calories_per_unit: Decimal | None


@dataclass
class WeightData:
    """Модель данных веса."""

    user_id: int
    weight: Decimal
    date: date


@dataclass
class ActivityData:
    """Модель данных активности."""

    user_id: int
    activity_id: int
    date: date
    value: Decimal
    calories: int


@dataclass
class UserProgress:
    """Модель прогресса пользователя."""

    user_id: int
    target_point: Decimal
    current_point: Decimal
    lost_weight: Decimal
