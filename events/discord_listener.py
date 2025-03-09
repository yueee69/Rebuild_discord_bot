from nextcord.ext import commands
from new_bot.events.impl import message_event

class Discord_Event(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_event = message_event.MessageEvent()
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        await self.message_event.on_message(message)
        
def setup(bot):
    bot.add_cog(Discord_Event(bot))