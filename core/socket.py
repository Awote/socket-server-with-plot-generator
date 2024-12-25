# server.py

from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
import threading

from core.storage import Storage


def process_incoming_line(line: str, storage: Storage):
    """
    Обрабатывает одну строку данных из TCP-сокета.

    Формат строки: {IP_ADDR}\t{TIMESTAMP}\t{VALUE}

    Args:
        line (str): Строка данных.
        storage (Storage): Объект хранения и логирования данных.
    """
    parts = line.split("\t")
    if len(parts) != 3:
        print(f"Некорректная строка данных: {line}")
        return
    ip, timestamp_str, value_str = parts
    print(parts)
    try:
        timestamp = datetime.strptime(timestamp_str, "%Y.%m.%d %H:%M:%S.%f")
        value = float(value_str)
        # Получаем единицу измерения из meter_storage
        meter = storage.meter_storage.get(ip)
        if not meter:
            print(f"Неизвестный IP-адрес в данных: {ip}")
            return
        unit = meter.unit
        # Валидируем и сохраняем данные
        success = storage.validate_and_store(ip, timestamp, value, unit)
        if success:
            print(
                f"Данные сохранены: IP={ip}, Время={timestamp}, Значение={value}, Единица={unit}"
            )
        else:
            print(
                f"Данные не сохранены: IP={ip}, Время={timestamp}, Значение={value}, Единица={unit}"
            )
    except ValueError as e:
        print(f"Ошибка обработки строки {line}: {e}")


def handle_client(client_socket: socket, address: tuple, storage: Storage):
    """
    Обрабатывает соединение с клиентом.

    Args:
        client_socket (socket): Сокет клиента.
        address (tuple): Адрес клиента.
        storage (Storage): Объект хранения и логирования данных.
    """
    print(f"Подключён клиент: {address}")
    buffer = ""
    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                print(f"Клиент {address} отключился.")
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    process_incoming_line(line.strip(), storage)
    except ConnectionResetError:
        print(f"Соединение с клиентом {address} было разорвано.")
    except Exception as e:
        print(f"Ошибка при обработке клиента {address}: {e}")
    finally:
        client_socket.close()
        print(f"Соединение с клиентом {address} закрыто.")


def run_server(host: str, port: int, storage: Storage):
    """
    Запускает TCP-сервер.

    Args:
        host (str): Адрес сервера.
        port (int): Порт сервера.
        storage (Storage): Объект хранения и логирования данных.
    """
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Сервер запущен и слушает на {host}:{port}")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                # Запускаем обработку клиента в отдельном потоке
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address, storage),
                    daemon=True,
                )
                client_thread.start()
            except KeyboardInterrupt:
                print("\nСервер остановлен пользователем.")
                break
            except Exception as e:
                print(f"Ошибка сервера: {e}")
