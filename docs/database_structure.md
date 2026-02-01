# Структура базы данных SQLite

## Общее описание

База данных будет реализована с использованием SQLite и будет содержать три основные таблицы:
- users - информация о зарегистрированных участниках
- weight_records - ежедневные записи веса участников
- step_records - ежедневные записи количества шагов участников

## Таблица users

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ, ID пользователя в Telegram |
| username | TEXT | Ник участника |
| gender | TEXT | Пол (M/F) |
| age | INTEGER | Возраст |
| height | REAL | Рост в см |
| start_weight | REAL | Стартовый вес |
| target_weight | REAL | Целевой вес |
| registration_date | TEXT | Дата регистрации |

### SQL-запрос для создания таблицы

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F')),
    age INTEGER,
    height REAL,
    start_weight REAL,
    target_weight REAL,
    registration_date TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Таблица weight_records

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| user_id | INTEGER | Внешний ключ, ссылка на пользователя |
| weight | REAL | Вес в кг |
| record_date | TEXT | Дата и время записи |

### SQL-запрос для создания таблицы

```sql
CREATE TABLE IF NOT EXISTS weight_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weight REAL NOT NULL,
    record_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Таблица step_records

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| user_id | INTEGER | Внешний ключ, ссылка на пользователя |
| steps_count | INTEGER | Количество шагов |
| record_date | TEXT | Дата и время записи |

### SQL-запрос для создания таблицы

```sql
CREATE TABLE IF NOT EXISTS step_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    steps_count INTEGER NOT NULL,
    record_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Индексы

Для улучшения производительности рекомендуется создать следующие индексы:

```sql
-- Индекс для быстрого поиска записей по пользователю и дате
CREATE INDEX IF NOT EXISTS idx_weight_records_user_date ON weight_records (user_id, record_date);
CREATE INDEX IF NOT EXISTS idx_step_records_user_date ON step_records (user_id, record_date);

-- Индекс для поиска по дате
CREATE INDEX IF NOT EXISTS idx_weight_records_date ON weight_records (record_date);
CREATE INDEX IF NOT EXISTS idx_step_records_date ON step_records (record_date);
```

## Возможные дополнительные таблицы

В будущем могут потребоваться дополнительные таблицы для расширения функциональности:

- notifications_log - для отслеживания отправленных уведомлений
- achievements - для хранения достижений участников
- challenges - для хранения информации о различных челленджах

## Совместимость с Python 3.13

Структура базы данных полностью совместима с Python 3.13 и использует стандартную библиотеку sqlite3, доступную в этой версии Python.