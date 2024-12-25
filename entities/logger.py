from dataclasses import dataclass, field
from datetime import datetime
from entities.meter import UnitType


@dataclass
class LogEntry:
    """Запись в логере"""

    ip: str
    timestamp: datetime
    value: float


@dataclass
class Logger:
    """Класс для хранения входящих данных"""

    entries_v: list[LogEntry] = field(default_factory=list)
    entries_a: list[LogEntry] = field(default_factory=list)

    def add_entry(self, ip: str, timestamp: datetime, value: float, unit: UnitType):
        """Добавление новой записи в лог"""
        if unit == UnitType.AMPS.value:
            entry = LogEntry(ip=ip, timestamp=timestamp, value=value)
            self.entries_a.append(entry)
        elif unit == UnitType.VOLTS.value:
            entry = LogEntry(ip=ip, timestamp=timestamp, value=value)
            self.entries_v.append(entry)
        print(f"Запись добавлена: {entry}")
