"""Базовые классы для ETL процесса."""

from abc import ABC, abstractmethod
from typing import TypeVar

ExtractData = TypeVar("ExtractData")
TransformData = TypeVar("TransformData")


class BaseExtractor[ExtractData](ABC):
    """Базовый класс для извлечения данных."""

    @abstractmethod
    async def connect(self) -> None:
        """Подключение к источнику данных."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Отключение от источника данных."""

    @abstractmethod
    async def extract(self) -> list[ExtractData]:
        """Извлечение данных из источника."""


class BaseTransformer[ExtractData, TransformData](ABC):
    """Базовый класс для трансформации данных."""

    @abstractmethod
    async def transform(self, data: list[ExtractData]) -> list[TransformData]:
        """Трансформация данных."""


class BaseLoader[TransformData](ABC):
    """Базовый класс для загрузки данных."""

    @abstractmethod
    async def connect(self) -> None:
        """Подключение к целевой базе данных."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Отключение от целевой базы данных."""

    @abstractmethod
    async def load(self, data: list[TransformData]) -> None:
        """Загрузка данных в целевую базу."""


class BasePipeline[ExtractData, TransformData]:
    """Базовый класс для ETL pipeline."""

    def __init__(
        self,
        extractor: BaseExtractor[ExtractData],
        transformer: BaseTransformer[ExtractData, TransformData],
        loader: BaseLoader[TransformData],
    ) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    async def run(self) -> None:
        """Запуск ETL процесса."""
        await self.extractor.connect()
        await self.loader.connect()

        try:
            extracted_data = await self.extractor.extract()
            transformed_data = await self.transformer.transform(extracted_data)
            await self.loader.load(transformed_data)
        finally:
            await self.extractor.disconnect()
            await self.loader.disconnect()
