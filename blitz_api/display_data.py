import tkinter as tk
from configparser import ConfigParser
import sys
import json

class DataDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.lift()
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-disabled", True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"+300+0")

    def show_enemies_data(self, enemies_data):
        for user_data in enemies_data:
            username = user_data['username']
            wins = user_data['wins']
            background_color = self.get_color(wins)
            label = tk.Label(self.root, text=f"{username} {wins}", width=30, borderwidth=1, relief="solid", background=background_color, font=("Arial", 14))
            label.pack(anchor="w")
            
    def get_color(self, wins):
        # Удаление символа процента и преобразование переменной wins в тип float
        wins = float(wins.rstrip('%'))  
        if wins >= 70:
            return '#800080'  # Violet
        elif wins >= 60:
            return '#00BFFF'  # Light Blue
        elif wins >= 50:
            return '#00FF00'  # Green
        elif wins <= 49:
            return '#fcf0f0'  # White

    def update_geometry(self, new_geometry):
        self.geometry = new_geometry
        self.root.geometry(f"+{self.geometry}+0")

    def read_config(self, filename, name):
        config = ConfigParser()
        config.read(filename)
        if name in config:
            coords = config[name].get('coords', None)
            if coords:
                x, y = map(int, coords.split(','))
                self.update_geometry(x)

    def display_data(self, name):
        self.update_geometry_after(name)
        self.root.update()  # Обновляем окно Tkinter один раз
        self.root.mainloop()  # Запускаем бесконечный цикл обработки событий

    def update_geometry_after(self, name):
        self.read_config('config.ini', name)  
        self.root.after(100, self.update_geometry_after, name)  # Передача аргумента name

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python display_data.py <JSON_data> <name>")
        sys.exit(1)
    json_data = sys.argv[1]
    name = sys.argv[2]
    try:
        enemies_data = json.loads(json_data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON data")
        sys.exit(1)

    display = DataDisplay()
    display.show_enemies_data(enemies_data)
    display.display_data(name)