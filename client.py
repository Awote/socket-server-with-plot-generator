import socket
import random
import time
from datetime import datetime


def generate_data(ip: str, range_start: float, range_stop: float) -> str:
    """
    Генерирует строку данных для отправки серверу.

    Args:
        ip (str): IP-адрес измерителя.
        range_start (float): Начало диапазона.
        range_stop (float): Конец диапазона.

    Returns:
        str: Сформированная строка данных.
    """
    timestamp = datetime.now().strftime("%Y.%m.%d %H:%M:%S.%f")
    value = random.uniform(range_start, range_stop)  # Генерация случайного значения
    return f"{ip}\t{timestamp}\t{value:.2f}\n"


def run_client(server_host: str, server_port: int, devices: list, delay: float = 1.0):
    """
    Запускает клиента, который отправляет синтетические данные на сервер.

    Args:
        server_host (str): Адрес сервера.
        server_port (int): Порт сервера.
        devices (list): Список устройств с параметрами (IP, range_start, range_stop).
        delay (float): Задержка между отправками данных (в секундах).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((server_host, server_port))
            print(f"Подключено к серверу {server_host}:{server_port}")

            while True:
                # Генерация и отправка данных для каждого устройства
                for device in devices:
                    ip, range_start, range_stop = device
                    data = generate_data(ip, range_start, range_stop)
                    client_socket.sendall(data.encode("utf-8"))
                    print(f"Отправлено: {data.strip()}")

                # Задержка перед следующей отправкой
                time.sleep(delay)

        except ConnectionRefusedError:
            print(
                f"Ошибка подключения к серверу {server_host}:{server_port}. Сервер может быть недоступен."
            )
        except KeyboardInterrupt:
            print("Клиент остановлен пользователем.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    # Настройки клиента
    SERVER_HOST = "127.0.0.1"  # Замените на IP вашего сервера
    SERVER_PORT = 44444  # Замените на порт вашего сервера

    # Список устройств: (IP, range_start, range_stop)
    DEVICES = [
        ("10.0.0.1", 0, 110),  # Измеритель напряжения
        ("10.0.0.2", 0, 0.5),  # Измеритель тока (0 - 0.5 A)
        ("10.0.0.3", 0.2, 1),  # Измеритель тока (0.2 - 1 A)
        ("10.0.0.4", 1, 5),  # Измеритель тока (1 - 5 A)
        ("10.0.0.8", 3, 10),  # Измеритель тока (3 - 10 A)
    ]

    # Задержка между отправками данных
    DELAY = 1.0  # 1 секунда

    # Запуск клиента
    run_client(SERVER_HOST, SERVER_PORT, DEVICES, DELAY)
