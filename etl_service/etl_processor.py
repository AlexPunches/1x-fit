"""ETL процесс для загрузки данных из SQLite в PostgreSQL."""

import logging
import sqlite3
import typing
from datetime import date
from decimal import Decimal

import asyncpg
from config import etl_settings
from models import Activity, ActivityData, User, WeightData

logger = logging.getLogger(__name__)


class ETLProcessor:
    def __init__(self, batch_size: int | None = None) -> None:
        self.source_conn: sqlite3.Connection | None = None
        self.target_conn = None
        self.batch_size = batch_size or etl_settings.batch_size

    async def connect_to_sources(self) -> None:
        """Подключение к исходной и целевой базам данных."""
        # Подключение к исходной SQLite базе
        logger.debug(f"Подключение к исходной базе данных: {etl_settings.database_path}")
        self.source_conn = sqlite3.connect(etl_settings.database_path)
        logger.debug("Успешное подключение к исходной базе данных")

        # Подключение к целевой PostgreSQL базе
        if not etl_settings.anal_postgres_db:
            error_msg = "Не задана строка подключения к аналитической БД"
            raise ValueError(error_msg)

        # Логирование параметров подключения к целевой БД
        logger.info(f"Подключение к целевой аналитической БД: host={etl_settings.anal_postgres_host or 'localhost'}, "
                    f"port={etl_settings.anal_postgres_port or 5432}, "
                    f"user={etl_settings.anal_postgres_user}, "
                    f"database={etl_settings.anal_postgres_db}")
        
        logger.debug(f"Детали подключения к целевой БД: host_raw={etl_settings.anal_postgres_host}, "
                     f"port_raw={etl_settings.anal_postgres_port}, "
                     f"user_raw={etl_settings.anal_postgres_user}, "
                     f"password_present={bool(etl_settings.anal_postgres_password)}, "
                     f"database_raw={etl_settings.anal_postgres_db}")

        try:
            self.target_conn = await asyncpg.connect(
                host=etl_settings.anal_postgres_host or "localhost",
                port=etl_settings.anal_postgres_port or 5432,
                user=etl_settings.anal_postgres_user,
                password=etl_settings.anal_postgres_password,
                database=etl_settings.anal_postgres_db,
            )
            
            logger.debug("Успешное подключение к целевой аналитической БД")
        except Exception as e:
            logger.error(f"Ошибка подключения к целевой аналитической БД: {str(e)}")
            logger.error(f"Проверьте настройки подключения: host={etl_settings.anal_postgres_host}, "
                         f"port={etl_settings.anal_postgres_port}, "
                         f"user={etl_settings.anal_postgres_user}, "
                         f"database={etl_settings.anal_postgres_db}")
            raise

    async def disconnect_from_sources(self) -> None:
        """Закрытие соединений."""
        if self.source_conn:
            self.source_conn.close()
            logger.debug("Соединение с исходной базой данных закрыто")
        if self.target_conn:
            await self.target_conn.close()
            logger.debug("Соединение с целевой аналитической БД закрыто")

    async def get_users_from_source(self) -> list[dict[str, typing.Any]]:
        """Получение пользователей из исходной базы данных."""
        cursor = self.source_conn.cursor()
        cursor.execute("""
            SELECT id, username FROM users
        """)
        rows = cursor.fetchall()
        return [{"id": row[0], "nickname": row[1]} for row in rows]

    async def get_activities_from_source(self) -> list[dict[str, typing.Any]]:
        """Получение типов активностей из исходной базы данных."""
        cursor = self.source_conn.cursor()
        cursor.execute("""
            SELECT id, name, unit, calories_per_unit FROM activity_types
        """)
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "unit": row[2],
                "calories_per_unit": row[3] if row[3] is not None else None,
            }
            for row in rows
        ]

    async def get_weight_data_from_source_batch(self, offset: int = 0) -> list[dict[str, typing.Any]]:
        """Получение данных о весе из исходной базы данных порционно."""
        cursor = self.source_conn.cursor()
        cursor.execute("""
            SELECT user_id, weight, record_date FROM weight_records
            ORDER BY user_id, record_date
            LIMIT ? OFFSET ?
        """, (self.batch_size, offset))
        rows = cursor.fetchall()
        return [
            {
                "user_id": row[0],
                "weight": Decimal(str(row[1])),
                "date": date.fromisoformat(row[2].split()[0]),  # Преобразование строки даты в объект date
            }
            for row in rows
        ]

    async def get_activity_data_from_source_batch(self, offset: int = 0) -> list[dict[str, typing.Any]]:
        """Получение данных об активности из исходной базы данных порционно."""
        cursor = self.source_conn.cursor()
        cursor.execute("""
            SELECT ar.user_id, ar.activity_type_id, ar.value, ar.calories, ar.record_date
            FROM activity_records ar
            ORDER BY ar.user_id, ar.activity_type_id, ar.record_date
            LIMIT ? OFFSET ?
        """, (self.batch_size, offset))
        rows = cursor.fetchall()
        return [
            {
                "user_id": row[0],
                "activity_id": row[1],
                "value": Decimal(str(row[2])),
                "calories": int(row[3]) if row[3] is not None else 0,
                "date": date.fromisoformat(row[4].split()[0]),
            }
            for row in rows
        ]

    async def get_existing_users_in_target(self) -> list[int]:
        """Получение ID пользователей, уже существующих в целевой базе."""
        records = await self.target_conn.fetch("SELECT id FROM users")
        return [record["id"] for record in records]

    async def get_existing_activities_in_target(self) -> list[int]:
        """Получение ID активностей, уже существующих в целевой базе."""
        records = await self.target_conn.fetch("SELECT id FROM activities")
        return [record["id"] for record in records]

    async def get_existing_weight_data_in_target(self) -> set[tuple]:
        """Получение существующих записей о весе в целевой базе (user_id, date)."""
        records = await self.target_conn.fetch("SELECT user_id, date FROM weight_data")
        return {(record["user_id"], record["date"]) for record in records}

    async def get_existing_activity_data_in_target(self) -> set[tuple]:
        """Получение существующих записей об активности в целевой базе (user_id, activity_id, date)."""
        records = await self.target_conn.fetch("SELECT user_id, activity_id, date FROM activity_data")
        return {(record["user_id"], record["activity_id"], record["date"]) for record in records}

    async def insert_users_to_target(self, users: list[User]) -> None:
        """Вставка пользователей в целевую базу."""
        if not users:
            return

        # Подготовка данных для вставки
        values = [(user.id, user.nickname) for user in users]

        await self.target_conn.executemany("""
            INSERT INTO users (id, nickname)
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET
                nickname = EXCLUDED.nickname
        """, values)

    async def insert_activities_to_target(self, activities: list[Activity]) -> None:
        """Вставка типов активностей в целевую базу."""
        if not activities:
            return

        # Подготовка данных для вставки
        values = [
            (activity.id, activity.name, activity.unit, activity.calories_per_unit)
            for activity in activities
        ]

        await self.target_conn.executemany("""
            INSERT INTO activities (id, name, unit, calories_per_unit)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                unit = EXCLUDED.unit,
                calories_per_unit = EXCLUDED.calories_per_unit
        """, values)

    async def insert_weight_data_to_target(self, weight_data: list[WeightData]) -> None:
        """Вставка данных о весе в целевую базу."""
        if not weight_data:
            return

        # Подготовка данных для вставки
        values = [
            (wd.user_id, wd.weight, wd.date)
            for wd in weight_data
        ]

        await self.target_conn.executemany("""
            INSERT INTO weight_data (user_id, weight, date)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, date) DO NOTHING
        """, values)

    async def insert_activity_data_to_target(self, activity_data: list[ActivityData]) -> None:
        """Вставка данных об активности в целевую базу."""
        if not activity_data:
            return

        # Подготовка данных для вставки
        values = [
            (ad.user_id, ad.activity_id, ad.date, ad.value, ad.calories)
            for ad in activity_data
        ]

        await self.target_conn.executemany("""
            INSERT INTO activity_data (user_id, activity_id, date, value, calories)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id, activity_id, date) DO NOTHING
        """, values)

    async def extract_transform_load(self) -> None:
        """Основной метод ETL процесса."""
        await self.connect_to_sources()

        try:
            # Извлечение данных из исходной базы
            source_users = await self.get_users_from_source()
            source_activities = await self.get_activities_from_source()

            # Получение существующих данных в целевой базе
            existing_user_ids = await self.get_existing_users_in_target()
            existing_activity_ids = await self.get_existing_activities_in_target()
            existing_weight_keys = await self.get_existing_weight_data_in_target()
            existing_activity_keys = await self.get_existing_activity_data_in_target()

            # Преобразование и загрузка пользователей
            new_users = [
                User(id=user["id"], nickname=user["nickname"])
                for user in source_users
                if user["id"] not in existing_user_ids
            ]
            await self.insert_users_to_target(new_users)

            # Преобразование и загрузка активностей
            new_activities = [
                Activity(
                    id=activity["id"],
                    name=activity["name"],
                    unit=activity["unit"],
                    calories_per_unit=activity["calories_per_unit"],
                )
                for activity in source_activities
                if activity["id"] not in existing_activity_ids
            ]
            await self.insert_activities_to_target(new_activities)

            logger.info("Загружено: %s пользователей, %s активностей.", len(new_users), len(new_activities))

            # Обработка данных о весе порционно
            offset = 0
            total_weight_loaded = 0

            while True:
                source_weight_data = await self.get_weight_data_from_source_batch(offset)

                if not source_weight_data:
                    break

                # Фильтрация новых записей веса
                new_weight_data = [
                    WeightData(
                        user_id=wd["user_id"],
                        weight=wd["weight"],
                        date=wd["date"],
                    )
                    for wd in source_weight_data
                    if (wd["user_id"], wd["date"]) not in existing_weight_keys
                ]

                # Загрузка данных в целевую базу
                await self.insert_weight_data_to_target(new_weight_data)
                total_weight_loaded += len(new_weight_data)

                logger.debug(
                    "Обработано %s записей веса, добавлено %s новых.",
                    offset + len(source_weight_data),
                    len(new_weight_data),
                )

                offset += self.batch_size

                # Освобождение памяти
                del source_weight_data
                del new_weight_data

            # Обработка данных об активности порционно
            offset = 0
            total_activity_loaded = 0

            while True:
                source_activity_data = await self.get_activity_data_from_source_batch(offset)

                if not source_activity_data:
                    break

                # Фильтрация новых записей активности
                new_activity_data = [
                    ActivityData(
                        user_id=ad["user_id"],
                        activity_id=ad["activity_id"],
                        date=ad["date"],
                        value=ad["value"],
                        calories=ad["calories"],
                    )
                    for ad in source_activity_data
                    if (ad["user_id"], ad["activity_id"], ad["date"]) not in existing_activity_keys
                ]

                # Загрузка данных в целевую базу
                await self.insert_activity_data_to_target(new_activity_data)
                total_activity_loaded += len(new_activity_data)

                logger.debug(
                    "Обработано %s записей активности, добавлено %s новых.",
                    offset + len(source_activity_data),
                    len(new_activity_data),
                )

                offset += self.batch_size

                # Освобождение памяти
                del source_activity_data
                del new_activity_data

            logger.info(
                "ETL процесс завершен. Всего загружено: %s записей веса, %s записей активности.",
                total_weight_loaded,
                total_activity_loaded,
            )

        finally:
            await self.disconnect_from_sources()


async def run_etl_process() -> None:
    """Функция для запуска ETL процесса."""
    processor = ETLProcessor(batch_size=1000)
    await processor.extract_transform_load()
