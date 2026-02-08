"""Скрипт создания таблиц в витрине данных."""

import logging

import asyncpg
from config import etl_settings
from ddl import ALL_DDL_COMMANDS

logger = logging.getLogger(__name__)


async def init_analytics_tables() -> None:
    """Инициализация таблиц в витрине данных."""
    if not etl_settings.anal_postgres_db:
        error_msg = "Не задана строка подключения к аналитической БД"
        raise ValueError(error_msg)

    # Логирование параметров подключения
    logger.info(f"Подключение к аналитической БД: host={etl_settings.anal_postgres_host or 'localhost'}, "
                f"port={etl_settings.anal_postgres_port or 5432}, "
                f"user={etl_settings.anal_postgres_user}, "
                f"database={etl_settings.anal_postgres_db}")
    
    logger.debug(f"Детали подключения: host_raw={etl_settings.anal_postgres_host}, "
                 f"port_raw={etl_settings.anal_postgres_port}, "
                 f"user_raw={etl_settings.anal_postgres_user}, "
                 f"password_present={bool(etl_settings.anal_postgres_password)}, "
                 f"database_raw={etl_settings.anal_postgres_db}")

    # Подключение к PostgreSQL
    try:
        conn = await asyncpg.connect(
            host=etl_settings.anal_postgres_host or "localhost",
            port=etl_settings.anal_postgres_port or 5432,
            user=etl_settings.anal_postgres_user,
            password=etl_settings.anal_postgres_password,
            database=etl_settings.anal_postgres_db,
        )
        
        logger.debug("Успешное подключение к аналитической БД")
    except Exception as e:
        logger.error(f"Ошибка подключения к аналитической БД: {str(e)}")
        logger.error(f"Проверьте настройки подключения: host={etl_settings.anal_postgres_host}, "
                     f"port={etl_settings.anal_postgres_port}, "
                     f"user={etl_settings.anal_postgres_user}, "
                     f"database={etl_settings.anal_postgres_db}")
        raise

    try:
        # Выполнение всех DDL команд
        for ddl_command in ALL_DDL_COMMANDS:
            logger.debug(f"Выполняется DDL команда: {ddl_command[:50]}...")
            await conn.execute(ddl_command)

        logger.info("Таблицы витрины данных успешно созданы или уже существуют.")

    finally:
        await conn.close()
        logger.debug("Соединение с аналитической БД закрыто")


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_analytics_tables())
