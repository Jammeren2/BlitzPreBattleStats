import asyncio
import time
import re 
import json
import tkinter as tk
import difflib
import os

from blitz_api.blitz_api import BlitzAPI
from blitz_api.screenshot import Screenshot

def extract_player_names(data_file_path):
    with open(data_file_path, 'rb') as file:
        data = file.read()
        hex_list = [hex(b)[2:] for b in data]
        text_data = ''.join([chr(int(hex_val, 16)) for hex_val in hex_list])
        lines = text_data.split('\n')[:40]  # Ограничиваем чтение до 40 строк
        text = '\n'.join(lines)

    text_without_links = re.sub(r'https?://\S+', '', text)
    text_cleaned = re.sub(r'[^A-Za-z0-9()\n _ ]+', '', text_without_links)

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
    else:
        print("Ники игроков не найдены.")

    return players

def find_similar_names(screenshot_names, player_data):
    enemies = []
    others = []

    for name in screenshot_names:
        similar = difflib.get_close_matches(name, [p['username'] for p in player_data], n=1)
        if similar:
            player = next(p for p in player_data if p['username'] == similar[0])
            enemies.append(player)
        else:
            print(f"No match found for {name} in player data.")

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
        print("Ожидание боя")
        while not os.path.exists(data_file_path):
            time.sleep(0.5)
        print("Started")
        time.sleep(2)
        # Сделать скриншот и распознать текст противника
        screenshot_enemy_names = await screenshot.take_screenshot_and_detect_text((1570, 540, 215, 296), 'enemy.jpg')
        print("Имена противника:", screenshot_enemy_names)
        # Сделать скриншот и распознать текст команды
        screenshot_team_names = await screenshot.take_screenshot_and_detect_text((776, 552, 215, 296), 'team.jpg')
        print("Имена команды:", screenshot_team_names)
        while os.stat(data_file_path).st_size == 0:
            time.sleep(0.5)
        file_players = extract_player_names(data_file_path)
        print(file_players)
        players_data = await blitz_api.get_players_data(file_players)
        players_data = [player for player in players_data if player is not None]

        enemies = find_similar_names(screenshot_enemy_names, players_data)
        allies = find_similar_names(screenshot_team_names, players_data)
        print(allies)
        enemies_data = [{'username': enemy['username'], 'id': enemy['id'], 'wins': enemy['wins']} for enemy in enemies]
        allies_data = [{'username': ally['username'], 'id': ally['id'], 'wins': ally['wins']} for ally in allies]
        print("Противники:")
        print(json.dumps(enemies_data, ensure_ascii=False, indent=4))
        print("\nСоюзники:")
        print(json.dumps(allies_data, ensure_ascii=False, indent=4))


        end_time = time.time() 
        print("Время выполнения:", end_time - start_time, "секунд")

        # Создаем окно для союзников
        root = tk.Tk()
        root.overrideredirect(True)
        root.lift()
        root.wm_attributes("-topmost", True)
        root.wm_attributes("-disabled", True)
        root.wm_attributes("-transparentcolor", "white")
        root.geometry("+300+0")
        # Создаем окно для противников

        enemy_root = tk.Tk()
        enemy_root.overrideredirect(True)
        enemy_root.lift()
        enemy_root.wm_attributes("-topmost", True)
        enemy_root.wm_attributes("-disabled", True)
        enemy_root.wm_attributes("-transparentcolor", "white")
        enemy_root.geometry("+1800+0")

        # Отображаем данные в окнах
        for user_data in allies_data:
            username = user_data['username']
            wins = user_data['wins']
            background_color = get_color(wins)
            label = tk.Label(root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid",  background=background_color, font=("Arial", 14))
            label.pack(anchor="w")

        for user_data in enemies_data:
            username = user_data['username']
            wins = user_data['wins']
            background_color = get_color(wins)
            label = tk.Label(enemy_root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid",  background=background_color, font=("Arial", 14))
            label.pack(anchor="w")

        # Обновляем окна перед началом цикла
        root.update()
        enemy_root.update()

        while os.path.exists(data_file_path):
            time.sleep(0.5)

        root.destroy()
        enemy_root.destroy()
        # Закрыть сессию клиента
        await blitz_api.close()
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
loop.run_until_complete(main())  # Запускаем асинхронную функцию
 

