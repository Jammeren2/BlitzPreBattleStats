import asyncio
import time
import re 
import json
import tkinter as tk
import difflib
import os
import pyautogui
from colored import fg, attr
import sys
from configparser import ConfigParser
from pynput import keyboard
import subprocess

from blitz_api.blitz_api import BlitzAPI
from blitz_api.screenshot import Screenshot

config = ConfigParser()
config.read('config.ini')
data_file_path = config['settings']['data_file_path']

def run_code(progress):
    width = 40
    filled_length = int((progress / 10) * width)
    bar = '*' * filled_length + '-' * (width - filled_length)
    colored_bar = fg('green') + bar[:filled_length] + fg('white') + bar[filled_length:] + attr('reset')
    sys.stdout.write("\r" + colored_bar)
    sys.stdout.flush()
    time.sleep(0.1)


def get_screen_center():
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    return center_x, center_y, screen_width, screen_height

def extract_player_names(data_file_path):
    with open(data_file_path, 'rb') as file:
        data = file.read()
        hex_list = [hex(b)[2:] for b in data]
        text_data = ''.join([chr(int(hex_val, 16)) for hex_val in hex_list])
        lines = text_data.split('\n')[:40]  # Ограничиваем чтение до 40 строк
        text = '\n'.join(lines)

    text_without_links = re.sub(r'https?://\S+', '', text)
    text_cleaned = re.sub(r'[^A-Za-z0-9()\n _ ]+', '', text_without_links)
    # print(text_cleaned)
    pattern = r'[\W\s]*(\w+)\s*\('

    # Черный список ников
    blacklist = ["BattlesStats", "Database", "WaitTime", "mouseEnable", "playersBattleCategories"]

    # Находим все совпадения в тексте
    matches = re.findall(pattern, text_cleaned)

    players = []  # Создаем пустой массив для записи ников игроков
    if matches:
        for match in matches:
            if len(match) >= 4 and all(bad_word not in match for bad_word in blacklist):  
                # Проверяем, что ник не содержит слова из черного списка и имеет длину не менее 4 символов
                players.append(match)
    # else:
    #     # print("Ники игроков не найдены.")

    return players


def find_similar_names(screenshot_names, player_data):
    enemies = []
    others = []

    # Создаем переменную player_data_no_ и записываем туда player_data['username'] без '_'
    player_data_no_ = [re.sub(r'[^a-zA-Z0-9]', '', p['username']) for p in player_data]

    for name in screenshot_names:
        # Убираем все символы, кроме букв и цифр
        name_no_ = re.sub(r'[^a-zA-Z0-9]', '', name)
        similar = difflib.get_close_matches(name_no_, player_data_no_, n=1, cutoff=0.4)
        if similar:
            # print(f"Сравнивается {name_no_} с {similar[0]}")
            # Находим оригинальное имя в player_data
            original_name = player_data[player_data_no_.index(similar[0])]['username']
            # Сопоставляем оригинальное имя и screenshot_names
            for player in player_data:
                if player['username'] == original_name:
                    enemies.append(player)
                    break

    return enemies

async def main():
    # root = None  # Define root variable initially
    args3 = ["main.py"]
    process3 = subprocess.Popen([sys.executable] + args3)
    while True:

        start_time = time.time() 
        blitz_api = BlitzAPI()
        screenshot = Screenshot()
        print(' ')
        print(fg('yellow')+"Ожидание боя"+attr('reset'))
        while not os.path.exists(data_file_path):
            time.sleep(0.5)
        print(fg('green') + "Started" + attr('reset'))
        time.sleep(2)
        run_code(1)
        # Получение значений из конфига для скриншота врагов и команды
        enemy_coords = [int(x) for x in config['enemy']['coords'].split(',')]
        team_coords = [int(x) for x in config['team']['coords'].split(',')]
        enemy_coords[-1], enemy_coords[-2] = enemy_coords[-2], enemy_coords[-1]
        team_coords[-1], team_coords[-2] = team_coords[-2], team_coords[-1]


        center_x, center_y, screen_width, screen_height = get_screen_center()
        screenshot_enemy_names = await screenshot.take_screenshot_and_detect_text(tuple(enemy_coords), 'enemy.jpg')
        run_code(2)
        print("Имена противника:", screenshot_enemy_names)
        screenshot_team_names = await screenshot.take_screenshot_and_detect_text(tuple(team_coords), 'team.jpg')
        print("Имена команды:", screenshot_team_names)
        run_code(3)

        while os.stat(data_file_path).st_size == 0:
            time.sleep(0.5)
        file_players = extract_player_names(data_file_path)
        print(f'Из файла: {file_players}')
        run_code(4)

        players_data = await blitz_api.get_players_data(file_players)
        players_data = [player for player in players_data if player is not None]
        run_code(5)

        enemies = find_similar_names(screenshot_enemy_names, players_data)
        allies = find_similar_names(screenshot_team_names, players_data)
        run_code(7)
        enemies_data = [{'username': enemy['username'], 'id': enemy['id'], 'wins': enemy.get('wins', 0)} for enemy in enemies]
        allies_data = [{'username': ally['username'], 'id': ally['id'], 'wins': ally.get('wins', 0)} for ally in allies]
        run_code(9)


        args = ["blitz_api/display_data.py", json.dumps(allies_data), "Display_team"]
        args2 = ["blitz_api/display_data.py", json.dumps(enemies_data), "Display_enemy"]
        

        process1 = subprocess.Popen([sys.executable] + args)
        process2 = subprocess.Popen([sys.executable] + args2)
        


        run_code(10)
        print(" ")
        print(fg('magenta')+"SUCCESS!"+attr('reset'))
        while os.path.exists(data_file_path):
            time.sleep(0.5)
        print(" ")
        print(" ")
        process1.terminate()
        process2.terminate()
        # Закрыть сессию клиента
        await blitz_api.close()
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
loop.run_until_complete(main())  # Запускаем асинхронную функцию


