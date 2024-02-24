ver = "3.1.0"
print(f" ")
print(f" ")
print(f"   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ \033[38;5;206m██╗      █████╗ \033[0m")
print(f"  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗\033[38;5;206m██║     ██╔══██╗\033[0m")
print(f"  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║\033[38;5;206m██║     ███████║\033[0m")
print(f"  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║\033[38;5;206m██║     ██╔══██║\033[0m")
print(f"  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝\033[38;5;206m███████╗██║  ██║\033[0m")
print(f"   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ \033[38;5;206m╚══════╝╚═╝  ╚═╝\033[0m")
print(f"    \033[38;5;206mPolling Rate Tester\033[0m  " + ver + "                         https://gamepadla.com")
print(f" ")
print(f" ")
print(f"Based on the method of: https://github.com/chrizonix/XInputTest")

# Підключаємо бібліотеки
import pygame
import time
import numpy as np
import sys

# Розрахунок максиально можливого полінг рейту на базі існуючого
def get_polling_rate_max(actual_rate):
    max_rate = 125
    if actual_rate > 150:
         max_rate = 250
    if actual_rate > 320:
         max_rate = 500 
    if actual_rate > 600:
        max_rate = 1000
    return max_rate

# Ініціалізація Pygame та геймпадів
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# Перевірка доступності геймпадів
if not joysticks:
    print("No controller found")
    time.sleep(10)
    exit(1)

# Виведення списку доступних геймпадів
print("\nFound {} controller(s)".format(len(joysticks)))
[print(f"{idx + 1}. {joystick.get_name()}") for idx, joystick in enumerate(joysticks)]

# Вибір геймпаду за індексом або за замовчуванням
selected_index = input("Please enter the index of the controller you want to test: ")
try:
    selected_index = int(selected_index) - 1
    joystick = joysticks[selected_index] if 0 <= selected_index < len(joysticks) else joysticks[0]
except ValueError:
    joystick = joysticks[0]

print(f" ")
print(f"Rotate left stick without stopping.")

newRow = True

# Початок циклу
while True:
    if newRow:
        times = []
        last_delay = None
        start_time = time.perf_counter()
        prev_x, prev_y = None, None
        newRow = False

    pygame.event.pump()

    # Отримуємо положення стіків
    x = joystick.get_axis(0)
    y = joystick.get_axis(1)
    pygame.event.clear()

    # Якщо є рух стіку | Переконуємося що стік достатньо відхилився (Антидріфт)
    if not ("0.0" in str(x) and "0.0" in str(y)):

        # Фільтруємо нереальні показники від 0.2 до 150
        if last_delay is not None and last_delay > 0.5 and last_delay < 150: 

            # Закидаємо затримку в масив часу
            times.append(last_delay * 1.057) # Відіймаємо 5% * 1.057

            # Розраховуємо полінг рейт 499.33
            if times:
                # Отримуємо середній показник в масиві times 1.9918279988425118
                avg_times = np.mean(times)
                # Розраховуємо полінг рейт розділенням 1000
                polling_rate = 1000 / avg_times
                # Окрушляємо до двох знаків після крапки
                polling_rate = round(polling_rate, 2)
            else:
                polling_rate = 125

            # Вираховуємо максимальний полінг рейт [125, 250, 500, 1000]
            poling_max = get_polling_rate_max(polling_rate)

            # Розрахунок стабільності у відсотках
            stability = round((polling_rate / poling_max) * 100, 2)

            # Вивід інформації в строку з перезаписом
            sys.stdout.write(
                "\033[A\033[KPolling Rate: {:.2f} [{} Hz]   |   Stability: {:.2f}%\n".format(
                    polling_rate, poling_max, stability
                )
            )
            sys.stdout.flush()

        # Якщо не було попередніх позицій, то створюємо їх
        if prev_x is None and prev_y is None:
            prev_x, prev_y = x, y
        
        # Якщо попередні позиції відрізняються від поточних, було переміщення
        elif x != prev_x or y != prev_y:

            # Фіксуємо час заверження
            end_time = time.perf_counter()
            # Вираховуємо різницю між початком руху і завершенням
            duration = (end_time - start_time) * 1000

            # Оновлюємо start_time для насупного циклу
            start_time = end_time
            # Оновлюємо координати положення стіку для наступного циклу
            prev_x, prev_y = x, y

            while True:
                pygame.event.pump()
                new_x = joystick.get_axis(0)
                new_y = joystick.get_axis(1)
                pygame.event.clear()

                if new_x != x or new_y != y:
                    end = time.perf_counter()
                    last_delay = (end - start_time) * 1000
                    break

        # Вихід в новий цикл кожні X секунд
        if len(times) >= 500:
            print("")
            #print(f"Count = {len(times)}")
            newRow = True