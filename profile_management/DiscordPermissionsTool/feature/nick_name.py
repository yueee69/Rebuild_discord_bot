import nextcord

from views.ERROR import Error

class Nick:
    @staticmethod
    async def nick(target: object, name: str):
        """
        params:
            target - 被改的人
            name - 要改的暱稱
        """
        await target.edit(nick = name)