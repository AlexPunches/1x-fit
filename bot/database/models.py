# bot/database/models.py
import logging
import sqlite3

from settings import settings

logger = logging.getLogger(__name__)
DATABASE_PATH = settings.database_path


def init_db() -> None:
    """Инициализация базы данных."""
    logger.info(DATABASE_PATH)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            gender TEXT CHECK(gender IN ('M', 'F')),
            age INTEGER,
            height REAL,
            start_weight REAL,
            target_weight REAL,
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Создание таблицы записей веса
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            record_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Создание таблицы типов активности
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            unit TEXT NOT NULL,  -- единица измерения (шаги, минуты, км, ккал)
            calories_per_unit REAL,  -- коэффициент для перевода в калории (может быть NULL)
            description TEXT  -- описание активности
        )
    """)

    # Заполнение таблицы типов активности по умолчанию
    activities_defaults = [
        ("walking", "steps", 0.04, "Ходьба (шаги)"),
        ("running", "minutes", 12.0, "Бег (минуты)"),
        ("cycling", "km", 40.0, "Велосипед (км)"),
        ("cardio", "kcal", 1.0, "Кардио (ккал)"),
    ]

    for activity in activities_defaults:
        cursor.execute("""
            INSERT OR IGNORE INTO activity_types (name, unit, calories_per_unit, description)
            VALUES (?, ?, ?, ?)
        """, activity)

    # Создание таблицы записей активности
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type_id INTEGER NOT NULL,
            value REAL NOT NULL,  -- значение в единицах измерения типа активности
            calories REAL,  -- рассчитанные калории (может быть NULL, если уже указаны)
            record_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (activity_type_id) REFERENCES activity_types (id)
        )
    """)

    # Индексы для улучшения производительности
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weight_records_user_date ON weight_records (user_id, record_date)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_activity_records_user_date ON activity_records (user_id, record_date)",
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weight_records_date ON weight_records (record_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_records_date ON activity_records (record_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_records_type ON activity_records (activity_type_id)")

    conn.commit()
    conn.close()
