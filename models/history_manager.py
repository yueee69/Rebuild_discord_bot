from dataclasses import dataclass, field
from typing import Union, List

from utils.general import Toolkit

@dataclass
class HistoryData:
    manager: object = None
    user_lottery_history_list: List = field(default_factory=list)

    def __init__(self, LotteryHistoryJson, manager=None):
        self.manager = manager
        self.user_lottery_history_list = LotteryHistoryJson  # 修正為 self.user_lottery_history_list

    def dump_items(self, items: Union[str, list]):
        if isinstance(items, list):
            self.user_lottery_history_list.extend(items)  # 直接使用 extend
        elif isinstance(items, str):
            self.user_lottery_history_list.append(items)
        
        if self.manager:  # 避免 self.manager 為 None 時出錯
            self.manager.update()

    def to_dict(self):
        return self.user_lottery_history_list  # 回傳正確的歷史紀錄

class HistoryManager:
    def __init__(self, debug=False):
        self.HistoryDatas = {} # {userID: Lottery_history_Data}
        self.debug = debug
        if self.debug:
            print("\nHistoryManager in debug mode")
        else:  # 這裡不需要 `elif not self.debug`
            self.load_all_users()
    
    def load_all_users(self):
        data = Toolkit.open_jsons("history.json")
        for user_id, user_info in data.items():
            user = HistoryData(user_info, manager=self)  # 修正為 HistoryData
            self.__add_user(user, user_id)
            
    def update(self):
        if self.debug:
            print("update function is called")
        else:
            self.save_all_users()
            print("(history_manager) save all users success")
        
    # 禁止直接新增 User ，請使用 get_user 獲取用戶後再進行操作
    def __add_user(self, HistoryData: HistoryData, userID: Union[str, int]) -> HistoryData:
        HistoryData.manager = self
        self.HistoryDatas[str(userID)] = HistoryData
        return HistoryData

    def __create_user_instance(self) -> HistoryData:
        return HistoryData([], manager=self)

    def get_user(self, userID: Union[str, int]) -> HistoryData:
        user = self.HistoryDatas.get(str(userID)) 
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user
    
    def save_all_users(self):
        json_data = {userID: value.to_dict() for userID, value in self.HistoryDatas.items()}
        Toolkit.dump_jsons(("history.json", json_data))
