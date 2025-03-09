# Description: 處理訊息事件
class MessageEvent():
    def __init__(self):
        pass
        
    async def on_message(self, message):
        await message.channel.send(f"你說了: {message.content}")
    
    
    