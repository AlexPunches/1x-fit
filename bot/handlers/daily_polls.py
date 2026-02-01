# bot/handlers/daily_polls.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime
import sqlite3

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


@router.message(F.text.func(lambda x: x.replace('.', '', 1).isdigit()))
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
        """, (user_id, weight, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
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
            progress_score = calculate_final_score(start_weight, weight, height, target_weight)
            
            # Сохраняем прогресс в базу
            cursor.execute("""
                INSERT INTO progress (user_id, progress_points, calculation_date)
                VALUES (?, ?, ?)
            """, (user_id, progress_score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
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


@router.message(Command("steps"))
async def cmd_steps(message: Message):
    """Обработка команды /steps - ввод количества шагов"""
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
    
    await message.answer("Пожалуйста, введи количество шагов за сегодня:")


@router.message(F.text.func(lambda x: x.isdigit()))
async def process_steps_input(message: Message):
    """Обработка ввода количества шагов"""
    try:
        steps = int(message.text)
        
        if steps < 0 or steps > 50000:
            await message.answer("Количество шагов должно быть от 0 до 50000. Введи снова:")
            return
        
        user_id = message.from_user.id
        
        # Сохраняем шаги в базу
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO step_records (user_id, steps_count, record_date)
            VALUES (?, ?, ?)
        """, (user_id, steps, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        
        await message.answer(f"✅ Количество шагов сохранено: {steps}")
    
    except ValueError:
        # Если текст не является числом, не обрабатываем как шаги
        pass