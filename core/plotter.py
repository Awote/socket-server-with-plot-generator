from datetime import datetime, timedelta
import time
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from core.storage import Storage


def plot_power(storage: Storage):
    """
    Отрисовывает график мощности в режиме реального времени.

    Args:
        storage (Storage): Объект хранения и логирования данных.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    (line,) = ax.plot_date([], [], "-", label="Мощность (Вт)")
    ax.set_xlabel("Время")
    ax.set_ylabel("Мощность (Вт)")
    ax.set_title("Изменение потребляемой мощности во времени")
    ax.legend()
    ax.grid(True)

    # Форматирование оси X для отображения времени
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.autofmt_xdate()

    def init():
        ax.set_xlim(datetime.now(), datetime.now() + timedelta(seconds=60))
        ax.set_ylim(0, 100)  # Начальные пределы по оси Y, можно настроить
        line.set_data([], [])
        return (line,)

    def update(frame):
        with storage.lock:
            if not storage.power_data:
                return (line,)
            times, powers = zip(*storage.power_data)
        ax.set_xlim(times[0], times[-1] + timedelta(seconds=1))
        ax.set_ylim(min(powers) * 0.9, max(powers) * 1.1)
        line.set_data(times, powers)
        return (line,)

    ani = FuncAnimation(fig, update, init_func=init, interval=1000, blit=True)
    plt.show()
