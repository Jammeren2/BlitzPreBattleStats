# BlitzPreBattleStats

## Описание (Description)

### Русский:

Это приложение на Python предназначено для отображения статистики игроков в игре "Tanks Blitz" перед началом боя. Программа анализирует данные из файлов реплеев игры и отображает статистику игроков, такую как их ники и количество побед. Для работы программы необходимо указать путь к папке с файлами реплеев и путь к папке с Tesseract-OCR.

### English:

This Python application is designed to display player statistics in the game "Tanks Blitz" before the start of the battle. The program analyzes data from game replay files and displays player statistics, such as their nicknames and number of victories. To run the program, you need to specify the path to the folder with replay files and the path to the folder with Tesseract-OCR.

#### Test:
https://youtu.be/h1nUQOxF0Nw

## Установка (Installation)
Для установки необходимо выполнить следующие шаги:

1. Установите необходимые библиотеки с помощью команды pip:
```bash
pip install aiohttp beautifulsoup4 pyautogui pytesseract pillow colored
```

2. В файле screenshot.py укажите путь к исполняемому файлу tesseract.exe в следующей строке:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/my/Desktop/py/blitz_cheat/blitz_api/Tesseract-OCR/tesseract.exe'
```

3. В файле blitz_cheat_v0.4-test.py найдите следующую строку и замените ее на свой путь к файлу data.wotreplay:
```python
data_file_path = 'C:\\Users\\my\\Documents\\TanksBlitz\\replays\\recording_Nick_Name.wotbreplay\\data.wotreplay'
```
#### Обратите внимание, что папка recording_Nick_Name.wotbreplay появляется только во время боя.