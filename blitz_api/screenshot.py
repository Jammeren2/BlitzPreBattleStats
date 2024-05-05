import asyncio
import pyautogui
import pytesseract
from PIL import Image

class Screenshot:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:/Users/my/Desktop/py/blitz_cheat/blitz_api/Tesseract-OCR/tesseract.exe'

    async def take_screenshot_and_detect_text(self, region, filename):
        screenshot = await self.async_take_screenshot(region, filename)
        screenshot_path = filename

        try:
            text = await self.async_detect_text(screenshot_path)
            text_without_spaces = text.replace(" ", "")
            screenshot_names = [line.split()[0] for line in text_without_spaces.split('\n') if line.strip()]
            return screenshot_names
        except Exception as e:
            print(f"Ошибка при распознавании текста: {e}")
            return []

    async def async_take_screenshot(self, region, filename):
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(filename)
        return filename

    async def async_detect_text(self, screenshot_path):
        image = Image.open(screenshot_path)
        text = pytesseract.image_to_string(image, lang='eng')
        return text