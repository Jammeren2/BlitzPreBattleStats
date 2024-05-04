import re 
import os
import time
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import difflib
import json
import pyautogui
import pytesseract
from PIL import Image
import tkinter as tk

pytesseract.pytesseract.tesseract_cmd = r'C:/Users/my/Desktop/Tesseract-OCR/tesseract.exe'

def take_screenshot_and_detect_text():
    # Сделать скриншот
    screenshot = pyautogui.screenshot(region=(1570, 540, 215, 296))
    screenshot_path = 'enemy.jpg'
    screenshot.save(screenshot_path)
    print("Скриншот сохранен как enemy.jpg")

    # Распознать текст на скриншоте
    text = pytesseract.image_to_string(Image.open(screenshot_path), lang='eng')
    print("enemy:")
    print("")
    print(text)

    # Извлечение имен из текста скриншота
    screenshot_names = [line.split()[0] for line in text.split('\n') if line.strip()]
    # screenshot_names = ['maroz_122d', 'KEYS_2019', 'fatal__angel', 'laver1337_', 'thurramov', 'SenKo_105', 'pawel_613']
    return screenshot_names
def take_screenshot_and_detect_text_team():
    # Сделать скриншот
    screenshot = pyautogui.screenshot(region=(776, 552, 215, 296))
    screenshot_path = 'team.jpg'
    screenshot.save(screenshot_path)
    print("Скриншот сохранен как team.jpg")

    # Распознать текст на скриншоте
    text = pytesseract.image_to_string(Image.open(screenshot_path), lang='eng')
    print("team:")
    print("")
    print(text)

    # Извлечение имен из текста скриншота
    screenshot_names = [line.split()[0] for line in text.split('\n') if line.strip()]
    # screenshot_names = ['maroz_122d', 'KEYS_2019', 'fatal__angel', 'laver1337_', 'thurramov', 'SenKo_105', 'pawel_613']
    return screenshot_names

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

    return enemies, others


def get_player_id(nickname):
    url = f"https://romansh.ru/blitz/ru/player-search/{nickname}"
    response = requests.get(url)
    data = response.json()
    if "success" in data and len(data["success"]) > 0:
        for player_info in data["success"]:
            if "label" in player_info and player_info["label"] == nickname:
                return {"username": nickname, "id": player_info["id"]}
    return None



def get_player_stats(player_id):
    url = f"https://romansh.ru/blitz/ru/player/{player_id}"
    response = requests.get(url)
    try:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        player_info_table = soup.find("table", class_="playerInfoTable")
        if player_info_table:
            win_ratio_percent = get_win_ratio(player_info_table)
            return win_ratio_percent
        else:
            return None
    except requests.exceptions.HTTPError:
        return None

def get_win_ratio(player_info_table):
    total_stats_td = player_info_table.find("td", class_="js_total")
    if total_stats_td:
        li_tags = total_stats_td.find_all("li")
        for li in li_tags:
            win_ratio_tag = li.find("b")
            if win_ratio_tag:
                win_ratio_text = win_ratio_tag.get_text(strip=True)
                if "%" in win_ratio_text:
                    win_ratio_percent = win_ratio_text
                    return win_ratio_percent
    return None


data_file_path = 'C:\\Users\\my\\Documents\\TanksBlitz\\replays\\recording_BuKa_B_Cyxux_TpycuKax.wotbreplay\\data.wotreplay'


# Проверяем, существует ли файл
while not os.path.exists(data_file_path):
    time.sleep(1)
print("Продолжаем выполнение кода.")
time.sleep(3)
screenshot_names = take_screenshot_and_detect_text()
screenshot_names_team = take_screenshot_and_detect_text_team()


time.sleep(10)

with open(data_file_path, 'rb') as file:
    data = file.read()
    hex_list = [hex(b)[2:] for b in data]
    text_data = ''.join([chr(int(hex_val, 16)) for hex_val in hex_list])
    lines = text_data.split('\n')[:40]  # Ограничиваем чтение до 40 строк
    # print(lines)
    text = '\n'.join(lines)

text_without_links = re.sub(r'https?://\S+', '', text)
text_cleaned = re.sub(r'[^A-Za-z0-9()\n _ ]+', '', text_without_links)

pattern = r'[\W\s]*(\w+)\s*\('

# Черный список ников
blacklist = ["BattlesStats", "Database", "WaitTime", "mouseEnable", "playersBattleCategories"]

# Находим все совпадения в тексте
matches = re.findall(pattern, text_cleaned)
print(matches)
print(text_cleaned)
if matches:
    # print("Ники игроков:")
    players = []  # Создаем пустой массив для записи ников игроков
    for match in matches:
        if len(match) >= 4 and all(bad_word not in match for bad_word in blacklist):  
            # Проверяем, что ник не содержит слова из черного списка и имеет длину не менее 4 символов
            players.append(match)
            # print(match)
          # Добавляем ник каждого игрока в массив
    print(players)
else:
    print("Ники игроков не найдены.")
    
def get_player_data(player):
    player_info = get_player_id(player)
    if player_info:
        win_ratio = get_player_stats(player_info['id'])
        if win_ratio:
            player_info['wins'] = win_ratio
        return player_info
    return None

with ThreadPoolExecutor() as executor:
    player_data = list(executor.map(get_player_data, players))


# Фильтрация None значений
player_data = [player for player in player_data if player is not None]

# print(json.dumps(player_data, indent=4))
print(player_data)

    
# Соответствие с именами противников
screenshot_names_team = [name.replace(" ", "") for name in screenshot_names_team]
enemies, _ = find_similar_names(screenshot_names, player_data)
allies, _ = find_similar_names(screenshot_names_team, player_data)
print(f'1 {screenshot_names_team}')
print(f'2 {player_data}')

# Создание словарей для противников и союзников
enemies_data = [{'username': enemy['username'], 'id': enemy['id'], 'wins': enemy['wins']} for enemy in enemies]
allies_data = [{'username': ally['username'], 'id': ally['id'], 'wins': ally['wins']} for ally in allies]

# Вывод данных о противниках в формате JSON
print("Противники:")
print(json.dumps(enemies_data, ensure_ascii=False, indent=4))

# Вывод данных о союзниках в формате JSON
print("\nСоюзники:")
print(json.dumps(allies_data, ensure_ascii=False, indent=4))

def get_color(wins):
    wins_percent = float(wins[:-1])
    if wins_percent >= 100:
        return '#2600ff'
    elif wins_percent >= 49:
        return '#26ff00'
    elif wins_percent >= 40:
        return '#ff0000'

# Создаем окно для союзников
root = tk.Tk()
root.overrideredirect(True)
root.lift()
root.wm_attributes("-topmost", True)
root.wm_attributes("-disabled", True)
root.wm_attributes("-transparentcolor", "white")

root.geometry("+300+0")

for user_data in allies_data:
    username = user_data['username']
    wins = user_data['wins']
    background_color = get_color(wins)
    label = tk.Label(root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid",  background=background_color, font=("Arial", 14))
    label.pack(anchor="w")

# Создаем окно для противников
enemy_root = tk.Tk()
enemy_root.overrideredirect(True)
enemy_root.lift()
enemy_root.wm_attributes("-topmost", True)
enemy_root.wm_attributes("-disabled", True)
enemy_root.wm_attributes("-transparentcolor", "white")

enemy_root.geometry("+1800+0")

for user_data in enemies_data:
    username = user_data['username']
    wins = user_data['wins']
    background_color = get_color(wins)
    label = tk.Label(enemy_root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid",  background=background_color, font=("Arial", 14))
    label.pack(anchor="w")

root.mainloop()
enemy_root.mainloop()


