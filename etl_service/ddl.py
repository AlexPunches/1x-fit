"""DDL операции для создания таблиц витрины данных."""


CREATE_TABLE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        nickname VARCHAR(255),
        current_point DECIMAL(10,4) NOT NULL,
        target_point DECIMAL(10,4) NOT NULL,
        lost_weight DECIMAL(10,4) NOT NULL
    )
"""


ALL_DDL_COMMANDS: list[str] = [
    CREATE_TABLE_USERS,
]
