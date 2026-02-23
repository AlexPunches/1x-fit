"""Базовый класс для трансформеров."""

from abc import ABC, abstractmethod
from typing import TypeVar

ExtractData = TypeVar("ExtractData")
TransformData = TypeVar("TransformData")


class BaseTransformer[ExtractData, TransformData](ABC):
    """Базовый класс для трансформации данных."""

    @abstractmethod
    async def transform(self, data: list[ExtractData]) -> list[TransformData]:
        """Трансформация данных."""
