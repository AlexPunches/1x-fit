"""Функции для расчета прогресса пользователя."""

from dataclasses import dataclass


def calculate_bmi(weight: float, height: float) -> float:
    """Рассчитывает ИМТ (индекс массы тела).

    :param weight: вес в кг
    :param height: рост в см
    :return: значение ИМТ
    """
    height_m = height / 100  # переводим рост в метры
    return weight / (height_m ** 2)


def get_weight_factor(initial_bmi: float) -> float:
    """Возвращает коэффициент, зависящий от начального ИМТ.

    :param initial_bmi: начальный ИМТ
    :return: коэффициент для расчета прогресса
    """
    # Константы для порогов ИМТ
    normal_bmi_threshold = 25
    overweight_bmi_threshold = 30
    obesity1_bmi_threshold = 35
    obesity2_bmi_threshold = 40

    if initial_bmi < normal_bmi_threshold:  # нормальный вес
        return 1.0
    if initial_bmi < overweight_bmi_threshold:  # избыточный вес
        return 1.2
    if initial_bmi < obesity1_bmi_threshold:  # ожирение 1 степени
        return 1.5
    if initial_bmi < obesity2_bmi_threshold:  # ожирение 2 степени
        return 1.8
    # ожирение 3 степени
    return 2.0


def calculate_progress_points(start_weight: float, current_weight: float, height: float, target_weight: float) -> float:
    """Рассчитывает прогресс в условных пунктов.

    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :param height: рост
    :param target_weight: целевой вес
    :return: количество условных пунктов прогресса
    """
    initial_bmi = calculate_bmi(start_weight, height)
    current_bmi = calculate_bmi(current_weight, height)

    # Применяем коэффициент, зависящий от начального ИМТ
    _weight_factor = get_weight_factor(initial_bmi)

    # Рассчитываем адаптивный фактор для шкалы прогресса
    current_bmi_diff = abs(current_bmi - calculate_bmi(target_weight, height))
    initial_bmi_diff = abs(initial_bmi - calculate_bmi(target_weight, height))

    adaptive_factor = max(0.5, 1.0 - (current_bmi_diff / initial_bmi_diff if initial_bmi_diff != 0 else 1.0))

    # Определяем базовые очки за кг
    base_points_for_kg = 1.0

    # Рассчитываем очки за 1 кг с учетом адаптивного фактора
    points_for_kg = base_points_for_kg * adaptive_factor

    # Рассчитываем итоговый прогресс
    weight_loss = start_weight - current_weight
    return weight_loss * points_for_kg


def calculate_percentage_loss(start_weight: float, current_weight: float) -> float:
    """Рассчитывает процент снижения веса.

    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :return: процент снижения
    """
    return (start_weight - current_weight) / start_weight * 100


def calculate_adjusted_percentage(start_weight: float, current_weight: float, height: float) -> float:
    """Рассчитывает процент снижения веса с коррекцией на ИМТ.

    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :param height: рост
    :return: скорректированный процент снижения
    """
    percentage_loss = calculate_percentage_loss(start_weight, current_weight)
    initial_bmi = calculate_bmi(start_weight, height)

    # Определяем коэффициент коррекции
    normal_bmi_threshold = 25
    overweight_bmi_threshold = 30
    obesity1_bmi_threshold = 35
    obesity2_bmi_threshold = 40

    if initial_bmi < normal_bmi_threshold:
        adjustment_factor = 1.0
    elif initial_bmi < overweight_bmi_threshold:
        adjustment_factor = 1.1
    elif initial_bmi < obesity1_bmi_threshold:
        adjustment_factor = 1.3
    elif initial_bmi < obesity2_bmi_threshold:
        adjustment_factor = 1.6
    else:
        adjustment_factor = 2.0

    return percentage_loss * adjustment_factor


@dataclass
class ScoreCalculationParams:
    start_weight: float
    current_weight: float
    height: float
    target_weight: float
    user_id: int | None = None
    db_path: str | None = None


def calculate_target_point(start_weight: float, height: float, target_weight: float) -> float:
    """Рассчитывает целевой прогресс (максимально возможный).

    :param start_weight: начальный вес
    :param height: рост
    :param target_weight: целевой вес
    :return: целевое количество условных пунктов прогресса
    """
    return calculate_progress_points(start_weight, target_weight, height, target_weight)


def calculate_current_point(start_weight: float, current_weight: float, height: float, target_weight: float) -> float:
    """Рассчитывает текущий прогресс.

    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :param height: рост
    :param target_weight: целевой вес
    :return: текущее количество условных пунктов прогресса
    """
    return calculate_progress_points(start_weight, current_weight, height, target_weight)
