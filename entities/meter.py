from dataclasses import dataclass
from typing import Literal
import enum


class UnitType(enum.Enum):
    AMPS = "А"  # Амперы
    VOLTS = "В"  # Вольты

    def __str__(self):
        return self.value


@dataclass
class StoredMeter:
    """Структура для хранения информации об измерителе"""

    range_start: float
    range_stop: float
    unit: UnitType

    def check_value_in_range(self, value: float) -> bool:
        """Проверка, находится ли значение в диапазоне"""
        return self.range_start <= value <= self.range_stop

    def is_unit_correct(self, unit: UnitType) -> bool:
        """Проверка корректности единицы измерения"""
        return self.unit == unit
