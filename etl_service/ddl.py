"""DDL операции для создания таблиц витрины данных."""


# SQL команды для создания таблиц
CREATE_TABLE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        nickname VARCHAR(255)
    )
"""

CREATE_TABLE_ACTIVITIES = """
    CREATE TABLE IF NOT EXISTS activities (
        id BIGSERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        unit VARCHAR(50) NOT NULL,
        calories_per_unit DECIMAL(5,3)
    )
"""

CREATE_TABLE_WEIGHT_DATA = """
    CREATE TABLE IF NOT EXISTS weight_data (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        weight DECIMAL(5,1) NOT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE (user_id, date)
    )
"""

CREATE_TABLE_ACTIVITY_DATA = """
    CREATE TABLE IF NOT EXISTS activity_data (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        activity_id BIGINT NOT NULL,
        date DATE NOT NULL,
        value DECIMAL(8,2) NOT NULL,
        calories INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (activity_id) REFERENCES activities (id),
        UNIQUE (user_id, activity_id, date)
    )
"""

# SQL команды для создания индексов
CREATE_INDEX_WEIGHT_DATA_USER_DATE = """
    CREATE INDEX IF NOT EXISTS idx_weight_data_user_date ON weight_data (user_id, date)
"""

CREATE_INDEX_ACTIVITY_DATA_USER_DATE = """
    CREATE INDEX IF NOT EXISTS idx_activity_data_user_date ON activity_data (user_id, date)
"""

CREATE_TABLE_USER_PROGRESS = """
    CREATE TABLE IF NOT EXISTS user_progress (
        user_id BIGINT PRIMARY KEY,
        target_point DECIMAL(10,4) NOT NULL,
        current_point DECIMAL(10,4) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
"""

CREATE_INDEX_USER_PROGRESS_USER = """
    CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress (user_id)
"""


# Список всех DDL команд для инициализации
ALL_DDL_COMMANDS: list[str] = [
    CREATE_TABLE_USERS,
    CREATE_TABLE_ACTIVITIES,
    CREATE_TABLE_WEIGHT_DATA,
    CREATE_TABLE_ACTIVITY_DATA,
    CREATE_TABLE_USER_PROGRESS,
    CREATE_INDEX_WEIGHT_DATA_USER_DATE,
    CREATE_INDEX_ACTIVITY_DATA_USER_DATE,
    CREATE_INDEX_USER_PROGRESS_USER,
]
