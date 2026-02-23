"""Формулы для расчёта прогресса пользователей."""

import math
from decimal import Decimal


def calculate_bmi(weight: Decimal, height: Decimal) -> Decimal:
    """Расчёт индекса массы тела (ИМТ)."""
    height_positive_error = ValueError("Рост должен быть положительным числом")
    if height <= 0:
        raise height_positive_error

    height_m = height / Decimal(100)  # Конвертируем см в метры
    bmi = weight / (height_m * height_m)
    return round(bmi, 4)


def calculate_progress_score(start_bmi: Decimal, current_bmi: Decimal) -> Decimal:
    """Расчёт прогресса по формуле.

    progress_score = (start_bmi - current_bmi) × max(e^((30 - current_bmi)/7), 0.5)

    Эта формула учитывает:
    - Разницу между начальным и текущим ИМТ
    - Экспоненциальный множитель, который даёт больший вес прогрессу
      при более высоком текущем ИМТ
    - Минимальный множитель 0.5 для предотвращения отрицательных значений
    """
    bmi_diff = start_bmi - current_bmi

    # Экспоненциальный множитель
    exponent = (Decimal(30) - current_bmi) / Decimal(7)
    exp_multiplier = Decimal(str(math.exp(float(exponent))))

    # Берём максимум из экспоненциального множителя и 0.5
    multiplier = max(exp_multiplier, Decimal("0.5"))

    progress_score = bmi_diff * multiplier
    return round(progress_score, 4)


def calculate_target_point(
    start_weight: Decimal,
    target_weight: Decimal,
    height: Decimal,
) -> Decimal:
    """Расчёт целевого прогресса (target_point)."""
    start_bmi = calculate_bmi(start_weight, height)
    target_bmi = calculate_bmi(target_weight, height)

    return calculate_progress_score(start_bmi, target_bmi)


def calculate_current_point(
    start_weight: Decimal,
    current_weight: Decimal,
    height: Decimal,
) -> Decimal:
    """Расчёт текущего прогресса (current_point)."""
    start_bmi = calculate_bmi(start_weight, height)
    current_bmi = calculate_bmi(current_weight, height)

    return calculate_progress_score(start_bmi, current_bmi)
