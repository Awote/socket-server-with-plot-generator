import threading
from core.plotter import plot_power
from core.socket import run_server
from core.storage import Storage, power_computation_thread
from helpers.file import parse_file
from helpers.variables import HOST, LOG_PATH, PORT
from datetime import datetime
import os


def main():
    # Парсим файл сопоставления IP-адресов
    os.makedirs(LOG_PATH, exist_ok=True)
    log_file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    meter_storage = parse_file("ip_mapping.txt")  # Замените на путь к вашему файлу
    storage = Storage(
        meter_storage=meter_storage,
        log_name=os.path.join(LOG_PATH, f"{log_file_name}.txt"),
    )

    # Запуск сервера в отдельном потоке
    server_thread = threading.Thread(
        target=run_server, args=(HOST, PORT, storage), daemon=True
    )
    server_thread.start()

    # Запуск потока для вычисления мощности
    power_thread = threading.Thread(
        target=power_computation_thread, args=(storage,), daemon=True
    )
    power_thread.start()

    # Запуск графика в главном потоке
    plot_power(storage)


if __name__ == "__main__":
    main()
