# bot/handlers/notifications.py

import asyncio
from datetime import datetime, time
import pytz
from aiogram import Bot, Router
import sqlite3

from config import BOT_TOKEN
from database.models import DATABASE_PATH


# Создаем роутер для уведомлений
router = Router()


class NotificationScheduler:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.running = False

    async def start_scheduler(self):
        """Запуск планировщика уведомлений"""
        # Используем московский часовой пояс
        tz = pytz.timezone('Europe/Moscow')
        self.running = True

        # Переменные для отслеживания последней отправки
        last_weight_notification_day = None
        last_activity_notification_day = None

        while self.running:
            now = datetime.now(tz)
            current_day = now.date()

            # Проверяем, нужно ли отправить уведомления о весе (в 10:00 по Московскому времени)
            # Отправляем только один раз в день в 10:00
            if (now.hour == 10 and now.minute == 0 and
                last_weight_notification_day != current_day):
                await self.send_weight_reminders()
                last_weight_notification_day = current_day

            # Проверяем, нужно ли отправить уведомления об активности (в 22:00 по Московскому времени)
            # Отправляем только один раз в день в 22:00
            if (now.hour == 22 and now.minute == 0 and
                last_activity_notification_day != current_day):
                await self.send_activity_reminders()
                last_activity_notification_day = current_day

            # Проверяем каждые 30 секунд
            await asyncio.sleep(30)

    async def send_weight_reminders(self):
        """Отправка напоминаний о вводе веса"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Получаем всех пользователей
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text="⏰ Привет! Пожалуйста, введи свой сегодняшний вес в килограммах. Используй команду /weight или просто пришли число."
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

        conn.close()

    async def send_activity_reminders(self):
        """Отправка напоминаний о вводе активности"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Получаем всех пользователей
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text="⏰ Не забудь ввести сегодняшнюю активность! Пожалуйста, используй команду /activity, чтобы ввести данные о своей активности за сегодня."
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

        conn.close()

    def stop_scheduler(self):
        """Остановка планировщика уведомлений"""
        self.running = False


# Глобальный экземпляр планировщика
scheduler = NotificationScheduler()