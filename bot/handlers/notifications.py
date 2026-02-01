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
        self.running = True
        while self.running:
            now = datetime.now()

            # Проверяем, нужно ли отправить уведомления о весе (в 10:00)
            if now.hour == 10 and now.minute == 0 and now.second < 10:
                await self.send_weight_reminders()

            # Проверяем, нужно ли отправить уведомления о шагах (в 22:00)
            if now.hour == 22 and now.minute == 0 and now.second < 10:
                await self.send_steps_reminders()

            # Проверяем каждую минуту
            await asyncio.sleep(60)

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

    async def send_steps_reminders(self):
        """Отправка напоминаний о вводе количества шагов"""
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
                    text="⏰ Не забудь сегодняшние шаги! Пожалуйста, введи количество шагов за сегодня. Используй команду /steps или просто пришли число."
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

        conn.close()

    def stop_scheduler(self):
        """Остановка планировщика уведомлений"""
        self.running = False


# Глобальный экземпляр планировщика
scheduler = NotificationScheduler()