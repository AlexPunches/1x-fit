# bot/handlers/registration.py

import sqlite3

import utils.messages as msg

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
        msg.REGISTRATION_WELCOME_SS.format(USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH),
    )
    await state.set_state(RegistrationStates.waiting_for_username)


@router.message(RegistrationStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext) -> None:
    """Обработка ввода ника."""
    username = message.text.strip() if message.text is not None else ""

    if len(username) < USERNAME_MIN_LENGTH or len(username) > USERNAME_MAX_LENGTH:
        await message.answer(msg.INVALID_NICKNAME_LENGTH_SS.format(USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH))
        return

    await state.update_data(username=username)
    await message.answer(
        msg.GENDER_REQUEST_SIMPLE,
    )
    await state.set_state(RegistrationStates.waiting_for_gender)


@router.message(RegistrationStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext) -> None:
    """Обработка ввода пола."""
    gender = message.text.strip().upper() if message.text is not None else ""

    if gender not in ["М", "Ж", "M", "F"]:
        await message.answer(msg.INVALID_GENDER_SS.format("М", "Ж"))
        return

    # Преобразуем в формат базы данных
    gender_db = "M" if gender in ["М", "M"] else "F"

    await state.update_data(gender=gender_db)
    await message.answer(msg.AGE_REQUEST)
    await state.set_state(RegistrationStates.waiting_for_age)


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext) -> None:
    """Обработка ввода возраста."""
    try:
        age = int(message.text.strip()) if message.text is not None else 0

        if age < AGE_MIN_VALUE or age > AGE_MAX_VALUE:
            await message.answer(msg.INVALID_AGE_SS.format(AGE_MIN_VALUE, AGE_MAX_VALUE))
            return

        await state.update_data(age=age)
        await message.answer(msg.HEIGHT_REQUEST)
        await state.set_state(RegistrationStates.waiting_for_height)

    except ValueError:
        await message.answer(msg.INVALID_AGE_INPUT)


@router.message(RegistrationStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext) -> None:
    """Обработка ввода роста."""
    try:
        height = float(message.text.strip()) if message.text is not None else 0.0

        if height < HEIGHT_MIN_VALUE or height > HEIGHT_MAX_VALUE:
            await message.answer(msg.INVALID_HEIGHT_SS.format(HEIGHT_MIN_VALUE, HEIGHT_MAX_VALUE))
            return

        await state.update_data(height=height)
        await message.answer(msg.START_WEIGHT_REQUEST)
        await state.set_state(RegistrationStates.waiting_for_start_weight)

    except ValueError:
        await message.answer(msg.INVALID_HEIGHT_INPUT)


@router.message(RegistrationStates.waiting_for_start_weight)
async def process_start_weight(message: Message, state: FSMContext) -> None:
    """Обработка ввода стартового веса."""
    try:
        start_weight = float(message.text.strip()) if message.text is not None else 0.0

        if start_weight < WEIGHT_MIN_VALUE or start_weight > WEIGHT_MAX_VALUE:
            await message.answer(msg.INVALID_WEIGHT_SS.format(WEIGHT_MIN_VALUE, WEIGHT_MAX_VALUE))
            return

        await state.update_data(start_weight=start_weight)
        await message.answer(msg.TARGET_WEIGHT_REQUEST_EXTRA)
        await state.set_state(RegistrationStates.waiting_for_target_weight)

    except ValueError:
        await message.answer(msg.INVALID_START_WEIGHT_INPUT)


@router.message(RegistrationStates.waiting_for_target_weight)
async def process_target_weight(message: Message, state: FSMContext) -> None:
    """Обработка ввода целевого веса."""
    try:
        target_weight = float(message.text.strip()) if message.text is not None else 0.0
        data = await state.get_data()
        start_weight = data["start_weight"]

        if target_weight < WEIGHT_MIN_VALUE or target_weight > WEIGHT_MAX_VALUE:
            await message.answer(msg.INVALID_WEIGHT_SS.format(WEIGHT_MIN_VALUE, WEIGHT_MAX_VALUE))
            return

        if target_weight >= start_weight:
            await message.answer(msg.INVALID_TARGET_WEIGHT_S)
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
            msg.REGISTRATION_COMPLETED_SSSSSS.format(
                username,
                "Мужской" if gender == "M" else "Женский",
                age,
                height,
                start_weight,
                target_weight,
            ),
        )

        await state.clear()

    except ValueError:
        await message.answer(msg.INVALID_TARGET_WEIGHT_INPUT)
