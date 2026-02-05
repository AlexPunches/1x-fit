# bot/handlers/daily_polls.py

import logging
import sqlite3
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from database.models import DATABASE_PATH
from utils.calculations import calculate_final_score

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("weight"))
async def cmd_weight(message: Message) -> None:
    """Обработка команды /weight - ввод текущего веса."""
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


@router.message(F.text.func(lambda x: x.replace(".", "", 1).isdigit()), StateFilter(None))
async def process_weight_input(message: Message) -> None:
    """Обработка ввода веса."""
    logger.debug("Получено числовое сообщение: %s от пользователя %s", message.text, message.from_user.id)

    try:
        weight = float(message.text)
        logger.debug("Обнаружен вес: %s кг для пользователя %s", weight, message.from_user.id)

        # Используем константы вместо магических чисел
        min_weight = 30
        max_weight = 300

        if weight < min_weight or weight > max_weight:
            logger.debug("Вес %s кг вне допустимого диапазона для пользователя %s", weight, message.from_user.id)
            await message.answer(f"Вес должен быть от {min_weight} до {max_weight} кг. Введи снова:")
            return

        user_id = message.from_user.id

        # Сохраняем вес в базу
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO weight_records (user_id, weight, record_date)
            VALUES (?, ?, ?)
        """, (user_id, weight, datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S")))

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
            """, (user_id, progress_score, datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()
        logger.debug("Вес %s кг успешно сохранен для пользователя %s", weight, user_id)

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
                await message.answer(f"✅ Вес сохранен: {weight} кг\nТы сбросил {abs(weight_change):.2f} кг")
            elif weight_change < 0:
                await message.answer(f"⚠️ Вес сохранен: {weight} кг\nТы набрал {abs(weight_change):.2f} кг")
            else:
                await message.answer(f"✅ Вес сохранен: {weight} кг\nВес не изменился")
        else:
            await message.answer(f"✅ Вес сохранен: {weight} кг")

    except ValueError:
        # Если текст не является числом, не обрабатываем как вес
        logger.debug("Сообщение '%s' не является числом, пропускаем обработку", message.text)


@router.message(Command("activity"))
async def cmd_activity(message: Message) -> None:
    """Обработка команды /activity - ввод активности."""
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
    keyboard = []
    row = []
    for _activity_id, _name, description in activities:
        row.append(KeyboardButton(text=description))
        buttons_per_row = 2  # Добавляем по 2 кнопки в ряд для лучшего отображения
        if len(row) == buttons_per_row:
            keyboard.append(row)
            row = []
    if row:  # Добавляем оставшиеся кнопки
        keyboard.append(row)

    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer("Выбери тип активности:", reply_markup=reply_markup)

    conn.close()


# Состояния для FSM


class ActivityStates(StatesGroup):
    waiting_for_activity_type = State()
    waiting_for_value = State()


@router.message(ActivityStates.waiting_for_activity_type)
async def process_activity_type_selection(message: Message, state: FSMContext) -> None:
    """Обработка выбора типа активности."""
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
async def process_activity_value(message: Message, state: FSMContext) -> None:
    """Обработка ввода значения активности."""
    logger.debug("Получено значение активности: %s от пользователя %s", message.text, message.from_user.id)

    try:
        value = float(message.text)
        user_id = message.from_user.id

        # Получаем сохраненные данные
        data = await state.get_data()
        activity_type_id = data["activity_type_id"]
        activity_name = data["activity_name"]
        unit = data["unit"]

        logger.debug("Обрабатываем активность для пользователя %s: %s, значение %s %s",
                    user_id, activity_name, value, unit)

        # Проверяем диапазон значений в зависимости от типа активности
        max_steps = 50000
        max_running_minutes = 300  # до 5 часов
        max_cycling_km = 200  # до 200 км
        max_cardio_kcal = 2000  # до 2000 ккал

        if activity_name == "walking" and (value < 0 or value > max_steps):
            logger.debug("Значение %s вне диапазона для ходьбы", value)
            await message.answer(f"Количество шагов должно быть от 0 до {max_steps}. Введи снова:")
            return
        if activity_name == "running" and (value < 0 or value > max_running_minutes):  # до 5 часов
            logger.debug("Значение %s вне диапазона для бега", value)
            await message.answer(f"Время бега должно быть от 0 до {max_running_minutes} минут. Введи снова:")
            return
        if activity_name == "cycling" and (value < 0 or value > max_cycling_km):  # до 200 км
            logger.debug("Значение %s вне диапазона для велосипеда", value)
            await message.answer(f"Расстояние на велосипеде должно быть от 0 до {max_cycling_km} км. Введи снова:")
            return
        if activity_name == "cardio" and (value < 0 or value > max_cardio_kcal):  # до 2000 ккал
            logger.debug("Значение %s вне диапазона для кардио", value)
            await message.answer(f"Количество калорий должно быть от 0 до {max_cardio_kcal}. Введи снова:")
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

        logger.debug("Сохраняем активность в базу: пользователь %s, тип %s, значение %s, калории %s",
                    user_id, activity_type_id, value, calories)

        cursor.execute("""
            INSERT INTO activity_records (user_id, activity_type_id, value, calories, record_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, activity_type_id, value, calories, datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        # Отправляем подтверждение
        if calories:
            await message.answer(f"✅ Активность '{activity_name}' сохранена: {value} {unit}\nСожжено калорий: {calories:.2f}")
        else:
            await message.answer(f"✅ Активность '{activity_name}' сохранена: {value} {unit}")

        logger.debug("Активность успешно сохранена для пользователя %s", user_id)

        # Сбрасываем состояние
        await state.clear()

    except ValueError:
        logger.debug("Значение '%s' не является числом для активности", message.text)
        await message.answer("Пожалуйста, введи корректное числовое значение.")


@router.message(F.text.contains("Ходьба") | F.text.contains("Бег") | F.text.contains("Велосипед") | F.text.contains("Кардио"))
async def quick_activity_selection(message: Message, state: FSMContext) -> None:
    """Быстрый выбор активности через клавиатуру."""
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
