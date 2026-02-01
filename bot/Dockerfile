# Dockerfile для 1x-fit бота

FROM python:3.13-slim

# Установка системных зависимостей для компиляции пакетов и работы приложения
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    pkg-config \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16t64 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка pip-зависимостей
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка рабочей директории в bot (базовая директория приложения)
WORKDIR /app/bot

# Создание необходимых директорий
RUN mkdir -p /app/data /app/charts

# Копирование исходного кода в рабочую директорию
COPY . .

# Проверка, что все зависимости доступны (Pillow импортируется как PIL)
RUN python -c "import aiogram, matplotlib, seaborn, schedule, dotenv, pytz; from PIL import Image; print('Все зависимости успешно импортированы')"

# Открытие порта, который будет использоваться для вебхука
EXPOSE 8000

# Команда запуска приложения
CMD ["python", "main.py"]