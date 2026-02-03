# bot/handlers/notifications.py

import sqlite3

import pytz
from aiogram import Bot, Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.models import DATABASE_PATH
from settings import settings

# Создаем роутер для уведомлений
router = Router()


class NotificationScheduler:
    def __init__(self):
        self.bot = Bot(token=settings.bot_token)
        self.scheduler = AsyncIOScheduler()

    def start_scheduler(self):
        """Запуск планировщика уведомлений"""
        # Используем московский часовой пояс
        tz = pytz.timezone("Europe/Moscow")

        # Разбор времени уведомлений из настроек
        weight_hour, weight_minute = map(int, settings.weight_notification_time.split(":"))
        activity_hour, activity_minute = map(int, settings.activity_notification_time.split(":"))

        # Добавляем задачи в планировщик
        self.scheduler.add_job(
            self.send_weight_reminders,
            'cron',
            hour=weight_hour,
            minute=weight_minute,
            timezone=tz,
            id='weight_reminder'
        )

        self.scheduler.add_job(
            self.send_activity_reminders,
            'cron',
            hour=activity_hour,
            minute=activity_minute,
            timezone=tz,
            id='activity_reminder'
        )

        # Запускаем планировщик
        self.scheduler.start()

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
                    text="⏰ Привет! Пожалуйста, введи свой сегодняшний вес в килограммах. Используй команду /weight или просто пришли число.",
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
                    text="⏰ Не забудь ввести сегодняшнюю активность! Пожалуйста, используй команду /activity, чтобы ввести данные о своей активности за сегодня.",
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

        conn.close()

    def stop_scheduler(self):
        """Остановка планировщика уведомлений"""
        if self.scheduler.running:
            self.scheduler.shutdown()


# Глобальный экземпляр планировщика
scheduler = NotificationScheduler()
