from .coin_activity import MessageCoinActivity


class MessageEvent():
    def __init__(self):
        self.coin_activity = MessageCoinActivity()
        
    async def on_message(self, message):
        await self.coin_activity.on_message(message)

    async def on_message_delete(self, message):
        await self.coin_activity.on_message_delete(message)

    async def on_message_edit(self, before, after):
        await self.coin_activity.on_message_edit(before, after)
