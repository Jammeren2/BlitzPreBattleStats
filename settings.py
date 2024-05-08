import tkinter as tk
from configparser import ConfigParser
from pynput import keyboard
from colored import fg, attr
import os

# Функция для очистки экрана терминала
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Функция для вывода инструкции
def print_instructions():
    clear_screen()
    print(fg('green') + "ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:" + attr('reset'))
    print(fg('green') + "Выделите области союзников. должно быть так: https://i.imgur.com/ZNj9PWi.png" + attr('reset'))
    print(fg('cyan') + "Смена выделенной области:" + attr('reset') + " Нажмите 'q'")
    print(fg('cyan') + "Перемещение области:" + attr('reset') + " Используйте клавиши 'w', 'a', 's', 'd'")
    print(fg('cyan') + "Изменение высоты и ширины:" + attr('reset') + " Используйте клавиши 'z', 'x', 'c', 'v'")
    print(fg('yellow') + "Для более удобной настройки вы можете открыть скриншот загрузки боя." + attr('reset'))

global selected
selected = 'team'
print_instructions()

# Создание основного окна
root = tk.Tk()
root.overrideredirect(True)  # Убираем рамку и заголовок окна
root.lift()  # Поднимаем окно наверх
root.wm_attributes("-topmost", True)  # Установка окна поверх других окон
root.wm_attributes("-disabled", True)  # Отключение взаимодействия с окном
root.wm_attributes("-transparentcolor", "white")  # Прозрачный фон

# Получение размеров экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Создание холста с белым фоном и прозрачностью
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg='white', highlightthickness=0)
canvas.pack()

# Чтение координат из config.ini
config = ConfigParser()
config.read('config.ini')

# Функция для создания контура квадрата
def create_square_outline(x, y, h, w, color):
    return canvas.create_rectangle(x, y, x + w, y + h, outline=color, width=2)

# Создание квадратов
squares = {}
for section in config.sections():
    if section.startswith('team') or section.startswith('enemy'):
        if 'coords' in config[section]:
            coords = config[section]['coords']
            color = 'red' if section.startswith('team') else 'blue'  # Выбор цвета в зависимости от имени секции
            x, y, h, w = map(int, coords.split(","))
            squares[section] = {'x': x, 'y': y, 'h': h, 'w': w}
            create_square_outline(x, y, h, w, color)


# Функция для перемещения квадрата по стрелкам на клавиатуре
def move_square(key):
    global selected
    key = key.char
    print(key)
    if key in ['w', 'ц', 's', 'ы', 'a', 'ф', 'd', 'в', 'z', 'я', 'x', 'ч', 'c', 'с', 'v', 'м', 'q', 'й']:
        for section, square in squares.items():
            if section == selected:
                if key == 'w' or key == 'ц':
                    square['y'] -= 10
                elif key == 's' or key == 'ы':
                    square['y'] += 10
                elif key == 'a' or key == 'ф':
                    square['x'] -= 10
                elif key == 'd' or key == 'в':
                    square['x'] += 10
                elif key == 'z' or key == 'я':
                    square['h'] -= 10
                elif key == 'x' or key == 'ч':
                    square['h'] += 10
                elif key == 'c' or key == 'с':
                    square['w'] -= 10
                elif key == 'v' or key == 'м':
                    square['w'] += 10

                config[section]['coords'] = f"{square['x']},{square['y']},{square['h']},{square['w']}"
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                break  # Прерываем цикл после обновления координат выбранного квадрата
        redraw_squares()  # Перерисовываем квадраты после изменения координат
    if key == 'q' or key == 'й':
        if selected == 'team':
            selected = 'enemy'
        else:
            selected = 'team'

def on_press(key):
    try:
        move_square(key)
    except AttributeError:
        pass

# Слушатель событий клавиатуры
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Функция для изменения размера квадрата при изменении размера окна
def resize(event):
    for section, square in squares.items():
        coords = canvas.coords(section)
        if coords:  # Проверяем, что список не пустой
            w = coords[2] - coords[0]
            h = coords[3] - coords[1]
            square['w'] = w
            square['h'] = h
            config[section]['coords'] = f"{square['x']},{square['y']},{square['h']},{square['w']}"
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
    redraw_squares()  # Перерисовываем квадраты после изменения размера

# Привязка события изменения размера окна к функции resize
root.bind("<Configure>", resize)

def redraw_squares():
    # Очищаем холст от предыдущих квадратов
    canvas.delete("all")

    # Создание квадратов с обновленными координатами
    for section, square in squares.items():
        coords = config[section]['coords']
        color = 'green' if section.startswith('team') else 'red'  # Выбор цвета в зависимости от имени секции
        x, y, h, w = map(int, coords.split(","))
        create_square_outline(x, y, h, w, color)

root.mainloop()
