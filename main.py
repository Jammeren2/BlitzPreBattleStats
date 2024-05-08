import configparser
from pynput import keyboard
import pyautogui

# Функция для чтения и записи значений coords из файла конфигурации
def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    display_team_coords = tuple(map(int, config['Display_team']['coords'].split(',')))
    display_enemy_coords = tuple(map(int, config['Display_enemy']['coords'].split(',')))
    return display_team_coords, display_enemy_coords

def write_config(display_team_coords, display_enemy_coords):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('Display_team', 'coords', ','.join(map(str, display_team_coords)))
    config.set('Display_enemy', 'coords', ','.join(map(str, display_enemy_coords)))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Функции для изменения значений coords
def change_display_team_coords(direction):
    global display_team_coords
    if direction == 'left':
        display_team_coords = (display_team_coords[0] - 10, display_team_coords[1])
    elif direction == 'right':
        display_team_coords = (display_team_coords[0] + 10, display_team_coords[1])

def change_display_enemy_coords(direction):
    global display_enemy_coords
    if direction == 'left':
        display_enemy_coords = (display_enemy_coords[0] - 10, display_enemy_coords[1])
    elif direction == 'right':
        display_enemy_coords = (display_enemy_coords[0] + 10, display_enemy_coords[1])

# Функции-обработчики нажатия клавиш
def on_press(key):
    try:
        if key.char == 'o':
            change_display_team_coords('left')
            change_display_enemy_coords('right')

            write_config(display_team_coords, display_enemy_coords)
        elif key.char == 'p':
            change_display_team_coords('right')
            change_display_enemy_coords('left')
            write_config(display_team_coords, display_enemy_coords)
    except AttributeError:
        pass

def get_screen_center():
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    return center_x, center_y, screen_width, screen_height


center_x, center_y, screen_width, screen_height = get_screen_center()
# Инициализация начальных значений coords
display_team_coords, display_enemy_coords = (center_x-444, 0), (center_x+110, 0)
write_config(display_team_coords, display_enemy_coords)

# Запуск слушателя клавиатуры
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
