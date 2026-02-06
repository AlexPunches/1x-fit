# bot/handlers/registration.py

import sqlite3

# Константы для валидации данных
USERNAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 30
AGE_MIN_VALUE = 18
AGE_MAX_VALUE = 100
HEIGHT_MIN_VALUE = 100
HEIGHT_MAX_VALUE = 250
WEIGHT_MIN_VALUE = 30
WEIGHT_MAX_VALUE = 300

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from database.models import DATABASE_PATH

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_start_weight = State()
    waiting_for_target_weight = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обработка команды /start."""
    await message.answer(
        "Привет! Давай начнем регистрацию в соревновании по снижению веса.\n\n"
        "Сначала введи свой ник:",
    )
    await state.set_state(RegistrationStates.waiting_for_username)


@router.message(RegistrationStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext) -> None:
    """Обработка ввода ника."""
    username = message.text.strip() if message.text is not None else ""

    if len(username) < USERNAME_MIN_LENGTH or len(username) > USERNAME_MAX_LENGTH:
        await message.answer(f"Ник должен быть длиной от {USERNAME_MIN_LENGTH} до {USERNAME_MAX_LENGTH} символов. Введи снова:")
        return

    await state.update_data(username=username)
    await message.answer(
        "Отлично! Теперь укажи свой пол (М/Ж):",
    )
    await state.set_state(RegistrationStates.waiting_for_gender)


@router.message(RegistrationStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext) -> None:
    """Обработка ввода пола."""
    gender = message.text.strip().upper() if message.text is not None else ""

    if gender not in ["М", "Ж", "M", "F"]:
        await message.answer("Пожалуйста, укажи пол: М (мужской) или Ж (женский):")
        return

    # Преобразуем в формат базы данных
    gender_db = "M" if gender in ["М", "M"] else "F"

    await state.update_data(gender=gender_db)
    await message.answer("Теперь введи свой возраст:")
    await state.set_state(RegistrationStates.waiting_for_age)


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext) -> None:
    """Обработка ввода возраста."""
    try:
        age = int(message.text.strip()) if message.text is not None else 0

        if age < AGE_MIN_VALUE or age > AGE_MAX_VALUE:
            await message.answer(f"Возраст должен быть от {AGE_MIN_VALUE} до {AGE_MAX_VALUE} лет. Введи снова:")
            return

        await state.update_data(age=age)
        await message.answer("Теперь укажи свой рост в сантиметрах:")
        await state.set_state(RegistrationStates.waiting_for_height)

    except ValueError:
        await message.answer("Пожалуйста, введи корректный возраст:")


@router.message(RegistrationStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext) -> None:
    """Обработка ввода роста."""
    try:
        height = float(message.text.strip()) if message.text is not None else 0.0

        if height < HEIGHT_MIN_VALUE or height > HEIGHT_MAX_VALUE:
            await message.answer(f"Рост должен быть от {HEIGHT_MIN_VALUE} до {HEIGHT_MAX_VALUE} см. Введи снова:")
            return

        await state.update_data(height=height)
        await message.answer("Теперь введи свой стартовый вес в килограммах:")
        await state.set_state(RegistrationStates.waiting_for_start_weight)

    except ValueError:
        await message.answer("Пожалуйста, введи корректный рост:")


@router.message(RegistrationStates.waiting_for_start_weight)
async def process_start_weight(message: Message, state: FSMContext) -> None:
    """Обработка ввода стартового веса."""
    try:
        start_weight = float(message.text.strip()) if message.text is not None else 0.0

        if start_weight < WEIGHT_MIN_VALUE or start_weight > WEIGHT_MAX_VALUE:
            await message.answer(f"Вес должен быть от {WEIGHT_MIN_VALUE} до {WEIGHT_MAX_VALUE} кг. Введи снова:")
            return

        await state.update_data(start_weight=start_weight)
        await message.answer("Теперь введи свой целевой вес в килограммах:")
        await state.set_state(RegistrationStates.waiting_for_target_weight)

    except ValueError:
        await message.answer("Пожалуйста, введи корректный стартовый вес:")


@router.message(RegistrationStates.waiting_for_target_weight)
async def process_target_weight(message: Message, state: FSMContext) -> None:
    """Обработка ввода целевого веса."""
    try:
        target_weight = float(message.text.strip()) if message.text is not None else 0.0
        data = await state.get_data()
        start_weight = data["start_weight"]

        if target_weight < WEIGHT_MIN_VALUE or target_weight > WEIGHT_MAX_VALUE:
            await message.answer(f"Вес должен быть от {WEIGHT_MIN_VALUE} до {WEIGHT_MAX_VALUE} кг. Введи снова:")
            return

        if target_weight >= start_weight:
            await message.answer(
                f"Целевой вес ({target_weight} кг) должен быть меньше стартового веса ({start_weight} кг). Введи снова:",
            )
            return

        await state.update_data(target_weight=target_weight)

        # Сохраняем данные в базу
        user_data = await state.get_data()
        user_id = message.from_user.id if message.from_user and message.from_user.id is not None else 0
        username = user_data["username"]
        gender = user_data["gender"]
        age = user_data["age"]
        height = user_data["height"]
        start_weight = user_data["start_weight"]
        target_weight = user_data["target_weight"]

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO users
            (id, username, gender, age, height, start_weight, target_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, gender, age, height, start_weight, target_weight))

        conn.commit()
        conn.close()

        await message.answer(
            f"Регистрация завершена! Ты успешно зарегистрирован в соревновании.\n\n"
            f"Твой профиль:\n"
            f"- Ник: {username}\n"
            f"- Пол: {'Мужской' if gender == 'M' else 'Женский'}\n"
            f"- Возраст: {age} лет\n"
            f"- Рост: {height} см\n"
            f"- Стартовый вес: {start_weight} кг\n"
            f"- Целевой вес: {target_weight} кг\n\n"
            f"Теперь ты будешь получать ежедневные опросы о весе и количестве шагов.",
        )

        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введи корректный целевой вес:")
