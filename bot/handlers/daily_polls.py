# bot/handlers/daily_polls.py

import sqlite3
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from database.models import DATABASE_PATH
from utils.calculations import calculate_final_score

router = Router()


@router.message(Command("weight"))
async def cmd_weight(message: Message):
    """Обработка команды /weight - ввод текущего веса"""
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

    conn.close()

    await message.answer("Пожалуйста, введи свой текущий вес в килограммах:")


@router.message(F.text.func(lambda x: x.replace(".", "", 1).isdigit()))
async def process_weight_input(message: Message):
    """Обработка ввода веса"""
    try:
        weight = float(message.text)

        if weight < 30 or weight > 300:
            await message.answer("Вес должен быть от 30 до 300 кг. Введи снова:")
            return

        user_id = message.from_user.id

        # Сохраняем вес в базу
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO weight_records (user_id, weight, record_date)
            VALUES (?, ?, ?)
        """, (user_id, weight, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # Получаем данные пользователя для расчета прогресса
        cursor.execute("""
            SELECT start_weight, target_weight, height
            FROM users
            WHERE id = ?
        """, (user_id,))

        user_data = cursor.fetchone()

        if user_data:
            start_weight, target_weight, height = user_data

            # Рассчитываем прогресс
            progress_score = calculate_final_score(start_weight, weight, height, target_weight, user_id=user_id, db_path=DATABASE_PATH)

            # Сохраняем прогресс в базу
            cursor.execute("""
                INSERT INTO progress (user_id, progress_points, calculation_date)
                VALUES (?, ?, ?)
            """, (user_id, progress_score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        # Рассчитываем изменение веса
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT start_weight
            FROM users
            WHERE id = ?
        """, (user_id,))

        start_weight_result = cursor.fetchone()
        conn.close()

        if start_weight_result:
            start_weight = start_weight_result[0]
            weight_change = start_weight - weight

            if weight_change > 0:
                await message.answer(f"✅ Вес сохранен: {weight} кг\nТы сбросил(а) {abs(weight_change):.2f} кг")
            elif weight_change < 0:
                await message.answer(f"⚠️ Вес сохранен: {weight} кг\nТы набрал(а) {abs(weight_change):.2f} кг")
            else:
                await message.answer(f"✅ Вес сохранен: {weight} кг\nВес не изменился")
        else:
            await message.answer(f"✅ Вес сохранен: {weight} кг")

    except ValueError:
        # Если текст не является числом, не обрабатываем как вес
        pass


@router.message(Command("activity"))
async def cmd_activity(message: Message):
    """Обработка команды /activity - ввод активности"""
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

    # Получаем доступные типы активности
    cursor.execute("SELECT id, name, description FROM activity_types")
    activities = cursor.fetchall()

    if not activities:
        await message.answer("На данный момент нет доступных типов активности.")
        conn.close()
        return

    # Создаем клавиатуру с типами активности
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for activity_id, name, description in activities:
        keyboard.add(KeyboardButton(text=description))

    await message.answer("Выбери тип активности:", reply_markup=keyboard)

    conn.close()


# Состояния для FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class ActivityStates(StatesGroup):
    waiting_for_activity_type = State()
    waiting_for_value = State()


@router.message(ActivityStates.waiting_for_activity_type)
async def process_activity_type_selection(message: Message, state: FSMContext):
    """Обработка выбора типа активности"""
    activity_description = message.text

    # Получаем ID типа активности по описанию
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, unit FROM activity_types WHERE description = ?", (activity_description,))
    result = cursor.fetchone()

    if not result:
        await message.answer("Пожалуйста, выбери тип активности из предложенных вариантов.")
        conn.close()
        return

    activity_id, activity_name, unit = result

    # Сохраняем выбранный тип активности во временные данные
    await state.update_data(activity_type_id=activity_id, activity_name=activity_name, unit=unit)

    conn.close()

    # Запрашиваем значение активности
    await message.answer(f"Теперь введи значение активности '{activity_description}' в {unit}:")

    # Переходим к следующему состоянию
    await state.set_state(ActivityStates.waiting_for_value)


@router.message(ActivityStates.waiting_for_value)
async def process_activity_value(message: Message, state: FSMContext):
    """Обработка ввода значения активности"""
    try:
        value = float(message.text)
        user_id = message.from_user.id

        # Получаем сохраненные данные
        data = await state.get_data()
        activity_type_id = data["activity_type_id"]
        activity_name = data["activity_name"]
        unit = data["unit"]

        # Проверяем диапазон значений в зависимости от типа активности
        if activity_name == "walking" and (value < 0 or value > 50000):
            await message.answer("Количество шагов должно быть от 0 до 50000. Введи снова:")
            return
        if activity_name == "running" and (value < 0 or value > 300):  # до 5 часов
            await message.answer("Время бега должно быть от 0 до 300 минут. Введи снова:")
            return
        if activity_name == "cycling" and (value < 0 or value > 200):  # до 200 км
            await message.answer("Расстояние на велосипеде должно быть от 0 до 200 км. Введи снова:")
            return
        if activity_name == "cardio" and (value < 0 or value > 2000):  # до 2000 ккал
            await message.answer("Количество калорий должно быть от 0 до 2000. Введи снова:")
            return

        # Сохраняем активность в базу
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Получаем коэффициент для расчета калорий
        cursor.execute("SELECT calories_per_unit FROM activity_types WHERE id = ?", (activity_type_id,))
        calories_per_unit_result = cursor.fetchone()

        calories = None
        if calories_per_unit_result and calories_per_unit_result[0]:
            calories = value * calories_per_unit_result[0]

        cursor.execute("""
            INSERT INTO activity_records (user_id, activity_type_id, value, calories, record_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, activity_type_id, value, calories, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        # Отправляем подтверждение
        if calories:
            await message.answer(f"✅ Активность '{activity_name}' сохранена: {value} {unit}\nСожжено калорий: {calories:.2f}")
        else:
            await message.answer(f"✅ Активность '{activity_name}' сохранена: {value} {unit}")

        # Сбрасываем состояние
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введи корректное числовое значение.")


@router.message(F.text.contains("Ходьба") | F.text.contains("Бег") | F.text.contains("Велосипед") | F.text.contains("Кардио"))
async def quick_activity_selection(message: Message, state: FSMContext):
    """Быстрый выбор активности через клавиатуру"""
    activity_text = message.text

    # Определяем тип активности по тексту
    activity_mapping = {
        "Ходьба (шаги)": "walking",
        "Бег (время в минутах)": "running",
        "Велосипед (расстояние в км)": "cycling",
        "Кардио (калории)": "cardio",
    }

    if activity_text in activity_mapping:
        # Получаем ID типа активности
        activity_name = activity_mapping[activity_text]

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, unit FROM activity_types WHERE name = ?", (activity_name,))
        result = cursor.fetchone()

        if result:
            activity_id, unit = result

            # Сохраняем выбранный тип активности во временные данные
            await state.update_data(activity_type_id=activity_id, activity_name=activity_name, unit=unit)

            conn.close()

            # Запрашиваем значение активности
            await message.answer(f"Теперь введи значение активности '{activity_text}' в {unit}:")

            # Переходим к следующему состоянию
            await state.set_state(ActivityStates.waiting_for_value)
        else:
            await message.answer("Произошла ошибка при выборе типа активности.")
    else:
        # Если это не выбор активности, возможно это значение - игнорируем
        pass
