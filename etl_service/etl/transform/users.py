"""Трансформер для данных пользователей."""

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from etl.transform.base import BaseTransformer
from etl.transform.calculations import calculate_current_point, calculate_target_point
from models import SourceUser, SourceWeightRecord, TransformedUserData

if TYPE_CHECKING:
    from decimal import Decimal

logger = logging.getLogger(__name__)


class UserTransformer(
    BaseTransformer[tuple[SourceUser, list[SourceWeightRecord]], TransformedUserData],
):
    """Трансформация данных пользователей для витрины."""

    async def transform(
        self,
        data: list[tuple[SourceUser, list[SourceWeightRecord]]],
    ) -> list[TransformedUserData]:
        """Трансформация данных пользователей.

        На вход получает кортежи: (пользователь, список записей о весе)
        На выход отдаёт трансформированные данные для витрины.
        """
        result = []

        for source_user, weight_records in data:
            # Пропускаем пользователей без необходимых данных
            if source_user.start_weight is None or source_user.height is None:
                logger.warning(
                    "Пропущен пользователь %s: отсутствуют start_weight или height",
                    source_user.id,
                )
                continue

            # Получаем текущий вес (последняя запись)
            current_weight = self._get_current_weight(weight_records)

            # Если нет записей о весе, пропускаем
            if current_weight is None:
                logger.warning(
                    "Пропущен пользователь %s: нет записей о весе",
                    source_user.id,
                )
                continue

            # Используем target_weight или fallback на start_weight
            target_weight = source_user.target_weight
            if target_weight is None:
                target_weight = source_user.start_weight
                logger.warning(
                    "Пользователь %s: target_weight не задан, используем start_weight",
                    source_user.id,
                )

            # Расчёт точек прогресса
            try:
                target_point = calculate_target_point(
                    start_weight=source_user.start_weight,
                    target_weight=target_weight,
                    height=source_user.height,
                )

                current_point = calculate_current_point(
                    start_weight=source_user.start_weight,
                    current_weight=current_weight,
                    height=source_user.height,
                )

                lost_weight = source_user.start_weight - current_weight

                result.append(
                    TransformedUserData(
                        id=source_user.id,
                        nickname=source_user.username,
                        current_point=current_point,
                        target_point=target_point,
                        lost_weight=round(lost_weight, 4),
                    ),
                )
            except (ValueError, ZeroDivisionError):
                logger.exception(
                    "Ошибка расчёта прогресса для пользователя %s",
                    source_user.id,
                )
                continue

        logger.info("Трансформировано %s пользователей", len(result))
        return result

    def _get_current_weight(
        self,
        weight_records: list[SourceWeightRecord],
    ) -> Decimal | None:
        """Получение последнего веса по дате."""
        if not weight_records:
            return None

        # Сортируем по дате и берём последнюю запись
        latest_record = max(weight_records, key=lambda r: r.record_date)
        return latest_record.weight


def merge_user_weight_data(
    users: list[SourceUser],
    weight_records: list[SourceWeightRecord],
) -> list[tuple[SourceUser, list[SourceWeightRecord]]]:
    """Объединение пользователей с их записями о весе.

    Возвращает список кортежей: (пользователь, список его записей о весе)
    """
    # Группируем записи по user_id
    weight_by_user: dict[int, list[SourceWeightRecord]] = defaultdict(list)

    for record in weight_records:
        weight_by_user[record.user_id].append(record)

    # Объединяем с пользователями
    return [(user, weight_by_user.get(user.id, [])) for user in users]
