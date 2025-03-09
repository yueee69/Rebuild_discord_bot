from abc import ABC, abstractmethod
from enum import Enum

class CheckStatus(Enum):
    OK = 0
    CARD_IS_NOT_ENOUGH = 1
    FORBIDDEN = 2 #權限不足

class profile_manager(ABC):
    # 這裡搞抽象
    PER_DEDUCT = 1

    @abstractmethod
    def check_resource(self, context: object):
        pass

    @abstractmethod
    def deduct_fortune(self, context: object):
        pass

class NickTool(profile_manager):
    PER_DEDUCT = 1
    DO_NOT_ROLE = [
        "頭等鮭魚腹",
        "次等鮭魚腹",
        "鮭魚幹部",
        "食物鏈頂端",
        "花椰菜",
        "狗子",
        "鮭魚卵",
        "鮭魚們",
        "會外鮭魚",
        "會內鮭魚",
        "鮭姬",
        "鮭魚乾爹"
        ]

    def check_resource(self, context: object) -> dict[CheckStatus, str]:
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


