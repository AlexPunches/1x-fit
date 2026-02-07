# bot/handlers/progress.py

import sqlite3

import utils.messages as msg
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from database.models import DATABASE_PATH
from utils.visualization import (
    create_activity_chart,
    create_comparison_chart,
    create_individual_chart,
    create_total_activity_chart,
)

router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """Обработка команды /progress - отображение прогресса."""
    user_id = message.from_user.id if message.from_user and message.from_user.id is not None else 0

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        await message.answer(msg.NOT_REGISTERED)
        conn.close()
        return

    # Получаем данные пользователя
    cursor.execute("""
        SELECT username, start_weight, target_weight, height
        FROM users
        WHERE id = ?
    """, (user_id,))

    user_data = cursor.fetchone()
    username, start_weight, target_weight, _height = user_data

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

        # Формируем текст изменения веса
        if weight_change > 0:
            change_text = msg.PROGRESS_WEIGHT_LOST_TEXT_S.format(weight_change)
        elif weight_change < 0:
            change_text = msg.PROGRESS_WEIGHT_GAINED_TEXT_S.format(abs(weight_change))
        else:
            change_text = msg.PROGRESS_NO_CHANGE

        # Отправляем информацию о прогрессе
        progress_info = msg.PROGRESS_INFO_WITH_CHANGE_SSSSS.format(
            username, start_weight, last_weight, target_weight,
            change_text, "", last_date,
        )
        await message.answer(progress_info)
    else:
        await message.answer(
            msg.PROGRESS_INFO_NO_RECORDS_SS.format(username, start_weight, target_weight),
        )

    conn.close()


@router.message(Command("chart"))
async def cmd_chart(message: Message) -> None:
    """Обработка команды /chart - отображение графика прогресса."""
    user_id = message.from_user.id if message.from_user and message.from_user.id is not None else 0

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
        await message.answer(msg.NOT_REGISTERED)
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
            caption=msg.CHART_CAPTION,
        )
    else:
        await message.answer(msg.CHART_NO_DATA)


@router.message(Command("activity_chart"))
async def cmd_activity_chart(message: Message) -> None:
    """Обработка команды /activity_chart - отображение графика активности."""
    user_id = message.from_user.id if message.from_user and message.from_user.id is not None else 0

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM users
        WHERE id = ?
    """, (user_id,))

    user_exists = cursor.fetchone()

    if not user_exists:
        await message.answer(msg.NOT_REGISTERED)
        conn.close()
        return

    conn.close()

    # Создаем график активности
    chart_path = create_activity_chart(user_id)

    if chart_path:
        # Отправляем график пользователю
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption=msg.ACTIVITY_CHART_CAPTION,
        )
    else:
        await message.answer(msg.ACTIVITY_CHART_NO_DATA)


@router.message(Command("activities"))
async def cmd_activities(message: Message) -> None:
    """Обработка команды /activities - отображение статистики активности."""
    user_id = message.from_user.id if message.from_user and message.from_user.id is not None else 0

    # Проверяем, зарегистрирован ли пользователь
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        await message.answer(msg.NOT_REGISTERED)
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
        activities_info = msg.NO_ACTIVITIES_RECORDS

    await message.answer(activities_info)

    conn.close()


@router.message(Command("rating"))
async def cmd_rating(message: Message) -> None:
    """Обработка команды /rating - отображение сравнительного графика."""
    # Создаем сравнительный график прогресса
    chart_path = create_comparison_chart()

    if chart_path:
        # Отправляем график всем пользователям
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption="📊 Сравнительный график прогресса участников",
        )
    else:
        await message.answer(msg.COMPARISON_CHART_NO_DATA)


@router.message(Command("activity_rating"))
async def cmd_activity_rating(message: Message) -> None:
    """Обработка команды /activity_rating - отображение сравнительного графика активности."""
    # Создаем сравнительный график активности
    chart_path = create_total_activity_chart()

    if chart_path:
        # Отправляем график всем пользователям
        await message.answer_photo(
            photo=FSInputFile(chart_path),
            caption="📊 Сравнительный график активности участников (за последние 7 дней)",
        )
    else:
        await message.answer(msg.TOTAL_ACTIVITY_CHART_NO_DATA)
