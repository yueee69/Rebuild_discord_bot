from utils.general import Toolkit

class Nick:
    @staticmethod
    async def nick(target: object, name: str, user: object):
        """
        params:
            target - 被改的人
            name - 要改的暱稱
            user: 用戶物件，用於建立log
        """
        log = create_log(target, name, user)
        await target.edit(nick = name, reason = log)

def create_log(target: object, name: str, user: object):
    """創造一個log，這會顯示在伺服器的審核日誌裡"""
    time = Toolkit.get_time()
    times = f"{time.year}/{time.month}/{time.day} | {time.hour}:{time.minute}:{time.second}"
    return f"(Log) | {user.display_name} 在 {times} 指定了 {target.display_name} {name}暱稱"