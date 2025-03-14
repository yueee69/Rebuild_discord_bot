from dataclasses import dataclass
from typing import Union

from new_bot.utils.general import Toolkit

@dataclass
class User:
    manager = None
    user_id: str = ""
    coin: int = 0
    fortune: int = 0
    voice: int = 0
    stream: int = 0
    gain: int = 0
    lvl: int = 0
    chat: int = 0
    buy: int = 0
    
    def __init__(self, userJson, manager=None):
        self.manager = manager
        self.user_id = userJson["user_id"]
        self._coin = userJson["coin"]
        self._fortune = userJson["fortune"]
        self._voice = userJson["voice"]
        self._stream = userJson["stream"]
        self._gain = userJson["gain"]
        self._lvl = userJson["lvl"]
        self._chat = userJson["chat"]
        self._buy = userJson["buy"]
        self._trusteeship = {}
        #self.trusteeship = BasePlan(**userJson["trusteeship"])
        
    @property
    def coin(self):
        return self._coin
    
    @coin.setter
    def coin(self, value):
        
        if value < self._coin:
            # 減少金幣不影響 gain（例如玩家花費金幣時）
            self._coin = value
        else:
            # 只增加累積獲得的金幣
            gained = value - self._coin
            self._coin = value
            self._gain += gained
            self._lvl = int(self._gain / 1500)  #此處更新以獲得的鮭魚幣，反映到等級 1500 = 1等
        
        self.manager.update()
        
    @property
    def fortune(self):
        return self._fortune
    
    @fortune.setter
    def fortune(self, value):
        self._fortune = value
        self.manager.update()
        
    @property
    def voice(self):
        return self._voice
    
    @voice.setter
    def voice(self, value):
        self._voice = value
        self.manager.update()
        
    @property
    def stream(self):
        return self._stream
    
    @stream.setter
    def stream(self, value):
        self._stream = value
        self.manager.update()
        
    @property
    def gain(self):
        return self._gain
    
    @gain.setter
    def gain(self, value):
        self._gain = value
        self.manager.update()
        
    @property
    def lvl(self):
        return self._lvl
    
    @lvl.setter
    def lvl(self, value):
        self._lvl = value
        self.manager.update()
        
    @property
    def chat(self):
        return self._chat
    
    @chat.setter
    def chat(self, value):
        self._chat = value
        self.manager.update()
        
    @property
    def buy(self):
        return self._buy
    
    @buy.setter
    def buy(self, value):
        self._buy = value
        self.manager.update()
        
    @property
    def trusteeship(self):
        return self._trusteeship
    
    @trusteeship.setter
    def trusteeship(self, value):
        self._trusteeship = value
        self.manager.update()
        
        
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "coin": self.coin,
            "fortune": self.fortune,
            "voice": self.voice,
            "stream": self.stream,
            "gain": self.gain,
            "lvl": self.lvl,
            "chat": self.chat,
            "buy": self.buy,
            "trusteeship": {}
            # "trusteeship": {
            #     "plan": self.trusteeship.plan,
            #     "day": self.trusteeship.day,
            #     "stop_day": self.trusteeship.stop_day,
            #     "notice": self.trusteeship.notice,
            #     "buy_plan": self.trusteeship.buy_plan
            # }
        }


class UserManager:
    def __init__(self, debug=False):
        self.UserDatas = {} # {userID: User}
        self.debug = debug
        self.user = None
        if self.debug:
            print("\nUserManager in debug mode")
        elif not self.debug:
            self.load_all_users()
    
    def load_all_users(self):
        data = Toolkit.open_jsons("user.json")
        for user_info in data:
            user = User(user_info, manager=self)
            self.__add_user(user)
            
    def update(self):
        if self.debug:
            print("update function is called")
        elif not self.debug:
            self.save_all_users()
            print("(user_manager) save all users success")
        
    # 禁止直接新增 User ，請使用 get_user 獲取用戶後再進行操作
    def __add_user(self, user: User) -> User:
        user.manager = self
        self.UserDatas[user.user_id] = user
        return user

    def __create_user_instance(self, userID: Union[str, int]) -> User:
        new_data = {
            "user_id": str(userID),
            "coin": 0,
            "fortune": 0,
            "voice": 0,
            "stream": 0,
            "gain": 0,
            "lvl": 0,
            "chat": 0,
            "buy": 0,
            "trusteeship": {
                "plan": None,
                "day": 0,
                "stop_day": 0,
                "notice": 1,
                "buy_plan": 0
            }
        }
        return User(new_data, manager=self)

    def get_user(self, userID: Union[str, int], from_register: bool = False) -> tuple[User, str]:
        """
        Prarms:
            from_register: 是否來自可以註冊的指令，如果沒有這項，所有開啟UserData的指令都會幫用戶註冊(如果沒有資料)
                但bot預設是讓用戶只在 /用戶資訊 註冊

        回傳:
            status: 返回取得用戶的狀態，用於 global_views.py/UserEmbed
                "Found": 找到用戶，回傳包含用戶資訊的Embed
                "NotFound": 沒找到，但已經幫你註冊了，回傳"已完成登記"的Embed
                "NotFoundAndNeedToRegister": 沒找到而且不是使用 /用戶資訊，回傳叫用戶註冊的Embed
        """
        user = self.UserDatas.get(str(userID)) 

        if user:
            self.user = user
            return user, "Found"
        elif from_register:
            new_create_user = self.__create_user_instance(userID)
            user = self.__add_user(new_create_user)
            self.user = user
            self.save_all_users()
            return user, "NotFound"

        return None, "NotFoundAndNeedToRegister"
        
    def save_all_users(self):
        user_list = [user.to_dict() for user in self.UserDatas.values()]
        Toolkit.dump_jsons(("user.json", user_list))
        
    


