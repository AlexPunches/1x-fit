import matplotlib.pyplot as plt
from datetime import datetime
import os
from config import CHARTS_DIR
from database.models import DATABASE_PATH
import sqlite3
import numpy as np


def create_individual_chart(user_id, user_data):
    """
    Создает индивидуальный график прогресса для одного участника
    :param user_id: ID пользователя
    :param user_data: данные пользователя
    :return: путь к файлу графика
    """
    # Получаем данные из базы
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT wr.weight, wr.record_date, p.progress_points
        FROM weight_records wr
        LEFT JOIN progress p ON wr.user_id = p.user_id AND wr.record_date = p.calculation_date
        WHERE wr.user_id = ?
        ORDER BY wr.record_date
    """, (user_id,))
    
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        return None
    
    dates = [datetime.strptime(record[1], '%Y-%m-%d %H:%M:%S') for record in records]
    weights = [record[0] for record in records]
    progress_points = [record[2] if record[2] is not None else 0 for record in records]
    
    # Создаем график
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Основной график - прогресс в условных единицах
    ax1.plot(progress_points, weights, 'o-', label='Вес', color='blue')
    ax1.set_xlabel('Прогресс (усл. ед.)')
    ax1.set_ylabel('Вес (кг)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Добавляем линии для старта и цели
    start_weight = user_data['start_weight']
    target_weight = user_data['target_weight']
    ax1.axhline(y=start_weight, color='red', linestyle='--', label=f'Старт: {start_weight}кг')
    ax1.axhline(y=target_weight, color='green', linestyle='--', label=f'Цель: {target_weight}кг')
    
    # Добавляем сетку
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Добавляем легенду
    fig.legend(loc='upper left', bbox_to_anchor=(0.15, 0.85))
    
    # Настраиваем заголовок
    plt.title(f'Прогресс участника {user_data["username"]}')
    
    # Сохраняем график
    os.makedirs(CHARTS_DIR, exist_ok=True)
    filename = f"{CHARTS_DIR}individual_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    
    return filename


def create_comparison_chart():
    """
    Создает сравнительный график для всех участников
    :return: путь к файлу графика
    """
    # Получаем данные из базы
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT u.id, u.username, u.start_weight, u.target_weight, 
               MAX(p.progress_points) as current_progress
        FROM users u
        LEFT JOIN progress p ON u.id = p.user_id
        GROUP BY u.id
    """)
    
    users_data = cursor.fetchall()
    conn.close()
    
    if not users_data:
        return None
    
    # Подготовка данных для графика
    usernames = [user[1] for user in users_data]
    current_progress = [user[4] if user[4] is not None else 0 for user in users_data]
    target_progress = []  # Здесь будет индивидуальная цель для каждого участника
    
    # Для простоты примера, пусть целевой прогресс будет равен разнице между начальным и целевым весом
    # В реальности это должно быть рассчитано по формуле
    for user in users_data:
        start_weight = user[2]
        target_weight = user[3]
        # Рассчитываем условную цель для каждого участника
        # В реальности это должно быть рассчитано по формуле прогресса
        target_progress.append(abs(start_weight - target_weight) * 2)  # Умножаем на 2 для примера
    
    # Создаем график
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Рисуем точки для текущего прогресса
    y_pos = np.arange(len(usernames))
    bars = ax.barh(y_pos, current_progress, align='center', color='skyblue', label='Текущий прогресс')
    
    # Добавляем линии для целей
    for i, target in enumerate(target_progress):
        ax.axvline(x=target, color='red', linestyle='--', alpha=0.5)
        ax.text(target, i, f'Цель: {target:.1f}', verticalalignment='center', fontsize=9)
    
    # Настройка осей
    ax.set_yticks(y_pos)
    ax.set_yticklabels(usernames)
    ax.set_xlabel('Прогресс (усл. ед.)')
    ax.set_title('Сравнительный прогресс участников')
    
    # Добавляем сетку
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    
    # Добавляем значения на бары
    for bar, progress in zip(bars, current_progress):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f'{progress:.1f}', 
                ha='left', va='center', fontweight='bold')
    
    # Сохраняем график
    os.makedirs(CHARTS_DIR, exist_ok=True)
    filename = f"{CHARTS_DIR}comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    
    return filename