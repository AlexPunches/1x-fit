"""Реестр витрин данных для динамической регистрации pipeline."""

from collections.abc import Callable

from etl.base import BasePipeline


class ViewRegistry:
    """Реестр витрин данных."""

    def __init__(self) -> None:
        self._pipelines: dict[str, type[BasePipeline]] = {}

    def register(self, name: str) -> Callable[[type[BasePipeline]], type[BasePipeline]]:
        """Декоратор для регистрации pipeline витрины."""

        def decorator(cls: type[BasePipeline]) -> type[BasePipeline]:
            self._pipelines[name] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[BasePipeline] | None:
        """Получение pipeline по имени витрины."""
        return self._pipelines.get(name)

    def get_all(self) -> dict[str, type[BasePipeline]]:
        """Получение всех зарегистрированных pipeline."""
        return self._pipelines.copy()


# Глобальный экземпляр реестра
view_registry = ViewRegistry()
