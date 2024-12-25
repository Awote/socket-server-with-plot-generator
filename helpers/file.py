import csv
from entities.meter import StoredMeter
from entities.meter_storage import MeterStorage


def parse_file(file_dir: str) -> MeterStorage:
    """
    Парсит файл с сопоставлением IP-адресов и характеристик измерителей.

    Args:
        file_dir (str): Путь к файлу.

    Returns:
        MeterStorage: Словарь с IP-адресами и соответствующими измерителями.
    """
    storage: MeterStorage = {}
    with open(file_dir, encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\t")
        for line in reader:
            if len(line) != 4:
                print(f"Некорректная строка: {line}")
                continue  # Пропустить некорректные строки
            ip, start, end, unit = line
            try:
                storage[ip] = StoredMeter(float(start), float(end), unit)
                print(
                    f"Измеритель добавлен: IP={ip}, Диапазон=({start}, {end}), Единица={unit}"
                )
            except ValueError as e:
                print(f"Ошибка преобразования строки {line}: {e}")
    return storage
