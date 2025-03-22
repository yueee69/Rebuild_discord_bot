import random
import json
from pathlib import Path
from typing import Union

from datetime import timezone ,timedelta, datetime
from nextcord import Color
from new_bot.core import constants

class Toolkit():
    def __init__(self, message = None, debug=False):
        self.message = message
        self.debug = debug

    @classmethod
    def get_time(self) -> timedelta:
        tzinfo=timezone(timedelta(hours=constants.TIME_ZONE))
        return datetime.now(tzinfo)

    @classmethod
    def get_period_time(self):
        tzinfo=timezone(timedelta(hours=constants.TIME_ZONE))
        taipei_time = datetime.now(tzinfo)
        hour = taipei_time.hour
        minute = "0" + str(taipei_time.minute) if len(str(taipei_time.minute)) == 1 else taipei_time.minute
        period = "上午" if hour < 12 else "下午"
        return hour,minute,period
    
    @staticmethod
    def randomcolor():
        while True:
            r = random.randint(0, 150)  # 避免 R 過高
            g = random.randint(50, 255)  # G 不能太低，避免暗紅
            b = random.randint(50, 255)  # B 不能太低，避免暗紅

            # 確保 G 和 B 至少有一個接近 R，避免「紅遠大於其他顏色」
            if abs(r - g) > 60 and abs(r - b) > 60:
                continue

            return Color.from_rgb(r, g, b)
    
    @staticmethod
    def is_custom_color(color: str) -> bool:
        """檢查字串是否為合法的 HEX 色碼"""
        if not color.startswith("#") or len(color) != 7:
            return True
        try:
            int(color[1:], 16)  # 嘗試將 #RRGGBB 轉換為 16 進制數字
            return False
        except ValueError:
            return True
    
    @classmethod
    def open_jsons(self, *names:str) -> list[dict]:
        jsons = []
        base_path = Path(__file__).resolve().parent.parent / "Json" 

        for name in names:
            json_path = base_path / name
            try:
                with json_path.open('r', encoding='utf-8-sig') as file:
                    jsons.append(json.load(file))
            except FileNotFoundError:
                raise FileNotFoundError(f'Cant find {name}')    
        
        return jsons[0] if len(jsons) == 1 else jsons
    
    @classmethod
    def dump_jsons(self, *file_pairs:tuple) -> bool:
        base_path = Path(__file__).resolve().parent.parent / "Json"
        try:
            for name, file in file_pairs:
                json_path = base_path / name
                try:
                    with json_path.open("w", encoding="utf-8") as f:
                        json.dump(file, f, ensure_ascii=False, indent=4)
                except:
                    print(f'Cant find {name}')
                    return False
        except ValueError:
            print(f"無法解包 {file_pairs} ，確認是否是 ('json_name.json', file) 的類型")
            return False
        
    @classmethod
    def check_money_is_enough(self, money: int, price: int) -> bool:
        return money >= price