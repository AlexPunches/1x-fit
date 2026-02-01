# bot/database/models.py

import sqlite3
from config import DATABASE_PATH


def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    cursor.execute('''
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
    ''')
    
    # Создание таблицы записей веса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            record_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Создание таблицы записей шагов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS step_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            steps_count INTEGER NOT NULL,
            record_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Создание таблицы прогресса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            progress_points REAL NOT NULL,
            calculation_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Индексы для улучшения производительности
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weight_records_user_date ON weight_records (user_id, record_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_step_records_user_date ON step_records (user_id, record_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weight_records_date ON weight_records (record_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_step_records_date ON step_records (record_date)')
    
    conn.commit()
    conn.close()