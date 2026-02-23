"""Реестр витрин данных для динамической регистрации pipeline."""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "ViewRegistry",
    "view_registry",
]


class RunnablePipeline(Protocol):
    """Протокол для любого pipeline с методом run."""

    async def run(self) -> None:
        """Запуск pipeline."""
        ...


class ViewRegistry:
    """Реестр витрин данных."""

    def __init__(self) -> None:
        self._pipelines: dict[str, type[RunnablePipeline]] = {}

    def register(
        self, name: str,
    ) -> Callable[[type[RunnablePipeline]], type[RunnablePipeline]]:
        """Декоратор для регистрации pipeline витрины."""

        def decorator(cls: type[RunnablePipeline]) -> type[RunnablePipeline]:
            self._pipelines[name] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[RunnablePipeline] | None:
        """Получение pipeline по имени витрины."""
        return self._pipelines.get(name)

    def get_all(self) -> dict[str, type[RunnablePipeline]]:
        """Получение всех зарегистрированных pipeline."""
        return self._pipelines.copy()


# Глобальный экземпляр реестра
view_registry = ViewRegistry()
