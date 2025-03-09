from dataclasses import dataclass
from typing import Union

from new_bot.utils.general import Toolkit

@dataclass
class Lottery_Data:
    manager = None
    lottery_accumulation: int = 0
    lottery_total : int = 0
    
    def __init__(self, LotteryJson, manager=None):
        self.manager = manager
        self._lottery_accumulation = LotteryJson["lot"] #墊抽次數
        self._lottery_total = LotteryJson["total"]

    @property
    def lottery_accumulation(self):
        return self._lottery_accumulation
    
    @lottery_accumulation.setter
    def lottery_accumulation(self, value):
        self._lottery_accumulation = value
        self.manager.update()
        
    @property
    def lottery_total(self):
        return self._lottery_total
    
    @lottery_total.setter
    def lottery_total(self, value):
        self._lottery_total = value
        self.manager.update()

    def to_dict(self):
        return {
            "lot": self._lottery_accumulation,
            "total": self._lottery_total
        }

class LotteryManager:
    def __init__(self, debug=False):
        self.LotteryDatas = {} # {userID: Lottery_Data}
        self.debug = debug
        if self.debug:
            print("\nUserManager in debug mode")
        elif not self.debug:
            self.load_all_users()
    
    def load_all_users(self):
        data = Toolkit.open_jsons("lottery.json")
        for user_id, user_info in data.items():
            #print(f"Loading user {user_id}: {user_info}") 
            user = Lottery_Data(user_info, manager=self)
            self.__add_user(user, user_id)
            
    def update(self):
        if self.debug:
            print("\nupdate function is called\n")
        elif not self.debug:
            self.save_all_users()
            print("\nsave all users success\n")
        
    # 禁止直接新增 User ，請使用 get_user 獲取用戶後再進行操作
    def __add_user(self, lotteryData: Lottery_Data, userID: Union[str, int]) -> Lottery_Data:
        lotteryData.manager = self
        self.LotteryDatas[str(userID)] = lotteryData
        return lotteryData

    def __create_user_instance(self) -> Lottery_Data:
        new_data = {
            "lot":0,
            "total":0
        }
        return Lottery_Data(new_data, manager=self)

    def get_user(self, userID: Union[str, int]) -> Lottery_Data:
        user = self.LotteryDatas.get(str(userID)) 
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user
             
    def save_all_users(self):
        json_data = {userID: value.to_dict() for userID, value in self.LotteryDatas.items()}
        Toolkit.dump_jsons(("lottery.json", json_data))
        
    


