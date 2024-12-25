from dataclasses import dataclass, field
import threading
from typing import Optional
from time import sleep
from datetime import datetime, timedelta
from entities.logger import Logger
from entities.meter import StoredMeter
from entities.meter_storage import MeterStorage


@dataclass
class Storage:
    """Класс для хранения измерителей и логирования данных"""

    log_name: str
    meter_storage: MeterStorage
    logger: Logger = field(default_factory=Logger)
    power_data: list[tuple[datetime, float]] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)
    data_updated: bool = field(default=False)

    def validate_and_store(
        self, ip: str, timestamp: datetime, value: float, unit: str
    ) -> bool:
        """
        Валидирует входящие данные и сохраняет их в лог, если они корректны.

        Args:
            ip (str): IP-адрес измерителя.
            timestamp (datetime): Временная метка измерения.
            value (float): Значение измерения.
            unit (str): Единица измерения ("A" или "B").

        Returns:
            bool: True, если данные валидны и сохранены, иначе False.
        """
        meter: Optional[StoredMeter] = self.meter_storage.get(ip)
        if not meter:
            print(f"Неизвестный IP-адрес: {ip}")
            return False

        if not meter.is_unit_correct(unit):
            print(
                f"Неверная единица измерения для IP {ip}: ожидается {meter.unit}, получено {unit}"
            )
            return False

        if not meter.check_value_in_range(value):
            print(
                f"Значение {value} вне диапазона для IP {ip} ({meter.range_start} - {meter.range_stop} {unit})"
            )
            return False
        with self.lock:
            self.logger.add_entry(ip, timestamp, value, unit)
            self.data_updated = True
        return True

    def compute_power(self, max_time_diff: float = 0.5):
        """
        Вычисляет мощность на основе последних измерений напряжения и тока.

        Args:
            max_time_diff (float): Максимальная допустимая разница во времени в секундах.
        """
        with self.lock:
            if not self.data_updated:
                # Нет новых данных для вычисления
                return
            voltage_entries = self.logger.entries_v
            current_entries = self.logger.entries_a

            if not voltage_entries or not current_entries:
                return

            latest_voltage = voltage_entries[-1]

            closest_current = None
            min_diff = timedelta(seconds=max_time_diff + 1)
            for current in reversed(current_entries):
                diff = abs(latest_voltage.timestamp - current.timestamp)
                if diff <= timedelta(seconds=max_time_diff) and diff < min_diff:
                    closest_current = current
                    min_diff = diff

            if closest_current:
                power = latest_voltage.value * closest_current.value
                self.power_data.append((latest_voltage.timestamp, power))
                print(f"Мощность вычислена: {power} Вт в {latest_voltage.timestamp}")
                with open(self.log_name, "a", encoding="utf-8") as f:
                    f.write(f"{power}|{latest_voltage.timestamp}\n")
                if len(self.power_data) > 1000:
                    self.power_data = self.power_data[-1000:]
            self.data_updated = False


def power_computation_thread(storage: Storage, interval: float = 1.0):
    """
    Периодически вычисляет мощность и обновляет power_data в Storage.

    Args:
        storage (Storage): Объект хранения и логирования данных.
        interval (float): Интервал вычислений в секундах.
    """
    while True:
        storage.compute_power()
        sleep(interval)
