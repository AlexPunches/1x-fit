def calculate_bmi(weight, height):
    """
    Рассчитывает ИМТ (индекс массы тела)
    :param weight: вес в кг
    :param height: рост в см
    :return: значение ИМТ
    """
    height_m = height / 100  # переводим рост в метры
    return weight / (height_m ** 2)


def get_weight_factor(initial_bmi):
    """
    Возвращает коэффициент, зависящий от начального ИМТ
    :param initial_bmi: начальный ИМТ
    :return: коэффициент для расчета прогресса
    """
    if initial_bmi < 25:  # нормальный вес
        return 1.0
    elif initial_bmi < 30:  # избыточный вес
        return 1.2
    elif initial_bmi < 35:  # ожирение 1 степени
        return 1.5
    elif initial_bmi < 40:  # ожирение 2 степени
        return 1.8
    else:  # ожирение 3 степени
        return 2.0


def calculate_progress_points(start_weight, current_weight, height, target_weight):
    """
    Рассчитывает прогресс в условных пунктах
    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :param height: рост
    :param target_weight: целевой вес
    :return: количество условных пунктов прогресса
    """
    initial_bmi = calculate_bmi(start_weight, height)
    current_bmi = calculate_bmi(current_weight, height)
    
    bmi_improvement = initial_bmi - current_bmi
    
    # Применяем коэффициент, зависящий от начального ИМТ
    weight_factor = get_weight_factor(initial_bmi)
    progress_score = bmi_improvement * weight_factor
    
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
    progress_points = weight_loss * points_for_kg
    
    return progress_points


def calculate_percentage_loss(start_weight, current_weight):
    """
    Рассчитывает процент снижения веса
    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :return: процент снижения
    """
    return (start_weight - current_weight) / start_weight * 100


def calculate_adjusted_percentage(start_weight, current_weight, height):
    """
    Рассчитывает процент снижения веса с коррекцией на ИМТ
    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :param height: рост
    :return: скорректированный процент снижения
    """
    percentage_loss = calculate_percentage_loss(start_weight, current_weight)
    initial_bmi = calculate_bmi(start_weight, height)
    
    # Определяем коэффициент коррекции
    if initial_bmi < 25:
        adjustment_factor = 1.0
    elif initial_bmi < 30:
        adjustment_factor = 1.1
    elif initial_bmi < 35:
        adjustment_factor = 1.3
    elif initial_bmi < 40:
        adjustment_factor = 1.6
    else:
        adjustment_factor = 2.0
    
    return percentage_loss * adjustment_factor


def calculate_final_score(start_weight, current_weight, height, target_weight):
    """
    Рассчитывает итоговый прогресс с использованием комбинированной формулы
    :param start_weight: начальный вес
    :param current_weight: текущий вес
    :param height: рост
    :param target_weight: целевой вес
    :return: итоговый прогресс
    """
    bmi_based_score = calculate_progress_points(start_weight, current_weight, height, target_weight)
    percentage_based_score = calculate_adjusted_percentage(start_weight, current_weight, height)
    
    # Комбинируем оба подхода
    final_score = (bmi_based_score * 0.6) + (percentage_based_score * 0.4)
    
    return final_score