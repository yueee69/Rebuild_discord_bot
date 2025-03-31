from abc import ABC, abstractmethod
from enum import Enum

from utils.general import Toolkit
from core import constants

class CheckStatus(Enum):
    OK = 0
    CARD_IS_NOT_ENOUGH = 1
    FORBIDDEN = 2 #權限不足
    ERROR = 3 #資訊有誤

class profile_manager(ABC):
    # 這裡搞抽象
    PER_DEDUCT = 1
    DO_NOT_TOLE = constants.DO_NOT_ROLE

    @abstractmethod
    def check_resource(self, context: object):
        pass

    @abstractmethod
    def deduct_fortune(self, context: object):
        pass

class NickTool(profile_manager):
    PER_DEDUCT = 1

    def check_resource(self, context: object) -> tuple[CheckStatus, str]:
        if context.user_item.nick_card < 1:
            return(CheckStatus.CARD_IS_NOT_ENOUGH, "你的指定暱稱卡不足！")
        
        bot_self = context.interaction.guild.me
        user = context.target_user
        if not bot_self.guild_permissions.manage_nicknames:
            return (CheckStatus.FORBIDDEN, "我的權限不足... 沒有管理暱稱的權限")
        
        if bot_self.top_role.position <= user.top_role.position:
            return (CheckStatus.FORBIDDEN, "我的權限不足... 用戶的權限太高啦！")

        return (CheckStatus.OK, "")

    def deduct_fortune(self, context: object):
        context.user_item.nick_card -= 1


class Create_role_tool(profile_manager):
    PER_DEDUCT = 1

    def check_resource(self, context: object) -> tuple[CheckStatus, str]:
        if context.user_item.add_role_card < 1:
            return(CheckStatus.CARD_IS_NOT_ENOUGH, "你的創建身分組卡不足！")
        
        bot_self = context.interaction.guild.me
        if not bot_self.guild_permissions.manage_roles:
            return (CheckStatus.FORBIDDEN, "我的權限不足... 我沒有建立身分組的權限")
        
        if Toolkit.is_custom_color(context.create_role_color):
            return (CheckStatus.ERROR, f'你輸入的 "{context.create_role_color}" 不是一個有效Hex色碼')
        
        if context.create_role_name in self.DO_NOT_ROLE:
            return (CheckStatus.ERROR, f'不可以創建名為 {context.create_role_name} 的身分組！')
   
        return (CheckStatus.OK, "")

    def deduct_fortune(self, context: object):
        context.user_item.add_role_card -= 1


class Assign_role_tool(profile_manager):
    PER_DEDUCT = 1

    def check_resource(self, context: object) -> tuple[CheckStatus, str]:
        if context.user_item.role_card < 1:
            return(CheckStatus.CARD_IS_NOT_ENOUGH, "你的指定身分組卡不足！")

        bot_self = context.interaction.guild.me
        if not bot_self.guild_permissions.manage_roles:
            return (CheckStatus.FORBIDDEN, "我的權限不足... 我沒有建立身分組的權限")
        
        if context.add_role.name in self.DO_NOT_ROLE:
            return (CheckStatus.ERROR, f'你想壞壞喔 不可以增加 {context.add_role.name} 這個身分組')
        
        if context.add_role in context.target_user.roles and not context.display_color:
            return (CheckStatus.ERROR, "該用戶已經擁有這個身分組 無法再次指定！")
        
        return (CheckStatus.OK, "")

    def deduct_fortune(self, context: object):
        context.user_item.role_card -= 1

    