import asyncio
import aiohttp
from bs4 import BeautifulSoup

class BlitzAPI:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def get_player_id(self, nickname):
        url = f"https://romansh.ru/blitz/ru/player-search/{nickname}"
        async with self.session.get(url) as response:
            data = await response.json()
            if "success" in data and len(data["success"]) > 0:
                for player_info in data["success"]:
                    if "label" in player_info and player_info["label"] == nickname:
                        return {"username": nickname, "id": player_info["id"]}
        return None

    async def get_player_stats(self, player_id):
        url = f"https://romansh.ru/blitz/ru/player/{player_id}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), "html.parser")
            player_info_table = soup.find("table", class_="playerInfoTable")
            if player_info_table:
                win_ratio_percent = self.get_win_ratio(player_info_table)
                return win_ratio_percent
            else:
                return None

    def get_win_ratio(self, player_info_table):
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

    async def get_player_data(self, player):
        player_info = await self.get_player_id(player)
        if player_info:
            win_ratio = await self.get_player_stats(player_info['id'])
            if win_ratio:
                player_info['wins'] = win_ratio
            return player_info
        return None

    async def get_players_data(self, players):
        tasks = [self.get_player_data(player) for player in players]
        return await asyncio.gather(*tasks)


