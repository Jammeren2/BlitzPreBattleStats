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

from blitz_api.blitz_api import BlitzAPI
from blitz_api.screenshot import Screenshot

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
        similar = difflib.get_close_matches(name_no_, player_data_no_, n=1, cutoff=0.2)
        if similar:
            print(f"Сравнивается {name_no_} с {similar[0]}")
            # Находим оригинальное имя в player_data
            original_name = player_data[player_data_no_.index(similar[0])]['username']
            # Сопоставляем оригинальное имя и screenshot_names
            for player in player_data:
                if player['username'] == original_name:
                    enemies.append(player)
                    break

    return enemies



def get_color(wins):
    wins_percent = float(wins[:-1])
    if wins_percent >= 100:
        return '#2600ff'
    elif wins_percent >= 49:
        return '#26ff00'
    elif wins_percent >= 40:
        return '#ff0000'

async def main():
    while True:

        start_time = time.time() 
        blitz_api = BlitzAPI()
        screenshot = Screenshot()
        data_file_path = 'C:\\Users\\my\\Documents\\TanksBlitz\\replays\\recording_BuKa_B_Cyxux_TpycuKax.wotbreplay\\data.wotreplay'
        print(' ')
        print(fg('yellow')+"Ожидание боя"+attr('reset'))
        while not os.path.exists(data_file_path):
            time.sleep(0.5)
        print(fg('green') + "Started" + attr('reset'))
        time.sleep(2)
        run_code(1)





        center_x, center_y, screen_width, screen_height = get_screen_center()
        screenshot_enemy_names = await screenshot.take_screenshot_and_detect_text((center_x+290, center_y-180, 215, 296), 'enemy.jpg')
        run_code(2)
        # print("Имена противника:", screenshot_enemy_names)
        screenshot_team_names = await screenshot.take_screenshot_and_detect_text((center_x-505, center_y-189, 215, 300), 'team.jpg')
        # print("Имена команды:", screenshot_team_names)
        run_code(3)

        while os.stat(data_file_path).st_size == 0:
            time.sleep(0.5)
        file_players = extract_player_names(data_file_path)
        # print(file_players)
        run_code(4)

        players_data = await blitz_api.get_players_data(file_players)
        players_data = [player for player in players_data if player is not None]
        run_code(5)

        enemies = find_similar_names(screenshot_enemy_names, players_data)
        allies = find_similar_names(screenshot_team_names, players_data)
        run_code(7)
        # file_players = ['BuKa_B_Cyxux_TpycuKax6f0q', 'Gon43', 'AriStokRat_s_BaShkiRii', '8eBMTBH', 'Nikitka_ejik', '_kalavrat_', '3Jlou_u_HeDoBep4uBblu', 'MMurakame', 'BuKa_B_Cyxux_TpycuKax', 'maloyy34777', 'TTpaBo_uMel0', 'HU_GA__TOP', 'Arbus_228', 'Alexei228760', 'Steel_Gold', 'bibok_metkij']
        enemies_data = [{'username': enemy['username'], 'id': enemy['id'], 'wins': enemy['wins']} for enemy in enemies]
        allies_data = [{'username': ally['username'], 'id': ally['id'], 'wins': ally['wins']} for ally in allies]
        run_code(9)

        # print("Противники:")
        # print(json.dumps(enemies_data, ensure_ascii=False, indent=4))
        # print("\nСоюзники:")
        # print(json.dumps(allies_data, ensure_ascii=False, indent=4))

        end_time = time.time() 
        # print("Время выполнения:", end_time - start_time, "секунд")



        # Создаем окно для союзников

        # Создаем окно для противников

        if allies_data:
            root = tk.Tk()
            root.overrideredirect(True)
            root.lift()
            root.wm_attributes("-topmost", True)
            root.wm_attributes("-disabled", True)
            root.wm_attributes("-transparentcolor", "white")
            geo_team = (11.7 / 100) * screen_width
            geo_team = int(geo_team)
            root.geometry(f"+{geo_team}+0")

            # Отображаем данные в окнах
            for user_data in allies_data:
                username = user_data['username']
                wins = user_data['wins']
                background_color = get_color(wins)
                label = tk.Label(root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid",  background=background_color, font=("Arial", 14))
                label.pack(anchor="w")
            root.update()


        if enemies_data:
            enemy_root = tk.Tk()
            enemy_root.overrideredirect(True)
            enemy_root.lift()
            enemy_root.wm_attributes("-topmost", True)
            enemy_root.wm_attributes("-disabled", True)
            enemy_root.wm_attributes("-transparentcolor", "white")
            geo_enemy = (75 / 100) * screen_width
            geo_enemy = int(geo_enemy)
            enemy_root.geometry(f"+{geo_enemy}+0")

            for user_data in enemies_data:
                username = user_data['username']
                wins = user_data['wins']
                background_color = get_color(wins)
                label = tk.Label(enemy_root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid",  background=background_color, font=("Arial", 14))
                label.pack(anchor="w")
                enemy_root.update()

        run_code(10)
        print(" ")
        print(fg('magenta')+"SUCCESS!"+attr('reset'))
        while os.path.exists(data_file_path):
            time.sleep(0.5)
        print(" ")
        print(" ")
        if 'root' in locals() and isinstance(root, tk.Tk):
            root.destroy()

        if 'enemy_root' in locals() and isinstance(enemy_root, tk.Tk):
            enemy_root.destroy()

        # Закрыть сессию клиента
        await blitz_api.close()
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
loop.run_until_complete(main())  # Запускаем асинхронную функцию
 

