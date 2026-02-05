import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from database.models import DATABASE_PATH
from settings import settings


def create_individual_chart(user_id: int, user_data: dict) -> str | None:
    """Создает индивидуальный график прогресса для одного участника.

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

    # Получаем данные об активности
    cursor.execute("""
        SELECT ar.value, ar.record_date, at.name
        FROM activity_records ar
        JOIN activity_types at ON ar.activity_type_id = at.id
        WHERE ar.user_id = ?
        ORDER BY ar.record_date
    """, (user_id,))

    cursor.fetchall()  # Не используется
    conn.close()

    if not records:
        return None

    dates = [datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc) for record in records]
    weights = [record[0] for record in records]
    progress_points = [record[2] if record[2] is not None else 0 for record in records]

    # Создаем график
    _fig, ax1 = plt.subplots(figsize=(12, 8))

    # Основной график - вес
    ax1.plot(dates, weights, "o-", label="Вес", color="blue")
    ax1.set_xlabel("Дата")
    ax1.set_ylabel("Вес (кг)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    # Добавляем линии для старта и цели
    start_weight = user_data["start_weight"]
    target_weight = user_data["target_weight"]
    ax1.axhline(y=start_weight, color="red", linestyle="--", label=f"Старт: {start_weight}кг")
    ax1.axhline(y=target_weight, color="green", linestyle="--", label=f"Цель: {target_weight}кг")

    # Добавляем сетку
    ax1.grid(b=True, linestyle="--", alpha=0.6)

    # Создаем вторую ось для прогресса
    ax2 = ax1.twinx()
    ax2.plot(dates, progress_points, "s-", label="Прогресс", color="orange")
    ax2.set_ylabel("Прогресс (усл. ед.)", color="orange")
    ax2.tick_params(axis="y", labelcolor="orange")

    # Добавляем легенду
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # Настраиваем заголовок
    plt.title(f'Прогресс участника {user_data["username"]}')

    # Поворачиваем подписи дат для лучшего отображения
    plt.xticks(rotation=45)

    # Сохраняем график
    Path(settings.charts_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{settings.charts_dir}individual_{user_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return filename


def create_activity_chart(user_id: int) -> str | None:
    """Создает график активности для одного участника.

    :param user_id: ID пользователя
    :return: путь к файлу графика
    """
    # Получаем данные из базы
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получаем данные об активности за последние 30 дней
    thirty_days_ago = (datetime.now(datetime.timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT ar.value, ar.record_date, at.name, at.unit, ar.calories
        FROM activity_records ar
        JOIN activity_types at ON ar.activity_type_id = at.id
        WHERE ar.user_id = ? AND ar.record_date >= ?
        ORDER BY ar.record_date
    """, (user_id, thirty_days_ago))

    activity_records = cursor.fetchall()
    conn.close()

    if not activity_records:
        return None

    # Подготовка данных
    dates = [datetime.strptime(record[1].split()[0], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc) for record in activity_records]
    values = [record[0] for record in activity_records]
    activity_names = [record[2] for record in activity_records]
    calories = [record[4] if record[4] is not None else 0 for record in activity_records]

    # Группировка данных по датам
    unique_dates = sorted(set(dates))
    daily_values = {}
    daily_calories = {}

    for date, value, cal in zip(dates, values, calories, strict=True):
        if date not in daily_values:
            daily_values[date] = {}
            daily_calories[date] = 0

        # Получаем тип активности для этой записи
        idx = dates.index(date)
        activity_name = activity_names[idx]

        if activity_name not in daily_values[date]:
            daily_values[date][activity_name] = 0
        daily_values[date][activity_name] += value
        daily_calories[date] += cal

    # Подготовка данных для графика
    plot_dates = [date.strftime("%d.%m") for date in unique_dates]
    plot_calories = [daily_calories[date] for date in unique_dates]

    # Создаем график
    _fig, ax = plt.subplots(figsize=(12, 8))

    # График сожженных калорий
    ax.bar(plot_dates, plot_calories, label="Сожжено калорий", color="coral", alpha=0.7)
    ax.set_xlabel("Дата")
    ax.set_ylabel("Калории", color="coral")
    ax.tick_params(axis="y", labelcolor="coral")

    # Добавляем сетку
    ax.grid(b=True, linestyle="--", alpha=0.6)

    # Настраиваем заголовок
    plt.title(f"Активность участника (ID: {user_id}) за последние 30 дней")

    # Поворачиваем подписи дат для лучшего отображения
    plt.xticks(rotation=45)

    # Сохраняем график
    Path(settings.charts_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{settings.charts_dir}activity_{user_id}_{datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return filename


def create_comparison_chart() -> str | None:
    """Создает сравнительный график для всех участников.

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
    _fig, ax = plt.subplots(figsize=(12, 8))

    # Рисуем точки для текущего прогресса
    y_pos = np.arange(len(usernames))
    bars = ax.barh(y_pos, current_progress, align="center", color="skyblue", label="Текущий прогресс")

    # Добавляем линии для целей
    for i, target in enumerate(target_progress):
        ax.axvline(x=target, color="red", linestyle="--", alpha=0.5)
        ax.text(target, i, f"Цель: {target:.1f}", verticalalignment="center", fontsize=9)

    # Настройка осей
    ax.set_yticks(y_pos)
    ax.set_yticklabels(usernames)
    ax.set_xlabel("Прогресс (усл. ед.)")
    ax.set_title("Сравнительный прогресс участников")

    # Добавляем сетку
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    # Добавляем значения на бары
    for bar, progress in zip(bars, current_progress, strict=True):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f"{progress:.1f}",
                ha="left", va="center", fontweight="bold")

    # Сохраняем график
    Path(settings.charts_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{settings.charts_dir}comparison_{datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return filename


def create_total_activity_chart() -> str | None:
    """Создает сравнительный график активности всех участников.

    :return: путь к файлу графика
    """
    # Получаем данные из базы
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Получаем суммарные калории за последние 7 дней для каждого пользователя
    seven_days_ago = (datetime.now(datetime.timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT u.id, u.username, COALESCE(SUM(ar.calories), 0) as total_calories
        FROM users u
        LEFT JOIN activity_records ar ON u.id = ar.user_id AND ar.record_date >= ?
        WHERE ar.calories IS NOT NULL
        GROUP BY u.id
    """, (seven_days_ago,))

    users_data = cursor.fetchall()
    conn.close()

    if not users_data:
        return None

    # Подготовка данных для графика
    usernames = [user[1] for user in users_data]
    total_calories = [user[2] for user in users_data]

    # Создаем график
    _fig, ax = plt.subplots(figsize=(12, 8))

    # Рисуем столбцы для сожженных калорий
    y_pos = np.arange(len(usernames))
    bars = ax.barh(y_pos, total_calories, align="center", color="lightcoral", label="Сожжено калорий")

    # Настройка осей
    ax.set_yticks(y_pos)
    ax.set_yticklabels(usernames)
    ax.set_xlabel("Сожженные калории")
    ax.set_title("Сравнительная активность участников (за последние 7 дней)")

    # Добавляем сетку
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    # Добавляем значения на бары
    for bar, calories in zip(bars, total_calories, strict=True):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f"{calories:.0f}",
                ha="left", va="center", fontweight="bold")

    # Сохраняем график
    Path(settings.charts_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{settings.charts_dir}total_activity_{datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return filename
