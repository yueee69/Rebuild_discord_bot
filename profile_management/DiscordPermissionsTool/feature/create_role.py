from utils.general import Toolkit

import nextcord

class Create_role:
    @staticmethod
    async def create_role(guild: object, name: str, color: str, user: str):
        """
        params:
            guild: 群組
            name: 要加的名稱
            color: 顏色
            user: 用戶物件，用於建立log
        """
        log = create_log(user)
        color = trans_hex_to_color(color)
        return await guild.create_role(name = name, color = color, reason = log, mentionable = True)

def trans_hex_to_color(hex: str):
    return nextcord.Colour(
        int(hex.replace("#", ''), 16)
    )

def create_log(user: object):
    """創造一個log，這會顯示在伺服器的審核日誌裡"""
    time = Toolkit.get_time()
    times = f"{time.year}/{time.month}/{time.day} | {time.hour}:{time.minute}:{time.second}"
    return f"(Log) | {user.display_name} 在 {times} 創建了這個身分組"
        