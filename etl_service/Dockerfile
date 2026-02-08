# Dockerfile для ETL сервиса 1x-fit

FROM python:3.14-slim

# Установка системных зависимостей для компиляции пакетов и работы приложения
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Установка pip-зависимостей
WORKDIR /app

# Создание необходимых директорий
RUN mkdir -p /app/data

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка рабочей директории в etl_service (базовая директория приложения)
WORKDIR /app/etl_service

# Копирование исходного кода в рабочую директорию
COPY . .

# Открытие порта, который будет использоваться для вебхука
EXPOSE 8000

# Команда запуска приложения
CMD ["python", "main.py"]