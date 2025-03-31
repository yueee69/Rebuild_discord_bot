import nextcord

from utils.general import Toolkit

class Assign_role:
    @staticmethod
    async def assign_role(target: nextcord.Member, role: nextcord.Role, user: nextcord.Member, display_color: bool):
        """
        params:
            target - 被加的人
            role - 要加的身分組(物件)
            user - 施加的人
        """
        log = create_log(target, role, user)
        await target.add_roles(role, reason = log)

        if display_color:
            await Assign_role.adjust_role_position(user.guild, user, role)

    @staticmethod
    async def adjust_role_position(guild: nextcord.Guild, user: nextcord.Member, role: nextcord.Role):
        user_roles = sorted(user.roles, key=lambda r: r.position, reverse = True)
        new_position = user_roles[0].position + 1 if user_roles else 1
        await guild.edit_role_positions(positions={role: new_position})

    @staticmethod
    def generate_result_description(context: object) -> str:
        """根據不同情況回應result的title"""
        user_has_role = context.add_role in context.target_user.roles
        display_color = context.display_color

        if user_has_role and display_color:
            return "✅ **成功更改顏色！**（無身分組增加）"

        if not user_has_role and display_color:
            return f"✅ **成功指定 {context.add_role.mention}，並更改顏色！**"

        return f"✅ **成功指定 {context.add_role.mention}！**"


def create_log(target: object, role: object, user: object):
    """創造一個log，這會顯示在伺服器的審核日誌裡"""
    time = Toolkit.get_time()
    times = f"{time.year}/{time.month}/{time.day} | {time.hour}:{time.minute}:{time.second}"
    return f"(log) | {user.display_name} 在 {times} 對 {target.display_name} 添加了 {role.name} 身分組"