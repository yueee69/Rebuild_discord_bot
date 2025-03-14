from dataclasses import dataclass
from typing import Union

from new_bot.utils.general import Toolkit

@dataclass
class Air_Data:
    manager = None
    times: int = 0
    
    def __init__(self, AirJson, manager=None):
        self.manager = manager
        self._times = AirJson["times"]

    @property
    def times(self):
        return self._times
    
    @times.setter
    def lottery_accumulation(self, value):
        self._times = value
        self.manager.update()
        
    def to_dict(self):
        return {
            "times": self._times
        }

class AirManager:
    def __init__(self, debug=False):
        self.AirDatas = {} # {userID: air_Data}
        self.debug = debug
        if self.debug:
            print("\nUserManager in debug mode")
        elif not self.debug:
            self.load_all_users()
    
    def load_all_users(self):
        data = Toolkit.open_jsons("air.json")
        for user_id, user_info in data.items():
            #print(f"Loading user {user_id}: {user_info}") 
            user = Air_Data(user_info, manager=self)
            self.__add_user(user, user_id)
            
    def update(self):
        if self.debug:
            print("update function is called")
        elif not self.debug:
            self.save_all_users()
            print("(air_manager) save all users success")
        
    # 禁止直接新增 User ，請使用 get_user 獲取用戶後再進行操作
    def __add_user(self, AirData: Air_Data, userID: Union[str, int]) -> Air_Data:
        AirData.manager = self
        self.AirDatas[str(userID)] = AirData
        return AirData

    def __create_user_instance(self) -> Air_Data:
        new_data = {
            "times": 0
        }
        return Air_Data(new_data, manager=self)

    def get_user(self, userID: Union[str, int]) -> Air_Data:
        user = self.AirDatas.get(str(userID)) 
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user
             
    def save_all_users(self):
        json_data = {userID: value.to_dict() for userID, value in self.AirDatas.items()}
        Toolkit.dump_jsons(("air.json", json_data))
        
    


