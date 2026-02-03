# bot/handlers/progress.py

import sqlite3

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from database.models import DATABASE_PATH
from utils.visualization import create_comparison_chart, create_individual_chart

router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message):
    """Обработка команды /progress - отображение прогресса"""
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        await message.answer("Сначала необходимо зарегистрироваться. Используй команду /start")
        conn.close()
        return

    # Получаем данные пользователя
    cursor.execute("""
        SELECT username, start_weight, target_weight, height
        FROM users
        WHERE id = ?
    """, (user_id,))

    user_data = cursor.fetchone()
    username, start_weight, target_weight, height = user_data

    # Получаем последнюю запись веса
    cursor.execute("""
        SELECT weight, record_date
        FROM weight_records
        WHERE user_id = ?
        ORDER BY record_date DESC
        LIMIT 1
    """, (user_id,))

    last_weight_record = cursor.fetchone()

    if last_weight_record:
        last_weight, last_date = last_weight_record
        weight_change = start_weight - last_weight

        # Отправляем информацию о прогрессе
        progress_info = f"📊 Прогресс участника {username}:\n\n"
        progress_info += f"📈 Стартовый вес: {start_weight} кг\n"
        progress_info += f"📉 Текущий вес: {last_weight} кг\n"
        progress_info += f"🎯 Целевой вес: {target_weight} кг\n\n"

        if weight_change > 0:
            progress_info += f"✅ Сброшено: {weight_change:.2f} кг\n"
        elif weight_change < 0:
            progress_info += f"⚠️ Набрано: {abs(weight_change):.2f} кг\n"
        else:
            progress_info += "➡️ Вес не изменился\n"

        progress_info += f"\n📅 Последнее обновление: {last_date}"

        await message.answer(progress_info)
    else:
        await message.answer(
            f"📊 Прогресс участника {username}:\n\n"
            f"📈 Стартовый вес: {start_weight} кг\n"
            f"🎯 Целевой вес: {target_weight} кг\n\n"
            f"ℹ️ Пока нет записей о текущем весе. Используй команду /weight, чтобы добавить.",
        )

    conn.close()


@router.message(Command("chart"))
async def cmd_chart(message: Message):
    """Обработка команды /chart - отображение графика прогресса"""
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, start_weight, target_weight, height
        FROM users
        WHERE id = ?
    """, (user_id,))

    user_data_row = cursor.fetchone()

    if not user_data_row:
        await message.answer("Сначала необходимо зарегистрироваться. Используй команду /start")
        conn.close()
        return

    user_data = {
        "id": user_data_row[0],
        "username": user_data_row[1],
        "start_weight": user_data_row[2],
        "target_weight": user_data_row[3],
        "height": user_data_row[4],
    }

    conn.close()

    # Создаем индивидуальный график
    chart_path = create_individual_chart(user_id, user_data)

    if chart_path:
        # Отправляем график пользователю
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption="📊 Твой индивидуальный график прогресса",
        )
    else:
        await message.answer("❌ Недостаточно данных для построения графика")


@router.message(Command("activity_chart"))
async def cmd_activity_chart(message: Message):
    """Обработка команды /activity_chart - отображение графика активности"""
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM users
        WHERE id = ?
    """, (user_id,))

    user_exists = cursor.fetchone()

    if not user_exists:
        await message.answer("Сначала необходимо зарегистрироваться. Используй команду /start")
        conn.close()
        return

    conn.close()

    # Создаем график активности
    from utils.visualization import create_activity_chart
    chart_path = create_activity_chart(user_id)

    if chart_path:
        # Отправляем график пользователю
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption="📊 Твой график активности за последние 30 дней",
        )
    else:
        await message.answer("❌ Недостаточно данных для построения графика активности")


@router.message(Command("activities"))
async def cmd_activities(message: Message):
    """Обработка команды /activities - отображение статистики активности"""
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        await message.answer("Сначала необходимо зарегистрироваться. Используй команду /start")
        conn.close()
        return

    # Получаем последние записи активности пользователя
    cursor.execute("""
        SELECT ar.value, at.name, at.unit, ar.calories, ar.record_date
        FROM activity_records ar
        JOIN activity_types at ON ar.activity_type_id = at.id
        WHERE ar.user_id = ?
        ORDER BY ar.record_date DESC
        LIMIT 10
    """, (user_id,))

    activities = cursor.fetchall()

    if activities:
        activities_info = "📊 Твоя история активности (последние 10 записей):\n\n"
        for value, name, unit, calories, date in activities:
            if calories:
                activities_info += f"• {name}: {value} {unit} (сожжено: {calories:.2f} ккал) - {date}\n"
            else:
                activities_info += f"• {name}: {value} {unit} - {date}\n"
    else:
        activities_info = "📊 У тебя пока нет записей об активности. Используй команду /activity, чтобы добавить."

    await message.answer(activities_info)

    conn.close()


@router.message(Command("rating"))
async def cmd_rating(message: Message):
    """Обработка команды /rating - отображение сравнительного графика"""
    # Создаем сравнительный график прогресса
    chart_path = create_comparison_chart()

    if chart_path:
        # Отправляем график всем пользователям
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption="📊 Сравнительный график прогресса участников",
        )
    else:
        await message.answer("❌ Недостаточно данных для построения сравнительного графика")


@router.message(Command("activity_rating"))
async def cmd_activity_rating(message: Message):
    """Обработка команды /activity_rating - отображение сравнительного графика активности"""
    # Создаем сравнительный график активности
    from utils.visualization import create_total_activity_chart
    chart_path = create_total_activity_chart()

    if chart_path:
        # Отправляем график всем пользователям
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption="📊 Сравнительный график активности участников (за последние 7 дней)",
        )
    else:
        await message.answer("❌ Недостаточно данных для построения сравнительного графика активности")
