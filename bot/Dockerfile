FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libpq-dev \
    python3-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/bot

RUN mkdir -p /app/data /app/charts

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]