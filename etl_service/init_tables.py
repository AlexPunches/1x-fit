"""Скрипт создания таблиц в витрине данных."""

import logging

import asyncpg

import ddl
from config import etl_settings

logger = logging.getLogger(__name__)


async def init_analytics_tables() -> None:
    """Инициализация таблиц в витрине данных."""
    if not etl_settings.anal_postgres_db:
        error_msg = "Не задана строка подключения к аналитической БД"
        raise ValueError(error_msg)

    # Логирование параметров подключения
    logger.info(
        "Подключение к аналитической БД: host=%s, port=%s, user=%s, database=%s",
        etl_settings.anal_postgres_host,
        etl_settings.anal_postgres_port,
        etl_settings.anal_postgres_user,
        etl_settings.anal_postgres_db,
    )

    # Подключение к PostgreSQL
    try:
        conn = await asyncpg.connect(
            host=etl_settings.anal_postgres_host,
            port=etl_settings.anal_postgres_port,
            user=etl_settings.anal_postgres_user,
            password=etl_settings.anal_postgres_password,
            database=etl_settings.anal_postgres_db,
        )

        logger.debug("Успешное подключение к аналитической БД")
    except Exception:
        logger.exception("Ошибка подключения к аналитической БД")
        raise

    try:
        # Выполнение всех DDL команд
        for ddl_command in ddl.ALL_DDL_COMMANDS:
            logger.debug("Выполняется DDL команда: %s...", ddl_command[:50])
            await conn.execute(ddl_command)

        logger.info("Таблицы витрины данных успешно созданы или уже существуют.")

    finally:
        await conn.close()
        logger.debug("Соединение с аналитической БД закрыто")


__all__ = [
    "init_analytics_tables",
]
