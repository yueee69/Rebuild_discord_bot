from utils.general import Toolkit

class Assign_role:
    @staticmethod
    async def assign_role(target: object, role: object, user: object):
        """
        params:
            target - 被加的人
            role - 要加的身分組(物件)
            user - 施加的人
        """
        log = create_log(target, role, user)
        await target.add_roles(role, reason = log)

def create_log(target: object, role: object, user: object):
    """創造一個log，這會顯示在伺服器的審核日誌裡"""
    time = Toolkit.get_time()
    times = f"{time.year}/{time.month}/{time.day} | {time.hour}:{time.minute}:{time.second}"
    return f"(log) | {user.display_name} 在 {times} 對 {target.display_name} 添加了 {role.name} 身分組"