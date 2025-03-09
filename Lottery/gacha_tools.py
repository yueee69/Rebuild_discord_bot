"""
這個專案專門存放與抽卡相關的工具。
"""
import random
from abc import ABC, abstractmethod

from new_bot.utils.general import Toolkit

class Lottery(ABC):
    @abstractmethod
    def draw(self, draw_count):
        pass

class Norm_pool(Lottery):
    def __init__(self):
        self.percent = {"一般": 90, "普通": 9, "大獎": 1}
        self.prize_pools = {
            "普通": {
                "空氣": 35,
                "鮭魚幣+10000": 1,
                "鮭魚幣+1000": 10,
                "鮭魚幣+500": 20,
                "鮭魚幣+2000": 5,
                "鮭魚幣+5000": 4,
                "5萬眾神幣": 20,
                "10萬眾神幣": 5
            },
            "一般": {
                "100萬眾神幣": 10,
                "舞者之書": 15,
                "魔法戰士之書": 45,
                "空氣": 20,
                "50萬眾神幣": 10,
                "75萬眾神幣": 10
            },
            "大獎": {
                "500萬眾神幣:star:": 15,
                "免費附魔一次:star:": 35,
                "暗黑之書/徒手書/詩人書/忍書 四選一:star:": 35,
                "紅色王石任選:star:": 2,
                "綠色王石任選:star:": 5,
                "王石任選:star:": 1,
                "紫色王石任選:star:": 2,
                "黃色王石任選:star:": 5
            }
        }

    def draw(self, lottery_json: object, times: int = 10) -> list:
        """
        Params:
            lottery_json: 用戶的 json 資料, 用於判斷大、小保底
            times: 抽取次數 預設10
        """
        prizes = []
    
        for _ in range(times):
            lottery_json.lottery_accumulation += 1
            lottery_json.lottery_total += 1

            weights = self.percent.copy()

            if lottery_json.lottery_accumulation == 101:
                weights = {
                    "一般": 0,
                    "普通": 0,
                    "大獎": 100
                }

            pool = random.choices(["普通", "一般", "大獎"], weights=list(weights.values()))[0]

            if pool == "大獎":
                lottery_json.lottery_accumulation = 0

            prize = random.choices(
                list(self.prize_pools[pool].keys()), 
                weights=list(self.prize_pools[pool].values())
            )[0]
            prizes.append(prize)

        return prizes


class Item_pool(Lottery):
    def __init__(self):
        self.item_pools = {
            "鮭魚幣+1750": 35,
            "鮭魚幣+2000": 25,
            "鮭魚幣+2500": 15,
            "鮭魚幣+3000": 8,
            "鮭魚幣+5000": 3,
            "迴轉卡": 2,
            "增加身分組卡": 4,
            "指定身分組卡": 4,
            "指定暱稱卡": 4
        }

    def draw(self, times: int = 10) -> list:
        """
        Params:
            times: 抽取次數 預設10
        """
        prizes = random.choices(
            list(self.item_pools.keys()), 
            weights=list(self.item_pools.values()), 
            k=times
        )
        return prizes

class Xtal_pool(Lottery):
    @staticmethod
    def draw(times: int = 1) -> list:
        """
        Prarms:
            times: 抽取次數 預設10
        """
        xtal_Probability_Data = Toolkit.open_jsons("xtal_lottery.json")
        item_list = list(xtal_Probability_Data[0].keys())
        weigths = list(xtal_Probability_Data[0].values())
        prizes = random.choices(item_list, weights = weigths, k = times)
        return prizes


