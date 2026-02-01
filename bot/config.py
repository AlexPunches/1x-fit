import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Время уведомлений (в формате HH:MM)
WEIGHT_NOTIFICATION_TIME = os.getenv('WEIGHT_NOTIFICATION_TIME', '10:00')
ACTIVITY_NOTIFICATION_TIME = os.getenv('ACTIVITY_NOTIFICATION_TIME', '22:00')

DATABASE_PATH = '../data/database.db'

# Настройки графиков
CHARTS_DIR = '../charts/'