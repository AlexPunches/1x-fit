"""Скрипт создания таблиц в витрине данных."""

import logging

import asyncpg
from etl_service.ddl import ALL_DDL_COMMANDS
from settings import settings

logger = logging.getLogger(__name__)


async def init_analytics_tables() -> None:
    """Инициализация таблиц в витрине данных."""
    if not settings.anal_postgres_db:
        error_msg = "Не задана строка подключения к аналитической БД"
        raise ValueError(error_msg)

    # Подключение к PostgreSQL
    conn = await asyncpg.connect(
        host=settings.anal_postgres_host or "localhost",
        port=settings.anal_postgres_port or 5432,
        user=settings.anal_postgres_user,
        password=settings.anal_postgres_password,
        database=settings.anal_postgres_db,
    )

    try:
        # Выполнение всех DDL команд
        for ddl_command in ALL_DDL_COMMANDS:
            await conn.execute(ddl_command)

        logger.info("Таблицы витрины данных успешно созданы или уже существуют.")

    finally:
        await conn.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_analytics_tables())
